"""Utility functions for working with Deephaven tables."""

from deephaven.table import Table


def validate_columns(table: Table, required_columns: list[str]) -> bool:
    """Check if table has all required columns."""
    table_columns = [col.name for col in table.columns]
    return all(col in table_columns for col in required_columns)


def get_table_info(table: Table) -> dict:
    """Get basic information about a table."""
    return {
        "num_rows": table.size,
        "num_columns": len(table.columns),
        "columns": [col.name for col in table.columns],
    }
