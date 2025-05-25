"""
API Setup for Magic Crafting System

This module registers the magic crafting API endpoints with the main FastAPI application.
"""

from fastapi import FastAPI
from .magic_crafting_api import router as magic_crafting_router
from .magic_crafting_seed import seed_all as seed_magic_crafting


def register_magic_crafting_api(app: FastAPI):
    """
    Register magic crafting API endpoints with the main FastAPI application
    
    Args:
        app: The FastAPI application
    """
    # Register the router
    app.include_router(magic_crafting_router)
    
    # Add startup event to seed the database
    @app.on_event("startup")
    async def startup_seed_magic_crafting():
        """Seed the magic crafting database on startup"""
        try:
            seed_magic_crafting()
        except Exception as e:
            print(f"Warning: Failed to seed magic crafting data: {e}")
            # Don't fail startup if seeding fails