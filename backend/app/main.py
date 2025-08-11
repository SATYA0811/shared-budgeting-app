"""
Main FastAPI Application - Shared Budgeting API

This is the core FastAPI application that serves as the entry point for the
Shared Budgeting Application. It handles:
- Application setup and configuration
- Middleware registration (CORS, security, logging)
- Router inclusion and URL routing
- Global exception handling
- Health checks and monitoring endpoints

The application is organized using FastAPI routers for better modularity:
- Authentication routes (login, registration, user management)
- Transaction routes (CRUD operations, filtering)
- Category routes (category management, budgeting)
- Income routes (income tracking, financial summaries)
- Goals routes (goal management, progress tracking)
- Analytics routes (financial insights, reporting)
- File routes (bank statement upload and parsing)
"""

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import time

# Import configuration and database
from .database import create_tables
from .config import settings
from .auth import get_current_user
from .models import User

# Import all routers
from .routers import auth_routes, transactions, categories, income, goals, analytics, files, partners, banks

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)

# Create database tables on startup
create_tables()
logger.info("Database tables created successfully")

# Create FastAPI application
app = FastAPI(
    title="Shared Budgeting API",
    description="""
    A comprehensive budgeting application with the following features:
    
    ## 🔐 Authentication
    - User registration and login with JWT tokens
    - Secure password hashing with bcrypt
    - Rate limiting on authentication endpoints
    
    ## 💳 Transaction Management
    - Manual transaction entry and editing
    - File upload for bank statements (PDF, CSV, Excel)
    - Automatic transaction categorization with rules
    - Advanced filtering and search capabilities
    
    ## 📊 Analytics & Insights
    - Spending trends and patterns over time
    - Category-wise analysis and breakdowns
    - Budget performance tracking
    - Monthly financial reports
    - Personalized insights and recommendations
    
    ## 🎯 Goals & Savings
    - Goal creation with target amounts and dates
    - Progress tracking and visualization
    - Contribution logging and achievement detection
    - Recurring goal support
    
    ## 🏢 Multi-User Support
    - Household sharing and collaboration
    - User-based data isolation
    - Role-based access control
    
    ## 🛡️ Security Features
    - Rate limiting on sensitive endpoints
    - Input validation and sanitization
    - CORS and security headers
    - Comprehensive error handling
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "Shared Budgeting App",
        "email": "support@budgetapp.com",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {"name": "Authentication", "description": "User registration and login"},
        {"name": "Transactions", "description": "Transaction management and categorization"},
        {"name": "Categories", "description": "Category management and budgeting"},
        {"name": "Income", "description": "Income tracking and financial summaries"},
        {"name": "Goals", "description": "Goal creation and progress tracking"},
        {"name": "Analytics", "description": "Financial analytics and insights"},
        {"name": "File Upload", "description": "Bank statement file processing"},
    ]
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s"
    )
    return response

# Global exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

@app.exception_handler(ValueError)
async def validation_exception_handler(request: Request, exc: ValueError):
    """Handle validation errors."""
    logger.warning(f"Validation error: {str(exc)}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

# Health and monitoring endpoints
@app.get("/health", tags=["Monitoring"])
def health_check():
    """Health check endpoint for monitoring and load balancers."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.environment
    }

@app.get("/debug", tags=["Development"])
def debug_endpoint():
    """Debug endpoint to check server status (development only).""" 
    if settings.environment == "production":
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "status": "ok", 
        "message": "Server is running",
        "environment": settings.environment,
        "debug_mode": settings.debug
    }

@app.get("/debug-auth", tags=["Development"])
def debug_auth(current_user: User = Depends(get_current_user)):
    """Debug endpoint to test authentication (development only)."""
    if settings.environment == "production":
        raise HTTPException(status_code=404, detail="Not found")
    try:
        return {
            "status": "ok", 
            "user_id": current_user.id, 
            "message": "Auth working",
            "user_email": current_user.email
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Include all routers with their respective prefixes
app.include_router(auth_routes.router, tags=["Authentication"])
app.include_router(transactions.router, tags=["Transactions"])
app.include_router(categories.router, tags=["Categories"])
app.include_router(income.router, tags=["Income"])
app.include_router(goals.router, tags=["Goals"])
app.include_router(analytics.router, tags=["Analytics"])
app.include_router(files.router, tags=["File Upload"])
app.include_router(partners.router, tags=["Partners"])
app.include_router(banks.router, tags=["Banks"])

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(f"Starting Shared Budgeting API v1.0.0 in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info(f"CORS origins: {settings.cors_origins}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Shared Budgeting API")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )