from importlib import resources

import duckdb
import polars as pl

from moneypype.duck import get_duckdb_connection
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


def load(data: pl.DataFrame, con: duckdb.DuckDBPyConnection) -> None:
    con.sql("CREATE TABLE transactions AS SELECT * FROM data")


def run() -> None:
    with get_duckdb_connection() as con:
        data = extract()
        data = transform(data)
        load(data, con)

    return data

if __name__ == "__main__":
    run()