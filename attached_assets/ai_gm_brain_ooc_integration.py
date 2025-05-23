"""
Integration of OOC handler into the main AI GM Brain
"""

from ai_gm_brain_phase6_complete import AIGMBrainPhase6Complete
from ai_gm_brain_ooc_handler import OOCHandler


class AIGMBrainWithOOC(AIGMBrainPhase6Complete):
    """
    AI GM Brain with OOC (Out-of-Character) command support
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize AI GM Brain with OOC support"""
        super().__init__(*args, **kwargs)
        
        # Initialize OOC handler
        self.ooc_handler = OOCHandler(self)
        
        self.logger.info("AI GM Brain initialized with OOC command support")
    
    async def process_player_input(self, input_string: str) -> Dict[str, Any]:
        """
        Enhanced input processing that handles OOC commands.
        
        Args:
            input_string: Player's text input (may include OOC commands)
            
        Returns:
            Response with OOC handling if applicable
        """
        start_time = datetime.utcnow()
        
        try:
            # Parse input using enhanced parser (includes OOC detection)
            from text_parser import parse_input
            parsed_command = parse_input(input_string, self.game_context.get_context())
            
            # Check if this is an OOC command
            if (parsed_command and 
                parsed_command.action == "OOC_COMMAND" and 
                hasattr(parsed_command, 'ooc_data')):
                
                return await self._handle_ooc_command(parsed_command, input_string, start_time)
            
            # If not OOC, process normally through Phase 4
            return await super().process_player_input(input_string)
            
        except Exception as e:
            self.logger.error(f"Error in OOC-enhanced input processing: {e}")
            
            # Emergency fallback
            error_response = f"I encountered an error processing your input: {str(e)}"
            
            await self.delivery_system.deliver_response(
                response_data={'response_text': error_response, 'response_source': 'error'},
                metadata={
                    'session_id': self.session_id,
                    'player_id': self.player_id,
                    'error': True
                },
                channels=[DeliveryChannel.CONSOLE]
            )
            
            return {
                'response_text': error_response,
                'error': True,
                'error_message': str(e),
                'ooc_error': True
            }
    
    async def _handle_ooc_command(self, 
                                parsed_command, 
                                input_string: str, 
                                start_time: datetime) -> Dict[str, Any]:
        """Handle OOC command processing"""
        
        # Check for OOC parsing errors
        if parsed_command.has_error():
            error_response = {
                'response_text': f"(OOC) GM: {parsed_command.error_message}",
                'ooc_response': True,
                'response_source': 'ooc_parser_error',
                'error': parsed_command.error_message
            }
            
            # Deliver error response
            await self.delivery_system.deliver_response(
                response_data=error_response,
                metadata={
                    'session_id': self.session_id,
                    'player_id': self.player_id,
                    'ooc_command': True,
                    'error': True
                },
                channels=self.default_delivery_channels
            )
            
            return error_response
        
        # Get current context
        context = await self._get_enhanced_context()
        context['session_id'] = self.session_id
        context['player_id'] = self.player_id
        
        # Process OOC request through handler
        ooc_response = await self.ooc_handler.handle_ooc_request(
            parsed_command.ooc_data, 
            context
        )
        
        # Save OOC interaction to database
        interaction_data = {
            'session_id': self.session_id,
            'interaction_number': self.interaction_counter + 1,
            'player_input': input_string,
            'input_complexity': 'OOC_COMMAND',
            'processing_mode': 'OOC_HANDLER',
            'parser_success': True,
            'parsed_command': {
                'action': 'OOC_COMMAND',
                'ooc_type': parsed_command.ooc_data['command_type'].value
            },
            'ai_response': ooc_response['response_text'],
            'response_type': 'ooc_response',
            'llm_used': ooc_response.get('llm_used', False),
            'processing_time': ooc_response.get('processing_time', 0.0),
            'tokens_used': ooc_response.get('llm_metadata', {}).get('tokens_used', 0),
            'cost_estimate': ooc_response.get('llm_metadata', {}).get('cost_estimate', 0.0),
            'created_at': start_time
        }
        
        interaction_id = self.db_service.save_interaction(interaction_data)
        
        # Log OOC event
        self.db_service.save_event({
            'session_id': self.session_id,
            'event_type': 'OOC_COMMAND_EXECUTED',
            'actor': self.player_id,
            'context': {
                'ooc_type': parsed_command.ooc_data['command_type'].value,
                'payload': parsed_command.ooc_data['payload'],
                'response_source': ooc_response.get('response_source'),
                'llm_used': ooc_response.get('llm_used', False)
            }
        })
        
        # Deliver OOC response
        delivery_result = await self.delivery_system.deliver_response(
            response_data=ooc_response,
            metadata={
                'session_id': self.session_id,
                'player_id': self.player_id,
                'interaction_id': interaction_id,
                'ooc_command': True,
                'processing_time': (datetime.utcnow() - start_time).total_seconds()
            },
            channels=self.default_delivery_channels,
            priority=ResponsePriority.NORMAL
        )
        
        # Prepare complete response
        complete_response = {
            **ooc_response,
            'ooc_command': True,
            'interaction_id': interaction_id,
            'delivery_result': delivery_result,
            'metadata': {
                'session_id': self.session_id,
                'interaction_id': interaction_id,
                'processing_time': (datetime.utcnow() - start_time).total_seconds(),
                'ooc_type': parsed_command.ooc_data['command_type'].value,
                'timestamp': datetime.utcnow().isoformat()
            },
            'enterprise_metadata': {
                'session_id': self.session_id,
                'interaction_id': interaction_id,
                'database_saved': True,
                'ooc_handler_used': True,
                'delivery_successful': delivery_result['overall_success']
            }
        }
        
        return complete_response
    
    def get_comprehensive_statistics_with_ooc(self) -> Dict[str, Any]:
        """Get comprehensive statistics including OOC usage"""
        base_stats = self.get_complete_statistics()
        ooc_stats = self.ooc_handler.get_ooc_statistics()
        
        return {
            **base_stats,
            'ooc_statistics': ooc_stats,
            'features': {
                **base_stats.get('system_status', {}),
                'ooc_commands_active': True
            }
        }


