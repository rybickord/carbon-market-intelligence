# Carbon Market Intelligence - Frontend

React-based dashboard for carbon market analysis and prediction.

## Features

- **Global Market Overview**: Real-time market statistics and KPIs
- **Market Charts**: Historical trends and forecasts with Plotly
- **Country Intelligence**: Risk and opportunity rankings with detailed views
- **Trading Predictor**: ML-powered buy/sell recommendations
- **Scenario Simulator**: Interactive what-if analysis

## Tech Stack

- React 18
- Vite
- Tailwind CSS
- Plotly.js for charts
- Axios for API calls

## Setup

```bash
# Install dependencies
npm install

# Start development server (requires backend running on port 8000)
npm run dev

# Build for production
npm run build
```

## Development

The app runs on `http://localhost:3000` and proxies API requests to the FastAPI backend on port 8000.

Make sure the backend is running before starting the frontend.
