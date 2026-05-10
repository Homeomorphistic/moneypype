import pytest

import moneypype.console as cli


def test_run_raises_not_existing_source(tmp_path):
    with pytest.raises(FileNotFoundError):
        cli.run(tmp_path / "non_existing_file.csv", "")


def test_run_raises_existing_dest(tmp_path):
    source = tmp_path / "input.csv"
    dest = tmp_path

    source.touch()
    (tmp_path / "input.parquet").touch()

    with pytest.raises(FileExistsError):
        cli.run(source, dest)
