import os
import pytest
from tools.csv_tool import summarise_csv

SAMPLE = "sample_data/people.csv"

def test_summary_keys():
    info = summarise_csv(SAMPLE)
    assert set(info) == {"row_count", "column_count", "columns"}
    assert info["row_count"] == 3
    assert info["column_count"] == 3
    assert isinstance(info["columns"], list)

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        summarise_csv("no_such_file.csv")

def test_wrong_extension(tmp_path):
    txt = tmp_path / "dummy.txt"
    txt.write_text("hello")
    with pytest.raises(ValueError):
        summarise_csv(txt)