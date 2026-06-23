from pathlib import Path
from unittest.mock import patch

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


def test_run_raises_missing_categories_map_for_xlsx(tmp_path):
    source = tmp_path / "input.xlsx"
    source.touch()
    with pytest.raises(ValueError, match="--categories-map"):
        cli.run(str(source), str(tmp_path))


def test_run_raises_unsupported_file_type(tmp_path):
    source = tmp_path / "input.txt"
    source.touch()
    with pytest.raises(ValueError, match="Unsupported"):
        cli.run(str(source), str(tmp_path))


def test_run_routes_xlsx_to_etl_excel(
    tmp_path, xlsx_file, categories_map_file
):
    result = cli.run(xlsx_file, str(tmp_path), categories_map_file)
    assert len(result) > 0


def test_run_raises_missing_categories_map_for_gdrive(tmp_path):
    with pytest.raises(ValueError, match="--categories-map"):
        cli.run("gdrive:some-file-id", str(tmp_path))


def test_run_routes_gdrive_to_etl_gdrive_excel(
    tmp_path, xlsx_file, categories_map_file
):
    xlsx_bytes = Path(xlsx_file).read_bytes()
    auth_target = "moneypype.etl_gdrive_excel._authenticate"
    dl_target = "moneypype.etl_gdrive_excel._download"
    with patch(auth_target, return_value=object()):
        with patch(dl_target, return_value=xlsx_bytes):
            result = cli.run(
                "gdrive:fake-id", str(tmp_path), categories_map_file
            )
    assert len(result) > 0
