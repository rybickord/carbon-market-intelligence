# Frontend Installation Instructions

## Prerequisites

- Node.js 18+ installed
- Backend API running on port 8000

## Installation Steps

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

This will install:
- react & react-dom
- vite
- tailwindcss, postcss, autoprefixer
- plotly.js & react-plotly.js
- axios

3. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file if you need to customize the API URL:

```
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### "Cannot find module" errors
Run `npm install` to ensure all dependencies are installed.

### API connection errors
Ensure the backend is running on port 8000. Start it with:
```bash
cd ..
python run_backend.py
```

### Port 3000 already in use
The port can be changed in `vite.config.js` under `server.port`.
