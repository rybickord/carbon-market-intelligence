import { useState } from 'react'
import { scenarioAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'
import ErrorMessage from '../ErrorMessage'

export default function ScenarioSection() {
  const [params, setParams] = useState({
    carbon_price_change: 0,
    renewable_share_change: 0,
    gdp_growth_change: 0,
    emissions_change: 0,
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSimulate = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await scenarioAPI.simulate(params)
      setResult(response.data)
    } catch (err) {
      console.error('Simulation failed:', err)
      setError(err.message || 'Failed to run scenario simulation')
    } finally {
      setLoading(false)
    }
  }

  const sliders = [
    { key: 'carbon_price_change', label: 'Carbon Price', min: -50, max: 50, unit: '%' },
    { key: 'renewable_share_change', label: 'Renewable Energy Share', min: -20, max: 20, unit: '%' },
    { key: 'gdp_growth_change', label: 'GDP Growth', min: -5, max: 5, unit: '%' },
    { key: 'emissions_change', label: 'CO₂ Emissions', min: -30, max: 30, unit: '%' },
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
            {sliders.map((slider) => (
              <div key={slider.key} className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-sm font-medium text-ivory-secondary">{slider.label}</label>
                  <span className={`text-lg font-bold ${
                    params[slider.key] > 0 ? 'text-positive' :
                    params[slider.key] < 0 ? 'text-negative' :
                    'text-ivory-muted'
                  }`}>
                    {params[slider.key] > 0 ? '+' : ''}{params[slider.key]}{slider.unit}
                  </span>
                </div>
                <input
                  type="range"
                  min={slider.min}
                  max={slider.max}
                  step={1}
                  value={params[slider.key]}
                  onChange={(e) => setParams({ ...params, [slider.key]: Number(e.target.value) })}
                  className="w-full h-2 bg-carbon-dark-secondary rounded-lg appearance-none cursor-pointer accent-scenario-accent"
                />
                <div className="flex justify-between text-xs text-ivory-muted">
                  <span>{slider.min}{slider.unit}</span>
                  <span>0{slider.unit}</span>
                  <span>{slider.max}{slider.unit}</span>
                </div>
              </div>
            ))}
            <button 
              onClick={handleSimulate}
              disabled={loading}
              className="w-full btn-primary text-lg py-4"
            >
              {loading ? 'Simulating...' : 'Run Simulation'}
            </button>
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
