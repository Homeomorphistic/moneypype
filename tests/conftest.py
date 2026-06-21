from datetime import date
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"

@pytest.fixture
def csv_file():
    return Path(__file__).parent / "fixtures" / "sample.csv"


@pytest.fixture
def categories_map_file():
    return str(FIXTURES_DIR / "categories_map.csv")


@pytest.fixture
def xlsx_file():
    return str(FIXTURES_DIR / "transactions.xlsx")
