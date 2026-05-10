import polars as pl
import pandera.polars as pa

TRANSACTIONS_SCHEMA = pl.Schema(
    {
        "date": pl.Date,
        "account": pl.String,
        "type": pl.String,
        "category": pl.String,
        "note": pl.String,
        "label": pl.String,
        "amount": pl.Int32,
        "amount_fx_ccy": pl.Int32,
        "currency": pl.String,
    }
)

RAW_TRANSACTIONS_SCHEMA = pa.DataFrameSchema(
    {
        "date": pa.Column(pl.String),
        "account": pa.Column(pl.String),
        "category": pa.Column(pl.String),
        "type": pa.Column(pl.String),
        "note": pa.Column(pl.String),
        "currency": pa.Column(pl.String),
        "amount": pa.Column(pl.Float64),
        "ref_currency_amount": pa.Column(pl.Float64),
        "label": pa.Column(pl.String),
    }
)

VALID_TRANSACTIONS_SCHEMA = pa.DataFrameSchema(
    {
        "date": pa.Column(pl.Date),
        "account": pa.Column(pl.String),
        "type": pa.Column(pl.String),
        "category": pa.Column(pl.String),
        "note": pa.Column(pl.String),
        "label": pa.Column(pl.String),
        "amount": pa.Column(pl.Int32),
        "amount_fx_ccy": pa.Column(pl.Int32),
        "currency": pa.Column(pl.String),
    }
)
