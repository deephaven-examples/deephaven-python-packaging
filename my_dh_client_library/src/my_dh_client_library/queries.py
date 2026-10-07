"""Reusable query functions that run on a remote Deephaven server.

Each function takes and returns client-side ``pydeephaven.Table`` handles. The table
operations are sent to the server for execution; only the handle comes back.
"""

from pydeephaven import Session, Table, agg

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
            agg.sum_(f"Sum = {value_col}"),
            agg.avg(f"Avg = {value_col}"),
            agg.count_("Count"),
        ],
        by=[group_col],
    )


def publish(session: Session, name: str, table: Table) -> None:
    """Bind a table under a name so it is visible in the server's IDE and to other clients."""
    session.bind_table(name, table)
