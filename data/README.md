# Data

Raw datasets are **not distributed** in this repository (size and licensing).
Place the required inputs in this directory (or edit the path at the top of each
script in `../src/`).

## Required inputs

| file / group | description | source |
|---|---|---|
| `ERA5_JA_HW_index_1979-2024.nc` | ERA5-based JA heatwave-day count over Korea (`korea_nday`) | derived from ERA5 |
| `SPEI/SPEIbase_v2.11_spei3_korea_JA_1901-2024.csv` | SPEI-3 (drought) index, JA, Korea | SPEIbase v2.11 |
| ERA5 monthly fields | predictor fields at leads 0–3 | ERA5 — Copernicus CDS |
| `predictor_accepted_era5.npz` | screened predictor pool — produced by `src/01_make_predictor_index.py` | this project |
| `c3s_cdhd_permember_predictors_1993-2016.csv` | **per-member** C3S forecast values of the CDHD predictors (for the ensemble / tercile forecast) | C3S seasonal multi-model — Copernicus CDS |

The CDHD predictand is `( log1p(HWD)/σ ) × ( −SPEI3 )`.

## Data sources

- **ERA5 reanalysis** — Copernicus Climate Data Store: https://cds.climate.copernicus.eu
- **C3S seasonal forecasts (multi-model)** — Copernicus Climate Data Store.
- **SPEIbase v2.11** — Global SPEI database (CSIC).

Download and preprocessing scripts are project-internal; please contact the
authors for access to the exact intermediate files.
