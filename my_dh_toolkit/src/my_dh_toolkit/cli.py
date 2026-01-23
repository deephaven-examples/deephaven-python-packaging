import click


def my_dh_query(input_file: str, verbose: bool = False):
    """Read a CSV file and perform a simple query operation on the data."""
    from deephaven import read_csv

    if verbose:
        click.echo(f"Processing {input_file}...")

    source = read_csv(input_file)

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
