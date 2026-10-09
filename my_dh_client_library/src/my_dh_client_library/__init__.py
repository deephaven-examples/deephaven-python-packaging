"""Reusable query functions and table utilities for a remote Deephaven server.

Unlike a package built on deephaven-server, this package can import pydeephaven at
module scope, so the public API is re-exported here.
"""

__version__ = "0.1.0"

from my_dh_client_library.queries import (
    add_computed_columns,
    filter_by_threshold,
    publish,
    summarize_by_group,
)
from my_dh_client_library.utils import upload_csv

__all__ = [
    "add_computed_columns",
    "filter_by_threshold",
    "publish",
    "summarize_by_group",
    "upload_csv",
]
