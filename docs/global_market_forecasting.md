# Global Carbon Market Forecasting

## Dataset

- Source: `data/processed/global_market_timeseries.csv`
- Frequency: annual
- Range: 2005–2024 (20 observations)
- Targets present and used: `Market_Value`, `Market_Volume`

## Why this setup is small-sample

Twenty annual points is a short series. Complex models can overfit easily.
Walk-forward RMSE is therefore compared against naive last-value and a 3-year
moving-average baseline. If a machine-learning model does not improve RMSE,
the simpler method is selected.

## Features

Built only from information available before the predicted year:

- `Year_Index` (time trend)
- Lag-1, lag-2, 3-year rolling mean, and lag growth for both market series
- One-year lags of `Global_CO2`, `Renewable_Electricity_Share`,
  `Renewable_Production`, and `Global_GDP_Growth`

Missing 2022–2024 CO2/renewable fields are forward-filled from the last known
year and then lagged, so they represent last known values, not fabricated fills
for the same year as the target.

## Validation

Expanding-window walk-forward: initial training window is the first 12 complete
rows; each later year is predicted using only earlier years.

## Models compared

- Naive last-value
- 3-year moving average
- Linear regression
- Random forest (shallow trees)
- XGBoost (if installed; shallow trees)

## Results

### Market_Value

- Selected model: **Naive_LastValue**

| Model | MAE | RMSE | R² | MAPE | n |
|---|---:|---:|---:|---:|---:|
| Naive_LastValue | 563.3333 | 807.7848 | -0.3146 | 54.7487 | 6 |
| MovingAverage_3 | 806.3889 | 963.6093 | -0.8706 | 85.8511 | 6 |
| LinearRegression | 1592.25 | 2148.215 | -8.297 | 287.2459 | 6 |
| RandomForest | 659.2717 | 837.5441 | -0.4132 | 60.7665 | 6 |
| XGBoost | 549.7181 | 818.8822 | -0.3509 | 55.9396 | 6 |

### Market_Volume

- Selected model: **XGBoost**

| Model | MAE | RMSE | R² | MAPE | n |
|---|---:|---:|---:|---:|---:|
| Naive_LastValue | 141.5 | 180.3242 | -0.4778 | 63.032 | 6 |
| MovingAverage_3 | 164.0556 | 204.3147 | -0.8972 | 102.7263 | 6 |
| LinearRegression | 337.9819 | 525.2065 | -11.5363 | 281.9723 | 6 |
| RandomForest | 138.4296 | 184.8601 | -0.5531 | 74.9632 | 6 |
| XGBoost | 139.7033 | 172.2488 | -0.3484 | 65.5486 | 6 |

## Leakage prevention

- Chronological walk-forward only
- No contemporaneous macros for the target year
- No random shuffle
- Recursive multi-year forecasts hold macros at last known lagged values

## Limitations

- Annual series with 20 points; uncertainty is high
- 2021 value/volume spike dominates recent error
- R² can be negative when a persistent-level forecast misses a structural jump
- Forward forecasts are not guaranteed outcomes
- Macro coverage ends in 2021 for CO2 and renewables

## Outputs

- Models/metadata: `ml/models/global_market/`
- Combined history + forecast: `data/processed/global_market_forecast.csv`
- Walk-forward predictions: `data/processed/global_market_walkforward.csv`
- Metrics JSON: `data/processed/global_market_model_metrics.json`
