# My Deephaven Toolkit

An example of one package with two interfaces:

- **A library** — importable query functions, matching the [`my_dh_library`](../my_dh_library/) example.
- **Command-line tools** — two terminal commands, following the same pattern as the [`my_dh_cli`](../my_dh_cli/) example.

The commands are defined by the `[project.scripts]` entry points in [`pyproject.toml`](pyproject.toml):

```toml
[project.scripts]
my-dh-toolkit-query = "my_dh_toolkit.cli:app"
my-dh-toolkit-process = "my_dh_toolkit.processor:process"
```

## Installation

From the repository root:

```shell
pip install ./my_dh_toolkit
```

Or in editable mode for development:

```shell
pip install -e ./my_dh_toolkit
```

## Usage as command-line tools

Run the installed commands on the sample data. Each command starts its own Deephaven server, so no separate setup is needed:

```shell
my-dh-toolkit-query data/sample.csv --verbose
my-dh-toolkit-process data/batch --output output --verbose
```

`my-dh-toolkit-query` processes a single CSV file. `my-dh-toolkit-process` processes every CSV file in a directory and writes the results to the output directory.

## Usage as a library

> [!NOTE]
> All Deephaven functionality requires a running server in the same Python process. Start the server before importing `deephaven` modules.

From the repository root, start Python and use the library:

```python
# A Deephaven server must be running before deephaven modules are imported.
from deephaven_server import Server
Server(port=10000, jvm_args=["-Xmx4g"]).start()

# Import and use the installed library.
from my_dh_toolkit.queries import filter_by_threshold, add_computed_columns
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
enhanced = add_computed_columns(filtered)
```

## Command reference

### my-dh-toolkit-query

Process a single CSV file with Deephaven. The file must contain a `Score` column.

**Arguments:**

- `input_file` - Path to the CSV file to process.

**Options:**

- `--verbose, -v` - Enable verbose output.

### my-dh-toolkit-process

Batch process every CSV file in a directory. Each file must contain a `Score` column.

**Arguments:**

- `directory` - Directory containing CSV files to process.

**Options:**

- `--output, -o` - Output directory (default: `./output`).
- `--verbose, -v` - Enable verbose output.

## Available functions

### Query functions (`my_dh_toolkit.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where the column value exceeds the threshold.
- `add_computed_columns(table)` - Add commonly used computed columns to a table.
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column.

### Utility functions (`my_dh_toolkit.utils`)

- `validate_columns(table, required_columns)` - Check if a table has all required columns.
- `get_table_info(table)` - Get basic information about a table.

## Requirements

- Python 3.9 or later
- Java 17 or later
- Deephaven Server 0.35.0 or later
- Click 8.0.0 or later
