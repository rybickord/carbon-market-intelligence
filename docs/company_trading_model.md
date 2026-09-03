# Company Trading Decision Model

## Target

`Target_Trade_Action` is binary. In the processed dataset it is identical to the
Buy/Sell flag: 1 = Buy, 0 = Sell. There is no 'no trade' class in this file.

## Leakage audit

| Column | Decision | Reason |
|---|---|---|
| `Transaction_Type` | exclude | In the processed file Buy maps exactly to Target_Trade_Action=1 and Sell to 0. Using it would reconstruct the label. |
| `Carbon_Cost_Savings_USD` | exclude | Recorded cost savings are an outcome of the executed action, not a pre-decision input. |
| `Optimization_Scenario` | exclude | Scenario tag describes the case after the optimization/trade framing; it is not a firm-state variable available as a trading input. |
| `Credits_Traded_tCO2` | exclude | This is the volume of the transaction that was executed. It is known only after the decision to buy or sell. |
| `Company_ID` | exclude | Identifier. It would allow memorizing firms rather than learning transferable drivers. |
| `Date` | exclude | Calendar stamp is not a causal pre-trade feature and can leak period-specific artifacts. |
| `Compliance_Cost_USD` | include | Treated as a known compliance obligation cost available before the trade. Means are similar across classes, so it is not a disguised label. |
| `Verification_Status` | include | Compliance/verification state of the firm can be known before a trade is placed. |

## Included features

- Categorical: `Industry_Type`, `Fuel_Type`, `Verification_Status`
- Numeric: `Energy_Demand_MWh`, `Emission_Produced_tCO2`, `Emission_Allowance_tCO2`, `Carbon_Price_USD_per_t`, `Compliance_Cost_USD`
- Derived (pre-decision): `Allowance_Gap_tCO2` = emissions minus allowance

## Validation

stratified 80/20 train/test split, random_state=42

Class balance (full file): {'1': 2531, '0': 2469}

## Models

Logistic regression baseline, random forest, and XGBoost when available.
Selection criterion is binary F1 on the held-out test set, not accuracy alone.

Selected model: **LogisticRegression**

## Test metrics

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| LogisticRegression | 0.517 | 0.5209 | 0.5652 | 0.5422 | 0.5168 |
| RandomForest | 0.518 | 0.5226 | 0.5474 | 0.5347 | 0.5039 |
| XGBoost | 0.5 | 0.5058 | 0.5178 | 0.5117 | 0.5001 |

Selected-model confusion matrix (rows = actual 0/1, columns = predicted 0/1):

`[[231, 263], [220, 286]]`

## Limitations

- The label is a reconstructed Buy/Sell action, not an observed future decision.
- Predictive power depends on whether allowance gaps and costs actually drive trades in this table.
- Company identifiers were excluded, so firm-specific trading style is not modeled.
- Probabilities are classifier scores on a held-out split, not calibrated market odds.

## Outputs

- `ml/models/company_trading/`
- `data/processed/company_trading_evaluation.json`
