# PRD: Streamlit Frontend

Status: ready-for-agent

## Problem Statement

Running the moneypype ETL pipeline requires typing a terminal command with file paths as arguments. As a personal finance tool used occasionally, this friction is unnecessary — the user wants to trigger a pipeline run from a browser UI without memorising CLI syntax or opening a terminal.

## Solution

A local Streamlit web app that presents three pre-filled path inputs (source file, output directory, categories map), a Run button, and — on success — a confirmation banner and a preview of the first 20 rows of the output DataFrame. On failure, a human-readable error message is shown in place of the preview.

## User Stories

1. As a user, I want to open the moneypype UI with a short command, so that I don't have to remember the CLI syntax.
2. As a user, I want to see pre-filled default values for the output directory and categories map, so that I can run the pipeline without editing anything for the common case.
3. As a user, I want to type a file path into a text input to specify the source file, so that I can point at any file on my machine without uploading it.
4. As a user, I want to type a directory path to specify where the output Parquet is saved, so that I can change the destination when needed.
5. As a user, I want to type a file path for the categories map, so that I can override the bundled default when needed.
6. As a user, I want to click a single Run button to trigger the pipeline, so that the action is explicit and intentional.
7. As a user, I want to see a success banner telling me where the output was saved, so that I can confirm the run completed.
8. As a user, I want to see a preview table of the first 20 rows of the output, so that I can visually verify the data looks correct without opening the Parquet file.
9. As a user, I want to see a clear error message when the source file does not exist, so that I can correct the path and retry.
10. As a user, I want to see a clear error message when the output file already exists at the destination, so that I understand why the run was blocked.
11. As a user, I want to see a clear error message when the input file fails schema validation, so that I know the data is malformed before it reaches the output.
12. As a user, I want to see a clear error message when an unsupported file format is provided, so that I know which formats are accepted.
13. As a user, I want the UI to remain usable after an error, so that I can fix the inputs and retry without refreshing the page.

## Implementation Decisions

- The Streamlit app lives in the `moneypype` package and is the sole new module. It imports and calls `console.run()` directly — the app is a thin adapter with no business logic of its own.
- A new Poetry script entry point (`moneypype-ui`) is added so the user can launch the app with a short command rather than `streamlit run src/...`.
- All three inputs (source path, output directory, categories map path) are `st.text_input` widgets. No file upload widget is used — the files already exist on disk, so copying them through the browser is unnecessary.
- Default values for output directory and categories map are sourced from `console.default_dest()` and `console.default_map()` respectively, keeping them in sync with the CLI defaults.
- The Run button triggers a call to `console.run(source, dest, categories_map)`. The return value (a Polars DataFrame) is displayed as a preview using `st.dataframe()` limited to the first 20 rows.
- All exceptions raised by `console.run()` (including `FileNotFoundError`, `FileExistsError`, `ValueError`, and Pandera validation errors) are caught and displayed via `st.error()`. The `.args[0]` message from each exception is already user-readable.
- `streamlit` is added as a project dependency in `pyproject.toml`.
- No authentication, sessions, or multi-user concerns are addressed — the app is local-only.

## Testing Decisions

- **What makes a good test here:** tests should verify observable pipeline behaviour (correct Parquet output, correct error raised) at the `console.run()` seam — not Streamlit rendering details or widget state.
- **No new tests are written for the UI layer.** The Streamlit app is a three-input adapter over `console.run()`; testing it meaningfully would require a browser driver (Playwright/Selenium), which is disproportionate for a personal local tool.
- The existing `test_console.py`, `test_etl_csv.py`, and `test_etl_excel.py` suites already cover the seam the UI delegates to. Any regression in pipeline logic will surface there.
- If `console.run()` is refactored to accommodate the UI (e.g. signature changes), the existing tests must be updated accordingly.

## Out of Scope

- Authentication or access control of any kind.
- Deployment to a remote server or containerised environment.
- Viewing or querying previously generated Parquet files from the UI.
- Bulk / batch processing of multiple source files in one run.
- A directory picker dialog — the destination is a plain text input.
- Drag-and-drop file upload — paths are entered as text.
- Removing the categories map input (deferred to a future PR once the CSV pipeline is fully retired).

## Further Notes

- The categories map is expected to remain a static bundled file for the foreseeable future. The input is retained so the user can override it, but it is likely to be removed once only the Excel pipeline remains and the default is always appropriate.
- The CLI entry point (`moneypype`) is not affected by this change and should continue to work as before.
