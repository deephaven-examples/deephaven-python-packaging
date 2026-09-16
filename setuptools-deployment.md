---
title: Packaging custom code and dependencies
sidebar_label: Python packaging
---

[Python packaging](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) enables you to create distributable packages containing custom code, command line tools, and managed dependencies. Deephaven's own packages are pip-installable, so a package that depends on them can be built and installed with the standard Python tooling. This guide walks through the concepts and patterns for packaging Deephaven-based Python projects.

Python packaging with [`pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) provides:

- **Reusable libraries** - Package query functions and utilities for import by other projects.
- **Command line tools** - Build executable scripts with entry point definitions.
- **Dependency management** - Automatically install Deephaven and required packages, with version constraints for reproducible installations.
- **Distribution** - Share code as wheel archives via PyPI or direct distribution.

## Example repository

The examples in this guide use the [deephaven-python-packaging](https://github.com/deephaven-examples/deephaven-python-packaging) repository. It demonstrates three complete packaging scenarios with working code, sample data, and a README for each package.

To explore the examples, clone the repository:

```bash
git clone https://github.com/deephaven-examples/deephaven-python-packaging.git
cd deephaven-python-packaging
```

The repository contains three example packages:

- `my_dh_library/` - Library-only package with reusable query functions.
- `my_dh_cli/` - CLI-only package with a command line tool.
- `my_dh_toolkit/` - Combined package with both library and CLI functionality.

## Package structure

The example packages in this guide use the **src-layout** described in the Python Packaging Authority's [src layout vs flat layout discussion](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/). This layout keeps source code separate from tests and configuration files:

```
my_dh_library/
├── src/
│   └── my_dh_library/
│       ├── __init__.py
│       ├── queries.py
│       └── utils.py
├── pyproject.toml
└── README.md
```

### Key components

- **`src/`** - Source directory containing the package code.
- **`my_dh_library/`** (under `src/`) - The Python package. Its directory name is the name used in `import` statements.
- **`__init__.py`** - Makes the directory importable and can export a public API.
- **`pyproject.toml`** - Defines package metadata, dependencies, and entry points.
- **Module files** - Python files containing your functions and classes.

The package name under `src/` determines how users import your code. For example, with `src/my_dh_library/`, users import via `from my_dh_library import ...`.

## Server initialization

Deephaven requires a running server before using any Deephaven functionality. The server must be initialized in the same Python process that uses Deephaven:

```python
from deephaven_server import Server

# Initialize and start the server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Now you can import and use Deephaven
from deephaven import read_csv
data = read_csv("data/sample.csv")
```

### Key points

- Each Python process has its own JVM.
- Starting a server in one terminal doesn't help another terminal.
- Entry-point CLI commands should start their own server internally (see [CLI-only package](#cli-only-package)) so they work standalone; only functions imported directly need an already-running session.
- The examples size the JVM to 4 GB with `jvm_args=["-Xmx4g"]`; adjust this value to fit the workload.

> [!NOTE]
> The examples bind the server to port 10000. If another process already uses that port (for example, a Deephaven server running in Docker), the server fails to start with `Address already in use`. Change the `port` value to a free port.

### Keep `__init__.py` free of Deephaven imports

Because `deephaven` modules cannot be imported until a server is running, the order of imports matters in any package that defines a command. When a command such as `my-dh-toolkit-query` starts, Python imports the package (`my_dh_toolkit/__init__.py`) before the command function has a chance to start the server. If `__init__.py` imported a module that imports `deephaven`, every command in the package would fail at startup.

The rule that follows:

- In a package that defines commands, keep `__init__.py` free of imports that reach `deephaven`. Expose library functions from submodules (`my_dh_toolkit.queries`, `my_dh_toolkit.utils`) instead.
- Inside command modules, import `deephaven` and any library submodules lazily, inside the function that runs after the server has started.
- A library-only package such as `my_dh_library` can safely re-export its functions from `__init__.py`. It has no commands, so it is only ever imported after a server is running.

## Packaging scenarios

Different projects have different needs. The example repository demonstrates three common scenarios. The Python usage snippets below assume a running Deephaven server, as shown in [Server initialization](#server-initialization).

### Library-only package

Package reusable code without CLI tools. Other projects import your modules.

**Structure:**

```
my_dh_library/
├── src/
│   └── my_dh_library/
│       ├── __init__.py
│       ├── queries.py
│       └── utils.py
├── pyproject.toml
└── README.md
```

**Usage:**

```python
from my_dh_library.queries import filter_by_threshold, add_computed_columns
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
```

**Use when:**

- Creating reusable utilities for other projects.
- You don't need a command line interface.
- Code will be imported, not executed directly.

### CLI-only package

Package an executable command line tool without exposing library code. The command starts its own Deephaven server, so it runs as a standalone terminal command.

**Structure:**

```
my_dh_cli/
├── src/
│   └── my_dh_cli/
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py
├── pyproject.toml
└── README.md
```

**Usage:**

```bash
my-dh-query data/sample.csv --verbose
```

**Use when:**

- Building command line tools for data processing.
- The tool is run from a terminal, with no Python code required from the user.
- You don't need to expose library code to other projects.

### Combined package

Package both reusable library code and command line tools. In `my_dh_toolkit`, the commands call the package's own library functions: `my-dh-toolkit-query` and `my-dh-toolkit-process` both use `validate_columns` and `add_computed_columns` from `my_dh_toolkit.utils` and `my_dh_toolkit.queries`. Python users and terminal users get two interfaces to one implementation.

**Structure:**

```
my_dh_toolkit/
├── src/
│   └── my_dh_toolkit/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── processor.py
│       ├── queries.py
│       └── utils.py
├── pyproject.toml
└── README.md
```

**Usage:**

```python
# As a library
from my_dh_toolkit.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
```

```bash
# As CLI commands
my-dh-toolkit-query data/sample.csv --verbose
my-dh-toolkit-process data/batch --output output --verbose
```

**Use when:**

- You need both library and CLI functionality.
- You want to provide multiple interfaces to the same code.
- Library functions are useful independently.

## Configure `pyproject.toml`

The [`pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) file defines your package configuration.

