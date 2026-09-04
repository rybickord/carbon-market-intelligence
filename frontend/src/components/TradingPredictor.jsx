import { useState, useEffect } from 'react'
import { tradingAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function TradingPredictor() {
  const [modelInfo, setModelInfo] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(true)
  const [predicting, setPredicting] = useState(false)
  const [error, setError] = useState(null)

  const [formData, setFormData] = useState({
    industry_type: 'Energy',
    fuel_type: 'Coal',
    verification_status: 'Verified',
    energy_demand_mwh: 5000,
    emission_produced_tco2: 3000,
    emission_allowance_tco2: 2500,
    carbon_price_usd_per_t: 50,
    compliance_cost_usd: 10000
  })

  useEffect(() => {
    fetchModelInfo()
  }, [])

  const fetchModelInfo = async () => {
    try {
      setLoading(true)
      const response = await tradingAPI.getModelInfo()
      setModelInfo(response.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load model info')
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: ['industry_type', 'fuel_type', 'verification_status'].includes(name) 
        ? value 
        : parseFloat(value) || 0
    }))
  }

  const handlePredict = async (e) => {
    e.preventDefault()
    try {
      setPredicting(true)
      setPrediction(null)
      const response = await tradingAPI.predict(formData)
      setPrediction(response.data)
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Prediction failed')
    } finally {
      setPredicting(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading trading predictor..." />
  if (error) return <ErrorMessage message={error} />

  return (
    <div className="space-y-6">
      {/* Model Info */}
      {modelInfo && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Trading Model Information</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-3 bg-blue-50 rounded-lg">
              <div className="text-sm text-blue-600">Model</div>
              <div className="text-lg font-semibold text-blue-900">{modelInfo.model_name}</div>
            </div>
            <div className="p-3 bg-green-50 rounded-lg">
              <div className="text-sm text-green-600">F1 Score</div>
              <div className="text-lg font-semibold text-green-900">{(modelInfo.f1_score * 100).toFixed(1)}%</div>
            </div>
            <div className="p-3 bg-purple-50 rounded-lg">
              <div className="text-sm text-purple-600">Accuracy</div>
              <div className="text-lg font-semibold text-purple-900">{(modelInfo.accuracy * 100).toFixed(1)}%</div>
            </div>
            <div className="p-3 bg-orange-50 rounded-lg">
              <div className="text-sm text-orange-600">ROC-AUC</div>
              <div className="text-lg font-semibold text-orange-900">{(modelInfo.roc_auc * 100).toFixed(1)}%</div>
            </div>
          </div>
          <p className="mt-4 text-sm text-gray-600">
            <strong>Target:</strong> {modelInfo.target_interpretation}
          </p>
        </div>
      )}

      {/* Prediction Form */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Company Trading Prediction</h2>
        <form onSubmit={handlePredict} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Industry Type</label>
              <select
                name="industry_type"
                value={formData.industry_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
              >
                <option value="Cement">Cement</option>
                <option value="Energy">Energy</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Steel">Steel</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Fuel Type</label>
              <select
                name="fuel_type"
                value={formData.fuel_type}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
              >
                <option value="Coal">Coal</option>
                <option value="Mixed Fuel">Mixed Fuel</option>
                <option value="Natural Gas">Natural Gas</option>
                <option value="Renewable">Renewable</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Verification Status</label>
              <select
                name="verification_status"
                value={formData.verification_status}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
              >
                <option value="Verified">Verified</option>
                <option value="Disputed">Disputed</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Energy Demand (MWh)</label>
              <input
                type="number"
                name="energy_demand_mwh"
                value={formData.energy_demand_mwh}
                onChange={handleInputChange}
                step="100"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Emission Produced (tCO₂)</label>
              <input
                type="number"
                name="emission_produced_tco2"
                value={formData.emission_produced_tco2}
                onChange={handleInputChange}
                step="100"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Emission Allowance (tCO₂)</label>
              <input
                type="number"
                name="emission_allowance_tco2"
                value={formData.emission_allowance_tco2}
                onChange={handleInputChange}
                step="100"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Carbon Price (USD/t)</label>
              <input
                type="number"
                name="carbon_price_usd_per_t"
                value={formData.carbon_price_usd_per_t}
                onChange={handleInputChange}
                step="1"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Compliance Cost (USD)</label>
              <input
                type="number"
                name="compliance_cost_usd"
                value={formData.compliance_cost_usd}
                onChange={handleInputChange}
                step="100"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={predicting}
            className="w-full bg-emerald-600 text-white py-3 px-6 rounded-md hover:bg-emerald-700 disabled:bg-gray-400 font-medium transition-colors"
          >
            {predicting ? 'Predicting...' : 'Predict Trading Action'}
          </button>
        </form>
      </div>

      {/* Prediction Result */}
      {prediction && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Prediction Result</h3>
          <div className="flex items-center justify-between p-6 bg-gradient-to-r from-emerald-50 to-cyan-50 rounded-lg border-2 border-emerald-200">
            <div>
              <div className="text-sm text-gray-600 mb-1">Recommended Action</div>
              <div className={`text-4xl font-bold ${
                prediction.predicted_action === 'Buy' ? 'text-green-600' : 'text-orange-600'
              }`}>
                {prediction.predicted_action === 'Buy' ? '📈 BUY' : '📉 SELL'}
              </div>
              <div className="text-sm text-gray-600 mt-2">
                Confidence: <span className="font-semibold">{prediction.confidence}</span>
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-600 mb-1">Probability</div>
              <div className="text-3xl font-bold text-gray-900">
                {(prediction.probability * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-gray-500 mt-2">
                Model: {prediction.model_used}
              </div>
            </div>
          </div>

          <div className="mt-4 p-4 bg-gray-50 rounded-lg">
            <div className="text-sm font-semibold text-gray-700 mb-2">Input Summary</div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>Industry: <span className="font-medium">{prediction.input_summary.industry}</span></div>
              <div>Fuel: <span className="font-medium">{prediction.input_summary.fuel}</span></div>
              <div>Allowance Gap: <span className="font-medium">{prediction.input_summary.allowance_gap_tco2} tCO₂</span></div>
              <div>Status: <span className="font-medium">{prediction.input_summary.deficit_surplus}</span></div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
