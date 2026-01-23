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

> [!NOTE]
> CLI functions require a Deephaven server running in the same Python process. Use the functions within a Python session where the server is already started.

```shell
pip install -e .
python
```

Then in Python:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Now use the CLI function
from my_dh_cli.cli import my_dh_query
result = my_dh_query("../data/sample.csv", verbose=True)
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