### Configuration options

Here's a detailed breakdown of `pyproject.toml` for a library-only package:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my_dh_library"
version = "0.1.0"
description = "Reusable Deephaven query functions"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
  # deephaven-server also provides the deephaven module (through its deephaven-core dependency).
  "deephaven-server>=0.35.0",
]

[tool.setuptools.packages.find]
where = ["src"]
```

### Key sections

- **`[build-system]`** - Specifies setuptools as the build backend
- **`[project]`** - Package metadata and dependencies
- **`name`** - Project name (used for `pip install`)
- **`dependencies`** - Required packages, installed automatically
- **`[tool.setuptools.packages.find]`** - Tells setuptools to find packages in `src/`

For CLI packages, add a `[project.scripts]` section:

```toml
[project.scripts]
my-dh-query = "my_dh_cli.cli:app"
```

This creates a command line entry point that calls the `app` function from `my_dh_cli.cli`. A package can define any number of commands in this section; `my_dh_toolkit` defines two.

## Manage dependencies

Dependencies are specified in the `dependencies` field:

```toml
[project]
dependencies = [
  "deephaven-server>=0.35.0",
  "click>=8.0.0",
  "pandas>=2.0.0",
]
```

Declaring `deephaven-server` is sufficient for Deephaven: it depends on a matching version of `deephaven-core`, which provides the `deephaven` module that packages import.

### Version constraints

Use version specifiers to control which versions are acceptable:

- `>=0.35.0` - Minimum version (0.35.0 or higher)
- `>=2.0.0,<3.0.0` - Version range (2.x only)
- `~=1.24.0` - Compatible release (>=1.24.0, <1.25.0)
- `==1.0.0` - Exact version (not recommended for libraries)

### Optional dependencies

Define optional feature sets that users can install separately:

```toml
[project.optional-dependencies]
visualization = [
  "matplotlib>=3.7.0",
  "seaborn>=0.12.0",
]
dev = [
  "pytest>=7.0.0",
  "black>=23.0.0",
]
```

Users can install optional dependencies:

```bash
pip install my_dh_library[visualization]
pip install my_dh_library[visualization,dev]
```

## Install and distribute

Install from source in editable mode for development. Editable installs pick up source edits without reinstalling:

```bash
cd my_dh_library
pip install -e .
```

Or install normally:

```bash
pip install .
```

After installation, use the package as shown in [Packaging scenarios](#packaging-scenarios): import a library's functions after starting a server, or run a CLI package's commands directly.

To distribute a package to other machines or publish it to a package index, build a wheel:

```bash
cd my_dh_library
pip install build
python -m build
```

This creates a `.whl` file in `dist/` that can be:

- Installed locally: `pip install dist/my_dh_library-0.1.0-py3-none-any.whl`
- Distributed to others
- Published to PyPI: `python -m twine upload dist/*`

## Best practices

### Package structure

- Prefer the src-layout for packages like these examples
- Keep package names lowercase with underscores
- Match the package directory name to the import name
- Include `__init__.py` in all package directories
- In packages that define entry-point commands, keep `__init__.py` free of imports that require a running Deephaven server, and import `deephaven` lazily inside command functions

### Dependencies

- Specify minimum versions for Deephaven and critical dependencies
- Use version ranges for flexibility
- Group related optional dependencies
- Document any system-level dependencies, such as the Java version

### Documentation

- Include a README.md with installation and usage instructions
- Document all public functions and classes
- Explain server initialization requirements
- Include sample data so users can try the package

## Create a new package

<details>
<summary>Step-by-step instructions for creating packages from scratch</summary>

This section walks through creating each type of package from scratch. The code is the same as in the example repository.

### Create a library-only package

Create the directory structure:

```bash
mkdir -p my_dh_library/src/my_dh_library
cd my_dh_library
```

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my_dh_library"
version = "0.1.0"
description = "Reusable Deephaven query functions"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
  # deephaven-server also provides the deephaven module (through its deephaven-core dependency).
  "deephaven-server>=0.35.0",
]

[tool.setuptools.packages.find]
where = ["src"]
```

Create `src/my_dh_library/__init__.py`:

```python
"""Reusable Deephaven query functions and table utilities."""

__version__ = "0.1.0"

from my_dh_library.queries import filter_by_threshold, add_computed_columns, summarize_by_group

__all__ = ["filter_by_threshold", "add_computed_columns", "summarize_by_group"]
```

Create `src/my_dh_library/utils.py`:

```python
"""Utility functions for working with Deephaven tables."""

from __future__ import annotations

from deephaven.table import Table


def validate_columns(table: Table, required_columns: list[str], raise_error: bool = False) -> bool:
    """Check if table has all required columns.

    Args:
        table: The table to validate
        required_columns: List of column names that must be present
        raise_error: If True, raises ValueError when columns are missing

    Returns:
        True if all columns are present, False otherwise

    Raises:
        ValueError: If raise_error is True and columns are missing
    """
    table_columns = [col.name for col in table.columns]
    missing = [col for col in required_columns if col not in table_columns]

    if missing:
        if raise_error:
            raise ValueError(
                f"Column(s) {missing} not found in table. "
                f"Available columns: {', '.join(table_columns)}"
            )
        return False
    return True


def get_table_info(table: Table) -> dict:
    """Get basic information about a table."""
    return {
        "num_rows": table.size,
        "num_columns": len(table.columns),
        "columns": [col.name for col in table.columns],
    }
```

Create `src/my_dh_library/queries.py`:

```python
"""Reusable Deephaven query functions."""

from deephaven.table import Table
from deephaven import agg
from .utils import validate_columns


def filter_by_threshold(table: Table, column: str, threshold: float) -> Table:
    """Filter table rows where column value exceeds threshold."""
    validate_columns(table, [column], raise_error=True)
    return table.where(f"{column} > {threshold}")


def add_computed_columns(table: Table) -> Table:
    """Add commonly used computed columns to a table."""
    validate_columns(table, ["Value"], raise_error=True)
    return table.update(
        [
            "DoubleValue = Value * 2",
            "IsHigh = Value > 100",
        ]
    )


def summarize_by_group(table: Table, group_col: str, value_col: str) -> Table:
    """Create summary statistics grouped by a column."""
    validate_columns(table, [group_col, value_col], raise_error=True)
    return table.agg_by(
        [
            agg.sum_(f"Sum = {value_col}"),
            agg.avg(f"Avg = {value_col}"),
            agg.count_("Count"),
        ],
        by=[group_col],
    )
```

Create `README.md` with installation and usage instructions.

### Create a CLI-only package

Create the directory structure:

```bash
mkdir -p my_dh_cli/src/my_dh_cli
cd my_dh_cli
```

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my_dh_cli"
version = "0.1.0"
description = "Command line tool for data processing"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
  # deephaven-server also provides the deephaven module (through its deephaven-core dependency).
  "deephaven-server>=0.35.0",
  # click implements the command line interface.
  "click>=8.0.0",
]

[project.scripts]
my-dh-query = "my_dh_cli.cli:app"

[tool.setuptools.packages.find]
where = ["src"]
```

Create `src/my_dh_cli/__init__.py`:

```python
"""Command line tool that processes a CSV file with Deephaven."""

__version__ = "0.1.0"
```

Create `src/my_dh_cli/__main__.py`:

```python
from my_dh_cli.cli import app

if __name__ == "__main__":
    app()
```

Create `src/my_dh_cli/cli.py`:

```python
import click


def my_dh_query(input_file: str, verbose: bool = False):
    """Read a CSV file and perform a simple query operation on the data."""
    from deephaven import read_csv
    from pathlib import Path

    input_path = Path(input_file)

    if not input_path.exists():
        raise click.ClickException(f"Input file does not exist: '{input_path}'")
    if not input_path.is_file():
        raise click.ClickException(f"Input path is not a file: '{input_path}'")

    if verbose:
        click.echo(f"Processing {input_file}...")

    try:
        source = read_csv(input_file)
    except Exception as e:
        raise click.ClickException(f"Failed to read CSV file '{input_file}': {e}")

    column_names = [col.name for col in source.columns]
    if "Score" not in column_names:
        raise click.ClickException(
            f"File '{input_path.name}' is missing required column 'Score'. "
            f"Available columns: {', '.join(column_names)}"
        )

    result = source.update(formulas=["DoubleScore = Score * 2"])

    if verbose:
        click.echo(f"Processed {result.size} rows")

    return result


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def app(input_file: str, verbose: bool) -> None:
    """Process data with Deephaven."""
    from deephaven_server import Server

    Server(port=10000, jvm_args=["-Xmx4g"]).start()

    my_dh_query(input_file, verbose)
    click.echo("Processing complete!")


if __name__ == "__main__":
    app()
```

Create `README.md` with installation and usage instructions.

### Create a combined package

Create the directory structure:

```bash
mkdir -p my_dh_toolkit/src/my_dh_toolkit
cd my_dh_toolkit
```

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my_dh_toolkit"
version = "0.1.0"
description = "Deephaven library and CLI tools"
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
  # deephaven-server also provides the deephaven module (through its deephaven-core dependency).
  "deephaven-server>=0.35.0",
  # click implements the command line interfaces.
  "click>=8.0.0",
]

[project.scripts]
my-dh-toolkit-query = "my_dh_toolkit.cli:app"
my-dh-toolkit-process = "my_dh_toolkit.processor:process"

[tool.setuptools.packages.find]
where = ["src"]
```

Create `src/my_dh_toolkit/__init__.py`:

```python
"""Deephaven query library and command line tools.

This __init__ deliberately imports nothing that requires Deephaven: the CLI
entry points import this package before a Deephaven server is running, so the
package must be importable without one. The library API lives in the
`my_dh_toolkit.queries` and `my_dh_toolkit.utils` submodules.
"""

__version__ = "0.1.0"
```

The import-free `__init__.py` is the key structural difference from a library-only package. See [Keep `__init__.py` free of Deephaven imports](#keep-__init__py-free-of-deephaven-imports).

Create `src/my_dh_toolkit/__main__.py`:

```python
from my_dh_toolkit.cli import app

if __name__ == "__main__":
    app()
```

Create the library modules `src/my_dh_toolkit/queries.py` and `src/my_dh_toolkit/utils.py` using the same code as the library-only package.

Create `src/my_dh_toolkit/cli.py`. It follows the same pattern as the CLI-only package, but the query calls the package's own `validate_columns` and `add_computed_columns`. Those imports are inside the function so that they run after the server has started:

```python
import click


def my_dh_query(input_file: str, verbose: bool = False):
    """Read a CSV file and add computed columns using the package's library functions."""
    # Imported here, not at module level: these modules import deephaven, which
    # requires a running server. The entry point starts the server first, then
    # calls this function.
    from deephaven import read_csv
    from my_dh_toolkit.queries import add_computed_columns
    from my_dh_toolkit.utils import validate_columns
    from pathlib import Path

    input_path = Path(input_file)

    if not input_path.exists():
        raise click.ClickException(f"Input file does not exist: '{input_path}'")
    if not input_path.is_file():
        raise click.ClickException(f"Input path is not a file: '{input_path}'")

    if verbose:
        click.echo(f"Processing {input_file}...")

    try:
        source = read_csv(input_file)
    except Exception as e:
        raise click.ClickException(f"Failed to read CSV file '{input_file}': {e}")

    try:
        validate_columns(source, ["Value"], raise_error=True)
    except ValueError as e:
        raise click.ClickException(f"File '{input_path.name}': {e}")

    result = add_computed_columns(source)

    if verbose:
        click.echo(f"Processed {result.size} rows")

    return result


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def app(input_file: str, verbose: bool) -> None:
    """Process data with Deephaven."""
    from deephaven_server import Server

    Server(port=10000, jvm_args=["-Xmx4g"]).start()

    my_dh_query(input_file, verbose)
    click.echo("Processing complete!")


if __name__ == "__main__":
    app()
```

Create `src/my_dh_toolkit/processor.py`, a second command that applies the same library functions to every CSV file in a directory:

```python
import click
from pathlib import Path


def batch_process(directory: str, output_dir: str, verbose: bool = False) -> None:
    """Process multiple CSV files from a directory."""
    input_path = Path(directory)
    output_path = Path(output_dir)

    if not input_path.exists():
        raise click.ClickException(f"Input directory does not exist: '{input_path}'")
    if not input_path.is_dir():
        raise click.ClickException(f"Input path is not a directory: '{input_path}'")
    if input_path.resolve() == output_path.resolve():
        raise click.ClickException(
            f"Input and output directories must be different: '{input_path}'"
        )

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.ClickException(f"Permission denied: Cannot create output directory '{output_path}'")
    except OSError as e:
        raise click.ClickException(f"Failed to create output directory '{output_path}': {e}")

    # Imported here, not at module level: these modules import deephaven, which
    # requires a running server. The entry point starts the server first, then
    # calls this function.
    from deephaven import read_csv, write_csv
    from my_dh_toolkit.queries import add_computed_columns
    from my_dh_toolkit.utils import validate_columns

    csv_files = list(input_path.glob("*.csv"))

    if verbose:
        click.echo(f"Found {len(csv_files)} CSV files to process")

    for csv_file in csv_files:
        if verbose:
            click.echo(f"Processing {csv_file.name}...")

        try:
            table = read_csv(str(csv_file))
        except Exception as e:
            raise click.ClickException(f"Failed to read CSV file '{csv_file}': {e}")

        try:
            validate_columns(table, ["Value"], raise_error=True)
        except ValueError as e:
            raise click.ClickException(f"File '{csv_file.name}': {e}")

        processed = add_computed_columns(table)

        output_file = output_path / f"processed_{csv_file.name}"
        try:
            write_csv(processed, str(output_file))
        except Exception as e:
            raise click.ClickException(f"Failed to write output file '{output_file}': {e}")

        if verbose:
            click.echo(f"  Processed {processed.size} rows -> {output_file.name}")


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def process(directory: str, output: str, verbose: bool) -> None:
    """Batch process CSV files with Deephaven."""
    from deephaven_server import Server

    Server(port=10000, jvm_args=["-Xmx4g"]).start()

    batch_process(directory, output, verbose)
    click.echo("Batch processing complete!")


if __name__ == "__main__":
    process()
```

Create `README.md` with installation and usage instructions.

</details>

## Next steps

The [deephaven-python-packaging](https://github.com/deephaven-examples/deephaven-python-packaging) repository provides complete, working examples of all three packaging scenarios, along with sample data in its `data/` directory. Clone it and adapt the example that matches your project.

## Related documentation

- [Install and use Python packages](https://deephaven.io/core/docs/how-to-guides/install-and-use-python-packages/)
- [Use the Deephaven Python package](https://deephaven.io/core/docs/how-to-guides/deephaven-python-package/)
- [Writing your `pyproject.toml`](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [src layout vs flat layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)
- [Creating and packaging command-line tools](https://packaging.python.org/en/latest/guides/creating-command-line-tools/)
- [Setuptools documentation](https://setuptools.pypa.io/)
- [Click documentation](https://click.palletsprojects.com/)
