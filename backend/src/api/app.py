from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .characters import router as characters_router

def create_app() -> FastAPI:
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Chronicles RPG Backend",
        description="API for text-based RPG with simulated systems",
        version="0.1.0"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, restrict this to your frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register routers
    app.include_router(characters_router)
    
    @app.get("/")
    async def root():
        return {"message": "Welcome to Chronicles RPG API"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app