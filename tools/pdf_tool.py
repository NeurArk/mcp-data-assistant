"""
Professional PDF generator using ReportLab.
"""

from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Image,
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Flowable,
)
import matplotlib.pyplot as _plt

REPORT_DIR = Path(__file__).resolve().parent.parent / "reports"
REPORT_DIR.mkdir(exist_ok=True)


class PdfReportBuilder:
    """Helper class to build multi-page PDF reports."""

    def __init__(self, out_path: str | Path):
        self.out_path = Path(out_path)
        self.story: List[Flowable] = []
        self.tmp_pngs: List[str] = []
        self.styles = getSampleStyleSheet()
        self.doc = SimpleDocTemplate(str(self.out_path), pagesize=A4)

    def add_cover(
        self,
        title: str,
        logo_path: str | None = None,
        summary: str | None = None,
    ) -> None:
        """Insert a cover page with optional logo and summary."""
        if logo_path and Path(logo_path).exists():
            self.story.append(
                Image(
                    str(logo_path),
                    width=80,
                    height=80,
                    kind="proportional",
                    hAlign="CENTER",
                )
            )
            self.story.append(Spacer(1, 12))
        self.story.append(Paragraph(title, self.styles["Title"]))
        timestamp_text = (
            f"Generated: {_dt.datetime.now().isoformat(timespec='seconds')}"
        )
        self.story.append(Paragraph(timestamp_text, self.styles["Normal"]))
        if summary:
            box = Table(
                [[Paragraph(summary, self.styles["Normal"])]],
                style=TableStyle(
                    [
                        ("BOX", (0, 0), (-1, -1), 0.25, colors.black),
                        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
                    ]
                ),
            )
            self.story.append(Spacer(1, 12))
            self.story.append(box)
        self.story.append(PageBreak())

    def add_section(self, section: Dict[str, Any]) -> None:
        """Add a paragraph, table or chart section."""
        self.story.append(Paragraph(section.get("title", ""), self.styles["Heading2"]))
        stype = section.get("type")
        if stype == "paragraph":
            self.story.append(Paragraph(section.get("text", ""), self.styles["Normal"]))
        elif stype == "table":
            table_data = section.get("data", {})
            if isinstance(table_data, dict):
                table = _build_table(table_data)
            else:
                table = _build_table_from_list(table_data)
            self.story.append(table)
        elif stype == "chart":
            spec = section.get("chart_spec", {})
            specs = spec if isinstance(spec, list) else [spec]
            for cs in specs:
                png = create_chart(cs)
                width = cs.get("width", 400)
                height = cs.get("height", 250)
                self.story.append(Image(png, width=width, height=height))
                self.tmp_pngs.append(png)
        else:
            self.story.append(
                Paragraph("Unsupported section type", self.styles["Italic"])
            )
        self.story.append(Spacer(1, 12))

    def save(self) -> str:
        """Finalize the PDF and clean up temporary files."""
        self.doc.build(self.story)
        for png in self.tmp_pngs:
            if os.path.exists(png):
                os.unlink(png)
        return str(self.out_path.resolve())

    def __enter__(self) -> "PdfReportBuilder":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        for png in self.tmp_pngs:
            if os.path.exists(png):
                os.unlink(png)


def _build_table(data: Dict[str, object]) -> Table:
    """
    Build a ReportLab Table from a dictionary of data.
    Smartly processes nested structures for better presentation.
    """
    rows: List[List[object]] = [["Field", "Value"]]
    styles = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]

    # Special case handling: if we have data with a 'title' and 'data' field
    # where data is a list, process them specially for better presentation
    if (
        "title" in data
        and "data" in data
        and isinstance(data["data"], list)
        and len(data["data"]) > 0
    ):
        # First, add the title
        rows.append(["title", data["title"]])
        styles.append(("BACKGROUND", (0, 1), (-1, 1), colors.whitesmoke))

        # Process the items in the data list directly instead of as a string
        if all(isinstance(item, dict) for item in data["data"]):
            # Start from row 2 (after title)
            for i, item_dict in enumerate(data["data"], start=2):
                for key, value in item_dict.items():
                    rows.append([key, value])
                    if i % 2 == 1:  # alternate row shading
                        row_idx = len(rows) - 1
                        styles.append(
                            (
                                "BACKGROUND",
                                (0, row_idx),
                                (-1, row_idx),
                                colors.whitesmoke,
                            )
                        )

            # Add any other keys that aren't title or data
            other_keys = {k: v for k, v in data.items() if k not in ["title", "data"]}
            for i, (k, v) in enumerate(other_keys.items(), start=len(rows)):
                rows.append([k, v])
                if i % 2 == 1:  # alternate row shading
                    row_idx = len(rows) - 1
                    styles.append(
                        ("BACKGROUND", (0, row_idx), (-1, row_idx), colors.whitesmoke)
                    )

            return Table(rows, style=TableStyle(styles))

    # Standard processing for all other cases
    for idx, (k, v) in enumerate(data.items(), start=1):
        # Convert non-primitive values to better string representation
        if (
            isinstance(v, list)
            and len(v) > 0
            and all(isinstance(item, dict) for item in v)
        ):
            # If it's a list of dictionaries, try to format it better
            formatted_items = []
            for item in v:
                formatted_item = ", ".join(
                    f"{sub_k}: {sub_v}" for sub_k, sub_v in item.items()
                )
                formatted_items.append(formatted_item)
            v = "\n".join(formatted_items)
        elif isinstance(v, (dict, list)):
            # For other complex types, use basic string representation
            v = str(v)

        rows.append([k, v])

        # Alternate row shading for readability
        if idx % 2 == 1:  # alternate row shading (skip header row)
            styles.append(("BACKGROUND", (0, idx), (-1, idx), colors.whitesmoke))

    # Ensure we have at least one data row
    if len(rows) == 1:
        rows.append(["No data", ""])

    return Table(rows, style=TableStyle(styles))


