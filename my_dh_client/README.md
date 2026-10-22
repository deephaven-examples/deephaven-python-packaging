# My Deephaven Client

An example of packaging a [`pydeephaven`](https://pypi.org/project/pydeephaven/) client program as a command line tool. Installing this package creates one terminal command, `my-dh-client-query`, which connects to a Deephaven server that is already running, uploads a CSV file to it, processes the data there, and binds the result under a name so it appears in the server's IDE.

Compare it with [`my_dh_cli`](../my_dh_cli/), which does similar work with an embedded server. The two differ in three ways:

- The dependency is `pydeephaven` rather than `deephaven-server`, so the client machine does not need Java. The command also starts faster than `my-dh-cli-query`, because it does not have to start a JVM and a server before it can work.
- The command does not start a server. It needs one to connect to, and many copies of the command can run against the same server at once.
- `pydeephaven` is imported at the top of `cli.py`. The embedded-server command has to delay its `deephaven` import until after it creates a `Server`; the client has no such constraint.

The command is defined by the `[project.scripts]` entry point in [`pyproject.toml`](pyproject.toml):

```toml
[project.scripts]
my-dh-client-query = "my_dh_client.cli:main"
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
> A Deephaven server must already be running. By default the command connects to `localhost:10000` with anonymous authentication. See [Start a server for the client examples](../README.md#start-a-server-for-the-client-examples) in the repository README for ways to start one, and [Authentication](#authentication) below to connect to a server that requires a key or password.

Run the installed command on a CSV file:

```bash
my-dh-client-query data/sample.csv --verbose
```

It reads the file locally with pyarrow, uploads it to the server, adds a `DoubleScore` computed column there, and binds the result as a table named `sample` (the file's stem):

```text
Uploading data/sample.csv...
Processed 10 rows
Bound result table 'sample' on localhost:10000
```

Open the server's IDE at `http://localhost:10000` to see the table, or pick a different name with `--name`.

To connect to a different server, pass `--host` and `--port`. The command's connection options are passed to a [`Session`](https://deephaven.io/core/client-api/python/code/pydeephaven.session.html#pydeephaven.session.Session), the `pydeephaven` connection object. Its reference lists every connection and authentication setting, which is useful if you add options of your own.

During development, the package also runs without an entry point via [`__main__.py`](src/my_dh_client/__main__.py):

```bash
python -m my_dh_client data/sample.csv --verbose
```

## Authentication

The command has to authenticate the way the server is configured to accept. `--auth-type` selects the method, and the `DH_AUTH_TOKEN` environment variable holds the secret, if the method needs one. The command reads the token from the environment rather than from an option, so it stays out of shell history and process listings.

| Server authentication | `--auth-type` | `DH_AUTH_TOKEN` |
|---|---|---|
| [Anonymous](https://deephaven.io/core/docs/how-to-guides/authentication/auth-anon/) | `Anonymous` (the default) | Not used |
| [Pre-shared key](https://deephaven.io/core/docs/how-to-guides/authentication/auth-psk/) | `io.deephaven.authentication.psk.PskAuthenticationHandler` | The key |
| [Username and password](https://deephaven.io/core/docs/how-to-guides/authentication/auth-uname-pw/) | `Basic` | `username:password` |

In each example below, `read -s` waits for you to type or paste the secret without showing it, and does not save it to shell history. Press Enter when done.

### Pre-shared key

A Deephaven server uses a pre-shared key unless it is configured otherwise. It generates a random key and prints it at startup, or you can set your own with `-Dauthentication.psk=<key>` in the server's JVM arguments (`START_OPTS` for Docker). Pass the key as the token:

```bash
read -s DH_AUTH_TOKEN && export DH_AUTH_TOKEN
my-dh-client-query data/sample.csv \
  --auth-type io.deephaven.authentication.psk.PskAuthenticationHandler
```

### Username and password

For a server that uses username and password authentication, pass `Basic` and enter the token as `username:password`:

```bash
read -s DH_AUTH_TOKEN && export DH_AUTH_TOKEN
my-dh-client-query data/sample.csv \
  --host dh.example.com \
  --auth-type Basic
```

### Other methods

Deephaven also supports [mTLS](https://deephaven.io/core/docs/how-to-guides/authentication/auth-mtls/) and [OpenID Connect with Keycloak](https://deephaven.io/core/docs/how-to-guides/authentication/auth-keycloak/). This command does not include the TLS and certificate options these need. To add them, pass the matching `Session` arguments, such as `use_tls`, `tls_root_certs`, `client_cert_chain`, and `client_private_key`, from new command options. See the [`Session` reference](https://deephaven.io/core/client-api/python/code/pydeephaven.session.html#pydeephaven.session.Session).

### If authentication fails

A wrong token, a missing `DH_AUTH_TOKEN`, and an `--auth-type` that doesn't match the server all produce the same error:

```text
Error: Failed to connect to Deephaven server at localhost:10000 (failed to get the configuration constants.). Check that the server is running and that --auth-type matches its authentication.
```

The server doesn't report which part was wrong. Check that `--auth-type` matches the server's configuration, that `DH_AUTH_TOKEN` is exported in the same shell (`echo ${DH_AUTH_TOKEN:+set}` prints `set` if it is), and that the token has the format shown in the table.

## Command reference

### my-dh-client-query

Upload a CSV file to a running Deephaven server and process it there. The file must contain a numeric `Score` column.

**Arguments:**

- `input_file` - Path to the CSV file to upload.

**Options:**

- `--host` - Deephaven server host. Default: `localhost`.
- `--port` - Deephaven server port. Default: `10000`.
- `--auth-type` - Authentication type. For types other than `Anonymous`, set the token in the `DH_AUTH_TOKEN` environment variable. See [Authentication](#authentication) for the values and token formats. Default: `Anonymous`.
- `--name` - Name to bind the result table under on the server. Must be a valid Python identifier, so a file such as `my-scores.csv` needs `--name`. Default: the input file's stem.
- `-v, --verbose` - Print progress messages: the file being uploaded and the number of rows processed.

## What to study

- [`cli.py`](src/my_dh_client/cli.py): the command checks that the table name (the file's stem, or `--name`) is a valid Python identifier before it connects. It takes connection options instead of a port to bind, and reads the authentication token from the environment. `Session` is used as a context manager, so the connection closes when the command exits.

## Requirements

- Python 3.9 or later
- pydeephaven (installed automatically as a dependency; see [`pyproject.toml`](pyproject.toml) for the minimum version)
- Click 8.0.0 or later (installed automatically as a dependency)
- A running Deephaven server to connect to. Java is not required on the client machine.
