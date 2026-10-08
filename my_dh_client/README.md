# My Deephaven Client

An example of packaging a [`pydeephaven`](https://pypi.org/project/pydeephaven/) client program as a command line tool. Installing this package creates one terminal command, `my-dh-client`, which connects to a Deephaven server that is already running, uploads a CSV file to it, processes the data there, and binds the result under a name so it appears in the server's IDE.

Compare it with [`my_dh_cli`](../my_dh_cli/), which does similar work with an embedded server. The two differ in three ways:

- The dependency is `pydeephaven` rather than `deephaven-server`, so installing it does not pull in a JVM and the command starts quickly.
- The command does not start a server. It needs one to connect to, and many copies of the command can run against the same server at once.
- `pydeephaven` is imported at the top of `cli.py`. The embedded-server command has to delay its `deephaven` import until after the server starts; the client has no such constraint.

The command is defined by the `[project.scripts]` entry point in [`pyproject.toml`](pyproject.toml):

```toml
[project.scripts]
my-dh-client = "my_dh_client.cli:main"
```

## Installation

From the repository root:

```bash
pip install ./my_dh_client
```

Or in editable mode for development:

```bash
pip install -e ./my_dh_client
```

## Usage

> [!NOTE]
> A Deephaven server must already be running. By default the command connects to `localhost:10000` with anonymous authentication. See [Start a server for the client examples](../README.md#start-a-server-for-the-client-examples) in the repository README for ways to start one, and for connecting to a server that uses a pre-shared key.

Run the installed command on a CSV file:

```bash
my-dh-client data/sample.csv --verbose
```

It reads the file locally with pyarrow, uploads it to the server, adds a `DoubleScore` computed column there, and binds the result as a table named `sample` (the file's stem). Open the server's IDE at `http://localhost:10000` to see the table, or pick a different name with `--name`.

To connect to a different server, pass `--host` and `--port`. For a server that requires a token, pass `--auth-type` and put the token in the `DH_AUTH_TOKEN` environment variable. Set the variable without typing the token into a command, so it stays out of your shell history; for example, enter it at a hidden prompt with `read -s`:

```bash
read -s DH_AUTH_TOKEN && export DH_AUTH_TOKEN
my-dh-client data/sample.csv \
  --host dh.example.com \
  --auth-type io.deephaven.authentication.psk.PskAuthenticationHandler
```

During development, the package also runs without an entry point via [`__main__.py`](src/my_dh_client/__main__.py):

```bash
python -m my_dh_client data/sample.csv --verbose
```

## Command reference

### my-dh-client

Upload a CSV file to a running Deephaven server and process it there. The file must contain a numeric `Score` column.

**Arguments:**

- `input_file` - Path to the CSV file to upload.

**Options:**

- `--host` - Deephaven server host. Default: `localhost`.
- `--port` - Deephaven server port. Default: `10000`.
- `--auth-type` - Authentication type. Default: `Anonymous`. For other types, set the token in the `DH_AUTH_TOKEN` environment variable.
- `--name` - Name to bind the result table under on the server. Default: the input file's stem.
- `--verbose, -v` - Enable verbose output.

## Requirements

- Python 3.9 or later
- pydeephaven 0.35.0 or later (installed automatically as a dependency)
- Click 8.0.0 or later (installed automatically as a dependency)
- A running Deephaven server to connect to. Java is not required on the client machine.
