import { useState } from 'react'
import { scenarioAPI } from '../services/api'

export default function ScenarioSimulator() {
  const [result, setResult] = useState(null)
  const [simulating, setSimulating] = useState(false)

  const [params, setParams] = useState({
    carbon_price_change_pct: 0,
    emissions_change_pct: 0,
    renewable_share_change_pct: 0,
    gdp_growth_change_pct: 0
  })

  const handleChange = (name, value) => {
    setParams(prev => ({ ...prev, [name]: parseFloat(value) || 0 }))
  }

  const handleSimulate = async () => {
    try {
      setSimulating(true)
      setResult(null)
      const response = await scenarioAPI.simulate(params)
      setResult(response.data)
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Simulation failed')
    } finally {
      setSimulating(false)
    }
  }

  const handleReset = () => {
    setParams({
      carbon_price_change_pct: 0,
      emissions_change_pct: 0,
      renewable_share_change_pct: 0,
      gdp_growth_change_pct: 0
    })
    setResult(null)
  }

  const scenarios = [
    {
      name: 'Green Transition',
      desc: 'Increased renewables, reduced emissions',
      params: { emissions_change_pct: -15, renewable_share_change_pct: 30, gdp_growth_change_pct: 5 }
    },
    {
      name: 'Economic Boom',
      desc: 'High growth, increased emissions',
      params: { emissions_change_pct: 20, renewable_share_change_pct: 10, gdp_growth_change_pct: 30 }
    },
    {
      name: 'Carbon Tax',
      desc: 'Higher carbon prices',
      params: { carbon_price_change_pct: 100, emissions_change_pct: -10, renewable_share_change_pct: 20 }
    }
  ]

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Scenario Simulator</h2>
        <p className="text-gray-600 mb-6">
          Modify market conditions to see potential impacts on carbon market predictions
        </p>

        {/* Quick Scenarios */}
        <div className="mb-6">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Quick Scenarios</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {scenarios.map(scenario => (
              <button
                key={scenario.name}
                onClick={() => setParams({ carbon_price_change_pct: 0, ...scenario.params })}
                className="p-4 text-left border-2 border-gray-200 rounded-lg hover:border-emerald-500 hover:bg-emerald-50 transition-colors"
              >
                <div className="font-semibold text-gray-900">{scenario.name}</div>
                <div className="text-sm text-gray-600 mt-1">{scenario.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Parameter Controls */}
        <div className="space-y-6">
          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Carbon Price Change</label>
              <span className="text-sm font-semibold text-emerald-600">
                {params.carbon_price_change_pct > 0 ? '+' : ''}{params.carbon_price_change_pct}%
              </span>
            </div>
            <input
              type="range"
              min="-50"
              max="200"
              step="5"
              value={params.carbon_price_change_pct}
              onChange={(e) => handleChange('carbon_price_change_pct', e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>-50%</span>
              <span>+200%</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Global Emissions Change</label>
              <span className="text-sm font-semibold text-emerald-600">
                {params.emissions_change_pct > 0 ? '+' : ''}{params.emissions_change_pct}%
              </span>
            </div>
            <input
              type="range"
              min="-30"
              max="50"
              step="5"
              value={params.emissions_change_pct}
              onChange={(e) => handleChange('emissions_change_pct', e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>-30%</span>
              <span>+50%</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">Renewable Share Change</label>
              <span className="text-sm font-semibold text-emerald-600">
                {params.renewable_share_change_pct > 0 ? '+' : ''}{params.renewable_share_change_pct}%
              </span>
            </div>
            <input
              type="range"
              min="-20"
              max="100"
              step="5"
              value={params.renewable_share_change_pct}
              onChange={(e) => handleChange('renewable_share_change_pct', e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>-20%</span>
              <span>+100%</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700">GDP Growth Change</label>
              <span className="text-sm font-semibold text-emerald-600">
                {params.gdp_growth_change_pct > 0 ? '+' : ''}{params.gdp_growth_change_pct}%
              </span>
            </div>
            <input
              type="range"
              min="-20"
              max="50"
              step="5"
              value={params.gdp_growth_change_pct}
              onChange={(e) => handleChange('gdp_growth_change_pct', e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>-20%</span>
              <span>+50%</span>
            </div>
          </div>
        </div>

        <div className="flex space-x-4 mt-6">
          <button
            onClick={handleSimulate}
            disabled={simulating}
            className="flex-1 bg-emerald-600 text-white py-3 px-6 rounded-md hover:bg-emerald-700 disabled:bg-gray-400 font-medium transition-colors"
          >
            {simulating ? 'Simulating...' : 'Run Simulation'}
          </button>
          <button
            onClick={handleReset}
            className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-md hover:bg-gray-100 font-medium transition-colors"
          >
            Reset
          </button>
        </div>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Simulation Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* Market Value */}
            <div className="p-6 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg border-2 border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-600">Market Value</div>
                <div className="flex items-center text-xs text-gray-500">
                  <span className="mr-1">📊</span>
                  {result.model_info.market_value_model}
                </div>
              </div>
              <div className="flex items-end justify-between">
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    ${result.scenario.market_value.toFixed(0)}M
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Baseline: ${result.baseline.market_value.toFixed(0)}M
                  </div>
                </div>
                <div className={`text-right ${result.changes.value_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  <div className="text-2xl font-bold">
                    {result.changes.value_percent >= 0 ? '+' : ''}{result.changes.value_percent.toFixed(1)}%
                  </div>
                  <div className="text-sm">
                    {result.changes.value_percent >= 0 ? '↑' : '↓'} ${Math.abs(result.changes.value_absolute).toFixed(0)}M
                  </div>
                </div>
              </div>
              {result.model_info && !result.model_info.market_value_sensitive_to_scenario && (
                <div className="mt-3 p-2 bg-blue-100 rounded text-xs text-blue-700">
                  💡 This model uses the last known value - scenario changes do not affect the prediction
                </div>
              )}
            </div>

            {/* Market Volume */}
            <div className="p-6 bg-gradient-to-br from-emerald-50 to-green-50 rounded-lg border-2 border-emerald-200">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm text-gray-600">Market Volume</div>
                <div className="flex items-center text-xs text-gray-500">
                  <span className="mr-1">🤖</span>
                  {result.model_info.market_volume_model}
                </div>
              </div>
              <div className="flex items-end justify-between">
                <div>
                  <div className="text-2xl font-bold text-gray-900">
                    {result.scenario.market_volume.toFixed(0)}M tCO₂
                  </div>
                  <div className="text-sm text-gray-600 mt-1">
                    Baseline: {result.baseline.market_volume.toFixed(0)}M tCO₂
                  </div>
                </div>
                <div className={`text-right ${result.changes.volume_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  <div className="text-2xl font-bold">
                    {result.changes.volume_percent >= 0 ? '+' : ''}{result.changes.volume_percent.toFixed(1)}%
                  </div>
                  <div className="text-sm">
                    {result.changes.volume_percent >= 0 ? '↑' : '↓'} {Math.abs(result.changes.volume_absolute).toFixed(0)}M
                  </div>
                </div>
              </div>
              {result.model_info && result.model_info.market_volume_sensitive_to_scenario && (
                <div className="mt-3 p-2 bg-emerald-100 rounded text-xs text-emerald-700">
                  📈 This model responds to CO₂, renewable energy, and GDP changes
                </div>
              )}
            </div>
          </div>

          {/* Model Behavior Explanation */}
          <div className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg mb-4 border border-gray-200">
            <div className="text-sm font-semibold text-gray-700 mb-2">💡 Model Behavior</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-600">
              <div>
                <div className="font-medium text-gray-700 mb-1">Market Value Model:</div>
                <div className="space-y-1">
                  <div>• Uses: {result.model_info.market_value_model}</div>
                  <div>• Sensitive to scenarios: {result.model_info.market_value_sensitive_to_scenario ? '✅ Yes' : '❌ No'}</div>
                  <div>• Responds to: {result.model_info.features_affecting_value ? result.model_info.features_affecting_value.join(', ') : 'Last known value only'}</div>
                </div>
              </div>
              <div>
                <div className="font-medium text-gray-700 mb-1">Market Volume Model:</div>
                <div className="space-y-1">
                  <div>• Uses: {result.model_info.market_volume_model}</div>
                  <div>• Sensitive to scenarios: {result.model_info.market_volume_sensitive_to_scenario ? '✅ Yes' : '❌ No'}</div>
                  <div>• Responds to: {result.model_info.features_affecting_volume ? result.model_info.features_affecting_volume.join(', ') : 'Last known value only'}</div>
                </div>
              </div>
            </div>
            {result.model_info && !result.model_info.carbon_price_directly_modeled && (
              <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700">
                ⚠️ <strong>Carbon Price Note:</strong> Carbon price changes are shown for context but do not directly influence ML predictions in the current models.
              </div>
            )}
          </div>

          {/* Model Info */}
          <div className="p-4 bg-gray-50 rounded-lg mb-4">
            <div className="text-sm font-semibold text-gray-700 mb-2">Model Information</div>
            <div className="text-xs text-gray-600 space-y-1">
              <div>Value Model: <span className="font-medium">{result.model_info.market_value_model}</span></div>
              <div>Volume Model: <span className="font-medium">{result.model_info.market_volume_model}</span></div>
              <div>Baseline Year: <span className="font-medium">{result.model_info.baseline_year}</span></div>
              <div>Prediction Year: <span className="font-medium">{result.model_info.prediction_year}</span></div>
            </div>
          </div>

          {/* Warnings */}
          {result.warnings && result.warnings.length > 0 && (
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="text-sm font-semibold text-yellow-800 mb-2">⚠️ Warnings</div>
              <ul className="text-xs text-yellow-700 space-y-1">
                {result.warnings.map((warning, idx) => (
                  <li key={idx}>• {warning}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
