import argparse
from importlib import resources
from pathlib import Path

import polars as pl

import moneypype.etl_csv as etl


def main() -> None:
    parser = argparse.ArgumentParser(description="moneypype CLI")
    parser.add_argument("source")
    parser.add_argument(
        "dest",
        default=default_dest(),
        nargs="?",
    )

    args = parser.parse_args()

    data = run(args.source, args.dest)
    print(data)


def default_dest() -> str:
    return str(resources.files("moneypype").joinpath("data", "staging"))


def run(input_path: str, dest_dir: str) -> pl.DataFrame:
    if not Path(input_path).is_file():
        raise FileNotFoundError(f"Source file not found: {input_path}")

    filename = Path(input_path).name.replace(".csv", ".parquet")
    dest = Path(dest_dir).joinpath(filename)

    if dest.is_file():
        raise FileExistsError(f"Destination file already exists: {dest}")

    return etl.run(input_path, str(dest))
