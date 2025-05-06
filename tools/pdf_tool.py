"""
PDF report generator for the MCP Data Assistant.

`create_pdf(data: dict, out_path: str | None = None) -> str`
------------------------------------------------------------
* Builds a one-page A4 PDF using reportlab.
* Shows a title, timestamp, and a table (key | value) for each item
  in *data*.
* Returns the absolute path of the file created.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Dict

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def create_pdf(data: Dict[str, object], out_path: str | None = None) -> str:
    """
    Create a PDF report from the provided data dictionary.
    
    Args:
        data: Dictionary of key-value pairs to include in the report
        out_path: Optional output path, defaults to reports/report-TIMESTAMP.pdf
        
    Returns:
        Absolute path to the created PDF file
        
    Raises:
        ValueError: If data is empty
    """
    if not data:
        raise ValueError("data cannot be empty.")

    timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    if out_path is None:
        out_path = REPORT_DIR / f"report-{timestamp}.pdf"
    else:
        out_path = Path(out_path)

    # Create a new PDF with ReportLab
    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4  # Width and height in points
    
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Data Assistant Report")
    
    # Add timestamp
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 70, 
                f"Generated: {_dt.datetime.now().isoformat(sep=' ', timespec='seconds')}")
    
    # Add data rows
    c.setFont("Helvetica", 12)
    start_y = height - 90
    line_height = 20
    
    for idx, (k, v) in enumerate(data.items(), start=1):
        y = start_y - idx * line_height
        if y < 50:  # avoid writing off-page
            break
        c.drawString(50, y, f"{k}: {v}")
    
    # Save the PDF
    c.save()
    
    return str(out_path.resolve())


if __name__ == "__main__":
    demo_path = create_pdf({"hello": "world", "number": 42})
    print("PDF created at", demo_path)
