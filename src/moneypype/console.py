import argparse
from importlib import resources
from pathlib import Path

import polars as pl

import moneypype.etl_csv as etl_csv
import moneypype.etl_excel as etl_excel
import moneypype.etl_gdrive_excel as etl_gdrive_excel

_GDRIVE_PREFIX = "gdrive:"


def main() -> None:
    parser = argparse.ArgumentParser(description="moneypype CLI")
    parser.add_argument("source")
    parser.add_argument(
        "dest",
        default=default_dest(),
        nargs="?",
    )
    parser.add_argument(
        "--categories-map", default=default_map(), dest="categories_map"
    )

    args = parser.parse_args()

    data = run(args.source, args.dest, args.categories_map)
    print(data)


def default_dest() -> str:
    return str(resources.files("moneypype").joinpath("data", "staging"))


def default_map() -> str:
    return str(
        resources.files("moneypype").joinpath(
            "data", "raw", "categories_map.csv"
        )
    )


def run(
    input_path: str, dest_dir: str, categories_map_path: str | None = None
) -> pl.DataFrame:
    is_drive = str(input_path).startswith(_GDRIVE_PREFIX)

    if not is_drive and not Path(input_path).is_file():
        raise FileNotFoundError(f"Source file not found: {input_path}")

    if is_drive:
        file_id = str(input_path)[len(_GDRIVE_PREFIX):]
        filename = file_id + ".parquet"
    else:
        filename = Path(input_path).stem + ".parquet"

    dest = Path(dest_dir).joinpath(filename)

    if dest.is_file():
        raise FileExistsError(f"Destination file already exists: {dest}")

    if is_drive:
        if categories_map_path is None:
            raise ValueError(
                "--categories-map is required for Google Drive Excel input"
            )
        return etl_gdrive_excel.run(file_id, str(dest), categories_map_path)

    suffix = Path(input_path).suffix.lower()
    if suffix == ".csv":
        return etl_csv.run(input_path, str(dest))
    elif suffix == ".xlsx":
        if categories_map_path is None:
            raise ValueError("--categories-map is required for Excel input")
        return etl_excel.run(input_path, str(dest), categories_map_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")
