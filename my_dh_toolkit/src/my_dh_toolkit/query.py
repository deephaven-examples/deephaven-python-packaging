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

    try:
        result = add_computed_columns(source)
    except Exception:
        raise click.ClickException(
            f"Failed to compute columns for '{input_path.name}'. "
            "The 'Value' column must be numeric."
        )

    if verbose:
        click.echo(f"Processed {result.size} rows")

    return result


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--port", default=10000, show_default=True, help="Port for the embedded Deephaven server")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def main(input_file: str, port: int, verbose: bool) -> None:
    """Process data with Deephaven."""
    try:
        from deephaven_server import Server

        server = Server(port=port, jvm_args=["-Xmx4g"])
        server.start()
    except Exception as e:
        raise click.ClickException(
            f"Failed to start Deephaven server on port {port}: {e}"
        )

    my_dh_query(input_file, verbose)
    click.echo("Processing complete!")


if __name__ == "__main__":
    main()
