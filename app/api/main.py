"""
Main FastAPI application for Telegram Medical Analytics API
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
import logging
import time
from datetime import datetime

from app.api.routes import analytics
from app.api.schemas import ErrorResponse
from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Telegram Medical Analytics API",
    description="""
    Comprehensive analytics API for Telegram medical data pipeline.
    
    ## Features
    
    * **Channel Analytics**: Get insights about Telegram channels
    * **Message Search**: Search through messages with relevance scoring
    * **Product Analysis**: Track most mentioned medical products
    * **Image Detection**: Access YOLO object detection results
    * **Medical Insights**: Get medical trends and patterns
    
    ## Data Sources
    
    This API queries the dbt data warehouse with the following models:
    * `marts.dim_channels` - Channel information and metrics
    * `marts.fct_messages` - Message facts and content analysis
    * `marts.fct_image_detections` - YOLO object detection results
    * `marts.dim_dates` - Time-based analysis dimensions
    """,
    version="1.0.0",
    docs_url=None,  # Disable default docs
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url}")
    
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} - {process_time:.3f}s")
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error",
            error_code="INTERNAL_ERROR",
            details={"exception": str(exc)}
        ).dict()
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Telegram Medical Analytics API",
        version="1.0.0",
        description="Analytics API for Telegram medical data pipeline",
        routes=app.routes,
    )
    
    # Add custom info
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Custom docs endpoint
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui.css",
    )

# Root endpoint
@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Telegram Medical Analytics API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now(),
        "endpoints": {
            "analytics": "/api/analytics/summary",
            "channels": "/api/channels",
            "search": "/api/search/messages",
            "products": "/api/reports/top-products",
            "rankings": "/api/reports/channel-rankings",
            "detections": "/api/image-detections",
            "insights": "/api/reports/medical-insights",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

# Health check endpoint
@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "telegram-medical-analytics-api",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }

# Include routers
app.include_router(analytics.router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("🚀 Starting Telegram Medical Analytics API...")
    logger.info(f"📊 API Version: 1.0.0")
    logger.info(f"🔗 Documentation: /docs")
    logger.info(f"📖 ReDoc: /redoc")
    logger.info("✅ API started successfully!")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("🛑 Shutting down Telegram Medical Analytics API...")

# API metadata
@app.get("/api/metadata", response_model=dict)
async def get_api_metadata():
    """Get API metadata and configuration"""
    return {
        "api_name": "Telegram Medical Analytics API",
        "version": "1.0.0",
        "description": "Analytics API for Telegram medical data pipeline",
        "data_sources": [
            "marts.dim_channels",
            "marts.fct_messages", 
            "marts.fct_image_detections",
            "marts.dim_dates"
        ],
        "features": [
            "Channel Analytics",
            "Message Search",
            "Product Analysis", 
            "Image Detection",
            "Medical Insights"
        ],
        "endpoints": {
            "analytics": "/api/analytics/summary",
            "channels": "/api/channels",
            "channel_activity": "/api/channels/{channel_name}/activity",
            "channel_messages": "/api/channels/{channel_name}/messages",
            "search": "/api/search/messages",
            "top_products": "/api/reports/top-products",
            "channel_rankings": "/api/reports/channel-rankings",
            "image_detections": "/api/image-detections",
            "medical_insights": "/api/reports/medical-insights"
        },
        "timestamp": datetime.now()
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info"
    ) 