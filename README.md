# Deephaven Python packaging examples

This repository shows how to package Python code that uses [Deephaven Community Core](https://deephaven.io/community/) so that it can be installed with `pip`. It contains five small, self-contained example packages. Each example demonstrates one packaging pattern:

| Example | Deephaven package | Pattern | Installing it provides |
|---|---|---|---|
| [`my_dh_library/`](my_dh_library/) | `deephaven-server` | Library only | Functions to import in Python code |
| [`my_dh_cli/`](my_dh_cli/) | `deephaven-server` | Command line tool only | A `my-dh-query` terminal command |
| [`my_dh_toolkit/`](my_dh_toolkit/) | `deephaven-server` | Library and command line tools combined | Importable functions plus `my-dh-toolkit-query` and `my-dh-toolkit-process` commands |
| [`my_dh_client_library/`](my_dh_client_library/) | `pydeephaven` | Library only | Functions to import in Python code |
| [`my_dh_client/`](my_dh_client/) | `pydeephaven` | Command line tool only | A `my-dh-client` terminal command |

All five examples follow the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) conventions: a `pyproject.toml` file for metadata, dependencies, and entry points, and the src-layout for source code. This repository accompanies the [Package a Deephaven Python project](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) guide, which explains the underlying concepts in depth.

## Two ways to work with a Deephaven server

A packaged project can work with a Deephaven server in one of two ways, and the choice decides which Deephaven package it depends on:

