# Data

Raw datasets are **not distributed** in this repository (size and licensing).
Place the required inputs in this directory (or edit the path at the top of each script in `../src/`).

## Required inputs

### Predictand — Korea-mean series (`year` + `korea_nday`)

| file | description | source |
|---|---|---|
| `ERA5_JA_CDHD_index_1979-2024.nc` | JA compound hot–dry index (CDHD), Korea cos-weighted mean | ERA5 (tmax HWD) + SPEIbase v2.11 (SPEI3) |

CDHD = `( log1p(HWD) / σ ) × ( −SPEI3 )` — see **How CDHD is computed** in the main README. Only the finished CDHD series is needed to run the model; the heatwave-day and SPEI inputs used to *derive* it are project-internal.

### Observed predictors — precomputed track-A indices

| file | description | source |
|---|---|---|
| `era5_JA_trackA_predictors_1979-2024.csv` | JA box-mean indices `t2mna` (2-m temp, tropical N. Atlantic) and `v10io` (10-m meridional wind, E. Indian Ocean) | derived from ERA5 monthly T2M / V10 |

Source fields: ERA5 — Copernicus Climate Data Store (CDS).

### C3S multi-model-ensemble forecast — concurrent (L0) predictors

For the L0 predictors **JA T2M** and **JA V10**, two forms are required (the probabilistic/tercile forecast needs the ensemble):

| file | description |
|---|---|
| `c3s_mme_L0_ja.csv` | **MME (model-mean)** L0 predictor series — deterministic / hybrid forecast |
| `c3s_ensemble_L0_ja.csv` | **full per-member ensemble** L0 predictor values — tercile / probabilistic forecast |

Source: C3S seasonal multi-model forecasts — Copernicus CDS.

### Produced by the code (not uploaded)

`predictor_accepted_era5.npz` — from `src/01_make_predictor_index.py`.

## Data sources

- **ERA5 reanalysis** — Copernicus Climate Data Store: https://cds.climate.copernicus.eu
- **C3S seasonal forecasts (multi-model)** — Copernicus CDS.
- **SPEIbase v2.11** — Global SPEI database (CSIC).

Download / preprocessing scripts are project-internal; please contact the authors for the exact intermediate files.
