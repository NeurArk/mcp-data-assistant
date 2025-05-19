from pathlib import Path
from tools.pdf_tool import PdfReportBuilder


def _count_image_references(pdf_path: Path) -> int:
    """Count occurrences of /Subtype /Image in the raw PDF bytes"""
    with open(pdf_path, "rb") as f:
        content = f.read()
        return content.count(b"/Subtype /Image")


def test_pdf_with_logo_and_chart(tmp_path):
    data = {"a": 1, "b": 2, "c": 3, "grand_total": 6}
    with PdfReportBuilder(tmp_path / "visual.pdf") as builder:
        builder.add_cover("Visual")
        builder.add_section({"title": "Data", "type": "table", "data": data})
        builder.add_section(
            {
                "title": "Chart",
                "type": "chart",
                "chart_spec": {
                    "chart_type": "bar",
                    "labels": list(data.keys()),
                    "values": list(data.values()),
                },
            }
        )
        pdf_path = Path(builder.save())
    assert pdf_path.exists() and pdf_path.stat().st_size > 8000
    assert _count_image_references(pdf_path) >= 2  # logo + chart
