"""
CSV summary utility for the MCP Data Assistant.

`summarise_csv(path: str) -> dict`
----------------------------------
* Opens the CSV file using pandas.
* Returns basic statistics: number of rows, columns and
  per-column information (name, pandas-inferred dtype,
  missing value count).
* Validates the path:
    • must exist,
    • must end with `.csv` (case-insensitive).
* Protects memory: raises MemoryError if the file holds more
  than 1,000,000 rows.
"""

from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Dict, List

MAX_ROWS = 1_000_000


def summarise_csv(path: str | Path) -> Dict[str, object]:
    """
    Analyze a CSV file and provide summary statistics.
    
    Opens the CSV file using pandas and returns basic statistics including the number of rows, 
    columns, and per-column information (name, data type, missing value count).
    
    Args:
        path: Path to the CSV file (must exist and have .csv extension)
        
    Returns:
        Dictionary with row_count, column_count, and detailed column information
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file doesn't have a .csv extension
        MemoryError: If the file contains more than 1,000,000 rows
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")

    df = pd.read_csv(path)
    if len(df) > MAX_ROWS:
        raise MemoryError(
            f"CSV too large ({len(df):,} rows). Limit is {MAX_ROWS:,}."
        )

    columns: List[Dict[str, object]] = []
    for col in df.columns:
        series = df[col]
        columns.append(
            {
                "name": col,
                "inferred_type": str(series.dtype),
                "missing_values": int(series.isna().sum()),
            }
        )

    return {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": columns,
    }


if __name__ == "__main__":  # quick manual check
    import json

    print(json.dumps(summarise_csv("sample_data/people.csv"), indent=2))
