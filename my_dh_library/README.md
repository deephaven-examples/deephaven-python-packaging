# My Deephaven Library

An example of packaging reusable Deephaven query functions as a library. Installing this package makes its functions importable from any Python code. There are no command line tools; this package is only ever imported.

The package depends on `deephaven-core`, which provides the server-side `deephaven` API without a server of its own. It is meant to be installed into a Deephaven server's Python environment and imported from there. It can also be used from a standalone Python process that starts its own server.

## Installation

From the repository root:

```bash
pip install ./my_dh_library
```

Or in editable mode for development:

```bash
pip install -e ./my_dh_library
```

Install it into the same environment as the Deephaven server that will use it. For Docker, install it in a custom image based on `ghcr.io/deephaven/server`; see [Install and use Python packages](https://deephaven.io/core/docs/how-to-guides/install-and-use-python-packages/).

## Usage

### Inside a Deephaven server

In the server's console or a script it runs, import the functions directly:

```python
from my_dh_library import filter_by_threshold, add_computed_columns
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
enhanced = add_computed_columns(filtered)
```

`filtered` and `enhanced` appear in the IDE, each with 9 of the 10 rows. There is no `Server` to create, because the code already runs inside one.

To try this locally, install a server next to the library and open the URL it prints, which includes its login key:

```bash
pip install -e ./my_dh_library deephaven-server
deephaven server --port 10001
```

### In a standalone Python process

Outside a server, install `deephaven-server` as well, and create a `Server` before importing `deephaven` or this library. See [Import order for the `deephaven` module](../README.md#import-order-for-the-deephaven-module) in the repository README for why.

```python
# Creating a Server starts the JVM, which deephaven modules need at import time.
from deephaven_server import Server
server = Server(port=10001, jvm_args=["-Xmx4g"])
server.start()

# Import and use the installed library.
from my_dh_library import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

After the server's startup log, this prints `9 of 10 rows have Score > 75`.

## Available functions

### Query functions (`my_dh_library.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where the column value exceeds the threshold.
- `add_computed_columns(table)` - Add `DoubleValue` and `IsHigh` columns computed from `Value`.
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column.

### Utility functions (`my_dh_library.utils`)

- `validate_columns(table, required_columns)` - Check if a table has all required columns.
- `get_table_info(table)` - Get basic information about a table.

## What to study

- [`pyproject.toml`](pyproject.toml): the `dependencies` list declares `deephaven-core`. A Deephaven server already has it, so installing the library into a server adds nothing else and doesn't change the server's Deephaven version. `[tool.setuptools.packages.find]` points setuptools at `src/`.
- [`queries.py`](src/my_dh_library/queries.py): plain functions that take and return Deephaven tables.
- [`__init__.py`](src/my_dh_library/__init__.py): re-exports the public functions. Because of this, even `import my_dh_library` needs a running JVM. See [Import order for the `deephaven` module](../README.md#import-order-for-the-deephaven-module).

## Requirements

- Python 3.9 or later
- deephaven-core (installed automatically as a dependency, and already present in a Deephaven server; see [`pyproject.toml`](pyproject.toml) for the minimum version)
- For standalone use only: deephaven-server, and Java 17 or later with `JAVA_HOME` set (neither is installed automatically)
