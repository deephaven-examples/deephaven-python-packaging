# Deephaven Python packaging examples

This repository shows how to package Python code that uses [Deephaven](https://deephaven.io/) so that it can be installed with `pip`. It contains five small, self-contained example packages. Each example demonstrates one packaging pattern:

| # | Example | Server model (dependency) | Pattern | Installing it provides |
|---|---|---|---|---|
| 1 | [`my_dh_library/`](my_dh_library/) | Inside a running server (`deephaven-core`) | Library only | Functions to import in Python code |
| 2 | [`my_dh_cli/`](my_dh_cli/) | Inside an embedded server (`deephaven-server`) | Command line tool only | A `my-dh-cli-query` terminal command |
| 3 | [`my_dh_toolkit/`](my_dh_toolkit/) | Inside an embedded server (`deephaven-server`) | Library and command line tools combined | Importable functions plus `my-dh-toolkit-query` and `my-dh-toolkit-process` commands |
| 4 | [`my_dh_client_library/`](my_dh_client_library/) | Through a remote client (`pydeephaven`) | Library only | Functions to import in Python code |
| 5 | [`my_dh_client/`](my_dh_client/) | Through a remote client (`pydeephaven`) | Command line tool only | A `my-dh-client-query` terminal command |

All five examples follow the [Python Packaging User Guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/) conventions:

- A `pyproject.toml` file declares the package's metadata, its dependencies, and any [entry points](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts). An entry point maps a terminal command name to a Python function, and `pip install` creates the command.
- The [src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/) puts the importable package in a `src/` directory instead of at the project root. Python then can't import the package straight from the project folder, so you always test the installed version.

This repository accompanies the [Package a Deephaven Python project](https://deephaven.io/core/docs/how-to-guides/sysadmin/setuptools-deployment/) guide, which explains the underlying concepts in depth.

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

## Choose an example

- **Example 1, `my_dh_library`**: reusable functions that other projects, or code running in a Deephaven server, import. No command line interface.
- **Example 2, `my_dh_cli`**: a tool that users run from a terminal. No importable library code.
- **Example 3, `my_dh_toolkit`**: both importable functions for Python users and commands for terminal users.
- **Example 4, `my_dh_client_library`** or **Example 5, `my_dh_client`**: connect to a server you already have running instead of starting one.

## Three ways to work with a Deephaven server

A packaged project uses Deephaven in one of three ways. The choice determines which Deephaven package it depends on.

- **Inside a running server.** The package is installed into a Deephaven server's own Python environment, such as a custom Docker image or the virtual environment of a pip-installed server, and imported from the server's console or scripts.
  - Depend on [`deephaven-core`](https://pypi.org/project/deephaven-core/), which provides the server-side `deephaven` API without a server of its own.
  - The server is already running, so code imports `deephaven` directly.
  - Example 1 uses this model.
- **Inside an embedded server.** The package starts a Deephaven server inside its own Python process.
  - Depend on [`deephaven-server`](https://pypi.org/project/deephaven-server/), which includes `deephaven-core`.
  - Every machine that runs it needs Java.
  - Examples 2 and 3 use this model. Example 1 can also run this way.

  The code must create a `deephaven_server.Server` before importing `deephaven`. See [Import order for the `deephaven` module](#import-order-for-the-deephaven-module).
- **Through a remote client.** The package connects to a server that is already running, possibly on another machine.
  - Depend on [`pydeephaven`](https://pypi.org/project/pydeephaven/), the Deephaven Python client. It does not start a server, does not need Java, and can be imported at any time.
  - It works with tables through a [`Session`](https://deephaven.io/core/client-api/python/code/pydeephaven.session.html#pydeephaven.session.Session). Its table API mirrors the server-side one closely but is not identical.
  - Examples 4 and 5 use this model.

The packaging tooling is the same in all three cases. What differs is the dependency and, for the server-side `deephaven` API, the import order.

### Import order for the `deephaven` module

`deephaven` modules can only be imported in a process where the Deephaven JVM is running. Inside a server, it always is. In a standalone Python process, creating a `deephaven_server.Server` starts the JVM, and `server.start()` is a separate step that starts the server itself. Importing `deephaven` (or a package that imports it) before creating the `Server` fails:

```text
>>> import deephaven
RuntimeError: The Deephaven Server has not been initialized. Please ensure that deephaven_server.Server has been constructed before importing deephaven.
```

This rule shapes how the examples are written:

- `my_dh_library` (Example 1) has no commands, so its `__init__.py` can re-export its functions. It is only imported inside a server or after the calling program has created a `Server`.
- `my_dh_cli` and `my_dh_toolkit` (Examples 2 and 3) import `deephaven` inside a function that runs after `main()` has created the `Server`, not at the top of the module.
- `my_dh_toolkit` (Example 3) keeps [`__init__.py`](my_dh_toolkit/src/my_dh_toolkit/__init__.py) free of imports. When a command starts, Python imports its package, including `__init__.py`, before `main()` runs, so re-exporting the query functions there would make every toolkit command fail at startup with the error above. Python users import the toolkit's functions from its submodules instead, such as `my_dh_toolkit.queries`.

`pydeephaven` has no such rule.

## Prerequisites

- **Python 3.9 or later**, and pip. A virtual environment is recommended, as shown in the [Quick start](#quick-start).
- **Java 17 or later** with `JAVA_HOME` set, required by `deephaven-server` in Examples 1 to 3. `pip` does not install Java. Not needed for Examples 4 and 5.
- **A running Deephaven server** to connect to, required by Examples 4 and 5. See [Start a server for Examples 4 and 5](#start-a-server-for-examples-4-and-5). Not needed for Examples 1 to 3.
- **Deephaven 0.35.0 or later**, declared in each example's `pyproject.toml` and installed automatically. For current versions and changes, see the [Deephaven release notes](https://github.com/deephaven/deephaven-core/releases).

The embedded servers in Examples 1 to 3 listen on port 10001 rather than Deephaven's usual 10000. That way they don't collide with the server on port 10000 that Examples 4 and 5 connect to.

## Sample data

The examples read the CSV files in the `data/` directory:

- `data/sample.csv`: a single 10-row file with `Name`, `Score`, `Value`, and `Category` columns. It is the input for the single-file examples: the library snippets, `my-dh-cli-query`, `my-dh-toolkit-query`, and `my-dh-client-query`.
- `data/batch/`: three smaller files (`file1.csv`, `file2.csv`, and `file3.csv`) with the same columns but different rows. It is the input for `my-dh-toolkit-process`, which processes every CSV file in a directory.

## Start a server for Examples 4 and 5

Examples 4 and 5 use `pydeephaven` and need a Deephaven server to connect to. Their defaults assume a server on `localhost:10000` that accepts anonymous connections. Either of these starts one:

```bash
# With Docker:
docker run --rm -p 10000:10000 \
  -e START_OPTS="-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler" \
  ghcr.io/deephaven/server:latest

# With pip-installed deephaven-server (also installed by Examples 2 and 3):
deephaven server --port 10000 --no-browser \
  --jvm-args "-DAuthHandlers=io.deephaven.auth.AnonymousAuthenticationHandler"
```

Leave the server running in that terminal and run Examples 4 and 5 from another one. The server's web IDE is at `http://localhost:10000`; the tables the examples bind appear there. Where possible, keep `pydeephaven` on the same version as the server it connects to.

A Deephaven server started without the `AuthHandlers` setting uses a [pre-shared key](https://deephaven.io/core/docs/how-to-guides/authentication/auth-psk/) instead, which it prints at startup. To connect to such a server, pass `auth_type="io.deephaven.authentication.psk.PskAuthenticationHandler"` and `auth_token="<key>"` to `Session`, or for `my-dh-client-query`, pass `--auth-type` and set `DH_AUTH_TOKEN`. The [`my_dh_client` README](my_dh_client/README.md#authentication) has examples for pre-shared key and username/password authentication.

## Example 1: `my_dh_library`, a library for use inside a server

This example packages reusable Deephaven query functions so that other projects can `pip install` the package and import the functions. It depends on `deephaven-core`, not `deephaven-server`, so installing it does not bring a server of its own.

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

The library also works from a standalone Python process that creates its own `Server` first. See the [`my_dh_library` README](my_dh_library/README.md) for that usage, the directory layout, and what to study in the code.

## Example 2: `my_dh_cli`, an embedded-server command line tool

This example packages a Deephaven script as a terminal command. `pip install` creates a `my-dh-cli-query` command that users run without writing any Python. The command starts its own Deephaven server, so it does not need one already running. It does need Java.

```bash
pip install -e ./my_dh_cli
my-dh-cli-query data/sample.csv --verbose
```

The command reads the CSV file, adds a computed `DoubleScore` column, and prints the first five rows. See the [`my_dh_cli` README](my_dh_cli/README.md) for the directory layout, `pyproject.toml` entry point, and what to study in the code.

## Example 3: `my_dh_toolkit`, an embedded-server library and command line tools in one package

In this example, one package provides both interfaces. Python users import its query functions, just as in `my_dh_library`; terminal users run its installed commands, just as in `my_dh_cli`. The commands call the package's own library functions, so there is one implementation behind both interfaces.

```bash
pip install -e ./my_dh_toolkit
my-dh-toolkit-query data/sample.csv --verbose
my-dh-toolkit-process data/batch --output output --verbose
```

`my-dh-toolkit-query` processes one CSV file. `my-dh-toolkit-process` processes every CSV in a directory. Import the library from its submodules (`my_dh_toolkit.queries`, `my_dh_toolkit.utils`), not from `my_dh_toolkit` itself — see [Import order](#import-order-for-the-deephaven-module) for why. See the [`my_dh_toolkit` README](my_dh_toolkit/README.md) for the directory layout, library usage, and what to study in the code.

## Example 4: `my_dh_client_library`, a client library

This example packages the same reusable query functions as `my_dh_library`, written for `pydeephaven` so that they run against a server the calling program is already connected to. It does not need Java and does not start a server.

With a [server running](#start-a-server-for-examples-4-and-5):

```bash
pip install -e ./my_dh_client_library
python
```

```python
from pydeephaven import Session
from my_dh_client_library import upload_csv, filter_by_threshold, publish

with Session(host="localhost", port=10000) as session:
    data = upload_csv(session, "data/sample.csv")
    filtered = filter_by_threshold(data, "Score", 75.0)
    publish(session, "filtered", filtered)
    print(f"{filtered.size} of {data.size} rows have Score > 75")
```

See the [`my_dh_client_library` README](my_dh_client_library/README.md) for the directory layout, available functions, and what to study in the code.

## Example 5: `my_dh_client`, a client command line tool

This example packages a `pydeephaven` program as a terminal command. `pip install` creates a `my-dh-client-query` command that uploads a CSV file to a running server, processes it there, and binds the result under a name. Like Example 4, it does not need Java.

With a [server running](#start-a-server-for-examples-4-and-5):

```bash
pip install -e ./my_dh_client
my-dh-client-query data/sample.csv --verbose
```

The command connects to `localhost:10000`, uploads the file, adds a computed `DoubleScore` column on the server, and binds the result as a table named `sample`. Pass `--auth-type` plus the `DH_AUTH_TOKEN` environment variable for a server that requires a token ([examples](my_dh_client/README.md#authentication)). See the [`my_dh_client` README](my_dh_client/README.md) for full command options, authentication details, and what to study in the code.

## Adapt an example for your own project

Each example is a template. To turn one into your own package:

1. **Copy an example.** Choose the one that matches your scenario:

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

4. **Update internal imports.** Change them to the new package name (for example, `from my_tool.cli import main` in `__main__.py`).

5. **Replace the example logic.** Add your own code, and add any packages it needs to `dependencies` in `pyproject.toml`. Keep the Deephaven dependency in the list so it installs automatically: `deephaven-core` for code that runs inside a server, `deephaven-server` for code that starts an embedded server, or `pydeephaven` for a client.

6. **Reinstall and test.** Install the package again and run its command:

   ```bash
   pip install -e .
   my-tool --help
   ```

Three names must stay in sync: the package directory under `src/`, the module paths in `[project.scripts]`, and the package name in `import` statements.

## Install and distribute

The examples above use editable installs (`pip install -e ./my_dh_cli`), which pick up source edits without reinstalling. This is ideal while developing. The other common options:

- **Install from source:** `pip install ./my_dh_cli`
- **Build and install a wheel:** use this format to distribute a package to other machines or publish it to a package index:

  ```bash
  pip install build
  python -m build my_dh_cli
  pip install my_dh_cli/dist/my_dh_cli-0.1.0-py3-none-any.whl
  ```

  Wheels can be shared directly or published to PyPI with [`twine`](https://twine.readthedocs.io/).

## Troubleshooting

- **Command not found after installation:** the install failed, or the Python scripts directory is not on `PATH`. Check the install with `pip show my_dh_cli`, and install inside an activated virtual environment to avoid most `PATH` issues.
- **`Address already in use` when an embedded-server command or snippet starts:** another process is using the port, which is 10001 by default for Examples 1 to 3. This also happens if the server started for Examples 4 and 5 is still running on port 10000 and an embedded-server command tries to use the same port. Pass a free port to the commands with `--port`, or change the `port` value in the `Server(...)` call in the library snippets.
- **`The Deephaven Server has not been initialized`:** a `deephaven` module, or a package that imports one, was imported before a `deephaven_server.Server` was created. Create the `Server` first, as described in [Import order for the `deephaven` module](#import-order-for-the-deephaven-module). Creating it also requires Java 17 or later through `JAVA_HOME`.
- **`No module named 'deephaven_server'` when running Example 1 standalone:** `my_dh_library` depends only on `deephaven-core`. Install `deephaven-server` as well to create a `Server` in your own process.
- **`failed to get the configuration constants` from a client example:** `pydeephaven` could not complete its first request to the server. Either no server is listening at the given host and port, or the server requires authentication the client did not provide. Check that the server is running and, if it uses a pre-shared key, pass the key as described in [Start a server for Examples 4 and 5](#start-a-server-for-examples-4-and-5).
- **Module not found after renaming:** the new package name is not used everywhere. Check that the directory under `src/`, the `[project.scripts]` module paths, and the `import` statements all use the new package name, then reinstall with `pip install -e .`.

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
