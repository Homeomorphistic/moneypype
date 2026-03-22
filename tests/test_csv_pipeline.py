import pytest
from pathlib import Path

import polars as pl

from moneypype.etl import CsvTransactionsPipeline


@pytest.fixture
def pipeline(tmp_path):
    FIXTURES_DIR = Path(__file__).parent / "fixtures"
    source = FIXTURES_DIR / "2026-03-03_budget.csv"
    dest = tmp_path
    return CsvTransactionsPipeline(source=source, dest=dest)


def test_csv_extract(pipeline):
    pipeline.extract()
    staged = Path(pipeline.dest) / "staging" / "2026-03-03_budget.parquet"

    assert staged.exists()


def test_csv_transform(pipeline):
    pipeline.extract().transform()
    curated_file = Path(pipeline.dest) / "curated" / "2026-03-03_budget.parquet"

    assert curated_file.exists()

    curated = pl.read_parquet(curated_file)
