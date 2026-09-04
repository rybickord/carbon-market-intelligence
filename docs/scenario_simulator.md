# Scenario Simulator

## Purpose

The Scenario Simulator allows users to explore "what-if" questions about the carbon market by modifying key market conditions and comparing predicted outcomes against a baseline.

This is **scenario analysis**, not guaranteed economic forecasting. The simulator helps understand potential directional impacts of changing market conditions.

## Supported Parameters

The simulator exposes only parameters that are technically supported by the Phase 3 global market models:

### 1. Emissions Change (`emissions_change_pct`)

- **What it represents**: Change in global CO2 emissions
- **Model feature**: `Global_CO2_lag1`
- **Valid range**: -30% to +50%
- **Interpretation**: Positive values = increased emissions; Negative values = emission reductions

### 2. Renewable Share Change (`renewable_share_change_pct`)

- **What it represents**: Change in renewable electricity share
- **Model feature**: `Renewable_Electricity_Share_lag1`
- **Valid range**: -20% to +100%
- **Interpretation**: Measures shift toward renewable energy adoption
- **Note**: Clamped to 0-100% after applying change

### 3. GDP Growth Change (`gdp_growth_change_pct`)

- **What it represents**: Change in global GDP growth rate
- **Model feature**: `Global_GDP_Growth_lag1`
- **Valid range**: -20% to +50%
- **Interpretation**: Economic activity indicator

### 4. Carbon Price Change (`carbon_price_change_pct`)

- **What it represents**: Conceptual carbon price change
- **Model feature**: **NOT directly modeled**
- **Valid range**: -50% to +200%
- **Interpretation**: Included for completeness but does not directly affect predictions in current model
- **Note**: Carbon price may indirectly correlate with emissions/renewables but is not an explicit feature

## How It Works

### Baseline Prediction

1. Loads last known values from historical data (2024)
2. Builds feature dictionary using lag-1, lag-2, and rolling features
3. Applies trained Phase 3 models (or baselines) to predict next year (2025)
4. Returns baseline predictions for Market_Value and Market_Volume

### Scenario Prediction

1. Takes the same baseline features
2. Applies percentage changes to relevant macro features:
   - Emissions → `Global_CO2_lag1`
   - Renewable Share → `Renewable_Electricity_Share_lag1`
   - GDP Growth → `Global_GDP_Growth_lag1`
3. Re-runs predictions with modified features
4. Calculates absolute and percentage differences vs baseline

### Output Structure

```json
{
  "baseline": {
    "market_value": 535.0,
    "market_volume": 98.21
  },
  "scenario": {
    "market_value": 535.0,
    "market_volume": 398.12
  },
  "changes": {
    "value_absolute": 0.0,
    "value_percent": 0.0,
    "volume_absolute": 299.91,
    "volume_percent": 305.36
  },
  "scenario_parameters": {
    "emissions_change_pct": -10.0,
    "renewable_share_change_pct": 30.0,
    "gdp_growth_change_pct": 0.0,
    "carbon_price_change_pct": 0.0
  },
  "model_info": {
    "market_value_model": "Naive_LastValue",
    "market_volume_model": "XGBoost",
    "baseline_year": 2024,
    "prediction_year": 2025
  },
  "warnings": [
    "Market_Value uses Naive_LastValue baseline - scenario changes may not affect prediction"
  ]
}
```

## Models Used

### Market_Value

- **Selected Model**: `Naive_LastValue`
- **Implication**: Scenario changes to macro features will **not** affect Market_Value predictions
- **Reason**: Walk-forward validation showed the naive baseline outperformed ML models for this target

### Market_Volume

- **Selected Model**: `XGBoost`
- **Implication**: Scenario changes **will** affect Market_Volume predictions
- **Key Features**: Renewable_Electricity_Share_lag1 has the highest importance (54%)

## Assumptions

1. **Lagged Features**: The models use lagged (previous year) macro values. Scenario changes are applied to these lagged features, representing changes from the last known state.

2. **Ceteris Paribus**: Scenario changes are applied independently. Real-world interactions between parameters (e.g., GDP growth affecting emissions) are not automatically modeled.

3. **Historical Patterns**: Predictions assume future relationships follow historical patterns from 2005-2024.

4. **No Structural Breaks**: The simulator cannot predict structural market changes (new regulations, technology breakthroughs, market crashes).

