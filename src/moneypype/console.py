import argparse
from pathlib import Path

import polars as pl

import moneypype.etl as etl


def main() -> None:
    parser = argparse.ArgumentParser(description="moneypype CLI")
    parser.add_argument(
        "source",
        help="input file name",
        default=etl._default_source(),
        nargs="?",
    )
    parser.add_argument(
        "dest",
        help="output file name",
        default=None,
        nargs="?",
    )

    args = parser.parse_args()

    data = run(args.source, args.dest)
    print(data)


def run(source: str, dest: str) -> pl.DataFrame:
    if not Path(source).is_file():
        raise FileNotFoundError(f"Source file not found: {source}")

    filename = Path(source).name.replace(".csv", ".parquet")
    dest_ = Path(dest).joinpath(filename)

    if dest_.is_file():
        raise FileExistsError(f"Destination file already exists: {dest_}")

    return etl.run(source, str(dest_))
