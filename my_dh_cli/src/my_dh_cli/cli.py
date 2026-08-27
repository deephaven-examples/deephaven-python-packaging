import click


def my_dh_query(input_file: str, verbose: bool = False):
    """Read a CSV file and perform a simple query operation on the data."""
    from deephaven import read_csv
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
    
    column_names = [col.name for col in source.columns]
    if "Score" not in column_names:
        raise click.ClickException(
            f"File '{input_path.name}' is missing required column 'Score'. "
            f"Available columns: {', '.join(column_names)}"
        )

    result = source.update(formulas=["DoubleScore = Score * 2"])

    if verbose:
        click.echo(f"Processed {result.size} rows")

    return result


@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def app(input_file: str, verbose: bool) -> None:
    """Process data with Deephaven."""
    result = my_dh_query(input_file, verbose)
    click.echo("Processing complete!")


if __name__ == "__main__":
    app()
