from pathlib import Path
import pytest
from tools.pdf_tool import create_pdf

def test_pdf_creation_size(tmp_path):
    sample = {"foo": "bar", "grand_total": 999}
    file_path = create_pdf(sample, out_path=tmp_path / "demo.pdf")
    assert Path(file_path).exists() and Path(file_path).stat().st_size > 1500  # Minimum size in bytes

def test_pdf_empty_data():
    with pytest.raises(ValueError):
        create_pdf({})