import gradio as gr
from tools.sql_tool import run_sql
from tools.csv_tool import summarise_csv
from tools.pdf_tool import create_pdf

def server_status() -> str:
    """
    A dummy function to show the server is alive.
    
    Returns:
        str: Status message confirming the server is running
    """
    return "✅ MCP Data Assistant server is running."

with gr.Blocks() as demo:
    gr.Markdown("# MCP Data Assistant")
    gr.Markdown("This server will expose three tools (SQL query, CSV summary, PDF report).")
    
    # Register MCP tools
    run_sql_interface = gr.Interface(
        fn=run_sql,
        inputs=gr.Textbox(label="SQL Query"),
        outputs=gr.JSON(),
        title="SQL Query Tool",
        description="Execute read-only SQL queries",
        examples=["SELECT 1 AS one"]
    )
    
    # Add simple UI components
    status_btn = gr.Button("Ping server")
    status_output = gr.Textbox()
    status_btn.click(server_status, outputs=status_output)

if __name__ == "__main__":
    # Ensure the static folder exists
    import os
    import pathlib
    import json
    import requests
    
    # Enable MCP server for LLM tools access
    app = demo.launch(mcp_server=True, share=False, show_error=True)
    
    # After launch, fetch and save the schema
    try:
        pathlib.Path("static").mkdir(exist_ok=True)
        schema_url = f"{app.local_url}gradio_api/mcp/schema"
        response = requests.get(schema_url)
        if response.status_code == 200:
            with open("static/schema.json", "w") as f:
                f.write(json.dumps(response.json(), indent=2))
            print("Schema saved to static/schema.json")
    except Exception as e:
        print(f"Failed to save schema: {e}")
