# MCP Data Assistant

![CI](https://github.com/NeurArk/mcp-data-assistant/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
📄 [MCP schema](static/schema.json)
🔖 [Latest release](https://github.com/NeurArk/mcp-data-assistant/releases/latest)

**Data Assistant MVP v0.5** – a fully-local Model Context Protocol
server that lets any modern LLM:

* **run_sql** – safely query a SQLite database
* **summarise_csv** – get quick statistics from a CSV file
* **create_pdf** – turn any dict into a one-page PDF report
* **Assistant** – natural language interface with GPT-4.1 mini agent or local qwen3:8b model

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Option 1: Use with OpenAI API
export OPENAI_API_KEY=your_api_key
python app.py          # open http://localhost:7860

# Option 2: Use with local qwen3:8b (see Edge AI setup below)
# No API key required!
python app.py

# CLI demo (requires OpenAI API key)
export OPENAI_API_KEY=your_api_key
./scripts/demo_cli.py "Show me total sales for 2024 and create a PDF report"
```

## Docker
```bash
docker build -t neurark/mcp-data-assistant .
docker run -p 7860:7860 neurark/mcp-data-assistant
# open http://localhost:7860
```

▶ **Demo** — open [`sample_docs/report-demo.pdf`](sample_docs/report-demo.pdf)

## How it works
The app launches Gradio with `mcp_server=True`.  
The LLM discovers three tools via the MCP schema and chains them as
needed (query → analyse → generate report).

The Assistant tab provides a natural language interface allowing users to interact with the tools through conversational prompts. It supports two model options:
- **OpenAI API** with GPT-4.1 mini model (requires API key)
- **Local qwen3:8b** model via Ollama (no API key required)

Built with Python 3.12, Gradio 5.29, SQLModel, Pandas, ReportLab, OpenAI Agents SDK, and Ollama.

## Edge AI Capability (v0.5)

MCP Data Assistant now supports a local qwen3:8b model using Ollama:

1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Run: `ollama pull qwen3:8b` (downloads the 8B parameter model, ~5GB)
3. Make sure Ollama is running: `ollama serve` (if not already running)
4. Start the app and select "Local (qwen3:8b)" in the interface

No API key required when using the local model! The qwen3:8b model supports multilingual requests, reasoning, mathematics, and function calling.

Troubleshooting:
- If you encounter errors, make sure Ollama is running by executing `ollama serve` in a separate terminal
- If you get API errors, try restarting the application
- qwen3:8b requires at least 12GB of RAM for optimal performance
