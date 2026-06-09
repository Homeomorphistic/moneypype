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
- `console.py` — CLI (argparse), validates file existence, orchestrates the run
- `etl.py` — Core pipeline using Polars `.pipe()` chaining: extract → validate input → transform → validate output → load
- `schemas.py` — Pandera schemas for I/O validation + Polars schema for type enforcement

**Key data transforms in `etl.py`:**
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
- `test_etl.py` — schema validation errors, full pipeline assertion
