from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from app.api.v1 import recipes, instagram, ai, proxy, multimodal_extraction, shopping_lists
# DISABLED: auth module removed - Firebase handles authentication on frontend
from app.core.config import settings
from app.core.database import firebase_service
from app.schemas.responses import HealthCheckResponse
import logging
import time
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)

def validate_production_config():
    """Validate that all required configuration is present for production."""
    errors = []
    
    # Check Firebase configuration
    if not settings.firebase_project_id:
        errors.append("FIREBASE_PROJECT_ID is required")
    
    if not settings.firebase_credentials_path:
        errors.append("FIREBASE_CREDENTIALS_PATH is required")
    elif not os.path.exists(settings.firebase_credentials_path):
        errors.append(f"Firebase credentials file not found: {settings.firebase_credentials_path}")
    
    # Check security configuration
    if not settings.secret_key or len(settings.secret_key) < 32:
        errors.append("SECRET_KEY must be at least 32 characters long")
    
    if errors:
        error_msg = "❌ Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        logger.error(error_msg)
        raise RuntimeError(f"Invalid configuration: {'; '.join(errors)}")
    
    logger.info("✅ Production configuration validated successfully")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Recipe Reel Manager API - Save and organize Instagram food recipes with AI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Initialize Firebase on startup
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        logger.info("🚀 Starting ForkFlix API...")
        
        # Validate production configuration
        validate_production_config()
        
        # Initialize Firebase services
        firebase_service.initialize()
        
        logger.info("✅ ForkFlix API started successfully")
        logger.info(f"📊 Environment: {settings.environment}")
        logger.info(f"🔥 Firebase Project: {settings.firebase_project_id}")
        logger.info(f"🌐 CORS Origins: {settings.cors_origins}")
        
    except Exception as e:
        logger.error(f"❌ Failed to start application: {e}")
        raise

# Include API routers
app.include_router(
    recipes.router,
    prefix=f"{settings.api_v1_prefix}/recipes",
    tags=["recipes"]
)

app.include_router(
    instagram.router,
    prefix=f"{settings.api_v1_prefix}/instagram",
    tags=["instagram"]
)

app.include_router(
    ai.router,
    prefix=f"{settings.api_v1_prefix}/ai",
    tags=["ai"]
)

# DISABLED: Auth endpoints not used - Firebase handles authentication on frontend
# app.include_router(
#     auth.router,
#     prefix=f"{settings.api_v1_prefix}/auth",
#     tags=["auth"]
# )

app.include_router(
    proxy.router,
    prefix=f"{settings.api_v1_prefix}/proxy",
    tags=["proxy"]
)

app.include_router(
    multimodal_extraction.router,
    prefix=f"{settings.api_v1_prefix}/multimodal",
    tags=["multimodal-extraction"]
)

app.include_router(
    shopping_lists.router,
    prefix=f"{settings.api_v1_prefix}/shopping-lists",
    tags=["shopping-lists"]
)

# Root endpoint
@app.get("/", response_model=HealthCheckResponse)
async def root():
    """API health check"""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version=settings.version,
        environment=settings.environment,
        services={
            "firebase": "connected" if firebase_service.initialized else "disconnected",
            "api": "running"
        }
    )

# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Detailed health check"""
    return await root()

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global exception on {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level
    )