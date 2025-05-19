# pragma: no cover
"""
SQL query tool for executing read-only queries against a database.

This module provides functionality to safely execute SELECT queries against
either PostgreSQL (when DB_URL env var is set) or the project's SQLite database,
and return results in a structured format.
"""

import os
import pathlib
from typing import List, Dict, Any

import pandas as pd
from sqlalchemy import create_engine, Engine, text


def get_engine() -> Engine:
    """
    Creates a database engine based on environment settings.

    If DB_URL environment variable starts with postgresql://, returns a PostgreSQL engine.
    Otherwise, returns a SQLite engine pointing to data/sales.db.

    Returns:
        SQLAlchemy Engine object for database connection
    """
    db_url = os.getenv("DB_URL")

    if db_url and db_url.startswith("postgresql://"):
        # Use PostgreSQL if DB_URL is set with postgresql:// protocol
        return create_engine(db_url, pool_pre_ping=True)

    # Default to SQLite
    db_path = pathlib.Path(__file__).parent.parent / "data" / "sales.db"
    sqlite_url = f"sqlite:///{db_path}"
    return create_engine(sqlite_url)


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

    Works with both PostgreSQL (when DB_URL env var is set) and SQLite (default).

    Args:
        query: The SQL query to execute (must be a SELECT statement)

    Returns:
        List of dictionaries where each dictionary represents a row
        with column names as keys and cell values as values

    Raises:
        ValueError: If the query is not a SELECT statement
        Exception: Database-specific errors from the underlying engine
    """
    # Validate that this is a read-only query
    _validate_query_is_select(query)

    # Get database engine (PostgreSQL or SQLite)
    engine = get_engine()

    try:
        # Use pandas to execute the query and convert to dictionaries
        # This works with both SQLite and PostgreSQL
        df = pd.read_sql(text(query), engine)

        # Convert DataFrame to list of dictionaries
        return df.to_dict(orient="records")
    except Exception:
        # Re-raise any database errors
        raise
