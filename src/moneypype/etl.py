from importlib import resources

import polars as pl

from moneypype.schemas import TRANSACTIONS_SCHEMA


def extract(filepath: str) -> pl.DataFrame:
    return pl.read_csv(filepath, decimal_comma=True, null_values="NA")


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


def load(data: pl.DataFrame, dest: str) -> None:
    data.write_parquet(dest)


def run(source: str, dest: str) -> pl.DataFrame:
    data = extract(source)
    data = transform(data)
    load(data, dest)

    return data


if __name__ == "__main__":
    package_path = resources.files("moneypype")
    source = package_path.joinpath("data", "raw", "2026-03-03_budget.csv")
    dest = package_path.joinpath(
        "data", "staging", "2026-03-03_budget.parquet"
    )
    data = run(str(source), str(dest))
    print(data)
