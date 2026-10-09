import click
from pathlib import Path


def batch_process(directory: str, output_dir: str, verbose: bool = False) -> None:
    """Process multiple CSV files from a directory."""
    input_path = Path(directory)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise click.ClickException(f"Input directory does not exist: '{input_path}'")
    if not input_path.is_dir():
        raise click.ClickException(f"Input path is not a directory: '{input_path}'")
    if input_path.resolve() == output_path.resolve():
        raise click.ClickException(
            f"Input and output directories must be different: '{input_path}'"
        )

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.ClickException(f"Permission denied: Cannot create output directory '{output_path}'")
    except OSError as e:
        raise click.ClickException(f"Failed to create output directory '{output_path}': {e}")

    # Imported here, not at module level: these modules import deephaven, which
    # can only be imported after a Server has been created, which starts the JVM.
    # The entry point creates and starts the server first, then calls this function.
    from deephaven import read_csv, write_csv
    from my_dh_toolkit.queries import add_computed_columns
    from my_dh_toolkit.utils import validate_columns

    csv_files = [path for path in input_path.glob("*.csv") if path.is_file()]

    if verbose:
        click.echo(f"Found {len(csv_files)} CSV files to process")

    for csv_file in csv_files:
        if verbose:
            click.echo(f"Processing {csv_file.name}...")

        try:
            table = read_csv(str(csv_file))
        except Exception as e:
            raise click.ClickException(f"Failed to read CSV file '{csv_file}': {e}")

        try:
            validate_columns(table, ["Value"], raise_error=True)
        except ValueError as e:
            raise click.ClickException(f"File '{csv_file.name}': {e}")

        try:
            processed = add_computed_columns(table)
        except Exception:
            raise click.ClickException(
                f"Failed to compute columns for '{csv_file.name}'. "
                "The 'Value' column must be numeric."
            )

        output_file = output_path / f"processed_{csv_file.name}"
        try:
            write_csv(processed, str(output_file))
        except Exception as e:
            raise click.ClickException(f"Failed to write output file '{output_file}': {e}")

        if verbose:
            click.echo(f"  Processed {processed.size} rows -> {output_file.name}")


@click.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--output", "-o", default="./output", help="Output directory")
@click.option("--port", default=10000, show_default=True, help="Port for the embedded Deephaven server")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def main(directory: str, output: str, port: int, verbose: bool) -> None:
    """Batch process CSV files with Deephaven."""
    try:
        from deephaven_server import Server

        server = Server(port=port, jvm_args=["-Xmx4g"])
        server.start()
    except Exception as e:
        raise click.ClickException(
            f"Failed to start Deephaven server on port {port}: {e}"
        )

    batch_process(directory, output, verbose)
    click.echo("Batch processing complete!")


if __name__ == "__main__":
    main()
