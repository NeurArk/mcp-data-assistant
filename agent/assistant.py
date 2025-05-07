from __future__ import annotations
import os
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerSse

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

# Initialize agent
agent = Agent(
    name="NeurArk Data Assistant",
    instructions=(
        "You are a data assistant that can analyze tabular data and create PDFs.\n"
        "You can work with SQL databases, CSV files, and generate PDF reports.\n"
        "Common workflows include:\n"
        "- Query data from database then generate PDF report with results\n"
        "- Analyze CSV files and create summary reports\n"
        "- Generate custom reports based on user specifications\n"
        "You should auto-discover available tools via the MCP server connection.\n\n"
        "When working with databases:\n"
        "- First, discover what tables are available in the database\n"
        "- If the user mentions a table that doesn't exist, look for alternatives\n"
        "- Explore the structure of the tables to understand columns\n"
        "- Execute appropriate queries based on what you discovered\n\n"
        "When generating PDF reports:\n"
        "- The 'data_json' parameter should be a JSON string with data to include\n"
        "- Always include the generated PDF file path in your response\n"
        "- Example format: {\"title\": \"Report Title\", \"data\": \"Your Data\"}\n"
    ),
    model="gpt-4.1-mini",
    mcp_servers=[mcp_server],
)


async def _run_agent(prompt: str) -> str:
    """Run the agent asynchronously with proper server connection handling."""
    # Connect to MCP server before running the agent
    async with mcp_server:
        # Execute the agent with the prompt
        result = await Runner.run(starting_agent=agent, input=prompt)
        return result.final_output  # String with PDF path or response


def answer(prompt: str) -> str:
    """Synchronous wrapper for running the agent."""
    if not os.getenv("OPENAI_API_KEY"):
        return "⚠️ OPENAI_API_KEY not set."

    try:
        # Run the async function in a synchronous context
        return asyncio.run(_run_agent(prompt))
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Agent error: {str(e)}")
        print(f"Error trace: {error_trace}")
        return f"Error: {str(e)}\nTrace: {error_trace}"
