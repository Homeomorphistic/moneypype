import polars as pl

from moneypype.etl import validate_output, load, scale_and_finalise
from moneypype.schemas import RAW_TRANSACTIONS_SCHEMA


def run(input_path: str, output_path: str) -> pl.DataFrame:
    return (
        _extract(input_path)
        .pipe(_validate_input)
        .pipe(_transform)
        .pipe(validate_output)
        .pipe(load, output_path)
    )


def _extract(filepath: str) -> pl.DataFrame:
    return pl.read_csv(filepath, decimal_comma=True, null_values="NA")


def _validate_input(data: pl.DataFrame) -> pl.DataFrame:
    RAW_TRANSACTIONS_SCHEMA.validate(data)
    return data


def _transform(data: pl.DataFrame) -> pl.DataFrame:
    return scale_and_finalise(
        data.with_columns(pl.col("date").cast(pl.Date))
    )
