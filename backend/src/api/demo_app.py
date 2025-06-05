"""
Minimal FastAPI demo application for character creation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .demo_character_creation import router as character_creation_router

def create_app() -> FastAPI:
    """
    Create and configure a minimal FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Character Creation Demo API",
        description="API for the TextRealms character creation system",
        version="1.0.0"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify actual origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include character creation router
    app.include_router(character_creation_router, prefix="/api")

    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Character Creation Demo API",
            "version": "1.0.0",
            "status": "running",
            "docs_url": "/docs"
        }

    return app

# Create the app instance for uvicorn
app = create_app()
