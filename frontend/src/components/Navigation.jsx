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
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ease-out ${
        isScrolled 
          ? 'glass-surface backdrop-blur-xl border-b border-white/12 shadow-2xl' 
          : 'bg-transparent'
      }`}
    >
      <div className="section-container">
        {/*
          Navbar row heights:
            mobile  (<640px):  h-20  = 80px
            sm (640–1023px):   h-24  = 96px
            lg (1024px+):      h-28  = 112px  (desktop, unchanged)
        */}
        <div className="flex items-center justify-between h-20 sm:h-24 lg:h-28">
          {/* Logo / Brand with micro-interaction */}
          <div className="flex items-center interactive">
            {/* Responsive logo container — see .logo-container in index.css */}
            <div className="logo-container flex-shrink-0 overflow-hidden">
              <img
                src="/Logo/Print_Transparent.svg"
                alt="Carbon Intelligence"
                className="logo-img block"
              />
            </div>
            {/* Divider + tagline — desktop only */}
            <div className="hidden lg:flex items-center ml-3">
              <div className="w-px h-10 bg-white/20 mr-3" />
              <p className="text-xs text-ivory-muted leading-none whitespace-nowrap">Market Prediction Platform</p>
            </div>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`nav-link px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                  activeSection === item.id
                    ? 'nav-link active text-cyan bg-cyan/10'
                    : 'text-ivory-secondary hover:text-ivory hover:bg-white/5'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden interactive p-2 rounded-lg text-ivory-secondary hover:text-ivory hover:bg-white/5"
          >
            <div className="space-y-1">
              <div className={`w-5 h-0.5 bg-current transition-transform duration-200 ${mobileMenuOpen ? 'rotate-45 translate-y-1.5' : ''}`} />
              <div className={`w-5 h-0.5 bg-current transition-opacity duration-200 ${mobileMenuOpen ? 'opacity-0' : ''}`} />
              <div className={`w-5 h-0.5 bg-current transition-transform duration-200 ${mobileMenuOpen ? '-rotate-45 -translate-y-1.5' : ''}`} />
            </div>
          </button>
        </div>

        {/* Mobile Navigation */}
        <div className={`lg:hidden transition-all duration-300 ease-out ${
          mobileMenuOpen 
            ? 'max-h-96 opacity-100 pb-4' 
            : 'max-h-0 opacity-0 overflow-hidden'
        }`}>
          <div className="glass-card mt-2 p-2 space-y-1">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => {
                  onNavigate(item.id)
                  setMobileMenuOpen(false)
                }}
                className={`w-full text-left px-4 py-3 text-sm font-medium rounded-lg transition-all duration-200 ${
                  activeSection === item.id
                    ? 'text-cyan bg-cyan/10 border-l-2 border-cyan'
                    : 'text-ivory-secondary hover:text-ivory hover:bg-white/5'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </nav>
  )
}
