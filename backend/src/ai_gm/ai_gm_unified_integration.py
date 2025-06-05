"""
Unified AI GM Brain Integration System

This module creates a single, cohesive integration that combines all AI GM Brain components
into a working system that can be easily used throughout the application.
"""

import os
import sys
import time
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timedelta
from enum import Enum

# Core AI GM Brain imports
try:
    # Try relative imports first
    try:
        from .ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
        from .ai_gm_config import IntegratedAIGMConfig
    except (ImportError, ValueError):
        # Handle relative import error
        pass
except ImportError:
    # Fall back to absolute imports if running from backend/src/
    import sys
    import os
    try:
        # Try direct import first
        from ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
        from ai_gm_config import IntegratedAIGMConfig
    except ImportError:
        # Fall back to absolute imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        try:
            from ai_gm.ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
            from ai_gm.ai_gm_config import IntegratedAIGMConfig
        except ImportError:
            from backend.src.ai_gm.ai_gm_brain import AIGMBrain, ProcessingMode, InputComplexity
            from backend.src.ai_gm.ai_gm_config import IntegratedAIGMConfig

# Integration modules
try:
    try:
        from .world_reaction.optimized_world_reaction_integration import extend_ai_gm_brain_with_optimized_world_reaction
        from .optimizations.optimization_config import get_optimization_config
    except ImportError:
        try:
            from world_reaction.optimized_world_reaction_integration import extend_ai_gm_brain_with_optimized_world_reaction
            from optimizations.optimization_config import get_optimization_config
        except ImportError:
            try:
                from ai_gm.world_reaction.optimized_world_reaction_integration import extend_ai_gm_brain_with_optimized_world_reaction
                from ai_gm.optimizations.optimization_config import get_optimization_config
            except ImportError:
                from backend.src.ai_gm.world_reaction.optimized_world_reaction_integration import extend_ai_gm_brain_with_optimized_world_reaction
                from backend.src.ai_gm.optimizations.optimization_config import get_optimization_config
    
    # Fallback to legacy integration if optimized version fails
    try:
        from .world_reaction.world_reaction_integration import extend_ai_gm_brain_with_world_reaction
    except ImportError:
        try:
            from world_reaction.world_reaction_integration import extend_ai_gm_brain_with_world_reaction
        except ImportError:
            try:
                from ai_gm.world_reaction.world_reaction_integration import extend_ai_gm_brain_with_world_reaction
            except ImportError:
                from backend.src.ai_gm.world_reaction.world_reaction_integration import extend_ai_gm_brain_with_world_reaction
    
    WORLD_REACTION_AVAILABLE = True
    OPTIMIZED_WORLD_REACTION_AVAILABLE = True
except ImportError:
    WORLD_REACTION_AVAILABLE = False
    OPTIMIZED_WORLD_REACTION_AVAILABLE = False

try:
    try:
        from .pacing.pacing_integration import PacingIntegration
    except ImportError:
        try:
            from pacing.pacing_integration import PacingIntegration
        except ImportError:
            try:
                from ai_gm.pacing.pacing_integration import PacingIntegration
            except ImportError:
                from backend.src.ai_gm.pacing.pacing_integration import PacingIntegration
    PACING_AVAILABLE = True
except ImportError:
    PACING_AVAILABLE = False

try:
    try:
        from .output_integration import OutputGenerationIntegration, OutputType, DeliveryChannel, ResponsePriority
    except ImportError:
        try:
            from output_integration import OutputGenerationIntegration, OutputType, DeliveryChannel, ResponsePriority
        except ImportError:
            try:
                from ai_gm.output_integration import OutputGenerationIntegration, OutputType, DeliveryChannel, ResponsePriority
            except ImportError:
                from backend.src.ai_gm.output_integration import OutputGenerationIntegration, OutputType, DeliveryChannel, ResponsePriority
    OUTPUT_AVAILABLE = True
except ImportError:
    OUTPUT_AVAILABLE = False

try:
    try:
        from .ai_gm_brain_ooc_handler import OOCCommandHandler
    except ImportError:
        try:
            from ai_gm_brain_ooc_handler import OOCCommandHandler
        except ImportError:
            try:
                from ai_gm.ai_gm_brain_ooc_handler import OOCCommandHandler
            except ImportError:
                from backend.src.ai_gm.ai_gm_brain_ooc_handler import OOCCommandHandler
    OOC_AVAILABLE = True