- **Embedded server.** The package depends on [`deephaven-server`](https://pypi.org/project/deephaven-server/), which starts a Deephaven server and its JVM inside the Python process. The code then uses the server-side `deephaven` API in that same process. This fits self-contained tools and batch jobs that should run without any other infrastructure. It comes with one rule that shapes how these packages are written: `deephaven` modules cannot be imported until the server has started. Examples 1 to 3 use this model.
- **Remote client.** The package depends on [`pydeephaven`](https://pypi.org/project/pydeephaven/), the Deephaven Python client, and connects to a server that is already running, such as one started with Docker. The client does not start a server, does not need Java, and can be imported at any time. It works with tables through a `Session`, and its table API mirrors the server-side one closely but is not identical. Examples 4 and 5 use this model.

The packaging tooling is the same for both. What differs is the dependency and, for the embedded server, the import ordering.

## Choose an example

- Start from **`my_dh_library`** to share reusable functions that other projects import. There is no command line interface.
- Start from **`my_dh_cli`** to ship a tool that users run from a terminal. No library code is exposed.
- Start from **`my_dh_toolkit`** to provide both: importable functions for Python users and commands for terminal users.
- Start from **`my_dh_client_library`** or **`my_dh_client`** when the program should connect to a server you already have running instead of starting its own.

## Prerequisites

- Python 3.9 or later.
- pip.
- For the embedded-server examples (1 to 3): Java 17 or later, required by `deephaven-server`, which those examples install as a dependency.
- For the client examples (4 and 5): a running Deephaven server to connect to. See [Start a server for the client examples](#start-a-server-for-the-client-examples).
- The examples declare `deephaven-server` or `pydeephaven` 0.35.0 or later as their dependency. For the latest Deephaven version, see [deephaven.io](https://deephaven.io/).

## Get the examples

Clone the repository and work from its root directory. All commands below are run from the repository root.

```bash
git clone https://github.com/deephaven-examples/deephaven-python-packaging.git
cd deephaven-python-packaging
```

## Sample data

The examples read the CSV files in the `data/` directory:

- `data/sample.csv`: a single 10-row file with `Name`, `Score`, `Value`, and `Category` columns. It is the input for the single-file examples: the library snippets, `my-dh-query`, `my-dh-toolkit-query`, and `my-dh-client`.
- `data/batch/`: three smaller files (`file1.csv`, `file2.csv`, and `file3.csv`) with the same columns but different rows. It is the input for `my-dh-toolkit-process`, which processes every CSV file in a directory.

## Example 1: `my_dh_library` — an embedded-server library

**The story:** package reusable Deephaven query functions so that other projects can `pip install` the package and import the functions. The importing program starts the embedded server.

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

```bash
pip install -e ./my_dh_library
python
```

A library built on `deephaven-server` needs a running server in the same process, so start one before importing `deephaven` modules:

```python
# A Deephaven server must be running before deephaven modules are imported.
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Import and use the installed library.
from my_dh_library.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

### What to study

- [`pyproject.toml`](my_dh_library/pyproject.toml): the `dependencies` list installs `deephaven-server` automatically, and `[tool.setuptools.packages.find]` points setuptools at `src/`.
- [`queries.py`](my_dh_library/src/my_dh_library/queries.py): plain functions that take and return Deephaven tables.
- [`__init__.py`](my_dh_library/src/my_dh_library/__init__.py): re-exports the public functions.

## Example 2: `my_dh_cli` — an embedded-server command line tool

This example packages a Deephaven script as a terminal command. `pip install` creates a `my-dh-query` command that users run without writing any Python. The command starts its own server, so it works with no other infrastructure in place.

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
my-dh-query = "my_dh_cli.cli:main"
```

### Try it

Install the package, then run the command on the sample data:

```bash
pip install -e ./my_dh_cli
my-dh-query data/sample.csv --verbose
```

The command starts its own Deephaven server, reads the CSV file, adds a computed `DoubleScore` column, and reports the row count. No separate setup is needed.

### What to study

- [`pyproject.toml`](my_dh_cli/pyproject.toml): the `[project.scripts]` section maps the command name to a function.
- [`cli.py`](my_dh_cli/src/my_dh_cli/cli.py): a [Click](https://click.palletsprojects.com/) command that starts the Deephaven server itself, so it works as a standalone tool. It imports `deephaven` inside the function that runs after the server has started, not at the top of the module, because `deephaven` modules can't be imported until a server is running.
- [`__main__.py`](my_dh_cli/src/my_dh_cli/__main__.py): allows `python -m my_dh_cli data/sample.csv` as an alternative during development.

## Example 3: `my_dh_toolkit` — an embedded-server library and command line tools in one package

In this example, one package provides both interfaces. Python users import its query functions, just as in `my_dh_library`; terminal users run its installed commands, just as in `my_dh_cli`. The commands call the package's own library functions, so there is one implementation behind both interfaces.

`queries.py` and `utils.py` are copies of the `my_dh_library` modules rather than a dependency on that package. The duplication is deliberate: it keeps each example self-contained, so you can copy any one of them on its own.

```
my_dh_toolkit/
├── src/
│   └── my_dh_toolkit/
│       ├── __init__.py     # Intentionally contains no imports (see "What to study")
│       ├── __main__.py     # Enables `python -m my_dh_toolkit` (runs the query command)
│       ├── query.py        # Implements my-dh-toolkit-query (same Click pattern as my_dh_cli)
│       ├── process.py      # Implements my-dh-toolkit-process
│       ├── queries.py      # Library query functions (same code as my_dh_library)
│       └── utils.py        # Library table helpers (same code as my_dh_library)
├── pyproject.toml          # Declares both commands
└── README.md
```

### Try the commands

Install the package, then run each command:

```bash
pip install -e ./my_dh_toolkit
my-dh-toolkit-query data/sample.csv --verbose
my-dh-toolkit-process data/batch --output output --verbose
```

`my-dh-toolkit-query` processes one CSV file. `my-dh-toolkit-process` processes every CSV file in a directory and writes one result file per input to the output directory. Both commands validate that the input has a `Value` column (which must be numeric) and add `DoubleValue` and `IsHigh` columns by calling the library's `validate_columns` and `add_computed_columns`. Like `my-dh-query` in the previous example, each command starts its own Deephaven server.

### Try the library

The same installation also provides the library. In a Python session, start a Deephaven server, then import and use the query functions:

```python
# A Deephaven server must be running before deephaven modules are imported.
from deephaven_server import Server
server = Server(port=10000, jvm_args=["-Xmx4g"])
server.start()

# Import and use the installed library.
from my_dh_toolkit.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

### What to study

- [`pyproject.toml`](my_dh_toolkit/pyproject.toml): a single `[project.scripts]` section defines both commands.
- [`__init__.py`](my_dh_toolkit/src/my_dh_toolkit/__init__.py): deliberately contains no imports.
  - Importing any `deephaven` module fails unless a Deephaven server is already running in the process.
  - When a command such as `my-dh-toolkit-query` starts, Python imports the `my_dh_toolkit` package before the command has started its server. If `__init__.py` imported the query functions, the import would reach `deephaven` and every command would fail at startup.
  - For this reason, Python users import the library from its submodules (`my_dh_toolkit.queries`, `my_dh_toolkit.utils`). `my_dh_library` can re-export its functions from `__init__.py` because it has no commands, so it is only imported after a server is running.
- [`query.py`](my_dh_toolkit/src/my_dh_toolkit/query.py) and [`process.py`](my_dh_toolkit/src/my_dh_toolkit/process.py): one module per command, each defining the command's `main()`. Like `my_dh_cli`, both import `deephaven` and the library modules inside the function that runs after the server has started.

## Start a server for the client examples

The remaining two examples use `pydeephaven` and need a Deephaven server to connect to. Their defaults assume a server on `localhost:10000` that accepts anonymous connections. Either of these starts one:

```bash
# With Docker:
docker run --rm -p 10000:10000 \
  -e START_OPTS="-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler" \
  ghcr.io/deephaven/server:latest

# With pip-installed deephaven-server (already present if you installed examples 1 to 3):
deephaven server --port 10000 --no-browser \
  --jvm-args "-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler"
```

Leave the server running in that terminal and run the client examples from another one. The server's web IDE is at `http://localhost:10000`; the tables the examples bind appear there.

A Deephaven server started without the `AuthHandlers` setting uses a [pre-shared key](https://deephaven.io/core/docs/how-to-guides/authentication/auth-psk/) instead, which it prints at startup. To connect to such a server, pass `auth_type="io.deephaven.authentication.psk.PskAuthenticationHandler"` and `auth_token="<key>"` to `Session`, or for `my-dh-client`, pass `--auth-type` and set `DH_AUTH_TOKEN`.

## Example 4: `my_dh_client_library` — a client library

**The story:** the same reusable query functions as `my_dh_library`, written for `pydeephaven` so that they run against a server the calling program is already connected to.

```
my_dh_client_library/
├── src/
│   └── my_dh_client_library/
│       ├── __init__.py     # Re-exports the public API
│       ├── queries.py      # Query functions: filter, compute, summarize, publish
│       └── utils.py        # Upload a CSV, validate columns
├── pyproject.toml          # Declares metadata and the pydeephaven dependency
└── README.md
```

As in `my_dh_library`, there is no `[project.scripts]` section and no `__main__.py`.

### Try it

With a server running, install the package and start Python:

```bash
pip install -e ./my_dh_client_library
python
```

The calling program creates the `Session` and passes it to the library. There is nothing to start first:

```python
from pydeephaven import Session
from my_dh_client_library import upload_csv, filter_by_threshold, publish

with Session(host="localhost", port=10000) as session:
    data = upload_csv(session, "data/sample.csv")
    filtered = filter_by_threshold(data, "Score", 75.0)
    publish(session, "filtered", filtered)
    print(f"{filtered.size} of {data.size} rows have Score > 75")
```

`filtered` is now bound on the server, so it appears in the IDE and other clients can open it with `session.open_table("filtered")`. Call `filtered.to_arrow()` to bring the rows back into the client process as a pyarrow table.

### What to study

- [`pyproject.toml`](my_dh_client_library/pyproject.toml): the only difference from `my_dh_library` is `pydeephaven` in place of `deephaven-server`.
- [`queries.py`](my_dh_client_library/src/my_dh_client_library/queries.py): the functions take and return client-side `pydeephaven.Table` handles. Compare it with the `my_dh_library` version: the query strings and table operations are the same, but the operations run on the server and only the handle comes back. `publish` wraps `session.bind_table`, which is how a client gives a table a name on the server.
- [`utils.py`](my_dh_client_library/src/my_dh_client_library/utils.py): `upload_csv` reads a CSV file locally with pyarrow and sends it with `session.import_table`, because the server cannot see the client's files. Column names come from `table.schema.names` rather than `table.columns`.
- [`__init__.py`](my_dh_client_library/src/my_dh_client_library/__init__.py): re-exports the public functions. `pydeephaven` can be imported at any time, so there are no import-ordering concerns in a client package, with or without commands.

## Example 5: `my_dh_client` — a client command line tool

This example packages a `pydeephaven` program as a terminal command. `pip install` creates a `my-dh-client` command that uploads a CSV file to a running server, processes it there, and binds the result under a name.

```
my_dh_client/
├── src/
│   └── my_dh_client/
│       ├── __init__.py
│       ├── __main__.py     # Enables `python -m my_dh_client` during development
│       └── cli.py          # The command implementation
├── pyproject.toml          # Declares the my-dh-client entry point
└── README.md
```

### Try it

With a server running, install the package and run the command on the sample data:

```bash
pip install -e ./my_dh_client
my-dh-client data/sample.csv --verbose
```

The command connects to `localhost:10000`, uploads the file, adds a computed `DoubleScore` column on the server, and binds the result as a table named `sample`. Open the IDE to see it. Pass `--host` and `--port` to reach a different server, `--name` to choose the table name, and `--auth-type` plus the `DH_AUTH_TOKEN` environment variable for a server that requires a token.

### What to study

- [`pyproject.toml`](my_dh_client/pyproject.toml): the same `[project.scripts]` pattern as `my_dh_cli`, with `pydeephaven` as the dependency.
- [`cli.py`](my_dh_client/src/my_dh_client/cli.py): imports `pydeephaven` at the top of the module, where `my_dh_cli` has to delay its `deephaven` import until after the server starts. The command takes connection options instead of a port to bind, and reads the authentication token from the environment so it stays out of shell history. `Session` is used as a context manager so the connection closes when the command exits.
- [`__main__.py`](my_dh_client/src/my_dh_client/__main__.py): allows `python -m my_dh_client data/sample.csv` as an alternative during development.

## Adapt an example for your own project

Each example is a template. To turn one into your own package:

1. **Copy the example** that matches your scenario:

   ```bash
   cp -r my_dh_cli my_tool
   cd my_tool
   ```

2. **Rename the import package.** The directory under `src/` is the name used in `import` statements:

   ```bash
   mv src/my_dh_cli src/my_tool
   ```

3. **Update `pyproject.toml`.** Set your own `name`, `version`, and `description`, and point any `[project.scripts]` entries at the new package:

   ```toml
   [project]
   name = "my_tool"

   [project.scripts]
   my-tool = "my_tool.cli:main"
   ```

4. **Update internal imports** to the new package name (for example, `from my_tool.cli import main` in `__main__.py`).

5. **Replace the example logic** with your own code, and add any packages it needs to `dependencies` in `pyproject.toml`. Keep the Deephaven dependency in the list (`deephaven-server` for an embedded server, `pydeephaven` for a client) so it installs automatically.

6. **Reinstall and test:**

   ```bash
   pip install -e .
   my-tool --help
   ```

Three names must stay in sync: the package directory under `src/`, the module paths in `[project.scripts]`, and the package name in `import` statements.

## Install and distribute

The examples above use editable installs (`pip install -e ./my_dh_cli`), which pick up source edits without reinstalling. This is ideal while developing. The other common options:

- **Regular install from source:** `pip install ./my_dh_cli`
- **Build and install a wheel** — the format to use when distributing a package to other machines or publishing to a package index:

  ```bash
  pip install build
  python -m build my_dh_cli
  pip install my_dh_cli/dist/my_dh_cli-0.1.0-py3-none-any.whl
  ```

  Wheels can be shared directly or published to PyPI with [`twine`](https://twine.readthedocs.io/).

## Troubleshooting

- **Command not found after installation:** confirm the install succeeded (`pip show my_dh_cli`) and that the Python scripts directory is on `PATH`. Installing inside an activated virtual environment avoids most `PATH` issues.
- **`Address already in use` when an embedded-server command or snippet starts:** examples 1 to 3 bind the Deephaven server to port 10000. If another process already uses that port (for example, a Deephaven server running in Docker), change the `port` value in the `Server(...)` call to a free port.
- **`deephaven` import errors:** the Deephaven server must be started (as shown in the embedded-server library examples) before `deephaven` modules are imported, and Java 17 or later must be available. This does not apply to `pydeephaven`, which can be imported at any time.
- **`failed to get the configuration constants` from a client example:** `pydeephaven` could not complete its first request to the server. Either no server is listening at the given host and port, or the server requires authentication the client did not provide. Check that the server is running and, if it uses a pre-shared key, pass the key as described in [Start a server for the client examples](#start-a-server-for-the-client-examples).
- **Module not found after renaming:** check that the directory under `src/`, the `[project.scripts]` module paths, and the `import` statements all use the new package name, then reinstall with `pip install -e .`.

## Related documentation

- [Package a Deephaven Python project](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/), the guide this repository accompanies.
- [Choose the right Deephaven Python packages](https://deephaven.io/core/docs/reference/cheat-sheets/choose-python-packages/)
- [Install and use Python packages](https://deephaven.io/core/docs/how-to-guides/install-and-use-python-packages/)
- [Use the Deephaven Python package](https://deephaven.io/core/docs/how-to-guides/deephaven-python-package/)
- [Python Client Quickstart](https://deephaven.io/core/docs/getting-started/pyclient-quickstart/) and the [`pydeephaven` API reference](https://deephaven.io/core/client-api/python/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Click documentation](https://click.palletsprojects.com/)

## Contributing

Have improvements or additional examples? Contributions are welcome! Please open an issue or pull request on GitHub.

## License

This example code is provided under the Apache License 2.0.
