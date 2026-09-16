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
