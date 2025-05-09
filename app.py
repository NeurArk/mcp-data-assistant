# existing imports
import gradio as gr
import json
import os
import uuid
import shutil
from tools.sql_tool import run_sql
from tools.csv_tool import summarise_csv
from tools.pdf_tool import create_pdf
from tools.default_paths import DATA_DIR, UPLOADS_DIR

# assistant
from agent import answer, _check_ollama_available, session_manager


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
        api_name="sql",
    )

    # REMOVED: csv_handler function - we'll use summarise_csv directly instead
        
    # Create a proper Interface for CSV summary tool
    # This is the primary interface that will be exposed to MCP
    summarise_csv_interface = gr.Interface(
        fn=summarise_csv,  # Use the function directly
        inputs=gr.Textbox(
            label="CSV File Path", 
            placeholder="Path to CSV file (e.g., sample_data/people.csv)",
            value="sample_data/people.csv"
        ),
        outputs=gr.JSON(),
        title="CSV Summary Tool",
        description="Analyze a CSV file and provide summary statistics",
        examples=["sample_data/people.csv"],
        api_name="csv",  # This sets the name for MCP tool
    )
    
    # Create a user-friendly UI version with upload capability
    # This won't be exposed to MCP due to the explicit api_name=False
    with gr.Blocks() as csv_upload_ui:
        gr.Markdown("## CSV Upload & Analysis")
        
        with gr.Tabs():
            with gr.TabItem("Upload CSV"):
                # File upload
                file_upload = gr.File(
                    label="Upload a CSV file",
                    file_types=[".csv"],
                    type="filepath"
                )
                
                # Process uploaded file function
                def process_upload(file):
                    if file is None:
                        return {"error": "No file uploaded"}
                    try:
                        return summarise_csv(file)
                    except Exception as e:
                        return {"error": str(e)}
                
                # Hide function from MCP
                process_upload._hide_from_mcp = True
                
                # UI components
                upload_button = gr.Button("Analyze CSV")
                upload_output = gr.JSON()
                
                # Connect with api_name=False to hide from MCP
                upload_button.click(
                    fn=process_upload, 
                    inputs=file_upload, 
                    outputs=upload_output,
                    api_name=False
                )
                
            with gr.TabItem("File Path"):
                # Path input
                path_input = gr.Textbox(
                    label="CSV File Path",
                    placeholder="Enter path to a CSV file (e.g., sample_data/people.csv)",
                    value="sample_data/people.csv"
                )
                
                # Process path function
                def process_path(path):
                    if not path or not path.strip():
                        return {"error": "No path provided"}
                    try:
                        return summarise_csv(path)
                    except Exception as e:
                        return {"error": str(e)}
                
                # Hide function from MCP
                process_path._hide_from_mcp = True
                
                # UI components
                path_button = gr.Button("Analyze CSV")
                path_output = gr.JSON()
                
                # Connect with api_name=False to hide from MCP
                path_button.click(
                    fn=process_path, 
                    inputs=path_input, 
                    outputs=path_output,
                    api_name=False
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
                    "raw_input": (
                        data_json[:200] + "..." if len(data_json) > 200 else data_json
                    ),
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
                    "received_type": str(type(data)),
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
                label="Report Data (JSON)", value='{"customer": "ACME", "total": 1000}'
            ),
            gr.Textbox(
                label="Output Path (optional)",
                placeholder="Leave empty for default location",
            ),
            gr.Checkbox(label="Include Chart", value=True),
        ],
        outputs=gr.Textbox(label="Generated PDF Path"),
        title="PDF Report Generator",
        description="Create professional PDF reports with data and optional charts",
        examples=[['{"customer": "ACME", "total": 999}', None, True]],
        api_name="pdf",
    )

    # Add simple UI components
    status_btn = gr.Button("Ping server")
    status_output = gr.Textbox()
    # Hide from API and MCP
    status_btn.click(server_status, outputs=status_output, api_name=False)


