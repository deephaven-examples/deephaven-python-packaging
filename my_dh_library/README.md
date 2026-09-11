# My Deephaven Library

An example of packaging reusable Deephaven query functions as a library. Installing this package makes its functions importable from any Python code. There are no command line tools — this package is only ever imported.

## Installation

From the repository root:

```shell
pip install ./my_dh_library
```

Or in editable mode for development:

```shell
pip install -e ./my_dh_library
```

## Usage

> [!NOTE]
> All Deephaven functionality requires a running server in the same Python process. Start the server before importing `deephaven` modules.

From the repository root, start Python and use the library:

```python
# A Deephaven server must be running before deephaven modules are imported.
from deephaven_server import Server
Server(port=10000, jvm_args=["-Xmx4g"]).start()

# Import and use the installed library.
from my_dh_library.queries import filter_by_threshold, add_computed_columns
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
enhanced = add_computed_columns(filtered)
```

## Available functions

### Query functions (`my_dh_library.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where the column value exceeds the threshold.
- `add_computed_columns(table)` - Add commonly used computed columns to a table.
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column.

### Utility functions (`my_dh_library.utils`)

- `validate_columns(table, required_columns)` - Check if a table has all required columns.
- `get_table_info(table)` - Get basic information about a table.

## Requirements

- Python 3.9 or later
- Java 17 or later
- Deephaven Server 0.35.0 or later
