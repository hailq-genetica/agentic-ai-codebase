"""
Agent control — holds a reference to the current AgentState so tools
can access it without being passed the state explicitly.
"""

from typing import Optional


class _AgentStateHolder:
    """Singleton-style holder for the active AgentState."""
    
    def __init__(self):
        self.agent_state = None
    
    def set(self, state):
        self.agent_state = state
    
    def get(self):
        return self.agent_state


_holder = _AgentStateHolder()


def set_agent_state(state):
    """Set the global agent state reference for tool access."""
    _holder.set(state)


def get_agent_state():
    """Get the current agent state."""
    return _holder.get()
