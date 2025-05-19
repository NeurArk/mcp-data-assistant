# pragma: no cover
# mypy: ignore-errors
from __future__ import annotations
import os
import asyncio
from typing import Optional, Any
from agents import Agent, Runner, ModelSettings, set_tracing_disabled
from agents.mcp import MCPServerSse
from .session_manager import session_manager
from .ollama_integration import (
    check_ollama_available,
    create_ollama_model,
    get_ollama_model_name,
)

# Disable tracing for local models to avoid errors
set_tracing_disabled(True)

# Gradio 5.29 SSE endpoint
MCP_SSE_URL = os.getenv(
    "MCP_SSE_URL",
    "http://127.0.0.1:7860/gradio_api/mcp/sse",
)

# Create MCP server instance but don't connect yet
mcp_server = MCPServerSse(
    params={"url": MCP_SSE_URL},
    cache_tools_list=True,
)

# Base agent instructions
BASE_INSTRUCTIONS = (
    "You are a data assistant that can analyze tabular data and create PDFs.\n"
    "You can work with SQL databases, CSV files, and generate PDF reports.\n"
    "Common workflows include:\n"
    "- Query data from database then generate PDF report with results\n"
    "- Analyze CSV files and create summary reports\n"
    "- Generate custom reports based on user specifications\n"
    "You should auto-discover available tools via the MCP server connection.\n\n"
    "IMPORTANT: You have access to conversation memory. The system will maintain your\n"
    "conversation history with the user, so you can refer to previous messages and context.\n"
    "Remember what was discussed earlier and maintain continuity in the conversation.\n\n"
    "When working with databases:\n"
    "- First, discover what tables are available in the database\n"
    "- If the user mentions a table that doesn't exist, look for alternatives\n"
    "- Explore the structure of the tables to understand columns\n"
    "- Execute appropriate queries based on what you discovered\n"
    '- To call the SQL tool, use: {"name": "sql", "arguments": {"query": "YOUR SQL QUERY"}}\n\n'
    "When generating PDF reports:\n"
    "- IMPORTANT: When asked to create a PDF report, create it immediately with the information provided\n"
    "- Generate reports even with minimal information - do not ask for clarification\n"
    "- Build dictionary per pdf_schema.json with title, optional insights and list of sections.\n"
    "  Each section has type 'paragraph', 'table', or 'chart'; charts require 'chart_type' (bar, pie, line) and data.\n"
    "- Pass this dictionary as a JSON string via the 'data_json' parameter\n"
    "- Always include the generated PDF file path in your response\n"
    '- To call the PDF tool, use: {"name": "pdf", "arguments": {"data_json": "JSON string here"}}\n\n'
    "When working with CSV files:\n"
    "- If a user has uploaded a CSV file, it will be available in the uploads directory\n"
    "- Use the csv tool to analyze and provide insights about the data\n"
    "- Remember previous analyses of the same file when the user asks follow-up questions\n"
    "- Always consider the context of previous questions about the data\n"
    '- To call the CSV tool, use: {"name": "csv", "arguments": {"file_path": "/path/to/file.csv"}}\n\n'
    "IMPORTANT: Always execute tools by submitting the proper JSON format directly.\n"
    "DO NOT show explanations of what you're going to do - just directly call the tool with the proper JSON format.\n"
    "After receiving tool results, then you can explain and interpret the results to the user.\n"
)

# Standard model settings for all agents
# Use the same settings across providers for consistency (following the example)
model_settings = ModelSettings(temperature=0.7, tool_choice="auto")

# Initialize agent - we'll modify the model and instructions per session
agent = Agent(
    name="NeurArk Data Assistant",
    instructions=BASE_INSTRUCTIONS,
    model="gpt-4.1-mini",  # Default model, will be changed based on provider
    model_settings=model_settings,
    mcp_servers=[mcp_server],
)

# Use the function from ollama_integration.py module
# Just for backward compatibility with existing code
_check_ollama_available = check_ollama_available


