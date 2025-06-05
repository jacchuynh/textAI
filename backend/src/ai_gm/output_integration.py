"""
Output Generation Integration for AI GM Brain

This module provides unified output generation and formatting for all AI GM responses,
supporting multiple delivery channels and response types.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime

class OutputType(Enum):
    """Types of output the AI GM can generate."""
    NARRATIVE = auto()      # Story descriptions and narration
    DIALOGUE = auto()       # NPC dialogue
    SYSTEM = auto()         # Game system messages
    ERROR = auto()          # Error messages
    DEBUG = auto()          # Debug information
    AMBIENT = auto()        # Ambient descriptions
    ACTION_RESULT = auto()  # Results of player actions

class DeliveryChannel(Enum):
    """Channels through which output can be delivered."""
    MAIN = auto()           # Main game output
    WHISPER = auto()        # Private messages to player
    BROADCAST = auto()      # Public announcements
    LOG = auto()           # System logs
    DEBUG_CONSOLE = auto()  # Debug console
    CONSOLE = auto()        # Console output (compatibility)

class ResponsePriority(Enum):
    """Priority levels for responses."""
    CRITICAL = auto()       # Critical system messages
    HIGH = auto()          # Important game events
    NORMAL = auto()        # Standard responses
    LOW = auto()           # Background/ambient content
    DEBUG = auto()         # Debug information

@dataclass
class FormattedResponse:
    """A formatted response ready for delivery."""
    content: str
    output_type: OutputType
    channel: DeliveryChannel
    priority: ResponsePriority
    metadata: Dict[str, Any]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "content": self.content,
            "output_type": self.output_type.name,
            "channel": self.channel.name,
            "priority": self.priority.name,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }

class OutputFormatter:
    """Handles formatting of different types of output."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def format_narrative(self, content: str, context: Dict[str, Any] = None) -> str:
        """Format narrative content."""
        if context and context.get('location'):
            return f"[{context['location']}] {content}"
        return content
    
    def format_dialogue(self, speaker: str, content: str, context: Dict[str, Any] = None) -> str:
        """Format dialogue content."""
        mood = context.get('mood', '') if context else ''
        if mood:
            return f"{speaker} {mood}: \"{content}\""
        return f"{speaker}: \"{content}\""
    
    def format_system(self, content: str, severity: str = "info") -> str:
        """Format system messages."""
        prefix = {
            "error": "⚠️ ERROR:",
            "warning": "⚠️ WARNING:",
            "info": "ℹ️ INFO:",
            "success": "✅ SUCCESS:"
        }.get(severity, "ℹ️")
        
        return f"{prefix} {content}"
    
    def format_action_result(self, action: str, result: str, success: bool = True) -> str:
        """Format action results."""
        indicator = "✅" if success else "❌"
        return f"{indicator} {action}: {result}"

