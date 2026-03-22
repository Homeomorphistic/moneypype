from importlib.resources import files
from pathlib import Path

import polars as pl

# df = df.rename({"ref_currency_amount": "amount_fx_ccy"})


class CsvTransactionsPipeline:
    def __init__(self, source: str, dest: str | None = None):
        self.source = source
        self.dest = dest if dest else files("moneypype.data")

    def _save_parquet(self, subdir: str):
        dir_path = Path(self.dest) / subdir
        dir_path.mkdir(parents=True, exist_ok=True)
        filename = Path(self.source).stem + ".parquet"
        self.df.write_parquet(dir_path / filename)

    def extract(self):
        self.df = pl.read_csv(self.source, decimal_comma=True, null_values="NA")
        self._save_parquet("staging")
        return self

    def transform(self):
        self._save_parquet("curated")
        return self
