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
    const handleScroll = () => {
      const sections = ['overview', 'intelligence', 'forecast', 'countries', 'scenario', 'trading', 'documentation']
      const scrollPosition = window.scrollY + 100 // Offset for navbar height

      for (let i = sections.length - 1; i >= 0; i--) {
        const element = document.getElementById(sections[i])
        if (element && element.offsetTop <= scrollPosition) {
          setActiveSection(sections[i])
          break
        }
      }
    }

    window.addEventListener('scroll', handleScroll)
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
    <div className="min-h-screen" style={{ backgroundColor: '#020C09' }}>
      <Navigation activeSection={activeSection} onNavigate={handleNavigate} />
      
      <main>
        <Hero onExplore={handleNavigate} />
        <OverviewSection />
        <IntelligenceSection />
        <ForecastSection />
        <CountriesSection />
        <ScenarioSection />
        <TradingSection />
        <DocumentationSection />
      </main>

      {/* Footer */}
      <footer className="bg-carbon-surface border-t border-white/16 py-12">
        <div className="section-container">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-cyan to-royal rounded-lg flex items-center justify-center shadow-lg">
                  <span className="text-ivory font-bold text-xl">C</span>
                </div>
                <div>
                  <h3 className="text-ivory font-bold">Carbon Intelligence</h3>
                  <p className="text-xs text-ivory-muted">Market Prediction Platform</p>
                </div>
              </div>
              <p className="text-ivory-secondary text-sm">
                AI-powered carbon market intelligence delivering predictive insights for 
                the global carbon credit market.
              </p>
            </div>
            <div>
              <h4 className="text-ivory font-semibold mb-3">Platform</h4>
              <ul className="space-y-2 text-sm text-ivory-secondary">
                <li><button onClick={() => handleNavigate('overview')} className="hover:text-cyan transition-colors">Market Overview</button></li>
                <li><button onClick={() => handleNavigate('intelligence')} className="hover:text-cyan transition-colors">Intelligence</button></li>
                <li><button onClick={() => handleNavigate('forecast')} className="hover:text-cyan transition-colors">Forecast</button></li>
                <li><button onClick={() => handleNavigate('countries')} className="hover:text-cyan transition-colors">Countries</button></li>
                <li><button onClick={() => handleNavigate('documentation')} className="hover:text-cyan transition-colors">Documentation</button></li>
              </ul>
            </div>
            <div>
              <h4 className="text-ivory font-semibold mb-3">About</h4>
              <p className="text-ivory-secondary text-sm">
                Built with React, FastAPI, PostgreSQL, and ML models. 
                Powered by open carbon market data and global emissions databases.
              </p>
            </div>
          </div>
          <div className="border-t border-white/16 mt-8 pt-8 text-center text-sm text-ivory-muted">
            © 2026 Carbon Market Intelligence Platform. Educational project.
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