class OutputGenerationIntegration:
    """Main integration class for output generation."""
    
    def __init__(self, game_id: str, player_id: str):
        self.game_id = game_id
        self.player_id = player_id
        self.logger = logging.getLogger(__name__)
        self.formatter = OutputFormatter()
        self.response_history: List[FormattedResponse] = []
        
        self.logger.info(f"Output Generation Integration initialized for game {game_id} and player {player_id}")
    
    def generate_response(
        self,
        content: str,
        output_type: OutputType = OutputType.NARRATIVE,
        channel: DeliveryChannel = DeliveryChannel.MAIN,
        priority: ResponsePriority = ResponsePriority.NORMAL,
        context: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None
    ) -> FormattedResponse:
        """Generate a formatted response."""
        
        # Apply appropriate formatting based on output type
        if output_type == OutputType.NARRATIVE:
            formatted_content = self.formatter.format_narrative(content, context)
        elif output_type == OutputType.DIALOGUE:
            speaker = context.get('speaker', 'Unknown') if context else 'Unknown'
            formatted_content = self.formatter.format_dialogue(speaker, content, context)
        elif output_type == OutputType.SYSTEM:
            severity = context.get('severity', 'info') if context else 'info'
            formatted_content = self.formatter.format_system(content, severity)
        elif output_type == OutputType.ACTION_RESULT:
            action = context.get('action', 'Action') if context else 'Action'
            success = context.get('success', True) if context else True
            formatted_content = self.formatter.format_action_result(action, content, success)
        else:
            formatted_content = content
        
        # Create formatted response
        response = FormattedResponse(
            content=formatted_content,
            output_type=output_type,
            channel=channel,
            priority=priority,
            metadata=metadata or {},
            timestamp=datetime.utcnow()
        )
        
        # Store in history
        self.response_history.append(response)
        
        # Limit history size
        if len(self.response_history) > 100:
            self.response_history = self.response_history[-100:]
        
        self.logger.debug(f"Generated {output_type.name} response: {formatted_content[:100]}...")
        
        return response
    
    def generate_error_response(self, error_message: str, context: Dict[str, Any] = None) -> FormattedResponse:
        """Generate an error response."""
        return self.generate_response(
            content=error_message,
            output_type=OutputType.ERROR,
            channel=DeliveryChannel.MAIN,
            priority=ResponsePriority.HIGH,
            context={"severity": "error", **(context or {})}
        )
    
    def generate_success_response(self, success_message: str, context: Dict[str, Any] = None) -> FormattedResponse:
        """Generate a success response."""
        return self.generate_response(
            content=success_message,
            output_type=OutputType.SYSTEM,
            channel=DeliveryChannel.MAIN,
            priority=ResponsePriority.NORMAL,
            context={"severity": "success", **(context or {})}
        )
    
    def generate_ambient_content(self, content: str, location: str = None) -> FormattedResponse:
        """Generate ambient content."""
        context = {"location": location} if location else None
        return self.generate_response(
            content=content,
            output_type=OutputType.AMBIENT,
            channel=DeliveryChannel.MAIN,
            priority=ResponsePriority.LOW,
            context=context
        )
    
    def deliver_response(
        self,
        response_text: str,
        output_type: OutputType = OutputType.NARRATIVE,
        channels: List[DeliveryChannel] = None,
        priority: ResponsePriority = ResponsePriority.NORMAL,
        metadata: Dict[str, Any] = None
    ) -> FormattedResponse:
        """
        Deliver a formatted response through specified channels.
        
        Args:
            response_text: The response text to deliver
            output_type: Type of output content
            channels: List of delivery channels (uses MAIN if not specified)
            priority: Response priority level
            metadata: Additional metadata for the response
            
        Returns:
            FormattedResponse object with the delivered content
        """
        if channels is None:
            channels = [DeliveryChannel.MAIN]
        
        # Use the first channel for the primary response
        primary_channel = channels[0] if channels else DeliveryChannel.MAIN
        
        # Generate the formatted response
        formatted_response = self.generate_response(
            content=response_text,
            output_type=output_type,
            channel=primary_channel,
            priority=priority,
            metadata=metadata
        )
        
        # If multiple channels specified, log that multi-channel delivery was requested
        if len(channels) > 1:
            self.logger.debug(f"Multi-channel delivery requested: {[c.name for c in channels]}")
            # In a full implementation, you would deliver to each channel
            # For now, we'll just use the primary channel
        
        return formatted_response

    def get_recent_responses(self, count: int = 10) -> List[FormattedResponse]:
        """Get recent responses."""
        return self.response_history[-count:] if count > 0 else self.response_history[:]
    
    def get_responses_by_type(self, output_type: OutputType) -> List[FormattedResponse]:
        """Get responses of a specific type."""
        return [r for r in self.response_history if r.output_type == output_type]
    
    def clear_history(self):
        """Clear response history."""
        self.response_history.clear()
        self.logger.info("Response history cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get output generation statistics."""
        total_responses = len(self.response_history)
        
        type_counts = {}
        channel_counts = {}
        priority_counts = {}
        
        for response in self.response_history:
            # Count by type
            type_name = response.output_type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # Count by channel
            channel_name = response.channel.name
            channel_counts[channel_name] = channel_counts.get(channel_name, 0) + 1
            
            # Count by priority
            priority_name = response.priority.name
            priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1
        
        return {
            "total_responses": total_responses,
            "responses_by_type": type_counts,
            "responses_by_channel": channel_counts,
            "responses_by_priority": priority_counts,
            "history_size": len(self.response_history)
        }

# Convenience function for easy integration
def create_output_integration(game_id: str, player_id: str) -> OutputGenerationIntegration:
    """Create and return an OutputGenerationIntegration instance."""
    return OutputGenerationIntegration(game_id, player_id)
