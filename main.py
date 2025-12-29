from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import time
import logging
from pathlib import Path
import models
from database import engine
from routers import auth, users, posts, admin
from exceptions import AppException
from config import settings

# Create database tables

# Create required directories
Path("uploads").mkdir(exist_ok=True)
Path("static").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Blog API",
    description="A complete blog API with authentication, posts, and admin panel",
    version="1.0.0",
    contact={"name": "API Support", "email": "support@example.com"}
)

models.Base.metadata.create_all(bind=engine)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://blog-api-web-li4k.onrender.com"],  # In production: specify exact origins
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

# Custom exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.__class__.__name__, "message": exc.message}
    )
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    html_path = Path("static/index.html")
    return html_path.read_text()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Application starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Application shutting down...")