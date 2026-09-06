import { useState, useEffect } from 'react'
import { marketAPI } from '../../services/api'
import LoadingSpinner from '../LoadingSpinner'
import ErrorMessage from '../ErrorMessage'
import Plot from 'react-plotly.js'

export default function ForecastSection() {
  const [forecast, setForecast] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      setLoading(true)
      const [forecastRes, metricsRes] = await Promise.all([
        marketAPI.getForecast(),
        marketAPI.getMetrics()
      ])
      setForecast(forecastRes.data)
      setMetrics(metricsRes.data)
      setError(null)
    } catch (err) {
      setError(err.message || 'Failed to load forecast data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading forecasts..." />
  if (error) return <ErrorMessage message={error} />
  if (!forecast || !metrics) return null

  // Separate historical and forecast data
  const historical = forecast.filter(d => d.series === 'historical')
  const predictions = forecast.filter(d => d.series === 'forecast')

  // Get model info
  const valueModel = metrics.Market_Value?.selected_model || 'N/A'
  const volumeModel = metrics.Market_Volume?.selected_model || 'N/A'

  return (
    <section id="forecast" className="py-10 sm:py-16 lg:py-24 bg-royal">
      <div className="section-container space-y-10 sm:space-y-16">
        {/* Section Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-white/10 border border-white/20 rounded-full mb-4 sm:mb-6">
            <span className="text-xs sm:text-sm text-ivory font-medium uppercase tracking-wider">Predictive Analytics</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-ivory mb-3 sm:mb-4">
            Market Forecast
          </h2>
          <p className="text-base sm:text-xl text-ivory-secondary">
            ML-powered predictions for global carbon market value and volume based on 
            historical trends, market drivers, and validated forecast models.
          </p>
        </div>

        {/* Model Info Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
          <div className="bg-white/5 rounded-xl border border-white/16 p-6 space-y-4 hover:border-white/28 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-ivory">Market Value Forecast</h3>
              <div className="w-2 h-2 rounded-full bg-cyan"></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-ivory-muted">Selected Model</span>
                <span className="text-ivory font-medium">{valueModel}</span>
              </div>
              {metrics.Market_Value?.walk_forward_metrics?.[valueModel] && (
                <>
                  <div className="flex justify-between text-sm">
                    <span className="text-ivory-muted">RMSE</span>
                    <span className="text-ivory font-medium">
                      {metrics.Market_Value.walk_forward_metrics[valueModel].RMSE.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ivory-muted">MAE</span>
                    <span className="text-ivory font-medium">
                      {metrics.Market_Value.walk_forward_metrics[valueModel].MAE.toFixed(2)}
                    </span>
                  </div>
                </>
              )}
            </div>
            <div className="pt-3 border-t border-white/16">
              <p className="text-xs text-ivory-muted">
                Model selected via walk-forward validation for optimal forecast accuracy
              </p>
            </div>
          </div>

          <div className="bg-white/5 rounded-xl border border-white/16 p-6 space-y-4 hover:border-white/28 transition-all duration-200">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-ivory">Market Volume Forecast</h3>
              <div className="w-2 h-2 rounded-full bg-cyan"></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-ivory-muted">Selected Model</span>
                <span className="text-ivory font-medium">{volumeModel}</span>
              </div>
              {metrics.Market_Volume?.walk_forward_metrics?.[volumeModel] && (
                <>
                  <div className="flex justify-between text-sm">
                    <span className="text-ivory-muted">RMSE</span>
                    <span className="text-ivory font-medium">
                      {metrics.Market_Volume.walk_forward_metrics[volumeModel].RMSE.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-ivory-muted">MAE</span>
                    <span className="text-ivory font-medium">
                      {metrics.Market_Volume.walk_forward_metrics[volumeModel].MAE.toFixed(2)}
                    </span>
                  </div>
                </>
              )}
            </div>
            <div className="pt-3 border-t border-white/16">
              <p className="text-xs text-ivory-muted">
                Best-performing model determined through rigorous evaluation
              </p>
            </div>
          </div>
        </div>

        {/* Forecast Charts */}
        <div className="space-y-6">
          <div className="bg-white/5 rounded-xl border border-white/16 p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-xl font-semibold text-ivory">Market Value: Historical &amp; Forecast</h3>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-ivory rounded-full"></div>
                  <span className="text-ivory-secondary">Historical</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-cyan rounded-full"></div>
                  <span className="text-ivory-secondary">Forecast</span>
                </div>
              </div>
            </div>
            <Plot
              data={[
                {
                  x: historical.map(d => d.year),
                  y: historical.map(d => d.market_value),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Historical',
                  marker: { color: '#F4F1E8', size: 6 },
                  line: { color: '#F4F1E8', width: 2 },
                },
                {
                  x: predictions.map(d => d.year),
                  y: predictions.map(d => d.market_value),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Forecast',
                  marker: { color: '#00C8C8', size: 6 },
                  line: { color: '#00C8C8', width: 2, dash: 'dash' },
                },
              ]}
              layout={{
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#AEB5B1', family: 'Inter', size: 11 },
                margin: { t: 20, r: 10, b: 45, l: 50 },
                xaxis: { 
                  gridcolor: 'rgba(255,255,255,0.08)',
                  showgrid: true,
                  title: { text: 'Year', font: { color: '#AEB5B1', size: 10 } }
                },
                yaxis: { 
                  gridcolor: 'rgba(255,255,255,0.08)',
                  showgrid: true,
                  title: { text: 'Value (M USD)', font: { color: '#AEB5B1', size: 10 } }
                },
                hovermode: 'x unified',
                showlegend: true,
                legend: { 
                  x: 0, y: 1.12, orientation: 'h',
                  bgcolor: 'transparent',
                  font: { color: '#AEB5B1', size: 11 }
                },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '280px' }}
            />
          </div>

          <div className="bg-white/5 rounded-xl border border-white/16 p-4 sm:p-6">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 mb-4 sm:mb-6">
              <h3 className="text-base sm:text-xl font-semibold text-ivory">Market Volume: Historical &amp; Forecast</h3>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-ivory rounded-full"></div>
                  <span className="text-ivory-secondary">Historical</span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-cyan rounded-full"></div>
                  <span className="text-ivory-secondary">Forecast</span>
                </div>
              </div>
            </div>
            <Plot
              data={[
                {
                  x: historical.map(d => d.year),
                  y: historical.map(d => d.market_volume),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Historical',
                  marker: { color: '#F4F1E8', size: 6 },
                  line: { color: '#F4F1E8', width: 2 },
                },
                {
                  x: predictions.map(d => d.year),
                  y: predictions.map(d => d.market_volume),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Forecast',
                  marker: { color: '#00C8C8', size: 6 },
                  line: { color: '#00C8C8', width: 2, dash: 'dash' },
                },
              ]}
              layout={{
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                font: { color: '#AEB5B1', family: 'Inter', size: 11 },
                margin: { t: 20, r: 10, b: 45, l: 50 },
                xaxis: { 
                  gridcolor: 'rgba(255,255,255,0.08)',
                  showgrid: true,
                  title: { text: 'Year', font: { color: '#AEB5B1', size: 10 } }
                },
                yaxis: { 
                  gridcolor: 'rgba(255,255,255,0.08)',
                  showgrid: true,
                  title: { text: 'Volume (M tCO₂)', font: { color: '#AEB5B1', size: 10 } }
                },
                hovermode: 'x unified',
                showlegend: true,
                legend: { 
                  x: 0, y: 1.12, orientation: 'h',
                  bgcolor: 'transparent',
                  font: { color: '#AEB5B1', size: 11 }
                },
              }}
              config={{ displayModeBar: false, responsive: true }}
              style={{ width: '100%', height: '280px' }}
            />
          </div>
        </div>

        {/* Methodology Note */}
        <div className="bg-white/5 rounded-xl p-6 border border-white/16">
          <div className="flex items-start space-x-4">
            <svg className="w-6 h-6 text-cyan flex-shrink-0 mt-1" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
            </svg>
            <div>
              <h4 className="text-ivory font-semibold mb-2">Forecast Methodology</h4>
              <p className="text-ivory-secondary text-sm leading-relaxed">
                Forecasts are generated using walk-forward validation to select optimal models. 
                Multiple candidate models are evaluated on historical data, and the best-performing 
                model is selected based on prediction accuracy metrics (RMSE, MAE). This approach 
                ensures robust, validated forecasts rather than overfitted predictions.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
