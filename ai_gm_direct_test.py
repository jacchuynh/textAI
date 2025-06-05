#!/usr/bin/env python3
"""
Direct AI GM Brain Integration Test

This script provides a direct test of the AI GM unified integration system
without relying on the component imports, which helps isolate integration logic.
"""

import os
import sys
import logging
import json
from typing import Dict, Any, List, Optional
from enum import Enum, auto
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_src = os.path.join(current_dir, 'backend', 'src')
attached_assets = os.path.join(current_dir, 'attached_assets')

# Add to Python path
sys.path.insert(0, backend_src)
sys.path.insert(0, attached_assets)
sys.path.insert(0, current_dir)

# Define enums and mock classes needed for testing
class ProcessingMode(Enum):
    NORMAL = auto()
    OOC = auto()
    SYSTEM = auto()
    AMBIENT = auto()

class InputComplexity(Enum):
    SIMPLE_COMMAND = auto()
    COMPLEX_COMMAND = auto()
    CONVERSATION = auto()
    COMPLEX_QUERY = auto()
    OOC_COMMAND = auto()

class ActionSignificance(Enum):
    MINOR = auto()
    MODERATE = auto()
    MAJOR = auto()
    CRITICAL = auto()

class ReputationLevel(Enum):
    HOSTILE = auto()
    UNFRIENDLY = auto()
    NEUTRAL = auto()
    FRIENDLY = auto()
    ALLIED = auto()

class OutputType(Enum):
    NARRATIVE = auto()
    DIALOGUE = auto()
    DESCRIPTION = auto()
    COMBAT = auto()
    SYSTEM = auto()

class DeliveryChannel(Enum):
    CONSOLE = auto()
    UI = auto()
    AUDIO = auto()
    VISUAL = auto()

class ResponsePriority(Enum):
    LOW = auto()
    NORMAL = auto()
    HIGH = auto()
    IMMEDIATE = auto()

# Mock AI GM Brain class to avoid import issues
class MockAIGMBrain:
    """Mock implementation of AIGMBrain for testing."""
    
    def __init__(self, game_id: str, player_id: str):
        self.game_id = game_id
        self.player_id = player_id
        self.extensions = {}
        self.stats = {
            "inputs_processed": 0,
            "ooc_commands": 0,
            "normal_commands": 0,
            "last_processing_time": 0
        }
    
    def register_extension(self, name: str, extension: Any):
        """Register an extension module."""
        self.extensions[name] = extension
        print(f"Registered extension: {name}")
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """Process player input."""
        self.stats["inputs_processed"] += 1
        
        # Check if this is an OOC command
        if input_text.startswith('/'):
            self.stats["ooc_commands"] += 1
            
            # Handle OOC commands
            if 'ooc_handler' in self.extensions:
                handler = self.extensions['ooc_handler']
                if hasattr(handler, 'process_command'):
                    result = handler.process_command(input_text, self)
                    if result:
                        return {
                            "status": "success",
                            "response_text": result.get('response', 'Command processed.'),
                            "metadata": {
                                "processing_mode": "OOC",
                                "complexity": "OOC_COMMAND",
                                "ooc_command": input_text.split()[0][1:] if ' ' in input_text else input_text[1:],
                                "tags": ["ooc", "system"]
                            }
                        }
            
            # Default OOC response
            return {
                "status": "success",
                "response_text": f"OOC Command: {input_text}",
                "metadata": {
                    "processing_mode": "OOC",
                    "complexity": "OOC_COMMAND",
                    "tags": ["ooc", "system"]
                }
            }
        else:
            # Regular command processing
            self.stats["normal_commands"] += 1
            
            # Generate a response based on the input
            if "look" in input_text.lower():
                response_text = "You look around and see a testing environment with various components of the AI GM system."
                tags = ["description", "observation"]
                complexity = InputComplexity.SIMPLE_COMMAND
            elif "go" in input_text.lower() or "move" in input_text.lower():
                response_text = "You attempt to move in that direction, but find yourself still in the test environment."
                tags = ["movement", "action"]
                complexity = InputComplexity.SIMPLE_COMMAND
            elif any(word in input_text.lower() for word in ["talk", "speak", "ask", "tell"]):
                response_text = "You attempt to communicate, but there's no one here to respond yet. The integration system acknowledges your attempt."
                tags = ["dialogue", "social"]
                complexity = InputComplexity.CONVERSATION
            elif "?" in input_text:
                response_text = "That's an interesting question about the test environment. The AI GM system would normally process this as a complex query."
                tags = ["question", "information"]
                complexity = InputComplexity.COMPLEX_QUERY
            else:
                response_text = f"The AI GM system processes your input: '{input_text}' and prepares an appropriate response based on the context."
                tags = ["action", "generic"]
                complexity = InputComplexity.COMPLEX_COMMAND
            
            return {
                "status": "success",
                "response_text": response_text,
                "metadata": {
                    "processing_mode": "NORMAL",
                    "complexity": complexity.name,
                    "tags": tags,
                    "input_text": input_text
                }
            }

