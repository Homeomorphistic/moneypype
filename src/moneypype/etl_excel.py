import polars as pl

from moneypype.etl import validate_output, load, scale_and_finalise
from moneypype.schemas import RAW_EXCEL_TRANSACTIONS_SCHEMA


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


def _load_category_map(path: str) -> pl.DataFrame:
    # Filter out "Inne" — the app's non-renameable default category.
    # It gets default_type and is renamed to "Other" in the caller.
    # Returning a DataFrame (not dict) preserves String column schema
    # even when the result is empty, preventing a Null-typed join key.
    return (
        pl.read_csv(path)
        .filter(pl.col("Category") != "Inne")
        .select([
            pl.col("Category").alias("Kategoria"),
            pl.col("Type").alias("type"),
        ])
    )


def _read_sheet(path: str, sheet_name: str) -> pl.DataFrame:
    # header_row=1: row 0 is the sheet title, row 1 contains column names.
    # schema_overrides: calamine may return Datetime for date-only cells.
    return pl.read_excel(
        path,
        sheet_name=sheet_name,
        engine="calamine",
        read_options={"header_row": 1},
        schema_overrides={"Data i godzina": pl.Date},
    )


def _transform_income_expense(
    df: pl.DataFrame,
    map_df: pl.DataFrame,
    default_type: str,
    negate: bool,
) -> pl.DataFrame:
    sign = pl.lit(-1.0) if negate else pl.lit(1.0)
    # Explicit Float64 cast: fastexcel infers whole-number cells as Int64,
    # which would break concat across sheets.
    return (
        df
        .join(map_df, on="Kategoria", how="left")
        .with_columns(pl.col("type").fill_null(default_type))
        .select([
            pl.col("Data i godzina").alias("date"),
            pl.col("Konto").alias("account"),
            pl.col("Kategoria").replace({"Inne": "Other"}).alias("category"),
            pl.col("type"),
            pl.col("Komentarz").alias("note"),
            pl.col("Waluta konta").alias("currency"),
            (sign * pl.col("Kwota w walucie domyślnej").cast(pl.Float64))
            .alias("amount"),
            (sign * pl.col("Kwota w walucie konta").cast(pl.Float64))
            .alias("ref_currency_amount"),
            pl.col("Etykietki").alias("label"),
        ])
    )


def _transform_transfers(df: pl.DataFrame) -> pl.DataFrame:
    # Each transfer becomes two rows: one debiting the source account,
    # one crediting the destination. The app export does not provide a
    # separate incoming-currency column, so currency on both legs records
    # the outgoing currency — correct for same-currency transfers, but
    # imprecise for cross-currency ones.
    from_df = df.select([
        pl.col("Data i godzina").alias("date"),
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
        pl.col("Data i godzina").alias("date"),
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
    map_df = _load_category_map(categories_map_path)

    income = _read_sheet(filepath, "Dochody")
    expenses = _read_sheet(filepath, "Wydatki")
    transfers = _read_sheet(filepath, "Przelewy")

    return pl.concat([
        _transform_income_expense(income, map_df, "Income", negate=False),
        _transform_income_expense(expenses, map_df, "Wants", negate=True),
        _transform_transfers(transfers),
    ]).sort("date")


def _validate_input(data: pl.DataFrame) -> pl.DataFrame:
    RAW_EXCEL_TRANSACTIONS_SCHEMA.validate(data)
    return data


def _transform(data: pl.DataFrame) -> pl.DataFrame:
    return scale_and_finalise(data)
