from importlib import resources
from moneypype.etl import run


def main() -> None:
    package_path = resources.files("moneypype")
    source = package_path.joinpath("data", "raw", "2026-03-03_budget.csv")
    dest = package_path.joinpath(
        "data", "staging", "2026-03-03_budget.parquet"
    )
    data = run(str(source), str(dest))
    print(data)
