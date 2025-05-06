# MCP Data Assistant

![CI](https://github.com/NeurArk/mcp-data-assistant/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
📄 [MCP schema](static/schema.json)

**Data Assistant MVP v0.1** – a fully-local Model Context Protocol
server that lets any modern LLM:

* **run_sql** – safely query a SQLite database  
* **summarise_csv** – get quick statistics from a CSV file  
* **create_pdf** – turn any dict into a one-page PDF report  

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py          # open http://localhost:7860
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

Built with Python 3.12, Gradio 5, SQLModel, Pandas and ReportLab.
