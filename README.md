# Python Packaging with Deephaven

This example demonstrates how to create and deploy Python packages that use Deephaven. It shows you how to package both command-line tools and reusable libraries using modern Python packaging standards.

This example accompanies the [Packaging custom code and dependencies](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) guide in the Deephaven documentation.

## What you'll learn

This example shows you how to:

- Create installable Python packages with Deephaven dependencies
- Build command-line tools that process data with Deephaven
- Package reusable library code for other projects
- Manage dependencies with `pyproject.toml`
- Distribute packages as wheel archives

## Project structure

The example includes three complete packaging scenarios:

### 1. Library-only package (`my_dh_library/`)

A reusable library with Deephaven query functions that other projects can import.

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

### 2. CLI-only package (`my_dh_cli/`)

Command-line tools for processing data with Deephaven.

```
my_dh_cli/
├── src/
│   └── my_dh_package/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── processor.py
├── pyproject.toml
├── data/
│   └── sample.csv
└── README.md
```

### 3. Combined package (`my_dh_toolkit/`)

Both reusable library code and command-line tools in one package.

```
my_dh_toolkit/
├── src/
│   └── my_dh_package/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── queries.py
│       └── utils.py
├── pyproject.toml
└── README.md
```

## Prerequisites

- Python 3.8 or later
- pip (Python package installer)
- Basic familiarity with Python packaging

## Quick start

Clone the repository:

```shell
git clone https://github.com/deephaven-examples/python-packaging.git
cd python-packaging
```

Choose an example to try:

### Try the CLI package

```shell
cd my_dh_cli
pip install -e .
my-dh-query data/sample.csv --verbose
my-dh-process data/ --output results/
```

### Try the library package

```shell
cd my_dh_library
pip install -e .
python
```

Then in Python:

```python
from my_dh_library.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("../data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"Filtered to {filtered.size} rows")
```

### Try the combined package

```shell
cd my_dh_toolkit
pip install -e .

# Use as a library
python -c "from my_dh_toolkit.queries import filter_by_threshold; print('Library imported successfully')"

# Use as CLI tools
my-dh-query ../data/sample.csv
my-dh-process ../data/ --output results/
```

## What's included

### Command-line tools

The CLI examples demonstrate:

- **Entry point scripts** - Commands installed to your PATH
- **Module execution** - Running with `python -m package_name`
- **Argument parsing** - Using Click for robust CLI interfaces
- **Multiple commands** - Single package with multiple tools
- **Verbose output** - Optional detailed logging

### Library modules

The library examples show:

- **Reusable query functions** - Common Deephaven operations
- **Type hints** - Proper function signatures
- **Public API exports** - Clean import patterns
- **Documentation** - Docstrings for all functions

### Configuration

All examples include:

- **`pyproject.toml`** - Modern Python packaging configuration
- **Dependency management** - Automatic installation of Deephaven and other requirements
- **Version constraints** - Ensuring compatible package versions
- **Entry points** - Mapping command names to Python functions

## Building and distributing

Each example can be built into a distributable wheel:

```shell
cd my_dh_cli  # or any example directory
pip install build
python -m build
```

This creates a `.whl` file in the `dist/` directory that can be:

- Installed locally: `pip install dist/my_dh_cli-0.1.0-py3-none-any.whl`
- Distributed to others
- Published to PyPI: `python -m twine upload dist/*`

## Running the examples

### Development mode

Install in editable mode to make changes without reinstalling:

```shell
pip install -e .
```

### Regular installation

Install from the built wheel:

```shell
pip install dist/package_name-0.1.0-py3-none-any.whl
```

### Without installation

Run directly from source using module execution:

```shell
python -m my_dh_package input_data.csv
```

## Sample data

The `data/` directory contains sample CSV files for testing:

- `sample.csv` - Small dataset with Name, Age, and Score columns
- `batch/` - Multiple CSV files for batch processing examples

You can use your own CSV files with these examples.

## Key concepts

### Entry point scripts vs module execution

The examples demonstrate two ways to run Python packages:

1. **Entry point scripts** - Commands defined in `[project.scripts]` that become available after installation
   ```shell
   my-dh-query data.csv
   ```

2. **Module execution** - Running packages with `python -m` without installation
   ```shell
   python -m my_dh_package data.csv
   ```

See the [Execution patterns](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/#execution-patterns) section of the guide for when to use each method.

### Package structure

All examples use the **src-layout**, which is the recommended structure for Python packages. This keeps source code separate from tests and configuration files.

### Dependencies

The examples show how to:

- Specify required packages (like `deephaven-server`)
- Set version constraints
- Define optional dependencies for features like visualization or testing

## Related documentation

- [Packaging custom code and dependencies](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) - Complete guide
- [Install and use Python packages](https://deephaven.io/core/docs/how-to-guides/install-and-use-python-packages/)
- [Use the Deephaven Python package](https://deephaven.io/core/docs/how-to-guides/deephaven-python-package/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Click documentation](https://click.palletsprojects.com/)

## Troubleshooting

### Command not found after installation

If your command isn't found after installation:

- Ensure the installation completed without errors
- Check that the installation directory is in your PATH
- Try reinstalling: `pip install --force-reinstall .`

### Import errors

If you encounter import errors:

- Verify all dependencies are installed: `pip list`
- Check that you're using Python 3.8 or later
- Ensure Deephaven is installed: `pip install deephaven-server`

### Module not found errors

If Python can't find your modules:

- Verify `__init__.py` files exist in all package directories
- Check that package names in `[project.scripts]` match your directory structure
- Try reinstalling in editable mode: `pip install -e .`

## Note

The code in this repository is built for Deephaven Community Core v0.35.0 or later. For the latest Deephaven version, see [deephaven.io](https://deephaven.io/).

## Contributing

Have improvements or additional examples? Contributions are welcome! Please open an issue or pull request on GitHub.

## License

This example code is provided under the Apache License 2.0.
