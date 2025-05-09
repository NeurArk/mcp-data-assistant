"""
Agent integration module for the MCP Data Assistant.
"""

from agent.assistant import answer, _check_ollama_available
from agent.session_manager import session_manager

__all__ = ["answer", "_check_ollama_available", "session_manager"]
