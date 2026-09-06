import { useState, useEffect } from 'react'
import { countriesAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'
import ErrorMessage from '../ErrorMessage'

export default function CountriesSection() {
  const [riskRanking, setRiskRanking] = useState([])
  const [oppRanking, setOppRanking] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [view, setView] = useState('risk')

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
    <section id="countries" className="py-10 sm:py-16 lg:py-24 bg-carbon-dark">
      <div className="section-container space-y-10 sm:space-y-16">

        {/* Section Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-positive/10 border border-positive/20 rounded-full mb-4 sm:mb-6">
            <span className="text-xs sm:text-sm text-positive font-medium uppercase tracking-wider">Country Intelligence</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-ivory mb-3 sm:mb-4">
            Regional Risk &amp; Opportunity
          </h2>
          <p className="text-base sm:text-xl text-ivory-secondary">
            Country-level carbon market intelligence analyzing risk factors and opportunity
            scores based on emissions, renewable energy adoption, GDP, and carbon pricing.
          </p>
        </div>

        {/* View Toggle */}
        <div className="flex items-center justify-center">
          <div className="inline-flex bg-carbon-surface rounded-lg p-1 w-full sm:w-auto">
            <button
              onClick={() => setView('risk')}
              className={`flex-1 sm:flex-none px-4 sm:px-6 py-2.5 sm:py-3 rounded-lg text-sm font-medium transition-all ${
                view === 'risk'
                  ? 'bg-negative/20 text-negative border border-negative/30'
                  : 'text-ivory-secondary hover:text-ivory'
              }`}
            >
              Risk Ranking
            </button>
            <button
              onClick={() => setView('opportunity')}
              className={`flex-1 sm:flex-none px-4 sm:px-6 py-2.5 sm:py-3 rounded-lg text-sm font-medium transition-all ${
                view === 'opportunity'
                  ? 'bg-positive/20 text-positive border border-positive/30'
                  : 'text-ivory-secondary hover:text-ivory'
              }`}
            >
              Opportunity Ranking
            </button>
          </div>
        </div>

        {/* Rankings Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3 sm:gap-4">
          {displayData.slice(0, 12).map((country, idx) => {
            const score = view === 'risk' ? country.risk_score : country.opportunity_score
            const scoreColor = view === 'risk'
              ? score >= 70 ? 'negative' : score >= 40 ? 'warning' : 'positive'
              : score >= 70 ? 'positive' : score >= 40 ? 'warning' : 'negative'

            return (
              <div key={idx} className="glass-card-hover p-4 sm:p-5 space-y-3">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-ivory-muted mb-1">#{idx + 1}</div>
                    <div className="text-base font-bold text-ivory truncate">{country.country}</div>
                  </div>
                  <div className={`text-xl font-bold flex-shrink-0 ${
                    scoreColor === 'positive' ? 'text-positive' :
                    scoreColor === 'warning'  ? 'text-warning'  :
                    'text-negative'
                  }`}>
                    {score.toFixed(1)}
                  </div>
                </div>
                <div className="w-full bg-carbon-surface rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full transition-all duration-500 ${
                      scoreColor === 'positive' ? 'bg-positive' :
                      scoreColor === 'warning'  ? 'bg-warning'  :
                      'bg-negative'
                    }`}
                    style={{ width: `${Math.min(score, 100)}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>

        {/* Scoring Explanation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-8">
          <div className="glass-card p-5 sm:p-8 space-y-4 border-l-4 border-negative">
            <h3 className="text-xl sm:text-2xl font-bold text-ivory">Risk Score Factors</h3>
            <div className="space-y-2 text-ivory-secondary">
              {[
                'High absolute CO₂ emissions per capita',
                'Low renewable electricity share',
                'Weak carbon pricing mechanisms',
                'Exposure to regulatory changes',
              ].map((item, i) => (
                <div key={i} className="flex items-start space-x-2">
                  <span className="text-negative mt-0.5 flex-shrink-0">•</span>
                  <span className="text-sm sm:text-base">{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass-card p-5 sm:p-8 space-y-4 border-l-4 border-positive">
            <h3 className="text-xl sm:text-2xl font-bold text-ivory">Opportunity Score Factors</h3>
            <div className="space-y-2 text-ivory-secondary">
              {[
                'Strong renewable energy growth potential',
                'Economic development trajectory',
                'Established carbon pricing infrastructure',
                'Policy support for decarbonization',
              ].map((item, i) => (
                <div key={i} className="flex items-start space-x-2">
                  <span className="text-positive mt-0.5 flex-shrink-0">•</span>
                  <span className="text-sm sm:text-base">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Methodology Note */}
        <div className="glass-surface rounded-xl p-4 sm:p-6 border border-white/8">
          <p className="text-ivory-secondary text-sm leading-relaxed">
            <span className="font-semibold text-ivory">Scoring Methodology:</span> Risk and opportunity
            scores are calculated using a transparent, data-driven approach that combines emissions data,
            renewable energy metrics, carbon pricing information, and economic indicators. Scores range
            from 0–100, with higher risk scores indicating greater carbon transition challenges and higher
            opportunity scores indicating stronger market potential.
          </p>
        </div>

      </div>
    </section>
  )
}
