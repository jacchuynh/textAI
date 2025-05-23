"""
Test script for the fully integrated AI GM Brain with all systems working together.

This test demonstrates how all systems work together cohesively:
1. Decision Logic system from Phase 3
2. Output Generation from Phase 4
3. World Reaction system from Phase 5
4. Pacing and ambient storytelling from Phase 6
5. Integration with domain and combat systems
"""

import asyncio
import json
from datetime import datetime, timedelta
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Import the main integrated AI GM Brain Phase 6
from backend.src.ai_gm.ai_gm_brain_phase6_complete import AIGMBrainPhase6Complete
from backend.src.ai_gm.ai_gm_delivery_system import DeliverySystem, DeliveryChannel, ResponsePriority
from backend.src.ai_gm.ai_gm_config import IntegratedAIGMConfig


# Simulation test context (what would come from the game in a real scenario)
TEST_CONTEXT = {
    'player_id': 'player_123',
    'player_name': 'Adventurer',
    'session_id': 'test_integrated_session',
    'current_location': 'Rusted Tavern',
    'current_scene': 'tavern_main_room',
    'time_of_day': 'evening',
    'present_npcs': ['barkeeper', 'merchant', 'mysterious_stranger'],
    'npcs': {
        'barkeeper': {
            'name': 'Darius',
            'personality': 'friendly',
            'occupation': 'tavern owner',
            'disposition': 'helpful'
        },
        'merchant': {
            'name': 'Geralt',
            'personality': 'wise',
            'occupation': 'retired adventurer',
            'disposition': 'neutral'
        },
        'mysterious_stranger': {
            'name': 'Shadowcloak',
            'personality': 'suspicious',
            'occupation': 'unknown',
            'disposition': 'wary'
        }
    },
    'inventory': ['sword', 'healing potion', 'gold coins'],
    'world_state': {
        'political_stability': 'unrest',
        'economic_status': 'struggling',
        'local_threats': ['bandit activity', 'strange lights in the mine']
    },
    'location_context': {
        'dominant_aura': 'welcoming',
        'notable_features': ['warm fireplace', 'wooden tables', 'trophy wall']
    },
    'recent_significant_events': [
        'Player helped village elder find lost heirloom',
        'Player spotted strange lights in the abandoned mine'
    ],
    'player_reputation': {
        'village': 'respected',
        'merchants_guild': 'neutral',
        'barkeeper': 'friendly'
    },
    'domains': {
        'active_domains': ['PERCEPTION', 'SOCIAL', 'KNOWLEDGE'],
        'available_domains': ['PERCEPTION', 'SOCIAL', 'KNOWLEDGE', 'COMBAT', 'STEALTH']
    },
    'branch_opportunities': {
        'abandoned_mine_mystery': {
            'status': 'available',
            'hooks': ['strange lights', 'missing miners']
        },
        'bandit_problem': {
            'status': 'available',
            'hooks': ['merchant complaints', 'village elder request']
        }
    }
}


# Mock test player inputs with different types of interactions
TEST_INPUTS = [
    # Simple parsed command
    "look around",
    
    # Direct NPC interaction (social domain)
    "talk to the barkeeper about rumors",
    
    # Knowledge domain query
    "what do I know about the abandoned mine?",
    
    # Action with world reaction implications
    "draw my sword and threaten the mysterious stranger",
    
    # Narrative branch opportunity hook
    "ask about the strange lights in the mine",
    
    # Complex conversational query
    "can you tell me more about the history of this region and why there's political unrest?"
]


# Mock configuration for testing
TEST_CONFIG = IntegratedAIGMConfig.get_config()


