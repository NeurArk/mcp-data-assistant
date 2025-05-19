# pragma: no cover
"""
CSV summary utility for the MCP Data Assistant.

`summarise_csv(file_input: str | Path | FileUpload) -> dict`
----------------------------------
* Opens the CSV file using pandas.
* Returns basic statistics: number of rows, columns and
  per-column information (name, pandas-inferred dtype,
  missing value count).
* Accepts:
    • Path as string or Path object (file must exist),
    • Uploaded file from Gradio interface.
* Validates the file:
    • must exist,
    • must have `.csv` extension (case-insensitive).
* Protects memory: raises MemoryError if the file holds more
  than 1,000,000 rows.
* Intelligent file discovery:
    • Searches in standard locations (/uploads, /data)
    • Handles both relative and absolute paths
    • Can find the most recently uploaded CSV if no specific file is mentioned
"""

from __future__ import annotations

import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
from .default_paths import find_file

MAX_ROWS = 1_000_000


def summarise_csv(file_input: Any) -> Dict[str, object]:
    """
    Analyze a CSV file and provide summary statistics.

    Opens the CSV file using pandas and returns basic statistics including the number of rows,
    columns, and per-column information (name, data type, missing value count).

    This function will automatically search for the CSV file in standard locations:
    - /uploads/ directory (prioritized for uploaded files)
    - /data/ directory
    - The current directory
    - Using the 'uploaded.csv' symlink if present

    Args:
        file_input: Path to the CSV file or keyword
            This can be:
            - A specific file path (relative or absolute)
            - A filename like "data.csv" (will be searched in standard locations)
            - The exact string "uploaded.csv" to use the most recently uploaded file
            - The strings "find", "latest", or any similar term to get the most recent CSV file
            - A file object from Gradio interface with a name attribute

    Returns:
        Dictionary with row_count, column_count, and detailed column information

    Raises:
        FileNotFoundError: If the file doesn't exist after search attempts
        ValueError: If the file doesn't have a .csv extension
        MemoryError: If the file contains more than 1,000,000 rows
    """
    # Debug the input
    print(
        f"DEBUG CSV TOOL - Input type: {type(file_input)}, Value: {str(file_input)[:100]}"
    )

    # Handle different input types (including None)
    if file_input is None:
        print("DEBUG CSV TOOL - No input provided, trying to find any CSV file")
        # Try to find the most recent CSV file in standard locations
        file_path = find_file("any.csv", file_type="csv")
        if file_path == "any.csv":  # No file found
            raise ValueError(
                "No file provided and no CSV files found in standard locations."
            )
    elif isinstance(file_input, (str, Path)):
        # Case 1: Input is a string or Path object
        file_input_str = str(file_input)  # Convert Path to string if needed

        # Special keywords for file discovery
        if file_input_str.lower() in ["find", "latest", "any", "recent", "uploaded"]:
            print(f"DEBUG CSV TOOL - Using discovery mode for '{file_input_str}'")
            file_path = find_file("any.csv", file_type="csv")
            if file_path == "any.csv":  # No file found
                raise ValueError(
                    f"No CSV files found in standard locations when searching for '{file_input_str}'."
                )
        else:
            # Try to find file in standard locations
            print(f"DEBUG CSV TOOL - Searching for '{file_input_str}'")
            file_path = find_file(file_input_str, file_type="csv")
    elif hasattr(file_input, "name"):
        # Case 2: Input is a file object with a name attribute (from Gradio upload)
        file_path = file_input.name
        print(f"DEBUG CSV TOOL - Using uploaded file: {file_path}")
    else:
        # Unknown type
        print(
            f"DEBUG CSV TOOL - Unsupported input type: {type(file_input)}, value: {file_input}"
        )
        raise ValueError(
            f"Unsupported input type: {type(file_input)}. Please provide a valid file path."
        )

    # Validate the file path
    if not file_path:
        raise ValueError(
            "Could not determine file path. Please provide a valid file path."
        )

    # Check if the file exists and has the correct extension
    path_obj = Path(file_path)
    if not path_obj.exists():
        # One last chance - is this a simple filename in current dir?
        base_name = os.path.basename(file_path)
        if os.path.exists(base_name):
            path_obj = Path(base_name)
            file_path = base_name
        else:
            raise FileNotFoundError(f"No such file: {file_path}")

    if path_obj.suffix.lower() != ".csv":
        raise ValueError("Only CSV files are supported.")

    # Print more debug info
    print(f"DEBUG CSV TOOL - Final file_path: {file_path}")
    print(f"DEBUG CSV TOOL - File exists: {path_obj.exists()}")
    print(f"DEBUG CSV TOOL - Is file: {path_obj.is_file()}")

    try:
        # Read the CSV file
        df = pd.read_csv(file_path)
        if len(df) > MAX_ROWS:
            raise MemoryError(
                f"CSV too large ({len(df):,} rows). Limit is {MAX_ROWS:,}."
            )

        # Process the dataframe
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

        # Return the analysis
        return {
            "row_count": int(len(df)),
            "column_count": int(len(df.columns)),
            "columns": columns,
            "filename": os.path.basename(file_path),
            "filepath": file_path,  # Include full path for reference
        }
    except Exception as e:
        # Provide a detailed error message to help with debugging
        print(f"DEBUG CSV TOOL - Error analyzing CSV: {str(e)}")
        raise ValueError(f"Error analyzing CSV file at {file_path}: {str(e)}")


if __name__ == "__main__":  # quick manual check
    import json

    print(json.dumps(summarise_csv("sample_data/people.csv"), indent=2))