def _build_table_from_list(data: List[Any]) -> Table:
    """Create a table from a list of dicts or rows."""
    if not data:
        return Table([["No data"]])

    if all(isinstance(row, dict) for row in data):
        headers = sorted({k for row in data for k in row.keys()})
        rows = [headers]
        for row in data:
            rows.append([row.get(h, "") for h in headers])
    else:
        rows = data

    styles = [
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
    ]
    return Table(rows, style=TableStyle(styles))


def create_chart(chart_spec: Dict[str, Any]) -> str:
    """Generate a chart image from a specification and return PNG path."""
    chart_type = chart_spec.get("chart_type", "bar")
    labels = chart_spec.get("labels", [])
    values = chart_spec.get("values", [])
    color = chart_spec.get("color", "#143d8d")
    width = float(chart_spec.get("width", 6))
    height = float(chart_spec.get("height", 3.5))
    fig, ax = _plt.subplots(figsize=(width, height))

    if chart_type == "bar":
        ax.bar(labels, values, color=color)
    elif chart_type == "pie":
        ax.pie(values, labels=labels, autopct="%1.1f%%")
    elif chart_type == "line":
        ax.plot(labels, values, marker="o", color=color)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")

    fig.tight_layout()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name, bbox_inches="tight")
    _plt.close(fig)
    return tmp.name


def create_pdf(
    data: Dict[str, object],
    out_path: str | None = None,
    include_chart: bool = True,
) -> str:
    """
    Generate a professional PDF report from provided data.

    Creates a PDF document with the given data formatted as a table.
    Optionally includes a bar chart visualization of numeric values,
    if at least 3 numeric fields are present.
    The PDF includes the company logo if available in the assets directory.

    Args:
        data: Dictionary containing the data to include in the report
        out_path: Optional custom path for the generated PDF file
            (default: reports/report-{timestamp}.pdf)
        include_chart: Whether to include a bar chart visualization
            of numeric values (default: True)

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

    logo_default = Path(__file__).resolve().parent.parent / "assets" / "logo.png"

    builder = PdfReportBuilder(out_path)

    has_sections = isinstance(data, dict) and "sections" in data

    if has_sections:
        cover = data.get("cover", {})
        builder.add_cover(
            data.get("title", "Data Assistant Report"),
            cover.get(
                "logo_path", str(logo_default) if logo_default.exists() else None
            ),
            data.get("summary"),
        )
        for ins in data.get("insights", []):
            builder.add_section({"title": "", "type": "paragraph", "text": ins})
        for section in data.get("sections", []):
            builder.add_section(section)
    else:
        builder.add_cover(
            "Data Assistant Report",
            str(logo_default) if logo_default.exists() else None,
        )
        builder.add_section({"title": "Data", "type": "table", "data": data})
        if include_chart:
            numeric_items = {
                k: v for k, v in data.items() if isinstance(v, (int, float))
            }
            if len(numeric_items) >= 3:
                labels, values = zip(*numeric_items.items())
                chart_spec = {"chart_type": "bar", "labels": labels, "values": values}
                builder.add_section(
                    {"title": "Chart", "type": "chart", "chart_spec": chart_spec}
                )

    return builder.save()


if __name__ == "__main__":
    demo = {"customer": "ACME", "grand_total": 1234}
    print(create_pdf(demo))
