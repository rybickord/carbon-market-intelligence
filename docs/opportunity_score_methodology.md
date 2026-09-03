# Country Opportunity Score Methodology

## What the score means

Opportunity Score is a **relative** 0–100 index of carbon-market / transition
enablement versus peers. Higher scores indicate comparatively stronger renewable
penetration, production scale, economic capacity, and carbon-policy signal, plus
a cleaner per-capita baseline used as transition-readiness context.

It is **not** a predicted investment return.

## Data

- File: `data/processed/country_intelligence.csv`
- Latest year per country; 223 countries
- Columns used: `Renewable_Electricity_Share`, `Renewable_Production`,
  `Per_Capita_CO2`, `GDP_Growth`, `Carbon_Rate_2023`

## Normalization

Same rank-normalization as the risk score: 0–100 within the latest-year peer set.

## Missing values

| Column | Handling |
|---|---|
| Renewable_Electricity_Share | Median fill; flagged |
| Renewable_Production | Median fill; flagged |
| Per_Capita_CO2 | Observed |
| GDP_Growth | Median fill; flagged |
| Carbon_Rate_2023 | Fill 0 (no observed policy rate); flagged |

## Weights (sum to 1.0)

| Component | Weight | Direction |
|---|---:|---|
| Renewable electricity share | 0.30 | higher → more opportunity |
| Renewable production | 0.25 | higher → more opportunity |
| Transition potential | 0.15 | lower per-capita CO2 → higher score |
| Economic resilience | 0.15 | higher GDP growth → higher score |
| Policy enablement | 0.15 | higher carbon rate → higher score |

## Formula

```
Opportunity_Score =
  0.30 * rank(Renewable_Electricity_Share)
+ 0.25 * rank(Renewable_Production)
+ 0.15 * rank_inverted(Per_Capita_CO2)
+ 0.15 * rank(GDP_Growth)
+ 0.15 * rank(Carbon_Rate_2023 filled)
```

Clipped to [0, 100].

## Categories

Low 0–34.99; Moderate 35–54.99; High 55–74.99; Very High 75–100.

## Limitations

- Absolute renewable production favors larger energy systems.
- Median fills pull data-sparse countries toward the middle.
- Policy rate is 2023 vintage, not contemporaneous with 2021 emissions.
- Opportunity and risk can both be elevated (large emitter with strong renewables).

## Output

`data/processed/country_opportunity_scores.csv`
