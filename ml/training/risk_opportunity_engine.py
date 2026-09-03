"""
Country risk and opportunity scores from country_intelligence.csv.

Transparent weighted composites on the latest year per country. No ML model.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from ml.paths import docs_dir, processed_dir, project_root

DATA_PATH = processed_dir() / "country_intelligence.csv"
RISK_OUTPUT = processed_dir() / "country_risk_scores.csv"
OPP_OUTPUT = processed_dir() / "country_opportunity_scores.csv"
RISK_DOC = docs_dir() / "risk_score_methodology.md"
OPP_DOC = docs_dir() / "opportunity_score_methodology.md"
COMPONENTS_PATH = processed_dir() / "country_score_components.json"

RISK_WEIGHTS = {
    "CO2_intensity": 0.30,
    "Per_Capita_CO2_risk": 0.20,
    "Renewable_weakness": 0.25,
    "GDP_weakness": 0.15,
    "Policy_weakness": 0.10,
}
OPP_WEIGHTS = {
    "Renewable_electricity": 0.30,
    "Renewable_production": 0.25,
    "Transition_potential": 0.15,
    "Economic_resilience": 0.15,
    "Policy_enablement": 0.15,
}

assert abs(sum(RISK_WEIGHTS.values()) - 1.0) < 1e-9
assert abs(sum(OPP_WEIGHTS.values()) - 1.0) < 1e-9

CATEGORY_BREAKS = [(35, "Low"), (55, "Moderate"), (75, "High"), (101, "Very High")]


def rank_normalise(series: pd.Series, ascending: bool = True) -> pd.Series:
    ranked = series.rank(method="average", na_option="keep", ascending=ascending)
    n_valid = int(series.notna().sum())
    if n_valid == 0:
        return pd.Series(np.nan, index=series.index)
    if n_valid == 1:
        out = ranked.copy()
        out.loc[series.notna()] = 50.0
        return out
    return ((ranked - 1) / (n_valid - 1) * 100).round(4)


def fill_missing_with_median(series: pd.Series):
    mask = series.isna()
    return series.fillna(series.median()), mask


def categorize(score: float) -> str:
    if pd.isna(score):
        return "Unknown"
    for threshold, label in CATEGORY_BREAKS:
        if score < threshold:
            return label
    return "Very High"


def latest_by_country(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values("Year").groupby("ISO", as_index=False).last()


def compute_risk_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["CO2_filled"] = out["CO2"]
    out["PerCap_filled"] = out["Per_Capita_CO2"]
    out["Renew_filled"], renew_mask = fill_missing_with_median(
        out["Renewable_Electricity_Share"]
    )
    out["GDP_filled"], gdp_mask = fill_missing_with_median(out["GDP_Growth"])
    out["Rate_filled"] = out["Carbon_Rate_2023"].fillna(0)
    rate_mask = out["Carbon_Rate_2023"].isna()

    out["comp_CO2"] = rank_normalise(out["CO2_filled"], ascending=True)
    out["comp_PerCap"] = rank_normalise(out["PerCap_filled"], ascending=True)
    out["comp_RenewWeak"] = rank_normalise(out["Renew_filled"], ascending=False)
    out["comp_GDPWeak"] = rank_normalise(out["GDP_filled"], ascending=False)
    out["comp_PolicyWeak"] = rank_normalise(out["Rate_filled"], ascending=False)

    out["Risk_Score"] = (
        RISK_WEIGHTS["CO2_intensity"] * out["comp_CO2"]
        + RISK_WEIGHTS["Per_Capita_CO2_risk"] * out["comp_PerCap"]
        + RISK_WEIGHTS["Renewable_weakness"] * out["comp_RenewWeak"]
        + RISK_WEIGHTS["GDP_weakness"] * out["comp_GDPWeak"]
        + RISK_WEIGHTS["Policy_weakness"] * out["comp_PolicyWeak"]
    ).clip(0, 100).round(2)
    out["Risk_Category"] = out["Risk_Score"].map(categorize)
    out["Flag_Renewable_Imputed"] = renew_mask
    out["Flag_GDP_Imputed"] = gdp_mask
    out["Flag_CarbonRate_Imputed"] = rate_mask
    return out


def compute_opportunity_scores(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["Renew_elec_filled"], re_mask = fill_missing_with_median(
        out["Renewable_Electricity_Share"]
    )
    out["Renew_prod_filled"], rp_mask = fill_missing_with_median(
        out["Renewable_Production"]
    )
    out["GDP_filled_opp"], gdp_mask = fill_missing_with_median(out["GDP_Growth"])
    out["Rate_opp"] = out["Carbon_Rate_2023"].fillna(0)
    rate_mask = out["Carbon_Rate_2023"].isna()

    out["comp_RenewElec"] = rank_normalise(out["Renew_elec_filled"], ascending=True)
    out["comp_RenewProd"] = rank_normalise(out["Renew_prod_filled"], ascending=True)
    out["comp_Transition"] = rank_normalise(out["Per_Capita_CO2"], ascending=False)
    out["comp_EconRes"] = rank_normalise(out["GDP_filled_opp"], ascending=True)
    out["comp_PolicyEnable"] = rank_normalise(out["Rate_opp"], ascending=True)

    out["Opportunity_Score"] = (
        OPP_WEIGHTS["Renewable_electricity"] * out["comp_RenewElec"]
        + OPP_WEIGHTS["Renewable_production"] * out["comp_RenewProd"]
        + OPP_WEIGHTS["Transition_potential"] * out["comp_Transition"]
        + OPP_WEIGHTS["Economic_resilience"] * out["comp_EconRes"]
        + OPP_WEIGHTS["Policy_enablement"] * out["comp_PolicyEnable"]
    ).clip(0, 100).round(2)
    out["Opportunity_Category"] = out["Opportunity_Score"].map(categorize)
    out["Flag_RenewElec_Imputed"] = re_mask
    out["Flag_RenewProd_Imputed"] = rp_mask
    out["Flag_GDP_Imputed_opp"] = gdp_mask
    out["Flag_CarbonRate_Imputed_opp"] = rate_mask
    return out


def validate_scores(df: pd.DataFrame, score_col: str):
    assert df[score_col].between(0, 100).all(), f"{score_col} outside [0, 100]"
    assert not df[score_col].isna().any(), f"{score_col} has NaN"
    print(f"  {score_col}: range [{df[score_col].min():.2f}, {df[score_col].max():.2f}]")


def _write_risk_doc(n_countries: int):
    RISK_DOC.write_text(
        f"""# Country Risk Score Methodology

