from importlib import resources
from typing import Optional

import polars as pl

from moneypype.schemas import TRANSACTIONS_SCHEMA


def run(
    source: Optional[str] = None, dest: Optional[str] = None
) -> pl.DataFrame:
    source = source or _default_source()
    dest = dest or _default_dest()

    return _extract(source).pipe(_transform).pipe(_load, dest)


def _default_source() -> str:
    return str(
        resources.files("moneypype").joinpath(
            "data", "raw", "2026-03-03_budget.csv"
        )
    )


def _default_dest() -> str:
    return str(
        resources.files("moneypype").joinpath(
            "data", "staging", "2026-03-03_budget.parquet"
        )
    )


def _extract(filepath: str) -> pl.DataFrame:
    return pl.read_csv(filepath, decimal_comma=True, null_values="NA")


def _transform(data: pl.DataFrame) -> pl.DataFrame:
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


def _load(data: pl.DataFrame, dest: str) -> pl.DataFrame:
    data.write_parquet(dest)
    return data


if __name__ == "__main__":
    data = run()
    print(data)
