"""
Delivery System for AI GM Brain output.

The delivery system manages how responses from the AI GM Brain are delivered
to different channels, with priority handling.
"""

from typing import List, Dict, Any, Optional
from enum import Enum, auto
import logging
import asyncio


class ResponsePriority(Enum):
    """Priority levels for responses."""
    IMMEDIATE = auto()  # Critical, interrupting feedback
    HIGH = auto()       # Important information
    NORMAL = auto()     # Standard responses
    LOW = auto()        # Background or ambient content
    DEFER = auto()      # Content that can wait


class DeliveryChannel(Enum):
    """Channels for delivering content."""
    NARRATIVE = auto()  # Main narrative content
    AMBIENT = auto()    # Environmental descriptions
    COMBAT = auto()     # Combat-specific content
    SYSTEM = auto()     # System messages
    DEBUG = auto()      # Debug information
    CONSOLE = auto()    # Console output for testing
    CHAT = auto()       # Chat messages from NPCs
    UI = auto()         # User interface updates


class DeliverySystem:
    """System for delivering AI GM Brain responses to appropriate channels."""
    
    def __init__(self):
        """Initialize the delivery system."""
        self.logger = logging.getLogger("DeliverySystem")
    
    async def deliver_response(self, 
                             response_text: str, 
                             channels: Optional[List[DeliveryChannel]] = None, 
                             priority: ResponsePriority = ResponsePriority.NORMAL) -> None:
        """
        Deliver a response to specified channels with the given priority.
        
        Args:
            response_text: The text to deliver
            channels: List of channels to deliver to (default: [NARRATIVE])
            priority: Priority level for this response
        """
        if not channels:
            channels = [DeliveryChannel.NARRATIVE]
        
        # Default implementation just logs the response
        channel_names = [channel.name for channel in channels]
        self.logger.info(f"[{priority.name}] Delivering to {', '.join(channel_names)}: {response_text[:100]}...")
        
        # In a real implementation, would route to different output channels
        # based on the channels parameter and handle priority appropriately