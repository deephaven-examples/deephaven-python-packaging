# Deephaven Python packaging examples

This repository shows how to package Python code that uses [Deephaven Community Core](https://deephaven.io/community/) so that it can be installed with `pip`. It contains five small, self-contained example packages. Each example demonstrates one packaging pattern:

| Example | Server model (dependency) | Pattern | Installing it provides |
|---|---|---|---|
| [`my_dh_library/`](my_dh_library/) | Inside a server (`deephaven-core`) | Library only | Functions to import in Python code |
| [`my_dh_cli/`](my_dh_cli/) | Embedded server (`deephaven-server`) | Command line tool only | A `my-dh-cli-query` terminal command |
| [`my_dh_toolkit/`](my_dh_toolkit/) | Embedded server (`deephaven-server`) | Library and command line tools combined | Importable functions plus `my-dh-toolkit-query` and `my-dh-toolkit-process` commands |
| [`my_dh_client_library/`](my_dh_client_library/) | Remote client (`pydeephaven`) | Library only | Functions to import in Python code |
| [`my_dh_client/`](my_dh_client/) | Remote client (`pydeephaven`) | Command line tool only | A `my-dh-client-query` terminal command |

All five examples follow the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) conventions: a `pyproject.toml` file for metadata, dependencies, and entry points, and the src-layout for source code. This repository accompanies the [Package a Deephaven Python project](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) guide, which explains the underlying concepts in depth.

## Quick start

With Python 3.9 or later and Java 17 or later (with `JAVA_HOME` set), clone the repository, create a virtual environment, and run the command line example:

```bash
git clone https://github.com/deephaven-examples/deephaven-python-packaging.git
cd deephaven-python-packaging
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
pip install -e ./my_dh_cli
my-dh-cli-query data/sample.csv
```

The command starts a Deephaven server, adds a column to the sample data, prints the first five rows, and exits. All commands in this README are run from the repository root, inside the activated virtual environment.

## Three ways to work with a Deephaven server

A packaged project uses Deephaven in one of three ways. The choice determines which Deephaven package it depends on.

