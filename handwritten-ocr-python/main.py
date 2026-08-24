from pathlib import Path

from fastapi import (
    FastAPI,
    Request
)

from fastapi.responses import HTMLResponse

from fastapi.templating import Jinja2Templates

from fastapi.staticfiles import StaticFiles

from fastapi.middleware.cors import CORSMiddleware

from database import check_database

from app.routes.ocr_routes import router as ocr_router


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent


# ============================================================
# DIRECTORIES
# ============================================================

TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR = BASE_DIR / "static"

UPLOAD_DIR = BASE_DIR / "uploads"


# ============================================================
# CREATE DIRECTORIES IF THEY DON'T EXIST
# ============================================================

TEMPLATES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Handwritten OCR API",
    description=(
        "Handwritten Image and PDF OCR "
        "using Unlimited-OCR"
    ),
    version="1.0.0"
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static"
)


# ============================================================
# JINJA2 TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# FRONTEND
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
async def root(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    try:

        database_status = check_database()

    except Exception as error:

        print(
            "DATABASE HEALTH ERROR:",
            repr(error)
        )

        database_status = False


    return {

        "success": True,

        "api": "running",

        "database": (
            "connected"
            if database_status
            else "disconnected"
        )
    }


# ============================================================
# OCR ROUTES
# ============================================================

app.include_router(
    ocr_router
)


# ============================================================
# STARTUP MESSAGE
# ============================================================

@app.on_event("startup")
async def startup_event():

    print("")
    print("=" * 60)
    print("Handwritten OCR API")
    print("=" * 60)
    print("Server: http://localhost:5000")
    print("Frontend: http://localhost:5000/")
    print("Health: http://localhost:5000/health")
    print("OCR: http://localhost:5000/api/ocr")
    print("History: http://localhost:5000/api/ocr/history")
    print("Docs: http://localhost:5000/docs")
    print("=" * 60)
    print("")