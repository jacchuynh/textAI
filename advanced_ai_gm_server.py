#!/usr/bin/env python3
"""
Advanced AI GM Brain API Server
This server integrates the complex AI GM Brain implementation from the backend/src/ai_gm module.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

# Import our custom AI GM Brain implementation
from ai_gm_brain_custom import AIGMBrainCustom, ProcessingMode, InputComplexity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("advanced_ai_gm_server")

# Player sessions store
player_sessions: Dict[str, AIGMBrainCustom] = {}

# Request/Response models
class PlayerContext(BaseModel):
    """Player context information passed from the game engine."""
    name: str = Field(..., description="Player character name")
    level: int = Field(1, description="Player character level")
    location_region: str = Field(..., description="Current region")
    location_area: str = Field(..., description="Current area within region")
    health: Dict[str, int] = Field(..., description="Health stats (current/max)")
    magic_profile: Optional[Dict[str, Any]] = Field(None, description="Magic abilities info")
    
class PlayerInput(BaseModel):
    """Model for player input requests."""
    player_id: str = Field(..., description="Unique player identifier")
    game_id: Optional[str] = Field(None, description="Game session identifier")
    input_text: str = Field(..., description="Raw player text input")
    player_context: Optional[PlayerContext] = Field(None, description="Player game context")

class AIGMResponse(BaseModel):
    """Model for AI GM Brain responses."""
    response_text: str = Field(..., description="Text response to player")
    success: bool = Field(True, description="Whether processing succeeded")
    requires_llm: Optional[bool] = Field(None, description="Whether LLM was needed")
    llm_used: Optional[bool] = Field(None, description="Whether LLM was actually used")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional response metadata")

# Application startup/shutdown handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    # Startup: Initialize LLM and other resources
    logger.info("Starting Advanced AI GM Brain Server")
    # Initialize resources here
    
    yield
    
    # Shutdown: Cleanup resources
    logger.info("Shutting down Advanced AI GM Brain Server")
    # Close sessions and resources
    player_sessions.clear()

# Create FastAPI application
app = FastAPI(
    title="TextRealmsAI - Advanced AI GM Brain API",
    description="Enterprise-grade AI Game Master for text-based roleplaying games",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint providing service information."""
    return {
        "service": "TextRealmsAI - Advanced AI GM Brain API",
        "status": "running",
        "ai_gm_available": True,
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "ai_gm_available": True}

def get_or_create_session(player_id: str, game_id: Optional[str] = None) -> AIGMBrainCustom:
    """Get existing player session or create a new one."""
    if player_id not in player_sessions:
        session_id = game_id or f"game_{player_id}"
        logger.info(f"Creating new AI GM Brain session for player {player_id}, game {session_id}")
        player_sessions[player_id] = AIGMBrainCustom(
            game_id=session_id,
            player_id=player_id
        )
    return player_sessions[player_id]

@app.post("/api/ai-gm/process-input", response_model=AIGMResponse)
async def process_player_input(input_data: PlayerInput, background_tasks: BackgroundTasks):
    """Process player input through the AI GM Brain."""
    try:
        player_id = input_data.player_id
        input_text = input_data.input_text
        
        logger.info(f"Processing input from {player_id}: '{input_text}'")
        
        # Get or create AI GM Brain session for this player
        ai_gm_brain = get_or_create_session(player_id, input_data.game_id)
        
        # Process the input with our advanced AI GM Brain
        result = ai_gm_brain.process_player_input(input_text)
        
        # Convert processing mode and complexity enums to strings for JSON serialization
        if 'metadata' in result and result['metadata']:
            if 'processing_mode' in result['metadata'] and isinstance(result['metadata']['processing_mode'], ProcessingMode):
                result['metadata']['processing_mode'] = result['metadata']['processing_mode'].name
            
            if 'complexity' in result['metadata'] and isinstance(result['metadata']['complexity'], InputComplexity):
                result['metadata']['complexity'] = result['metadata']['complexity'].name
        
        # Schedule background processing if needed
        if result.get('requires_background_processing'):
            background_tasks.add_task(
                ai_gm_brain.process_background_tasks,
                input_text,
                player_id
            )
        
        return result
    
    except Exception as e:
        logger.error(f"Error processing input: {e}", exc_info=True)
        return {
            "response_text": "I'm having trouble processing your request right now. Please try again.",
            "success": False,
            "metadata": {"error": str(e)}
        }

@app.post("/api/ai-gm/clear-session")
async def clear_session(player_id: str):
    """Clear a player's AI GM Brain session."""
    if player_id in player_sessions:
        del player_sessions[player_id]
        return {"success": True, "message": f"Session cleared for player {player_id}"}
    return {"success": False, "message": f"No session found for player {player_id}"}

@app.get("/api/ai-gm/sessions")
async def list_sessions():
    """List active AI GM Brain sessions (admin endpoint)."""
    return {
        "sessions": [
            {"player_id": player_id, "interaction_count": brain.interaction_count}
            for player_id, brain in player_sessions.items()
        ],
        "count": len(player_sessions)
    }

if __name__ == "__main__":
    port = int(os.environ.get("AI_GM_PORT", 8000))
    host = os.environ.get("AI_GM_HOST", "127.0.0.1")
    
    print(f"🧠 Advanced AI GM Brain API server starting on http://{host}:{port}")
    
    uvicorn.run("advanced_ai_gm_server:app", host=host, port=port, reload=False)
