import os
import tempfile
from pathlib import Path

import polars as pl

import moneypype.etl_excel as etl_excel


_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
_DEFAULT_CREDENTIALS_PATH = (
    Path.home() / ".config" / "moneypype" / "credentials.json"
)


def run(
    file_id: str, output_path: str, categories_map_path: str
) -> pl.DataFrame:
    default = str(_DEFAULT_CREDENTIALS_PATH)
    credentials_path = Path(
        os.environ.get("MONEYPYPE_GDRIVE_CREDENTIALS", default)
    )
    creds = _authenticate(credentials_path)
    xlsx_bytes = _download(file_id, creds)
    return _run_excel_pipeline(xlsx_bytes, output_path, categories_map_path)


def _authenticate(credentials_path: Path):
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    token_path = credentials_path.parent / "token.json"
    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), _SCOPES
            )
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return creds


def _download(file_id: str, creds) -> bytes:
    import io

    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload

    service = build("drive", "v3", credentials=creds)
    request = service.files().get_media(fileId=file_id)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()


def _run_excel_pipeline(
    xlsx_bytes: bytes, output_path: str, categories_map_path: str
) -> pl.DataFrame:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp.write(xlsx_bytes)
            tmp_path = tmp.name
        return etl_excel.run(tmp_path, output_path, categories_map_path)
    finally:
        if tmp_path and Path(tmp_path).exists():
            Path(tmp_path).unlink()