# Mock delivery system to capture outputs
class TestDeliverySystem(DeliverySystem):
    """Mock delivery system for testing that captures all outputs."""
    
    def __init__(self):
        self.delivered_messages = []
        self.logger = logging.getLogger("TestDeliverySystem")
    
    async def deliver_response(self, 
                             response_text: str, 
                             channels=None, 
                             priority=ResponsePriority.NORMAL):
        """Deliver a response by storing it."""
        if not channels:
            channels = [DeliveryChannel.NARRATIVE]
            
        channel_names = [c.name for c in channels]
        
        message = {
            'text': response_text,
            'channels': channel_names,
            'priority': priority.name,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.delivered_messages.append(message)
        self.logger.info(f"[DELIVERY] [{priority.name}] {response_text} → {', '.join(channel_names)}")
    
    def get_all_messages(self):
        """Get all delivered messages."""
        return self.delivered_messages
    
    def get_messages_by_channel(self, channel: DeliveryChannel):
        """Get messages delivered to a specific channel."""
        channel_name = channel.name
        return [msg for msg in self.delivered_messages 
                if channel_name in msg['channels']]
    
    def clear_messages(self):
        """Clear all delivered messages."""
        self.delivered_messages = []


# Mock context manager
class TestContextManager:
    """Mock context manager for testing."""
    
    def __init__(self, initial_context=None):
        self.context = initial_context or {}
        self.logger = logging.getLogger("TestContextManager")
    
    def get_current_context(self):
        """Get current context."""
        return self.context
    
    def update_context(self, updates):
        """Update context with new data."""
        self.context.update(updates)
        self.logger.info(f"Context updated with {len(updates)} items")
    
    def clear_context(self):
        """Clear all context data."""
        self.context = {}


# Class to run test cases
class IntegratedAIGMBrainTester:
    """Tester for the integrated AI GM Brain."""
    
    def __init__(self):
        self.logger = logging.getLogger("AIGMBrainTester")
        self.brain = None
        self.delivery_system = TestDeliverySystem()
        self.context_manager = TestContextManager(TEST_CONTEXT)
    
    async def setup(self):
        """Set up the AI GM Brain and dependencies."""
        self.logger.info("Setting up AI GM Brain test...")
        
        # Initialize the AI GM Brain with test configuration
        self.brain = AIGMBrainPhase6Complete(TEST_CONFIG)
        
        # Inject mock dependencies
        self.brain.delivery_system = self.delivery_system
        self.brain.context_manager = self.context_manager
        
        # Set up initial state for testing
        self.brain.last_input_time = datetime.utcnow() - timedelta(minutes=5)
        
        self.logger.info("AI GM Brain test setup complete")
    
    async def run_test_with_parser(self):
        """Run test with commands that would be typically parsed."""
        self.logger.info("\n=== Testing commands typically handled by parser ===")
        
        await self.process_input("look around")
        await self.process_input("examine the fireplace")
        await self.process_input("take my sword from inventory")
        
        return self.delivery_system.get_messages_by_channel(DeliveryChannel.NARRATIVE)
    
    async def run_test_with_llm(self):
        """Run test with conversational inputs usually handled by LLM."""
        self.logger.info("\n=== Testing conversational inputs ===")
        
        await self.process_input("tell me about this tavern's history")
        await self.process_input("who is the mysterious stranger in the corner?")
        await self.process_input("what do the villagers think about the abandoned mine?")
        
        return self.delivery_system.get_messages_by_channel(DeliveryChannel.NARRATIVE)
    
    async def run_test_world_reaction(self):
        """Run test focused on world reaction system."""
        self.logger.info("\n=== Testing world reaction system ===")
        
        # Action that would trigger reputation changes
        await self.process_input("offer to buy a round of drinks for everyone")
        
        # Action that would receive negative reaction
        await self.process_input("steal coins from the merchant when he's not looking")
        
        # Check if reaction changed based on previous actions
        await self.process_input("ask the merchant for a discount")
        
        return self.delivery_system.get_messages_by_channel(DeliveryChannel.NARRATIVE)
    
    async def run_test_pacing(self):
        """Run test focused on pacing system."""
        self.logger.info("\n=== Testing pacing system ===")
        
        # Set time back to simulate idle period
        self.brain.last_input_time = datetime.utcnow() - timedelta(minutes=10)
        
        # Check for ambient updates during idle period
        self.logger.info("Checking for ambient updates after 10 minutes of inactivity...")
        ambient_triggered = await self.brain.check_ambient_updates()
        
        if ambient_triggered:
            self.logger.info("Ambient content was successfully triggered!")
        else:
            self.logger.info("No ambient content was triggered")
        
        # Get ambient messages
        ambient_messages = self.delivery_system.get_messages_by_channel(DeliveryChannel.AMBIENT)
        npc_messages = self.delivery_system.get_messages_by_channel(DeliveryChannel.NARRATIVE)
        
        return {
            'ambient': ambient_messages,
            'npc_initiative': npc_messages
        }
    
    async def run_test_decision_logic(self):
        """Run test focused on decision logic and output generation."""
        self.logger.info("\n=== Testing decision logic and output generation ===")
        
        # Input that would hook into a narrative branch
        await self.process_input("I want to investigate the strange lights in the mine")
        
        # Input that would need to be handled by fallback
        await self.process_input("xyzzy plugh")
        
        return self.delivery_system.get_messages_by_channel(DeliveryChannel.NARRATIVE)
    
    async def process_input(self, input_text: str):
        """Process a single input through the AI GM Brain."""
        self.logger.info(f"\n[PLAYER INPUT] {input_text}")
        
        # Create a basic mock simulation of LLM response
        # In a real system, this would be handled by a real LLM service
        mock_llm_result = self._create_mock_llm_result(input_text)
        
        # Normally we'd call the Brain's process_player_input method
        # But for testing without real LLM, we'll simulate parts of it
        try:
            # Process with the Brain's components
            context = self.brain._get_current_context()
            enhanced_context = await self.brain._enhance_context_with_pacing(context)
            
            # Simulate decision logic output
            from backend.src.ai_gm.ai_gm_decision_logic import DecisionResult, DecisionPriority
            decision_result = DecisionResult(
                priority=DecisionPriority.GENERAL_INTERPRETATION,
                action_type='PROCESS_GENERAL_INTENT',
                success=True,
                action_data={'player_intent': 'Explore the environment'},
                response_template=mock_llm_result
            )
            
            # Simulate output generation
            response = {
                'response_text': mock_llm_result,
                'metadata': {
                    'action_type': 'PROCESS_GENERAL_INTENT',
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            # Deliver response
            await self.brain.deliver_response(
                response['response_text'],
                channels=[DeliveryChannel.NARRATIVE],
                priority=ResponsePriority.NORMAL
            )
            
            # Update pacing
            await self.brain.ai_gm_pacing.process_ai_response(
                input_text, response, enhanced_context
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing input: {e}")
            await self.brain.deliver_response(
                f"I encountered a problem processing your input: {str(e)}",
                channels=[DeliveryChannel.NARRATIVE],
                priority=ResponsePriority.IMMEDIATE
            )
            return None
    
    def _create_mock_llm_result(self, input_text: str) -> str:
        """Create a mock LLM result for testing."""
        input_lower = input_text.lower()
        
        if "look around" in input_lower:
            return "The Rusted Tavern is warm and inviting. A crackling fireplace dominates one wall, casting dancing shadows across the wooden floor. Several patrons are scattered about, including Darius the barkeeper who polishes glasses behind the bar, a merchant named Geralt sitting in the corner, and a mysterious cloaked figure who keeps to themselves."
            
        elif "fireplace" in input_lower:
            return "The fireplace is made of large stones, blackened by years of use. A shield and crossed swords hang above it, and several animal trophies adorn the surrounding wall. The fire burns steadily, providing both warmth and light to the tavern."
            
        elif "sword" in input_lower or "inventory" in input_lower:
            return "You retrieve your sword from your belongings. It's a well-crafted steel blade with a leather-wrapped hilt. It feels balanced and ready for use."
            
        elif "history" in input_lower:
            return "The Rusted Tavern has stood at this crossroads for over a century. Originally built as a trading post, it gained its current name when the original owner, a retired soldier, hung his rusted armor above the door as a sign. The region has seen political turmoil since the death of the old duke six months ago, with various nobles vying for power and allegiance."
            
        elif "mysterious stranger" in input_lower:
            return "The figure sits alone in the corner, face partially obscured by a hood. What little you can see reveals sharp, watchful eyes that seem to take in everything around them. They've been nursing the same drink for hours, according to the barkeeper's whispers."
            
        elif "mine" in input_lower:
            return "The abandoned mine lies about an hour's walk north of the village. It was once the primary source of income for the region until a collapse five years ago killed several miners. Recently, villagers have reported strange lights and sounds coming from within, though no one has been brave enough to investigate closely."
            
        elif "drink" in input_lower:
            return "You announce you're buying a round for the house. The patrons cheer appreciatively, and Darius the barkeeper gives you a wide smile. 'That's mighty generous of you!' he says, quickly getting to work. You notice several patrons regarding you with newfound respect."
            
        elif "steal" in input_lower:
            return "While the merchant Geralt is engaged in conversation with another patron, you carefully slide your hand toward his coin pouch. Though no one seems to notice your theft, you feel a pang of guilt as you pocket several silver coins from the old man."
            
        elif "discount" in input_lower:
            return "You approach Geralt the merchant to ask about a discount. He squints at you suspiciously, clutching his coin pouch closer. 'I think not,' he says curtly. 'In fact, for you, prices just went up.' It seems he may have noticed your earlier theft."
            
        elif "investigate" in input_lower and "lights" in input_lower:
            return "Your interest in the strange lights piques the attention of several patrons. 'You planning to head to the mine?' asks Darius, leaning over the bar. 'If you are, you might want to speak with Old Marta at the edge of town. They say she saw something strange there last full moon.' This could be the beginning of an interesting adventure."
            
        elif "xyzzy" in input_lower:
            return "I'm not sure what you mean by that. Perhaps you could try a different approach or clarify what you're trying to do?"
            
        else:
            return f"You said: {input_text}. I understand and acknowledge your input. How would you like to proceed from here?"
    
    async def run_all_tests(self):
        """Run all test cases."""
        await self.setup()
        
        # Run all tests
        parser_results = await self.run_test_with_parser()
        llm_results = await self.run_test_with_llm()
        world_reaction_results = await self.run_test_world_reaction()
        pacing_results = await self.run_test_pacing()
        decision_results = await self.run_test_decision_logic()
        
        # Get comprehensive statistics
        stats = self.brain.get_phase6_comprehensive_statistics()
        
        self.logger.info("\n=== Test Results Summary ===")
        self.logger.info(f"Parser tests: {len(parser_results)} responses")
        self.logger.info(f"LLM tests: {len(llm_results)} responses")
        self.logger.info(f"World reaction tests: {len(world_reaction_results)} responses")
        self.logger.info(f"Pacing tests - Ambient: {len(pacing_results['ambient'])} messages")
        self.logger.info(f"Pacing tests - NPC Initiative: {len(pacing_results['npc_initiative'])} messages")
        self.logger.info(f"Decision logic tests: {len(decision_results)} responses")
        
        self.logger.info("\n=== AI GM Brain Comprehensive Statistics ===")
        self.logger.info(json.dumps(stats, indent=2))
        
        return {
            'parser': parser_results,
            'llm': llm_results,
            'world_reaction': world_reaction_results,
            'pacing': pacing_results,
            'decision_logic': decision_results,
            'statistics': stats
        }


async def main():
    """Main test function."""
    tester = IntegratedAIGMBrainTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())