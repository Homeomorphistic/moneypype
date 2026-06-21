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
    income = result.filter(
        (pl.col("category") == "Salary") & (pl.col("amount") == 100000)
    )
    assert len(income) == 1
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


def test_inne_income_category_renamed_to_other(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    inne_row = result.filter(
        (pl.col("type") == "Income") & (pl.col("category") == "Other")
    )
    assert len(inne_row) == 1
    assert inne_row["category"][0] == "Other"


def test_inne_expense_category_renamed_to_other(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    inne_row = result.filter(
        (pl.col("type") == "Wants") & (pl.col("category") == "Other")
    )
    assert len(inne_row) == 1
    assert inne_row["category"][0] == "Other"


def test_run_non_null_label_is_preserved(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    row = result.filter(pl.col("label") == "bonus")
    assert len(row) == 1
    assert row["label"][0] == "bonus"


def test_run_null_note_in_expense_is_valid(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    expense = result.filter(pl.col("category") == "Groceries")
    assert expense["note"][0] is None


def test_run_expense_amount_fx_ccy_is_negative(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    expense = result.filter(pl.col("category") == "Groceries")
    assert expense["amount_fx_ccy"][0] is not None
    assert expense["amount_fx_ccy"][0] < 0


def test_run_income_amount_fx_ccy_is_positive_and_scaled(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    income = result.filter(
        (pl.col("category") == "Salary") & (pl.col("amount") == 100000)
    )
    assert income["amount_fx_ccy"][0] is not None
    assert income["amount_fx_ccy"][0] == 100000


def test_run_transfer_from_leg_account_is_source(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    from_leg = result.filter(
        (pl.col("type") == "Transfer") & (pl.col("amount") < 0)
    )
    assert from_leg["account"][0] == "Main Account"


def test_run_transfer_to_leg_account_is_destination(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    to_leg = result.filter(
        (pl.col("type") == "Transfer") & (pl.col("amount") > 0)
    )
    assert to_leg["account"][0] == "Savings"


def test_run_transfer_from_leg_amount_fx_ccy_is_negative(
    tmp_path, xlsx_file, categories_map_file
):
    dest = str(tmp_path / "out.parquet")
    result = run(xlsx_file, dest, categories_map_file)
    from_leg = result.filter(
        (pl.col("type") == "Transfer") & (pl.col("amount") < 0)
    )
    assert from_leg["amount_fx_ccy"][0] is not None
    assert from_leg["amount_fx_ccy"][0] == -20000
