# Deephaven Python packaging examples

This repository shows how to package Python code that uses [Deephaven Community Core](https://deephaven.io/community/) so that it can be installed with `pip`. It contains three small, self-contained example packages. Each example demonstrates exactly one packaging pattern:

| Example | Pattern | Installing it provides |
|---|---|---|
| [`my_dh_library/`](my_dh_library/) | Library only | Functions to import in Python code |
| [`my_dh_cli/`](my_dh_cli/) | Command-line tool only | A `my-dh-query` terminal command |
| [`my_dh_toolkit/`](my_dh_toolkit/) | Library and command-line tools combined | Importable functions plus `my-dh-toolkit-query` and `my-dh-toolkit-process` commands |

`my_dh_toolkit` is the other two patterns merged into a single package: its library modules play the same role as `my_dh_library`, and its commands play the same role as `my_dh_cli`.

All three examples follow the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) conventions: a `pyproject.toml` file for metadata, dependencies, and entry points, and the src-layout for source code. This repository accompanies the [Packaging custom code and dependencies](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) guide, which explains the underlying concepts in depth.

## Choose an example

- Start from **`my_dh_library`** to share reusable functions that other projects import. There is no command-line interface.
- Start from **`my_dh_cli`** to ship a tool that users run from a terminal. No library code is exposed.
- Start from **`my_dh_toolkit`** to provide both: importable functions for Python users and commands for terminal users.

## Prerequisites

- Python 3.9 or later.
- pip.
- Java 17 or later (required by `deephaven-server`, which each example installs as a dependency).

## Get the examples

Clone the repository and work from its root directory. All commands below are run from the repository root.

```shell
git clone https://github.com/deephaven-examples/deephaven-python-packaging.git
cd deephaven-python-packaging
```

## Example 1: `my_dh_library` — a library

**The story:** package reusable Deephaven query functions so that other projects can `pip install` the package and import the functions.

```
my_dh_library/
├── src/
│   └── my_dh_library/
│       ├── __init__.py     # Exports the public API
│       ├── queries.py      # Query functions: filter, compute, summarize
│       └── utils.py        # Table validation helpers
├── pyproject.toml          # Declares metadata and the deephaven-server dependency
└── README.md
```

There is no `[project.scripts]` section in `pyproject.toml` and no `__main__.py` — this package is only ever imported.

### Try it

Install the package and start Python:

```shell
pip install -e ./my_dh_library
python
```

A library that uses Deephaven needs a running server in the same process, so start one before importing `deephaven` modules:

```python
# A Deephaven server must be running before deephaven modules are imported.
from deephaven_server import Server
Server(port=10000, jvm_args=["-Xmx4g"]).start()

# Import and use the installed library.
from my_dh_library.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

### What to study

- [`pyproject.toml`](my_dh_library/pyproject.toml) — the `dependencies` list installs `deephaven-server` automatically, and `[tool.setuptools.packages.find]` points setuptools at `src/`.
- [`queries.py`](my_dh_library/src/my_dh_library/queries.py) — plain functions that take and return Deephaven tables.
- [`__init__.py`](my_dh_library/src/my_dh_library/__init__.py) — re-exports the public functions.

## Example 2: `my_dh_cli` — a command-line tool

**The story:** package a Deephaven script as a terminal command. `pip install` creates a `my-dh-query` command that users run without writing any Python.

```
my_dh_cli/
├── src/
│   └── my_dh_cli/
│       ├── __init__.py
│       ├── __main__.py     # Enables `python -m my_dh_cli` during development
│       └── cli.py          # The command implementation
├── pyproject.toml          # Declares the my-dh-query entry point
└── README.md
```

The command comes from one line in `pyproject.toml`:

```toml
[project.scripts]
my-dh-query = "my_dh_cli.cli:app"
```

### Try it

Install the package, then run the command on the sample data:

```shell
pip install -e ./my_dh_cli
my-dh-query data/sample.csv --verbose
```

The command starts its own Deephaven server, reads the CSV file, adds a computed column, and reports the row count. No separate setup is needed.

### What to study

- [`pyproject.toml`](my_dh_cli/pyproject.toml) — the `[project.scripts]` section maps the command name to a function.
- [`cli.py`](my_dh_cli/src/my_dh_cli/cli.py) — a [Click](https://click.palletsprojects.com/) command that starts the Deephaven server itself, so it works as a standalone tool.
- [`__main__.py`](my_dh_cli/src/my_dh_cli/__main__.py) — allows `python -m my_dh_cli data/sample.csv` as an alternative during development.

## Example 3: `my_dh_toolkit` — a library and commands in one package

**The story:** one package, two interfaces. Terminal users get commands; Python users import functions. The library modules (`queries.py`, `utils.py`) match `my_dh_library`, and the command modules (`cli.py`, `processor.py`) follow the same pattern as `my_dh_cli`.

```
my_dh_toolkit/
├── src/
│   └── my_dh_toolkit/
│       ├── __init__.py     # Kept minimal — see "What to study" below
│       ├── __main__.py
│       ├── cli.py          # my-dh-toolkit-query command
│       ├── processor.py    # my-dh-toolkit-process command
│       ├── queries.py      # Library: query functions
│       └── utils.py        # Library: table validation helpers
├── pyproject.toml          # Declares two entry points
└── README.md
```

### Try the commands

Install the package, then run the two commands:

```shell
pip install -e ./my_dh_toolkit
my-dh-toolkit-query data/sample.csv --verbose
my-dh-toolkit-process data/batch --output output --verbose
```

`my-dh-toolkit-query` processes a single CSV file. `my-dh-toolkit-process` processes every CSV file in a directory and writes the results to the output directory. Both start their own Deephaven server.

### Try the library

The same installed package is importable. As with any Deephaven library, start a server first:

```python
# A Deephaven server must be running before deephaven modules are imported.
from deephaven_server import Server
Server(port=10000, jvm_args=["-Xmx4g"]).start()

