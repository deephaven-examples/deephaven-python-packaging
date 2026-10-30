# My Deephaven CLI

An example of packaging a Deephaven script as a command line tool. Installing this package creates one terminal command, `my-dh-cli-query`. No library code is exposed; the package is used only through that command, so no Python needs to be written to use it.

The command is defined by the `[project.scripts]` entry point in [`pyproject.toml`](pyproject.toml):

```toml
[project.scripts]
my-dh-cli-query = "my_dh_cli.cli:main"
```

## Installation

From the repository root:

```bash
pip install ./my_dh_cli
```

Or in editable mode for development:

```bash
pip install -e ./my_dh_cli
```

## Usage

Run the installed command on a CSV file. The command starts its own Deephaven server, so no separate server is needed:

```bash
my-dh-cli-query data/sample.csv --verbose
```

It reads the file, adds a `DoubleScore` computed column, and prints the first five rows. After the server's startup log, the output is:

```text
Processing data/sample.csv...
Processed 10 rows
      Name|     Score|     Value|  Category|DoubleScore
----------+----------+----------+----------+-----------
Alice     |        85|       120|A         |        170
Bob       |        92|       150|B         |        184
Charlie   |        78|        95|A         |        156
Diana     |        88|       110|C         |        176
Eve       |        95|       180|B         |        190

Processing complete!
```

The server listens on port 10001 by default, so it doesn't collide with a Deephaven server on the usual port 10000. Pass `--port` to choose another.

During development, the package also runs without an entry point via [`__main__.py`](src/my_dh_cli/__main__.py):

```bash
python -m my_dh_cli data/sample.csv --verbose
```

## Command reference

### my-dh-cli-query

Process a CSV file with Deephaven. The file must contain a numeric `Score` column.

**Arguments:**

- `input_file` - Path to the CSV file to process.

**Options:**

- `--port` - Port for the embedded Deephaven server. Default: `10001`.
- `--heap` - JVM maximum heap size. Default: `4g`.
- `-v, --verbose` - Verbose output, listing the file being processed and the number of rows processed.

## What to study

- [`pyproject.toml`](pyproject.toml): maps the command name to a function in its `[project.scripts]` section.
- [`cli.py`](src/my_dh_cli/cli.py): defines a [Click](https://click.palletsprojects.com/) command that starts the Deephaven server itself, so it works as a standalone tool. It imports `deephaven` inside a function that runs after it creates the `Server`, not at the top of the module. See [Import order for the `deephaven` module](../README.md#import-order-for-the-deephaven-module).

## Requirements

- Python 3.9 or later
- Java 17 or later, with `JAVA_HOME` set (not installed by `pip`)
- deephaven-server (installed automatically as a dependency; see [`pyproject.toml`](pyproject.toml) for the minimum version)
- Click 8.0.0 or later (installed automatically as a dependency)
