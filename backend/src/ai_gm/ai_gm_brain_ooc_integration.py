"""
AI GM Brain - OOC Command Integration

This module connects the Out-of-Character (OOC) command handler to the main AI GM Brain.
It adapts the OOC commands to work with the core AI GM Brain architecture.
"""

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Import local components
from .ai_gm_brain import AIGMBrain
from .ai_gm_brain_ooc_handler import OOCCommandHandler


class OOCIntegration:
    """
    Integration layer that connects OOC command handling to the AI GM Brain.
    
    This class:
    1. Intercepts OOC commands from the main input stream
    2. Routes them to the specialized OOC handler
    3. Formats responses consistently with the main AI GM Brain
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the OOC integration layer.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.ooc_handler = OOCCommandHandler(ai_gm_brain)
        self.logger = logging.getLogger(f"OOCIntegration_{ai_gm_brain.game_id}")
    
    def process_ooc_command(self, input_string: str, start_time: float) -> Dict[str, Any]:
        """
        Process an OOC command.
        
        Args:
            input_string: The full input string including the '/ooc' prefix
            start_time: Processing start time for metrics
            
        Returns:
            Response data dictionary
        """
        # Strip the /ooc prefix and any leading/trailing whitespace
        command = input_string.lower().replace('/ooc', '', 1).strip()
        
        # Pass to the OOC handler
        response = self.ooc_handler.handle_command(command)
        
        # Add standard metadata
        processing_time = time.time() - start_time if 'processing_time' not in response else response['processing_time']
        
        response.update({
            'metadata': {
                'processing_time': processing_time,
                'complexity': 'OOC_COMMAND',
                'processing_mode': 'MECHANICAL',
                'interaction_count': self.ai_gm_brain.interaction_count,
                'timestamp': datetime.utcnow().isoformat()
            },
            'ooc_response': True
        })
        
        # Log the OOC command
        self.logger.info(f"Processed OOC command: '{command}' in {processing_time:.3f}s")
        
        return response
    
    def is_ooc_command(self, input_string: str) -> bool:
        """
        Check if an input string is an OOC command.
        
        Args:
            input_string: Input string to check
            
        Returns:
            True if the input is an OOC command, False otherwise
        """
        return input_string.lower().startswith('/ooc')


# Extend the AIGMBrain with OOC integration
def extend_ai_gm_brain_with_ooc(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with OOC integration capabilities.
    
    This function patches the AI GM Brain instance to use the OOC integration
    for handling OOC commands.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create OOC integration
    ooc_integration = OOCIntegration(ai_gm_brain)
    
    # Store the original _handle_ooc_command method
    original_handle_ooc = ai_gm_brain._handle_ooc_command
    
    # Replace with the integrated version
    def integrated_handle_ooc(input_string: str, start_time: float) -> Dict[str, Any]:
        return ooc_integration.process_ooc_command(input_string, start_time)
    
    # Patch the AI GM Brain
    ai_gm_brain._handle_ooc_command = integrated_handle_ooc
    
    # Store the OOC integration for future reference
    ai_gm_brain.ooc_integration = ooc_integration