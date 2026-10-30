"""Utility functions for working with Deephaven tables."""

from __future__ import annotations

from deephaven.table import Table


def validate_columns(table: Table, required_columns: list[str], raise_error: bool = False) -> bool:
    """Check if table has all required columns.
    
    Args:
        table: The table to validate
        required_columns: List of column names that must be present
        raise_error: If True, raises ValueError when columns are missing
        
    Returns:
        True if all columns are present, False otherwise
        
    Raises:
        ValueError: If raise_error is True and columns are missing
    """
    table_columns = [col.name for col in table.columns]
    missing = [col for col in required_columns if col not in table_columns]
    
    if missing:
        if raise_error:
            raise ValueError(
                f"Column(s) {missing} not found in table. "
                f"Available columns: {', '.join(table_columns)}"
            )
        return False
    return True


def get_table_info(table: Table) -> dict:
    """Get basic information about a table."""
    return {
        "num_rows": table.size,
        "num_columns": len(table.columns),
        "columns": [col.name for col in table.columns],
    }
