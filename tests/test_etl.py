import pytest

import polars as pl
from polars.testing import assert_schema_equal
from pandera.errors import SchemaError

from moneypype.etl import run, _validate_input
from moneypype.schemas import TRANSACTIONS_SCHEMA


@pytest.fixture
def data():
    return pl.DataFrame(
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


def test_input_validation(data):
    data = data.with_columns(
        pl.col("amount").cast(pl.String), pl.lit(None).alias("label")
    )

    with pytest.raises(SchemaError):
        _validate_input(data)


def test_run(tmp_path, data):

    source = tmp_path / "test.csv"
    dest = tmp_path / "test.parquet"

    data.write_csv(source, decimal_comma=True)
    run(source, dest)

    result = pl.read_parquet(dest)

    assert_schema_equal(result.schema, TRANSACTIONS_SCHEMA)
