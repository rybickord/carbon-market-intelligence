# Country Risk Score Methodology

## What the score means

Risk Score is a **relative** 0–100 index across countries in `country_intelligence.csv`.
0 = lower carbon-market / transition risk versus peers in this dataset.
100 = higher relative risk.

It is **not** a probability of default, a price forecast, or an absolute hazard rate.

## Data

- File: `data/processed/country_intelligence.csv`
- Unit of analysis: latest available year per country (ISO)
- Coverage: 223 countries
- Columns used (only those that exist): `CO2`, `Per_Capita_CO2`,
  `Renewable_Electricity_Share`, `GDP_Growth`, `Carbon_Rate_2023`

## Normalization

Each component is rank-normalized among countries with a valid value:

```
score = (rank - 1) / (N_valid - 1) * 100
```

Ranks use average ties. This is robust to outliers and keeps every component on 0–100.

## Missing values

| Column | Handling | Rationale |
|---|---|---|
| CO2, Per_Capita_CO2 | No fill (complete in source) | Observed values |
| Renewable_Electricity_Share | Median of latest-year sample | Neutral peer assumption; flagged |
| GDP_Growth | Median of latest-year sample | Neutral peer assumption; flagged |
| Carbon_Rate_2023 | Fill 0 | Missing rate treated as no observed carbon price; flagged |

## Weights (sum to 1.0)

These weights encode an explicit interpretation: high emissions intensity, weak
renewables, weak growth, and weak carbon pricing raise relative risk.

| Component | Weight | Direction |
|---|---:|---|
| Total CO2 | 0.30 | higher CO2 → higher risk |
| Per-capita CO2 | 0.20 | higher intensity → higher risk |
| Renewable weakness | 0.25 | lower renewable electricity share → higher risk |
| GDP weakness | 0.15 | lower GDP growth → higher risk |
| Policy weakness | 0.10 | lower carbon rate → higher risk |

## Formula

```
Risk_Score =
  0.30 * rank(CO2)
+ 0.20 * rank(Per_Capita_CO2)
+ 0.25 * rank_inverted(Renewable_Electricity_Share)
+ 0.15 * rank_inverted(GDP_Growth)
+ 0.10 * rank_inverted(Carbon_Rate_2023 filled)
```

Clipped to [0, 100].

## Categories

| Category | Score |
|---|---|
| Low | 0–34.99 |
| Moderate | 35–54.99 |
| High | 55–74.99 |
| Very High | 75–100 |

## Limitations

- Relative ranks move if the country set changes.
- Latest year is 2021 for this processed table.
- `Carbon_Rate_2023` is a static 2023 field, not a historical panel.
- Total CO2 favors large emitters; per-capita is included to offset size-only ranking.
- Imputation flags must be read with the score.

## Output

`data/processed/country_risk_scores.csv`
