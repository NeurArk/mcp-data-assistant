from pathlib import Path
import json
import pytest
import traceback
from tools.pdf_tool import PdfReportBuilder, create_pdf, _build_table


def test_pdf_creation_size(tmp_path):
    sample = {"foo": "bar", "grand_total": 999}
    with PdfReportBuilder(tmp_path / "test.pdf") as builder:
        builder.add_cover("Report")
        builder.add_section({"title": "Data", "type": "table", "data": sample})
        file_path = builder.save()
    assert Path(file_path).exists()
    assert Path(file_path).stat().st_size > 1000


def test_pdf_empty_data():
    with pytest.raises(ValueError):
        create_pdf({})


def test_table_builder():
    """Test the table builder function separately to isolate issues."""
    try:
        data = {"customer": "Test", "value": 123, "grand_total": 456}
        table = _build_table(data)
        assert table is not None
    except Exception as e:
        print(f"Table builder failed: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"Table builder failed: {str(e)}")


def test_pdf_with_different_data_types(tmp_path):
    """Test PDF creation with various data types."""
    try:
        # Mix of data types
        sample = {
            "string": "text value",
            "integer": 42,
            "float": 3.14159,
            "boolean": True,
            "none_value": None,
            "grand_total": 999,
        }
        with PdfReportBuilder(tmp_path / "datatypes.pdf") as builder:
            builder.add_cover("Types")
            builder.add_section({"title": "Data", "type": "table", "data": sample})
            file_path = builder.save()
        assert Path(file_path).exists()
    except Exception as e:
        print(f"PDF creation with mixed data types failed: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"PDF creation failed: {str(e)}")


def test_pdf_from_json_string(tmp_path):
    """Test PDF creation from JSON string similar to agent use case."""
    try:
        # JSON string similar to what the agent might produce
        json_str = """
        {
            "title": "Sales Report",
            "customer": "ACME Inc",
            "total": 1282.38,
            "year": 2024,
            "items": 42,
            "grand_total": 1282.38
        }
        """
        # Parse JSON to dict
        data = json.loads(json_str)
        with PdfReportBuilder(tmp_path / "from_json.pdf") as builder:
            builder.add_cover(data.get("title", "Report"))
            builder.add_section({"title": "Data", "type": "table", "data": data})
            file_path = builder.save()
        assert Path(file_path).exists()
    except Exception as e:
        print(f"PDF creation from JSON string failed: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"PDF creation failed: {str(e)}")


def test_pdf_with_sql_like_data(tmp_path):
    """Test PDF creation with data structure similar to SQL query results."""
    try:
        # Similar to what might come from SQL query results
        sql_results = [
            {"year": 2024, "month": "January", "sales": 456.78},
            {"year": 2024, "month": "February", "sales": 345.6},
            {"year": 2024, "month": "March", "sales": 480.0},
        ]
        # Convert to format expected by PDF tool
        data = {
            "title": "Sales Report 2024",
            "total_sales": sum(item["sales"] for item in sql_results),
            "data_source": "sales.db",
        }
        # Add each row from SQL results
        for i, item in enumerate(sql_results, 1):
            data[f"month_{i}"] = item["month"]
            data[f"sales_{i}"] = item["sales"]
        # Add grand total
        data["grand_total"] = data["total_sales"]
        with PdfReportBuilder(tmp_path / "sql_results.pdf") as builder:
            builder.add_cover(data["title"])
            builder.add_section({"title": "Data", "type": "table", "data": data})
            file_path = builder.save()
        assert Path(file_path).exists()
    except Exception as e:
        print(f"SQL results PDF creation failed: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"PDF creation failed: {str(e)}")


def test_pdf_without_chart(tmp_path):
    """Test PDF creation with chart disabled."""
    sample = {"customer": "No Chart Test", "value": 500, "grand_total": 500}
    with PdfReportBuilder(tmp_path / "no_chart.pdf") as builder:
        builder.add_cover("No Chart Test")
        builder.add_section({"title": "Data", "type": "table", "data": sample})
        file_path = builder.save()
    assert Path(file_path).exists()


def test_pdf_with_edge_cases(tmp_path):
    """Test PDF creation with edge cases."""
    # Long text
    long_text = (
        "This is a very long text that should be wrapped properly in the PDF table "
    ) * 5
    data = {
        "title": "Edge Case Test",
        "long_description": long_text,
        "value_1": 100,
        "value_2": 200,
        "value_3": 300,
        "grand_total": 600,
    }
    with PdfReportBuilder(tmp_path / "edge_case.pdf") as builder:
        builder.add_cover(data["title"])
        builder.add_section({"title": "Data", "type": "table", "data": data})
        file_path = builder.save()
    assert Path(file_path).exists()


def test_wrapper_function(tmp_path):
    """Test the PDF wrapper function similar to app.py implementation."""

    # Simulate the create_pdf_wrapper function from app.py
    def create_pdf_wrapper(data_json, out_path=None, include_chart=True):
        # Handle data parsing like the wrapper in app.py
        if isinstance(data_json, str):
            try:
                data = json.loads(data_json)
            except Exception:
                data = {"error": "Invalid JSON", "raw_input": data_json}
        else:
            data = data_json
        return create_pdf(data, out_path, include_chart)

    # Test case 1: Dict input
    test_data = {
        "title": "Sales Report 2024",
        "total_sales": 1282.38,
        "grand_total": 1282.38,
    }
    output_path = create_pdf_wrapper(test_data, out_path=tmp_path / "wrapper_dict.pdf")
    assert Path(output_path).exists()

    # Test case 2: JSON string input
    json_data = json.dumps(test_data)
    output_path = create_pdf_wrapper(json_data, out_path=tmp_path / "wrapper_json.pdf")
    assert Path(output_path).exists()

    # Test case 3: Invalid JSON string input
    bad_data = "Please create a PDF with sales data for 2024"
    output_path = create_pdf_wrapper(
        bad_data, out_path=tmp_path / "wrapper_invalid.pdf"
    )
    assert Path(output_path).exists()
    # The PDF should contain the error message
    assert Path(output_path).stat().st_size > 1000


def test_mcp_simulation_direct(tmp_path):
    """Test direct MCP-like calls to the PDF tool."""
    # Test data similar to what an agent might send via MCP
    test_data = {
        "title": "Sales Report 2024",
        "total_sales": 1282.38,
        "data_source": "sales.db",
        "month_1": "January",
        "sales_1": 456.78,
        "month_2": "February",
        "sales_2": 345.60,
        "month_3": "March",
        "sales_3": 480.00,
        "grand_total": 1282.38,
    }

    # Direct call with dictionary (like calling the tool directly)
    try:
        output_path = create_pdf(test_data, out_path=tmp_path / "mcp_direct_dict.pdf")
        assert Path(output_path).exists()
    except Exception as e:
        print(f"Error with direct dict call: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"Direct dict call failed: {str(e)}")

    # Call with JSON string (simulating agent sending JSON via MCP)
    try:
        json_data = json.dumps(test_data)
        # Parse JSON (similar to create_pdf_wrapper in app.py)
        data = json.loads(json_data)
        output_path = create_pdf(data, out_path=tmp_path / "mcp_direct_json.pdf")
        assert Path(output_path).exists()
    except Exception as e:
        print(f"Error with JSON string call: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"JSON string call failed: {str(e)}")

    # Simulate error handling (malformed request)
    try:
        # Malformed data
        bad_data = {
            "error": "Invalid JSON",
            "raw_input": "Please create a PDF with sales data",
        }
        output_path = create_pdf(bad_data, out_path=tmp_path / "mcp_malformed.pdf")
        assert Path(output_path).exists()
    except Exception as e:
        print(f"Error with malformed data: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"Malformed data call failed: {str(e)}")


def test_empty_value_handling(tmp_path):
    """Test handling of empty or None values."""
    data = {
        "title": "Empty Value Test",
        "empty_string": "",
        "none_value": None,
        "zero_value": 0,
        "grand_total": 1000,
    }
    with PdfReportBuilder(tmp_path / "empty_values.pdf") as builder:
        builder.add_cover(data["title"])
        builder.add_section({"title": "Data", "type": "table", "data": data})
        output_path = builder.save()
    assert Path(output_path).exists()


def _count_images(pdf_path: Path) -> int:
    with open(pdf_path, "rb") as f:
        return f.read().count(b"/Subtype /Image")


def test_pdf_with_cover_and_summary(tmp_path):
    data = {
        "title": "Cover Report",
        "summary": "Quick overview",
        "cover": {"logo_path": "assets/logo.png"},
        "sections": [{"title": "Intro", "type": "paragraph", "text": "Hello"}],
    }
    with PdfReportBuilder(tmp_path / "cover.pdf") as builder:
        builder.add_cover(
            data["title"],
            data["cover"].get("logo_path"),
            data["summary"],
        )
        for sec in data["sections"]:
            builder.add_section(sec)
        pdf_path = Path(builder.save())
    assert pdf_path.exists()
    from PyPDF2 import PdfReader

    reader = PdfReader(str(pdf_path))
    assert len(reader.pages) >= 2
    assert "Quick overview" in reader.pages[0].extract_text()


def test_multiple_chart_specs(tmp_path):
    data = {
        "title": "Charts",
        "sections": [
            {
                "title": "Multi",
                "type": "chart",
                "chart_spec": [
                    {
                        "chart_type": "bar",
                        "labels": ["A", "B"],
                        "values": [1, 2],
                        "color": "#ff0000",
                    },
                    {"chart_type": "line", "labels": [1, 2], "values": [3, 4]},
                ],
            }
        ],
    }
    with PdfReportBuilder(tmp_path / "multi.pdf") as builder:
        builder.add_cover(data["title"])
        for sec in data["sections"]:
            builder.add_section(sec)
        pdf_path = Path(builder.save())
    assert pdf_path.exists()
    assert _count_images(pdf_path) >= 3


def test_builder_class(tmp_path):
    from tools.pdf_tool import PdfReportBuilder

    with PdfReportBuilder(tmp_path / "builder.pdf") as builder:
        builder.add_cover("Title")
        builder.add_section({"title": "P", "type": "paragraph", "text": "Hi"})
        path = builder.save()
    assert Path(path).exists()


def test_pdf_with_sections_and_charts(tmp_path):
    """Generate a PDF using the new schema with multiple chart types."""
    data = {
        "title": "Complex Report",
        "insights": ["Insight one", "Another insight"],
        "sections": [
            {
                "title": "Numbers",
                "type": "table",
                "data": [{"a": 1, "b": 2}, {"a": 3, "b": 4}],
            },
            {
                "title": "Bar Chart",
                "type": "chart",
                "chart_spec": {
                    "chart_type": "bar",
                    "labels": ["A", "B"],
                    "values": [1, 2],
                },
            },
            {
                "title": "Pie Chart",
                "type": "chart",
                "chart_spec": {
                    "chart_type": "pie",
                    "labels": ["X", "Y"],
                    "values": [3, 7],
                },
            },
            {
                "title": "Line Chart",
                "type": "chart",
                "chart_spec": {
                    "chart_type": "line",
                    "labels": [1, 2, 3],
                    "values": [1, 4, 9],
                },
            },
        ],
    }

    with PdfReportBuilder(tmp_path / "complex.pdf") as builder:
        builder.add_cover(data["title"])
        for sec in data["sections"]:
            builder.add_section(sec)
        pdf_path = Path(builder.save())
    assert pdf_path.exists()
    assert _count_images(pdf_path) >= 4


def test_build_table_special_case():
    """Cover _build_table path for structured list data."""
    from tools.pdf_tool import _build_table

    data = {
        "title": "Items",
        "data": [{"a": 1}, {"b": 2}],
        "extra": "val",
    }
    table = _build_table(data)
    assert table is not None


def test_create_chart_variants(tmp_path):
    """Ensure create_chart supports bar, pie and line charts."""
    from tools.pdf_tool import create_chart

    specs = [
        {"chart_type": "bar", "labels": ["A"], "values": [1]},
        {"chart_type": "pie", "labels": ["A"], "values": [1]},
        {"chart_type": "line", "labels": [1, 2], "values": [3, 4]},
    ]
    for spec in specs:
        path = create_chart(spec, tmp_path)
        assert Path(path).exists()


def test_create_pdf_with_sections(tmp_path):
    """Exercise the create_pdf branch handling section dictionaries."""
    from tools.pdf_tool import create_pdf

    data = {
        "title": "Report",
        "summary": "S",
        "cover": {"logo_path": None},
        "insights": ["ok"],
        "sections": [
            {"title": "Data", "type": "table", "data": {"a": 1}},
            {
                "title": "Chart",
                "type": "chart",
                "chart_spec": {"chart_type": "bar", "labels": ["a"], "values": [1]},
            },
        ],
    }
    path = create_pdf(data, out_path=tmp_path / "sections.pdf")
    assert Path(path).exists()
