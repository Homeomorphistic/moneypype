import polars as pl

from moneypype.schemas import (
    TRANSACTIONS_SCHEMA,
    RAW_TRANSACTIONS_SCHEMA,
    VALID_TRANSACTIONS_SCHEMA,
)


def run(input_path: str, output_path: str) -> pl.DataFrame:
    return (
        _extract(input_path)
        .pipe(_validate_input)
        .pipe(_transform)
        .pipe(_validate_output)
        .pipe(_load, output_path)
    )


def _extract(filepath: str) -> pl.DataFrame:
    return pl.read_csv(filepath, decimal_comma=True, null_values="NA")


def _validate_input(data: pl.DataFrame) -> pl.DataFrame:
    RAW_TRANSACTIONS_SCHEMA.validate(data)
    return data


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


def _validate_output(data: pl.DataFrame) -> pl.DataFrame:
    VALID_TRANSACTIONS_SCHEMA.validate(data)
    return data


def _load(data: pl.DataFrame, output_path: str) -> pl.DataFrame:
    data.write_parquet(output_path)
    return data
