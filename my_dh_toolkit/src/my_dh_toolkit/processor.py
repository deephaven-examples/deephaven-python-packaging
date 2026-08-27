import click
from pathlib import Path


def batch_process(directory: str, output_dir: str, verbose: bool = False) -> None:
    """Process multiple CSV files from a directory."""
    from deephaven import read_csv, write_csv
    
    input_path = Path(directory)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        raise click.ClickException(f"Input directory does not exist: '{input_path}'")
    if not input_path.is_dir():
        raise click.ClickException(f"Input path is not a directory: '{input_path}'")
    
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.ClickException(f"Permission denied: Cannot create output directory '{output_path}'")
    except OSError as e:
        raise click.ClickException(f"Failed to create output directory '{output_path}': {e}")

    csv_files = list(input_path.glob("*.csv"))

    if verbose:
        click.echo(f"Found {len(csv_files)} CSV files to process")

    for csv_file in csv_files:
        if verbose:
            click.echo(f"Processing {csv_file.name}...")

        table = read_csv(str(csv_file))
        
        column_names = [col.name for col in table.columns]
        if "Score" not in column_names:
            raise click.ClickException(
                f"File '{csv_file.name}' is missing required column 'Score'. "
                f"Available columns: {', '.join(column_names)}"
            )
        
        processed = table.update(formulas=["ProcessedScore = Score * 2"])
        
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
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def process(directory: str, output: str, verbose: bool) -> None:
    """Batch process CSV files with Deephaven."""
    batch_process(directory, output, verbose)
    click.echo("Batch processing complete!")


if __name__ == "__main__":
    process()
