import click
from pathlib import Path


def batch_process(directory: str, output_dir: str, verbose: bool = False) -> None:
    """Process multiple CSV files from a directory."""
    from deephaven import read_csv
    
    input_path = Path(directory)
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    csv_files = list(input_path.glob("*.csv"))

    if verbose:
        click.echo(f"Found {len(csv_files)} CSV files to process")

    for csv_file in csv_files:
        if verbose:
            click.echo(f"Processing {csv_file.name}...")

        table = read_csv(str(csv_file))
        processed = table.update(formulas=["ProcessedScore = Score * 2"])

        if verbose:
            click.echo(f"  Processed {processed.size} rows")


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
