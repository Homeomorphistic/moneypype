from datetime import date

import pytest
import polars as pl
from polars.testing import assert_schema_equal
from pandera.errors import SchemaError

from moneypype.etl import scale_and_finalise
from moneypype.etl_csv import run, _extract, _validate_input
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


# --- _extract ---

def test_extract_parses_decimal_comma(csv_file):
    result = _extract(csv_file)
    assert result["amount"][0] == pytest.approx(36.96)


def test_extract_parses_negative_decimal_comma(csv_file):
    result = _extract(csv_file)
    assert result["amount"][1] == pytest.approx(-53.96)


def test_extract_reads_na_as_null(csv_file):
    result = _extract(csv_file)
    assert result["note"][2] is None


def test_extract_reads_label_na_as_null(csv_file):
    result = _extract(csv_file)
    assert result["label"][0] is None


# --- scale_and_finalise ---

def test_scale_and_finalise_converts_to_cents(data):
    data = data.with_columns(pl.col("date").cast(pl.Date))
    result = scale_and_finalise(data)
    assert result["amount"][0] == 10000


def test_scale_and_finalise_negative_amount():
    df = pl.DataFrame({
        "date": [date(2023, 1, 20)],
        "account": ["Alior"],
        "category": ["Groceries"],
        "type": ["Needs"],
        "note": ["Aldi"],
        "currency": ["PLN"],
        "amount": [-53.96],
        "ref_currency_amount": [-53.96],
        "label": [None],
    })
    result = scale_and_finalise(df)
    assert result["amount"][0] == -5396


def test_scale_and_finalise_renames_column(data):
    data = data.with_columns(pl.col("date").cast(pl.Date))
    result = scale_and_finalise(data)
    assert "amount_fx_ccy" in result.schema
    assert "ref_currency_amount" not in result.schema


def test_scale_and_finalise_null_fx_ccy():
    df = pl.DataFrame({
        "date": [date(2023, 1, 25)],
        "account": ["Alior"],
        "category": ["Hobby"],
        "type": ["Wants"],
        "note": [None],
        "currency": ["PLN"],
        "amount": [-198.0],
        "ref_currency_amount": [None],
        "label": [None],
    }).with_columns(pl.col("ref_currency_amount").cast(pl.Float64))
    result = scale_and_finalise(df)
    assert result["amount_fx_ccy"][0] is None


# --- _validate_input ---

@pytest.mark.parametrize("bad_col,bad_value", [
    ("amount", pl.lit("not_a_number").alias("amount")),
    ("account", pl.lit(None).cast(pl.String).alias("account")),
])
def test_input_validation_rejects_invalid(data, bad_col, bad_value):
    bad = data.with_columns(bad_value)
    with pytest.raises(SchemaError):
        _validate_input(bad)


# --- run (integration) ---

def test_run_schema(csv_file, tmp_path):
    dest = tmp_path / "out.parquet"
    run(csv_file, dest)
    result = pl.read_parquet(dest)
    assert_schema_equal(result.schema, TRANSACTIONS_SCHEMA)


def test_run_values(csv_file, tmp_path):
    dest = tmp_path / "out.parquet"
    run(csv_file, dest)
    result = pl.read_parquet(dest)

    assert result["date"][0] == date(2023, 1, 15)
    assert result["amount"][0] == 3696
    assert result["amount_fx_ccy"][0] == 3696
    assert result["amount"][1] == -5396
    assert result["amount_fx_ccy"][3] == 23456
    assert result["label"][3] == "VYM"
    assert result["label"][0] is None
    assert result["note"][2] is None


def test_run_null_fx_amount(csv_file, tmp_path):
    dest = tmp_path / "out.parquet"
    run(csv_file, dest)
    result = pl.read_parquet(dest)

    assert result["amount_fx_ccy"][2] == -19800
    assert result["amount_fx_ccy"][0] is not None