def answer(
    prompt: str,
    provider: str = "openai",
    session_id: Optional[str] = None,
    prev_result: Optional[Any] = None,
) -> str:
    """
    Run the agent with the specified provider and session context.

    Args:
        prompt: The user prompt to send to the agent
        provider: The LLM provider (openai or ollama)
        session_id: Optional session ID for maintaining conversation context
        prev_result: Previous result object from Runner.run, used to maintain conversation history

    Returns:
        tuple: The agent's response and the result object for future calls
    """
    try:
        # Create a new session if none provided
        if not session_id:
            session_id = session_manager.create_session()
            print(f"Created new session: {session_id}")

        # Exit early if Ollama selected but not available
        if provider == "ollama" and not _check_ollama_available():
            return "⚠️ Ollama not available or not running.", None

        # Exit early if OpenAI selected but API key not set
        if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            return "⚠️ OPENAI_API_KEY not set.", None

        try:
            # Update instructions with session context
            if session_id:
                agent.instructions = session_manager.create_system_prompt(
                    session_id, BASE_INSTRUCTIONS
                )

            # Configure the model based on provider
            if provider == "ollama":
                # Get the Ollama model
                model_name = get_ollama_model_name()
                print(f"Using Ollama model: {model_name}")

                # Set the agent's model to use Ollama
                agent.model = create_ollama_model()
            else:
                # Get the OpenAI model
                model_name = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
                print(f"Using OpenAI model: {model_name}")

                # Set the agent's model to use OpenAI
                agent.model = model_name

        except Exception as e:
            print(f"Error setting up provider: {str(e)}")
            return f"⚠️ Error setting up {provider} client: {str(e)}", None

        # Prepare input based on whether prev_result exists
        if prev_result:
            # Use the conversation history from the previous result
            print("Using previous result to maintain conversation history")
            # Add the new user message to the previous conversation history
            input_messages = prev_result.to_input_list() + [
                {"role": "user", "content": prompt}
            ]
        else:
            # First message in conversation
            print("Starting new conversation")
            input_messages = [{"role": "user", "content": prompt}]

        # Still store in session for persistence/logging (but won't be used directly)
        session_manager.add_message(session_id, "user", prompt)

        print(f"Running agent with prompt: {prompt[:30]}...")

        try:
            # Define async function to run the agent
            async def run_agent_async():
                # Connect to MCP server
                try:
                    print("Connecting to MCP server...")
                    await mcp_server.connect()
                    print("MCP server connected successfully")
                except Exception as e:
                    print(f"Warning: MCP server connection issue: {str(e)}")

                # Use async context manager for clean connections
                async with mcp_server:
                    # Use input_messages from prev_result or new conversation
                    print(f"Running with {len(input_messages)} messages in history")
                    if len(input_messages) > 0:
                        first_role = input_messages[0].get("role", "?")
                        last_role = input_messages[-1].get("role", "?")
                        print(f"First message: {first_role}, latest: {last_role}")

                    result = await Runner.run(
                        starting_agent=agent,
                        input=input_messages,
                        max_turns=10,  # Prevent infinite loops
                    )

                    # Ensure we properly close any OpenAI clients if using Ollama
                    if provider == "ollama":
                        try:
                            # Get the OpenAI client from the model and close it
                            if hasattr(agent.model, "openai_client"):
                                client = agent.model.openai_client
                                if hasattr(client, "aclose"):
                                    await client.aclose()
                        except Exception as e:
                            print(f"Warning when closing httpx client: {str(e)}")

                    return result

            # Run the agent with better event loop handling
            try:
                try:
                    # Vérifier si une boucle est déjà en cours d'exécution
                    loop = asyncio.get_running_loop()
                    # Si on est déjà dans une boucle asyncio, utiliser create_task
                    task = asyncio.run_coroutine_threadsafe(run_agent_async(), loop)
                    result = task.result()
                except RuntimeError:
                    # Aucune boucle en cours d'exécution, en créer une nouvelle
                    result = asyncio.run(run_agent_async())
            except Exception as e:
                print(f"Error during async execution: {str(e)}")
                # Ensure any pending tasks are cleaned up
                try:
                    for task in asyncio.all_tasks():
                        if not task.done():
                            task.cancel()
                except RuntimeError:
                    # Handle the case where there's no running event loop
                    pass
                raise

            # Get the response text
            response = result.final_output
            print(
                f"DEBUG - Raw LLM response from result.final_output: {response[:150]}"
            )

            # Store the assistant response in session history
            session_manager.add_message(session_id, "assistant", response)

            # Return both the response and result object
            return response, result

        except Exception as e:
            print(f"Error running agent: {str(e)}")
            import traceback

            print(traceback.format_exc())

            # Add error message to history
            error_msg = f"Error: {str(e)}"
            session_manager.add_message(session_id, "assistant", error_msg)
            return error_msg, None

    except Exception as e:
        import traceback

        error_trace = traceback.format_exc()
        print(f"Agent error: {str(e)}")
        print(f"Error trace: {error_trace}")

        # Add error to history if session exists
        if session_id:
            error_response = f"Error: {str(e)}"
            session_manager.add_message(session_id, "assistant", error_response)

        return f"Error: {str(e)}\nTrace: {error_trace}", None
