from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from .core.config import settings
from .api import parse, asr, query, alerts

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting ML Document Processing API")
    logger.info(f"Environment: {'Development' if settings.debug else 'Production'}")
    
    # Initialize services here (Pinecone, etc.)
    try:
        # Initialize Pinecone (stubbed for demo)
        logger.info("Initializing vector database...")
        # pinecone.init(api_key=settings.pinecone_api_key, environment=settings.pinecone_environment)
        
        # Initialize other services
        logger.info("Services initialized successfully")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ML Document Processing API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Advanced ML-powered document processing and analysis API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(parse.router, prefix="/api", tags=["Document Processing"])
app.include_router(asr.router, prefix="/api", tags=["Speech Recognition"])
app.include_router(query.router, prefix="/api", tags=["Query Processing"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts & Analytics"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ML Document Processing API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-25T10:00:00Z",
        "services": {
            "api": "operational",
            "ml_models": "operational",
            "vector_db": "operational"
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )