"""
Hooks for the agent execution pipeline using unified LLM client.

Provider-specific strategies:

Azure OpenAI:
    Uses previous_response_id to continue the conversation and access the model's
    full hidden reasoning state (not just the exposed summary). This requires
    providing placeholder outputs for pending tool calls.

Anthropic:
    Cannot use previous_response_id (doesn't exist). Instead, we build a standalone
    context that includes the task and recent execution history, then ask the model
    to explain its reasoning. This avoids the tool_result/tool_use pairing requirement.

For retries, both use a specialized prompt and tool to capture WHY parameters changed.
"""

import json
from typing import Any, Dict, Optional

# Tool for first-time tool calls (OpenAI function format)
REASONING_TOOL = {
    "type": "function",
    "name": "submit_reasoning",
    "description": "Submit structured reasoning about the tool call decision",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "What is the goal of this tool call?"
            },
            "alternatives_considered": {
                "type": "string",
                "description": "Were other tools or approaches considered?"
            },
            "reason_for_choice": {
                "type": "string",
                "description": "Why was this tool chosen over alternatives?"
            },
            "assumptions": {
                "type": "string",
                "description": "What assumptions are being made about the data or state?"
            },
            "expected_outcome": {
                "type": "string",
                "description": "What is the expected result of this tool call?"
            }
        },
        "required": ["intent", "alternatives_considered", "reason_for_choice", "assumptions", "expected_outcome"],
        "additionalProperties": False
    },
    "strict": True
}

# Tool for retry attempts - captures reasoning about what changed and why (OpenAI format)
RETRY_REASONING_TOOL = {
    "type": "function",
    "name": "submit_retry_reasoning",
    "description": "Submit structured reasoning about why this retry uses different parameters",
    "parameters": {
        "type": "object",
        "properties": {
            "error_diagnosis": {
                "type": "string",
                "description": "What caused the previous failure?"
            },
            "parameters_changed": {
                "type": "string",
                "description": "Which parameters did you change from the failed attempt?"
            }
        },
        "required": ["error_diagnosis", "parameters_changed"],
        "additionalProperties": False
    },
    "strict": True
}

# Anthropic-native tool formats (input_schema instead of parameters)
REASONING_TOOL_ANTHROPIC = {
    "name": "submit_reasoning",
    "description": "Submit structured reasoning about the tool call decision",
    "input_schema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "What is the goal of this tool call?"
            },
            "alternatives_considered": {
                "type": "string",
                "description": "Were other tools or approaches considered?"
            },
            "reason_for_choice": {
                "type": "string",
                "description": "Why was this tool chosen over alternatives?"
            },
            "assumptions": {
                "type": "string",
                "description": "What assumptions are being made about the data or state?"
            },
            "expected_outcome": {
                "type": "string",
                "description": "What is the expected result of this tool call?"
            }
        },
        "required": ["intent", "alternatives_considered", "reason_for_choice", "assumptions", "expected_outcome"],
    },
}

RETRY_REASONING_TOOL_ANTHROPIC = {
    "name": "submit_retry_reasoning",
    "description": "Submit structured reasoning about why this retry uses different parameters",
    "input_schema": {
        "type": "object",
        "properties": {
            "error_diagnosis": {
                "type": "string",
                "description": "What caused the previous failure?"
            },
            "parameters_changed": {
                "type": "string",
                "description": "Which parameters did you change from the failed attempt?"
            }
        },
        "required": ["error_diagnosis", "parameters_changed"],
    },
}

# Export field names for dynamic logging (derived from tool definitions)
REASONING_FIELDS = list(REASONING_TOOL["parameters"]["properties"].keys())
RETRY_REASONING_FIELDS = list(RETRY_REASONING_TOOL["parameters"]["properties"].keys())


