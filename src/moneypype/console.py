import argparse
from importlib import resources
from pathlib import Path

import polars as pl

import moneypype.etl_csv as etl_csv
import moneypype.etl_excel as etl_excel


def main() -> None:
    parser = argparse.ArgumentParser(description="moneypype CLI")
    parser.add_argument("source")
    parser.add_argument(
        "dest",
        default=default_dest(),
        nargs="?",
    )
    parser.add_argument(
        "--categories-map", default=None, dest="categories_map"
    )

    args = parser.parse_args()

    data = run(args.source, args.dest, args.categories_map)
    print(data)


def default_dest() -> str:
    return str(resources.files("moneypype").joinpath("data", "staging"))


def run(
    input_path: str, dest_dir: str, categories_map_path: str | None = None
) -> pl.DataFrame:
    if not Path(input_path).is_file():
        raise FileNotFoundError(f"Source file not found: {input_path}")

    filename = Path(input_path).stem + ".parquet"
    dest = Path(dest_dir).joinpath(filename)

    if dest.is_file():
        raise FileExistsError(f"Destination file already exists: {dest}")

    suffix = Path(input_path).suffix.lower()
    if suffix == ".csv":
        return etl_csv.run(input_path, str(dest))
    elif suffix == ".xlsx":
        if categories_map_path is None:
            raise ValueError("--categories-map is required for Excel input")
        return etl_excel.run(input_path, str(dest), categories_map_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
