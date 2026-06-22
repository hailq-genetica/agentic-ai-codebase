"""
Unified LLM client abstraction for OpenAI, Azure OpenAI, and Anthropic Claude.

This module provides a single interface for calling different LLM providers,
handling message format conversion, API differences, and response parsing.
"""

import copy
import json
import os
from typing import Any, Optional
from dataclasses import dataclass


# Anthropic models that use adaptive thinking + output_config.effort instead of
# the legacy {type:"enabled", budget_tokens} thinking config. The legacy form
# returns HTTP 400 on Opus 4.7/4.8.
_ADAPTIVE_THINKING_MARKERS = (
    "opus-4-5", "opus-4-6", "opus-4-7", "opus-4-8",
    "sonnet-4-6", "fable-5", "mythos-5",
)


def _supports_adaptive_thinking(model: str) -> bool:
    m = (model or "").lower()
    return any(marker in m for marker in _ADAPTIVE_THINKING_MARKERS)


class UsageInfo:
    """Unified usage object that exposes attributes like the Azure OpenAI usage object."""
    def __init__(self, input_tokens: int = 0, output_tokens: int = 0,
                 input_tokens_details=None, output_tokens_details=None):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
        self.input_tokens_details = input_tokens_details
        self.output_tokens_details = output_tokens_details
    
    def __repr__(self):
        return f"UsageInfo(input={self.input_tokens}, output={self.output_tokens})"


@dataclass
class LLMResponse:
    """Unified response object across providers."""
    id: str
    provider: str  # "openai", "azure_openai", or "anthropic"
    output: list  # Unified output format
    usage: Any  # Token usage object (attribute access: .input_tokens, .output_tokens, etc.)
    raw_response: Any  # Original response object


