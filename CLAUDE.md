# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
poetry install

# Run CLI
moneypype <source.csv> [dest_dir]       # Default dest: src/moneypype/data/staging/

# Run tests
pytest tests --color=yes -vv --tb=short

# Lint
flake8 src/ tests/

# Docker
docker build -t moneypype .
docker run moneypype
```

## Architecture

Moneypype is a personal finance ETL pipeline: CSV → validate → transform → Parquet.

**Entry point:** `moneypype.console:main` (defined in `pyproject.toml`)

**Pipeline flow** (`src/moneypype/`):
- `console.py` — CLI (argparse), validates file existence, routes to the correct pipeline
- `etl.py` — Shared pipeline steps: `_validate_output`, `_load`
- `etl_csv.py` — CSV pipeline: extract → validate input → transform → (shared) validate output → load
- `schemas.py` — Pandera schemas for I/O validation + Polars schema for type enforcement

**Multi-pipeline convention:** each source format gets its own `etl_<format>.py` module with a `run(input_path, output_path)` entry point. Shared steps live in `etl.py`.

**Key data transforms in `etl_csv.py`:**
- Decimal comma CSV parsing (European format), `NA` treated as null
- Amount: Float64 → Int32 (multiplied by 100, stored as cents)
- Date: string → `pl.Date`
- Nullable columns: `note`, `label`, `amount_fx_ccy`

**Data files** (not tracked in git, per `.gitignore`):
- `src/moneypype/data/raw/` — input CSVs
- `src/moneypype/data/staging/` — output Parquets

## Testing

Tests live in `tests/` with two files:
- `test_console.py` — error handling for missing source / existing destination
- `test_etl_csv.py` — schema validation errors, full pipeline assertion

## Git Workflow

- Main working branch: `dev`
- Feature branches are created from `dev` and merged back into `dev`
- Do not push to `main` directly

## Agent skills

### Issue tracker

Issues live as local markdown files under `.scratch/<feature-slug>/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Default five-state vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
