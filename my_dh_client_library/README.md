# My Deephaven Client Library

An example of packaging reusable query functions that work with a Deephaven server over the network. The package depends on [`pydeephaven`](https://pypi.org/project/pydeephaven/), the Deephaven Python client, instead of `deephaven-server`. It does not start a server; the calling program connects to one that is already running and passes the connection in. There are no command line tools; this package is only ever imported.

Compare it with [`my_dh_library`](../my_dh_library/), which provides the same functions for an embedded server. The two differ in three ways:

- The dependency is `pydeephaven` rather than `deephaven-server`, so installing it does not pull in a JVM.
- The functions take and return client-side `pydeephaven.Table` handles. Operations on a handle are sent to the server for execution.
- `__init__.py` re-exports the public API. `my_dh_library` does the same, and is able to do so because it does not define any commands. Here, there is no such constraint: `pydeephaven` can be imported at any time, so a client package can re-export freely even if it also defines commands.

## Installation

From the repository root:

```bash
pip install ./my_dh_client_library
```

Or in editable mode for development:

```bash
pip install -e ./my_dh_client_library
```

## Usage

> [!NOTE]
> A Deephaven server must already be running. The snippet below connects to one on `localhost:10000` with anonymous authentication. See [Start a server for the client examples](../README.md#start-a-server-for-the-client-examples) in the repository README for ways to start one, and for connecting to a server that uses a pre-shared key.

From the repository root, start Python and use the library:

```python
from pydeephaven import Session
from my_dh_client_library import upload_csv, filter_by_threshold, add_computed_columns, publish

with Session(host="localhost", port=10000) as session:
    data = upload_csv(session, "data/sample.csv")
    filtered = filter_by_threshold(data, "Score", 75.0)
    enhanced = add_computed_columns(filtered)
    publish(session, "enhanced", enhanced)
    print(f"{enhanced.size} of {data.size} rows have Score > 75")
```

The `enhanced` table is now bound on the server, so it appears in the server's IDE and other clients can open it with `session.open_table("enhanced")`. To bring results back into the client process, call `enhanced.to_arrow()` and work with the result as a pyarrow table.

## Available functions

### Query functions (`my_dh_client_library.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where the column value exceeds the threshold.
- `add_computed_columns(table)` - Add `DoubleValue` and `IsHigh` columns computed from `Value`.
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column.
- `publish(session, name, table)` - Bind a table under a name on the server.

### Utility functions (`my_dh_client_library.utils`)

- `upload_csv(session, path)` - Read a local CSV file and upload it to the server as a table.
- `validate_columns(table, required_columns)` - Check if a table has all required columns.
- `get_table_info(table)` - Get basic information about a table.

## Requirements

- Python 3.9 or later
- pydeephaven 0.35.0 or later (installed automatically as a dependency)
- A running Deephaven server to connect to. Java is not required on the client machine.