# Example usage and testing
async def test_ooc_commands():
    """Test OOC command functionality"""
    print("Testing OOC Command System")
    print("=" * 50)
    
    # Initialize brain with OOC support
    brain = AIGMBrainWithOOC(
        player_id="test_player_ooc",
        database_url="postgresql://user:pass@localhost/ai_gm_db",
        openrouter_api_key="test_key"
    )
    
    # Test OOC commands
    ooc_test_commands = [
        "/ooc stats",
        "/ooc inventory",
        "/ooc help",
        "/ooc help combat",
        "/ooc what is the history of this place?",
        "/ooc how does combat work?",
        "/ooc time",
        "/ooc session",
        "/ooc",  # Empty command
        "look around",  # Non-OOC command for comparison
        "/ooc what should I do next?",
        "/ooc quest log"
    ]
    
    for i, command in enumerate(ooc_test_commands, 1):
        print(f"\n{'='*20} Test {i} {'='*20}")
        print(f"Command: '{command}'")
        print("-" * 50)
        
        try:
            response = await brain.process_player_input(command)
            
            print(f"✓ Response: {response['response_text']}")
            print(f"✓ OOC Command: {response.get('ooc_command', False)}")
            print(f"✓ Source: {response.get('response_source', 'unknown')}")
            print(f"✓ LLM Used: {response.get('llm_used', False)}")
            
            if response.get('ooc_command'):
                print(f"✓ OOC Type: {response.get('metadata', {}).get('ooc_type', 'unknown')}")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    # Show OOC statistics
    print(f"\n{'='*20} OOC Statistics {'='*20}")
    stats = brain.get_comprehensive_statistics_with_ooc()
    ooc_stats = stats['ooc_statistics']
    
    print(f"Total OOC Requests: {ooc_stats['total_requests']}")
    print(f"Data Handler Success Rate: {ooc_stats['data_handler_success_rate']:.1%}")
    print(f"LLM Usage Rate: {ooc_stats['llm_usage_rate']:.1%}")
    print("Command Usage:")
    for cmd_type, count in ooc_stats['command_usage'].items():
        if count > 0:
            print(f"  - {cmd_type}: {count}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ooc_commands())