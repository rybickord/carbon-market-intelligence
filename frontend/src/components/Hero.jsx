export default function Hero({ onExplore }) {
  return (
    <div className="relative min-h-screen flex items-center overflow-hidden">
      {/* Hero Background Image */}
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: 'url(/carbon-forest-hero.jpg)' }}
      >
        {/* Subtle blur and dark overlay for text readability */}
        <div className="absolute inset-0 backdrop-blur-[1px] bg-gradient-to-b from-carbon/80 via-carbon/60 to-carbon/90"></div>
      </div>

      {/* Hero Content */}
      <div className="section-container relative z-10 pt-20 sm:pt-24 pb-12 sm:pb-16 w-full">
        <div className="max-w-4xl">
          {/* Eyebrow */}
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 sm:px-4 sm:py-2 bg-carbon/90 backdrop-blur-md border border-white/20 rounded-full mb-4 sm:mb-6">
            <div className="w-1.5 h-1.5 bg-cyan rounded-full"></div>
            <span className="text-xs sm:text-sm text-ivory font-medium uppercase tracking-widest">
              Global Carbon Market Intelligence
            </span>
          </div>
          
          {/* Main Heading */}
          <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.1] tracking-tight mb-4 sm:mb-6">
            <span className="block text-ivory">Understand the</span>
            <span className="block text-ivory">Carbon Market.</span>
            <span className="block text-ivory mt-1 sm:mt-2">
              Predict What <span className="text-cyan">Comes Next</span>.
            </span>
          </h1>

          {/* Supporting Text */}
          <p className="text-base sm:text-lg md:text-xl text-ivory-secondary leading-relaxed max-w-3xl mb-8 sm:mb-10">
            AI-powered market intelligence, forecasting, risk analysis and scenario 
            modeling for the global carbon credit market.
          </p>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <button 
              onClick={() => onExplore('forecast')}
              className="group px-6 sm:px-8 py-3 sm:py-4 bg-cyan hover:bg-cyan-light text-carbon font-semibold rounded-lg transition-all duration-200 text-base sm:text-lg shadow-lg"
            >
              View Forecasts
            </button>
            <button 
              onClick={() => onExplore('intelligence')}
              className="px-6 sm:px-8 py-3 sm:py-4 bg-transparent hover:bg-carbon-surface text-ivory font-semibold rounded-lg border border-white/28 hover:border-white/40 transition-all duration-200 text-base sm:text-lg"
            >
              Explore Market Intelligence
            </button>
          </div>
        </div>
      </div>

      {/* Scroll Indicator */}
      <div className="absolute bottom-8 left-1/2 transform -translate-x-1/2 animate-bounce z-20">
        <svg className="w-6 h-6 text-ivory-muted" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
          <path d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </div>
  )
}
