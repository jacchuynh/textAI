"""
OOC (Out-of-Character) handler for AI GM Brain
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
from text_parser.ooc_parser_extension import OOCCommandType


class OOCHandler:
    """Handles out-of-character requests and queries"""
    
    def __init__(self, ai_gm_brain):
        """
        Initialize OOC handler.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.brain = ai_gm_brain
        self.logger = logging.getLogger("OOCHandler")
        
        # Quick data handlers for common OOC requests
        self.data_handlers = {
            OOCCommandType.STATS_REQUEST: self._handle_stats_request,
            OOCCommandType.INVENTORY_REQUEST: self._handle_inventory_request,
            OOCCommandType.QUEST_LOG: self._handle_quest_log_request,
            OOCCommandType.HELP_REQUEST: self._handle_help_request,
            OOCCommandType.SYSTEM_INFO: self._handle_system_info_request
        }
        
        # Track OOC usage statistics
        self.ooc_stats = {
            'total_ooc_requests': 0,
            'command_type_usage': {cmd_type: 0 for cmd_type in OOCCommandType},
            'data_handler_hits': 0,
            'llm_handler_calls': 0
        }
    
    async def handle_ooc_request(self, ooc_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main OOC request handler.
        
        Args:
            ooc_data: OOC command data from parser
            context: Current game context
            
        Returns:
            Response dictionary with OOC response
        """
        self.ooc_stats['total_ooc_requests'] += 1
        start_time = datetime.utcnow()
        
        command_type = ooc_data['command_type']
        payload = ooc_data['payload']
        metadata = ooc_data['metadata']
        
        self.ooc_stats['command_type_usage'][command_type] += 1
        
        self.logger.info(f"Handling OOC request: {command_type.value} - '{payload}'")
        
        try:
            # Step 1: Try to answer from game data
            data_response = await self._try_data_handler(command_type, payload, metadata, context)
            
            if data_response:
                self.ooc_stats['data_handler_hits'] += 1
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return {
                    'response_text': f"(OOC) GM: {data_response}",
                    'ooc_response': True,
                    'response_source': 'game_data',
                    'command_type': command_type.value,
                    'processing_time': processing_time,
                    'llm_used': False
                }
            
            # Step 2: Use LLM for complex OOC queries
            return await self._handle_with_llm(command_type, payload, metadata, context, start_time)
            
        except Exception as e:
            self.logger.error(f"Error handling OOC request: {e}")
            return {
                'response_text': f"(OOC) GM: I'm sorry, I encountered an error processing your OOC request: {str(e)}",
                'ooc_response': True,
                'response_source': 'error',
                'error': str(e)
            }
    
    async def _try_data_handler(self, 
                              command_type: OOCCommandType, 
                              payload: str, 
                              metadata: Dict[str, Any], 
                              context: Dict[str, Any]) -> Optional[str]:
        """Try to handle OOC request with local game data"""
        
        handler = self.data_handlers.get(command_type)
        if handler:
            try:
                return await handler(payload, metadata, context)
            except Exception as e:
                self.logger.warning(f"Data handler failed for {command_type.value}: {e}")
        
        return None
    
    async def _handle_stats_request(self, payload: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle player stats requests"""
        stat_type = metadata.get('stat_type', 'all').lower()
        
        # Get player data from context
        player_id = context.get('player_id', 'unknown')
        player_data = context.get('player_data', {})
        
        if stat_type == 'all' or stat_type == 'stats':
            # Return comprehensive stats
            stats_lines = [
                f"Character Stats for {player_data.get('name', 'Unknown Character')}:",
                f"  Location: {context.get('current_location', 'Unknown')}",
                f"  Health: {player_data.get('health', 'Unknown')}",
                f"  Level: {player_data.get('level', 'Unknown')}",
                f"  Experience: {player_data.get('experience', 'Unknown')}"
            ]
            
            # Add any special stats
            if 'attributes' in player_data:
                stats_lines.append("  Attributes:")
                for attr, value in player_data['attributes'].items():
                    stats_lines.append(f"    {attr.title()}: {value}")
            
            return '\n'.join(stats_lines)
        
        else:
            # Return specific stat
            if stat_type in player_data:
                return f"{stat_type.title()}: {player_data[stat_type]}"
            else:
                return f"I don't have information about '{stat_type}'. Try '/ooc stats' for all available stats."
    
    async def _handle_inventory_request(self, payload: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle inventory requests"""
        # Get inventory from game context
        player_id = context.get('player_id', 'unknown')
        
        # Use game_context to get inventory
        from game_context import game_context
        inventory = game_context.get_player_inventory(player_id)
        
        if not inventory:
            return "Your inventory is empty."
        
        inventory_lines = ["Your Inventory:"]
        for item in inventory:
            item_name = item.get('name', 'Unknown Item')
            item_desc = item.get('description', '')
            if item_desc:
                inventory_lines.append(f"  - {item_name}: {item_desc}")
            else:
                inventory_lines.append(f"  - {item_name}")
        
        return '\n'.join(inventory_lines)
    
    async def _handle_quest_log_request(self, payload: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle quest log requests"""
        # This would integrate with your quest system
        # For now, return a placeholder
        
        active_quests = context.get('active_quests', [])
        completed_quests = context.get('completed_quests', [])
        
        if not active_quests and not completed_quests:
            return "You have no quests at the moment."
        
        quest_lines = []
        
        if active_quests:
            quest_lines.append("Active Quests:")
            for quest in active_quests:
                quest_name = quest.get('name', 'Unknown Quest')
                quest_desc = quest.get('description', 'No description available')
                quest_lines.append(f"  - {quest_name}: {quest_desc}")
        
        if completed_quests:
            quest_lines.append("\nCompleted Quests:")
            for quest in completed_quests:
                quest_name = quest.get('name', 'Unknown Quest')
                quest_lines.append(f"  - {quest_name}")
        
        return '\n'.join(quest_lines)
    
    async def _handle_help_request(self, payload: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle help requests"""
        help_topic = metadata.get('help_topic', 'general').lower()
        
        help_topics = {
            'general': """Available Commands:
- Basic Actions: look, take, go, use, attack, talk
- OOC Commands: /ooc stats, /ooc inventory, /ooc help [topic]
- Special: north/south/east/west for movement

For specific help, try: /ooc help [topic]
Example: /ooc help combat""",
            
            'combat': """Combat System:
- Use 'attack [target]' to initiate combat
- Combat is turn-based with skill checks
- Your success depends on character stats and luck
- Some actions may require specific items or conditions""",
            
            'movement': """Movement Commands:
- 'go [direction]' or just '[direction]'
- Available directions: north, south, east, west, up, down
- Some locations may have special exits
- Use 'look' to see available exits""",
            
            'ooc': """Out-of-Character Commands:
- /ooc stats - View character statistics
- /ooc inventory - View your items
- /ooc quest log - View active and completed quests
- /ooc help [topic] - Get help on specific topics
- /ooc time - Check current game time
- /ooc session - View session information"""
        }
        
        return help_topics.get(help_topic, f"No help available for '{help_topic}'. Try '/ooc help' for available topics.")
    
    async def _handle_system_info_request(self, payload: str, metadata: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Handle system information requests"""
        info_lines = []
        
        # Current game time
        current_time = context.get('time_of_day', 'unknown')
        current_season = context.get('current_season', 'unknown')
        info_lines.append(f"Game Time: {current_time} in {current_season}")
        
        # Real world time
        real_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        info_lines.append(f"Real Time: {real_time}")
        
        # Session info
        session_id = context.get('session_id', 'unknown')
        player_id = context.get('player_id', 'unknown')
        info_lines.append(f"Session ID: {session_id}")
        info_lines.append(f"Player ID: {player_id}")
        
        # World state
        world_state = context.get('world_state', {})
        if world_state:
            economic_status = world_state.get('economic_status', 'unknown')
            political_stability = world_state.get('political_stability', 'unknown')
            info_lines.append(f"World State: Economic {economic_status}, Political {political_stability}")
        
        return '\n'.join(info_lines)
    
    async def _handle_with_llm(self, 
                             command_type: OOCCommandType, 
                             payload: str, 
                             metadata: Dict[str, Any], 
                             context: Dict[str, Any],
                             start_time: datetime) -> Dict[str, Any]:
        """Handle OOC request using LLM"""
        self.ooc_stats['llm_handler_calls'] += 1
        
        # Build LLM prompt for OOC queries
        prompt = self._build_ooc_llm_prompt(payload, context)
        
        try:
            # Get optimal model for OOC queries (usually cheaper models are fine)
            model = self.brain.llm_manager.get_optimal_model("world_query", "medium")
            
            # Call LLM
            llm_result = await self.brain.llm_manager.call_llm_with_tracking(
                prompt=prompt,
                model=model,
                prompt_mode="ooc_query",
                temperature=0.3,  # Lower temperature for factual responses
                max_tokens=200
            )
            
            if llm_result['success']:
                response_text = llm_result['content'].strip()
                processing_time = (datetime.utcnow() - start_time).total_seconds()
                
                return {
                    'response_text': f"(OOC) GM: {response_text}",
                    'ooc_response': True,
                    'response_source': 'llm_ooc',
                    'command_type': command_type.value,
                    'processing_time': processing_time,
                    'llm_used': True,
                    'llm_metadata': {
                        'model': model,
                        'tokens_used': llm_result['tokens_used'],
                        'cost_estimate': llm_result['cost_estimate']
                    }
                }
            else:
                return {
                    'response_text': "(OOC) GM: I'm having trouble processing your request right now. Please try again.",
                    'ooc_response': True,
                    'response_source': 'llm_error',
                    'error': llm_result.get('error_message', 'Unknown LLM error')
                }
                
        except Exception as e:
            self.logger.error(f"LLM OOC handling error: {e}")
            return {
                'response_text': f"(OOC) GM: I encountered an error while processing your request: {str(e)}",
                'ooc_response': True,
                'response_source': 'error',
                'error': str(e)
            }
    
    def _build_ooc_llm_prompt(self, payload: str, context: Dict[str, Any]) -> str:
        """Build LLM prompt for OOC queries"""
        
        # Get context information
        player_data = context.get('player_data', {})
        world_state = context.get('world_state', {})
        
        # Build player summary
        player_summary = f"Player: {player_data.get('name', 'Unknown')} (Level {player_data.get('level', '?')}, Location: {context.get('current_location', 'Unknown')})"
        
        # Build quest summary
        active_quests = context.get('active_quests', [])
        if active_quests:
            current_quest = f"Current Quest: {active_quests[0].get('name', 'Unknown Quest')} - {active_quests[0].get('description', 'No description')}"
        else:
            current_quest = "Current Quest: None"
        
        # Build world state summary
        world_summary = f"World: Economic {world_state.get('economic_status', 'stable')}, Political {world_state.get('political_stability', 'stable')}"
        
        # Current date/time
        current_datetime = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        user_login = "tien2512"  # From your current session
        
        prompt = f"""You are a helpful and knowledgeable Assistant Game Master. The player is asking an out-of-character (OOC) question or making an OOC comment.

Player's OOC Request: "{payload}"

Available Information Context:
- Player Character Summary: {player_summary}
- {current_quest}
- {world_summary}
- Date/Time: {current_datetime} UTC
- User Login: {user_login}

Please provide a clear, concise, and helpful out-of-character response.
- If it's a question about game mechanics you have information on, answer it.
- If it's a request for information you can access (like lore snippets or general game knowledge), provide it.
- If it's a subjective question (e.g., "what should I do?"), offer general, non-spoiler advice or suggest ways the player could find out in-game.
- If you cannot answer the question, politely state that.
- Do NOT respond in-character as a story narrator. Maintain an assistant GM persona.
- Keep responses concise but helpful."""
        
        return prompt
    
    def get_ooc_statistics(self) -> Dict[str, Any]:
        """Get OOC usage statistics"""
        return {
            'total_requests': self.ooc_stats['total_ooc_requests'],
            'command_usage': {
                cmd_type.value: count 
                for cmd_type, count in self.ooc_stats['command_type_usage'].items()
            },
            'data_handler_success_rate': (
                self.ooc_stats['data_handler_hits'] / 
                max(1, self.ooc_stats['total_ooc_requests'])
            ),
            'llm_usage_rate': (
                self.ooc_stats['llm_handler_calls'] / 
                max(1, self.ooc_stats['total_ooc_requests'])
            )
        }