"""Interactive mode utilities for user intervention."""

import questionary
from questionary import Style


# Custom style for questionary prompts
INTERACTIVE_STYLE = Style([
    ('qmark', 'fg:cyan bold'),
    ('question', 'bold'),
    ('answer', 'fg:green bold'),
    ('pointer', 'fg:cyan bold'),
    ('highlighted', 'fg:cyan bold'),
    ('selected', 'fg:green'),
])


def interactive_prompt():
    """Show interactive prompt for user intervention after each tool execution.
    
    Returns:
        tuple: (action, data) where action is one of:
            - "continue": User pressed enter, continue execution (data=None)
            - "question": User asked a question (data=question text)
            - "feedback": User provided feedback (data=feedback text)
            - "abort": User wants to stop execution (data=None)
    """
    print("\n" + "─" * 60)
    print("🎯 \033[1mInteractive Mode\033[0m - Choose an action:")
    
    choices = [
        questionary.Choice("▶ Continue execution", value="continue"),
        questionary.Choice("❓ Ask a question (won't affect context)", value="question"),
        questionary.Choice("💬 Provide feedback (will be added to context)", value="feedback"),
        questionary.Choice("⛔ Abort execution", value="abort"),
    ]
    
    action = questionary.select(
        "What would you like to do?",
        choices=choices,
        style=INTERACTIVE_STYLE,
        instruction="(Use arrow keys to navigate, Enter to select)"
    ).ask()
    
    if action is None:  # User pressed Ctrl+C
        return ("abort", None)
    
    if action == "continue":
        print("─" * 60 + "\n")
        return ("continue", None)
    elif action == "abort":
        return ("abort", None)
    elif action in ("question", "feedback"):
        prompt_text = "Your question" if action == "question" else "Your feedback"
        text = questionary.text(
            f"{prompt_text}:",
            style=INTERACTIVE_STYLE
        ).ask()
        if text is None:  # User pressed Ctrl+C
            return ("abort", None)
        print("─" * 60 + "\n")
        return (action, text.strip() if text else None)
    
    return ("continue", None)


def prompt_for_continuation() -> tuple:
    """Prompt user after agent completes a response (multi-turn conversation).
    
    Returns:
        tuple: (action, data) where action is one of:
            - "continue": User provided new instructions (data=new_instructions)
            - "exit": User wants to end the session (data=None)
    """
    print("\n" + "─" * 60)
    print("✨ \033[1mAgent completed response\033[0m - What would you like to do?")
    
    choices = [
        questionary.Choice("💬 Continue conversation (give new instructions)", value="continue"),
        questionary.Choice("🚪 Exit session", value="exit"),
    ]
    
    action = questionary.select(
        "Choose an action:",
        choices=choices,
        style=INTERACTIVE_STYLE,
        instruction="(Use arrow keys to navigate, Enter to select)"
    ).ask()
    
    if action is None:  # User pressed Ctrl+C
        return ("exit", None)
    
    if action == "exit":
        print("─" * 60 + "\n")
        return ("exit", None)
    
    # Get new instructions from user
    new_instructions = questionary.text(
        "Your instructions:",
        style=INTERACTIVE_STYLE,
        multiline=False,
    ).ask()
    
    if new_instructions is None:  # User pressed Ctrl+C
        return ("exit", None)
    
    print("─" * 60 + "\n")
    return ("continue", new_instructions.strip() if new_instructions else None)


# def prompt_for_clarification(question: str, options: list = None) -> str:
#     """Prompt user for clarification when the model asks a question.
    
#     Args:
#         question: The clarifying question from the model
#         options: Optional list of suggested options
    
#     Returns:
#         str: The user's response, or None if cancelled
#     """
#     print("\n" + "─" * 60)
#     print("🤔 \033[1mModel needs clarification:\033[0m")
#     print(f"\n   {question}\n")
    
#     if options and len(options) > 0:
#         # Show options as choices
#         print("   Suggested options:")
#         for i, opt in enumerate(options, 1):
#             print(f"   {i}. {opt}")
#         print()
        
#         # Let user either pick an option or type custom response
#         choices = [questionary.Choice(f"  {opt}", value=opt) for opt in options]
#         choices.append(questionary.Choice("  ✏️  Type custom response", value="_custom_"))
        
#         selected = questionary.select(
#             "Choose an option or type custom:",
#             choices=choices,
#             style=INTERACTIVE_STYLE,
#         ).ask()
        
#         if selected is None:  # User pressed Ctrl+C
#             print("─" * 60 + "\n")
#             return None
        
#         if selected == "_custom_":
#             response = questionary.text(
#                 "Your response:",
#                 style=INTERACTIVE_STYLE,
#             ).ask()
#             print("─" * 60 + "\n")
#             return response.strip() if response else None
        
#         print("─" * 60 + "\n")
#         return selected
#     else:
#         # No options, just get text response
#         response = questionary.text(
#             "Your response:",
#             style=INTERACTIVE_STYLE,
#         ).ask()
        
#         print("─" * 60 + "\n")
#         return response.strip() if response else None


def handle_user_question(client, question: str, task: str, execution_history: list, current_tool: str = None):
    """Answer user question without affecting main context.

    Uses isolated mode to create a separate conversation that doesn't pollute
    the main agent's context. Context is provided via the prompt itself.

    Args:
        client: LLMClient instance (unified interface)
        question: User's question
        task: The original task description
        execution_history: Unified execution history (tool + token info)
        current_tool: Name of the tool that just executed (if any)

    Returns:
        str: Model's answer
    """
    print(f"\n💭 \033[1mAnswering your question...\033[0m")
    
    # Build context summary
    context_parts = [f"Original task: {task[:500]}"]
    
    if execution_history:
        recent_tools = execution_history[-5:]  # Last 5 executions
        tool_summary = ", ".join([
            f"{h['name']}({'✓' if h.get('success', True) else '✗'})" 
            for h in recent_tools
        ])
        context_parts.append(f"Recent tool calls: {tool_summary}")
    
    if current_tool:
        context_parts.append(f"Just executed: {current_tool}")
    
    context = "\n".join(context_parts)
    
    response = client.create(
        messages=[{
            "type": "message",
            "role": "user",
            "content": f"""[CONTEXT - You are an AI assistant helping with a data analysis task]
{context}

[USER QUESTION]
{question}

Please answer briefly and concisely based on the context above."""
        }],
        reasoning_effort="low",
        isolated=True,  # Does not affect main conversation state
    )
    
    # Extract answer from unified response
    answer = None
    for item in response.output:
        if isinstance(item, dict):
            if item.get("type") == "message":
                content = item.get("content", [])
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        answer = c.get("text")
                        break
        elif hasattr(item, "type") and item.type == "message":
            # Handle object format (Azure OpenAI raw response)
            for c in item.content:
                if hasattr(c, "text"):
                    answer = c.text
                    break
        if answer:
            break
    
    if answer:
        print(f"\n📝 \033[1mAnswer:\033[0m\n{answer}\n")
    else:
        print("\n⚠️ Could not get an answer.\n")
    
    return answer
