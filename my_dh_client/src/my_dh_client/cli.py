import keyword
import os
import re
from pathlib import Path

import click
import pyarrow.csv as pacsv
# Unlike deephaven, pydeephaven can be imported at module level: there is no server
# to start first, so the import order does not matter.
from pydeephaven import DHError, Session, Table


def upload_and_query(session: Session, input_file: str, verbose: bool = False) -> Table:
    """Upload a CSV file to the server and perform a simple query operation on it."""
    input_path = Path(input_file)

    if verbose:
        click.echo(f"Uploading {input_file}...")

    try:
        # The server cannot see the client's files, so read the CSV locally with
        # pyarrow and send it to the server as an Arrow table.
        source = session.import_table(pacsv.read_csv(input_file))
    except Exception as e:
        raise click.ClickException(f"Failed to upload CSV file '{input_file}': {e}") from e

    column_names = source.schema.names
    if "Score" not in column_names:
        raise click.ClickException(
            f"File '{input_path.name}' is missing required column 'Score'. "
            f"Available columns: {', '.join(column_names)}"
        )

    # This runs on the server. Only a handle to the result comes back to the client.
    try:
        result = source.update(formulas=["DoubleScore = Score * 2"])
    except DHError as e:
        raise click.ClickException(
            f"Failed to compute DoubleScore for '{input_path.name}': {e}"
        ) from e

    if verbose:
        click.echo(f"Processed {result.size} rows")

    return result


@click.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--host", default="localhost", show_default=True, help="Deephaven server host")
@click.option("--port", default=10000, show_default=True, help="Deephaven server port")
@click.option(
    "--auth-type",
    default="Anonymous",
    show_default=True,
    help="Authentication type. Set DH_AUTH_TOKEN in the environment for types that need a token.",
)
@click.option("--name", default=None, help="Name to bind the result under on the server [default: file stem]")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output, listing the file being uploaded and the number of rows processed")
def main(input_file: str, host: str, port: int, auth_type: str, name: str, verbose: bool) -> None:
    """Upload a CSV file to a running Deephaven server and process it there."""
    if name is None:
        # Derive a valid identifier from the file stem: replace non-alphanumeric
        # characters with underscores, strip leading underscores and digits, and
        # fall back to "table" if nothing usable remains.
        stem = re.sub(r"[^A-Za-z0-9_]", "_", Path(input_file).stem).lstrip("_")
        stem = re.sub(r"^[0-9]+", "", stem)
        name = stem or "table"
    if not name.isidentifier() or keyword.iskeyword(name):
        raise click.BadParameter(
            f"'{name}' is not a valid table name (must be a Python identifier and not a keyword)",
            param_hint="--name",
        )

    try:
        session = Session(
            host=host,
            port=port,
            auth_type=auth_type,
            # Read the token from the environment, not an option, so it stays out of
            # shell history and process listings.
            auth_token=os.environ.get("DH_AUTH_TOKEN", ""),
        )
    except DHError as e:
        raise click.ClickException(
            f"Failed to connect to Deephaven server at {host}:{port} ({e}). "
            "Check that the server is running and that --auth-type matches its authentication."
        ) from e

    # Session is a context manager: the connection closes when the block exits.
    with session:
        result = upload_and_query(session, input_file, verbose)
        # Binding gives the table a name on the server, so it shows up in the IDE and
        # other clients can open it with session.open_table(name).
        try:
            session.bind_table(name, result)
        except DHError as e:
            raise click.ClickException(f"Failed to bind table '{name}' on {host}:{port}: {e}") from e

    click.echo(f"Bound result table '{name}' on {host}:{port}")


if __name__ == "__main__":
    main()