- **Inside a running server.** The package is installed into a Deephaven server's own Python environment, such as a custom Docker image or the virtual environment of a pip-installed server, and imported from the server's console or scripts.
  - Depend on [`deephaven-core`](https://pypi.org/project/deephaven-core/), which provides the server-side `deephaven` API without a server of its own.
  - The server is already running, so code imports `deephaven` directly.
  - Example 1 is written for this model.
- **Embedded server.** The package starts a Deephaven server inside its own Python process.
  - Depend on [`deephaven-server`](https://pypi.org/project/deephaven-server/), which includes `deephaven-core`.
  - Every machine that runs it needs Java.
  - The code must create a `deephaven_server.Server` before importing `deephaven`. See [Import order for the `deephaven` module](#import-order-for-the-deephaven-module).
  - Examples 2 and 3 use this model. Example 1 can also run this way.
- **Remote client.** The package connects to a server that is already running, possibly on another machine.
  - Depend on [`pydeephaven`](https://pypi.org/project/pydeephaven/), the Deephaven Python client. It does not start a server, does not need Java, and can be imported at any time.
  - It works with tables through a `Session`. Its table API mirrors the server-side one closely but is not identical.
  - Examples 4 and 5 use this model.

The packaging tooling is the same in all three cases. What differs is the dependency and, for the server-side `deephaven` API, the import order.

### Import order for the `deephaven` module

`deephaven` modules can only be imported in a process where the Deephaven JVM is running. Inside a server, it always is. In a standalone Python process, creating a `deephaven_server.Server` starts the JVM, and `server.start()` is a separate step that starts the server itself. Importing `deephaven` (or a package that imports it) before creating the `Server` fails:

```text
>>> import deephaven
RuntimeError: The Deephaven Server has not been initialized. Please ensure that deephaven_server.Server has been constructed before importing deephaven.
```

This rule shapes how the examples are written:

- The commands in Examples 2 and 3 import `deephaven` inside a function that runs after `main()` has created the `Server`, not at the top of the module.
- When a command starts, Python imports its package, including `__init__.py`, before `main()` runs. That is why [`my_dh_toolkit/__init__.py`](my_dh_toolkit/src/my_dh_toolkit/__init__.py) contains no imports: if it re-exported the query functions, every toolkit command would fail at startup with the error above. Python users import the toolkit's functions from its submodules instead, such as `my_dh_toolkit.queries`.
- `my_dh_library` has no commands, so its `__init__.py` can re-export its functions. It is only imported inside a server or after the calling program has created a `Server`.

`pydeephaven` has no such rule.

## Choose an example

- Start from **`my_dh_library`** to share reusable functions that other projects, or code running in a Deephaven server, import. There is no command line interface.
- Start from **`my_dh_cli`** to ship a tool that users run from a terminal. No library code is exposed.
- Start from **`my_dh_toolkit`** to provide both: importable functions for Python users and commands for terminal users.
- Start from **`my_dh_client_library`** or **`my_dh_client`** when the program should connect to a server you already have running instead of starting its own.

## Prerequisites

- Python 3.9 or later, and pip. A virtual environment is recommended, as shown in the [Quick start](#quick-start).
- For Examples 2 and 3, and for Example 1 when it runs outside a server: Java 17 or later with `JAVA_HOME` set, required by `deephaven-server`. `pip` does not install Java.
- For Examples 4 and 5: a running Deephaven server to connect to. See [Start a server for the client examples](#start-a-server-for-the-client-examples).
- The examples declare Deephaven 0.35.0 or later as their dependency. For the latest version, see [deephaven.io](https://deephaven.io/).

The embedded servers in Examples 1 to 3 listen on port 10001 rather than Deephaven's usual 10000. That way they don't collide with the server on port 10000 that Examples 4 and 5 connect to.

## Sample data

The examples read the CSV files in the `data/` directory:

- `data/sample.csv`: a single 10-row file with `Name`, `Score`, `Value`, and `Category` columns. It is the input for the single-file examples: the library snippets, `my-dh-cli-query`, `my-dh-toolkit-query`, and `my-dh-client-query`.
- `data/batch/`: three smaller files (`file1.csv`, `file2.csv`, and `file3.csv`) with the same columns but different rows. It is the input for `my-dh-toolkit-process`, which processes every CSV file in a directory.

## Example 1: `my_dh_library`, a library for use inside a server

This example packages reusable Deephaven query functions so that other projects can `pip install` the package and import the functions. It depends on `deephaven-core`, not `deephaven-server`, so installing it does not bring a server of its own. Whatever imports it supplies the running JVM.

```
my_dh_library/
├── src/
│   └── my_dh_library/
│       ├── __init__.py     # Exports the public API
│       ├── queries.py      # Query functions: filter, compute, summarize
│       └── utils.py        # Table validation helpers
├── pyproject.toml          # Declares metadata and the deephaven-core dependency
└── README.md
```

There is no `[project.scripts]` section in `pyproject.toml` and no `__main__.py`, because this package is only ever imported.

### Try it inside a server

Install the library into the same environment as a Deephaven server, then use it from the server's console. To try this locally with a pip-installed server:

```bash
pip install -e ./my_dh_library deephaven-server
deephaven server --port 10001
```

Open the URL the server prints, which includes its login key, and run this in the console:

```python
from my_dh_library import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
```

`filtered` appears in the IDE with 9 of the 10 rows. There is no `Server` to create, because the code already runs inside one. For Docker deployments, install the package in a custom image based on `ghcr.io/deephaven/server`, as described in [Install and use Python packages](https://deephaven.io/core/docs/how-to-guides/install-and-use-python-packages/).

### Try it in a standalone Python process

The same library also works from a plain Python process, which then has to create its own `Server` first. With `deephaven-server` installed as above, start `python` and run:

```python
# Creating a Server starts the JVM, which deephaven modules need at import time.
from deephaven_server import Server
server = Server(port=10001, jvm_args=["-Xmx4g"])
server.start()

# Import and use the installed library.
from my_dh_library import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

After the server's startup log, this prints:

```text
9 of 10 rows have Score > 75
```

### What to study

- [`pyproject.toml`](my_dh_library/pyproject.toml): the `dependencies` list declares `deephaven-core`. A Deephaven server already has it, so installing the library into a server adds nothing else and doesn't change the server's Deephaven version. `[tool.setuptools.packages.find]` points setuptools at `src/`.
- [`queries.py`](my_dh_library/src/my_dh_library/queries.py): plain functions that take and return Deephaven tables.
- [`__init__.py`](my_dh_library/src/my_dh_library/__init__.py): re-exports the public functions. Because of this, even `import my_dh_library` needs a running JVM. See [Import order](#import-order-for-the-deephaven-module).

## Example 2: `my_dh_cli` — an embedded-server command line tool

This example packages a Deephaven script as a terminal command. `pip install` creates a `my-dh-cli-query` command that users run without writing any Python. The command starts its own server, so it does not need a separately running Deephaven server. It does need Java on the machine that runs it.

```
my_dh_cli/
├── src/
│   └── my_dh_cli/
│       ├── __init__.py
│       ├── __main__.py     # Enables `python -m my_dh_cli` during development
│       └── cli.py          # The command implementation
├── pyproject.toml          # Declares the my-dh-cli-query entry point
└── README.md
```

The command comes from one line in `pyproject.toml`:

```toml
[project.scripts]
my-dh-cli-query = "my_dh_cli.cli:main"
```

### Try it

Install the package, then run the command on the sample data:

```bash
pip install -e ./my_dh_cli
my-dh-cli-query data/sample.csv --verbose
```

The command starts a Deephaven server on port 10001, reads the CSV file, adds a computed `DoubleScore` column, and prints the first five rows. After the server's startup log, the output is:

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

### What to study

- [`pyproject.toml`](my_dh_cli/pyproject.toml): the `[project.scripts]` section maps the command name to a function.
- [`cli.py`](my_dh_cli/src/my_dh_cli/cli.py): a [Click](https://click.palletsprojects.com/) command that starts the Deephaven server itself, so it works as a standalone tool. It imports `deephaven` inside a function rather than at the top of the module, as explained in [Import order](#import-order-for-the-deephaven-module).
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

`my-dh-toolkit-query` processes one CSV file. `my-dh-toolkit-process` processes every CSV file in a directory and writes one result file per input to the output directory. Both commands validate that the input has a `Value` column (which must be numeric) and add `DoubleValue` and `IsHigh` columns by calling the library's `validate_columns` and `add_computed_columns`. Like `my-dh-cli-query`, each command starts its own Deephaven server.

After the server's startup log, `my-dh-toolkit-query` prints:

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

### Try the library

The same installation also provides the library. In a Python session, create and start a Deephaven server, then import the query functions from their submodule:

```python
# Creating a Server starts the JVM, which deephaven modules need at import time.
from deephaven_server import Server
server = Server(port=10001, jvm_args=["-Xmx4g"])
server.start()

# Import and use the installed library.
from my_dh_toolkit.queries import filter_by_threshold
from deephaven import read_csv

data = read_csv("data/sample.csv")
filtered = filter_by_threshold(data, "Score", 75.0)
print(f"{filtered.size} of {data.size} rows have Score > 75")
```

As in Example 1, this prints `9 of 10 rows have Score > 75`. Inside a running server, skip the `Server` lines.

### What to study

- [`pyproject.toml`](my_dh_toolkit/pyproject.toml): a single `[project.scripts]` section defines both commands.
- [`__init__.py`](my_dh_toolkit/src/my_dh_toolkit/__init__.py): deliberately contains no imports, so that the commands can start before they create a `Server`. See [Import order](#import-order-for-the-deephaven-module) for the failure this avoids.
- [`query.py`](my_dh_toolkit/src/my_dh_toolkit/query.py) and [`process.py`](my_dh_toolkit/src/my_dh_toolkit/process.py): one module per command, each defining the command's `main()`. Like `my_dh_cli`, both import `deephaven` and the library modules inside a function that runs after the `Server` has been created.

## Start a server for the client examples

The remaining two examples use `pydeephaven` and need a Deephaven server to connect to. Their defaults assume a server on `localhost:10000` that accepts anonymous connections. Either of these starts one:

```bash
# With Docker:
docker run --rm -p 10000:10000 \
  -e START_OPTS="-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler" \
  ghcr.io/deephaven/server:latest

# With pip-installed deephaven-server (already present if you installed Example 2 or 3):
deephaven server --port 10000 --no-browser \
  --jvm-args "-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler"
```

Leave the server running in that terminal and run the client examples from another one. The server's web IDE is at `http://localhost:10000`; the tables the examples bind appear there. Where possible, keep `pydeephaven` on the same version as the server it connects to.

A Deephaven server started without the `AuthHandlers` setting uses a [pre-shared key](https://deephaven.io/core/docs/how-to-guides/authentication/auth-psk/) instead, which it prints at startup. To connect to such a server, pass `auth_type="io.deephaven.authentication.psk.PskAuthenticationHandler"` and `auth_token="<key>"` to `Session`, or for `my-dh-client-query`, pass `--auth-type` and set `DH_AUTH_TOKEN`.

## Example 4: `my_dh_client_library` — a client library

This example provides the same reusable query functions as `my_dh_library`, written for `pydeephaven` so that they run against a server the calling program is already connected to.

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

This prints `9 of 10 rows have Score > 75`. `filtered` is now bound on the server, so it appears in the IDE and other clients can open it with `session.open_table("filtered")`. Call `filtered.to_arrow()` to bring the rows back into the client process as a pyarrow table.

### What to study

- [`pyproject.toml`](my_dh_client_library/pyproject.toml): the only difference from `my_dh_library` is `pydeephaven` in place of `deephaven-core`.
- [`queries.py`](my_dh_client_library/src/my_dh_client_library/queries.py): the functions take and return client-side `pydeephaven.Table` handles. Compare it with the `my_dh_library` version: the query strings and table operations are the same, but the operations run on the server and only the handle comes back. `publish` wraps `session.bind_table`, which is how a client gives a table a name on the server.
- [`utils.py`](my_dh_client_library/src/my_dh_client_library/utils.py): `upload_csv` reads a CSV file locally with pyarrow and sends it with `session.import_table`, because the server cannot see the client's files. Column names come from `table.schema.names` rather than `table.columns`.
- [`__init__.py`](my_dh_client_library/src/my_dh_client_library/__init__.py): re-exports the public functions. `pydeephaven` can be imported at any time, so there are no import-ordering concerns in a client package, with or without commands.

## Example 5: `my_dh_client` — a client command line tool

This example packages a `pydeephaven` program as a terminal command. `pip install` creates a `my-dh-client-query` command that uploads a CSV file to a running server, processes it there, and binds the result under a name.

```
my_dh_client/
├── src/
│   └── my_dh_client/
│       ├── __init__.py
│       ├── __main__.py     # Enables `python -m my_dh_client` during development
│       └── cli.py          # The command implementation
├── pyproject.toml          # Declares the my-dh-client-query entry point
└── README.md
```

### Try it

With a server running, install the package and run the command on the sample data:

```bash
pip install -e ./my_dh_client
my-dh-client-query data/sample.csv --verbose
```

The command connects to `localhost:10000`, uploads the file, adds a computed `DoubleScore` column on the server, and binds the result as a table named `sample`:

```text
Uploading data/sample.csv...
Processed 10 rows
Bound result table 'sample' on localhost:10000
```

Open the IDE to see the table. Pass `--host` and `--port` to reach a different server, `--name` to choose the table name (it must be a valid Python identifier, so a file such as `my-scores.csv` needs one), and `--auth-type` plus the `DH_AUTH_TOKEN` environment variable for a server that requires a token.

### What to study

- [`pyproject.toml`](my_dh_client/pyproject.toml): the same `[project.scripts]` pattern as `my_dh_cli`, with `pydeephaven` as the dependency.
- [`cli.py`](my_dh_client/src/my_dh_client/cli.py): imports `pydeephaven` at the top of the module, where `my_dh_cli` has to delay its `deephaven` import until after it creates a `Server`. The command checks that the table name (the file's stem, or `--name`) is a valid Python identifier before it connects. The command takes connection options instead of a port to bind, and reads the authentication token from the environment so it stays out of shell history. `Session` is used as a context manager so the connection closes when the command exits.
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

5. **Replace the example logic** with your own code, and add any packages it needs to `dependencies` in `pyproject.toml`. Keep the Deephaven dependency in the list so it installs automatically: `deephaven-core` for code that runs inside a server, `deephaven-server` for code that starts an embedded server, or `pydeephaven` for a client.

6. **Reinstall and test:**

   ```bash
   pip install -e .
   my-tool --help
   ```

Three names must stay in sync: the package directory under `src/`, the module paths in `[project.scripts]`, and the package name in `import` statements.

## Install and distribute

The examples above use editable installs (`pip install -e ./my_dh_cli`), which pick up source edits without reinstalling. This is ideal while developing. The other common options:

- **Regular install from source:** `pip install ./my_dh_cli`
- **Build and install a wheel**, the format to use when distributing a package to other machines or publishing to a package index:

  ```bash
  pip install build
  python -m build my_dh_cli
  pip install my_dh_cli/dist/my_dh_cli-0.1.0-py3-none-any.whl
  ```

  Wheels can be shared directly or published to PyPI with [`twine`](https://twine.readthedocs.io/).

## Troubleshooting

- **Command not found after installation:** confirm the install succeeded (`pip show my_dh_cli`) and that the Python scripts directory is on `PATH`. Installing inside an activated virtual environment avoids most `PATH` issues.
- **`Address already in use` when an embedded-server command or snippet starts:** Examples 1 to 3 bind their server to port 10001 by default. If another process already uses that port, pass a free port to the commands with `--port`, or change the `port` value in the `Server(...)` call in the library snippets.
- **`The Deephaven Server has not been initialized`:** a `deephaven` module, or a package that imports one, was imported before a `deephaven_server.Server` was created. See [Import order for the `deephaven` module](#import-order-for-the-deephaven-module). Creating the `Server` also requires Java 17 or later through `JAVA_HOME`.
- **`No module named 'deephaven_server'` when running Example 1 standalone:** `my_dh_library` depends only on `deephaven-core`. Install `deephaven-server` as well to create a `Server` in your own process.
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
