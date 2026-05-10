from importlib import resources
import moneypype.utils as utils


def test_source_to_dest():
    package_path = resources.files("moneypype")
    assert utils.source_to_dest("data/raw/2026-03-03_budget.csv") == str(
        package_path.joinpath("data", "staging", "2026-03-03_budget.parquet")
    )
    assert utils.source_to_dest("raw/2026-04-06_budget.csv") == str(
        package_path.joinpath("data", "staging", "2026-04-06_budget.parquet")
    )
