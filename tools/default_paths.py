# pragma: no cover
"""
Default path configurations for tools.

This module centralizes path configurations to ensure consistent
file access across different components of the application.
"""

import os
from typing import List

# Current working directory
CWD = os.getcwd()

# Standard data directories - we only use data and uploads
DATA_DIR = os.path.join(CWD, "data")
UPLOADS_DIR = os.path.join(CWD, "uploads")

# Create directories if they don't exist
for directory in [DATA_DIR, UPLOADS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Special file for backward compatibility
UPLOADED_CSV_SYMLINK = os.path.join(CWD, "uploaded.csv")


def get_search_paths(file_type: str | None = None) -> List[str]:
    """
    Get a list of paths to search for files of a given type.

    Args:
        file_type: Optional file type (e.g., 'csv', 'pdf') to get specific paths

    Returns:
        List of paths to search in priority order
    """
    # Base paths to search in all cases - priority order
    # We only use uploads, data, and current directory
    paths = [UPLOADS_DIR, DATA_DIR, CWD]

    # File type specific additions
    if file_type == "pdf":
        # Add report directory for PDF files
        reports_dir = os.path.join(CWD, "reports")
        os.makedirs(reports_dir, exist_ok=True)
        paths.append(reports_dir)

    return paths


def find_file(filename: str, file_type: str | None = None) -> str:
    """
    Search for a file in standard locations.

    Args:
        filename: The name of the file to find
        file_type: Optional file type to use type-specific search paths

    Returns:
        Full path to the file if found, otherwise returns the input filename
    """
    # Debug logging
    print(f"Finding file: {filename}, type: {file_type}")

    # If the filename is already an absolute path and exists, return it
    if os.path.isabs(filename) and os.path.exists(filename):
        print(f"  Found existing absolute path: {filename}")
        return filename

    # Check if the file exists in the current directory first
    if os.path.exists(filename):
        full_path = os.path.abspath(filename)
        print(f"  Found in current directory: {full_path}")
        return full_path

    # Check standard locations
    search_paths = get_search_paths(file_type)

    # Look for exact filename first
    for directory in search_paths:
        potential_path = os.path.join(directory, filename)
        if os.path.exists(potential_path):
            print(f"  Found in {directory}: {potential_path}")
            return potential_path

    # Special case for 'uploaded.csv' symlink
    if filename == "uploaded.csv" and os.path.exists(UPLOADED_CSV_SYMLINK):
        print(f"  Found special symlink: {UPLOADED_CSV_SYMLINK}")
        return UPLOADED_CSV_SYMLINK

    # If not found but file_type is provided, check for any file of that type
    if file_type:
        extension = f".{file_type}"
        # Check directories in priority order for files of this type
        for directory in search_paths:
            try:
                files = os.listdir(directory)
                # Sort by modification time (newest first)
                files.sort(
                    key=lambda f: os.path.getmtime(os.path.join(directory, f)),
                    reverse=True,
                )

                # Look for any file with the matching extension
                for file in files:
                    if file.endswith(extension):
                        found_path = os.path.join(directory, file)
                        print(f"  Found by extension in {directory}: {found_path}")
                        return found_path

            except (FileNotFoundError, NotADirectoryError):
                continue

    # Return the original filename if not found
    print(f"  No file found, returning original: {filename}")
    return filename
