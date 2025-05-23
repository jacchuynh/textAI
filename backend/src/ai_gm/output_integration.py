"""
Output Generation System Integration for AI GM Brain

This module integrates the output generation system with the AI GM Brain,
controlling how responses are formatted and delivered to the player.
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum, auto

# Add the assets directory to path to allow importing output generation components
sys.path.insert(0, 'attached_assets')

# Define enums for output generation
class DeliveryChannel(Enum):
    """Channels for delivering responses"""
    CONSOLE = auto()       # Text console
    VISUAL = auto()        # Visual display (images, UI elements)
    AUDIO = auto()         # Audio output
    SYSTEM = auto()        # System messages (OOC, meta information)


class ResponsePriority(Enum):
    """Priority levels for responses"""
    IMMEDIATE = auto()     # Should be displayed right away
    HIGH = auto()          # High priority message
    NORMAL = auto()        # Normal priority message
    LOW = auto()           # Low priority, can be delayed
    BACKGROUND = auto()    # Background information, lowest priority


class OutputType(Enum):
    """Types of output content"""
    NARRATIVE = auto()     # Story narrative
    DIALOGUE = auto()      # Character dialogue
    DESCRIPTION = auto()   # Environmental descriptions
    COMBAT = auto()        # Combat information
    SYSTEM = auto()        # System information
    AMBIENT = auto()       # Ambient/background information


class OutputGenerationIntegration:
    """Integration module for the output generation system with AI GM Brain."""
    
    def __init__(self, brain):
        """
        Initialize the output generation integration.
        
        Args:
            brain: The AI GM Brain instance to integrate with
        """
        self.brain = brain
        self.enabled = True
        
        # Initialize message queue and history
        self.message_queue = []
        self.message_history = []
        self.max_history = 100
        
        # Initialize styling configurations
        self._init_styling()
    
    def _init_styling(self):
        """Initialize styling configurations for different output types."""
        # Define styling for different output types (would be used for UI rendering)
        self.styling = {
            OutputType.NARRATIVE.value: {
                "font_weight": "normal",
                "font_style": "normal",
                "color": "#FFFFFF",
                "background": "none",
                "border": "none",
                "padding": "0.5em 0"
            },
            OutputType.DIALOGUE.value: {
                "font_weight": "normal",
                "font_style": "italic",
                "color": "#E6E6FA",
                "background": "none",
                "border": "none",
                "padding": "0.25em 0",
                "quote_marks": True
            },
            OutputType.DESCRIPTION.value: {
                "font_weight": "normal",
                "font_style": "normal",
                "color": "#ADD8E6",
                "background": "none",
                "border": "none",
                "padding": "0.5em 0"
            },
            OutputType.COMBAT.value: {
                "font_weight": "bold",
                "font_style": "normal",
                "color": "#FF6347",
                "background": "rgba(255, 99, 71, 0.1)",
                "border": "1px solid rgba(255, 99, 71, 0.3)",
                "padding": "0.5em",
                "border_radius": "0.25em"
            },
            OutputType.SYSTEM.value: {
                "font_weight": "normal",
                "font_style": "italic",
                "color": "#7FFF00",
                "background": "rgba(127, 255, 0, 0.1)",
                "border": "none",
                "padding": "0.25em 0",
                "font_size": "0.9em"
            },
            OutputType.AMBIENT.value: {
                "font_weight": "normal",
                "font_style": "italic",
                "color": "#D3D3D3",
                "background": "none",
                "border": "none",
                "padding": "0.25em 0",
                "font_size": "0.9em"
            }
        }
    
    def is_enabled(self) -> bool:
        """Check if the output generation system is enabled."""
        return self.enabled
    
    def format_response(self, 
                       response_text: str, 
                       output_type: Union[OutputType, str] = OutputType.NARRATIVE, 
                       metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Format a response with appropriate styling.
        
        Args:
            response_text: The response text to format
            output_type: The type of output content
            metadata: Additional metadata for the response
            
        Returns:
            Formatted response
        """
        if not self.enabled:
            return {"text": response_text, "raw": True}
            
        # Convert string output_type to enum if needed
        if isinstance(output_type, str):
            try:
                output_type = OutputType[output_type.upper()]
            except KeyError:
                output_type = OutputType.NARRATIVE
                
        # Get styling for output type
        output_type_value = output_type.value if isinstance(output_type, OutputType) else output_type
        style = self.styling.get(output_type_value, self.styling[OutputType.NARRATIVE.value])
        
        # Apply text transformations based on output type
        if output_type == OutputType.DIALOGUE and style.get("quote_marks", False):
            # Add quote marks to dialogue if not already present
            if not response_text.strip().startswith('"') and not response_text.strip().startswith('"'):
                response_text = f'"{response_text}"'
        
        # Create formatted response
        formatted_response = {
            "text": response_text,
            "style": style,
            "type": output_type_value if isinstance(output_type_value, str) else output_type_value.name.lower(),
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        return formatted_response
    
    def deliver_response(self, 
                        response_text: str, 
                        output_type: Union[OutputType, str] = OutputType.NARRATIVE,
                        channels: List[Union[DeliveryChannel, str]] = None,
                        priority: Union[ResponsePriority, str] = ResponsePriority.NORMAL,
                        metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Deliver a response to the appropriate channels with the specified priority.
        
        Args:
            response_text: The response text to deliver
            output_type: The type of output content
            channels: The channels to deliver the response to
            priority: The priority of the response
            metadata: Additional metadata for the response
            
        Returns:
            Delivery result
        """
        if not self.enabled:
            return {"status": "delivered", "text": response_text, "raw": True}
            
        # Set default channel if none provided
        if not channels:
            channels = [DeliveryChannel.CONSOLE]
            
        # Convert string channels to enum if needed
        processed_channels = []
        for channel in channels:
            if isinstance(channel, str):
                try:
                    channel = DeliveryChannel[channel.upper()]
                except KeyError:
                    channel = DeliveryChannel.CONSOLE
            processed_channels.append(channel)
            
        # Convert string priority to enum if needed
        if isinstance(priority, str):
            try:
                priority = ResponsePriority[priority.upper()]
            except KeyError:
                priority = ResponsePriority.NORMAL
        
        # Format the response
        formatted_response = self.format_response(
            response_text=response_text,
            output_type=output_type,
            metadata=metadata
        )
        
        # Add delivery information
        delivery_info = {
            "channels": [ch.name.lower() if isinstance(ch, DeliveryChannel) else ch 
                        for ch in processed_channels],
            "priority": priority.name.lower() if isinstance(priority, ResponsePriority) else priority,
            "delivery_time": datetime.now().isoformat()
        }
        
        formatted_response["delivery"] = delivery_info
        
        # Add to message queue and history
        self.message_queue.append(formatted_response)
        self.message_history.append(formatted_response)
        
        # Trim history if needed
        if len(self.message_history) > self.max_history:
            self.message_history = self.message_history[-self.max_history:]
        
        return {
            "status": "delivered",
            "message_id": len(self.message_history) - 1,
            "formatted_response": formatted_response
        }
    
    def get_message_queue(self) -> List[Dict[str, Any]]:
        """
        Get the current message queue.
        
        Returns:
            List of queued messages
        """
        return self.message_queue.copy()
    
    def clear_message_queue(self) -> None:
        """Clear the message queue."""
        self.message_queue = []
    
    def get_message_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get the message history.
        
        Args:
            limit: Maximum number of messages to return (from most recent)
            
        Returns:
            List of historical messages
        """
        if limit is None or limit >= len(self.message_history):
            return self.message_history.copy()
        
        return self.message_history[-limit:].copy()
    
    def generate_combined_response(self, 
                                 narrative_text: str, 
                                 dialogue_text: Optional[str] = None,
                                 system_text: Optional[str] = None,
                                 combat_text: Optional[str] = None,
                                 ambient_text: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate a combined response with multiple output types.
        
        Args:
            narrative_text: Main narrative text
            dialogue_text: Optional dialogue text
            system_text: Optional system text
            combat_text: Optional combat text
            ambient_text: Optional ambient text
            
        Returns:
            List of formatted responses
        """
        responses = []
        
        # Process narrative text (always required)
        narrative_response = self.format_response(
            response_text=narrative_text,
            output_type=OutputType.NARRATIVE
        )
        responses.append(narrative_response)
        
        # Process dialogue text if provided
        if dialogue_text:
            dialogue_response = self.format_response(
                response_text=dialogue_text,
                output_type=OutputType.DIALOGUE
            )
            responses.append(dialogue_response)
        
        # Process system text if provided
        if system_text:
            system_response = self.format_response(
                response_text=system_text,
                output_type=OutputType.SYSTEM
            )
            responses.append(system_response)
        
        # Process combat text if provided
        if combat_text:
            combat_response = self.format_response(
                response_text=combat_text,
                output_type=OutputType.COMBAT
            )
            responses.append(combat_response)
        
        # Process ambient text if provided
        if ambient_text:
            ambient_response = self.format_response(
                response_text=ambient_text,
                output_type=OutputType.AMBIENT
            )
            responses.append(ambient_response)
        
        return responses


def attach_to_brain(brain):
    """
    Attach the output generation system to the AI GM Brain.
    
    Args:
        brain: The AI GM Brain instance
        
    Returns:
        The created integration instance
    """
    integration = OutputGenerationIntegration(brain)
    brain.register_extension("output_generation", integration)
    return integration