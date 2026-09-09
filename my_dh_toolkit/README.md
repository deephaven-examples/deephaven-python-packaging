# My Deephaven Toolkit

A combined package providing both reusable library code and command-line tools for Deephaven. This package can be used as both a library (imported in Python code) and as standalone CLI commands.

## Installation

```shell
pip install .
```

Or in editable mode for development:

```shell
pip install -e .
```

## Usage as a Library

> [!NOTE]
> All Deephaven functionality requires a running server. Start the server before importing Deephaven modules.

Import and use the library functions in your Python code:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Now use the library functions
from my_dh_toolkit.queries import filter_by_threshold, add_computed_columns
from my_dh_toolkit import my_dh_query, batch_process
from deephaven import read_csv

data = read_csv("../data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)

# Or use the exported functions
result = my_dh_query("../data/sample.csv", verbose=True)
```

## Usage as CLI Commands

Run the installed commands directly from a terminal. Both `my-dh-toolkit-query` and `my-dh-toolkit-process` start their own Deephaven server:

```shell
my-dh-toolkit-query ../data/sample.csv --verbose
my-dh-toolkit-process ../data/batch --output ./output --verbose
```

The underlying functions are also importable, so you can call them directly within a Python session that already has a server running:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Call the underlying functions directly
from my_dh_toolkit import my_dh_query, batch_process
result = my_dh_query("../data/sample.csv", verbose=True)
batch_process("../data/batch/", "./output", verbose=True)
```

## Commands

### my-dh-toolkit-query

Process a single CSV file with Deephaven.

**Arguments:**
- `input_file` - Path to the CSV file to process

**Options:**
- `--verbose, -v` - Enable verbose output

### my-dh-toolkit-process

Batch process multiple CSV files from a directory.

**Arguments:**
- `directory` - Directory containing CSV files to process

**Options:**
- `--output, -o` - Output directory (default: ./output)
- `--verbose, -v` - Enable verbose output

## Available Functions

### Query Functions (`my_dh_toolkit.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where column value exceeds threshold
- `add_computed_columns(table)` - Add commonly used computed columns to a table
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column

### Utility Functions (`my_dh_toolkit.utils`)

- `validate_columns(table, required_columns)` - Check if table has all required columns
- `get_table_info(table)` - Get basic information about a table

### Exported Functions (`my_dh_toolkit`)

- `my_dh_query(input_file, verbose)` - Read and process a CSV file
- `batch_process(directory, output_dir, verbose)` - Process multiple CSV files

## Requirements

- Python 3.9 or later
- Deephaven Server 0.35.0 or later
- Click 8.0.0 or later
