import subprocess
import time
import requests
import os
import signal
import sys
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
        
        # Test SQL tool
        result = client.predict("SELECT 1 AS one", api_name="/sql")
        assert result == [{"one": 1}]
        
        # Test CSV tool
        csv_result = client.predict("sample_data/people.csv", api_name="/csv") 
        assert csv_result["row_count"] == 3
        assert csv_result["column_count"] == 3
        assert len(csv_result["columns"]) == 3
        
        # Test PDF tool with minimal data
        test_data = {"test_key": "test_value", "test_number": 42}
        pdf_path = client.predict(test_data, None, True, api_name="/pdf")
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1000  # Ensure PDF was created and has content
    finally:
        # Clean up
        os.kill(proc.pid, signal.SIGTERM)
        stdout, stderr = proc.communicate(timeout=10)
        print(f"Server output: {stdout.decode('utf-8') if stdout else ''}")
        print(f"Server errors: {stderr.decode('utf-8') if stderr else ''}")