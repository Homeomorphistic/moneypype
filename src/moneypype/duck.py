from importlib import resources

import duckdb
from pathlib import Path


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    path = resources.files("moneypype").joinpath("data", "moneypype.duckdb")
    return duckdb.connect(str(path))

if __name__ == "__main__":
    with get_duckdb_connection() as con:
        print(con.execute("SELECT * FROM transactions").pl())
