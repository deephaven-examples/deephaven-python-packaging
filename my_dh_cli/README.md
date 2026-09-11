# My Deephaven CLI

An example of packaging a Deephaven script as a command line tool. Installing this package creates one terminal command, `my-dh-query`. No library code is exposed — users of this package never write Python.

The command is defined by the `[project.scripts]` entry point in [`pyproject.toml`](pyproject.toml):

```toml
[project.scripts]
my-dh-query = "my_dh_cli.cli:app"
```

## Installation

From the repository root:

```shell
pip install ./my_dh_cli
```

Or in editable mode for development:

```shell
pip install -e ./my_dh_cli
```

## Usage

Run the installed command on a CSV file. The command starts its own Deephaven server, so no separate setup is needed:

```shell
my-dh-query data/sample.csv --verbose
```

It reads the file, adds a `DoubleScore` computed column, and reports the number of rows processed.

During development, the package also runs without an entry point via [`__main__.py`](src/my_dh_cli/__main__.py):

```shell
python -m my_dh_cli data/sample.csv --verbose
```

## Command reference

### my-dh-query

Process a CSV file with Deephaven. The file must contain a `Score` column.

**Arguments:**

- `input_file` - Path to the CSV file to process.

**Options:**

- `--verbose, -v` - Enable verbose output.

## Requirements

- Python 3.9 or later
- Java 17 or later
- Deephaven Server 0.35.0 or later
- Click 8.0.0 or later