# Model selector component
with gr.Blocks() as llm_selector:
    gr.Markdown("## Model Selection")

    # Determine default model based on environment
    default_model = (
        "OpenAI API" if os.getenv("OPENAI_API_KEY") else "Local (qwen3:8b)"
    )
    ollama_available = _check_ollama_available()

    # Radio button for model selection
    model_choice = gr.Radio(
        ["OpenAI API", "Local (qwen3:8b)"],
        label="Choose model",
        value=default_model,
        interactive=True,
    )

    # Add visual indicator for active model
    model_indicator = gr.Markdown(
        value=f"""<div style='padding: 8px; border-radius: 4px;
        background-color: {'#e6f7ff' if default_model == 'Local (qwen3:8b)' else '#e6ffe6'};
        border: 1px solid {'#91caff' if default_model == 'Local (qwen3:8b)' else '#52c41a'};
        color: {'#0050b3' if default_model == 'Local (qwen3:8b)' else '#135200'};
        font-weight: bold;
        margin-top: 8px;'>
        {'🖥️ Using Local Model (qwen3:8b)' + (' - Ollama Not Available' if not ollama_available else '')
        if default_model == 'Local (qwen3:8b)' else '☁️ Using OpenAI API (Cloud)'}</div>"""
    )

    # Update indicator on model change
    def update_indicator(model):
        ollama_status = _check_ollama_available()
        local_text = "🖥️ Using Local Model (qwen3:8b)"
        if model == "Local (qwen3:8b)" and not ollama_status:
            local_text += " - ⚠️ Ollama Not Available"

        return f"""<div style='padding: 8px; border-radius: 4px;
        background-color: {'#e6f7ff' if model == 'Local (qwen3:8b)' else '#e6ffe6'};
        border: 1px solid {'#91caff' if model == 'Local (qwen3:8b)' else '#52c41a'};
        color: {'#0050b3' if model == 'Local (qwen3:8b)' else '#135200'};
        font-weight: bold;
        margin-top: 8px;'>
        {local_text if model == 'Local (qwen3:8b)' else '☁️ Using OpenAI API (Cloud)'}</div>"""
    
    # Hide this function from MCP
    update_indicator._hide_from_mcp = True
    
    model_choice.change(update_indicator, inputs=model_choice, outputs=model_indicator, api_name=False)

# ---------- Assistant tab ----------
with gr.Blocks() as assistant_chat:
    gr.Markdown("# NeurArk Data Assistant")

    # Embed model selector
    llm_selector.render()
    
    # Add CSV file upload for the chat interface
    with gr.Row():
        with gr.Column(scale=2):
            # Create a file upload component
            chat_csv_upload = gr.File(
                label="Upload a CSV file to analyze",
                file_types=[".csv"],
                type="filepath"
            )
            
            # Display status of uploaded file
            csv_status = gr.Markdown("No CSV file uploaded")
            
            def update_csv_status(file):
                if file is None:
                    return "No CSV file uploaded"
                return f"✅ CSV file uploaded: **{os.path.basename(file)}**"
            
            # Hide this function from MCP
            update_csv_status._hide_from_mcp = True
            
            chat_csv_upload.change(update_csv_status, inputs=chat_csv_upload, outputs=csv_status, api_name=False)
            
        with gr.Column(scale=1):
            # Examples of questions about CSV
            gr.Markdown("## Example CSV questions")
            gr.Markdown("- Summarize the CSV file I uploaded")
            gr.Markdown("- What is the average age in this data?")
            gr.Markdown("- Create a PDF report from this CSV")
    
    # Modified chat interface to use selected model and include file info
    chatbot = gr.Chatbot(height=500, type="messages")
    msg = gr.Textbox(label="Ask something about the data or any other question...")
    clear = gr.Button("Clear")

    # Define the respond function - simplified approach
    def respond(message, history, model_choice, csv_file, session_id=None, prev_result=None):
        """Chat response function for the assistant.
        
        This function uses LLM (OpenAI or Ollama) to respond to user messages and integrates
        with uploaded CSV files.
        
        Args:
            message: User's message
            history: Chat history for display in Gradio UI
            model_choice: Selected model
            csv_file: Path to uploaded CSV file if available
            session_id: Session identifier for maintaining conversation state
            prev_result: Previous Runner result object for conversation continuity
        """
        # Create a session ID if None
        if not session_id:
            session_id = str(uuid.uuid4())
            print(f"Created new session: {session_id}")
        else:
            print(f"Using existing session: {session_id}")
            print(f"Gradio history has {len(history)} messages")
            
        # Log if we have a previous result object
        if prev_result:
            print(f"Using previous result object for conversation continuity")
        else:
            print("No previous result object available")
            
        provider = "ollama" if model_choice == "Local (qwen3:8b)" else "openai"
        
        # If a CSV file is uploaded, register it with the session
        if csv_file:
            # Log the uploaded file
            print(f"DEBUG - CSV file has been uploaded: {csv_file}")
            
            # Register the file with the session manager
            session_manager.register_file(session_id, "csv", csv_file)
            print(f"Registered CSV file with session {session_id}: {csv_file}")
            
            # Create symbolic links in standard locations for compatibility
            try:
                # Use the standard uploads directory from default_paths
                os.makedirs(UPLOADS_DIR, exist_ok=True)
                
                # Create a unique filename in the uploads directory
                file_basename = os.path.basename(csv_file)
                session_path = f"{UPLOADS_DIR}/{session_id[-8:]}_{file_basename}"
                standard_path = "./uploaded.csv"
                
                # Remove existing files/symlinks if they exist
                for path in [session_path, standard_path]:
                    if os.path.exists(path):
                        if os.path.islink(path):
                            os.remove(path)
                        elif os.path.isfile(path):
                            os.remove(path)
                
                # Copy the file to the uploads directory (more reliable than symlinks)
                shutil.copy2(csv_file, session_path)
                
                # Create symlink for backward compatibility
                try:
                    os.symlink(session_path, standard_path)
                except OSError as e:
                    print(f"Warning: Could not create symlink: {e}")
                    # On some systems symlinks may fail, so create a copy instead
                    shutil.copy2(session_path, standard_path)
                
                print(f"CSV file saved to: {session_path}")
                # The agent will automatically find the file in the uploads directory
            except Exception as e:
                print(f"Error handling uploaded file: {str(e)}")
        
        # Get the response from the assistant with session context
        response, new_result = answer(
            prompt=message, 
            provider=provider, 
            session_id=session_id,
            prev_result=prev_result
        )
        
        # DEBUG - Log the response type and content
        print(f"DEBUG - Response type: {type(response)}")
        print(f"DEBUG - Response content length: {len(response) if isinstance(response, str) else 'not a string'}")
        prefix = response[:100] if isinstance(response, str) else 'not a string'
        print(f"DEBUG - Response content starts with: {prefix}")

        # Nettoyage des balises <think> dans la réponse pour qwen3:8b
        if isinstance(response, str) and "<think>" in response:
            # Supprimer les balises think et leur contenu
            import re
            cleaned_response = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL).strip()
            print(f"DEBUG - Cleaned response: {cleaned_response[:100]}")
            response = cleaned_response

        # Return the result as messages with role/content format for display
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

        # Return updated history, persist session ID, and the result object for next call
        return "", history, session_id, new_result
    
    # Hide this function from MCP
    respond._hide_from_mcp = True

    # Create state for maintaining the session ID and previous result
    session_state = gr.State(None)
    # State to store the previous result object for conversation continuity
    prev_result_state = gr.State(None)
    
    # Submit with api_name=False to hide from MCP
    msg.submit(
        respond, 
        [msg, chatbot, model_choice, chat_csv_upload, session_state, prev_result_state], 
        [msg, chatbot, session_state, prev_result_state], 
        api_name=False
    )
    
    # Define clear function and hide from MCP
    def clear_chat(session_id):
        """Clear the chat history by creating a new session."""
        # Simplement créer une nouvelle session, toujours vide et propre
        new_session_id = session_manager.create_session()
        print(f"Créé une nouvelle session: {new_session_id}")

        # Effacer l'historique visuel
        empty_history = []

        # Renvoyer la nouvelle session, sans contexte précédent
        return empty_history, new_session_id, None
    
    clear_chat._hide_from_mcp = True
    
    # Use api_name=False to hide from API/MCP
    # Le bouton Clear démarre une nouvelle session, pour un dialogue complètement frais
    clear.click(
        clear_chat, 
        inputs=session_state,
        outputs=[chatbot, session_state, prev_result_state],  # Reset chat, keep ID, reset result
        queue=False, 
        api_name=False
    )


