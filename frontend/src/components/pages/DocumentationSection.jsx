export default function DocumentationSection() {
  return (
    <section id="documentation" className="py-24 bg-carbon">
      <div className="section-container space-y-16">
        {/* Section Header */}
        <div className="max-w-4xl">
          <div className="inline-flex items-center space-x-2 px-4 py-2 bg-cyan/10 border border-cyan/20 rounded-full mb-6">
            <span className="text-sm text-cyan font-medium uppercase tracking-wider">Documentation</span>
          </div>
          <h2 className="text-4xl md:text-5xl font-bold text-ivory mb-4">
            Platform Documentation
          </h2>
          <p className="text-xl text-ivory-secondary">
            Comprehensive guide to using the Carbon Market Intelligence platform for market analysis, 
            forecasting, and scenario modeling.
          </p>
        </div>

        {/* Documentation Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Getting Started */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-8 space-y-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-cyan/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-cyan" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-ivory">Getting Started</h3>
            </div>
            <div className="space-y-4 text-ivory-secondary">
              <div>
                <h4 className="font-semibold text-ivory mb-2">Platform Overview</h4>
                <p className="text-sm">Navigate through market overview, forecasts, country analysis, and trading predictions.</p>
              </div>
              <div>
                <h4 className="font-semibold text-ivory mb-2">Data Sources</h4>
                <p className="text-sm">Historical carbon market data from 2005-2024, emissions data, and renewable energy statistics.</p>
              </div>
            </div>
          </div>

          {/* API Reference */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-8 space-y-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-royal/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-royal" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-ivory">API Reference</h3>
            </div>
            <div className="space-y-4 text-ivory-secondary">
              <div>
                <h4 className="font-semibold text-ivory mb-2">Market Endpoints</h4>
                <ul className="text-sm space-y-1">
                  <li><code className="text-cyan">/api/market/overview</code></li>
                  <li><code className="text-cyan">/api/market/history</code></li>
                  <li><code className="text-cyan">/api/market/forecast</code></li>
                  <li><code className="text-cyan">/api/market/metrics</code></li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-ivory mb-2">Country & Trading</h4>
                <ul className="text-sm space-y-1">
                  <li><code className="text-cyan">/api/countries</code></li>
                  <li><code className="text-cyan">/api/countries/risk</code></li>
                  <li><code className="text-cyan">/api/countries/opportunity</code></li>
                  <li><code className="text-cyan">/api/trading/model</code></li>
                  <li><code className="text-cyan">/api/trading/predict</code></li>
                  <li><code className="text-cyan">/api/scenario/simulate</code></li>
                </ul>
              </div>
            </div>
          </div>

          {/* Models & Data */}
          <div className="bg-carbon-elevated rounded-xl border border-white/16 p-8 space-y-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gold/20 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-gold" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
                  <path d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-ivory">Models & Analysis</h3>
            </div>
            <div className="space-y-4 text-ivory-secondary">
              <div>
                <h4 className="font-semibold text-ivory mb-2">Machine Learning</h4>
                <p className="text-sm">Naive last-value and XGBoost models for market forecasting, logistic regression for trading predictions.</p>
              </div>
              <div>
                <h4 className="font-semibold text-ivory mb-2">Risk Assessment</h4>
                <p className="text-sm">Country-level risk and opportunity scoring based on emissions, renewable share, and economic factors.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="bg-carbon-elevated rounded-xl border border-white/16 p-8">
          <h3 className="text-2xl font-bold text-ivory mb-6">Technical Architecture</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-ivory">Frontend Stack</h4>
              <ul className="space-y-2 text-ivory-secondary">
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan rounded-full"></div>
                  <span>React 18 with Vite for fast development</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan rounded-full"></div>
                  <span>Tailwind CSS for responsive design</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan rounded-full"></div>
                  <span>Plotly.js for interactive data visualization</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-cyan rounded-full"></div>
                  <span>Axios for API communication</span>
                </li>
              </ul>
            </div>
            <div className="space-y-4">
              <h4 className="text-lg font-semibold text-ivory">Backend Stack</h4>
              <ul className="space-y-2 text-ivory-secondary">
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-royal rounded-full"></div>
                  <span>FastAPI for high-performance APIs</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-royal rounded-full"></div>
                  <span>PostgreSQL with Neon for data storage</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-royal rounded-full"></div>
                  <span>Scikit-learn for machine learning models</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-royal rounded-full"></div>
                  <span>Pandas for data processing and analysis</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* Support Section */}
        <div className="text-center bg-carbon-surface rounded-xl border border-white/16 p-8">
          <h3 className="text-2xl font-bold text-ivory mb-4">Need Help?</h3>
          <p className="text-ivory-secondary mb-6 max-w-2xl mx-auto">
            This is a demonstration platform showcasing AI-powered carbon market intelligence capabilities. 
            For technical questions about the implementation, refer to the project repository.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <div className="bg-carbon-elevated border border-white/16 rounded-lg px-6 py-4">
              <div className="text-sm text-ivory-muted uppercase tracking-wider mb-1">Platform Status</div>
              <div className="text-ivory font-semibold">Active Development</div>
            </div>
            <div className="bg-carbon-elevated border border-white/16 rounded-lg px-6 py-4">
              <div className="text-sm text-ivory-muted uppercase tracking-wider mb-1">API Version</div>
              <div className="text-ivory font-semibold">v1.0.0</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}