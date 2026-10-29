import click


def run_query(input_file: str, verbose: bool = False):
    """Read a CSV file and add computed columns using the package's library functions."""
    # Imported here, not at module level: these modules import deephaven, which
    # can only be imported after a Server has been created, which starts the JVM.
    # The entry point creates and starts the server first, then calls this function.
    from deephaven import read_csv
    from my_dh_toolkit.queries import add_computed_columns
    from my_dh_toolkit.utils import validate_columns
    from pathlib import Path

    input_path = Path(input_file)

    if verbose:
        click.echo(f"Processing {input_file}...")

    try:
        source = read_csv(input_file)
    except Exception as e:
        raise click.ClickException(f"Failed to read CSV file '{input_file}': {e}") from e

    try:
        validate_columns(source, ["Value"], raise_error=True)
    except ValueError as e:
        raise click.ClickException(f"File '{input_path.name}': {e}")

    try:
        result = add_computed_columns(source)
    except Exception as e:
        raise click.ClickException(
            f"Failed to compute columns for '{input_path.name}': {e}"
        ) from e

    if verbose:
        click.echo(f"Processed {result.size} rows")

    return result


@click.command()
@click.argument("input_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--port", default=10001, show_default=True, help="Port for the embedded Deephaven server")
@click.option("--heap", default="4g", show_default=True, help="JVM maximum heap size (e.g. 2g, 512m)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output, listing the file being processed and the number of rows processed")
def main(input_file: str, port: int, heap: str, verbose: bool) -> None:
    """Process data with Deephaven."""
    try:
        from deephaven_server import Server

        server = Server(port=port, jvm_args=[f"-Xmx{heap}"])
        server.start()
    except Exception as e:
        raise click.ClickException(f"Failed to start Deephaven server: {e}") from e

    result = run_query(input_file, verbose)
    click.echo(result.to_string(num_rows=5))
    click.echo("Processing complete!")


if __name__ == "__main__":
    main()
