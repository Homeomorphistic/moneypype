import polars as pl

from moneypype.schemas import VALID_TRANSACTIONS_SCHEMA


def validate_output(data: pl.DataFrame) -> pl.DataFrame:
    VALID_TRANSACTIONS_SCHEMA.validate(data)
    return data


def load(data: pl.DataFrame, output_path: str) -> pl.DataFrame:
    data.write_parquet(output_path)
    return data
