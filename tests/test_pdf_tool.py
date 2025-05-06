import os
import pytest
from pathlib import Path
from tools.pdf_tool import create_pdf

def test_pdf_creation_and_size(tmp_path):
    path = create_pdf({"foo": "bar", "x": 1}, out_path=tmp_path / "test.pdf")
    assert Path(path).exists() and Path(path).stat().st_size > 0

def test_pdf_empty_data():
    with pytest.raises(ValueError):
        create_pdf({})