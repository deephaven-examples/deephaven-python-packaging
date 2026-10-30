# My Deephaven Toolkit

An example of one package with two interfaces:

- **A library**: importable query functions, matching the [`my_dh_library`](../my_dh_library/) example.
- **Command line tools**: two terminal commands, following the same pattern as the [`my_dh_cli`](../my_dh_cli/) example.

The commands call the package's own library functions (`validate_columns` and `add_computed_columns`), so Python users and terminal users share one implementation.

`queries.py` and `utils.py` are copies of the `my_dh_library` modules rather than a dependency on that package. The duplication is deliberate: it keeps each example self-contained, so you can copy any one of them on its own.

The commands are defined by the `[project.scripts]` entry points in [`pyproject.toml`](pyproject.toml):

```toml
[project.scripts]
my-dh-toolkit-query = "my_dh_toolkit.query:main"
my-dh-toolkit-process = "my_dh_toolkit.process:main"
```

## Installation

From the repository root:

```bash
pip install ./my_dh_toolkit
```

Or in editable mode for development:

```bash
pip install -e ./my_dh_toolkit
```

## Usage as command line tools

Run the installed commands on the sample data. Each command starts its own Deephaven server, so no separate server is needed:

```bash
my-dh-toolkit-query data/sample.csv --verbose
my-dh-toolkit-process data/batch --output output --verbose
```

`my-dh-toolkit-query` processes a single CSV file and prints the first five rows of the result. `my-dh-toolkit-process` processes every CSV file in a directory and writes the results to the output directory. Both commands require a `Value` column and add `DoubleValue` and `IsHigh` columns. After the server's startup log, `my-dh-toolkit-query` prints:

```text
Processing data/sample.csv...
Processed 10 rows
      Name|     Score|     Value|  Category|DoubleValue|    IsHigh
----------+----------+----------+----------+-----------+----------
Alice     |        85|       120|A         |        240|true
Bob       |        92|       150|B         |        300|true
Charlie   |        78|        95|A         |        190|false
Diana     |        88|       110|C         |        220|true
Eve       |        95|       180|B         |        360|true

Processing complete!
```

And `my-dh-toolkit-process` prints:

```text
Found 3 CSV files to process
Processing file1.csv...
  Processed 3 rows -> processed_file1.csv
Processing file2.csv...
  Processed 3 rows -> processed_file2.csv
Processing file3.csv...
  Processed 4 rows -> processed_file3.csv
Batch processing complete!
```

The commands' servers listen on port 10001 by default, so they don't collide with a Deephaven server on the usual port 10000. Pass `--port` to choose another.

During development, the query command also runs via [`__main__.py`](src/my_dh_toolkit/__main__.py):

```bash
python -m my_dh_toolkit data/sample.csv --verbose
```

## Usage as a library

In a standalone Python process, create a `Server` before importing `deephaven` or the library modules. Inside a running Deephaven server, skip the `Server` lines. Import the functions from their submodules, as shown, not from `my_dh_toolkit` itself ([why](#what-to-study)).

From the repository root, start Python and use the library:

```python
# Creating a Server starts the JVM, which deephaven modules need at import time.
from deephaven_server import Server
server = Server(port=10001, jvm_args=["-Xmx4g"]).start()

# Import and use the installed library.
from my_dh_toolkit.queries import filter_by_threshold, add_computed_columns
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
enhanced = add_computed_columns(filtered)
```

## Command reference

### my-dh-toolkit-query

Process a single CSV file with Deephaven. The file must contain a numeric `Value` column. The result has two additional columns, `DoubleValue` and `IsHigh`.

**Arguments:**

- `input_file` - Path to the CSV file to process.

**Options:**

- `--port` - Port for the embedded Deephaven server. Default: `10001`.
- `--heap` - JVM maximum heap size. Default: `4g`.
- `-v, --verbose` - Verbose output, listing the file being processed and the number of rows processed.

### my-dh-toolkit-process

Batch process every CSV file in a directory. Each file must contain a numeric `Value` column. Each output file, named `processed_<input name>`, has two additional columns, `DoubleValue` and `IsHigh`.

**Arguments:**

- `directory` - Directory containing CSV files to process.

**Options:**

- `-o, --output` - Output directory. Must differ from the input directory. Default: `./output`.
- `--port` - Port for the embedded Deephaven server. Default: `10001`.
- `--heap` - JVM maximum heap size. Default: `4g`.
- `-v, --verbose` - Verbose output, listing the number of CSV files found and, for each file, its name, row count, and output file.

## Available functions

### Query functions (`my_dh_toolkit.queries`)

- `filter_by_threshold(table, column, threshold)` - Filter table rows where the column value exceeds the threshold.
- `add_computed_columns(table)` - Add `DoubleValue` and `IsHigh` columns computed from `Value`.
- `summarize_by_group(table, group_col, value_col)` - Create summary statistics grouped by a column.

### Utility functions (`my_dh_toolkit.utils`)

- `validate_columns(table, required_columns)` - Check if a table has all required columns.
- `get_table_info(table)` - Get basic information about a table.

## What to study

- [`pyproject.toml`](pyproject.toml): defines both commands in a single `[project.scripts]` section.
- [`__init__.py`](src/my_dh_toolkit/__init__.py): deliberately imports nothing that requires Deephaven, so that the commands can start before they create a `Server`. This is why the library is imported from its submodules (`my_dh_toolkit.queries`, `my_dh_toolkit.utils`). See [Import order for the `deephaven` module](../README.md#import-order-for-the-deephaven-module) for the failure this avoids.
- [`query.py`](src/my_dh_toolkit/query.py) and [`process.py`](src/my_dh_toolkit/process.py): each define one command's `main()`. Like `my_dh_cli`, both import `deephaven` and the library modules inside a function that runs after the `Server` has been created.

## Requirements

- Python 3.9 or later
- Java 17 or later, with `JAVA_HOME` set (not installed by `pip`)
- deephaven-server (installed automatically as a dependency; see [`pyproject.toml`](pyproject.toml) for the minimum version)
- Click 8.0.0 or later (installed automatically as a dependency)
