import { useState, useEffect } from 'react'
import { countriesAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'
import ErrorMessage from '../ErrorMessage'

export default function CountriesSection() {
  const [countries, setCountries] = useState([])
  const [riskRanking, setRiskRanking] = useState([])
  const [oppRanking, setOppRanking] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [view, setView] = useState('risk') // 'risk' or 'opportunity'

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [riskRes, oppRes] = await Promise.all([
        countriesAPI.getRiskRanking(20),
        countriesAPI.getOpportunityRanking(20)
      ])
      setRiskRanking(riskRes.data)
      setOppRanking(oppRes.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load country data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading country intelligence..." />
  if (error) return <ErrorMessage message={error} />

  const displayData = view === 'risk' ? riskRanking : oppRanking

  return (
    <section id="countries" className="py-24 bg-gradient-to-b from-charcoal-900 to-charcoal-950">
      <div className="section-container space-y-16">
        {/* Section Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-forest-500/10 border border-forest-500/20 rounded-full mb-6">
            <span className="text-sm text-forest-400 font-medium">Country Intelligence</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Regional Risk & Opportunity
          </h2>
          <p className="text-xl text-gray-400">
            Country-level carbon market intelligence analyzing risk factors and opportunity 
            scores based on emissions, renewable energy adoption, GDP, and carbon pricing.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-center">
          <div className="inline-flex bg-charcoal-800 rounded-lg p-1">
            <button
              onClick={() => setView('risk')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                view === 'risk'
                  ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Risk Ranking
            </button>
            <button
              onClick={() => setView('opportunity')}
              className={`px-6 py-3 rounded-lg font-medium transition-all ${
                view === 'opportunity'
                  ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Opportunity Ranking
            </button>
          </div>
        </div>

        {/* Rankings Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {displayData.slice(0, 12).map((country, idx) => {
            const score = view === 'risk' ? country.risk_score : country.opportunity_score
            const scoreColor = view === 'risk'
              ? score >= 70 ? 'red' : score >= 40 ? 'yellow' : 'green'
              : score >= 70 ? 'green' : score >= 40 ? 'yellow' : 'red'

            return (
              <div key={idx} className="card-hover p-6 space-y-3">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="text-sm text-gray-500 mb-1">#{idx + 1}</div>
                    <div className="text-lg font-bold text-white truncate">{country.country}</div>
                  </div>
                  <div className={`text-2xl font-bold ${
                    scoreColor === 'green' ? 'text-green-400' :
                    scoreColor === 'yellow' ? 'text-yellow-400' :
                    'text-red-400'
                  }`}>
                    {score.toFixed(1)}
                  </div>
                </div>
                <div className="w-full bg-charcoal-800 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      scoreColor === 'green' ? 'bg-green-500' :
                      scoreColor === 'yellow' ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${score}%` }}
                  ></div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Scoring Explanation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card p-8 space-y-4 border-l-4 border-red-500">
            <h3 className="text-2xl font-bold text-white">Risk Score Factors</h3>
            <div className="space-y-2 text-gray-300">
              <div className="flex items-start space-x-2">
                <span className="text-red-400 mt-1">•</span>
                <span>High absolute CO₂ emissions per capita</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-red-400 mt-1">•</span>
                <span>Low renewable electricity share</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-red-400 mt-1">•</span>
                <span>Weak carbon pricing mechanisms</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-red-400 mt-1">•</span>
                <span>Exposure to regulatory changes</span>
              </div>
            </div>
          </div>

          <div className="card p-8 space-y-4 border-l-4 border-green-500">
            <h3 className="text-2xl font-bold text-white">Opportunity Score Factors</h3>
            <div className="space-y-2 text-gray-300">
              <div className="flex items-start space-x-2">
                <span className="text-green-400 mt-1">•</span>
                <span>Strong renewable energy growth potential</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-green-400 mt-1">•</span>
                <span>Economic development trajectory</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-green-400 mt-1">•</span>
                <span>Established carbon pricing infrastructure</span>
              </div>
              <div className="flex items-start space-x-2">
                <span className="text-green-400 mt-1">•</span>
                <span>Policy support for decarbonization</span>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-charcoal-800/50 rounded-xl p-6 border border-charcoal-700">
          <p className="text-gray-400 text-sm leading-relaxed">
            <span className="font-semibold text-white">Scoring Methodology:</span> Risk and opportunity 
            scores are calculated using a transparent, data-driven approach that combines emissions data, 
            renewable energy metrics, carbon pricing information, and economic indicators. Scores range 
            from 0-100, with higher risk scores indicating greater carbon transition challenges and higher 
            opportunity scores indicating stronger market potential.
          </p>
        </div>
      </div>
    </section>
  )
}
