import polars as pl

from moneypype.schemas import TRANSACTIONS_SCHEMA, VALID_TRANSACTIONS_SCHEMA


def validate_output(data: pl.DataFrame) -> pl.DataFrame:
    VALID_TRANSACTIONS_SCHEMA.validate(data)
    return data


def load(data: pl.DataFrame, output_path: str) -> pl.DataFrame:
    data.write_parquet(output_path)
    return data


def scale_and_finalise(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.with_columns(
            (pl.col("amount") * 100).cast(pl.Int32),
            (pl.col("ref_currency_amount") * 100).cast(pl.Int32),
        )
        .rename({"ref_currency_amount": "amount_fx_ccy"})
        .select(TRANSACTIONS_SCHEMA.keys())
    )
