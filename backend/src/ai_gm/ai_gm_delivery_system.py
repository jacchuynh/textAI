"""
Output Delivery System for AI GM Brain - Phase 4.2

Handles the final delivery of responses to the game's UI/player interface.
"""

from typing import Dict, Any, List, Optional, Callable, Protocol
from enum import Enum, auto
import asyncio
import logging
from datetime import datetime
import json

# Import from core brain
from .ai_gm_brain import AIGMBrain


class DeliveryChannel(Enum):
    """Different delivery channels for responses"""
    CONSOLE = auto()
    WEB_INTERFACE = auto()
    API_ENDPOINT = auto()
    WEBSOCKET = auto()
    FILE_LOG = auto()
    DATABASE_LOG = auto()


class ResponsePriority(Enum):
    """Priority levels for response delivery"""
    IMMEDIATE = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


class DeliveryProtocol(Protocol):
    """Protocol for delivery handlers"""
    
    async def deliver(self, response_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Deliver response through this channel"""
        ...


class ConsoleDeliveryHandler:
    """Handles delivery to console/terminal"""
    
    def __init__(self, format_response: bool = True):
        self.format_response = format_response
        self.logger = logging.getLogger("ConsoleDeliveryHandler")
    
    async def deliver(self, response_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Deliver response to console"""
        try:
            response_text = response_data.get('response_text', '')
            
            if self.format_response:
                # Format with metadata for debugging
                print(f"\n{'='*60}")
                print(f"GM: {response_text}")
                print(f"{'='*60}")
                print(f"Mode: {response_data.get('response_source', 'unknown')}")
                print(f"Priority: {metadata.get('decision_priority', 'unknown')}")
                print(f"Time: {metadata.get('processing_time', 0.0):.3f}s")
                if response_data.get('tokens_used'):
                    print(f"Tokens: {response_data['tokens_used']}")
                print()
            else:
                # Simple format
                print(f"\nGM: {response_text}\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Console delivery error: {e}")
            return False


class WebInterfaceDeliveryHandler:
    """Handles delivery to web interface"""
    
    def __init__(self, websocket_manager=None, http_endpoint: str = None):
        self.websocket_manager = websocket_manager
        self.http_endpoint = http_endpoint
        self.logger = logging.getLogger("WebInterfaceDeliveryHandler")
    
    async def deliver(self, response_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Deliver response to web interface"""
        try:
            # Prepare payload for web interface
            payload = {
                'type': 'gm_response',
                'content': response_data.get('response_text', ''),
                'metadata': {
                    'response_source': response_data.get('response_source'),
                    'decision_priority': metadata.get('decision_priority'),
                    'processing_time': metadata.get('processing_time'),
                    'timestamp': datetime.utcnow().isoformat(),
                    'requires_followup': response_data.get('requires_followup', False)
                },
                'styling': {
                    'priority': self._determine_ui_priority(metadata),
                    'theme': self._determine_ui_theme(response_data)
                }
            }
            
            # Send via WebSocket if available
            if self.websocket_manager:
                await self.websocket_manager.broadcast(payload)
                return True
            
            # No delivery mechanism available
            return False
            
        except Exception as e:
            self.logger.error(f"Web interface delivery error: {e}")
            return False
    
    def _determine_ui_priority(self, metadata: Dict[str, Any]) -> str:
        """Determine UI priority styling"""
        priority = metadata.get('decision_priority', 'NORMAL')
        if priority in ['LLM_OPPORTUNITY_ALIGNMENT', 'LLM_BRANCH_ACTION_ALIGNMENT']:
            return 'high'
        elif priority == 'SUCCESSFUL_PARSED_COMMAND':
            return 'normal'
        else:
            return 'low'
    
    def _determine_ui_theme(self, response_data: Dict[str, Any]) -> str:
        """Determine UI theme based on response"""
        source = response_data.get('response_source', '')
        if 'npc' in source:
            return 'dialogue'
        elif 'creative' in source:
            return 'narrative'
        elif 'command' in source:
            return 'action'
        else:
            return 'default'


class FileLogDeliveryHandler:
    """Handles delivery to file logs"""
    
    def __init__(self, log_file_path: str, format_json: bool = True):
        self.log_file_path = log_file_path
        self.format_json = format_json
        self.logger = logging.getLogger("FileLogDeliveryHandler")
    
    async def deliver(self, response_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Deliver response to file log"""
        try:
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'response_text': response_data.get('response_text', ''),
                'metadata': metadata,
                'response_data': response_data
            }
            
            # Write to file
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                if self.format_json:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                else:
                    timestamp = log_entry['timestamp']
                    text = log_entry['response_text']
                    f.write(f"[{timestamp}] GM: {text}\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"File log delivery error: {e}")
            return False


class OutputDeliverySystem:
    """
    Main output delivery system that orchestrates response delivery
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the output delivery system.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.delivery_handlers: Dict[DeliveryChannel, DeliveryProtocol] = {}
        self.delivery_stats = {
            'total_deliveries': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'channel_usage': {channel.name: 0 for channel in DeliveryChannel}
        }
        self.logger = logging.getLogger(f"OutputDelivery_{ai_gm_brain.game_id}")
        
        # Initialize default handlers
        self._initialize_default_handlers()
    
    def _initialize_default_handlers(self):
        """Initialize default delivery handlers"""
        # Console handler (always available)
        self.register_handler(DeliveryChannel.CONSOLE, ConsoleDeliveryHandler())
        
        # Add file logging
        try:
            # Create a simple log file in the current directory
            import os
            log_dir = "logs"
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, f"gm_responses_{self.ai_gm_brain.game_id}.log")
            self.register_handler(DeliveryChannel.FILE_LOG, FileLogDeliveryHandler(log_file))
        except Exception as e:
            self.logger.warning(f"Could not initialize file logging: {e}")
    
    def register_handler(self, channel: DeliveryChannel, handler: DeliveryProtocol):
        """Register a delivery handler for a channel"""
        self.delivery_handlers[channel] = handler
        self.logger.info(f"Registered delivery handler for {channel.name}")
    
    def unregister_handler(self, channel: DeliveryChannel):
        """Unregister a delivery handler"""
        if channel in self.delivery_handlers:
            del self.delivery_handlers[channel]
            self.logger.info(f"Unregistered delivery handler for {channel.name}")
    
    async def deliver_response(self,
                             response_data: Dict[str, Any],
                             metadata: Dict[str, Any],
                             channels: List[DeliveryChannel] = None,
                             priority: ResponsePriority = ResponsePriority.NORMAL) -> Dict[str, Any]:
        """
        Deliver response through specified channels.
        
        Args:
            response_data: Generated response data
            metadata: Response metadata
            channels: List of delivery channels to use (default: all available)
            priority: Delivery priority
            
        Returns:
            Delivery results summary
        """
        start_time = datetime.utcnow()
        self.delivery_stats['total_deliveries'] += 1
        
        # Use all available channels if none specified
        if channels is None:
            channels = list(self.delivery_handlers.keys())
        
        # Add delivery metadata
        delivery_metadata = {
            **metadata,
            'delivery_priority': priority.name,
            'delivery_channels': [channel.name for channel in channels],
            'delivery_start_time': start_time.isoformat()
        }
        
        # Prepare delivery results
        delivery_results = {
            'total_channels': len(channels),
            'successful_channels': [],
            'failed_channels': [],
            'delivery_time': 0.0,
            'overall_success': False
        }
        
        try:
            # Execute deliveries one by one for simplicity
            for channel in channels:
                if channel in self.delivery_handlers:
                    handler = self.delivery_handlers[channel]
                    success = await self._deliver_to_channel(channel, handler, response_data, delivery_metadata)
                    self.delivery_stats['channel_usage'][channel.name] += 1
                    
                    if success:
                        delivery_results['successful_channels'].append(channel.name)
                    else:
                        delivery_results['failed_channels'].append(channel.name)
                else:
                    self.logger.warning(f"No handler registered for channel {channel.name}")
                    delivery_results['failed_channels'].append(channel.name)
            
            # Calculate final results
            delivery_results['delivery_time'] = (datetime.utcnow() - start_time).total_seconds()
            delivery_results['overall_success'] = len(delivery_results['successful_channels']) > 0
            
            # Update statistics
            if delivery_results['overall_success']:
                self.delivery_stats['successful_deliveries'] += 1
            else:
                self.delivery_stats['failed_deliveries'] += 1
            
            # Log delivery completion
            self.logger.info(
                f"Delivery completed: {len(delivery_results['successful_channels'])}/{delivery_results['total_channels']} channels successful"
            )
            
            return delivery_results
            
        except Exception as e:
            self.logger.error(f"Error in delivery system: {e}")
            delivery_results['overall_success'] = False
            delivery_results['error'] = str(e)
            self.delivery_stats['failed_deliveries'] += 1
            return delivery_results
    
    async def _deliver_to_channel(self,
                                channel: DeliveryChannel,
                                handler: DeliveryProtocol,
                                response_data: Dict[str, Any],
                                metadata: Dict[str, Any]) -> bool:
        """Deliver to a specific channel with error handling"""
        try:
            self.logger.debug(f"Delivering to {channel.name}")
            return await handler.deliver(response_data, metadata)
        except Exception as e:
            self.logger.error(f"Delivery to {channel.name} failed: {e}")
            return False
    
    def configure_web_interface(self, websocket_manager=None, http_endpoint: str = None):
        """Configure web interface delivery"""
        handler = WebInterfaceDeliveryHandler(websocket_manager, http_endpoint)
        self.register_handler(DeliveryChannel.WEB_INTERFACE, handler)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics on response delivery"""
        return self.delivery_stats
    
    # Synchronous wrapper for deliver_response to be used in non-async contexts
    def deliver_response_sync(self,
                            response_data: Dict[str, Any],
                            metadata: Dict[str, Any],
                            channels: List[DeliveryChannel] = None,
                            priority: ResponsePriority = ResponsePriority.NORMAL) -> Dict[str, Any]:
        """
        Synchronous wrapper for deliver_response.
        
        This uses a new event loop in a separate thread to run the async deliver_response.
        Not ideal for production but works for simple cases.
        """
        # Use asyncio to create and run an event loop
        loop = asyncio.new_event_loop()
        result = loop.run_until_complete(
            self.deliver_response(response_data, metadata, channels, priority)
        )
        loop.close()
        return result


# Extension function to add output delivery to AI GM Brain
def extend_ai_gm_brain_with_output_delivery(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with output delivery capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create output delivery system
    output_delivery = OutputDeliverySystem(ai_gm_brain)
    
    # Store the output delivery system for future reference
    ai_gm_brain.output_delivery = output_delivery
    
    # Add deliver_response method to the AI GM Brain
    ai_gm_brain.deliver_response = lambda response_data, metadata, channels=None, priority=ResponsePriority.NORMAL: output_delivery.deliver_response_sync(
        response_data, metadata, channels, priority
    )
    
    # Override the existing process_player_input method to use output generation and delivery
    original_process_player_input = ai_gm_brain.process_player_input
    
    def enhanced_process_player_input(player_input: str) -> Dict[str, Any]:
        """Enhanced player input processing with output generation and delivery."""
        # First, get the basic response and decision result using the original method and decision tree
        basic_response = original_process_player_input(player_input)
        
        # Extract decision result from metadata
        decision_result = None
        if 'metadata' in basic_response and 'decision_tree' in basic_response['metadata']:
            decision_result = {
                'action_taken': basic_response['metadata']['decision_tree'].get('action_taken'),
                'response_basis': basic_response['metadata']['decision_tree'].get('response_basis'),
                'mechanical_outcome': basic_response['metadata']['decision_tree'].get('mechanical_outcome'),
                'suggested_response': basic_response['response_text'],
                'success': True  # Assume success for now
            }
        
        # If no decision result, create a basic one from the response
        if not decision_result:
            decision_result = {
                'action_taken': 'process_input',
                'response_basis': 'direct_processing',
                'suggested_response': basic_response['response_text'],
                'success': True
            }
        
        # Create game context and interaction context
        game_context = {
            'game_id': ai_gm_brain.game_id,
            'player_id': ai_gm_brain.player_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        interaction_context = {
            'player_input': player_input,
            'processing_time': basic_response.get('metadata', {}).get('processing_time', 0.0),
            'player_id': ai_gm_brain.player_id
        }
        
        # If response generator exists, use it to generate response
        if hasattr(ai_gm_brain, 'response_generator'):
            response_data = ai_gm_brain.generate_response(decision_result, game_context, interaction_context)
        else:
            # Otherwise use the basic response
            response_data = {
                'response_text': basic_response['response_text'],
                'response_source': 'direct_processing'
            }
        
        # Extract metadata for delivery
        metadata = {
            'game_id': ai_gm_brain.game_id,
            'player_id': ai_gm_brain.player_id,
            'processing_time': basic_response.get('metadata', {}).get('processing_time', 0.0),
            'decision_priority': decision_result.get('response_basis', 'unknown')
        }
        
        # Deliver response
        delivery_result = ai_gm_brain.deliver_response(response_data, metadata)
        
        # Update the basic response with the generated and delivered response
        enhanced_response = basic_response.copy()
        enhanced_response['response_text'] = response_data['response_text']
        enhanced_response['metadata']['response_generation'] = {
            'response_source': response_data.get('response_source'),
            'generation_metadata': response_data.get('generation_metadata', {})
        }
        enhanced_response['metadata']['delivery'] = delivery_result
        
        return enhanced_response
    
    # Replace the original method with the enhanced version
    ai_gm_brain.process_player_input = enhanced_process_player_input