# Import and use the installed library.
from my_dh_toolkit.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

### What to study

- [`pyproject.toml`](my_dh_toolkit/pyproject.toml) — `[project.scripts]` defines multiple commands for one package.
- [`__init__.py`](my_dh_toolkit/src/my_dh_toolkit/__init__.py) — deliberately imports nothing that requires Deephaven. The entry-point commands import the package before a server is running, so the library API stays in the `queries` and `utils` submodules, and the command modules defer their `deephaven` imports until after the server starts. This is the key structural difference from a library-only package.

## Sample data

The `data/` directory holds the inputs used by the examples above:

- `data/sample.csv` — one 10-row file with `Name`, `Score`, `Value`, and `Category` columns. Input for the library snippets, `my-dh-query`, and `my-dh-toolkit-query`.
- `data/batch/file1.csv`, `file2.csv`, `file3.csv` — three separate files with the same columns but different rows. Input for `my-dh-toolkit-process`, which processes every CSV file in the directory.

## Adapt an example for your own project

Each example is a template. To turn one into your own package:

1. **Copy the example** that matches your scenario:

   ```shell
   cp -r my_dh_cli my_tool
   cd my_tool
   ```

2. **Rename the import package** — the directory under `src/` is the name used in `import` statements:

   ```shell
   mv src/my_dh_cli src/my_tool
   ```

3. **Update `pyproject.toml`** — set your own `name`, `version`, and `description`, and point any `[project.scripts]` entries at the new package:

   ```toml
   [project]
   name = "my_tool"

   [project.scripts]
   my-tool = "my_tool.cli:app"
   ```

4. **Update internal imports** to the new package name (for example, `from my_tool.cli import app` in `__main__.py`).

5. **Replace the example logic** with your own code, and add any packages it needs to `dependencies` in `pyproject.toml`. Keep `deephaven-server` in the list so it installs automatically.

6. **Reinstall and test:**

   ```shell
   pip install -e .
   my-tool --help
   ```

Three names must stay in sync: the package directory under `src/`, the module paths in `[project.scripts]`, and the package name in `import` statements.

## Install and distribute

The examples above use editable installs (`pip install -e ./my_dh_cli`), which pick up source edits without reinstalling — ideal while developing. The other common options:

- **Regular install from source:** `pip install ./my_dh_cli`
- **Build and install a wheel** — the format to use when distributing a package to other machines or publishing to a package index:

  ```shell
  pip install build
  python -m build my_dh_cli
  pip install my_dh_cli/dist/my_dh_cli-0.1.0-py3-none-any.whl
  ```

  Wheels can be shared directly or published to PyPI with [`twine`](https://twine.readthedocs.io/).

## Troubleshooting

- **Command not found after installation** — confirm the install succeeded (`pip show my_dh_cli`) and that the Python scripts directory is on `PATH`. Installing inside an activated virtual environment avoids most `PATH` issues.
- **`deephaven` import errors** — the Deephaven server must be started (as shown in the library examples) before `deephaven` modules are imported, and Java 17 or later must be available.
- **Module not found after renaming** — check that the directory under `src/`, the `[project.scripts]` module paths, and the `import` statements all use the new package name, then reinstall with `pip install -e .`.

## Related documentation

- [Packaging custom code and dependencies](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) — the guide this repository accompanies.
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
