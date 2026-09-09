# Python Packaging with Deephaven

This repository demonstrates how to create and deploy Python packages that use Deephaven Community Core. It shows three complete packaging scenarios following the official [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) recommendations.

This example accompanies the [Packaging custom code and dependencies](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) guide in the Deephaven documentation.

## What you'll learn

- Create installable Python packages with Deephaven dependencies
- Package reusable library code for other projects
- Build command-line tools with entry point scripts
- Manage dependencies with `pyproject.toml`
- Use the src-layout structure
- Distribute packages as wheel archives

## Prerequisites

- Python 3.9 or later
- pip (Python package installer)
- Basic familiarity with Python packaging

## Repository structure

This repository contains three complete packaging scenarios:

### 1. Library-only package (`my_dh_library/`)

Reusable library code without CLI tools. Other projects import your modules.

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
from my_dh_library.queries import filter_by_threshold
```

### 2. CLI-only package (`my_dh_cli/`)

Command-line tool without exposing library code.

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
```shell
my-dh-query input_data.csv --verbose
```

### 3. Combined package (`my_dh_toolkit/`)

Both reusable library code and command-line tools.

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
```

```shell
# As CLI commands
my-dh-toolkit-query input_data.csv --verbose
my-dh-toolkit-process data/ --output results/ --verbose
```

## Quick start

Clone the repository:

```shell
git clone https://github.com/deephaven-examples/deephaven-python-packaging.git
cd deephaven-python-packaging
```

### Try the library-only package

```shell
cd my_dh_library
pip install -e .
python
```

Then in Python:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Now use the library functions
from my_dh_library.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("../data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
```

### Try the CLI-only package

Install the package, then run the installed command directly from a terminal. `my-dh-query` starts its own Deephaven server, so no separate session setup is needed:

```shell
cd my_dh_cli
pip install -e .
my-dh-query ../data/sample.csv --verbose
```

The underlying `my_dh_query()` function is also importable, so you can call it directly within a Python session that already has a server running (useful when composing it with other Deephaven code):

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Call the underlying function directly
from my_dh_cli.cli import my_dh_query
result = my_dh_query("../data/sample.csv", verbose=True)
print(f"Processed {result.size} rows")
```

### Try the combined package

Install the package, then run the installed commands directly from a terminal. Both `my-dh-toolkit-query` and `my-dh-toolkit-process` start their own Deephaven server:

```shell
cd my_dh_toolkit
pip install -e .
my-dh-toolkit-query ../data/sample.csv --verbose
my-dh-toolkit-process ../data/batch --output ./output --verbose
```

The library functions are also importable for use within a Python session that already has a server running:

```python
# Start the Deephaven server
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Use as a library
from my_dh_toolkit.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("../data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)

# Or call the underlying CLI functions directly
from my_dh_toolkit import my_dh_query, batch_process
result = my_dh_query("../data/sample.csv", verbose=True)
batch_process("../data/batch/", "./output", verbose=True)
```

## Sample data

The `data/` directory contains sample CSV files for testing:

- `sample.csv` - Single file with Name, Score, Value, and Category columns
- `batch/` - Multiple CSV files for batch processing examples

## Key concepts

### Package structure

All examples use the **src-layout**, which is the recommended structure for Python packages:

```
my_project/
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── module.py
├── pyproject.toml
└── README.md
```

The src-layout keeps source code separate from tests and configuration files.

### Entry point scripts

Entry point scripts are defined in `[project.scripts]` and become available after installation:

```toml
[project.scripts]
my-command = "my_package.module:function"
```

After `pip install`, you can run `my-command` from anywhere.

### Module execution

Add a `__main__.py` file to support running packages with `python -m`:

```python
from my_package.cli import app

if __name__ == "__main__":
    app()
```

This allows running without installation: `python -m my_package`

### Dependencies

Dependencies are specified in `pyproject.toml`:

```toml
[project]
dependencies = [
  "deephaven-server>=0.35.0",
  "click>=8.0.0",
]
```

These are automatically installed when users install your package.

## Building and distributing

Build a distributable wheel:

```shell
cd my_dh_cli  # or any package directory
pip install build
python -m build
```

This creates a `.whl` file in `dist/` that can be:

- Installed locally: `pip install dist/my_dh_cli-0.1.0-py3-none-any.whl`
- Distributed to others
- Published to PyPI: `python -m twine upload dist/*`

## Packaging scenarios

### When to use library-only

- Creating reusable code for other projects
- No command-line interface needed
- Code will be imported, not executed

**Example:** Data processing utilities, query functions, helper classes

### When to use CLI-only

- Building command-line tools for end users
- No library code to expose
- Want clean command names

**Example:** Data conversion tools, file processors, automation scripts

### When to use combined

- Need both library and CLI functionality
- Want to provide multiple interfaces
- Library functions useful on their own

**Example:** Data analysis toolkit with both API and CLI

## Execution patterns

### Entry point scripts (recommended for CLI tools)

**Configure in `pyproject.toml`:**
```toml
[project.scripts]
my-command = "my_package.module:function"
```

**Run after installation:**
```shell
my-command
```

**Benefits:**
- Clean command names
- Available system-wide
- Standard Python packaging approach

### Module execution (useful for development)

**Add `__main__.py`:**
```python
from my_package.cli import app

if __name__ == "__main__":
    app()
```

**Run without installation:**
```shell
python -m my_package
```

**Benefits:**
- No installation required
- Useful for development and testing
- Works from source directory

## Troubleshooting

### Command not found after installation

- Ensure installation completed without errors
- Check that the installation directory is in your PATH
- Try reinstalling: `pip install --force-reinstall .`

### Import errors

- Verify all dependencies are installed: `pip list`
- Check that you're using Python 3.9 or later
- Ensure Deephaven is installed: `pip install deephaven-server`

### Module not found errors

- Verify `__init__.py` files exist in all package directories
- Check that package names in `[project.scripts]` match your directory structure
- Try reinstalling in editable mode: `pip install -e .`

## Related documentation

- [Packaging custom code and dependencies](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) - Complete guide
- [Install and use Python packages](https://deephaven.io/core/docs/how-to-guides/install-and-use-python-packages/)
- [Use the Deephaven Python package](https://deephaven.io/core/docs/how-to-guides/deephaven-python-package/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Click documentation](https://click.palletsprojects.com/)

## Note

The code in this repository is built for Deephaven Community Core v0.35.0 or later. For the latest Deephaven version, see [deephaven.io](https://deephaven.io/).

## Contributing

Have improvements or additional examples? Contributions are welcome! Please open an issue or pull request on GitHub.

## License

This example code is provided under the Apache License 2.0.
