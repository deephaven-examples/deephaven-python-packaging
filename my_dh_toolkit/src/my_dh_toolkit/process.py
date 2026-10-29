import click
from pathlib import Path


def batch_process(directory: str, output_dir: str, verbose: bool = False) -> None:
    """Process multiple CSV files from a directory."""
    input_path = Path(directory)
    output_path = Path(output_dir)

    if input_path.resolve() == output_path.resolve():
        raise click.ClickException(
            f"Input and output directories must be different: '{input_path}'"
        )

    # Imported here, not at module level: these modules import deephaven, which
    # can only be imported after a Server has been created, which starts the JVM.
    # The entry point creates and starts the server first, then calls this function.
    from deephaven import read_csv, write_csv
    from my_dh_toolkit.queries import add_computed_columns
    from my_dh_toolkit.utils import validate_columns

    csv_files = sorted(path for path in input_path.glob("*.csv") if path.is_file())

    if not csv_files:
        click.echo("No CSV files found")
        return

    if verbose:
        click.echo(f"Found {len(csv_files)} CSV files to process")

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.ClickException(f"Permission denied: Cannot create output directory '{output_path}'")
    except OSError as e:
        raise click.ClickException(f"Failed to create output directory '{output_path}': {e}") from e

    failures = []
    for csv_file in csv_files:
        if verbose:
            click.echo(f"Processing {csv_file.name}...")

        try:
            table = read_csv(str(csv_file))
            validate_columns(table, ["Value"], raise_error=True)
            processed = add_computed_columns(table)
            output_file = output_path / f"processed_{csv_file.name}"
            write_csv(processed, str(output_file))
        except Exception as e:
            failures.append((csv_file.name, str(e)))
            click.echo(f"  Failed: {e}", err=True)
            continue

        if verbose:
            click.echo(f"  Processed {processed.size} rows -> {output_file.name}")

    if failures:
        names = ", ".join(name for name, _ in failures)
        raise click.ClickException(f"Failed to process {len(failures)} file(s): {names}")


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--output", "-o", default="./output", show_default=True, help="Output directory")
@click.option("--port", default=10001, show_default=True, help="Port for the embedded Deephaven server")
@click.option("--heap", default="4g", show_default=True, help="JVM maximum heap size (e.g. 2g, 512m)")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output, listing the number of CSV files found and, for each file, its name, row count, and output file")
def main(directory: str, output: str, port: int, heap: str, verbose: bool) -> None:
    """Batch process CSV files with Deephaven."""
    try:
        from deephaven_server import Server

        server = Server(port=port, jvm_args=[f"-Xmx{heap}"])
        server.start()
    except Exception as e:
        raise click.ClickException(f"Failed to start Deephaven server: {e}") from e

    batch_process(directory, output, verbose)
    click.echo("Batch processing complete!")


if __name__ == "__main__":
    main()
