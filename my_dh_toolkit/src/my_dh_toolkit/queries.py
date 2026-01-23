"""Reusable Deephaven query functions."""

from deephaven.table import Table


def filter_by_threshold(table: Table, column: str, threshold: float) -> Table:
    """Filter table rows where column value exceeds threshold."""
    return table.where(f"{column} > {threshold}")


def add_computed_columns(table: Table) -> Table:
    """Add commonly used computed columns to a table."""
    return table.update(
        [
            "DoubleValue = Value * 2",
            "IsHigh = Value > 100",
        ]
    )


def summarize_by_group(table: Table, group_col: str, value_col: str) -> Table:
    """Create summary statistics grouped by a column."""
    return table.agg_by(
        [
            f"Sum = sum({value_col})",
            f"Avg = avg({value_col})",
            f"Count = count()",
        ],
        by=[group_col],
    )