def pre_tool_call_hook(
    client,  # LLMClient instance (unified interface)
    tool_name: str,
    tool_args: Dict[str, Any],
    previous_response_id: str,
    pending_tool_calls: list,
    # Retry context (optional)
    is_retry: bool = False,
    previous_error: str = None,
    previous_args: Dict[str, Any] = None,
    # Context for Anthropic (optional)
    task: str = None,
    execution_history: list = None,
) -> Optional[Dict[str, str]]:
    """
    Extract structured reasoning from the model about why it made a tool call.

    Dispatches to provider-specific implementations:
    - OpenAI / Azure OpenAI: Use previous_response_id to access hidden reasoning state
    - Anthropic: Builds standalone context (no previous_response_id support)

    Args:
        client: LLMClient instance (unified interface)
        tool_name: Name of the tool being called
        tool_args: Arguments passed to the tool
        previous_response_id: The response ID that produced this tool call (Azure only)
        pending_tool_calls: List of all tool calls from the response
        is_retry: Whether this is a retry of a previously failed tool call
        previous_error: Error message from the failed attempt (if retry)
        previous_args: Arguments used in the failed attempt (if retry)
        task: Original task description (used by Anthropic for context)
        execution_history: Recent execution history (used by Anthropic for context)

    Returns:
        Structured reasoning dict, or None on failure
    """
    if client.provider == "anthropic":
        return _pre_tool_call_hook_anthropic(
            client=client,
            tool_name=tool_name,
            tool_args=tool_args,
            is_retry=is_retry,
            previous_error=previous_error,
            previous_args=previous_args,
            task=task,
            execution_history=execution_history,
        )
    else:
        return _pre_tool_call_hook_azure(
            client=client,
            tool_name=tool_name,
            tool_args=tool_args,
            previous_response_id=previous_response_id,
            pending_tool_calls=pending_tool_calls,
            is_retry=is_retry,
            previous_error=previous_error,
            previous_args=previous_args,
        )


def _pre_tool_call_hook_azure(
    client,
    tool_name: str,
    tool_args: Dict[str, Any],
    previous_response_id: str,
    pending_tool_calls: list,
    is_retry: bool = False,
    previous_error: str = None,
    previous_args: Dict[str, Any] = None,
) -> Optional[Dict[str, str]]:
    """
    Azure OpenAI hook: Continue conversation using previous_response_id to access
    the model's full hidden reasoning state.
    """
    args_preview = {
        k: (f"<AnnData {v.n_obs}x{v.n_vars}>" if hasattr(v, 'n_obs') else str(v)[:100])
        for k, v in tool_args.items()
    }

    # Choose prompt and tool based on whether this is a retry
    if is_retry and previous_error:
        prev_args_preview = {
            k: (f"<AnnData>" if hasattr(v, 'n_obs') else str(v)[:100])
            for k, v in (previous_args or {}).items()
        }

        prompt = (
            f"You just retried `{tool_name}` after it previously FAILED.\n\n"
            f"PREVIOUS ATTEMPT (failed):\n"
            f"  Arguments: {json.dumps(prev_args_preview)}\n"
            f"  Error: {previous_error}\n\n"
            f"NEW ATTEMPT:\n"
            f"  Arguments: {json.dumps(args_preview)}\n\n"
            f"Explain your reasoning for the changes using the submit_retry_reasoning function. "
            f"Why did the previous call fail? What did you change and why?"
        )
        tool = RETRY_REASONING_TOOL
        tool_name_to_call = "submit_retry_reasoning"
        fallback = {
            "error_diagnosis": "(hook failed)",
            "parameters_changed": "N/A",
        }
    else:
        prompt = (
            f"You just decided to call `{tool_name}` with arguments: {json.dumps(args_preview)}. "
            f"Explain your reasoning for this specific tool call using the submit_reasoning function."
        )
        tool = REASONING_TOOL
        tool_name_to_call = "submit_reasoning"
        fallback = {
            "intent": "(hook failed)",
            "alternatives_considered": "N/A",
            "reason_for_choice": "N/A",
            "assumptions": "N/A",
            "expected_outcome": "N/A"
        }

    # Placeholder outputs for ALL pending tool calls to satisfy Azure API requirement
    placeholder_outputs = [
        {
            "type": "function_call_output",
            "call_id": tc.call_id,
            "output": json.dumps({"status": "pending", "note": "observability fork"})
        }
        for tc in pending_tool_calls
    ]

    try:
        response = client.create(
            messages=placeholder_outputs + [{"type": "message", "role": "user", "content": prompt}],
            tools=[tool],
            tool_choice={"type": "function", "name": tool_name_to_call},
            store=False,
            previous_response_id=previous_response_id,
            isolated=True,
        )

        for item in response.output:
            if isinstance(item, dict):
                if item.get("type") == "function_call" and item.get("name") == tool_name_to_call:
                    result = json.loads(item.get("arguments", "{}"))
                    result["_is_retry"] = is_retry
                    return result
            elif hasattr(item, "type"):
                if item.type == "function_call" and item.name == tool_name_to_call:
                    result = json.loads(item.arguments)
                    result["_is_retry"] = is_retry
                    return result

        return None

    except Exception as e:
        fallback["_error"] = str(e)
        fallback["_is_retry"] = is_retry
        return fallback


