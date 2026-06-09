import polars as pl

from moneypype.schemas import VALID_TRANSACTIONS_SCHEMA


def _validate_output(data: pl.DataFrame) -> pl.DataFrame:
    VALID_TRANSACTIONS_SCHEMA.validate(data)
    return data


def _load(data: pl.DataFrame, output_path: str) -> pl.DataFrame:
    data.write_parquet(output_path)
    return data
