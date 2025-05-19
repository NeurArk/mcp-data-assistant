# pragma: no cover
"""
Ollama integration for MCP Data Assistant.

Simple direct integration with OpenAI Agents SDK, following the pattern from
examples in the SDK documentation.
"""

import os
import httpx
from agents import OpenAIChatCompletionsModel, AsyncOpenAI, set_tracing_disabled

# Disable tracing for local models to avoid errors
set_tracing_disabled(True)

# Constants
OLLAMA_API_BASE = "http://localhost:11434"
OLLAMA_V1_API = f"{OLLAMA_API_BASE}/v1"


def check_ollama_available():
    """Check if Ollama is running and accessible."""
    try:
        # Use a client with context manager to ensure proper cleanup
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{OLLAMA_API_BASE}/api/tags")
            return response.status_code == 200
    except Exception:
        return False


def get_ollama_model_name():
    """Get the model name to use with Ollama."""
    # Get model name from environment or use default
    # Utiliser qwen3:8b comme modèle par défaut
    return os.getenv("OLLAMA_MODEL", "qwen3:8b")


def create_ollama_model():
    """
    Create an OpenAIChatCompletionsModel configured for Ollama,
    using the simple pattern shown in SDK examples.

    Returns:
        OpenAIChatCompletionsModel: Model configured to use Ollama
    """
    model_name = get_ollama_model_name()

    # Create and return the model
    # Après vérification de la documentation, nous utilisons simplement la configuration de base
    # Les paramètres comme temperature et tool_choice seront configurés au niveau de l'agent,
    # pas au niveau du modèle ou du client
    return OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=AsyncOpenAI(
            base_url=OLLAMA_V1_API,
            api_key="ollama",  # Just a placeholder value
            timeout=30.0,  # Add timeout to prevent hanging
        ),
    )
