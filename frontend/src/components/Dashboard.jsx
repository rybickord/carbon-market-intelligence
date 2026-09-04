import { useState, useEffect } from 'react'
import MarketOverview from './MarketOverview'
import MarketCharts from './MarketCharts'
import CountryIntelligence from './CountryIntelligence'
import TradingPredictor from './TradingPredictor'
import ScenarioSimulator from './ScenarioSimulator'
import LoadingSpinner from './LoadingSpinner'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState('market')

  const tabs = [
    { id: 'market', label: 'Global Market', icon: '🌍' },
    { id: 'countries', label: 'Country Intelligence', icon: '🗺️' },
    { id: 'trading', label: 'Trading Prediction', icon: '💼' },
    { id: 'scenario', label: 'Scenario Simulator', icon: '🎯' },
  ]

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md p-2">
        <div className="flex space-x-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 px-4 py-3 rounded-md font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-emerald-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'market' && (
          <div className="space-y-6">
            <MarketOverview />
            <MarketCharts />
          </div>
        )}
        
        {activeTab === 'countries' && <CountryIntelligence />}
        
        {activeTab === 'trading' && <TradingPredictor />}
        
        {activeTab === 'scenario' && <ScenarioSimulator />}
      </div>
    </div>
  )
}
