import { useState, useEffect } from 'react'
import { tradingAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'

export default function TradingSection() {
  const [modelInfo, setModelInfo] = useState(null)
  const [formData, setFormData] = useState({
    industry_type: 'Energy',
    fuel_type: 'Natural Gas',
    verification_status: 'Verified',
    energy_demand_mwh: 1500,
    emission_produced_tco2: 800,
    emission_allowance_tco2: 750,
    carbon_price_usd_per_t: 25,
    compliance_cost_usd: 10000,
  })
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchModelInfo()
  }, [])

  const fetchModelInfo = async () => {
    try {
      const response = await tradingAPI.getModelInfo()
      setModelInfo(response.data)
    } catch (err) {
      console.error('Failed to load model info:', err)
      setError('Failed to load model information')
    }
  }

  const handlePredict = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await tradingAPI.predict(formData)
      setPrediction(response.data)
    } catch (err) {
      console.error('Prediction failed:', err)
      setError(err.response?.data?.detail || 'Prediction failed')
    } finally {
      setLoading(false)
    }
  }

  // Dropdown options based on the actual dataset
  const industryOptions = ['Cement', 'Energy', 'Manufacturing', 'Steel']
  const fuelOptions = ['Coal', 'Mixed Fuel', 'Natural Gas', 'Renewable']
  const verificationOptions = ['Verified', 'Disputed']

  return (
    <section id="trading" className="py-10 sm:py-16 lg:py-24 bg-carbon">
      <div className="section-container space-y-10 sm:space-y-16">
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-cyan/10 border border-cyan/20 rounded-full mb-4 sm:mb-6">
            <span className="text-xs sm:text-sm text-cyan font-medium uppercase tracking-wider">Trading Intelligence</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-ivory mb-3 sm:mb-4">
            Trading Action Prediction
          </h2>
          <p className="text-base sm:text-xl text-ivory-secondary">
            ML-powered prediction for carbon credit trading actions. Enter your company's 
            emissions profile and market conditions to predict whether to Buy or Sell carbon credits.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          <div className="card p-5 sm:p-8 space-y-4 sm:space-y-6">
            <h3 className="text-xl sm:text-2xl font-bold text-ivory">Company Profile</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-ivory-secondary mb-2">
                  Industry Type
                </label>
                <select
                  value={formData.industry_type}
                  onChange={(e) => setFormData({ ...formData, industry_type: e.target.value })}
                  className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none appearance-none"
                >
                  {industryOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-ivory-secondary mb-2">
                  Fuel Type
                </label>
                <select
                  value={formData.fuel_type}
                  onChange={(e) => setFormData({ ...formData, fuel_type: e.target.value })}
                  className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none appearance-none"
                >
                  {fuelOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-ivory-secondary mb-2">
                  Verification Status
                </label>
                <select
                  value={formData.verification_status}
                  onChange={(e) => setFormData({ ...formData, verification_status: e.target.value })}
                  className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none appearance-none"
                >
                  {verificationOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-ivory-secondary mb-2">
                    Energy Demand (MWh)
                  </label>
                  <input
                    type="number"
                    value={formData.energy_demand_mwh}
                    onChange={(e) => setFormData({ ...formData, energy_demand_mwh: Number(e.target.value) })}
                    className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none"
                    min="0"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-ivory-secondary mb-2">
                    Carbon Price (USD/t)
                  </label>
                  <input
                    type="number"
                    value={formData.carbon_price_usd_per_t}
                    onChange={(e) => setFormData({ ...formData, carbon_price_usd_per_t: Number(e.target.value) })}
                    className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none"
                    min="0"
                    step="0.01"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-ivory-secondary mb-2">
                    Emissions Produced (tCO₂)
                  </label>
                  <input
                    type="number"
                    value={formData.emission_produced_tco2}
                    onChange={(e) => setFormData({ ...formData, emission_produced_tco2: Number(e.target.value) })}
                    className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none"
                    min="0"
                    step="0.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-ivory-secondary mb-2">
                    Emissions Allowance (tCO₂)
                  </label>
                  <input
                    type="number"
                    value={formData.emission_allowance_tco2}
                    onChange={(e) => setFormData({ ...formData, emission_allowance_tco2: Number(e.target.value) })}
                    className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none"
                    min="0"
                    step="0.1"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-ivory-secondary mb-2">
                  Compliance Cost (USD)
                </label>
                <input
                  type="number"
                  value={formData.compliance_cost_usd}
                  onChange={(e) => setFormData({ ...formData, compliance_cost_usd: Number(e.target.value) })}
                  className="w-full bg-carbon-surface text-ivory px-4 py-3 rounded-lg border border-white/16 focus:border-cyan focus:outline-none"
                  min="0"
                  step="0.01"
                />
              </div>
            </div>
            
            {error && (
              <div className="p-4 bg-negative/20 border border-negative/30 rounded-lg text-negative text-sm">
                {error}
              </div>
            )}
            
            <button 
              onClick={handlePredict}
              disabled={loading}
              className="w-full btn-primary text-lg py-4"
            >
              {loading ? 'Analyzing...' : 'Predict Trading Action'}
            </button>
          </div>

          <div className="card p-5 sm:p-8 space-y-4 sm:space-y-6">
            <h3 className="text-xl sm:text-2xl font-bold text-ivory">Prediction Result</h3>
            {loading ? (
              <LoadingSpinner message="Analyzing company profile..." />
            ) : prediction ? (
              <div className="space-y-6">
                <div className={`p-6 rounded-lg ${
                  prediction.predicted_action === 'Buy' 
                    ? 'bg-positive/20 border border-positive/30' 
                    : 'bg-negative/20 border border-negative/30'
                }`}>
                  <div className="text-sm text-ivory-secondary mb-2">Recommended Action</div>
                  <div className={`text-3xl sm:text-4xl font-bold ${
                    prediction.predicted_action === 'Buy' ? 'text-positive' : 'text-negative'
                  }`}>
                    {prediction.predicted_action.toUpperCase()}
                  </div>
                  <div className="mt-3 space-y-1">
                    <div className="text-sm text-ivory-muted">
                      Confidence: <span className="text-ivory font-medium">{prediction.confidence}</span>
                    </div>
                    <div className="text-sm text-ivory-muted">
                      Probability: <span className="text-ivory font-medium">{(prediction.probability * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                </div>

                {prediction.input_summary && (
                  <div className="p-6 bg-carbon-surface rounded-lg space-y-3">
                    <div className="text-sm text-ivory-muted mb-3">Analysis Summary</div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                      <div className="flex justify-between">
                        <span className="text-ivory-secondary">Industry:</span>
                        <span className="text-ivory">{prediction.input_summary.industry}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ivory-secondary">Fuel:</span>
                        <span className="text-ivory">{prediction.input_summary.fuel}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ivory-secondary">Allowance Gap:</span>
                        <span className={`${prediction.input_summary.deficit_surplus === 'Deficit' ? 'text-negative' : 'text-positive'}`}>
                          {prediction.input_summary.allowance_gap_tco2} tCO₂
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ivory-secondary">Carbon Price:</span>
                        <span className="text-ivory">${prediction.input_summary.carbon_price}/t</span>
                      </div>
                    </div>
                    <div className="text-xs text-ivory-muted mt-3 pt-3 border-t border-white/16">
                      {prediction.input_summary.deficit_surplus === 'Deficit' 
                        ? 'Company produces more emissions than allowance - may need to buy credits'
                        : 'Company has surplus allowance - may consider selling credits'
                      }
                    </div>
                  </div>
                )}

                {modelInfo && (
                  <div className="p-6 bg-carbon-surface rounded-lg space-y-2">
                    <div className="text-sm text-ivory-muted">Model Performance</div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                        <span className="text-ivory-secondary">Accuracy</span>
                        <span className="text-ivory font-medium">
                          {(modelInfo.accuracy * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-ivory-secondary">F1 Score</span>
                        <span className="text-ivory font-medium">
                          {(modelInfo.f1_score * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-ivory-muted mt-2">
                      Model: {prediction.model_used}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-ivory-muted">
                <div className="text-center space-y-2">
                  <svg className="w-16 h-16 mx-auto text-ivory-muted" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                    <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <p>Enter company details to predict trading action</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}
