from pathlib import Path
from importlib import resources


def source_to_dest(source: str) -> str:
    package_path = resources.files("moneypype")

    filename = Path(source).name
    filename = filename.replace(".csv", ".parquet")
    return str(package_path.joinpath("data", "staging", filename))
