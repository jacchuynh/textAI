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
            
            # Fallback to HTTP endpoint
            elif self.http_endpoint:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.http_endpoint, json=payload) as response:
                        return response.status == 200
            
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


class APIEndpointDeliveryHandler:
    """Handles delivery to external API endpoints"""
    
    def __init__(self, endpoint_url: str, api_key: str = None):
        self.endpoint_url = endpoint_url
        self.api_key = api_key
        self.logger = logging.getLogger("APIEndpointDeliveryHandler")
    
    async def deliver(self, response_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Deliver response to external API endpoint"""
        try:
            # Prepare API payload
            payload = {
                'response': response_data.get('response_text', ''),
                'metadata': metadata,
                'response_data': response_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            headers = {'Content-Type': 'application/json'}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.endpoint_url, 
                    json=payload, 
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return True
                    else:
                        self.logger.warning(f"API endpoint returned status {response.status}")
                        return False
            
        except Exception as e:
            self.logger.error(f"API endpoint delivery error: {e}")
            return False


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
            import aiofiles
            async with aiofiles.open(self.log_file_path, 'a', encoding='utf-8') as f:
                if self.format_json:
                    await f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                else:
                    timestamp = log_entry['timestamp']
                    text = log_entry['response_text']
                    await f.write(f"[{timestamp}] GM: {text}\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"File log delivery error: {e}")
            return False


class DatabaseLogDeliveryHandler:
    """Handles delivery logging to database"""
    
    def __init__(self, db_service):
        self.db_service = db_service
        self.logger = logging.getLogger("DatabaseLogDeliveryHandler")
    
    async def deliver(self, response_data: Dict[str, Any], metadata: Dict[str, Any]) -> bool:
        """Log delivery to database"""
        try:
            # Save delivery event
            await self.db_service.save_event({
                'session_id': metadata.get('session_id'),
                'event_type': 'RESPONSE_DELIVERED',
                'actor': 'ai_gm_brain',
                'context': {
                    'response_length': len(response_data.get('response_text', '')),
                    'response_source': response_data.get('response_source'),
                    'decision_priority': metadata.get('decision_priority'),
                    'delivery_channels': metadata.get('delivery_channels', []),
                    'processing_time': metadata.get('processing_time')
                }
            })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Database log delivery error: {e}")
            return False


class OutputDeliverySystem:
    """
    Main output delivery system that orchestrates response delivery
    """
    
    def __init__(self, db_service=None):
        self.db_service = db_service
        self.delivery_handlers: Dict[DeliveryChannel, DeliveryProtocol] = {}
        self.delivery_queue: List[Dict[str, Any]] = []
        self.delivery_stats = {
            'total_deliveries': 0,
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'channel_usage': {channel: 0 for channel in DeliveryChannel}
        }
        self.logger = logging.getLogger("OutputDeliverySystem")
        
        # Initialize default handlers
        self._initialize_default_handlers()
    
    def _initialize_default_handlers(self):
        """Initialize default delivery handlers"""
        # Console handler (always available)
        self.register_handler(DeliveryChannel.CONSOLE, ConsoleDeliveryHandler())
        
        # Database log handler if available
        if self.db_service:
            self.register_handler(DeliveryChannel.DATABASE_LOG, DatabaseLogDeliveryHandler(self.db_service))
    
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
            # Execute deliveries (potentially in parallel for performance)
            delivery_tasks = []
            for channel in channels:
                if channel in self.delivery_handlers:
                    handler = self.delivery_handlers[channel]
                    task = self._deliver_to_channel(channel, handler, response_data, delivery_metadata)
                    delivery_tasks.append(task)
                    self.delivery_stats['channel_usage'][channel] += 1
                else:
                    self.logger.warning(f"No handler registered for channel {channel.name}")
                    delivery_results['failed_channels'].append(channel.name)
            
            # Wait for all deliveries to complete
            if delivery_tasks:
                results = await asyncio.gather(*delivery_tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    channel = channels[i] if i < len(channels) else None
                    if channel and channel in self.delivery_handlers:
                        if isinstance(result, Exception):
                            self.logger.error(f"Delivery to {channel.name} failed: {result}")
                            delivery_results['failed_channels'].append(channel.name)
                        elif result:
                            delivery_results['successful_channels'].append(channel.name)
                        else:
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
    
    def configure_api_endpoint(self, endpoint_url: str, api_key: str = None):
        """Configure API endpoint delivery"""
        handler = APIEndpointDeliveryHandler(endpoint_url, api_key)
        self.register_handler(DeliveryChannel.API_ENDPOINT, handler)
    
    def configure_file_logging(self, log_file_path: str, format_json: bool = True):
        """Configure file logging delivery"""
        handler = FileLogDeliveryHandler(log_file_path, format_json)
        self.register_handler(DeliveryChannel.FILE_LOG, handler)
    
    def get_delivery_statistics(self) -> Dict[str, Any]:
        """Get delivery system statistics"""
        total = self.delivery_stats['total_deliveries']
        return {
            'total_deliveries': total,
            'successful_deliveries': self.delivery_stats['successful_deliveries'],
            'failed_deliveries': self.delivery_stats['failed_deliveries'],
            'success_rate': (self.delivery_stats['successful_deliveries'] / max(1, total)),
            'channel_usage': {
                channel.name: count 
                for channel, count in self.delivery_stats['channel_usage'].items()
            },
            'available_channels': [channel.name for channel in self.delivery_handlers.keys()]
        }