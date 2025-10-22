# ISAC 2025 Project Summary

This document summarizes the current state of the ISAC 2025 Liga MX analysis project, its goals, structure, and how to get started.

## Overview
- Analyze Liga MX football data using StatsBomb, enabling offline analysis and future modeling.
- Data access primarily via `statsbombpy`; optional authenticated access through environment variables.
- Emphasis on caching raw JSON data for speed, reliability, and reproducibility.

## Repository Structure
```
ISAC2025/
├── DATA_STORAGE_GUIDE.md          # Detailed data caching and usage guide
├── README.md                      # Quick start and high-level info
├── requirements.txt               # Python dependencies
├── notebooks/
│   ├── data_analysis_example.ipynb
│   └── exploracion_inicial.ipynb
├── report/
│   └── report.md                  # (placeholder)
└── src/
    ├── get_data.py                # API connection & basic parameters
    ├── kpi_predictor.py           # (placeholder)
    ├── pull_data.ipynb            # Notebook for data pulling
    ├── tcs_scorer.py              # (placeholder)
    └── team_fingerprint.py        # (placeholder)
```

Notes:
- `DATA_STORAGE_GUIDE.md` describes a target layout under `data/` with raw and processed caches and utilities like `data_loader.py`/`data_analyzer.py` referenced in the guide (not currently present in `src/`).
- Several source files appear as placeholders with no content yet (`kpi_predictor.py`, `tcs_scorer.py`, `team_fingerprint.py`).

## Setup
1. Python 3.8+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Optional: create a `.env` at the project root for premium StatsBomb access:
   ```
   STATSBOMB_USER=your_username
   STATSBOMB_PASS=your_password
   ```
   The `README.md` also mentions `SB_USERNAME`/`SB_PASSWORD`; align on one set of names during implementation.

## Key Components (Current)
- `src/get_data.py`
  - Loads environment variables from `../.env`.
  - Sets base parameters like `DATA_DIR`, `TEAM`, `COMP_ID`, `SEASON_ID`.
  - Imports `statsbombpy` and plotting utilities (`mplsoccer`, `matplotlib`).
  - Next steps: implement actual fetching (matches/events/lineups) and local caching into `data/`.

- Guides/Docs
  - `README.md`: Quick start, libraries used, and basic usage pointers.
  - `DATA_STORAGE_GUIDE.md`: Detailed caching strategy, folder structure, and example analysis patterns. Refers to `data_loader.py` and `data_analyzer.py` utilities to be created.

- Notebooks
  - `notebooks/data_analysis_example.ipynb`: Example analysis (see guide for sample code patterns).
  - `notebooks/exploracion_inicial.ipynb`: Initial exploration.

## Planned/Referenced But Missing Utilities
- `src/data_loader.py`: CLI/utility to download and cache matches, events, and lineups by season.
- `src/data_analyzer.py`: Loader and helper functions to work with cached data, export CSVs, and compute summaries.

If you plan to follow `DATA_STORAGE_GUIDE.md`, consider implementing these two modules first.

## Usage (Current Path)
- For quick experiments, use the notebooks in `notebooks/`.
- To progress toward offline workflows, implement `data_loader.py` and `data_analyzer.py` as outlined in `DATA_STORAGE_GUIDE.md`, then:
  ```bash
  python src/data_loader.py   # download/cache data
  python src/data_analyzer.py # load/analyze/export
  ```

## Next Steps
- Align environment variable names (`STATSBOMB_*` vs `SB_*`) across code and docs.
- Implement `data_loader.py` (download/caching) and `data_analyzer.py` (loading/exports).
- Fill in `kpi_predictor.py`, `tcs_scorer.py`, and `team_fingerprint.py` with concrete logic.
- Add `report/report.md` content summarizing findings once analyses are run.

---

¡Listo! Este resumen ofrece una vista clara del proyecto actual y los siguientes pasos recomendados.