class LLMClient:
    """Unified interface for LLM providers (OpenAI, Azure OpenAI, Anthropic)."""
    
    def __init__(self, provider: str, model: str, **kwargs):
        self.provider = provider.lower()
        self.model = model
        
        if self.provider == "openai":
            self._init_openai(**kwargs)
        elif self.provider == "azure_openai":
            self._init_azure_openai(**kwargs)
        elif self.provider == "anthropic":
            self._init_anthropic(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def _init_openai(self, **kwargs):
        """Direct OpenAI API (platform.openai.com), not Azure."""
        from openai import OpenAI
        self.client = OpenAI(
            api_key=kwargs.get("api_key") or os.environ.get("OPENAI_API_KEY"),
        )
        self._conversation_id = None
    
    def _init_azure_openai(self, **kwargs):
        from openai import AzureOpenAI
        self.client = AzureOpenAI(
            api_key=kwargs.get("api_key") or os.environ["AZURE_OPENAI_API_KEY"],
            api_version=kwargs.get("api_version") or os.environ.get("AZURE_OPENAI_API_VERSION", "2025-03-01-preview"),
            azure_endpoint=kwargs.get("azure_endpoint") or os.environ["AZURE_OPENAI_ENDPOINT"],
        )
        self._conversation_id = None
    
    def _init_anthropic(self, **kwargs):
        import anthropic
        self.client = anthropic.Anthropic(
            api_key=kwargs.get("api_key") or os.environ.get("ANTHROPIC_API_KEY")
        )
        # Anthropic conversation state: we maintain the full message list ourselves.
        # This is a list of dicts in Anthropic's native format:
        #   {"role": "user"|"assistant", "content": [...]}
        # System prompt is stored separately (Anthropic uses a top-level `system` param).
        self._conversation_history: list[dict] = []
        self._system_prompt: Optional[str] = None
    
    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def create(
        self,
        messages: list,
        tools: Optional[list] = None,
        reasoning_effort: str = "medium",
        store: bool = True,
        parallel_tool_calls: bool = False,
        tool_choice: Optional[dict] = None,
        previous_response_id: Optional[str] = None,
        isolated: bool = False,
    ) -> LLMResponse:
        if self.provider in ("openai", "azure_openai"):
            return self._create_openai_responses(
                messages, tools, reasoning_effort, store=store and not isolated,
                parallel_tool_calls=parallel_tool_calls, tool_choice=tool_choice,
                previous_response_id=previous_response_id
            )
        elif self.provider == "anthropic":
            if isolated:
                # Deep copy to prevent isolated call from modifying nested content
                saved_history = copy.deepcopy(self._conversation_history)
                saved_system = self._system_prompt
                try:
                    self._conversation_history = []
                    return self._create_anthropic(
                        messages, tools, reasoning_effort, tool_choice,
                        _isolated_mode=True  # Signal to filter problematic messages
                    )
                finally:
                    self._conversation_history = saved_history
                    self._system_prompt = saved_system
            else:
                return self._create_anthropic(messages, tools, reasoning_effort, tool_choice)
    
    @property
    def conversation_id(self) -> Optional[str]:
        if self.provider in ("openai", "azure_openai"):
            return self._conversation_id
        return None
    
    def reset_conversation_history(self):
        if self.provider == "anthropic":
            self._conversation_history = []
    
    # -------------------------------------------------------------------------
    # OpenAI Responses API (direct OpenAI and Azure OpenAI share the same API)
    # -------------------------------------------------------------------------
    def _create_openai_responses(self, messages, tools, reasoning_effort, store,
                                  parallel_tool_calls, tool_choice, previous_response_id):
        """Call OpenAI Responses API (same for direct OpenAI and Azure OpenAI)."""
        response = self.client.responses.create(
            model=self.model,
            input=messages,
            tools=tools or [],
            reasoning={"effort": reasoning_effort},
            store=store,
            parallel_tool_calls=parallel_tool_calls,
            **({"tool_choice": tool_choice} if tool_choice else {}),
            **({"previous_response_id": previous_response_id} if previous_response_id else {}),
        )
        self._conversation_id = response.id
        return LLMResponse(
            id=response.id, provider=self.provider,
            output=response.output, usage=response.usage, raw_response=response,
        )
    
    # -------------------------------------------------------------------------
    # Anthropic
    # -------------------------------------------------------------------------
    def _create_anthropic(self, messages, tools, reasoning_effort, tool_choice,
                           _isolated_mode: bool = False):
        """Call Anthropic Messages API.

        Anthropic multi-turn rules:
        1. Messages must strictly alternate: user, assistant, user, assistant, ...
        2. The first message must be role=user.
        3. tool_result blocks go in a user message and MUST reference a tool_use
           block in the immediately preceding assistant message.
        4. The system prompt is a separate top-level parameter, not a message.

        Strategy:
        - We maintain `_conversation_history` as the canonical Anthropic message list.
        - On each call, we convert the incoming OpenAI-format `messages` to Anthropic
          content blocks and append them to the history.
        - After the API call, we append the assistant's response to the history.
        - We never try to "merge" messages. Instead, we append content blocks to the
          last message if the role matches, or start a new message if it doesn't.
          This is safe because the caller always sends either:
            (a) Initial messages: [system, user] → system extracted, user appended
            (b) Tool results + images: [function_call_output, user(image)] → all user role
            (c) User feedback: [user message]

        Isolated mode (_isolated_mode=True):
        - History has been cleared by the caller
        - We filter out function_call_output messages since they require matching
          tool_use blocks in the history (which doesn't exist in isolated mode)
        - Only user/system messages are processed
        """
        # --- Step 1: Convert incoming messages and append to history ---
        # In isolated mode, filter out function_call_output to avoid tool_result errors
        if _isolated_mode:
            messages = [m for m in messages if m.get("type") != "function_call_output"]
        new_blocks = self._convert_incoming_messages(messages)
        
        for role, content_blocks in new_blocks:
            if not content_blocks:
                continue
            # Append to last message if same role, otherwise start new message
            if self._conversation_history and self._conversation_history[-1]["role"] == role:
                self._conversation_history[-1]["content"].extend(content_blocks)
            else:
                self._conversation_history.append({"role": role, "content": content_blocks})
        
        # --- Step 2: Build API kwargs ---
        # Defensive: filter out any thinking blocks from history before sending
        # (They should already be filtered by _serialize_response_content, but this
        # guards against any edge cases or legacy data)
        filtered_history = self._filter_thinking_blocks_from_history(self._conversation_history)

        max_tokens_map = {"low": 4096, "medium": 8192, "high": 16384}
        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens_map.get(reasoning_effort, 8192),
            "messages": filtered_history,
        }
        # Thinking configuration is model-dependent. Newer models (Opus 4.5+,
        # Sonnet 4.6, Fable 5) use adaptive thinking + output_config.effort; the
        # legacy {type:"enabled", budget_tokens} form returns HTTP 400 on Opus
        # 4.7/4.8. Older models keep the legacy form.
        if _supports_adaptive_thinking(self.model):
            effort = reasoning_effort if reasoning_effort in ("low", "medium", "high") else "medium"
            kwargs["output_config"] = {"effort": effort}
            if reasoning_effort == "high":
                kwargs["thinking"] = {"type": "adaptive"}
        elif reasoning_effort == "high":
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": 10000}
        if self._system_prompt:
            kwargs["system"] = self._system_prompt
        if tools:
            kwargs["tools"] = self._convert_tools_to_anthropic(tools)
        if tool_choice:
            kwargs["tool_choice"] = self._convert_tool_choice_to_anthropic(tool_choice)
        
        # --- Step 3: Call API ---
        response = self.client.messages.create(**kwargs)
        
        # --- Step 4: Append assistant response to history ---
        # Serialize the response content blocks to plain dicts so they can be
        # re-sent in future requests. This preserves tool_use ids.
        assistant_content = self._serialize_response_content(response.content)
        self._conversation_history.append({
            "role": "assistant",
            "content": assistant_content,
        })
        
        # --- Step 5: Convert to unified output format ---
        unified_output = self._convert_response_to_unified(response)
        
        usage = UsageInfo(
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
        cache_read = getattr(response.usage, 'cache_read_input_tokens', 0) or 0
        if cache_read:
            usage.input_tokens_details = type('Details', (), {'cached_tokens': cache_read})()
        
        return LLMResponse(
            id=response.id, provider="anthropic",
            output=unified_output, usage=usage, raw_response=response,
        )
    
    def _convert_incoming_messages(self, messages: list) -> list[tuple[str, list[dict]]]:
        """Convert incoming OpenAI Responses-format messages to (role, content_blocks) pairs.
        
        Each pair represents content that should be appended to the conversation.
        System messages are extracted to self._system_prompt and not returned.
        
        Returns a list of (role, content_blocks) tuples. Content blocks are in
        Anthropic's native format (text, image, tool_result).
        """
        result = []
        
        for msg in messages:
            msg_type = msg.get("type")
            
            if msg_type == "message":
                role = msg.get("role")
                content = msg.get("content")
                
                # System prompt → store separately, not a message
                if role == "system":
                    if isinstance(content, str):
                        self._system_prompt = content
                    elif isinstance(content, list):
                        self._system_prompt = "\n".join(
                            c.get("text", "") for c in content
                            if isinstance(c, dict) and c.get("type") in ("text", "input_text")
                        )
                    continue
                
                if role not in ("user", "assistant"):
                    continue
                
                # Convert content to Anthropic blocks
                blocks = self._convert_content_blocks(content)
                if blocks:
                    result.append((role, blocks))
            
            elif msg_type == "function_call_output":
                # Tool result → user message with tool_result block.
                # Anthropic requires this to be in a user message immediately
                # after an assistant message containing the matching tool_use.
                result.append(("user", [{
                    "type": "tool_result",
                    "tool_use_id": msg.get("call_id"),
                    "content": msg.get("output", ""),
                }]))
        
        return result
    
    def _convert_content_blocks(self, content) -> list[dict]:
        """Convert a single message's content (string or list) to Anthropic content blocks."""
        if isinstance(content, str):
            return [{"type": "text", "text": content}]
        
        if not isinstance(content, list):
            return []
        
        blocks = []
        for c in content:
            if not isinstance(c, dict):
                continue
            
            c_type = c.get("type")
            
            if c_type in ("text", "input_text"):
                text = c.get("text", "")
                if text:
                    blocks.append({"type": "text", "text": text})
            
            elif c_type == "input_image":
                image_block = self._convert_image_block(c)
                if image_block:
                    blocks.append(image_block)
        
        return blocks
    
    def _convert_image_block(self, c: dict) -> Optional[dict]:
        """Convert an input_image block to Anthropic image format."""
        image_url = c.get("image_url")
        source = c.get("source")
        
        if image_url and isinstance(image_url, str) and image_url.startswith("data:"):
            # Parse data URL: "data:image/png;base64,<data>"
            header, _, b64data = image_url.partition(",")
            media_type = "image/png"
            if ":" in header and ";" in header:
                media_type = header.split(":")[1].split(";")[0]
            return {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": b64data}
            }
        elif source and isinstance(source, dict):
            return {
                "type": "image",
                "source": {
                    "type": source.get("type", "base64"),
                    "media_type": source.get("media_type", "image/png"),
                    "data": source.get("data", ""),
                }
            }
        return None
    
    def _serialize_response_content(self, content, for_resend: bool = True) -> list[dict]:
        """Serialize Anthropic SDK response content blocks to plain dicts.

        This is critical: the serialized dicts are appended to _conversation_history
        and re-sent in subsequent API calls. We must preserve:
        - text blocks (type, text)
        - tool_use blocks (type, id, name, input) — id is needed by tool_result

        IMPORTANT: Thinking blocks are NOT included when for_resend=True because
        Anthropic's API does not accept thinking blocks in input messages. They
        are only valid in assistant responses, not in conversation history that
        gets re-sent. Including them causes API errors.

        Args:
            content: The response content blocks from the API
            for_resend: If True (default), filter out thinking blocks for re-sending.
                        If False, include thinking blocks (e.g., for logging).
        """
        out = []
        for block in content:
            # Get the type as a string, handling both str and enum
            bt = self._get_block_type(block)

            if bt == "text":
                out.append({
                    "type": "text",
                    "text": getattr(block, "text", ""),
                })
            elif bt == "tool_use":
                out.append({
                    "type": "tool_use",
                    "id": getattr(block, "id", ""),
                    "name": getattr(block, "name", ""),
                    "input": getattr(block, "input", {}),
                })
            elif bt == "thinking":
                # Skip thinking blocks when serializing for re-send
                # Anthropic API rejects thinking blocks in input messages
                if not for_resend:
                    out.append({
                        "type": "thinking",
                        "thinking": getattr(block, "thinking", ""),
                    })
                # When for_resend=True, we skip thinking blocks entirely
            else:
                # Fallback: try to detect tool_use by shape (id + name + input)
                if all(getattr(block, k, None) is not None for k in ("id", "name", "input")):
                    out.append({
                        "type": "tool_use",
                        "id": str(getattr(block, "id", "")),
                        "name": getattr(block, "name", ""),
                        "input": getattr(block, "input", {}),
                    })
                elif hasattr(block, "model_dump"):
                    # Filter thinking blocks from model_dump too
                    dumped = block.model_dump()
                    if for_resend and dumped.get("type") == "thinking":
                        continue
                    out.append(dumped)
                else:
                    # Last resort — skip unknown blocks rather than corrupt history
                    pass
        return out
    
    def _get_block_type(self, block) -> str:
        """Get content block type as a lowercase string, handling SDK enums."""
        if isinstance(block, dict):
            return block.get("type", "")
        t = getattr(block, "type", None)
        if t is None:
            return ""
        if isinstance(t, str):
            return t
        # Handle enums (e.g. ContentBlockType.tool_use)
        if hasattr(t, "value"):
            return str(t.value)
        return str(t).rsplit(".", 1)[-1].lower()

    def _filter_thinking_blocks_from_history(self, history: list) -> list:
        """Remove thinking blocks from conversation history.

        Anthropic's API does not accept thinking blocks in input messages.
        They are only valid in assistant responses, not when re-sending history.
        This is a defensive filter that ensures we never send thinking blocks.
        """
        filtered = []
        for msg in history:
            if not isinstance(msg, dict):
                filtered.append(msg)
                continue

            content = msg.get("content", [])
            if not isinstance(content, list):
                filtered.append(msg)
                continue

            # Filter out thinking blocks from the content
            filtered_content = [
                block for block in content
                if not (isinstance(block, dict) and block.get("type") == "thinking")
            ]

            # Only include messages that still have content after filtering
            if filtered_content:
                filtered.append({
                    **msg,
                    "content": filtered_content
                })
            # If message has no content left after filtering, skip it
            # (This handles edge case of assistant message with only thinking)

        return filtered
    
    def _convert_response_to_unified(self, response) -> list:
        """Convert Anthropic response to the unified output format used by the agent.

        Converts Anthropic content blocks to unified format:
        - thinking blocks → reasoning (with summary for logging)
        - text blocks → message with content
        - tool_use blocks → function_call

        Multiple text blocks are combined into a single message for cleaner output.
        """
        output = []
        text_parts = []
        thinking_parts = []

        for block in response.content:
            bt = self._get_block_type(block)
            if bt == "thinking":
                thinking_text = getattr(block, "thinking", "")
                if thinking_text:
                    thinking_parts.append(thinking_text)
            elif bt == "text":
                text_parts.append(block.text)
            elif bt == "tool_use":
                output.append({
                    "type": "function_call",
                    "name": block.name,
                    "call_id": block.id,
                    "arguments": json.dumps(block.input),
                })

        # Emit thinking blocks as unified "reasoning" items so parse_response can log them
        if thinking_parts:
            full_thinking = "\n".join(thinking_parts)
            # Truncate for summary display but keep full text available
            summary_text = full_thinking[:500] + ("..." if len(full_thinking) > 500 else "")
            output.insert(0, {
                "type": "reasoning",
                "summary": summary_text,
            })

        # Combine all text into a single message (cleaner than multiple messages)
        if text_parts:
            # Insert after reasoning (if present) but before tool calls
            insert_idx = 1 if thinking_parts else 0
            output.insert(insert_idx, {
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": "\n".join(text_parts)}]
            })

        return output
    
    # -------------------------------------------------------------------------
    # Tool format conversion
    # -------------------------------------------------------------------------
    def _convert_tools_to_anthropic(self, tools: list) -> list:
        claude_tools = []
        for tool in tools:
            if "input_schema" in tool:
                claude_tools.append(tool)
            elif tool.get("type") == "function":
                claude_tools.append({
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "input_schema": tool.get("parameters", {}),
                })
        return claude_tools
    
    def _convert_tool_choice_to_anthropic(self, tool_choice: dict) -> dict:
        if isinstance(tool_choice, dict) and tool_choice.get("type") == "function":
            return {"type": "tool", "name": tool_choice.get("name")}
        return tool_choice


def create_llm_client_from_config(config: dict) -> tuple[LLMClient, str]:
    """Create LLM client from configuration.
    
    Config under `llm`:
        provider: "openai" | "azure_openai" | "anthropic"
        model: model name or deployment name (required for provider selection)
        api_key: optional; otherwise uses OPENAI_API_KEY, AZURE_OPENAI_API_KEY, or ANTHROPIC_API_KEY
        For Azure: api_version, azure_endpoint (or env AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT)
    """
    llm_config = config.get("llm", {})
    provider = (llm_config.get("provider") or "azure_openai").strip().lower()
    
    if provider == "openai":
        model = llm_config.get("model") or os.environ.get("OPENAI_MODEL", "gpt-4o")
        client = LLMClient(
            provider="openai", model=model,
            api_key=llm_config.get("api_key"),
        )
    elif provider == "azure_openai":
        model = llm_config.get("model") or os.environ.get("AZURE_OPENAI_DEPLOYMENT", "o4-mini-0416")
        client = LLMClient(
            provider="azure_openai", model=model,
            api_key=llm_config.get("api_key"),
            api_version=llm_config.get("api_version"),
            azure_endpoint=llm_config.get("azure_endpoint"),
        )
    elif provider == "anthropic":
        model = llm_config.get("model", "claude-3-5-sonnet-20241022")
        client = LLMClient(
            provider="anthropic", model=model,
            api_key=llm_config.get("api_key"),
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Use one of: openai, azure_openai, anthropic")
    
    return client, model