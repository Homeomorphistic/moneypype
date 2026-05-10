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
        "note": pa.Column(pl.String, nullable=True),
        "currency": pa.Column(pl.String),
        "amount": pa.Column(pl.Float64),
        "ref_currency_amount": pa.Column(pl.Float64, nullable=True),
        "label": pa.Column(pl.String, nullable=True),
    }
)

VALID_TRANSACTIONS_SCHEMA = pa.DataFrameSchema(
    {
        "date": pa.Column(pl.Date),
        "account": pa.Column(pl.String),
        "type": pa.Column(pl.String),
        "category": pa.Column(pl.String),
        "note": pa.Column(pl.String, nullable=True),
        "label": pa.Column(pl.String, nullable=True),
        "amount": pa.Column(pl.Int32),
        "amount_fx_ccy": pa.Column(pl.Int32, nullable=True),
        "currency": pa.Column(pl.String),
    }
)
