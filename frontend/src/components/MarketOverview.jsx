import { useState, useEffect } from 'react'
import { marketAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function MarketOverview() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await marketAPI.getOverview()
      setData(response.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load market overview')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading market overview..." />
  if (error) return <ErrorMessage message={error} />
  if (!data) return null

  const stats = [
    {
      label: 'Latest Market Value',
      value: `$${data.latest_value.toFixed(0)}M`,
      change: data.value_growth_pct,
      year: data.latest_year,
      icon: '💰',
      color: 'emerald'
    },
    {
      label: 'Latest Market Volume',
      value: `${data.latest_volume.toFixed(0)}M tCO₂`,
      change: data.volume_growth_pct,
      year: data.latest_year,
      icon: '📊',
      color: 'cyan'
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {stats.map((stat, idx) => (
        <div key={idx} className={`bg-[#111C19] rounded-lg shadow-md p-6 border-l-4 border-[#00C8C8]`}>
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center">
                <span className="text-2xl mr-2">{stat.icon}</span>
                <p className="text-[#AEB5B1] font-medium">{stat.label}</p>
              </div>
              <p className="text-3xl font-bold text-[#F4F1E8] mt-2">{stat.value}</p>
              <p className="text-sm text-[#78827E] mt-1">Year: {stat.year}</p>
            </div>
            {stat.change !== null && (
              <div className={`text-right ${stat.change >= 0 ? 'text-[#00C8C8]' : 'text-[#FF6B6B]'}`}>
                <div className="text-sm font-medium">YoY Change</div>
                <div className="text-xl font-bold">
                  {stat.change >= 0 ? '+' : ''}{stat.change.toFixed(1)}%
                </div>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