5. **Limited Sample Size**: Models are trained on only 20 annual observations (2005-2024).

## Limitations

### Technical Limitations

1. **Naive Baseline for Value**: Market_Value uses a naive last-value approach, so scenario changes won't affect value predictions.

2. **Feature Availability**: Only features present in the Phase 3 models can be modified. Carbon price is not a direct model feature.

3. **Macro Coverage Gaps**: CO2 and renewable data end in 2021; forward-filled values are used for 2022-2024.

4. **No Multi-Year Simulation**: The simulator predicts one year ahead. It does not recursively simulate multiple future years.

### Interpretation Limitations

1. **Correlation ≠ Causation**: The models capture statistical relationships, not causal mechanisms.

2. **Extrapolation Risk**: Large scenario changes may push features outside the historical range, reducing prediction reliability.

3. **Market Dynamics**: Real carbon markets are influenced by policy, regulation, technology, and investor behavior beyond what's captured in macro indicators.

4. **Uncertainty Not Quantified**: The simulator provides point estimates without confidence intervals or probability distributions.

## Example Usage

### Python API

```python
from ml.scenario_simulator import simulate_scenario

# Baseline
result = simulate_scenario()
print(f"Baseline Value: ${result['baseline']['market_value']:.2f}M")

# Scenario: Green transition
result = simulate_scenario(
    renewable_share_change_pct=30.0,
    emissions_change_pct=-15.0,
    gdp_growth_change_pct=10.0
)

print(f"Scenario Value: ${result['scenario']['market_value']:.2f}M")
print(f"Volume Change: {result['changes']['volume_percent']:+.2f}%")
```

### FastAPI Endpoint

```bash
POST /api/scenario/simulate
Content-Type: application/json

{
  "carbon_price_change_pct": 50.0,
  "emissions_change_pct": -20.0,
  "renewable_share_change_pct": 40.0,
  "gdp_growth_change_pct": 5.0
}
```

## Validation

Scenario parameters are validated:

- **Type checking**: All parameters must be numeric
- **Range checking**: Each parameter has defined min/max bounds
- **Sanity checks**: Renewable share is clamped to 0-100% after changes

Invalid requests return 400 Bad Request with error details.

## Warnings

The simulator may return warnings such as:

- **"Market_Value uses Naive_LastValue baseline - scenario changes may not affect prediction"**: Value predictions won't respond to scenario changes
- **"Scenario shows extreme change (>100%)"**: Large changes should be interpreted with caution
- **Custom warnings**: Based on scenario configuration

## Interpretation Guidelines

### What the Simulator **Can** Tell You

- Directional impact of macro changes on market volume (given historical patterns)
- Relative sensitivity of predictions to different parameters
- Comparison of multiple scenario configurations

### What the Simulator **Cannot** Tell You

- Guaranteed future outcomes
- Causal mechanisms behind market changes
- Effects of new policies or technologies not in historical data
- Probability distributions or confidence intervals
- Multi-year trajectories

## Technical Details

### Feature Engineering

The simulator uses the same feature engineering as Phase 3 training:

- **Year_Index**: Linear time trend
- **Lag-1 and Lag-2**: Previous 1-2 year values
- **Rolling-3**: 3-year rolling average
- **Growth**: Year-over-year growth rate
- **Macro Lags**: One-year lagged macro indicators

### Model Loading

- Models are loaded from `ml/models/global_market/`
- Metadata includes feature columns, selected model, and validation metrics
- Scalers are applied before prediction (StandardScaler)
- Predictions are clamped to non-negative values

### Performance

- Simulation time: <100ms per scenario
- No model retraining occurs during simulation
- Stateless: each simulation is independent

## Future Enhancements

Potential improvements (not implemented):

1. **Confidence Intervals**: Bootstrap or quantile regression for uncertainty
2. **Multi-Year Simulation**: Recursive forecasting with scenario paths
3. **Policy Scenarios**: Incorporate regulatory changes
4. **Ensemble Predictions**: Average multiple model predictions
5. **Causal Modeling**: Use causal inference techniques
6. **Real-Time Data**: Integrate live market data feeds

## References

- Phase 3 Models: `docs/global_market_forecasting.md`
- Model Training: `ml/training/global_market_model.py`
- Model Metadata: `ml/models/global_market/*_metadata.json`
