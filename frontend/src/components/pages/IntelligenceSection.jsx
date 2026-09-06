export default function IntelligenceSection() {
  const drivers = [
    {
      title: 'Carbon Pricing Mechanisms',
      description: 'Global carbon pricing systems including emissions trading schemes (ETS) and carbon taxes drive market demand.',
      icon: (
        <svg className="w-8 h-8" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'mint',
    },
    {
      title: 'Corporate Net-Zero Commitments',
      description: 'Increasing corporate sustainability pledges and science-based targets create sustained demand for carbon credits.',
      icon: (
        <svg className="w-8 h-8" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
      ),
      color: 'data-blue',
    },
    {
      title: 'Renewable Energy Transition',
      description: 'Growth in renewable energy capacity and declining fossil fuel dependency influence carbon market dynamics.',
      icon: (
        <svg className="w-8 h-8" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      color: 'mint',
    },
    {
      title: 'Regulatory Policy',
      description: 'Government climate policies, Paris Agreement targets, and international cooperation shape market structure.',
      icon: (
        <svg className="w-8 h-8" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      ),
      color: 'data-blue',
    },
    {
      title: 'Economic Growth Patterns',
      description: 'Global GDP growth, industrial activity, and economic development affect emissions levels and offset demand.',
      icon: (
        <svg className="w-8 h-8" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
      ),
      color: 'gold',
    },
    {
      title: 'Market Infrastructure',
      description: 'Development of carbon registries, verification standards, and trading platforms enhances market efficiency.',
      icon: (
        <svg className="w-8 h-8" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1h-4a1 1 0 01-1-1v-3z" />
        </svg>
      ),
      color: 'data-blue',
    },
  ]

  return (
    <section id="intelligence" className="py-10 sm:py-16 lg:py-24 bg-carbon-dark-secondary">
      <div className="section-container space-y-10 sm:space-y-16">
        {/* Section Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-gold/10 border border-gold/20 rounded-full mb-4 sm:mb-6">
            <span className="text-xs sm:text-sm text-gold font-medium uppercase tracking-wider">Market Intelligence</span>
          </div>
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-bold text-ivory mb-3 sm:mb-4">
            Understanding Market Drivers
          </h2>
          <p className="text-base sm:text-xl text-ivory-secondary">
            The carbon credit market is shaped by interconnected forces spanning policy, economics, 
            technology, and corporate strategy. Our intelligence platform tracks these key drivers 
            to explain market behavior and inform predictions.
          </p>
        </div>

        {/* Drivers Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {drivers.map((driver, idx) => (
            <div key={idx} className="bg-carbon-dark-elevated rounded-xl border border-ivory-muted/10 p-5 sm:p-6 space-y-3 sm:space-y-4 hover:border-ivory-muted/20 transition-all duration-200 group">
              <div className={`w-12 h-12 rounded-lg flex items-center justify-center transition-colors ${
                driver.color === 'mint' ? 'bg-mint/10 text-mint' :
                driver.color === 'gold' ? 'bg-gold/10 text-gold' :
                'bg-data-blue/10 text-data-blue'
              }`}>
                {driver.icon}
              </div>
              <div>
                <h3 className="text-lg font-semibold text-ivory mb-2 group-hover:text-mint transition-colors">
                  {driver.title}
                </h3>
                <p className="text-ivory-secondary leading-relaxed">
                  {driver.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Key Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          <div className="bg-carbon-dark-elevated rounded-xl border border-mint/20 border-l-2 border-l-mint p-5 sm:p-8 space-y-4">
            <h3 className="text-xl sm:text-2xl font-bold text-ivory">Why Markets Move</h3>
            <div className="space-y-3 text-ivory-secondary leading-relaxed">
              <p>
                Carbon market dynamics reflect the intersection of environmental urgency, 
                regulatory frameworks, and economic incentives. Price movements correlate 
                with policy announcements, corporate commitments, and macroeconomic conditions.
              </p>
              <p>
                Our models incorporate carbon pricing data, energy market indicators, emissions 
                trends, renewable energy adoption, and GDP growth to provide comprehensive market 
                intelligence.
              </p>
            </div>
          </div>

          <div className="bg-carbon-dark-elevated rounded-xl border border-data-blue/20 border-l-2 border-l-data-blue p-5 sm:p-8 space-y-4">
            <h3 className="text-xl sm:text-2xl font-bold text-ivory">Data-Driven Insights</h3>
            <div className="space-y-3 text-ivory-secondary leading-relaxed">
              <p>
                Our platform analyzes historical relationships between market drivers and carbon 
                credit transactions to identify patterns and forecast future behavior.
              </p>
              <p>
                By tracking global CO₂ emissions, renewable energy capacity, energy pricing, 
                and economic indicators across 180+ countries, we deliver actionable intelligence 
                for market participants and policymakers.
              </p>
            </div>
          </div>
        </div>

        {/* Data Sources Note */}
        <div className="bg-carbon-dark-elevated rounded-xl p-6 border border-ivory-muted/10">
          <div className="flex items-start space-x-4">
            <svg className="w-6 h-6 text-mint flex-shrink-0 mt-1" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              <path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h4 className="text-ivory font-semibold mb-2">Comprehensive Data Integration</h4>
              <p className="text-ivory-secondary text-sm leading-relaxed">
                Our intelligence layer integrates data from multiple authoritative sources including 
                global emissions databases, renewable energy statistics, carbon market transaction 
                records, and economic indicators to provide a complete market picture.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
