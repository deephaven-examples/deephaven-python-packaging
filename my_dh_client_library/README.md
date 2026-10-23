# My Deephaven Client Library

An example of packaging reusable query functions that work with a Deephaven server over the network. The package depends on [`pydeephaven`](https://pypi.org/project/pydeephaven/), the Deephaven Python client, instead of the server-side `deephaven-core`. It does not need to run inside a server or start one; the calling program connects to one that is already running and passes the connection in. There are no command line tools; this package is only ever imported.

Compare it with [`my_dh_library`](../my_dh_library/), which provides the same functions for code running inside a Deephaven server. The two differ in three ways:

- The dependency is `pydeephaven` rather than `deephaven-core`, so the library runs in any Python process and needs no JVM.
- The functions take and return client-side `pydeephaven.Table` handles. Operations on a handle are sent to the server for execution.
- `__init__.py` re-exports the public API, as in `my_dh_library`. A client package can do this even if it later adds commands, because `pydeephaven` can be imported at any time.

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
> A Deephaven server must already be running. The snippet below connects to one on `localhost:10000` with anonymous authentication. See [Start a server for Examples 4 and 5](../README.md#start-a-server-for-examples-4-and-5) in the repository README for ways to start one, and for connecting to a server that uses a pre-shared key.

From the repository root, start Python and use the library. The calling program creates the [`Session`](https://deephaven.io/core/client-api/python/code/pydeephaven.session.html#pydeephaven.session.Session) and passes it to the library's functions. The `Session` reference lists the connection and authentication options, such as `host`, `port`, `auth_type`, and `auth_token`, along with the methods the library uses, including `import_table` and `bind_table`.

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

This prints `9 of 10 rows have Score > 75`. The `enhanced` table is now bound on the server, so it appears in the server's IDE and other clients can open it with `session.open_table("enhanced")`. To bring results back into the client process, call `enhanced.to_arrow()` and work with the result as a pyarrow table.

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

## What to study

- [`queries.py`](src/my_dh_client_library/queries.py): defines the same query strings and table operations as the [`my_dh_library` version](../my_dh_library/src/my_dh_library/queries.py), but the operations run on the server and only a handle comes back. `publish` wraps `session.bind_table`, which is how a client gives a table a name on the server.
- [`utils.py`](src/my_dh_client_library/utils.py): defines `upload_csv`, which reads a CSV file locally with pyarrow and sends it with `session.import_table`, because the server cannot see the client's files. Column names come from `table.schema.names` rather than `table.columns`.

## Requirements

- Python 3.9 or later
- pydeephaven (installed automatically as a dependency; see [`pyproject.toml`](pyproject.toml) for the minimum version)
- A running Deephaven server to connect to (Java is not required on the client machine)