# ---------- Tabs UI -----------------
demo = gr.TabbedInterface(
    [tools_demo, csv_upload_ui, assistant_chat],
    ["Tools API", "CSV Upload & Analysis", "Assistant"],
    title="NeurArk MCP Data Assistant",
)


# Function to check temp directory access - not used for MCP
def check_temp_directory_access():
    """Check temporary directory access and set allowed paths."""
    import tempfile
    temp_dir = tempfile.gettempdir()
    gradio_temp = os.path.join(temp_dir, "gradio")
    
    # Ensure standard directories exist
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Get absolute paths for proper environment variable setting
    cwd = os.getcwd()
    
    # Print out the directories that need to be accessible
    print(f"Temp directory: {temp_dir}")
    print(f"Gradio temp directory: {gradio_temp}")
    print(f"Uploads directory: {UPLOADS_DIR}")
    print(f"Data directory: {DATA_DIR}")
    
    # Make sure environment variable is set to allow access to all needed directories
    os.environ["GRADIO_ALLOWED_PATHS"] = f"{temp_dir},{gradio_temp},{UPLOADS_DIR},{DATA_DIR},{cwd}"
    print(f"Setting GRADIO_ALLOWED_PATHS to: {os.environ.get('GRADIO_ALLOWED_PATHS')}")
    
    return temp_dir


# No schema manipulation functions needed - Gradio 5.29 handles MCP schema automatically


if __name__ == "__main__":
    # Configure access to temporary and data directories
    temp_dir = check_temp_directory_access()
    
    # Ensure all data directories exist
    for directory in [DATA_DIR, UPLOADS_DIR]:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensuring directory exists: {directory}")
    
    print("Starting MCP server...")
    
    # Enable MCP server for LLM tools access with allowed_paths configuration
    # In Gradio 5.29, launch the server in a blocking way (default)
    demo.launch(
        mcp_server=True,  # Enable MCP to expose tools to LLMs
        share=False,      # Don't create a public link
        show_error=True,  # Show detailed error messages
        allowed_paths=[
            temp_dir, 
            DATA_DIR,     # Data directory
            UPLOADS_DIR,  # Uploads directory 
            "."           # Allow access to current directory for uploaded.csv symlink
        ],  # Allow access to standard directories
        # No need to manipulate the schema - Gradio handles this automatically
    )

    # This code will never be reached because launch() is blocking
    print("Server stopped.")
