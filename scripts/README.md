# Scripts directory

These utilities are **not** imported by the running API (`api_complete.py`). They exist for **data preparation**, **model work**, **QA**, and **maintenance**. Run them from the **repository root** so relative paths such as `./data/` and `./models/` work.

## Layout

| Folder | Purpose |
|--------|---------|
| **`corpus/`** | Build or extend RAG corpora: PDF/JSON ingestion, merge, rebuild, web scraping helpers. |
| **`training/`** | Golden training JSON and `train_golden_data` style jobs. |
| **`templates/`** | Generate or list professional DOCX templates; logo conversion helpers. |
| **`qa/`** | Lightweight document/API checks (`test_document_*.py`, `diagnose_document_testing.py`). |
| **`dev/`** | Environment setup, PDF stack installer, adapter config fixer, optional pipeline demo (`PRODUCTION_PIPELINE.py`), `cleanup_project.py`. |

## Bootstrap

`scripts/_repo.py` exposes `repo_root()` and `bootstrap_path()` so a script in any subfolder can add the repo root and `src/` to `sys.path` without hard-coding depth.

## Removed (intentionally)

Obsolete one-off template text fixers, duplicate security-regex patchers, broken master-runner, and two very large interactive manual test harnesses were deleted to keep the tree presentation-friendly. They remain recoverable from **git history** if needed for an appendix.