# Mock integration components
class MockWorldReaction:
    """Mock implementation of WorldReactionIntegration."""
    
    def __init__(self, brain):
        self.brain = brain
        print("World Reaction system initialized")
    
    def assess_reaction(self, player_id, player_input, context):
        """Assess world reaction to player input."""
        if "aggressive" in player_input.lower():
            significance = ActionSignificance.MAJOR
            reaction = "The world seems to react negatively to your aggressive action."
        elif "friendly" in player_input.lower():
            significance = ActionSignificance.MODERATE
            reaction = "The environment seems to respond positively to your friendly approach."
        else:
            significance = ActionSignificance.MINOR
            reaction = "The world takes minimal notice of your action."
        
        return {
            "success": True,
            "reaction_data": {
                "significance": significance.name,
                "response": reaction,
                "affected_entities": []
            }
        }

class MockPacing:
    """Mock implementation of PacingIntegration."""
    
    def __init__(self, brain):
        self.brain = brain
        self.pacing_state = "NORMAL"
        print("Pacing system initialized")
    
    def update_pacing_state(self, player_input, response_data):
        """Update the pacing state based on player input."""
        # Simple logic to adjust pacing
        if "quickly" in player_input.lower() or "hurry" in player_input.lower():
            self.pacing_state = "ACCELERATED"
        elif "slowly" in player_input.lower() or "careful" in player_input.lower():
            self.pacing_state = "DELIBERATE"
        else:
            self.pacing_state = "NORMAL"
        
        return {
            "success": True,
            "pacing_state": self.pacing_state,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def check_for_ambient_content(self):
        """Check if ambient content should be generated."""
        # 20% chance of ambient content for testing
        import random
        if random.random() < 0.2:
            return {
                "content": "You notice the soft hum of the test environment around you, a reminder that this is just a simulation.",
                "content_type": "ambient",
                "priority": "low"
            }
        return None

class MockOutput:
    """Mock implementation of OutputGenerationIntegration."""
    
    def __init__(self, brain):
        self.brain = brain
        print("Output system initialized")
    
    def deliver_response(self, response_text, output_type, channels, priority, metadata):
        """Format and deliver the response."""
        formatted = f"[{output_type.name}] {response_text}"
        
        # Add styling based on output type
        if output_type == OutputType.DIALOGUE:
            formatted = f"DIALOGUE: \"{response_text}\""
        elif output_type == OutputType.COMBAT:
            formatted = f"COMBAT: ** {response_text} **"
        elif output_type == OutputType.SYSTEM:
            formatted = f"SYSTEM: {response_text}"
        
        return {
            "formatted_text": formatted,
            "raw_text": response_text,
            "channels": [ch.name for ch in channels],
            "delivery_status": "success"
        }

class MockOOCHandler:
    """Mock implementation of OOCCommandHandler."""
    
    def __init__(self, brain):
        self.brain = brain
        self.commands = {}
        print("OOC command handler initialized")
    
    def register_command(self, command, config):
        """Register an OOC command."""
        self.commands[command] = config
    
    def process_command(self, input_text, brain):
        """Process an OOC command."""
        parts = input_text.strip().split()
        command = parts[0][1:]  # Remove the leading /
        args = parts[1:] if len(parts) > 1 else []
        
        if command in self.commands:
            handler = self.commands[command].get("handler")
            if handler:
                return handler({"args": args}, brain)
            else:
                return {"status": "success", "response": f"Command /{command} recognized but no handler defined."}
        else:
            return {"status": "error", "response": f"Unknown command: /{command}"}

# Main class that implements the unified integration
class AIGMUnifiedSystem:
    """
    Unified AI GM Brain system that integrates all available components.
    """
    
    def __init__(self, game_id: str, player_id: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the unified AI GM system."""
        self.game_id = game_id
        self.player_id = player_id
        self.logger = logging.getLogger(f"AIGMUnified_{game_id}")
        
        # Initialize configuration
        self.config = config or {"integration": {"debug_mode": True}}
        
        # Initialize core brain
        self.brain = MockAIGMBrain(game_id=game_id, player_id=player_id)
        
        # Initialize context tracking
        self._context = {}
        self._session_start = datetime.utcnow()
        
        # Initialize available systems
        self.world_reaction = MockWorldReaction(self.brain)
        self.pacing = MockPacing(self.brain)
        self.output = MockOutput(self.brain)
        self.ooc_handler = MockOOCHandler(self.brain)
        
        # Register extensions with the brain
        self.brain.register_extension("world_reaction", self.world_reaction)
        self.brain.register_extension("pacing", self.pacing)
        self.brain.register_extension("output", self.output)
        self.brain.register_extension("ooc_handler", self.ooc_handler)
        
        # Register standard OOC commands
        self._register_standard_ooc_commands()
        
        # Track available systems
        self.available_systems = {
            "core_brain": True,
            "world_reaction": True,
            "pacing": True,
            "output": True,
            "ooc": True
        }
        
        self.logger.info(f"AI GM Unified System initialized with {sum(self.available_systems.values())} components")
    
    def _register_standard_ooc_commands(self):
        """Register standard OOC commands."""
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
        """Process player input through the integrated system."""
        import time
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
    
    def _process_with_integrations(self, input_text: str, core_response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Process input with all available integrations."""
        import time
        response_text = core_response["response_text"]
        metadata = core_response["metadata"]
        
        # World Reaction processing
        world_reaction = self.world_reaction.assess_reaction(
            player_id=self.player_id,
            player_input=input_text,
            context=self._context
        )
        
        if world_reaction and world_reaction.get("success", False):
            reaction_text = world_reaction.get("reaction_data", {}).get("response", "")
            if reaction_text:
                response_text += f"\n\n{reaction_text}"
        
        # Pacing processing
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
        
        # Output formatting
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
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        return {
            "status": "success",
            "response_text": response_text,
            "formatted_text": formatted_response.get("formatted_text", response_text),
            "metadata": {
                **metadata,
                "processing_time_total": processing_time,
                "integrations": {
                    "world_reaction": True,
                    "pacing_update": True,
                    "ambient_content": ambient_content is not None,
                    "output_formatted": True
                }
            },
            "formatted_response": formatted_response,
            "world_reaction": world_reaction,
            "pacing_update": pacing_update,
            "ambient_content": ambient_content
        }
    
    def _format_ooc_response(self, core_response: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """Format OOC command responses."""
        import time
        processing_time = time.time() - start_time
        
        formatted_response = self.output.deliver_response(
            response_text=core_response["response_text"],
            output_type=OutputType.SYSTEM,
            channels=[DeliveryChannel.CONSOLE],
            priority=ResponsePriority.IMMEDIATE,
            metadata=core_response["metadata"]
        )
        
        return {
            "status": "success",
            "response_text": core_response["response_text"],
            "formatted_text": formatted_response.get("formatted_text", core_response["response_text"]),
            "metadata": {
                **core_response["metadata"],
                "processing_time_total": processing_time,
                "ooc_command": True
            },
            "formatted_response": formatted_response
        }
    
    def update_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        """Update the game context."""
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
        return {
            "game_id": self.game_id,
            "player_id": self.player_id,
            "session_start": self._session_start.isoformat(),
            "uptime": str(datetime.utcnow() - self._session_start),
            "available_systems": self.available_systems,
            "brain_stats": self.brain.stats,
            "extensions": list(self.brain.extensions.keys())
        }

def create_unified_gm(game_id: str, player_id: str, initial_context: Optional[Dict[str, Any]] = None) -> AIGMUnifiedSystem:
    """Create a unified AI GM system."""
    unified_gm = AIGMUnifiedSystem(game_id, player_id)
    
    if initial_context:
        unified_gm.set_initial_context(initial_context)
    
    return unified_gm

def demonstrate_direct_usage():
    """Demonstrate direct usage of the AIGMUnifiedSystem."""
    print("=" * 60)
    print("AI GM Unified Integration - Direct Implementation Test")
    print("=" * 60)
    
    # Create a unified GM system
    print("🔧 Creating unified AI GM system...")
    gm = create_unified_gm(
        game_id="direct_demo_001",
        player_id="direct_player",
        initial_context={
            "player": {
                "name": "Test Character",
                "domains": {"Combat": 3, "Social": 2, "Knowledge": 4},
                "health": 100,
                "experience": 150
            },
            "current_location": "Test Laboratory",
            "location_description": "A sterile laboratory filled with AI testing equipment and simulated game environments.",
            "active_npcs": ["AI Assistant", "System Monitor", "Test Coordinator"]
        }
    )
    
    # Show system status
    print("📊 System Status:")
    status = gm.get_system_status()
    print(f"   Game ID: {status['game_id']}")
    print(f"   Player ID: {status['player_id']}")
    print(f"   Available Systems:")
    for system, available in status['available_systems'].items():
        icon = "✅" if available else "❌"
        print(f"     {icon} {system.replace('_', ' ').title()}")
    
    # Test various input types
    test_inputs = [
        # OOC Commands
        "/help",
        "/status", 
        "/stats",
        "/location",
        
        # Simple commands
        "look around",
        "go north",
        
        # Conversational inputs
        "What is this place?",
        "Who are the NPCs here?",
        
        # Action commands with reaction triggers
        "friendly greet the AI Assistant",
        "aggressive push the System Monitor"
    ]
    
    print(f"\n🎮 Testing {len(test_inputs)} different input types...")
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n--- Test {i}: '{input_text}' ---")
        
        try:
            response = gm.process_player_input(input_text)
            
            # Display formatted response if available
            if "formatted_text" in response:
                print(f"Response: {response['formatted_text']}")
            else:
                print(f"Response: {response['response_text']}")
            
            # Show metadata for debugging
            metadata = response.get('metadata', {})
            if metadata:
                print(f"Processing Mode: {metadata.get('processing_mode', 'Unknown')}")
                print(f"Processing Time: {metadata.get('processing_time_total', 0):.3f}s")
                
                integrations = metadata.get('integrations', {})
                if integrations:
                    active_integrations = [k for k, v in integrations.items() if v]
                    if active_integrations:
                        print(f"Active Integrations: {', '.join(active_integrations)}")
            
            # Show world reaction if present
            world_reaction = response.get('world_reaction')
            if world_reaction and world_reaction.get("success"):
                reaction_data = world_reaction.get("reaction_data", {})
                significance = reaction_data.get("significance", "UNKNOWN")
                print(f"World Reaction (Significance: {significance})")
            
        except Exception as e:
            print(f"❌ Error processing input: {e}")
    
    print("\n✅ Direct implementation test completed successfully")

def main():
    """Run the direct implementation test."""
    print("🚀 AI GM Brain Direct Integration Test")
    
    try:
        demonstrate_direct_usage()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
