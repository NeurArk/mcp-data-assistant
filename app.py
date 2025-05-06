import gradio as gr

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
    status_btn = gr.Button("Ping server")
    status_btn.click(server_status, outputs=gr.Textbox())

if __name__ == "__main__":
    # Ensure the static folder exists and export the schema for docs
    import os, pathlib
    pathlib.Path("static").mkdir(exist_ok=True)
    demo.save_schema("static/schema.json")
    
    # Enable MCP server for LLM tools access
    demo.launch(mcp_server=True, share=False)
