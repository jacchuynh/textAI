"""
Pacing and Ambient Storytelling System for AI Game Master

This package provides components for managing game pacing, ambient narration,
idle NPC interactions, and event summarization to create dynamic narrative experiences.
"""

from .pacing_manager import PacingManager, PacingState, AmbientTrigger
from .idle_npc_manager import IdleNPCManager
from .event_summarizer import EventSummarizer
from .pacing_integration import PacingIntegration

__all__ = [
    'PacingManager',
    'PacingState',
    'AmbientTrigger',
    'IdleNPCManager',
    'EventSummarizer',
    'PacingIntegration'
]