import subprocess, time, requests, os, signal, sys
import pytest
from gradio_client import Client
from pathlib import Path

def wait_until_ready(url: str, timeout=20):
    start = time.time()
    while time.time() - start < timeout:
        try:
            requests.get(url, timeout=1)
            return True
        except requests.exceptions.ConnectionError:
            time.sleep(0.5)
    return False

@pytest.mark.integration
def test_mcp_end_to_end(tmp_path):
    # Check if database exists
    db_path = Path(__file__).parent.parent / "data" / "sales.db"
    assert db_path.exists(), f"Database not found at {db_path}"
    
    # Start the app in a subprocess
    app_path = Path(__file__).parent.parent / "app.py"
    cwd = Path(__file__).parent.parent
    proc = subprocess.Popen(
        [sys.executable, str(app_path)], 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        cwd=str(cwd)
    )
    try:
        # Wait for server to start
        if not wait_until_ready("http://127.0.0.1:7860"):
            # If server didn't start, capture output to help debug
            stdout, stderr = proc.communicate(timeout=1)
            stdout = stdout.decode('utf-8') if stdout else ""
            stderr = stderr.decode('utf-8') if stderr else ""
            pytest.fail(f"Server did not start in time. STDOUT: {stdout}, STDERR: {stderr}")
        
        # Connect to Gradio API
        client = Client("http://127.0.0.1:7860")
        print(f"Available endpoints: {client.view_api()}")
        
        # Test SQL tool - use the "/predict" endpoint which was automatically created for the Interface
        result = client.predict("SELECT 1 AS one", api_name="/predict")
        assert result == [{"one": 1}]
    finally:
        # Clean up
        os.kill(proc.pid, signal.SIGTERM)
        stdout, stderr = proc.communicate(timeout=10)
        print(f"Server output: {stdout.decode('utf-8') if stdout else ''}")
        print(f"Server errors: {stderr.decode('utf-8') if stderr else ''}")