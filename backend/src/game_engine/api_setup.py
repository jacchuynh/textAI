"""
API Setup for Magic Crafting System

This module registers the magic crafting API endpoints with the main FastAPI application.
"""

from fastapi import FastAPI
import importlib
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Try to import from new location first, then fall back to old location
try:
    # New location after restructuring
    from ..magic_system.magic_crafting_api import router as magic_crafting_router
    from ..magic_system.magic_crafting_seed import seed_magical_materials as seed_magic_crafting
    logger.info("Imported magic system components from new location")
except ImportError:
    try:
        # Old location
        from .magic_crafting_api import router as magic_crafting_router
        from .magic_crafting_seed import seed_all as seed_magic_crafting
        logger.info("Imported magic system components from original location")
    except ImportError:
        logger.error("Failed to import magic system components from any location")
        # Define placeholder router and seed function to prevent startup failures
        from fastapi import APIRouter
        magic_crafting_router = APIRouter()
        def seed_magic_crafting():
            logger.warning("Using placeholder magic crafting seed function")
            pass


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
            logger.info("Successfully seeded magic crafting data")
        except Exception as e:
            logger.warning(f"Failed to seed magic crafting data: {e}")
            # Don't fail startup if seeding fails