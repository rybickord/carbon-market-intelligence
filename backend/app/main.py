"""
FastAPI backend for Carbon Market Intelligence platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import health, market, countries, trading, scenario

app = FastAPI(
    title="Carbon Market Intelligence API",
    description="API for carbon market analysis, forecasting, and scenario simulation",
    version="1.0.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(market.router, prefix="/api/market", tags=["Market"])
app.include_router(countries.router, prefix="/api/countries", tags=["Countries"])
app.include_router(trading.router, prefix="/api/trading", tags=["Trading"])
app.include_router(scenario.router, prefix="/api/scenario", tags=["Scenario"])


@app.get("/")
async def root():
    return {
        "message": "Carbon Market Intelligence API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }
