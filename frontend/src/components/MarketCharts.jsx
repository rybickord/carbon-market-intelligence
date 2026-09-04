import { useState, useEffect } from 'react'
import Plot from 'react-plotly.js'
import { marketAPI } from '../services/api'
import LoadingSpinner from './LoadingSpinner'
import ErrorMessage from './ErrorMessage'

export default function MarketCharts() {
  const [forecast, setForecast] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await marketAPI.getForecast()
      setForecast(response.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load market data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading market charts..." />
  if (error) return <ErrorMessage message={error} />
  if (!forecast) return null

  const historical = forecast.filter(d => d.series === 'historical')
  const forecastData = forecast.filter(d => d.series === 'forecast')

  // Market Value Chart
  const valueTrace1 = {
    x: historical.map(d => d.year),
    y: historical.map(d => d.market_value),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Historical',
    line: { color: '#059669', width: 3 },
    marker: { size: 6 }
  }

  const valueTrace2 = {
    x: forecastData.map(d => d.year),
    y: forecastData.map(d => d.market_value),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Forecast',
    line: { color: '#f59e0b', width: 3, dash: 'dash' },
    marker: { size: 6 }
  }

  // Market Volume Chart
  const volumeTrace1 = {
    x: historical.map(d => d.year),
    y: historical.map(d => d.market_volume),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Historical',
    line: { color: '#0284c7', width: 3 },
    marker: { size: 6 }
  }

  const volumeTrace2 = {
    x: forecastData.map(d => d.year),
    y: forecastData.map(d => d.market_volume),
    type: 'scatter',
    mode: 'lines+markers',
    name: 'Forecast',
    line: { color: '#f59e0b', width: 3, dash: 'dash' },
    marker: { size: 6 }
  }

  const layout = {
    autosize: true,
    margin: { l: 60, r: 30, t: 40, b: 60 },
    paper_bgcolor: '#111C19',
    plot_bgcolor: '#0D1715',
    font: { family: 'system-ui, -apple-system, sans-serif', color: '#F4F1E8' },
    hovermode: 'x unified',
  }

  return (
    <div className="space-y-6">
      <div className="bg-[#111C19] rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-[#F4F1E8] mb-4">
          Market Value Trend & Forecast
        </h2>
        <Plot
          data={[valueTrace1, valueTrace2]}
          layout={{
            ...layout,
            xaxis: { title: 'Year', gridcolor: '#183B2C', titlefont: { color: '#F4F1E8' }, tickfont: { color: '#AEB5B1' } },
            yaxis: { title: 'Market Value ($ Million)', gridcolor: '#183B2C', titlefont: { color: '#F4F1E8' }, tickfont: { color: '#AEB5B1' } },
            showlegend: true,
            legend: { x: 0.02, y: 0.98, font: { color: '#F4F1E8' } }
          }}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%', height: '400px' }}
        />
      </div>

      <div className="bg-[#111C19] rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-[#F4F1E8] mb-4">
          Market Volume Trend & Forecast
        </h2>
        <Plot
          data={[volumeTrace1, volumeTrace2]}
          layout={{
            ...layout,
            xaxis: { title: 'Year', gridcolor: '#183B2C', titlefont: { color: '#F4F1E8' }, tickfont: { color: '#AEB5B1' } },
            yaxis: { title: 'Market Volume (Million tCO₂)', gridcolor: '#183B2C', titlefont: { color: '#F4F1E8' }, tickfont: { color: '#AEB5B1' } },
            showlegend: true,
            legend: { x: 0.02, y: 0.98, font: { color: '#F4F1E8' } }
          }}
          config={{ responsive: true, displayModeBar: false }}
          style={{ width: '100%', height: '400px' }}
        />
      </div>
    </div>
  )
}
