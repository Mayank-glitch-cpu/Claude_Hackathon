from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from app.utils.logger import setup_logger

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = setup_logger("main")

from app.routes import upload, analyze, generate, progress, questions

app = FastAPI(title="AI Learning Platform API", version="1.0.0")

logger.info("=" * 80)
logger.info("AI Learning Platform API Starting")
logger.info("=" * 80)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.info("CORS middleware configured for http://localhost:3000")

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(analyze.router, prefix="/api", tags=["analyze"])
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(progress.router, prefix="/api", tags=["progress"])
app.include_router(questions.router, prefix="/api", tags=["questions"])

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "AI Learning Platform API"}

@app.get("/health")
async def health():
    logger.debug("Health check endpoint accessed")
    return {"status": "healthy"}

