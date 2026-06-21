# 02 — Core app: inputs, run, output

Status: ready-for-agent

## Parent

`.scratch/streamlit-frontend/PRD.md`

## What to build

Replace the stub app with the full Streamlit UI: three text path inputs (source file, output directory, categories map), a Run button, and output handling for both the success and failure cases.

- Source file input has no default (user must fill it in)
- Output directory input is pre-filled from `console.default_dest()`
- Categories map input is pre-filled from `console.default_map()`
- Clicking Run calls `console.run(source, dest, categories_map)`
- On success: show a `st.success()` banner stating where the file was saved, then render the first 20 rows of the returned DataFrame via `st.dataframe()`
- On any exception: catch it and display the exception message via `st.error()`; the UI must remain usable so the user can correct inputs and retry without refreshing

No business logic belongs in the app module — it is a thin adapter over `console.run()`. No new tests are needed; the existing test suites cover the pipeline seam.

## Acceptance criteria

- [ ] Three `st.text_input` widgets are rendered with the correct labels and default values
- [ ] Clicking Run with a valid source path produces a `st.success()` banner and a 20-row preview table
- [ ] A non-existent source path shows a `st.error()` with the `FileNotFoundError` message
- [ ] A source path whose output already exists shows a `st.error()` with the `FileExistsError` message
- [ ] An unsupported file extension shows a `st.error()` with the `ValueError` message
- [ ] After any error the inputs remain editable and Run can be clicked again without refreshing
- [ ] All existing tests still pass

## Blocked by

- `.scratch/streamlit-frontend/issues/01-wiring.md`
