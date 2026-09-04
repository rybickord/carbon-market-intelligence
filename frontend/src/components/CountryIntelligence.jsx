import { useState, useEffect } from 'react'
import { countriesAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function CountryIntelligence() {
  const [view, setView] = useState('risk')
  const [riskData, setRiskData] = useState([])
  const [opportunityData, setOpportunityData] = useState([])
  const [selectedCountry, setSelectedCountry] = useState(null)
  const [countryDetail, setCountryDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [riskResp, oppResp] = await Promise.all([
        countriesAPI.getRiskRanking(50),
        countriesAPI.getOpportunityRanking(50)
      ])
      setRiskData(riskResp.data)
      setOpportunityData(oppResp.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load country data')
    } finally {
      setLoading(false)
    }
  }

  const fetchCountryDetail = async (countryName) => {
    try {
      const response = await countriesAPI.getDetail(countryName)
      setCountryDetail(response.data)
      setSelectedCountry(countryName)
    } catch (err) {
      alert(`Failed to load details for ${countryName}`)
    }
  }

  if (loading) return <LoadingSpinner message="Loading country intelligence..." />
  if (error) return <ErrorMessage message={error} />

  const currentData = view === 'risk' ? riskData : opportunityData
  const filteredData = searchTerm
    ? currentData.filter(d => d.country.toLowerCase().includes(searchTerm.toLowerCase()))
    : currentData

  const getRiskColor = (score) => {
    if (score >= 70) return 'text-red-600 bg-red-50'
    if (score >= 50) return 'text-orange-600 bg-orange-50'
    return 'text-yellow-600 bg-yellow-50'
  }

  const getOppColor = (score) => {
    if (score >= 70) return 'text-green-600 bg-green-50'
    if (score >= 50) return 'text-blue-600 bg-blue-50'
    return 'text-gray-600 bg-gray-50'
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Country Analysis</h2>
          <div className="flex space-x-2">
            <button
              onClick={() => setView('risk')}
              className={`px-4 py-2 rounded-md font-medium ${
                view === 'risk'
                  ? 'bg-red-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🚨 Risk Ranking
            </button>
            <button
              onClick={() => setView('opportunity')}
              className={`px-4 py-2 rounded-md font-medium ${
                view === 'opportunity'
                  ? 'bg-green-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              🌱 Opportunity Ranking
            </button>
          </div>
        </div>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Search countries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
          />
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredData.slice(0, 20).map((item) => (
                <tr key={item.rank} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{item.rank}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {item.country}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      view === 'risk' ? getRiskColor(item.risk_score || item.opportunity_score) : getOppColor(item.opportunity_score || item.risk_score)
                    }`}>
                      {(item.risk_score || item.opportunity_score).toFixed(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                    {item.risk_category || item.opportunity_category}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => fetchCountryDetail(item.country)}
                      className="text-emerald-600 hover:text-emerald-800 font-medium"
                    >
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {countryDetail && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-gray-900">{countryDetail.country} - Detailed View</h3>
            <button
              onClick={() => setCountryDetail(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕ Close
            </button>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Year</div>
              <div className="text-lg font-semibold">{countryDetail.year}</div>
            </div>
            {countryDetail.co2 && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">CO₂ Emissions</div>
                <div className="text-lg font-semibold">{countryDetail.co2.toFixed(2)} MtCO₂</div>
              </div>
            )}
            {countryDetail.per_capita_co2 && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Per Capita CO₂</div>
                <div className="text-lg font-semibold">{countryDetail.per_capita_co2.toFixed(2)} t</div>
              </div>
            )}
            {countryDetail.renewable_share !== null && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">Renewable Share</div>
                <div className="text-lg font-semibold">{countryDetail.renewable_share.toFixed(1)}%</div>
              </div>
            )}
            {countryDetail.gdp_growth !== null && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <div className="text-sm text-gray-600">GDP Growth</div>
                <div className="text-lg font-semibold">{countryDetail.gdp_growth.toFixed(1)}%</div>
              </div>
            )}
            {countryDetail.risk_score && (
              <div className="p-4 bg-red-50 rounded-lg">
                <div className="text-sm text-red-600">Risk Score</div>
                <div className="text-lg font-semibold text-red-700">{countryDetail.risk_score.toFixed(1)}</div>
                <div className="text-xs text-red-600">{countryDetail.risk_category}</div>
              </div>
            )}
            {countryDetail.opportunity_score && (
              <div className="p-4 bg-green-50 rounded-lg">
                <div className="text-sm text-green-600">Opportunity Score</div>
                <div className="text-lg font-semibold text-green-700">{countryDetail.opportunity_score.toFixed(1)}</div>
                <div className="text-xs text-green-600">{countryDetail.opportunity_category}</div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
