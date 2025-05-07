"""
Professional PDF generator using ReportLab.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Dict, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image
import matplotlib.pyplot as _plt
import tempfile
import os
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)


def _build_table(data: Dict[str, object]) -> Table:
    rows: List[List[object]] = [["Field", "Value"]]
    styles = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]
    for idx, (k, v) in enumerate(data.items(), start=1):
        rows.append([k, v])
        if idx % 2 == 1:  # alternate row shading (skip header row)
            styles.append(("BACKGROUND", (0, idx), (-1, idx), colors.whitesmoke))
        if k == "grand_total":
            styles.append(("FONTNAME", (1, idx), (1, idx), "Helvetica-Bold"))
    return Table(rows, style=TableStyle(styles))


def create_pdf(
    data: Dict[str, object],
    out_path: str | None = None,
    include_chart: bool = True,
) -> str:
    """
    Generate a professional PDF report from provided data.
    
    Creates a PDF document with the given data formatted as a table. Optionally includes
    a bar chart visualization of numeric values, if at least 3 numeric fields are present.
    The PDF includes the company logo if available in the assets directory.
    
    Args:
        data: Dictionary containing the data to include in the report
        out_path: Optional custom path for the generated PDF file (default: reports/report-{timestamp}.pdf)
        include_chart: Whether to include a bar chart visualization of numeric values (default: True)
        
    Returns:
        Absolute path to the generated PDF file
        
    Raises:
        ValueError: If the data dictionary is empty
    """
    if not data:
        raise ValueError("data cannot be empty.")

    timestamp = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    if out_path is None:
        out_path = REPORT_DIR / f"report-{timestamp}.pdf"
    else:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(out_path), pagesize=A4)
    styles = getSampleStyleSheet()
    story: List[object] = []

    # logo (if file exists)
    logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.png"
    if logo_path.exists():
        story.append(
            Image(
                str(logo_path),
                width=80,
                height=80,
                kind="proportional",
                hAlign="CENTER",
            )
        )
        story.append(Spacer(1, 12))  # more air below logo

    story.append(Paragraph("Data Assistant Report", styles["Title"]))
    timestamp_text = f"Generated: {_dt.datetime.now().isoformat(timespec='seconds')}"
    story.append(Paragraph(timestamp_text, styles["Normal"]))
    story.append(Spacer(1, 12))
    story.append(_build_table(data))

    # optional bar chart
    tmp_png = None
    if include_chart:
        numeric_items = {k: v for k, v in data.items() if isinstance(v, (int, float))}
        if len(numeric_items) >= 3:
            labels, values = zip(*numeric_items.items())
            fig, ax = _plt.subplots(figsize=(6, 3.5))
            
            # filter zero values
            filtered = [(k, v) for k, v in numeric_items.items() if v]
            labels, values = zip(*filtered) if filtered else (labels, values)
            
            ax.bar(range(len(labels)), values, color="#143d8d")  # NeurArk blue
            ax.set_ylabel("Value (€)")
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha="right")
            fig.tight_layout()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            fig.savefig(tmp.name, bbox_inches="tight")
            _plt.close(fig)
            story.append(Spacer(1, 24))
            story.append(Image(tmp.name, width=400, height=250))
            tmp_png = tmp.name

    doc.build(story)
    
    # clean temporary PNG
    if tmp_png and os.path.exists(tmp_png):
        os.unlink(tmp_png)
    return str(out_path.resolve())


if __name__ == "__main__":
    demo = {"customer": "ACME", "grand_total": 1234}
    print(create_pdf(demo))