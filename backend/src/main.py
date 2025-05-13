"""
Main entry point for the game engine backend.
"""
import uvicorn
from api.app import create_app


app = create_app()


if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )