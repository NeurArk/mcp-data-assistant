"""
Tests for PostgreSQL support in SQL Tool.

These tests require Docker to be running and available.
"""

import os
import time
import socket
import subprocess
import pytest
import sqlalchemy

from tools.sql_tool import run_sql, get_engine


def is_port_open(host, port, timeout=1):
    """Check if a port is open on the host."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        s.shutdown(socket.SHUT_RDWR)
        return True
    except (socket.timeout, ConnectionRefusedError):
        return False
    finally:
        s.close()


def is_docker_available():
    """Check if Docker is available."""
    try:
        subprocess.run(
            ["docker", "--version"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


@pytest.fixture(scope="module")
def postgres_container():
    """
    Start a PostgreSQL container for testing.

    This fixture:
    1. Checks if Docker is available
    2. Starts a postgres:16-alpine container
    3. Waits for it to be ready
    4. Creates a test table and inserts data
    5. Tears down the container after tests
    """
    # Skip if Docker is not available
    if not is_docker_available():
        pytest.skip("Docker is not available")

    # Start PostgreSQL container
    container_id = subprocess.check_output(
        [
            "docker",
            "run",
            "--rm",
            "-d",
            "-p",
            "5432:5432",
            "-e",
            "POSTGRES_PASSWORD=pass",
            "-e",
            "POSTGRES_DB=demo",
            "postgres:16-alpine",
        ],
        text=True,
    ).strip()

    # Wait for PostgreSQL to be ready
    connection_ready = False
    for _ in range(30):  # Try for 30 seconds
        if is_port_open("localhost", 5432):
            time.sleep(2)  # Give PostgreSQL a bit more time to initialize
            try:
                # Try to actually connect to verify PostgreSQL is ready
                test_conn = sqlalchemy.create_engine(
                    "postgresql://postgres:pass@localhost:5432/demo",
                    pool_pre_ping=True,
                    connect_args={"connect_timeout": 5},
                ).connect()
                test_conn.close()
                connection_ready = True
                break
            except Exception:
                # Connection not ready yet
                time.sleep(1)
        else:
            time.sleep(1)

    if not connection_ready:
        # Force cleanup if we couldn't connect
        subprocess.run(["docker", "kill", container_id], check=False)
        pytest.skip("PostgreSQL container did not become ready - skipping test")

    # Set DB_URL for the tests
    os.environ["DB_URL"] = "postgresql://postgres:pass@localhost:5432/demo"

    # Create test table and insert data
    engine = get_engine()
    try:
        with engine.connect() as conn:
            conn.execute(
                sqlalchemy.text(
                    """
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                date TEXT,
                product TEXT,
                amount NUMERIC(10, 2)
            )
            """
                )
            )

            # Insert some test data
            conn.execute(
                sqlalchemy.text(
                    """
            INSERT INTO orders (date, product, amount) VALUES
            ('2025-01-01', 'Widget A', 123.45),
            ('2025-01-02', 'Widget B', 67.89),
            ('2025-01-03', 'Gizmo', 456.78)
            """
                )
            )

            conn.commit()
    except Exception as e:
        # Force cleanup if setup failed
        subprocess.run(["docker", "kill", container_id], check=False)
        pytest.skip(f"Skipping PostgreSQL tests: {e}")

    yield  # Run the tests

    # Cleanup
    subprocess.run(["docker", "kill", container_id], check=False)
    if "DB_URL" in os.environ:
        del os.environ["DB_URL"]


@pytest.mark.usefixtures("postgres_container")
def test_postgres_connection():
    """Test that we can connect to PostgreSQL when DB_URL is set."""
    engine = get_engine()
    assert str(engine.url).startswith("postgresql://")
    # Ensure we can actually connect (if this fails, the test will skip)
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text("SELECT 1")).scalar_one()
        assert result == 1


@pytest.mark.usefixtures("postgres_container")
def test_postgres_run_sql():
    """Test that run_sql works with PostgreSQL."""
    # Count rows
    result = run_sql("SELECT COUNT(*) as count FROM orders")
    assert len(result) == 1
    assert result[0]["count"] == 3

    # Get actual data
    result = run_sql("SELECT * FROM orders ORDER BY id")
    assert len(result) == 3
    assert result[0]["product"] == "Widget A"
    assert result[1]["product"] == "Widget B"
    assert result[2]["product"] == "Gizmo"
