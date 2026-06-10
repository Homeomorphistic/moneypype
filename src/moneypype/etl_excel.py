import polars as pl

from moneypype.etl import validate_output, load
from moneypype.schemas import (
    TRANSACTIONS_SCHEMA,
    RAW_EXCEL_TRANSACTIONS_SCHEMA,
)


def run(
    input_path: str, output_path: str, categories_map_path: str
) -> pl.DataFrame:
    return (
        _extract(input_path, categories_map_path)
        .pipe(_validate_input)
        .pipe(_transform)
        .pipe(validate_output)
        .pipe(load, output_path)
    )


def _load_category_map(path: str) -> dict[str, str]:
    df = pl.read_csv(path)
    # Exclude "Inne" — it's the app's non-renameable default category;
    # it gets the sheet's default_type and is renamed to "Other".
    return {
        row["Category"]: row["Type"]
        for row in df.filter(pl.col("Category") != "Inne")
        .iter_rows(named=True)
    }


def _read_sheet(path: str, sheet_name: str) -> pl.DataFrame:
    # header_row=1: row 0 is the sheet title, row 1 contains column names.
    return pl.read_excel(
        path,
        sheet_name=sheet_name,
        engine="calamine",
        read_options={"header_row": 1},
    )


def _transform_income_expense(
    df: pl.DataFrame,
    category_map: dict[str, str],
    default_type: str,
) -> pl.DataFrame:
    negate = default_type != "Income"
    # Explicit Float64 cast: fastexcel infers whole-number cells as Int64,
    # which would break concat across sheets.
    amount_expr = (
        -pl.col("Kwota w walucie domyślnej").cast(pl.Float64)
        if negate
        else pl.col("Kwota w walucie domyślnej").cast(pl.Float64)
    )
    ref_amount_expr = (
        -pl.col("Kwota w walucie konta").cast(pl.Float64)
        if negate
        else pl.col("Kwota w walucie konta").cast(pl.Float64)
    )

    map_df = pl.DataFrame({
        "Kategoria": list(category_map.keys()),
        "type": list(category_map.values()),
    })

    return (
        df
        .join(map_df, on="Kategoria", how="left")
        .with_columns(pl.col("type").fill_null(default_type))
        .select([
            pl.col("Data i godzina").cast(pl.Date).alias("date"),
            pl.col("Konto").alias("account"),
            pl.col("Kategoria").replace({"Inne": "Other"}).alias("category"),
            pl.col("type"),
            pl.col("Komentarz").alias("note"),
            pl.col("Waluta konta").alias("currency"),
            amount_expr.alias("amount"),
            ref_amount_expr.alias("ref_currency_amount"),
            pl.col("Etykietki").alias("label"),
        ])
    )


def _transform_transfers(df: pl.DataFrame) -> pl.DataFrame:
    # Each transfer becomes two rows: one debiting the source account,
    # one crediting the destination. The app export omits the to-amount
    # in account currency, so ref_currency_amount on the to-row is null.
    from_df = df.select([
        pl.col("Data i godzina").cast(pl.Date).alias("date"),
        pl.col("Wychodzące").alias("account"),
        pl.lit("Transfer").alias("category"),
        pl.lit("Transfer").alias("type"),
        pl.col("Komentarz").alias("note"),
        pl.col("Waluta wychodząca").alias("currency"),
        (-pl.col("Kwota w walucie wychodzącej"))
        .cast(pl.Float64).alias("amount"),
        (-pl.col("Kwota w walucie wychodzącej"))
        .cast(pl.Float64).alias("ref_currency_amount"),
        pl.lit(None).cast(pl.String).alias("label"),
    ])

    to_df = df.select([
        pl.col("Data i godzina").cast(pl.Date).alias("date"),
        pl.col("Przychodzące").alias("account"),
        pl.lit("Transfer").alias("category"),
        pl.lit("Transfer").alias("type"),
        pl.col("Komentarz").alias("note"),
        pl.col("Waluta wychodząca").alias("currency"),
        pl.col("Kwota w walucie wychodzącej").cast(pl.Float64).alias("amount"),
        pl.lit(None).cast(pl.Float64).alias("ref_currency_amount"),
        pl.lit(None).cast(pl.String).alias("label"),
    ])

    return pl.concat([from_df, to_df])


def _extract(filepath: str, categories_map_path: str) -> pl.DataFrame:
    category_map = _load_category_map(categories_map_path)

    income = _read_sheet(filepath, "Dochody")
    expenses = _read_sheet(filepath, "Wydatki")
    transfers = _read_sheet(filepath, "Przelewy")

    return pl.concat([
        _transform_income_expense(income, category_map, "Income"),
        _transform_income_expense(expenses, category_map, "Wants"),
        _transform_transfers(transfers),
    ]).sort("date")


def _validate_input(data: pl.DataFrame) -> pl.DataFrame:
    RAW_EXCEL_TRANSACTIONS_SCHEMA.validate(data)
    return data


def _transform(data: pl.DataFrame) -> pl.DataFrame:
    return (
        data.with_columns(
            (pl.col("amount") * 100).cast(pl.Int32),
            (pl.col("ref_currency_amount") * 100).cast(pl.Int32),
        )
        .rename({"ref_currency_amount": "amount_fx_ccy"})
        .select(TRANSACTIONS_SCHEMA.keys())
    )
