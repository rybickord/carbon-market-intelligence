import { useState, useEffect } from 'react'

export default function Navigation({ activeSection, onNavigate }) {
  const [isScrolled, setIsScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const navItems = [
    { id: 'overview', label: 'Overview' },
    { id: 'intelligence', label: 'Market Intelligence' },
    { id: 'forecast', label: 'Forecast' },
    { id: 'countries', label: 'Countries' },
    { id: 'scenario', label: 'Scenario Lab' },
    { id: 'trading', label: 'Trading' },
    { id: 'documentation', label: 'Documentation' },
  ]

  return (
    <nav 
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled 
          ? 'bg-carbon/95 backdrop-blur-xl border-b border-white/16 shadow-2xl' 
          : 'bg-transparent'
      }`}
    >
      <div className="section-container">
        <div className="flex items-center justify-between h-20">
          {/* Logo / Brand */}
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan to-royal rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-ivory font-bold text-xl">C</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-ivory">Carbon Intelligence</h1>
              <p className="text-xs text-ivory-muted hidden sm:block">Market Prediction Platform</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-white/20 ${
                  activeSection === item.id
                    ? 'bg-cyan/15 text-cyan border border-cyan/30'
                    : 'text-ivory-secondary hover:text-ivory hover:bg-carbon-surface'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden p-2 text-ivory-secondary hover:text-ivory focus:outline-none focus:ring-2 focus:ring-white/20 rounded-lg"
          >
            <svg className="w-6 h-6" fill="none" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" viewBox="0 0 24 24" stroke="currentColor">
              {mobileMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-carbon-surface/98 backdrop-blur-xl border-t border-white/16">
          <div className="section-container py-4 space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onNavigate(item.id)
                  setMobileMenuOpen(false)
                }}
                className={`w-full text-left px-4 py-3 rounded-lg text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-white/20 ${
                  activeSection === item.id
                    ? 'bg-cyan/15 text-cyan'
                    : 'text-ivory-secondary hover:bg-carbon-elevated hover:text-ivory'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </nav>
  )
}
