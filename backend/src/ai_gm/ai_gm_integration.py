"""
AI GM Brain Integration Module

This module integrates all the AI GM Brain components into a cohesive system,
connecting the core brain with the world reaction, pacing, and output systems.
"""

import os
import sys
import time
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime

# Import core components
from backend.src.ai_gm.ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
from backend.src.ai_gm.ai_gm_brain_ooc_handler import OOCCommandHandler

# Import integration modules 
from backend.src.ai_gm.world_reaction.world_reaction_integration import WorldReactionIntegration, attach_to_brain as attach_world_reaction
from backend.src.ai_gm.pacing.pacing_integration import PacingIntegration, attach_to_brain as attach_pacing
from backend.src.ai_gm.output_integration import (
    OutputGenerationIntegration, 
    OutputType, 
    DeliveryChannel, 
    ResponsePriority,
    attach_to_brain as attach_output
)


class AIGMIntegrated:
    """
    Integrated AI GM Brain system with all components.
    
    This class manages the orchestration between the core AI GM Brain
    and its various extension systems (world reaction, pacing, output generation).
    """
    
    def __init__(self, game_id: str, player_id: str):
        """
        Initialize the integrated AI GM system.
        
        Args:
            game_id: The ID of the game session
            player_id: The ID of the player
        """
        # Create core brain
        self.brain = AIGMBrain(
            game_id=game_id,
            player_id=player_id
        )
        
        # Attach OOC command handler
        self.ooc_handler = OOCCommandHandler(self.brain)
        self.brain.register_extension("ooc_integration", self.ooc_handler)
        
        # Add standard OOC commands
        self._register_standard_commands()
        
        # Attach other systems
        self.world_reaction = attach_world_reaction(self.brain)
        self.pacing = attach_pacing(self.brain)
        self.output = attach_output(self.brain)
        
        # Initialize context
        self._context = {}
        
        # Store integration status
        self.status = {
            "world_reaction_enabled": self.world_reaction.is_enabled(),
            "pacing_enabled": self.pacing.is_enabled(),
            "output_enabled": self.output.is_enabled()
        }
    
    def _register_standard_commands(self):
        """Register standard OOC commands."""
        # Help command
        self.ooc_handler.commands["help"] = {
            "handler": self._handle_help_command,
            "description": "Display available commands",
            "parameters": []
        }
        
        # Stats command
        self.ooc_handler.commands["stats"] = {
            "handler": self._handle_stats_command,
            "description": "Display your character statistics",
            "parameters": []
        }
        
        # Location command
        self.ooc_handler.commands["location"] = {
            "handler": self._handle_location_command,
            "description": "Display information about your current location",
            "parameters": []
        }
    
    def _handle_help_command(self, args: Dict[str, Any], brain) -> Dict[str, Any]:
        """Handle the help command."""
        commands = self.ooc_handler.commands
        help_text = "Available Commands:\n"
        
        for cmd, details in commands.items():
            params = ""
            if details.get("parameters"):
                params = " " + " ".join([f"<{p}>" for p in details.get("parameters", [])])
            
            help_text += f"/{cmd}{params} - {details.get('description', 'No description')}\n"
        
        return {"status": "success", "response": help_text}
    
    def _handle_stats_command(self, args: Dict[str, Any], brain) -> Dict[str, Any]:
        """Handle the stats command."""
        player = self._context.get("player", {})
        if not player:
            return {"status": "error", "response": "No player data available"}
        
        stats_text = f"Character: {player.get('name', 'Unknown')}\n"
        stats_text += "Domains:\n"
        
        # Format domains
        domains = player.get("domains", {})
        for domain, value in domains.items():
            stars = "★" * value
            stats_text += f"  {domain}: {value} {stars}\n"
        
        # Add additional stats if available
        if "health" in player:
            stats_text += f"Health: {player['health']}\n"
            
        if "experience" in player:
            stats_text += f"Experience: {player['experience']}\n"
            
        if "reputation" in player:
            stats_text += f"Reputation: {player['reputation']}\n"
        
        return {"status": "success", "response": stats_text}
    
    def _handle_location_command(self, args: Dict[str, Any], brain) -> Dict[str, Any]:
        """Handle the location command."""
        location = self._context.get("current_location", "Unknown")
        
        if location == "Unknown":
            return {
                "status": "error", 
                "response": "You are not currently in a recognized location."
            }
        
        location_text = f"Current location: {location}\n"
        
        # Add NPCs in location if available
        npcs = self._context.get("active_npcs", [])
        if npcs:
            location_text += "\nPresent characters:\n"
            for npc in npcs:
                location_text += f"- {npc}\n"
        
        # Add location description if available
        description = self._context.get("location_description", "")
        if description:
            location_text += f"\n{description}\n"
        
        return {"status": "success", "response": location_text}
    
    def update_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the game context.
        
        Args:
            context_update: The context updates to apply
            
        Returns:
            Updated context
        """
        # Update the context
        self._context.update(context_update)
        
        # Return the updated context
        return self._context.copy()
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current game context.
        
        Returns:
            Current game context
        """
        return self._context.copy()
    
    def set_initial_context(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the initial game context.
        
        Args:
            initial_context: The initial context to set
            
        Returns:
            Set context
        """
        self._context = initial_context.copy()
        return self._context.copy()
    
    async def process_input_with_reactions(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input with world reactions and pacing integrated.
        
        Args:
            input_text: The player's input text
            
        Returns:
            Processed response with world reactions
        """
        # Start timing
        start_time = time.time()
        
        # Process through core brain
        basic_response = self.brain.process_player_input(input_text)
        response_text = basic_response["response_text"]
        metadata = basic_response["metadata"]
        
        # Skip further processing for OOC commands
        if metadata.get("processing_mode") == "OOC":
            # Format with output system
            if self.output.is_enabled():
                formatted_response = self.output.deliver_response(
                    response_text=response_text,
                    output_type=OutputType.SYSTEM,
                    channels=[DeliveryChannel.CONSOLE],
                    priority=ResponsePriority.IMMEDIATE,
                    metadata=metadata
                )
                return {
                    "response_text": response_text,
                    "metadata": metadata,
                    "formatted_response": formatted_response,
                    "world_reaction": None,
                    "pacing_update": None
                }
        
        # Get world reaction if enabled
        world_reaction = None
        if self.world_reaction.is_enabled():
            try:
                world_reaction = await self.world_reaction.assess_reaction(
                    player_id=self.brain.player_id,
                    player_input=input_text,
                    context=self._context
                )
                
                # If successful, add the reaction to the response
                if world_reaction.get("success", False):
                    reaction_data = world_reaction.get("reaction_data", {})
                    reaction_text = reaction_data.get("response", "")
                    
                    if reaction_text:
                        # Format the reaction text properly and add it to the response
                        response_text += f"\n\n{reaction_text}"
            except Exception as e:
                print(f"Error processing world reaction: {e}")
        
        # Update pacing if enabled
        pacing_update = None
        if self.pacing.is_enabled():
            try:
                pacing_update = self.pacing.update_pacing_state(
                    player_input=input_text,
                    response_data=basic_response
                )
            except Exception as e:
                print(f"Error updating pacing: {e}")
        
        # Format with output system if enabled
        formatted_response = None
        if self.output.is_enabled():
            # Determine output type based on response
            output_type = OutputType.NARRATIVE
            if "dialogue" in metadata.get("tags", []):
                output_type = OutputType.DIALOGUE
            elif "combat" in metadata.get("tags", []):
                output_type = OutputType.COMBAT
            elif "description" in metadata.get("tags", []):
                output_type = OutputType.DESCRIPTION
            
            # Deliver the response
            formatted_response = self.output.deliver_response(
                response_text=response_text,
                output_type=output_type,
                channels=[DeliveryChannel.CONSOLE],
                priority=ResponsePriority.NORMAL,
                metadata=metadata
            )
            
            # Check for ambient content based on pacing
            if pacing_update and self.pacing.is_enabled():
                ambient_content = self.pacing.check_for_ambient_content()
                if ambient_content:
                    # Format and deliver ambient content
                    ambient_text = ambient_content.get("content", "")
                    ambient_response = self.output.deliver_response(
                        response_text=ambient_text,
                        output_type=OutputType.AMBIENT,
                        channels=[DeliveryChannel.CONSOLE],
                        priority=ResponsePriority.LOW,
                        metadata={"pacing_trigger": True, "ambient_type": ambient_content.get("trigger_type")}
                    )
                    # Add to the formatted response
                    formatted_response["ambient_response"] = ambient_response
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Return complete result
        return {
            "response_text": response_text,
            "metadata": {
                **metadata,
                "processing_time_total": processing_time,
                "world_reaction_processed": world_reaction is not None,
                "pacing_updated": pacing_update is not None,
                "response_formatted": formatted_response is not None
            },
            "formatted_response": formatted_response,
            "world_reaction": world_reaction,
            "pacing_update": pacing_update
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the status of the integrated system.
        
        Returns:
            System status information
        """
        brain_stats = {}
        for stat_type, value in self.brain.stats.items():
            brain_stats[stat_type] = value
        
        return {
            "game_id": self.brain.game_id,
            "player_id": self.brain.player_id,
            "brain_stats": brain_stats,
            "integration_status": self.status,
            "extensions": list(self.brain.extensions.keys())
        }


def create_integrated_gm(game_id: str, player_id: str, initial_context: Dict[str, Any] = None) -> AIGMIntegrated:
    """
    Create an integrated AI GM system.
    
    Args:
        game_id: The ID of the game session
        player_id: The ID of the player
        initial_context: Optional initial context
        
    Returns:
        Created AIGMIntegrated instance
    """
    integrated_gm = AIGMIntegrated(game_id, player_id)
    
    if initial_context:
        integrated_gm.set_initial_context(initial_context)
    
    return integrated_gm