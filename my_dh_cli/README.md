# My Deephaven CLI

A CLI-only package providing command-line tools for data processing with Deephaven. This package is designed to be installed and run as a command-line tool.

## Installation

```shell
pip install .
```

Or in editable mode for development:

```shell
pip install -e .
```

## Usage

Run the installed command directly from a terminal. `my-dh-query` starts its own Deephaven server, so no separate session setup is needed:

```shell
my-dh-query data/sample.csv --verbose
```

The underlying `my_dh_query()` function is also importable, so you can call it directly within a Python session that already has a server running:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Call the underlying function directly
from my_dh_cli.cli import my_dh_query
result = my_dh_query("data/sample.csv", verbose=True)
print(f"Processed {result.size} rows")
```

## Commands

### my-dh-query

Process a CSV file with Deephaven.

**Arguments:**
- `input_file` - Path to the CSV file to process

**Options:**
- `--verbose, -v` - Enable verbose output

## Requirements

- Python 3.8 or later
- Deephaven Server 0.35.0 or later
- Click 8.0.0 or later
