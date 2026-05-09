from importlib import resources

import polars as pl

from moneypype.schemas import TRANSACTIONS_SCHEMA


def extract() -> pl.DataFrame:
    path = resources.files("moneypype").joinpath("data", "raw", "2026-03-03_budget.csv")

    return pl.read_csv(path, decimal_comma=True, null_values="NA")


def transform(data: pl.DataFrame) -> pl.DataFrame:
    data = (
        data.with_columns(
            pl.col("date").cast(pl.Date),
            (pl.col("amount") * 100).cast(pl.Int32),
            (pl.col("ref_currency_amount") * 100).cast(pl.Int32),
        )
        .rename({"ref_currency_amount": "amount_fx_ccy"})
        .select(TRANSACTIONS_SCHEMA.keys())
    )

    return data


def load(data: pl.DataFrame) -> None:
    pass


def run() -> None:
    data = extract()
    data = transform(data)
    load(data)
    return data
