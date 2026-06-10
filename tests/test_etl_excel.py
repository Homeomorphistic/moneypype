from datetime import date

import polars as pl
import pytest
from pandera.errors import SchemaError
from polars.testing import assert_schema_equal

from moneypype.etl_excel import run, _validate_input
from moneypype.schemas import TRANSACTIONS_SCHEMA


def test_run_schema(tmp_path, xlsx_file, categories_map_file):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    assert_schema_equal(result.schema, TRANSACTIONS_SCHEMA)


def test_run_transfer_expands_to_two_rows(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    transfers = result.filter(pl.col("type") == "Transfer")
    assert len(transfers) == 2


def test_run_expense_amount_is_negative(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    expense = result.filter(pl.col("category") == "Groceries")
    assert expense["amount"][0] < 0


def test_run_income_amount_is_positive(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    income = result.filter(pl.col("category") == "Salary")
    assert income["amount"][0] > 0


def test_run_amounts_in_cents(tmp_path, xlsx_file, categories_map_file):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    income = result.filter(pl.col("category") == "Salary")
    assert income["amount"][0] == 100000


def test_run_transfer_to_row_has_null_fx_amount(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    # to-row has positive amount; from-row has negative amount
    to_row = result.filter(
        (pl.col("type") == "Transfer") & (pl.col("amount") > 0)
    )
    assert to_row["amount_fx_ccy"][0] is None


def test_run_sorted_by_date(tmp_path, xlsx_file, categories_map_file):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    dates = result["date"].to_list()
    assert dates == sorted(dates)


def test_input_validation_raises():
    bad_data = pl.DataFrame({
        "date": pl.Series([date(2026, 1, 1)], dtype=pl.Date),
        "account": pl.Series(["Savings"], dtype=pl.String),
        "category": pl.Series(["Salary"], dtype=pl.String),
        "type": pl.Series(["Income"], dtype=pl.String),
        "note": pl.Series([None], dtype=pl.String),
        "currency": pl.Series(["PLN"], dtype=pl.String),
        "amount": pl.Series(["not_a_number"], dtype=pl.String),
        "ref_currency_amount": pl.Series([None], dtype=pl.Float64),
        "label": pl.Series([None], dtype=pl.String),
    })
    with pytest.raises(SchemaError):
        _validate_input(bad_data)
