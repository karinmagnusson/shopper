"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from backend.config import settings
from backend.routers import auth

# Initialize FastAPI app
app = FastAPI(
    title="Pinterest Style Matcher",
    description="Connect Pinterest pins with shopping recommendations",
    version="0.1.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/app")
async def serve_frontend():
    """Serve the frontend application."""
    frontend_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"error": "Frontend not found"}


@app.get("/")
async def root():
    """Redirect to frontend application."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app")


@app.get("/api")
async def api_status():
    """API health check endpoint."""
    return {
        "status": "ok",
        "message": "Pinterest Style Matcher API",
        "version": "0.1.0",
        "docs": "http://localhost:8000/docs"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
