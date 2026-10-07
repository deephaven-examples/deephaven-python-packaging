"""Utility functions for working with tables on a remote Deephaven server."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import pyarrow.csv as pacsv
from pydeephaven import Session, Table


def upload_csv(session: Session, path: Union[str, Path]) -> Table:
    """Read a local CSV file and upload it to the server.

    The client cannot call the server's ``read_csv`` on a file it cannot see, so the
    file is read locally with pyarrow and sent to the server as an Arrow table.
    """
    return session.import_table(pacsv.read_csv(str(path)))


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
    table_columns = table.schema.names
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
        "num_columns": len(table.schema),
        "columns": table.schema.names,
    }
