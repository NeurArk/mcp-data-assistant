import pytest
from tools.sql_tool import run_sql, _validate_query_is_select


def test_validate_query_accepts_select():
    """Test that _validate_query_is_select accepts a valid SELECT query."""
    # Should not raise any exceptions
    assert _validate_query_is_select("SELECT * FROM orders") is True
    assert (
        _validate_query_is_select("SELECT id, product FROM orders WHERE amount > 100")
        is True
    )
    assert _validate_query_is_select("SELECT COUNT(*) FROM orders") is True


def test_validate_query_rejects_update():
    """Test that _validate_query_is_select raises ValueError for non-SELECT queries."""
    with pytest.raises(ValueError):
        _validate_query_is_select("UPDATE orders SET amount = 100")

    with pytest.raises(ValueError):
        _validate_query_is_select("DELETE FROM orders")

    with pytest.raises(ValueError):
        _validate_query_is_select(
            "INSERT INTO orders VALUES (1, '2024-01-01', 'Test', 99.99)"
        )


def test_run_sql_returns_dict_with_expected_keys():
    """Test that run_sql returns a list of dictionaries with the expected keys."""
    result = run_sql("SELECT id, amount FROM orders LIMIT 1")

    # Check that we get a list with at least one item
    assert isinstance(result, list)
    assert len(result) > 0

    # Check that the first item is a dictionary with the expected keys
    first_row = result[0]
    assert isinstance(first_row, dict)
    assert "id" in first_row
    assert "amount" in first_row
