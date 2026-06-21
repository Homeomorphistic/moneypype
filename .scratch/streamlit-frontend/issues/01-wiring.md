# 01 — Wiring: dependency + entry point

Status: ready-for-agent

## Parent

`.scratch/streamlit-frontend/PRD.md`

## What to build

Add `streamlit` as a project dependency and wire up a `moneypype-ui` Poetry script entry point that launches the Streamlit app. The app module itself should exist as a stub (e.g. a title and a placeholder message) so the entry point is immediately runnable and demoable without the full UI.

Install the dependency with `poetry add streamlit` — do not edit `pyproject.toml` manually. Activate `.venv` before running any Python or CLI commands.

## Acceptance criteria

- [ ] `poetry add streamlit` has been run and both `pyproject.toml` and `poetry.lock` reflect the new dependency
- [ ] A `moneypype-ui` script entry point is declared in `pyproject.toml` and points to the app module
- [ ] Running `moneypype-ui` opens a Streamlit page in the browser (stub content is fine)
- [ ] The existing `moneypype` CLI entry point still works and tests still pass

## Blocked by

None — can start immediately
