from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from moneypype.etl_gdrive_excel import _download, _run_excel_pipeline
from moneypype.schemas import TRANSACTIONS_SCHEMA


def test_run_excel_pipeline_produces_valid_schema(
    tmp_path, xlsx_file, categories_map_file
):
    xlsx_bytes = Path(xlsx_file).read_bytes()
    dest = str(tmp_path / "out.parquet")
    result = _run_excel_pipeline(xlsx_bytes, dest, categories_map_file)
    assert result.schema == TRANSACTIONS_SCHEMA


def test_run_excel_pipeline_cleans_up_temp_file_on_error(
    tmp_path, categories_map_file
):
    captured = {}

    original_named_temp = __import__("tempfile").NamedTemporaryFile

    def capturing_named_temp(**kwargs):
        f = original_named_temp(**kwargs)
        captured["path"] = f.name
        return f

    target = "moneypype.etl_gdrive_excel.tempfile.NamedTemporaryFile"
    with patch(target, capturing_named_temp):
        with pytest.raises(Exception):
            _run_excel_pipeline(
                b"not a valid xlsx",
                str(tmp_path / "out.parquet"),
                categories_map_file,
            )

    assert not Path(captured["path"]).exists()


def test_download_calls_drive_api():
    expected_bytes = b"fake xlsx content"
    mock_creds = MagicMock()

    with patch("googleapiclient.discovery.build") as mock_build:
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_request = MagicMock()
        mock_service.files.return_value.get_media.return_value = mock_request

        with patch("googleapiclient.http.MediaIoBaseDownload") as mock_dl_cls:
            def write_to_buffer(buffer, request):
                buffer.write(expected_bytes)
                downloader = MagicMock()
                downloader.next_chunk.return_value = (None, True)
                return downloader

            mock_dl_cls.side_effect = write_to_buffer

            result = _download("some-file-id", mock_creds)

    mock_service.files.return_value.get_media.assert_called_once_with(
        fileId="some-file-id"
    )
    assert result == expected_bytes
