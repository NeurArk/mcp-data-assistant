import gradio as gr

def server_status():
    "A dummy function to show the server is alive."
    return "✅ MCP Data Assistant server is running."

with gr.Blocks() as demo:
    gr.Markdown("# MCP Data Assistant")
    gr.Markdown("This server will expose three tools (SQL query, CSV summary, PDF report).")
    status_btn = gr.Button("Ping server")
    status_btn.click(server_status, outputs=gr.Textbox())

if __name__ == "__main__":
    # mcp_server=True turns this Blocks app into an MCP server
    demo.launch(mcp_server=True, share=False)
