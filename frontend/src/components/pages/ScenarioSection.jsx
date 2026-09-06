import { useState } from 'react'
import { scenarioAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'
import ErrorMessage from '../ErrorMessage'

export default function ScenarioSection() {
  // Initialize with explicit baseline values
  const [params, setParams] = useState({
    carbon_price_change: 0,
    renewable_share_change: 0,
    gdp_growth_change: 0,
    emissions_change: 0,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Reset to baseline function
  const handleReset = () => {
    setParams({
      carbon_price_change: 0,
      renewable_share_change: 0,
      gdp_growth_change: 0,
      emissions_change: 0,
    })
    setResult(null)
    setError(null)
  }

  const handleSimulate = async () => {
    setLoading(true)
    setError(null)
    setResult(null) // Clear previous result
    
    try {
      // Convert parameter names to match API expectations
      const apiParams = {
        carbon_price_change_pct: params.carbon_price_change,
        renewable_share_change_pct: params.renewable_share_change,
        gdp_growth_change_pct: params.gdp_growth_change,
        emissions_change_pct: params.emissions_change,
      }
      
      // Debug logging to verify state synchronization
      console.log('ScenarioSection - Frontend State:', params)
      console.log('ScenarioSection - API Payload:', apiParams)
      
      const response = await scenarioAPI.simulate(apiParams)
      setResult(response.data)
      
      console.log('ScenarioSection - API Response:', response.data)
      
    } catch (err) {
      console.error('Simulation failed:', err)
      setError(err.response?.data?.detail || err.message || 'Failed to run scenario simulation')
    } finally {
      setLoading(false)
    }
  }

  const sliders = [
    { key: 'carbon_price_change', label: 'Carbon Price', min: -50, max: 200, unit: '%' },
    { key: 'renewable_share_change', label: 'Renewable Energy Share', min: -20, max: 100, unit: '%' },
    { key: 'gdp_growth_change', label: 'GDP Growth', min: -20, max: 50, unit: '%' },
    { key: 'emissions_change', label: 'CO₂ Emissions', min: -30, max: 50, unit: '%' },
  ]

  return (
    <section id="scenario" className="py-24 bg-carbon-dark">
      <div className="section-container space-y-16">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-scenario-accent/10 border border-scenario-accent/20 rounded-full mb-6">
            <span className="text-sm text-scenario-accent font-medium uppercase tracking-wider">Scenario Lab</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-ivory mb-4">
            What-If Analysis
          </h2>
          <p className="text-xl text-ivory-secondary">
            Interactive scenario modeling to explore how market drivers affect carbon credit 
            market outcomes. Adjust key parameters and see predicted impacts in real-time.
          </p>
        </div>

        {error && <ErrorMessage message={error} />}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Controls */}
          <div className="bg-carbon-dark-elevated rounded-xl border border-ivory-muted/10 p-8 space-y-8">
            <h3 className="text-2xl font-bold text-ivory">Scenario Parameters</h3>
            <div className="p-4 bg-carbon-dark-secondary rounded-lg mb-6">
              <div className="text-sm text-ivory-muted mb-2">Parameter Effects on Models</div>
              <div className="text-xs text-ivory-secondary space-y-1">
                <div><strong>Market Value:</strong> Uses Naive_LastValue and does not directly respond to scenario parameters</div>
                <div><strong>Market Volume:</strong> Uses XGBoost - responds to Renewables, GDP, CO₂</div>
                <div><strong>Carbon Price:</strong> Not directly modeled in current forecasting models</div>
              </div>
            </div>
            {sliders.map((slider) => (
              <div key={slider.key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-ivory-secondary">
                    {slider.label}
                    {slider.key === 'carbon_price_change' && (
                      <span className="ml-2 text-xs text-yellow-400" title="Not directly modeled in current forecasting models">⚠️</span>
                    )}
                  </label>
                  <span className={`text-lg font-bold ${
                    params[slider.key] > 0 ? 'text-positive' :
                    params[slider.key] < 0 ? 'text-negative' :
                    'text-ivory-muted'
                  }`}>
                    {params[slider.key] > 0 ? '+' : ''}{params[slider.key]}{slider.unit}
                  </span>
                </div>
                <div className="relative">
                  <input
                    type="range"
                    min={slider.min}
                    max={slider.max}
                    step={1}
                    value={params[slider.key]}
                    onChange={(e) => {
                      const newValue = Number(e.target.value)
                      setParams(prev => ({ ...prev, [slider.key]: newValue }))
                      // Clear previous results when parameters change
                      setResult(null)
                      setError(null)
                    }}
                    className="w-full h-2 bg-carbon-dark-secondary rounded-lg appearance-none cursor-pointer accent-scenario-accent"
                  />
                  {/* 0% baseline marker */}
                  <div 
                    className="absolute top-0 w-0.5 h-2 bg-ivory-muted/50 pointer-events-none"
                    style={{
                      left: `${((0 - slider.min) / (slider.max - slider.min)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  />
                </div>
                <div className="flex justify-between text-xs text-ivory-muted relative">
                  <span>{slider.min}{slider.unit}</span>
                  <span 
                    className="absolute text-ivory-muted/70 font-medium"
                    style={{
                      left: `${((0 - slider.min) / (slider.max - slider.min)) * 100}%`,
                      transform: 'translateX(-50%)'
                    }}
                  >
                    0{slider.unit}
                  </span>
                  <span>{slider.max}{slider.unit}</span>
                </div>
              </div>
            ))}
            <div className="flex space-x-4">
              <button 
                onClick={handleSimulate}
                disabled={loading}
                className="flex-1 btn-primary text-lg py-4"
              >
                {loading ? 'Simulating...' : 'Run Simulation'}
              </button>
              <button
                onClick={handleReset}
                disabled={loading}
                className="px-6 py-4 border-2 border-ivory-muted/30 text-ivory-secondary rounded-lg hover:bg-ivory-muted/10 transition-colors font-medium"
              >
                Reset
              </button>
            </div>
          </div>

          {/* Results */}
          <div className="bg-carbon-dark-elevated rounded-xl border border-ivory-muted/10 p-8 space-y-6">
            <h3 className="text-2xl font-bold text-ivory">Predicted Outcomes</h3>
            {loading ? (
              <LoadingSpinner message="Running scenario..." />
            ) : result ? (
              <div className="space-y-6">
                <div className="p-6 bg-carbon-dark-secondary rounded-lg space-y-3">
                  <div className="text-sm text-ivory-muted">Baseline Market Value</div>
                  <div className="text-3xl font-bold text-ivory">
                    ${result.baseline?.market_value?.toFixed(0) || 'N/A'}M
                  </div>
                </div>
                <div className="p-6 bg-scenario-accent/10 border border-scenario-accent/30 rounded-lg space-y-3">
                  <div className="text-sm text-scenario-accent">Scenario Market Value</div>
                  <div className="text-3xl font-bold text-ivory">
                    ${result.scenario?.market_value?.toFixed(0) || 'N/A'}M
                  </div>
                  <div className={`text-sm font-medium ${
                    (result.changes?.value_percent || 0) > 0 ? 'text-positive' : 
                    (result.changes?.value_percent || 0) < 0 ? 'text-negative' : 'text-ivory-muted'
                  }`}>
                    {(result.changes?.value_percent || 0) > 0 ? '+' : ''}
                    {result.changes?.value_percent?.toFixed(1) || 0}% change
                  </div>
                </div>
                <div className="p-6 bg-carbon-dark-secondary rounded-lg space-y-3">
                  <div className="text-sm text-ivory-muted">Baseline Market Volume</div>
                  <div className="text-3xl font-bold text-ivory">
                    {result.baseline?.market_volume?.toFixed(0) || 'N/A'}M tCO₂
                  </div>
                </div>
                <div className="p-6 bg-data-blue/10 border border-data-blue/30 rounded-lg space-y-3">
                  <div className="text-sm text-data-blue">Scenario Market Volume</div>
                  <div className="text-3xl font-bold text-ivory">
                    {result.scenario?.market_volume?.toFixed(0) || 'N/A'}M tCO₂
                  </div>
                  <div className={`text-sm font-medium ${
                    (result.changes?.volume_percent || 0) > 0 ? 'text-positive' : 
                    (result.changes?.volume_percent || 0) < 0 ? 'text-negative' : 'text-ivory-muted'
                  }`}>
                    {(result.changes?.volume_percent || 0) > 0 ? '+' : ''}
                    {result.changes?.volume_percent?.toFixed(1) || 0}% change
                  </div>
                </div>
                
                {/* Model Information */}
                <div className="p-4 bg-carbon-dark-secondary rounded-lg">
                  <div className="text-sm text-ivory-muted mb-2">Model Information</div>
                  <div className="text-xs text-ivory-secondary space-y-1">
                    <div>Value Model: <span className="font-medium">{result.model_info?.market_value_model || 'N/A'}</span></div>
                    <div>Volume Model: <span className="font-medium">{result.model_info?.market_volume_model || 'N/A'}</span></div>
                    <div>Next Forecast Year: <span className="font-medium">{result.model_info?.prediction_year || 'N/A'}</span></div>
                  </div>
                </div>

                {/* Warnings */}
                {result.warnings && result.warnings.length > 0 && (
                  <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                    <div className="text-sm text-yellow-400 mb-2">⚠️ Important Notes</div>
                    <ul className="text-xs text-yellow-300 space-y-1">
                      {result.warnings.map((warning, idx) => (
                        <li key={idx}>• {warning}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {/* Extreme results warning */}
                {(Math.abs(result.changes?.value_percent || 0) > 100 || Math.abs(result.changes?.volume_percent || 0) > 200) && (
                  <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                    <div className="text-sm text-orange-400 mb-2">⚠️ Extreme Model Response</div>
                    <div className="text-xs text-orange-300">
                      This scenario produces an extreme prediction. The model may be extrapolating 
                      beyond its training range. Results should be interpreted with caution.
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-ivory-muted">
                <div className="text-center space-y-2">
                  <svg className="w-16 h-16 mx-auto text-ivory-muted" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p>Adjust parameters and run simulation</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
