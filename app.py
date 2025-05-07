# existing imports
import gradio as gr
import json
import pathlib
import threading
import time
import requests
from tools.sql_tool import run_sql
from tools.csv_tool import summarise_csv
from tools.pdf_tool import create_pdf
# assistant
from agent import answer


def server_status() -> str:
    """
    A dummy function to show the server is alive.

    Returns:
        str: Status message confirming the server is running
    """
    # Function attribute to hide from MCP
    server_status._hide_from_mcp = True
    return "✅ MCP Data Assistant server is running."


with gr.Blocks() as tools_demo:
    gr.Markdown("# MCP Data Assistant")
    gr.Markdown("This server will expose three tools (SQL, CSV summary, PDF report).")

    # Register MCP tools
    run_sql_interface = gr.Interface(
        fn=run_sql,
        inputs=gr.Textbox(label="SQL Query"),
        outputs=gr.JSON(),
        title="SQL Query Tool",
        description="Execute read-only SQL queries",
        examples=["SELECT 1 AS one"],
        api_name="sql"
    )

    summarise_csv_interface = gr.Interface(
        fn=summarise_csv,
        inputs=gr.Textbox(label="CSV File Path"),
        outputs=gr.JSON(),
        title="CSV Summary Tool",
        description="Analyze and summarize a CSV file",
        examples=["sample_data/people.csv"],
        api_name="csv"
    )

    # Wrapper around create_pdf to ensure data parameter is properly processed
    def create_pdf_wrapper(data_json, out_path=None, include_chart=True):
        """
        Generate a professional PDF report from provided data.

        Creates a PDF document with the given data formatted as a table.
        Optionally includes a bar chart visualization of numeric values.

        Args:
            data_json: JSON string or object containing the data to include
            out_path: Optional custom path for the generated PDF file
            include_chart: Whether to include a bar chart visualization

        Returns:
            Absolute path to the generated PDF file

        Raises:
            ValueError: If the data dictionary is empty
        """
        # Debug log (minimal)
        print(f"PDF request received with type: {type(data_json)}")

        # Parse JSON string to dict if needed
        if isinstance(data_json, str):
            try:
                data = json.loads(data_json)
            except Exception:
                # Handle invalid JSON by creating an error dict
                data = {
                    "error": "Invalid JSON",
                    "raw_input": (data_json[:200] + "..."
                               if len(data_json) > 200 else data_json)
                }
        else:
            # Use the data directly
            data = data_json

        try:
            # Handle basic data type conversion
            if isinstance(data, dict):
                # Dictionary - use as is
                pass
            elif isinstance(data, list):
                # Convert list to simple dictionary with indexed keys
                items = {"item_" + str(i + 1): item for i, item in enumerate(data)}
                data = items
            else:
                # Unsupported type - create error dict
                data = {
                    "error": "Unsupported data type",
                    "received_type": str(type(data))
                }

            # Create the PDF
            return create_pdf(data, out_path, include_chart)

        except Exception as e:
            # If PDF creation fails, create an error report
            try:
                error_data = {"error": f"Failed to create PDF: {str(e)}"}
                return create_pdf(error_data, out_path, include_chart=False)
            except Exception:
                # Last resort if even the error PDF can't be created
                return "Critical error creating PDF"

    create_pdf_interface = gr.Interface(
        fn=create_pdf_wrapper,
        inputs=[
            gr.Textbox(
                label="Report Data (JSON)",
                value='{"customer": "ACME", "total": 1000}'
            ),
            gr.Textbox(
                label="Output Path (optional)",
                placeholder="Leave empty for default location"
            ),
            gr.Checkbox(label="Include Chart", value=True)
        ],
        outputs=gr.Textbox(label="Generated PDF Path"),
        title="PDF Report Generator",
        description="Create professional PDF reports with data and optional charts",
        examples=[
            ['{"customer": "ACME", "total": 999}',
             None, True]
        ],
        api_name="pdf"
    )

    # Add simple UI components
    status_btn = gr.Button("Ping server")
    status_output = gr.Textbox()
    # Hide from API and MCP
    status_btn.click(server_status, outputs=status_output, api_name=False)


# ---------- Assistant tab ----------
assistant_chat = gr.ChatInterface(
    fn=answer,
    title="NeurArk Data Assistant",
    examples=[
        "Show me total sales for 2024 and create a PDF report"
    ],
    api_name=False,  # Hide from API and MCP
    # Specify message type explicitly to avoid warning
    chatbot=gr.Chatbot(type="messages"),
    type="messages"
)


# ---------- Tabs UI -----------------
demo = gr.TabbedInterface(
    [tools_demo, assistant_chat],
    ["Tools demo", "Assistant"],
    title="NeurArk MCP Data Assistant",
)


# Create a function to save the schema with retry
def save_schema_with_retry(retries=3, delay=0.5):
    """Try to save the schema with retries in case the server isn't ready yet."""
    for attempt in range(retries):
        try:
            pathlib.Path("static").mkdir(exist_ok=True)
            # Use a fixed URL
            schema_url = "http://127.0.0.1:7860/gradio_api/mcp/schema"
            response = requests.get(schema_url, timeout=2)  # Short timeout
            if response.status_code == 200:
                schema = response.json()

                # Keep only the tools we want to expose
                filtered_schema = {
                    k: v for k, v in schema.items()
                    if k in ["sql", "csv", "pdf"]
                }

                with open("static/schema.json", "w") as f:
                    f.write(json.dumps(filtered_schema, indent=2))
                print("Schema saved to static/schema.json")

                # For information, display available tools
                tools_list = ', '.join(filtered_schema.keys())
                print(f"MCP Tools available: {tools_list}")
                return filtered_schema
        except Exception as e:
            if attempt < retries - 1:
                print(
                    f"Attempt {attempt + 1}/{retries} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                print(f"Failed to save schema after {retries} attempts: {e}")
    return None


# Function to save schema in background
def background_save_schema():
    # Wait for server to start
    time.sleep(2.0)
    # Try to save the schema
    save_schema_with_retry(retries=3, delay=1.0)


if __name__ == "__main__":
    # Create and start a thread to save the schema in the background
    schema_thread = threading.Thread(target=background_save_schema)
    schema_thread.daemon = True  # Thread will stop when main program stops
    schema_thread.start()

    print("Starting MCP server...")

    # Enable MCP server for LLM tools access
    # In Gradio 5.29, launch the server in a blocking way (default)
    demo.launch(mcp_server=True, share=False, show_error=True)

    # This code will never be reached because launch() is blocking
    print("Server stopped.")
