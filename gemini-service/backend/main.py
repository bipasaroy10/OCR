import os

from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Load environment variables
load_dotenv()


# Create FastAPI application
app = FastAPI(
    title="Handwritten OCR API",
    description="Convert handwritten images into text using Google Gemini",
    version="1.0.0"
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Routes
# --------------------------------------------------

from routes.ocr import router as ocr_router

app.include_router(ocr_router)


# --------------------------------------------------
# Root Route
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Handwritten OCR API is running",
        "docs": "/docs"
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
async def health_check():
    return {
        "success": True,
        "status": "healthy"
    }