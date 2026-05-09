import polars as pl
from polars.testing import assert_schema_equal

from moneypype.etl import run
from moneypype.schemas import TRANSACTIONS_SCHEMA


def test_run(tmp_path):
    data = pl.DataFrame(
        {
            "date": ["2023-01-01"],
            "account": ["Account1"],
            "category": ["Category1"],
            "type": ["Type1"],
            "note": ["Note1"],
            "currency": ["USD"],
            "amount": [100.0],
            "ref_currency_amount": [100.0],
            "label": ["Label1"],
        }
    )

    source = tmp_path / "test.csv"
    dest = tmp_path / "test.parquet"

    data.write_csv(source, decimal_comma=True)
    run(source, dest)

    result = pl.read_parquet(dest)

    assert_schema_equal(result.schema, TRANSACTIONS_SCHEMA)