except ImportError:
    OOC_AVAILABLE = False

try:
    try:
        from .ai_gm_llm_manager import LLMInteractionManager
    except ImportError:
        try:
            from ai_gm_llm_manager import LLMInteractionManager
        except ImportError:
            try:
                from ai_gm.ai_gm_llm_manager import LLMInteractionManager
            except ImportError:
                from backend.src.ai_gm.ai_gm_llm_manager import LLMInteractionManager
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

try:
    try:
        from .combat_integration import CombatIntegration
    except ImportError:
        try:
            from combat_integration import CombatIntegration
        except ImportError:
            try:
                from ai_gm.combat_integration import CombatIntegration
            except ImportError:
                from backend.src.ai_gm.combat_integration import CombatIntegration
    COMBAT_AVAILABLE = True
except ImportError:
    COMBAT_AVAILABLE = False


class AIGMUnifiedSystem:
    """
    Unified AI GM Brain system that integrates all available components.
    
    This class provides a single interface to the entire AI GM system,
    automatically detecting and integrating available components.
    """
    
    def __init__(self, 
                 game_id: str, 
                 player_id: str,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the unified AI GM system.
        
        Args:
            game_id: The ID of the game session
            player_id: The ID of the player
            config: Optional configuration override
        """
        self.game_id = game_id
        self.player_id = player_id
        self.logger = logging.getLogger(f"AIGMUnified_{game_id}")
        
        # Load configuration
        self.config = config or IntegratedAIGMConfig.get_config()
        
        # Initialize core brain
        self.brain = AIGMBrain(
            game_id=game_id,
            player_id=player_id
        )
        
        # Initialize optimization configuration
        self.optimization_config = get_optimization_config("auto") if OPTIMIZED_WORLD_REACTION_AVAILABLE else None
        
        # Initialize context tracking
        self._context = {}
        self._session_start = datetime.utcnow()
        
        # Track available systems
        self.available_systems = {
            "core_brain": True,
            "world_reaction": WORLD_REACTION_AVAILABLE,
            "optimized_world_reaction": OPTIMIZED_WORLD_REACTION_AVAILABLE,
            "pacing": PACING_AVAILABLE,
            "output": OUTPUT_AVAILABLE,
            "ooc": OOC_AVAILABLE,
            "llm": LLM_AVAILABLE,
            "combat": COMBAT_AVAILABLE
        }
        
        # Initialize available systems
        self._init_extensions()
        
        self.logger.info(f"AI GM Unified System initialized with {sum(self.available_systems.values())} components")
    
    def _init_extensions(self):
        """Initialize all available extension systems."""
        
        # Initialize OOC system if available
        if OOC_AVAILABLE:
            try:
                self.ooc_handler = OOCCommandHandler(self.game_id, self.player_id)
                self.brain.register_extension("ooc_handler", self.ooc_handler)
                self._register_standard_ooc_commands()
                self.logger.info("OOC system initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize OOC system: {e}")
                self.available_systems["ooc"] = False
        
        # Initialize World Reaction system with optimizations if available
        if WORLD_REACTION_AVAILABLE:
            try:
                if OPTIMIZED_WORLD_REACTION_AVAILABLE and self.optimization_config:
                    # Use optimized version with performance enhancements
                    self.world_reaction_integration = extend_ai_gm_brain_with_optimized_world_reaction(
                        self.brain, 
                        self.optimization_config.to_dict()
                    )
                    self.logger.info("Optimized World Reaction system initialized with performance enhancements")
                else:
                    # Fallback to legacy version
                    extend_ai_gm_brain_with_world_reaction(self.brain)
                    self.world_reaction_integration = None
                    self.logger.info("Legacy World Reaction system initialized")
                
                self.available_systems["world_reaction"] = True
                self.available_systems["optimized_world_reaction"] = OPTIMIZED_WORLD_REACTION_AVAILABLE
                
            except Exception as e:
                self.logger.warning(f"Could not initialize World Reaction system: {e}")
                self.available_systems["world_reaction"] = False
                self.available_systems["optimized_world_reaction"] = False
        
        # Initialize Pacing system if available
        if PACING_AVAILABLE:
            try:
                self.pacing = PacingIntegration(self.brain)
                self.brain.register_extension("pacing", self.pacing)
                self.logger.info("Pacing system initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize Pacing system: {e}")
                self.available_systems["pacing"] = False
        
        # Initialize Output system if available
        if OUTPUT_AVAILABLE:
            try:
                self.output = OutputGenerationIntegration(self.game_id, self.player_id)
                self.brain.register_extension("output", self.output)
                self.logger.info("Output system initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize Output system: {e}")
                self.available_systems["output"] = False
        
        # Initialize LLM system if available
        if LLM_AVAILABLE:
            try:
                self.llm_manager = LLMInteractionManager(self.brain)
                self.brain.register_extension("llm_manager", self.llm_manager)
                self.logger.info("LLM system initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize LLM system: {e}")
                self.available_systems["llm"] = False
        
        # Initialize Combat system if available
        if COMBAT_AVAILABLE:
            try:
                self.combat = CombatIntegration(self.game_id, self.player_id)
                self.brain.register_extension("combat", self.combat)
                self.logger.info("Combat system initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize Combat system: {e}")
                self.available_systems["combat"] = False
    
    def _register_standard_ooc_commands(self):
        """Register standard OOC commands if OOC system is available."""
        if not self.available_systems["ooc"]:
            return
        
        # Help command
        self.ooc_handler.register_command("help", {
            "handler": self._handle_help_command,
            "description": "Display available commands",
            "parameters": []
        })
        
        # Status command
        self.ooc_handler.register_command("status", {
            "handler": self._handle_status_command,
            "description": "Display system status",
            "parameters": []
        })
        
        # Stats command
        self.ooc_handler.register_command("stats", {
            "handler": self._handle_stats_command,
            "description": "Display character statistics",
            "parameters": []
        })
        
        # Location command
        self.ooc_handler.register_command("location", {
            "handler": self._handle_location_command,
            "description": "Display current location information",
            "parameters": []
        })
    
    def _handle_help_command(self, args: Dict[str, Any], brain) -> Dict[str, Any]:
        """Handle the help command."""
        if not self.available_systems["ooc"]:
            return {"status": "error", "response": "OOC system not available"}
        
        commands = self.ooc_handler.commands
        help_text = "Available Commands:\n"
        
        for cmd, details in commands.items():
            params = ""
            if details.get("parameters"):
                params = " " + " ".join([f"<{p}>" for p in details.get("parameters", [])])
            
            help_text += f"/{cmd}{params} - {details.get('description', 'No description')}\n"
        
        return {"status": "success", "response": help_text}
    
    def _handle_status_command(self, args: Dict[str, Any], brain) -> Dict[str, Any]:
        """Handle the status command."""
        status_text = f"AI GM System Status (Session: {self.game_id})\n"
        status_text += "=" * 50 + "\n"
        
        for system, available in self.available_systems.items():
            status = "✓ Available" if available else "✗ Unavailable"
            status_text += f"{system.replace('_', ' ').title()}: {status}\n"
        
        # Add session info
        uptime = datetime.utcnow() - self._session_start
        status_text += f"\nSession uptime: {uptime}\n"
        status_text += f"Player ID: {self.player_id}\n"
        
        return {"status": "success", "response": status_text}
    
    def _handle_stats_command(self, args: Dict[str, Any], brain) -> Dict[str, Any]:
        """Handle the stats command."""
        player = self._context.get("player", {})
        if not player:
            return {"status": "error", "response": "No player data available"}
        
        stats_text = f"Character: {player.get('name', 'Unknown')}\n"
        
        # Format domains if available
        domains = player.get("domains", {})
        if domains:
            stats_text += "Domains:\n"
            for domain, value in domains.items():
                stars = "★" * value
                stats_text += f"  {domain}: {value} {stars}\n"
        
        # Add additional stats if available
        for stat_name in ["health", "experience", "reputation"]:
            if stat_name in player:
                stats_text += f"{stat_name.title()}: {player[stat_name]}\n"
        
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
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input through the integrated system.
        
        Args:
            input_text: The player's input text
            
        Returns:
            Comprehensive response with all system outputs
        """
        start_time = time.time()
        
        try:
            # Process through core brain
            core_response = self.brain.process_player_input(input_text)
            
            # Enhanced processing for non-OOC commands
            if core_response.get("metadata", {}).get("processing_mode") != "OOC":
                return self._process_with_integrations(input_text, core_response, start_time)
            else:
                # For OOC commands, just return the core response with formatting
                return self._format_ooc_response(core_response, start_time)
                
        except Exception as e:
            self.logger.error(f"Error processing player input: {e}")
            return {
                "status": "error",
                "response_text": f"An error occurred processing your input: {str(e)}",
                "metadata": {
                    "error": True,
                    "processing_time": time.time() - start_time
                }
            }
    
    async def process_player_input_async(self, input_text: str) -> Dict[str, Any]:
        """
        Async version of process_player_input with full integration support.
        
        Args:
            input_text: The player's input text
            
        Returns:
            Comprehensive response with all system outputs
        """
        start_time = time.time()
        
        try:
            # Process through core brain
            core_response = self.brain.process_player_input(input_text)
            
            # Enhanced processing for non-OOC commands
            if core_response.get("metadata", {}).get("processing_mode") != "OOC":
                return await self._process_with_integrations_async(input_text, core_response, start_time)
            else:
                # For OOC commands, just return the core response with formatting
                return self._format_ooc_response(core_response, start_time)
                
        except Exception as e:
            self.logger.error(f"Error processing player input: {e}")
            return {
                "status": "error",
                "response_text": f"An error occurred processing your input: {str(e)}",
                "metadata": {
                    "error": True,
                    "processing_time": time.time() - start_time
                }
            }
    
    def _process_with_integrations(self, input_text: str, core_response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Process input with all available integrations (synchronous)."""
        response_text = core_response["response_text"]
        metadata = core_response["metadata"]
        
        # World Reaction processing
        world_reaction = None
        if self.available_systems["world_reaction"]:
            try:
                world_reaction = self.brain.assess_world_reaction(
                    player_input=input_text,
                    context=self._context
                )
                
                if world_reaction and world_reaction.get("success", False):
                    reaction_text = world_reaction.get("reaction_data", {}).get("response", "")
                    if reaction_text:
                        response_text += f"\n\n{reaction_text}"
            except Exception as e:
                self.logger.warning(f"World reaction processing failed: {e}")
        
        # Pacing processing
        pacing_update = None
        ambient_content = None
        if self.available_systems["pacing"]:
            try:
                pacing_update = self.pacing.update_pacing_state(
                    player_input=input_text,
                    response_data=core_response
                )
                
                # Check for ambient content
                ambient_content = self.pacing.check_for_ambient_content()
                if ambient_content:
                    ambient_text = ambient_content.get("content", "")
                    if ambient_text:
                        response_text += f"\n\n{ambient_text}"
            except Exception as e:
                self.logger.warning(f"Pacing processing failed: {e}")
        
        # Output formatting
        formatted_response = None
        if self.available_systems["output"]:
            try:
                # Determine output type
                output_type = OutputType.NARRATIVE
                if "dialogue" in metadata.get("tags", []):
                    output_type = OutputType.DIALOGUE
                elif "combat" in metadata.get("tags", []):
                    output_type = OutputType.COMBAT
                elif "description" in metadata.get("tags", []):
                    output_type = OutputType.DESCRIPTION
                
                formatted_response = self.output.deliver_response(
                    response_text=response_text,
                    output_type=output_type,
                    channels=[DeliveryChannel.CONSOLE],
                    priority=ResponsePriority.NORMAL,
                    metadata=metadata
                )
            except Exception as e:
                self.logger.warning(f"Output formatting failed: {e}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return {
            "status": "success",
            "response_text": response_text,
            "metadata": {
                **metadata,
                "processing_time_total": processing_time,
                "integrations": {
                    "world_reaction": world_reaction is not None,
                    "pacing_update": pacing_update is not None,
                    "ambient_content": ambient_content is not None,
                    "output_formatted": formatted_response is not None
                }
            },
            "formatted_response": formatted_response,
            "world_reaction": world_reaction,
            "pacing_update": pacing_update,
            "ambient_content": ambient_content
        }
    
    async def _process_with_integrations_async(self, input_text: str, core_response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Process input with all available integrations (asynchronous)."""
        response_text = core_response["response_text"]
        metadata = core_response["metadata"]
        
        # World Reaction processing (async)
        world_reaction = None
        if self.available_systems["world_reaction"]:
            try:
                world_reaction = self.brain.assess_world_reaction(
                    player_input=input_text,
                    context=self._context
                )
                
                if world_reaction and world_reaction.get("success", False):
                    reaction_text = world_reaction.get("reaction_data", {}).get("response", "")
                    if reaction_text:
                        response_text += f"\n\n{reaction_text}"
            except Exception as e:
                self.logger.warning(f"World reaction processing failed: {e}")
        
        # Pacing processing (async)
        pacing_update = None
        ambient_content = None
        if self.available_systems["pacing"]:
            try:
                pacing_update = self.pacing.update_pacing_state(
                    player_input=input_text,
                    response_data=core_response
                )
                
                # Check for ambient content (async)
                if hasattr(self.pacing, 'check_for_ambient_content_async'):
                    ambient_content = await self.pacing.check_for_ambient_content_async(self._context)
                else:
                    ambient_content = self.pacing.check_for_ambient_content()
                    
                if ambient_content:
                    ambient_text = ambient_content.get("content", "")
                    if ambient_text:
                        response_text += f"\n\n{ambient_text}"
            except Exception as e:
                self.logger.warning(f"Pacing processing failed: {e}")
        
        # LLM enhancement if available and needed
        if self.available_systems["llm"] and metadata.get("complexity") == "COMPLEX":
            try:
                llm_enhancement = await self.llm_manager.enhance_response(
                    original_response=response_text,
                    input_text=input_text,
                    context=self._context
                )
                if llm_enhancement:
                    response_text = llm_enhancement.get("enhanced_text", response_text)
            except Exception as e:
                self.logger.warning(f"LLM enhancement failed: {e}")
        
        # Output formatting
        formatted_response = None
        if self.available_systems["output"]:
            try:
                # Determine output type
                output_type = OutputType.NARRATIVE
                if "dialogue" in metadata.get("tags", []):
                    output_type = OutputType.DIALOGUE
                elif "combat" in metadata.get("tags", []):
                    output_type = OutputType.COMBAT
                elif "description" in metadata.get("tags", []):
                    output_type = OutputType.DESCRIPTION
                
                formatted_response = self.output.deliver_response(
                    response_text=response_text,
                    output_type=output_type,
                    channels=[DeliveryChannel.CONSOLE],
                    priority=ResponsePriority.NORMAL,
                    metadata=metadata
                )
            except Exception as e:
                self.logger.warning(f"Output formatting failed: {e}")
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return {
            "status": "success",
            "response_text": response_text,
            "metadata": {
                **metadata,
                "processing_time_total": processing_time,
                "integrations": {
                    "world_reaction": world_reaction is not None,
                    "pacing_update": pacing_update is not None,
                    "ambient_content": ambient_content is not None,
                    "output_formatted": formatted_response is not None
                }
            },
            "formatted_response": formatted_response,
            "world_reaction": world_reaction,
            "pacing_update": pacing_update,
            "ambient_content": ambient_content
        }
    
    def _format_ooc_response(self, core_response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Format OOC command responses."""
        processing_time = time.time() - start_time
        
        formatted_response = None
        if self.available_systems["output"]:
            try:
                formatted_response = self.output.deliver_response(
                    response_text=core_response["response_text"],
                    output_type=OutputType.SYSTEM,
                    channels=[DeliveryChannel.CONSOLE],
                    priority=ResponsePriority.IMMEDIATE,
                    metadata=core_response["metadata"]
                )
            except Exception as e:
                self.logger.warning(f"OOC output formatting failed: {e}")
        
        return {
            "status": "success",
            "response_text": core_response["response_text"],
            "metadata": {
                **core_response["metadata"],
                "processing_time_total": processing_time,
                "ooc_command": True
            },
            "formatted_response": formatted_response
        }
    
    def update_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the game context.
        
        Args:
            context_update: The context updates to apply
            
        Returns:
            Updated context
        """
        self._context.update(context_update)
        return self._context.copy()
    
    def get_context(self) -> Dict[str, Any]:
        """Get the current game context."""
        return self._context.copy()
    
    def set_initial_context(self, initial_context: Dict[str, Any]) -> Dict[str, Any]:
        """Set the initial game context."""
        self._context = initial_context.copy()
        return self._context.copy()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        brain_stats = {}
        if hasattr(self.brain, 'stats'):
            for stat_type, value in self.brain.stats.items():
                brain_stats[stat_type] = value
        
        return {
            "game_id": self.game_id,
            "player_id": self.player_id,
            "session_start": self._session_start.isoformat(),
            "uptime": str(datetime.utcnow() - self._session_start),
            "available_systems": self.available_systems,
            "brain_stats": brain_stats,
            "extensions": list(self.brain.extensions.keys()) if hasattr(self.brain, 'extensions') else []
        }
    
    def get_integration_statistics(self) -> Dict[str, Any]:
        """Get statistics from all integrated systems."""
        stats = {
            "core_brain": self.brain.get_processing_statistics() if hasattr(self.brain, 'get_processing_statistics') else {},
            "available_systems": self.available_systems
        }
        
        # Add statistics from each available system
        if self.available_systems["world_reaction"] and hasattr(self.brain, 'reaction_assessor') and hasattr(self.brain.reaction_assessor, 'get_statistics'):
            stats["world_reaction"] = self.brain.reaction_assessor.get_statistics()
        
        if self.available_systems["pacing"] and hasattr(self.pacing, 'get_pacing_statistics'):
            stats["pacing"] = self.pacing.get_pacing_statistics()
        
        if self.available_systems["output"] and hasattr(self.output, 'get_statistics'):
            stats["output"] = self.output.get_statistics()
        
        if self.available_systems["combat"] and hasattr(self.combat, 'get_statistics'):
            stats["combat"] = self.combat.get_statistics()
        
        return stats

# Performance Monitoring and Optimization Methods
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """
        Get comprehensive performance report from all optimization systems.
        
        Returns:
            Dictionary containing performance metrics and recommendations
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": {
                "game_id": self.game_id,
                "player_id": self.player_id,
                "session_duration": (datetime.utcnow() - self._session_start).total_seconds(),
                "available_systems": self.available_systems.copy(),
                "optimization_enabled": self.available_systems.get("optimized_world_reaction", False)
            }
        }

        # Get optimization report if available
        if (self.available_systems.get("optimized_world_reaction", False) and 
            hasattr(self.brain, 'get_optimization_performance_report')):
            try:
                optimization_report = await self.brain.get_optimization_performance_report()
                report["optimization_performance"] = optimization_report
            except Exception as e:
                self.logger.warning(f"Could not retrieve optimization performance report: {e}")
                report["optimization_performance"] = {"error": str(e)}

        # Get world reaction statistics if available
        if (self.available_systems.get("world_reaction", False) and 
            hasattr(self.brain, 'get_world_reaction_statistics')):
            try:
                wr_stats = self.brain.get_world_reaction_statistics()
                report["world_reaction_stats"] = wr_stats
            except Exception as e:
                self.logger.warning(f"Could not retrieve world reaction statistics: {e}")
                report["world_reaction_stats"] = {"error": str(e)}

        # Add recommendations
        report["recommendations"] = self._generate_system_recommendations(report)

        return report
    
    def get_performance_report_sync(self) -> Dict[str, Any]:
        """
        Synchronous version of get_performance_report for compatibility.
        
        Returns:
            Dictionary containing performance metrics and recommendations
        """
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_info": {
                "game_id": self.game_id,
                "player_id": self.player_id,
                "session_duration": (datetime.utcnow() - self._session_start).total_seconds(),
                "available_systems": self.available_systems.copy(),
                "optimization_enabled": self.available_systems.get("optimized_world_reaction", False)
            }
        }

        # Get world reaction statistics if available (sync version)
        if (self.available_systems.get("world_reaction", False) and 
            hasattr(self.brain, 'get_world_reaction_statistics')):
            try:
                wr_stats = self.brain.get_world_reaction_statistics()
                report["world_reaction_stats"] = wr_stats
            except Exception as e:
                self.logger.warning(f"Could not retrieve world reaction statistics: {e}")
                report["world_reaction_stats"] = {"error": str(e)}

        # Add recommendations
        report["recommendations"] = self._generate_system_recommendations(report)

        return report
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """
        Get current optimization status and configuration.
        
        Returns:
            Dictionary containing optimization status information
        """
        status = {
            "optimization_enabled": self.available_systems.get("optimized_world_reaction", False),
            "optimization_config": self.optimization_config.to_dict() if self.optimization_config else None,
            "available_systems": self.available_systems.copy(),
            "performance_features": {
                "async_processing": hasattr(self.brain, 'process_player_input_async'),
                "world_reaction_optimization": hasattr(self.brain, 'assess_world_reaction_optimized'),
                "batch_processing": hasattr(self.brain, 'assess_batch_world_reactions'),
                "performance_monitoring": hasattr(self.brain, 'get_optimization_performance_report')
            }
        }
        
        # Get optimization status from brain if available
        if hasattr(self.brain, 'get_optimization_status'):
            try:
                brain_status = self.brain.get_optimization_status()
                status["brain_optimization_status"] = brain_status
            except Exception as e:
                self.logger.warning(f"Could not retrieve brain optimization status: {e}")
                status["brain_optimization_status"] = {"error": str(e)}
        
        return status
    
    def adjust_optimization_setting(self, setting: str, value: Any) -> bool:
        """
        Adjust an optimization setting at runtime.
        
        Args:
            setting: The setting name to adjust
            value: The new value for the setting
            
        Returns:
            True if the adjustment was successful, False otherwise
        """
        if not self.optimization_config:
            self.logger.warning("No optimization configuration available for runtime adjustment")
            return False
        
        try:
            # Update configuration
            if hasattr(self.optimization_config, setting):
                setattr(self.optimization_config, setting, value)
                
                # Update world reaction integration if available
                if (self.world_reaction_integration and 
                    hasattr(self.world_reaction_integration, 'optimizer')):
                    config_dict = self.optimization_config.to_dict()
                    # Update the integration's configuration
                    # This would require the integration to support runtime updates
                    
                self.logger.info(f"Optimization setting '{setting}' adjusted to: {value}")
                return True
            else:
                self.logger.warning(f"Unknown optimization setting: {setting}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error adjusting optimization setting: {e}")
            return False
    
    async def optimize_for_performance_mode(self, mode: str) -> bool:
        """
        Optimize the system for a specific performance mode.
        
        Args:
            mode: Performance mode ("fast", "balanced", "quality")
            
        Returns:
            True if optimization was successful
        """
        if not self.optimization_config:
            self.logger.warning("No optimization configuration available")
            return False
        
        try:
            # Update quality mode
            self.optimization_config.quality_mode = mode
            
            # Adjust related settings based on mode
            if mode == "fast":
                self.optimization_config.max_concurrent_reactions = 12
                self.optimization_config.reaction_timeout = 2.0
                self.optimization_config.prefer_cache_over_accuracy = True
                self.optimization_config.fallback_threshold = 0.6
            elif mode == "balanced":
                self.optimization_config.max_concurrent_reactions = 8
                self.optimization_config.reaction_timeout = 4.0
                self.optimization_config.prefer_cache_over_accuracy = False
                self.optimization_config.fallback_threshold = 0.8
            elif mode == "quality":
                self.optimization_config.max_concurrent_reactions = 5
                self.optimization_config.reaction_timeout = 8.0
                self.optimization_config.prefer_cache_over_accuracy = False
                self.optimization_config.fallback_threshold = 0.9
            
            self.logger.info(f"System optimized for '{mode}' performance mode")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing for performance mode: {e}")
            return False
    
    def _generate_system_recommendations(self, performance_report: Dict[str, Any]) -> List[str]:
        """
        Generate system optimization recommendations based on performance data.
        
        Args:
            performance_report: Current performance report data
            
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Check if optimizations are available but not enabled
        if not self.available_systems.get("optimized_world_reaction", False):
            recommendations.append(
                "Consider enabling optimized world reaction system for better performance"
            )
        
        # Check system availability
        available_count = sum(self.available_systems.values())
        total_systems = len(self.available_systems)
        
        if available_count < total_systems:
            missing_systems = [name for name, available in self.available_systems.items() if not available]
            recommendations.append(
                f"Some systems are unavailable: {', '.join(missing_systems)}. "
                f"Check dependencies and configuration."
            )
        
        # Performance-based recommendations
        optimization_perf = performance_report.get("optimization_performance", {})
        if optimization_perf and not isinstance(optimization_perf, dict) or optimization_perf.get("error"):
            recommendations.append(
                "Optimization performance monitoring is not working properly. Check system health."
            )
        
        # Session duration recommendations
        session_duration = performance_report.get("system_info", {}).get("session_duration", 0)
        if session_duration > 3600:  # More than 1 hour
            recommendations.append(
                "Long session detected. Consider periodic cache cleanup and performance monitoring."
            )
        
        return recommendations
    
    async def run_performance_benchmark(self, test_inputs: List[str] = None) -> Dict[str, Any]:
        """
        Run a performance benchmark to evaluate system performance.
        
        Args:
            test_inputs: Optional list of test inputs to benchmark with
            
        Returns:
            Benchmark results dictionary
        """
        if not test_inputs:
            test_inputs = [
                "look around",
                "say hello to everyone",
                "examine the mysterious object",
                "ask the merchant about prices",
                "check my inventory"
            ]
        
        benchmark_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_inputs": test_inputs,
            "results": []
        }
        
        total_start_time = time.time()
        
        for i, test_input in enumerate(test_inputs):
            test_start_time = time.time()
            
            try:
                # Test async processing if available
                if hasattr(self, 'process_player_input_async'):
                    result = await self.process_player_input_async(test_input)
                else:
                    result = self.process_player_input(test_input)
                
                test_duration = time.time() - test_start_time
                
                benchmark_results["results"].append({
                    "input": test_input,
                    "duration": test_duration,
                    "success": result.get("status") != "error",
                    "response_length": len(result.get("response_text", "")),
                    "world_reaction_applied": result.get("metadata", {}).get("world_reaction") is not None,
                    "optimization_stats": result.get("metadata", {}).get("world_reaction_optimization")
                })
                
            except Exception as e:
                benchmark_results["results"].append({
                    "input": test_input,
                    "duration": time.time() - test_start_time,
                    "success": False,
                    "error": str(e)
                })
        
        # Calculate summary statistics
        successful_tests = [r for r in benchmark_results["results"] if r.get("success", False)]
        
        if successful_tests:
            durations = [r["duration"] for r in successful_tests]
            benchmark_results["summary"] = {
                "total_duration": time.time() - total_start_time,
                "successful_tests": len(successful_tests),
                "failed_tests": len(benchmark_results["results"]) - len(successful_tests),
                "average_duration": sum(durations) / len(durations),
                "min_duration": min(durations),
                "max_duration": max(durations),
                "optimization_usage": sum(1 for r in successful_tests 
                                        if r.get("world_reaction_applied", False)) / len(successful_tests)
            }
        else:
            benchmark_results["summary"] = {
                "total_duration": time.time() - total_start_time,
                "successful_tests": 0,
                "failed_tests": len(benchmark_results["results"]),
                "error": "All benchmark tests failed"
            }
        
        return benchmark_results


# Convenience function for easy system creation
def create_unified_gm(game_id: str, player_id: str, initial_context: Optional[Dict[str, Any]] = None, config: Optional[Dict[str, Any]] = None) -> AIGMUnifiedSystem:
    """
    Create a unified AI GM system with all available integrations.
    
    Args:
        game_id: The ID of the game session
        player_id: The ID of the player
        initial_context: Optional initial context
        config: Optional configuration override
        
    Returns:
        Created AIGMUnifiedSystem instance
    """
    unified_gm = AIGMUnifiedSystem(game_id, player_id, config)
    
    if initial_context:
        unified_gm.set_initial_context(initial_context)
    
    return unified_gm


# Factory function for different AI GM configurations
def create_gm_for_environment(environment: str, game_id: str, player_id: str) -> AIGMUnifiedSystem:
    """
    Create an AI GM configured for a specific environment.
    
    Args:
        environment: The environment type ("development", "production", "testing")
        game_id: The ID of the game session
        player_id: The ID of the player
        
    Returns:
        Configured AIGMUnifiedSystem instance
    """
    if environment == "development":
        config = IntegratedAIGMConfig.get_development_config()
    elif environment == "production":
        config = IntegratedAIGMConfig.get_production_config()
    elif environment == "testing":
        config = IntegratedAIGMConfig.get_testing_config()
    else:
        config = IntegratedAIGMConfig.get_config()
    
    return AIGMUnifiedSystem(game_id, player_id, config)
