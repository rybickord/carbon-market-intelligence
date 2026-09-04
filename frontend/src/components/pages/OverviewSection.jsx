import { useState, useEffect } from 'react'
import { marketAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'
import ErrorMessage from '../ErrorMessage'
import Plot from 'react-plotly.js'

export default function OverviewSection() {
  const [overview, setOverview] = useState(null)
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [overviewRes, historyRes] = await Promise.all([
        marketAPI.getOverview(),
        marketAPI.getHistory()
      ])
      setOverview(overviewRes.data)
      setHistory(historyRes.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load market data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading market overview..." />
  if (error) return <ErrorMessage message={error} />
  if (!overview || !history || !Array.isArray(history) || history.length === 0) return null

  // Prepare chart data
  const years = history.map(d => d.year)
  const values = history.map(d => d.market_value)
  const volumes = history.map(d => d.market_volume)

  return (
    <section id="overview" className="py-24 bg-carbon">
      <div className="section-container space-y-16">
        {/* Section Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-cyan/10 border border-cyan/20 rounded-full mb-6">
            <span className="text-sm text-cyan font-medium uppercase tracking-wider">Market Overview</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-ivory mb-4">
            Global Carbon Market Snapshot
          </h2>
          <p className="text-xl text-ivory-secondary">
            Current state of the voluntary carbon credit market with historical trends and key performance indicators.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Market Value Card */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-6 space-y-3 hover:border-white/28 transition-all duration-200">
            <div className="flex items-center justify-between">
              <div className="text-xs text-ivory-muted uppercase tracking-wider">Market Value</div>
              <div className="w-2 h-2 rounded-full bg-cyan"></div>
            </div>
            <div className="text-4xl font-bold text-ivory">
              ${overview.latest_value.toFixed(0)}M
            </div>
            {overview.value_growth_pct !== null && (
              <div className={`flex items-center space-x-1 text-sm font-semibold ${
                overview.value_growth_pct >= 0 ? 'text-positive' : 'text-negative'
              }`}>
                <svg className={`w-4 h-4 ${overview.value_growth_pct < 0 && 'transform rotate-180'}`} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                <span>{Math.abs(overview.value_growth_pct).toFixed(1)}% YoY</span>
              </div>
            )}
            <div className="text-xs text-ivory-muted">Year: {overview.latest_year}</div>
          </div>

          {/* Market Volume Card */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-6 space-y-3 hover:border-white/28 transition-all duration-200">
            <div className="flex items-center justify-between">
              <div className="text-xs text-ivory-muted uppercase tracking-wider">Market Volume</div>
              <div className="w-2 h-2 rounded-full bg-royal"></div>
            </div>
            <div className="text-4xl font-bold text-ivory">
              {overview.latest_volume.toFixed(0)}M
            </div>
            {overview.volume_growth_pct !== null && (
              <div className={`flex items-center space-x-1 text-sm font-semibold ${
                overview.volume_growth_pct >= 0 ? 'text-positive' : 'text-negative'
              }`}>
                <svg className={`w-4 h-4 ${overview.volume_growth_pct < 0 && 'transform rotate-180'}`} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                <span>{Math.abs(overview.volume_growth_pct).toFixed(1)}% YoY</span>
              </div>
            )}
            <div className="text-xs text-ivory-muted">Million tCO₂</div>
          </div>

          {/* Data Points Card */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-6 space-y-3 hover:border-white/28 transition-all duration-200">
            <div className="flex items-center justify-between">
              <div className="text-xs text-ivory-muted uppercase tracking-wider">Data Points</div>
              <div className="w-2 h-2 rounded-full bg-gold"></div>
            </div>
            <div className="text-4xl font-bold text-ivory">
              {history.length}
            </div>
            <div className="text-sm text-ivory-secondary">Years of historical data</div>
            <div className="text-xs text-ivory-muted">{years[0]} – {years[years.length - 1]}</div>
          </div>

          {/* Forecast Card */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-6 space-y-3 hover:border-white/28 transition-all duration-200">
            <div className="flex items-center justify-between">
              <div className="text-xs text-ivory-muted uppercase tracking-wider">Forecast</div>
              <div className="w-2 h-2 rounded-full bg-cyan"></div>
            </div>
            <div className="text-4xl font-bold text-ivory">
              Active
            </div>
            <div className="text-sm text-ivory-secondary">ML-powered predictions available</div>
            <div className="text-xs text-ivory-muted">Updated: {overview.latest_year}</div>
          </div>
        </div>

        {/* Historical Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-6">
            <h3 className="text-lg font-semibold text-ivory mb-4">Market Value Trend</h3>
            <Plot
              data={[
                {
                  x: years,
                  y: values,
                  type: 'scatter',
                  mode: 'lines+markers',
                  marker: { color: '#00C8C8', size: 7 },
                  line: { color: '#00C8C8', width: 3 },
                  fill: 'tozeroy',
                  fillcolor: 'rgba(0, 200, 200, 0.08)',
                  name: 'Historical'
                }
              ]}
              layout={{
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#F4F1E8', family: 'Inter', size: 12 },
                margin: { t: 20, r: 20, b: 50, l: 60 },
                xaxis: { 
                  gridcolor: 'rgba(244, 241, 232, 0.1)',
                  showgrid: true,
                  title: { text: 'Year', font: { color: '#AEB5B1' } },
                  tickfont: { color: '#AEB5B1' }
                },
                yaxis: { 
                  gridcolor: 'rgba(244, 241, 232, 0.1)',
                  showgrid: true,
                  title: { text: 'Market Value (Million USD)', font: { color: '#AEB5B1' } },
                  tickfont: { color: '#AEB5B1' }
                },
                hovermode: 'closest',
                showlegend: false
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '300px' }}
            />
          </div>

          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-6">
            <h3 className="text-lg font-semibold text-ivory mb-4">Market Volume Trend</h3>
            <Plot
              data={[
                {
                  x: years,
                  y: volumes,
                  type: 'scatter',
                  mode: 'lines+markers',
                  marker: { color: '#1A3FD6', size: 7 },
                  line: { color: '#1A3FD6', width: 3 },
                  fill: 'tozeroy',
                  fillcolor: 'rgba(26, 63, 214, 0.08)',
                  name: 'Historical'
                }
              ]}
              layout={{
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#F4F1E8', family: 'Inter', size: 12 },
                margin: { t: 20, r: 20, b: 50, l: 60 },
                xaxis: { 
                  gridcolor: 'rgba(244, 241, 232, 0.1)',
                  showgrid: true,
                  title: { text: 'Year', font: { color: '#AEB5B1' } },
                  tickfont: { color: '#AEB5B1' }
                },
                yaxis: { 
                  gridcolor: 'rgba(244, 241, 232, 0.1)',
                  showgrid: true,
                  title: { text: 'Market Volume (Million tCO₂)', font: { color: '#AEB5B1' } },
                  tickfont: { color: '#AEB5B1' }
                },
                hovermode: 'closest',
                showlegend: false
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '300px' }}
            />
          </div>
        </div>
      </div>
    </section>
  )
}
