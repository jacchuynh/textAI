"""
FastAPI application for the game engine's backend API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .combat_api import router as combat_router
from . import economy


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Game Engine API",
        description="API for the RPG game engine",
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

    # Add routers
    app.include_router(combat_router, prefix="/api/combat", tags=["Combat"])
    app.include_router(economy.router, prefix="/api/economy", tags=["Economy"])

    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Game Engine API",
            "version": "1.0.0",
            "status": "running"
        }

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create the app instance for uvicorn
app = create_app()