def _pre_tool_call_hook_anthropic(
    client,
    tool_name: str,
    tool_args: Dict[str, Any],
    is_retry: bool = False,
    previous_error: str = None,
    previous_args: Dict[str, Any] = None,
    task: str = None,
    execution_history: list = None,
) -> Optional[Dict[str, str]]:
    """
    Anthropic hook: Build standalone context since we can't use previous_response_id.

    Strategy:
    - Create a fresh conversation with context about the task and recent history
    - Ask the model to explain its reasoning for the tool call
    - Use Anthropic-native tool format (input_schema instead of parameters)
    - Do NOT include function_call_output messages (would require matching tool_use)
    """
    args_preview = {
        k: (f"<AnnData {v.n_obs}x{v.n_vars}>" if hasattr(v, 'n_obs') else str(v)[:100])
        for k, v in tool_args.items()
    }

    # Build context summary from execution history
    context_parts = []
    if task:
        context_parts.append(f"TASK: {task[:500]}")

    if execution_history:
        recent = execution_history[-5:]  # Last 5 tool calls
        history_summary = []
        for h in recent:
            status = "✓" if h.get("success", True) else "✗"
            history_summary.append(f"  - {h.get('name', 'unknown')} ({status})")
        if history_summary:
            context_parts.append("RECENT TOOL CALLS:\n" + "\n".join(history_summary))

    context = "\n\n".join(context_parts) if context_parts else "No additional context available."

    # Choose prompt and tool based on whether this is a retry
    if is_retry and previous_error:
        prev_args_preview = {
            k: (f"<AnnData>" if hasattr(v, 'n_obs') else str(v)[:100])
            for k, v in (previous_args or {}).items()
        }

        prompt = (
            f"[CONTEXT]\n{context}\n\n"
            f"[RETRY ANALYSIS]\n"
            f"A tool call to `{tool_name}` previously FAILED and is being retried.\n\n"
            f"PREVIOUS ATTEMPT (failed):\n"
            f"  Arguments: {json.dumps(prev_args_preview)}\n"
            f"  Error: {previous_error}\n\n"
            f"NEW ATTEMPT:\n"
            f"  Arguments: {json.dumps(args_preview)}\n\n"
            f"Please use the submit_retry_reasoning tool to explain why the previous call "
            f"failed and what was changed for this retry."
        )
        tool = RETRY_REASONING_TOOL_ANTHROPIC
        tool_name_to_call = "submit_retry_reasoning"
        fallback = {
            "error_diagnosis": "(hook failed)",
            "parameters_changed": "N/A",
        }
    else:
        prompt = (
            f"[CONTEXT]\n{context}\n\n"
            f"[TOOL CALL ANALYSIS]\n"
            f"The AI assistant has decided to call `{tool_name}` with these arguments:\n"
            f"  {json.dumps(args_preview)}\n\n"
            f"Please use the submit_reasoning tool to explain the reasoning behind this "
            f"tool call decision: what is the intent, what alternatives were considered, "
            f"why this tool was chosen, what assumptions are being made, and what outcome is expected."
        )
        tool = REASONING_TOOL_ANTHROPIC
        tool_name_to_call = "submit_reasoning"
        fallback = {
            "intent": "(hook failed)",
            "alternatives_considered": "N/A",
            "reason_for_choice": "N/A",
            "assumptions": "N/A",
            "expected_outcome": "N/A"
        }

    try:
        # For Anthropic, we use isolated=True with a clean user message (no tool results)
        # This creates a fresh conversation that won't conflict with the main context
        response = client.create(
            messages=[{"type": "message", "role": "user", "content": prompt}],
            tools=[tool],
            tool_choice={"type": "tool", "name": tool_name_to_call},  # Anthropic format
            reasoning_effort="low",  # Keep hook fast
            isolated=True,
        )

        for item in response.output:
            if isinstance(item, dict):
                if item.get("type") == "function_call" and item.get("name") == tool_name_to_call:
                    result = json.loads(item.get("arguments", "{}"))
                    result["_is_retry"] = is_retry
                    return result
            elif hasattr(item, "type"):
                if item.type == "function_call" and item.name == tool_name_to_call:
                    result = json.loads(item.arguments)
                    result["_is_retry"] = is_retry
                    return result

        return None

    except Exception as e:
        fallback["_error"] = str(e)
        fallback["_is_retry"] = is_retry
        return fallback
