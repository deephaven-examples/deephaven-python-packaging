# My Deephaven Library

A library-only package providing reusable Deephaven query functions. This package contains no CLI tools - it's designed to be imported and used as a library in other Python projects.

## Installation

```shell
pip install .
```

Or in editable mode for development:

```shell
pip install -e .
```

## Usage

> [!NOTE]
> All Deephaven functionality requires a running server. Start the server before importing Deephaven modules.

Import and use the library functions in your Python code:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Now use the library functions
from my_dh_library.queries import filter_by_threshold, add_computed_columns
from deephaven import read_csv

data = read_csv("data.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
enhanced = add_computed_columns(filtered)
```

## Available Functions

### Query Functions (`my_dh_library.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where column value exceeds threshold
- `add_computed_columns(table)` - Add commonly used computed columns to a table
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column

### Utility Functions (`my_dh_library.utils`)

- `validate_columns(table, required_columns)` - Check if table has all required columns
- `get_table_info(table)` - Get basic information about a table

## Requirements

- Python 3.8 or later
- Deephaven Server 0.35.0 or later
