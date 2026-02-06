"""Reusable Deephaven query functions."""

from deephaven.table import Table
from .utils import validate_columns


def filter_by_threshold(table: Table, column: str, threshold: float) -> Table:
    """Filter table rows where column value exceeds threshold."""
    validate_columns(table, [column], raise_error=True)
    return table.where(f"{column} > {threshold}")


def add_computed_columns(table: Table) -> Table:
    """Add commonly used computed columns to a table."""
    validate_columns(table, ["Value"], raise_error=True)
    return table.update(
        [
            "DoubleValue = Value * 2",
            "IsHigh = Value > 100",
        ]
    )


def summarize_by_group(table: Table, group_col: str, value_col: str) -> Table:
    """Create summary statistics grouped by a column."""
    validate_columns(table, [group_col, value_col], raise_error=True)
    return table.agg_by(
        [
            f"Sum = sum({value_col})",
            f"Avg = avg({value_col})",
            f"Count = count()",
        ],
        by=[group_col],
    )