## What the score means

Risk Score is a **relative** 0–100 index across countries in `country_intelligence.csv`.
0 = lower carbon-market / transition risk versus peers in this dataset.
100 = higher relative risk.

It is **not** a probability of default, a price forecast, or an absolute hazard rate.

## Data

- File: `data/processed/country_intelligence.csv`
- Unit of analysis: latest available year per country (ISO)
- Coverage: {n_countries} countries
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
""",
        encoding="utf-8",
    )


def _write_opp_doc(n_countries: int):
    OPP_DOC.write_text(
        f"""# Country Opportunity Score Methodology

## What the score means

Opportunity Score is a **relative** 0–100 index of carbon-market / transition
enablement versus peers. Higher scores indicate comparatively stronger renewable
penetration, production scale, economic capacity, and carbon-policy signal, plus
a cleaner per-capita baseline used as transition-readiness context.

It is **not** a predicted investment return.

## Data

- File: `data/processed/country_intelligence.csv`
- Latest year per country; {n_countries} countries
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
""",
        encoding="utf-8",
    )


def main():
    os.chdir(project_root())
    docs_dir().mkdir(parents=True, exist_ok=True)
    processed_dir().mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("COUNTRY RISK & OPPORTUNITY ENGINE")
    print("=" * 60)

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded: {DATA_PATH} shape={df.shape}")
    latest = latest_by_country(df)
    print(f"Latest-year rows: {len(latest)}")

    risk_df = compute_risk_scores(latest)
    risk_out = risk_df[
        [
            "Country",
            "ISO",
            "Year",
            "CO2",
            "Per_Capita_CO2",
            "Renewable_Electricity_Share",
            "GDP_Growth",
            "Carbon_Rate_2023",
            "comp_CO2",
            "comp_PerCap",
            "comp_RenewWeak",
            "comp_GDPWeak",
            "comp_PolicyWeak",
            "Risk_Score",
            "Risk_Category",
            "Flag_Renewable_Imputed",
            "Flag_GDP_Imputed",
            "Flag_CarbonRate_Imputed",
        ]
    ].copy()
    validate_scores(risk_out, "Risk_Score")
    risk_out.to_csv(RISK_OUTPUT, index=False)
    print(f"Saved {RISK_OUTPUT}")
    print(risk_out["Risk_Category"].value_counts().to_string())

    opp_df = compute_opportunity_scores(latest)
    opp_out = opp_df[
        [
            "Country",
            "ISO",
            "Year",
            "Renewable_Electricity_Share",
            "Renewable_Production",
            "Per_Capita_CO2",
            "GDP_Growth",
            "Carbon_Rate_2023",
            "comp_RenewElec",
            "comp_RenewProd",
            "comp_Transition",
            "comp_EconRes",
            "comp_PolicyEnable",
            "Opportunity_Score",
            "Opportunity_Category",
            "Flag_RenewElec_Imputed",
            "Flag_RenewProd_Imputed",
            "Flag_GDP_Imputed_opp",
            "Flag_CarbonRate_Imputed_opp",
        ]
    ].copy()
    validate_scores(opp_out, "Opportunity_Score")
    opp_out.to_csv(OPP_OUTPUT, index=False)
    print(f"Saved {OPP_OUTPUT}")
    print(opp_out["Opportunity_Category"].value_counts().to_string())

    n_countries = int(df["ISO"].nunique())
    _write_risk_doc(n_countries)
    _write_opp_doc(n_countries)
    print(f"Docs: {RISK_DOC} {OPP_DOC}")
    print("RISK & OPPORTUNITY ENGINE COMPLETE")


if __name__ == "__main__":
    main()
