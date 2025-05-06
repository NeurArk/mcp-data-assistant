"""
SQL query tool for executing read-only queries against the local database.

This module provides functionality to safely execute SELECT queries against
the project's SQLite database and return results in a structured format.
"""
import os
import sqlite3
import pathlib
from typing import List, Dict, Any


def _validate_query_is_select(query: str) -> bool:
    """
    Validate that the query is a read-only SELECT statement.
    
    Args:
        query: The SQL query to validate
        
    Returns:
        True if the query is valid, otherwise raises ValueError
        
    Raises:
        ValueError: If the query is not a SELECT statement
    """
    # Normalize the query by removing extra whitespace
    normalized_query = query.strip().upper()
    
    # Check if the query starts with SELECT
    if not normalized_query.startswith("SELECT "):
        raise ValueError("Only SELECT queries are allowed for security reasons")
    
    # Check for disallowed keywords that might modify data
    disallowed_keywords = ["INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE"]
    for keyword in disallowed_keywords:
        if f" {keyword} " in f" {normalized_query} ":
            raise ValueError(f"Query contains disallowed keyword: {keyword}")
    
    return True


def run_sql(query: str) -> List[Dict[str, Any]]:
    """
    Execute a read-only SQL query and return results as a list of dictionaries.
    
    Args:
        query: The SQL query to execute (must be a SELECT statement)
        
    Returns:
        List of dictionaries where each dictionary represents a row
        with column names as keys and cell values as values
        
    Raises:
        ValueError: If the query is not a SELECT statement
        sqlite3.Error: If there's an issue with the database or query execution
    """
    # Validate that this is a read-only query
    _validate_query_is_select(query)
    
    # Path to the SQLite database
    db_path = pathlib.Path(__file__).parent.parent / "data" / "sales.db"
    
    # Execute the query
    with sqlite3.connect(db_path) as conn:
        # Configure connection to return rows as dictionaries
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            # Convert sqlite3.Row objects to dictionaries
            rows = [dict(row) for row in cursor.fetchall()]
            return rows
        except sqlite3.Error as e:
            # Re-raise any SQLite errors so they can be handled by the caller
            raise
