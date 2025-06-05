"""
Out-of-Character (OOC) Command Handler for AI GM Brain

This module handles OOC commands from players, providing game administration,
help information, and meta-game functionality.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime

class OOCCommandType(Enum):
    """Types of OOC commands."""
    HELP = auto()           # Help and information
    STATUS = auto()         # System status
    SETTINGS = auto()       # Player settings
    ADMIN = auto()          # Administrative commands
    DEBUG = auto()          # Debug commands
    GAME_CONTROL = auto()   # Game control (save, load, etc.)
    SOCIAL = auto()         # Social commands (who, tell, etc.)

@dataclass
class OOCCommand:
    """Represents an OOC command."""
    command: str
    args: List[str]
    command_type: OOCCommandType
    player_id: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "command": self.command,
            "args": self.args,
            "command_type": self.command_type.name,
            "player_id": self.player_id,
            "timestamp": self.timestamp.isoformat()
        }

class OOCCommandHandler:
    """Handles out-of-character commands from players."""
    
    def __init__(self, game_id: str, player_id: str):
        self.game_id = game_id
        self.player_id = player_id
        self.logger = logging.getLogger(__name__)
        self.command_history: List[OOCCommand] = []
        self.command_handlers: Dict[str, Callable] = {}
        self.admin_players: List[str] = []  # List of admin player IDs
        
        # Register default command handlers
        self._register_default_handlers()
        
        self.logger.info(f"OOC Command Handler initialized for game {game_id} and player {player_id}")
    
    def _register_default_handlers(self):
        """Register default OOC command handlers."""
        self.command_handlers.update({
            "help": self._handle_help,
            "h": self._handle_help,
            "?": self._handle_help,
            "status": self._handle_status,
            "time": self._handle_time,
            "uptime": self._handle_uptime,
            "commands": self._handle_commands,
            "who": self._handle_who,
            "quit": self._handle_quit,
            "save": self._handle_save,
            "load": self._handle_load,
            "settings": self._handle_settings,
            "debug": self._handle_debug,
            "stats": self._handle_stats,
            "clear": self._handle_clear,
            "version": self._handle_version
        })
    
    def register_command(self, command: str, handler: Callable, command_type: OOCCommandType = OOCCommandType.HELP):
        """Register a new OOC command handler."""
        self.command_handlers[command.lower()] = handler
        self.logger.info(f"Registered OOC command: {command}")
    
    def is_ooc_command(self, input_text: str) -> bool:
        """Check if input is an OOC command."""
        stripped = input_text.strip()
        return stripped.startswith(('/', '.', '!')) or stripped.lower().startswith('ooc ')
    
    def parse_ooc_command(self, input_text: str) -> Optional[OOCCommand]:
        """Parse an OOC command from input text."""
        if not self.is_ooc_command(input_text):
            return None
        
        # Remove OOC prefixes
        text = input_text.strip()
        if text.lower().startswith('ooc '):
            text = text[4:]
        elif text.startswith(('/', '.', '!')):
            text = text[1:]
        
        # Split into command and arguments
        parts = text.split()
        if not parts:
            return None
        
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Determine command type
        command_type = self._get_command_type(command)
        
        return OOCCommand(
            command=command,
            args=args,
            command_type=command_type,
            player_id=self.player_id,
            timestamp=datetime.utcnow()
        )
    
    def _get_command_type(self, command: str) -> OOCCommandType:
        """Determine the type of an OOC command."""
        command_types = {
            # Help commands
            "help": OOCCommandType.HELP,
            "h": OOCCommandType.HELP,
            "?": OOCCommandType.HELP,
            "commands": OOCCommandType.HELP,
            
            # Status commands
            "status": OOCCommandType.STATUS,
            "time": OOCCommandType.STATUS,
            "uptime": OOCCommandType.STATUS,
            "stats": OOCCommandType.STATUS,
            "who": OOCCommandType.STATUS,
            
            # Settings commands
            "settings": OOCCommandType.SETTINGS,
            
            # Game control commands
            "save": OOCCommandType.GAME_CONTROL,
            "load": OOCCommandType.GAME_CONTROL,
            "quit": OOCCommandType.GAME_CONTROL,
            
            # Debug commands
            "debug": OOCCommandType.DEBUG,
            "clear": OOCCommandType.DEBUG,
            "version": OOCCommandType.DEBUG,
            
            # Social commands
            "tell": OOCCommandType.SOCIAL,
            "whisper": OOCCommandType.SOCIAL,
        }
        
        return command_types.get(command, OOCCommandType.HELP)
    
    def handle_ooc_command(self, ooc_command: OOCCommand) -> Dict[str, Any]:
        """Handle an OOC command and return a response."""
        self.command_history.append(ooc_command)
        
        # Limit history size
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]
        
        # Get handler for the command
        handler = self.command_handlers.get(ooc_command.command)
        
        if handler:
            try:
                response = handler(ooc_command)
                self.logger.debug(f"Handled OOC command: {ooc_command.command}")
                return response
            except Exception as e:
                self.logger.error(f"Error handling OOC command {ooc_command.command}: {e}")
                return {
                    "success": False,
                    "message": f"Error executing command: {str(e)}",
                    "type": "error"
                }
        else:
            return {
                "success": False,
                "message": f"Unknown command: {ooc_command.command}. Type 'help' for available commands.",
                "type": "error"
            }
    
    def process_input(self, input_text: str) -> Optional[Dict[str, Any]]:
        """Process input and handle if it's an OOC command."""
        ooc_command = self.parse_ooc_command(input_text)
        if ooc_command:
            return self.handle_ooc_command(ooc_command)
        return None
    
    # Default command handlers
    def _handle_help(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle help command."""
        if command.args:
            # Help for specific command
            specific_command = command.args[0].lower()
            help_text = self._get_command_help(specific_command)
        else:
            # General help
            help_text = self._get_general_help()
        
        return {
            "success": True,
            "message": help_text,
            "type": "help"
        }
    
    def _handle_status(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle status command."""
        status_info = {
            "game_id": self.game_id,
            "player_id": self.player_id,
            "commands_processed": len(self.command_history),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return {
            "success": True,
            "message": f"Game Status: {self.game_id}\\nPlayer: {self.player_id}\\nCommands processed: {len(self.command_history)}",
            "data": status_info,
            "type": "status"
        }
    
    def _handle_time(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle time command."""
        current_time = datetime.utcnow()
        return {
            "success": True,
            "message": f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            "type": "info"
        }
    
    def _handle_uptime(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle uptime command."""
        # This would need to be implemented with actual system uptime
        return {
            "success": True,
            "message": "System uptime information not available",
            "type": "info"
        }
    
    def _handle_commands(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle commands list."""
        available_commands = sorted(self.command_handlers.keys())
        commands_text = "Available commands:\\n" + "\\n".join([f"  {cmd}" for cmd in available_commands])
        
        return {
            "success": True,
            "message": commands_text,
            "data": {"commands": available_commands},
            "type": "help"
        }
    
    def _handle_who(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle who command."""
        return {
            "success": True,
            "message": f"Currently online:\\n  {self.player_id}",
            "type": "info"
        }
    
    def _handle_quit(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle quit command."""
        return {
            "success": True,
            "message": "Goodbye! Thanks for playing.",
            "type": "quit",
            "action": "quit"
        }
    
    def _handle_save(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle save command."""
        return {
            "success": True,
            "message": "Game state saved successfully.",
            "type": "system",
            "action": "save"
        }
    
    def _handle_load(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle load command."""
        save_name = command.args[0] if command.args else "default"
        return {
            "success": True,
            "message": f"Loading save: {save_name}",
            "type": "system",
            "action": "load",
            "data": {"save_name": save_name}
        }
    
    def _handle_settings(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle settings command."""
        return {
            "success": True,
            "message": "Settings menu not implemented yet.",
            "type": "info"
        }
    
    def _handle_debug(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle debug command."""
        if not self._is_admin(self.player_id):
            return {
                "success": False,
                "message": "Debug commands require admin privileges.",
                "type": "error"
            }
        
        debug_info = {
            "command_history_size": len(self.command_history),
            "registered_handlers": len(self.command_handlers),
            "last_command": self.command_history[-1].to_dict() if self.command_history else None
        }
        
        return {
            "success": True,
            "message": "Debug information:",
            "data": debug_info,
            "type": "debug"
        }
    
    def _handle_stats(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle stats command."""
        stats = self.get_command_statistics()
        return {
            "success": True,
            "message": "Command statistics:",
            "data": stats,
            "type": "stats"
        }
    
    def _handle_clear(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle clear command."""
        return {
            "success": True,
            "message": "\\n" * 50 + "Screen cleared.",
            "type": "system",
            "action": "clear_screen"
        }
    
    def _handle_version(self, command: OOCCommand) -> Dict[str, Any]:
        """Handle version command."""
        return {
            "success": True,
            "message": "AI GM Brain OOC Handler v1.0.0",
            "type": "info"
        }
    
    def _get_general_help(self) -> str:
        """Get general help text."""
        return """Available OOC Commands:
        
Basic Commands:
  help, h, ?          - Show this help
  commands            - List all available commands
  status              - Show system status
  time                - Show current time
  who                 - Show online players
  
Game Control:
  save                - Save game state
  load [name]         - Load saved game
  quit                - Exit the game
  
Utility:
  clear               - Clear screen
  stats               - Show command statistics
  version             - Show version information
  
Use 'help <command>' for specific command help.
Commands can be prefixed with /, ., !, or 'ooc '.
"""
    
    def _get_command_help(self, command: str) -> str:
        """Get help for a specific command."""
        help_texts = {
            "help": "help [command] - Show help information. Use with a command name for specific help.",
            "status": "status - Show current game and system status.",
            "save": "save - Save the current game state.",
            "load": "load [name] - Load a saved game. Defaults to 'default' if no name given.",
            "who": "who - Show currently online players.",
            "quit": "quit - Exit the game safely.",
            "clear": "clear - Clear the screen display.",
            "time": "time - Show the current real-world time.",
            "stats": "stats - Show OOC command usage statistics.",
            "version": "version - Show version information.",
            "commands": "commands - List all available OOC commands."
        }
        
        return help_texts.get(command, f"No help available for command: {command}")
    
    def _is_admin(self, player_id: str) -> bool:
        """Check if a player has admin privileges."""
        return player_id in self.admin_players
    
    def add_admin(self, player_id: str):
        """Add a player to the admin list."""
        if player_id not in self.admin_players:
            self.admin_players.append(player_id)
            self.logger.info(f"Added admin: {player_id}")
    
    def remove_admin(self, player_id: str):
        """Remove a player from the admin list."""
        if player_id in self.admin_players:
            self.admin_players.remove(player_id)
            self.logger.info(f"Removed admin: {player_id}")
    
    def get_command_statistics(self) -> Dict[str, Any]:
        """Get statistics about OOC command usage."""
        total_commands = len(self.command_history)
        
        command_counts = {}
        type_counts = {}
        
        for cmd in self.command_history:
            # Count by command
            command_counts[cmd.command] = command_counts.get(cmd.command, 0) + 1
            
            # Count by type
            type_name = cmd.command_type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            "total_commands": total_commands,
            "commands_by_name": command_counts,
            "commands_by_type": type_counts,
            "registered_handlers": len(self.command_handlers),
            "admin_count": len(self.admin_players)
        }
    
    def get_recent_commands(self, count: int = 10) -> List[OOCCommand]:
        """Get recent OOC commands."""
        return self.command_history[-count:] if count > 0 else self.command_history[:]
    
    def clear_command_history(self):
        """Clear the command history."""
        self.command_history.clear()
        self.logger.info("OOC command history cleared")

# Convenience function for easy integration
def create_ooc_handler(game_id: str, player_id: str) -> OOCCommandHandler:
    """Create and return an OOCCommandHandler instance."""
    return OOCCommandHandler(game_id, player_id)
