import polars as pl


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
