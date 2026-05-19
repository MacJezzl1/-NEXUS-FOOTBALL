"""
⚽ NEXUS FOOTBALL — Main FastAPI Application
World Cup 2026 Intelligence Platform

Three integrated systems:
1. PitchOracle — Match outcome predictions
2. StatPulse — Player performance ratings
3. MatchMind AI — AI-powered match intelligence
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

# ━━━━━ INITIALIZE LOGGING ━━━━━
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ━━━━━ LIFECYCLE EVENTS ━━━━━
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle:
    - Startup: Initialize connections, load models, warm up caches
    - Shutdown: Close connections gracefully
    """
    logger.info("🚀 Starting NEXUS FOOTBALL...")
    
    # ━━━━━ STARTUP ━━━━━
    # Initialize database connections
    # Load ML models into memory
    # Warm up caches
    # Connect to external APIs
    
    logger.info("✅ NEXUS FOOTBALL initialized successfully")
    yield
    
    # ━━━━━ SHUTDOWN ━━━━━
    logger.info("🛑 Shutting down NEXUS FOOTBALL...")
    # Close all connections
    # Save model checkpoints
    # Flush caches


# ━━━━━ CREATE FASTAPI APPLICATION ━━━━━
app = FastAPI(
    title="⚽ NEXUS FOOTBALL",
    description="World Cup 2026 Intelligence Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ━━━━━ MIDDLEWARE CONFIGURATION ━━━━━

# CORS - Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZIP compression for responses > 1KB
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# ━━━━━ HEALTH CHECK ENDPOINT ━━━━━
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """System health check endpoint"""
    return {
        "status": "healthy",
        "service": "NEXUS FOOTBALL",
        "version": "1.0.0"
    }

@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint - API information"""
    return {
        "service": "⚽ NEXUS FOOTBALL",
        "description": "World Cup 2026 Intelligence Platform",
        "docs": "/api/docs",
        "systems": ["PitchOracle", "StatPulse", "MatchMind AI"]
    }

# ━━━━━ INCLUDE ROUTERS ━━━━━
# These will be created in the apis/ directory
# from backend.apis import pitchoracle, statpulse, matchmind
# 
# app.include_router(pitchoracle.router, prefix="/api/v1/pitchoracle", tags=["PitchOracle"])
# app.include_router(statpulse.router, prefix="/api/v1/statpulse", tags=["StatPulse"])
# app.include_router(matchmind.router, prefix="/api/v1/matchmind", tags=["MatchMind AI"])

# ━━━━━ ERROR HANDLERS ━━━━━
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "message": str(exc)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
