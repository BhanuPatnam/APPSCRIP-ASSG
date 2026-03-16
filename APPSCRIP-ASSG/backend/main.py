import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import time

from backend.config import settings
from backend.app.rate_limiter import limiter, rate_limit_exceeded_handler
from backend.app.routes import auth, analyze, session
from backend.app.session_manager import cleanup_sessions
import asyncio

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL, format='[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s')
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up TradeIQ India backend...")
    # Start background task for session cleanup
    asyncio.create_task(run_session_cleanup())
    yield
    # Shutdown
    logger.info("Shutting down TradeIQ India backend...")

async def run_session_cleanup():
    while True:
        await asyncio.sleep(3600)  # Run every hour
        cleanup_sessions()

app = FastAPI(
    title="TradeIQ India API",
    description="A full-stack Trade Opportunities Intelligence Platform for Indian markets.",
    version="1.0.0",
    lifespan=lifespan
)

# Add state for rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# Add logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"Handled request: {request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration:.4f}s")
    return response

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
app.include_router(session.router, prefix="/session", tags=["Session"])

@app.get("/", tags=["Health"])
async def root():
    return {"service": "TradeIQ India API", "status": "ok", "version": "1.0.0"}
