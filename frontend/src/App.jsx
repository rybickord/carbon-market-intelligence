import { useState, useEffect } from 'react'
import Navigation from './components/Navigation'
import Hero from './components/Hero'
import OverviewSection from './components/pages/OverviewSection'
import IntelligenceSection from './components/pages/IntelligenceSection'
import ForecastSection from './components/pages/ForecastSection'
import CountriesSection from './components/pages/CountriesSection'
import ScenarioSection from './components/pages/ScenarioSection'
import TradingSection from './components/pages/TradingSection'
import DocumentationSection from './components/pages/DocumentationSection'

function App() {
  const [activeSection, setActiveSection] = useState('overview')

  // Track which section is currently visible
  useEffect(() => {
    let ticking = false
    
    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          const sections = ['overview', 'intelligence', 'forecast', 'countries', 'scenario', 'trading', 'documentation']
          const scrollPosition = window.scrollY + 100 // Offset for navbar height

          for (let i = sections.length - 1; i >= 0; i--) {
            const element = document.getElementById(sections[i])
            if (element && element.offsetTop <= scrollPosition) {
              setActiveSection(sections[i])
              break
            }
          }
          ticking = false
        })
        ticking = true
      }
    }

    window.addEventListener('scroll', handleScroll, { passive: true })
    handleScroll() // Check initial position
    
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const handleNavigate = (sectionId) => {
    const element = document.getElementById(sectionId)
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }

  return (
    <div className="overflow-safe bg-carbon text-ivory min-h-screen">
      <Navigation activeSection={activeSection} onNavigate={handleNavigate} />
      
      <main className="overflow-safe">
        <Hero onExplore={handleNavigate} />
        
        {/* No section-padding wrapper — each section manages its own vertical spacing */}
        <OverviewSection />
        <IntelligenceSection />
        <ForecastSection />
        <CountriesSection />
        <ScenarioSection />
        <TradingSection />
        <DocumentationSection />
      </main>

      {/* Enhanced Footer with glass effect */}
      <footer className="glass-surface border-t border-white/8 mt-8 sm:mt-16">
        <div className="section-container py-8 sm:py-12">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4 interactive">
                <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-cyan to-royal rounded-lg flex items-center justify-center shadow-lg transition-all duration-200">
                  <span className="text-ivory font-bold text-sm sm:text-xl">C</span>
                </div>
                <div>
                  <h3 className="text-ivory font-bold text-sm sm:text-base">Carbon Intelligence</h3>
                  <p className="text-xs text-ivory-muted">Market Prediction Platform</p>
                </div>
              </div>
              <p className="text-ivory-secondary text-sm mobile-body">
                AI-powered carbon market intelligence delivering predictive insights for 
                the global carbon credit market.
              </p>
            </div>
            <div>
              <h4 className="text-ivory font-semibold mb-3 text-sm sm:text-base">Platform</h4>
              <ul className="space-y-2 text-sm text-ivory-secondary">
                <li><button onClick={() => handleNavigate('overview')} className="interactive hover:text-cyan">Market Overview</button></li>
                <li><button onClick={() => handleNavigate('intelligence')} className="interactive hover:text-cyan">Intelligence</button></li>
                <li><button onClick={() => handleNavigate('forecast')} className="interactive hover:text-cyan">Forecast</button></li>
                <li><button onClick={() => handleNavigate('countries')} className="interactive hover:text-cyan">Countries</button></li>
                <li><button onClick={() => handleNavigate('documentation')} className="interactive hover:text-cyan">Documentation</button></li>
              </ul>
            </div>
            <div className="sm:col-span-2 lg:col-span-1">
              <h4 className="text-ivory font-semibold mb-3 text-sm sm:text-base">About</h4>
              <p className="text-ivory-secondary text-sm mobile-body">
                Built with React, FastAPI, PostgreSQL, and ML models. 
                Powered by open carbon market data and global emissions databases.
              </p>
            </div>
          </div>
          <div className="border-t border-white/8 mt-6 sm:mt-8 pt-6 sm:pt-8 text-center text-xs sm:text-sm text-ivory-muted">
            © 2026 Carbon Market Intelligence Platform. Educational project.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
