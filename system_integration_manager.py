#!/usr/bin/env python3
"""
System Integration Manager for TextRealmsAI

This module provides a comprehensive integration layer that connects all game systems
to create a smooth, interconnected gameplay experience.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
from enum import Enum, auto

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'backend', 'src'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SystemType(Enum):
    """Types of game systems available for integration."""
    AI_GM = "ai_gm"
    TEXT_PARSER = "text_parser"
    CRAFTING = "crafting"
    MAGIC = "magic"
    COMBAT = "combat"
    ECONOMY = "economy"
    BUSINESS = "business"
    NPC = "npc"
    QUEST = "quest"
    NARRATIVE = "narrative"
    EVENTS = "events"
    INVENTORY = "inventory"
    PERSISTENCE = "persistence"


class IntegrationEvent:
    """Represents an event that needs to be processed across multiple systems."""
    
    def __init__(self, event_type: str, source_system: SystemType, data: Dict[str, Any]):
        self.event_type = event_type
        self.source_system = source_system
        self.data = data
        self.timestamp = datetime.now()
        self.processed_by = set()
        
    def mark_processed(self, system: SystemType):
        """Mark this event as processed by a system."""
        self.processed_by.add(system)
        
    def is_processed_by(self, system: SystemType) -> bool:
        """Check if this event has been processed by a system."""
        return system in self.processed_by


class SystemIntegrationManager:
    """
    Central hub for managing integration between all game systems.
    
    This class orchestrates communication between systems, manages shared state,
    and ensures consistent experience across all game mechanics.
    """
    
    def __init__(self, session_id: str, player_id: str):
        """
        Initialize the integration manager.
        
        Args:
            session_id: Unique identifier for the game session
            player_id: Identifier for the player
        """
        self.session_id = session_id
        self.player_id = player_id
        self.start_time = datetime.now()
        
        # System registry
        self.systems = {}
        self.system_status = {}
        
        # Event system
        self.event_queue = []
        self.event_handlers = {}
        
        # Shared context
        self.shared_context = {
            'session_id': session_id,
            'player_id': player_id,
            'game_state': {},
            'player_state': {},
            'world_state': {},
            'system_metrics': {}
        }
        
        # Initialize core systems
        self._initialize_core_systems()
        
        logger.info(f"System Integration Manager initialized for session {session_id}")
    
    def _initialize_core_systems(self):
        """Initialize the core game systems."""
        
        # Initialize AI GM Brain (the central orchestrator)
        try:
            from ai_gm_direct_test import create_unified_gm
            
            self.ai_gm = create_unified_gm(
                game_id=self.session_id,
                player_id=self.player_id,
                initial_context=self.shared_context
            )
            
            self.register_system(SystemType.AI_GM, self.ai_gm)
            logger.info("✅ AI GM Brain initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI GM Brain: {e}")
        
        # Initialize Text Parser
        try:
            from backend.src.text_parser.parser_integrator import create_parser_integrator
            
            self.text_parser = create_parser_integrator()
            self.register_system(SystemType.TEXT_PARSER, self.text_parser)
            logger.info("✅ Text Parser initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Text Parser not available: {e}")
        
        # Initialize Crafting System
        try:
            from backend.src.crafting.services.crafting_integration_service import create_crafting_integration_service
            
            self.crafting_system = create_crafting_integration_service()
            self.register_system(SystemType.CRAFTING, self.crafting_system)
            logger.info("✅ Crafting System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Crafting System not available: {e}")
        
        # Initialize Magic System
        try:
            from backend.src.game_engine.magic_combat_integration import create_magic_integration_services
            
            self.magic_system = create_magic_integration_services()
            self.register_system(SystemType.MAGIC, self.magic_system)
            logger.info("✅ Magic System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Magic System not available: {e}")
        
        # Initialize Economy System
        try:
            from backend.src.game_engine.economy_system import economy_system
            
            self.economy_system = economy_system
            self.register_system(SystemType.ECONOMY, self.economy_system)
            logger.info("✅ Economy System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Economy System not available: {e}")
        
        # Initialize Business System
        try:
            from backend.src.business.api.business_api import BusinessAPI
            
            self.business_system = BusinessAPI()
            self.register_system(SystemType.BUSINESS, self.business_system)
            logger.info("✅ Business System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Business System not available: {e}")
        
        # Initialize Quest System
        try:
            from backend.src.quest.services.quest_manager_service import QuestManagerService
            
            self.quest_system = QuestManagerService()
            self.register_system(SystemType.QUEST, self.quest_system)
            logger.info("✅ Quest System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Quest System not available: {e}")
        
        # Initialize Narrative System
        try:
            from backend.src.narrative_engine.service import NarrativeService
            
            self.narrative_system = NarrativeService()
            self.register_system(SystemType.NARRATIVE, self.narrative_system)
            logger.info("✅ Narrative System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Narrative System not available: {e}")
        
        # Initialize Events System (World Events)
        try:
            from backend.src.economy.services.world_event_service import WorldEventService
            
            self.events_system = WorldEventService()
            self.register_system(SystemType.EVENTS, self.events_system)
            logger.info("✅ Events System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Events System not available: {e}")
        
        # Initialize Combat System
        try:
            from backend.src.game_engine.combat_system import CombatSystem
            
            self.combat_system = CombatSystem()
            self.register_system(SystemType.COMBAT, self.combat_system)
            logger.info("✅ Combat System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Combat System not available: {e}")
        
        # Initialize NPC System
        try:
            from backend.src.npc.npc_generator_service import NpcGeneratorService
            
            self.npc_system = NpcGeneratorService()
            self.register_system(SystemType.NPC, self.npc_system)
            logger.info("✅ NPC System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ NPC System not available: {e}")
        
        # Initialize Inventory System
        try:
            from backend.src.inventory.inventory_system import InventorySystem
            
            self.inventory_system = InventorySystem()
            
            # Connect the integration manager to the inventory system for event emission
            self.inventory_system.set_system_integration_manager(self)
            
            # Connect VocabularyManager if Text Parser is available
            if hasattr(self, 'text_parser') and self.text_parser:
                try:
                    vocabulary_manager = getattr(self.text_parser, 'vocabulary_manager', None)
                    if vocabulary_manager:
                        self.inventory_system.set_vocabulary_manager(vocabulary_manager)
                        logger.info("🔗 Connected Inventory System to VocabularyManager")
                except Exception as e:
                    logger.warning(f"⚠️ Could not connect VocabularyManager to Inventory: {e}")
            
            self.register_system(SystemType.INVENTORY, self.inventory_system)
            logger.info("✅ Inventory System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Inventory System not available: {e}")
        
        # Initialize Persistence System
        try:
            from backend.src.persistence.world_state_persistence import WorldStatePersistenceManager
            
            self.persistence_system = WorldStatePersistenceManager()
            
            # Start persistence session
            self.persistence_system.start_session(self.session_id)
            
            # Configure auto-save settings
            self.persistence_system.configure_auto_save(
                enabled=True,
                interval_seconds=300,  # 5 minutes
                backup_interval_seconds=3600,  # 1 hour
                min_changes_threshold=1
            )
            
            # Start auto-save timer for background checking
            self.persistence_system.start_auto_save_timer(check_interval=60)  # Check every minute
            
            # Set up auto-save event handlers
            self._setup_persistence_hooks()
            
            self.register_system(SystemType.PERSISTENCE, self.persistence_system)
            logger.info("✅ Persistence System initialized")
            
        except Exception as e:
            logger.warning(f"⚠️ Persistence System not available: {e}")
    
    def register_system(self, system_type: SystemType, system_instance: Any):
        """
        Register a game system with the integration manager.
        
        Args:
            system_type: Type of the system being registered
            system_instance: The actual system instance
        """
        self.systems[system_type] = system_instance
        self.system_status[system_type] = {
            'active': True,
            'last_used': datetime.now(),
            'operations_count': 0,
            'errors_count': 0
        }
        
        # Set up event handlers for this system
        self._register_system_events(system_type, system_instance)
        
        logger.info(f"Registered system: {system_type.value}")
    
    def _register_system_events(self, system_type: SystemType, system_instance: Any):
        """Register event handlers for a system."""
        
        if system_type == SystemType.AI_GM:
            # AI GM handles narrative integration
            self.register_event_handler('player_action', self._handle_ai_gm_integration)
            self.register_event_handler('world_change', self._handle_ai_gm_integration)
            
        elif system_type == SystemType.TEXT_PARSER:
            # Text parser handles command parsing
            self.register_event_handler('player_input', self._handle_text_parser_integration)
            
        elif system_type == SystemType.CRAFTING:
            # Crafting system handles item creation
            self.register_event_handler('craft_item', self._handle_crafting_integration)
            self.register_event_handler('use_item', self._handle_crafting_integration)
            
        elif system_type == SystemType.MAGIC:
            # Magic system handles spell casting
            self.register_event_handler('cast_spell', self._handle_magic_integration)
            self.register_event_handler('magic_effect', self._handle_magic_integration)
            
        elif system_type == SystemType.ECONOMY:
            # Economy system handles economic transactions
            self.register_event_handler('transaction', self._handle_economy_integration)
            self.register_event_handler('trade', self._handle_economy_integration)
            self.register_event_handler('currency_change', self._handle_economy_integration)
            
        elif system_type == SystemType.BUSINESS:
            # Business system handles business operations
            self.register_event_handler('business_interaction', self._handle_business_integration)
            self.register_event_handler('shop_purchase', self._handle_business_integration)
            
        elif system_type == SystemType.QUEST:
            # Quest system handles quest progression
            self.register_event_handler('quest_start', self._handle_quest_integration)
            self.register_event_handler('quest_update', self._handle_quest_integration)
            self.register_event_handler('quest_complete', self._handle_quest_integration)
            
        elif system_type == SystemType.NARRATIVE:
            # Narrative system handles story generation
            self.register_event_handler('story_event', self._handle_narrative_integration)
            self.register_event_handler('world_change', self._handle_narrative_integration)
            
        elif system_type == SystemType.EVENTS:
            # Events system handles world events
            self.register_event_handler('world_event', self._handle_events_integration)
            self.register_event_handler('environmental_change', self._handle_events_integration)
            
        elif system_type == SystemType.COMBAT:
            # Combat system handles combat encounters
            self.register_event_handler('combat_start', self._handle_combat_integration)
            self.register_event_handler('combat_action', self._handle_combat_integration)
            self.register_event_handler('combat_end', self._handle_combat_integration)
            
        elif system_type == SystemType.NPC:
            # NPC system handles NPC interactions
            self.register_event_handler('npc_interaction', self._handle_npc_integration)
            self.register_event_handler('npc_dialogue', self._handle_npc_integration)
            self.register_event_handler('npc_spawn', self._handle_npc_integration)
            
        elif system_type == SystemType.INVENTORY:
            # Inventory system handles item management
            self.register_event_handler('item_take', self._handle_inventory_integration)
            self.register_event_handler('item_drop', self._handle_inventory_integration)
            self.register_event_handler('item_use', self._handle_inventory_integration)
            self.register_event_handler('inventory_view', self._handle_inventory_integration)
            self.register_event_handler('item_give', self._handle_inventory_integration)
            
        elif system_type == SystemType.PERSISTENCE:
            # Persistence system handles state saving
            self.register_event_handler('location_change', self._handle_persistence_integration)
            self.register_event_handler('inventory_change', self._handle_persistence_integration)
            self.register_event_handler('world_state_change', self._handle_persistence_integration)
            # Register handlers for inventory system persistence events
            self.register_event_handler('item_given', self._handle_persistence_integration)
            self.register_event_handler('item_taken', self._handle_persistence_integration)
            self.register_event_handler('item_dropped', self._handle_persistence_integration)
            self.register_event_handler('item_used', self._handle_persistence_integration)
            self.register_event_handler('equipment_change', self._handle_persistence_integration)
    
    def register_event_handler(self, event_type: str, handler):
        """Register an event handler for a specific event type."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, source_system: SystemType, data: Dict[str, Any]):
        """
        Emit an event that will be processed by all relevant systems.
        
        Args:
            event_type: Type of event being emitted
            source_system: System that emitted the event
            data: Event data
        """
        logger.info(f"📢 Emitting event: {event_type} from {source_system.value} with data keys: {list(data.keys())}")
        
        event = IntegrationEvent(event_type, source_system, data)
        self.event_queue.append(event)
        
        # Process event immediately
        self._process_event(event)
        
        logger.debug(f"Event emitted: {event_type} from {source_system.value}")
    
    def _process_event(self, event: IntegrationEvent):
        """Process an integration event."""
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error processing event {event.event_type}: {e}")
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        """
        Process player input through the integrated system pipeline.
        
        Args:
            input_text: Raw player input text
            
        Returns:
            Integrated response from all systems
        """
        start_time = datetime.now()
        
        # Emit player input event
        self.emit_event('player_input', SystemType.AI_GM, {
            'input_text': input_text,
            'player_id': self.player_id,
            'timestamp': start_time
        })
        
        # Process through text parser first (if available)
        parsed_result = None
        if SystemType.TEXT_PARSER in self.systems:
            try:
                parsed_result = self.systems[SystemType.TEXT_PARSER].process_text_command(
                    self.player_id, input_text, self.shared_context
                )
                
                if parsed_result.get('success'):
                    # Emit specific action events based on parsing
                    self._emit_parsed_action_events(parsed_result)
                    
            except Exception as e:
                logger.error(f"Text parser error: {e}")
        
        # Process through AI GM for narrative integration
        ai_response = None
        if SystemType.AI_GM in self.systems:
            try:
                # Provide parser context to AI GM
                enhanced_context = self.shared_context.copy()
                if parsed_result:
                    enhanced_context['mechanical_result'] = parsed_result
                
                ai_response = self.systems[SystemType.AI_GM].process_player_input(input_text)
                
            except Exception as e:
                logger.error(f"AI GM error: {e}")
                ai_response = {
                    'response_text': "The game master is temporarily unavailable.",
                    'metadata': {'error': str(e)}
                }
        
        # Combine results from all systems
        combined_response = self._combine_system_responses(
            input_text, parsed_result, ai_response, start_time
        )
        
        # Update shared context
        self._update_shared_context(combined_response)
        
        return combined_response
    
    def _emit_parsed_action_events(self, parsed_result: Dict[str, Any]):
        """Emit specific events based on parsed actions."""
        action_type = parsed_result.get('action_type', '')
        
        if 'craft' in action_type.lower():
            self.emit_event('craft_item', SystemType.TEXT_PARSER, parsed_result)
        elif 'cast' in action_type.lower() or 'spell' in action_type.lower():
            self.emit_event('cast_spell', SystemType.TEXT_PARSER, parsed_result)
        elif 'trade' in action_type.lower() or 'buy' in action_type.lower() or 'sell' in action_type.lower():
            self.emit_event('trade_action', SystemType.TEXT_PARSER, parsed_result)
        else:
            self.emit_event('player_action', SystemType.TEXT_PARSER, parsed_result)
    
    def _combine_system_responses(self, input_text: str, parsed_result: Optional[Dict], 
                                 ai_response: Optional[Dict], start_time: datetime) -> Dict[str, Any]:
        """Combine responses from all systems into a unified response."""
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Primary response text (prefer AI GM, fallback to parser)
        response_text = "I'm not sure how to respond to that."
        
        if ai_response and ai_response.get('response_text'):
            response_text = ai_response['response_text']
        elif parsed_result and parsed_result.get('success') and parsed_result.get('message'):
            response_text = parsed_result['message']
        
        # Combine metadata
        metadata = {
            'processing_time': processing_time,
            'systems_involved': [],
            'mechanical_changes': [],
            'narrative_elements': [],
            'session_id': self.session_id,
            'player_id': self.player_id
        }
        
        if parsed_result:
            metadata['systems_involved'].append('text_parser')
            if parsed_result.get('success'):
                metadata['mechanical_changes'].append(parsed_result)
        
        if ai_response:
            metadata['systems_involved'].append('ai_gm')
            metadata['narrative_elements'].append(ai_response)
        
        return {
            'response_text': response_text,
            'metadata': metadata,
            'success': True,
            'input_text': input_text,
            'timestamp': start_time.isoformat()
        }
    
    def _update_shared_context(self, response: Dict[str, Any]):
        """Update shared context based on the response."""
        
        # Update system metrics
        for system_name in response['metadata'].get('systems_involved', []):
            if system_name not in self.shared_context['system_metrics']:
                self.shared_context['system_metrics'][system_name] = {
                    'operations': 0,
                    'last_used': None,
                    'avg_response_time': 0
                }
            
            metrics = self.shared_context['system_metrics'][system_name]
            metrics['operations'] += 1
            metrics['last_used'] = datetime.now().isoformat()
        
        # Update player state based on mechanical changes
        for change in response['metadata'].get('mechanical_changes', []):
            if 'player_changes' in change:
                self.shared_context['player_state'].update(change['player_changes'])
    
    # Event handlers for specific systems
    
    def _handle_ai_gm_integration(self, event: IntegrationEvent):
        """Handle events that need AI GM narrative integration."""
        if event.is_processed_by(SystemType.AI_GM):
            return
        
        # Add narrative context to the event
        if SystemType.AI_GM in self.systems:
            try:
                # Let AI GM know about the event for future context
                self.systems[SystemType.AI_GM].update_context({
                    'recent_event': event.data,
                    'event_type': event.event_type,
                    'timestamp': event.timestamp.isoformat()
                })
                
                event.mark_processed(SystemType.AI_GM)
                
            except Exception as e:
                logger.error(f"AI GM integration error: {e}")
    
    def _handle_text_parser_integration(self, event: IntegrationEvent):
        """Handle events that need text parser processing."""
        if event.is_processed_by(SystemType.TEXT_PARSER):
            return
        
        # Text parser doesn't need post-processing for most events
        event.mark_processed(SystemType.TEXT_PARSER)
    
    def _handle_crafting_integration(self, event: IntegrationEvent):
        """Handle events related to crafting system."""
        if event.is_processed_by(SystemType.CRAFTING):
            return
        
        if SystemType.CRAFTING in self.systems:
            try:
                # Update crafting system with the event
                # This could trigger market updates, skill changes, etc.
                event.mark_processed(SystemType.CRAFTING)
                
            except Exception as e:
                logger.error(f"Crafting integration error: {e}")
    
    def _handle_magic_integration(self, event: IntegrationEvent):
        """Handle events related to magic system."""
        if event.is_processed_by(SystemType.MAGIC):
            return
        
        if SystemType.MAGIC in self.systems:
            try:
                # Process magic-related events
                event.mark_processed(SystemType.MAGIC)
                
            except Exception as e:
                logger.error(f"Magic integration error: {e}")
    
    def _handle_economy_integration(self, event: IntegrationEvent):
        """Handle events related to economy system."""
        if event.is_processed_by(SystemType.ECONOMY):
            return
        
        if SystemType.ECONOMY in self.systems:
            try:
                # Process economy-related events (transactions, trades, currency changes)
                if event.event_type in ['transaction', 'trade', 'currency_change']:
                    # Update economic data and market dynamics
                    pass
                
                event.mark_processed(SystemType.ECONOMY)
                
            except Exception as e:
                logger.error(f"Economy integration error: {e}")
    
    def _handle_business_integration(self, event: IntegrationEvent):
        """Handle events related to business system."""
        if event.is_processed_by(SystemType.BUSINESS):
            return
        
        if SystemType.BUSINESS in self.systems:
            try:
                # Process business-related events (shop interactions, purchases)
                if event.event_type in ['business_interaction', 'shop_purchase']:
                    # Update business states and inventories
                    pass
                
                event.mark_processed(SystemType.BUSINESS)
                
            except Exception as e:
                logger.error(f"Business integration error: {e}")
    
    def _handle_quest_integration(self, event: IntegrationEvent):
        """Handle events related to quest system."""
        if event.is_processed_by(SystemType.QUEST):
            return
        
        if SystemType.QUEST in self.systems:
            try:
                # Process quest-related events (quest updates, completions)
                if event.event_type in ['quest_start', 'quest_update', 'quest_complete']:
                    # Update quest progress and objectives
                    pass
                
                event.mark_processed(SystemType.QUEST)
                
            except Exception as e:
                logger.error(f"Quest integration error: {e}")
    
    def _handle_narrative_integration(self, event: IntegrationEvent):
        """Handle events related to narrative system."""
        if event.is_processed_by(SystemType.NARRATIVE):
            return
        
        if SystemType.NARRATIVE in self.systems:
            try:
                # Process narrative-related events (story events, world changes)
                if event.event_type in ['story_event', 'world_change']:
                    # Generate appropriate narrative responses
                    pass
                
                event.mark_processed(SystemType.NARRATIVE)
                
            except Exception as e:
                logger.error(f"Narrative integration error: {e}")
    
    def _handle_events_integration(self, event: IntegrationEvent):
        """Handle events related to events system."""
        if event.is_processed_by(SystemType.EVENTS):
            return
        
        if SystemType.EVENTS in self.systems:
            try:
                # Process world events (environmental changes, world events)
                if event.event_type in ['world_event', 'environmental_change']:
                    # Trigger world-wide events and reactions
                    pass
                
                event.mark_processed(SystemType.EVENTS)
                
            except Exception as e:
                logger.error(f"Events integration error: {e}")
    
    def _handle_combat_integration(self, event: IntegrationEvent):
        """Handle events related to combat system."""
        if event.is_processed_by(SystemType.COMBAT):
            return
        
        if SystemType.COMBAT in self.systems:
            try:
                # Process combat-related events (combat start, actions, end)
                if event.event_type in ['combat_start', 'combat_action', 'combat_end']:
                    # Manage combat state and flow
                    pass
                
                event.mark_processed(SystemType.COMBAT)
                
            except Exception as e:
                logger.error(f"Combat integration error: {e}")
    
    def _handle_npc_integration(self, event: IntegrationEvent):
        """Handle events related to NPC system."""
        if event.is_processed_by(SystemType.NPC):
            return
        
        if SystemType.NPC in self.systems:
            try:
                # Process NPC-related events (interactions, dialogue, spawning)
                if event.event_type in ['npc_interaction', 'npc_dialogue', 'npc_spawn']:
                    # Update NPC behaviors and states
                    pass
                
                event.mark_processed(SystemType.NPC)
                
            except Exception as e:
                logger.error(f"NPC integration error: {e}")
    
    def _handle_inventory_integration(self, event: IntegrationEvent):
        """Handle events related to inventory system."""
        if event.is_processed_by(SystemType.INVENTORY):
            return
        
        if SystemType.INVENTORY in self.systems:
            try:
                # Process inventory-related events
                inventory_system = self.systems[SystemType.INVENTORY]
                
                if event.event_type == 'item_take':
                    # Handle item taking
                    result = inventory_system.process_command(
                        'TAKE', 
                        event.data.get('entity_id', 'player'),
                        event.data.get('item_name', ''),
                        event.data.get('quantity', 1)
                    )
                    event.data['result'] = result
                    
                elif event.event_type == 'item_drop':
                    # Handle item dropping
                    result = inventory_system.process_command(
                        'DROP',
                        event.data.get('entity_id', 'player'),
                        event.data.get('item_name', ''),
                        event.data.get('quantity', 1)
                    )
                    event.data['result'] = result
                    
                elif event.event_type == 'item_use':
                    # Handle item usage
                    result = inventory_system.process_command(
                        'USE',
                        event.data.get('entity_id', 'player'),
                        event.data.get('item_name', ''),
                        1
                    )
                    event.data['result'] = result
                    
                elif event.event_type == 'inventory_view':
                    # Handle inventory viewing
                    result = inventory_system.process_command(
                        'INVENTORY_VIEW',
                        event.data.get('entity_id', 'player'),
                        '',
                        0
                    )
                    event.data['result'] = result
                    
                elif event.event_type == 'item_give':
                    # Handle item giving
                    result = inventory_system.process_command(
                        'GIVE',
                        event.data.get('giver_id', 'player'),
                        event.data.get('item_name', ''),
                        event.data.get('quantity', 1),
                        event.data.get('receiver_id', '')
                    )
                    event.data['result'] = result
                
                event.mark_processed(SystemType.INVENTORY)
                
            except Exception as e:
                logger.error(f"Inventory integration error: {e}")
                event.data['error'] = str(e)
    
    def _handle_persistence_integration(self, event: IntegrationEvent):
        """Handle events related to persistence system."""
        logger.info(f"🔄 Processing persistence event: {event.event_type} from {event.source_system.value}")
        
        if event.is_processed_by(SystemType.PERSISTENCE):
            logger.debug(f"Event {event.event_type} already processed by persistence system")
            return
        
        if SystemType.PERSISTENCE in self.systems:
            try:
                persistence_system = self.systems[SystemType.PERSISTENCE]
                
                if event.event_type == 'location_change':
                    # Save location state when player moves
                    location_data = event.data.get('location_data', {})
                    location_id = event.data.get('location_id', '')
                    
                    if location_id and location_data:
                        result = persistence_system.save_location_state(location_id, location_data)
                        event.data['persistence_result'] = result
                        
                        # Mark current player location
                        self.shared_context['player_state']['current_location'] = location_id
                    
                elif event.event_type == 'inventory_change':
                    # Save player state when inventory changes
                    player_data = event.data.get('player_data', {})
                    if not player_data and 'player_state' in self.shared_context:
                        player_data = self.shared_context['player_state']
                    
                    if player_data:
                        result = persistence_system.save_player_state(player_data)
                        event.data['persistence_result'] = result
                        
                        # Mark persistence as dirty for inventory changes
                        persistence_system.mark_dirty("player")
                
                elif event.event_type == 'equipment_change':
                    # Save player state when equipment changes
                    player_data = event.data.get('player_state', {})
                    player_id = event.data.get('player_id', '')
                    action = event.data.get('action', '')
                    item_name = event.data.get('item_name', '')
                    
                    logger.info(f"Processing equipment change: {action} {item_name} for player {player_id}")
                    
                    if player_data:
                        result = persistence_system.save_player_state(player_data)
                        event.data['persistence_result'] = result
                        
                        # Mark persistence as dirty for equipment changes
                        persistence_system.mark_dirty("player")
                        
                        # Update shared context with latest player state
                        if player_id:
                            self.shared_context['player_state'] = player_data
                
                elif event.event_type == 'world_state_change':
                    # Save complete world state
                    world_state = event.data.get('world_state', {})
                    if not world_state:
                        world_state = self.shared_context.get('world_state', {})
                    
                    if world_state:
                        result = persistence_system.save_world_state(world_state)
                        event.data['persistence_result'] = result
                
                # Check if auto-save is needed
                if hasattr(persistence_system, 'auto_save_check'):
                    current_world_state = self.shared_context.get('world_state', {})
                    persistence_system.auto_save_check(current_world_state)
                
                event.mark_processed(SystemType.PERSISTENCE)
                
            except Exception as e:
                logger.error(f"Persistence integration error: {e}")
                event.data['error'] = str(e)
    
    def _setup_persistence_hooks(self):
        """Set up automatic persistence hooks for world state changes."""
        try:
            if SystemType.PERSISTENCE not in self.systems:
                return
            
            persistence_system = self.systems[SystemType.PERSISTENCE]
            
            # Register persistence event handlers for automatic saving
            def on_equipment_changed(data):
                """Handle equipment change events with proper world state update."""
                try:
                    player_state = data.get('player_state', {})
                    player_id = data.get('player_id', '')
                    action = data.get('action', '')
                    item_name = data.get('item_name', '')
                    
                    logger.debug(f"📢 Equipment changed: {action} {item_name} for player {player_id}")
                    
                    # Update world state through proper method
                    if player_state:
                        changes = {
                            'player': {
                                player_id: player_state
                            }
                        }
                        self._update_world_state(changes)
                        logger.debug(f"🔄 World state updated for equipment change")
                    
                    self.emit_event('equipment_change', SystemType.PERSISTENCE, data)
                    
                except Exception as e:
                    logger.error(f"Equipment change handler error: {e}")
            
            def on_inventory_changed(data):
                """Handle inventory change events with proper world state update."""
                try:
                    player_data = data.get('player_data', {})
                    player_id = data.get('player_id', '')
                    
                    logger.debug(f"📢 Inventory changed for player {player_id}")
                    
                    # Update world state through proper method
                    if player_data:
                        changes = {
                            'player': {
                                player_id: player_data
                            }
                        }
                        self._update_world_state(changes)
                        logger.debug(f"🔄 World state updated for inventory change")
                    
                    self.emit_event('inventory_change', SystemType.PERSISTENCE, data)
                    
                except Exception as e:
                    logger.error(f"Inventory change handler error: {e}")
            
            def on_location_changed(data):
                """Handle location change events with proper world state update."""
                try:
                    location_id = data.get('location_id', '')
                    location_data = data.get('location_data', {})
                    
                    logger.debug(f"📢 Location changed: {location_id}")
                    
                    # Update world state through proper method
                    if location_id and location_data:
                        changes = {
                            'locations': {
                                location_id: location_data
                            }
                        }
                        self._update_world_state(changes)
                        logger.debug(f"🔄 World state updated for location change")
                    
                    self.emit_event('location_change', SystemType.PERSISTENCE, data)
                    
                except Exception as e:
                    logger.error(f"Location change handler error: {e}")
            
            def on_world_state_changed(data):
                self.emit_event('world_state_change', SystemType.PERSISTENCE, data)
            
            def on_system_shutdown(data):
                # Force save on shutdown
                current_world_state = self.shared_context.get('world_state', {})
                if current_world_state:
                    persistence_system.save_world_state(current_world_state, force=True)
            
            # Register the handlers with the persistence system
            from backend.src.persistence.world_state_persistence import PersistenceEvent
            
            persistence_system.register_event_handler(
                PersistenceEvent.LOCATION_CHANGED, on_location_changed
            )
            persistence_system.register_event_handler(
                PersistenceEvent.ITEM_MOVED, on_inventory_changed
            )
            persistence_system.register_event_handler(
                PersistenceEvent.PLAYER_ACTION, on_inventory_changed
            )
            persistence_system.register_event_handler(
                PersistenceEvent.EQUIPMENT_CHANGED, on_equipment_changed
            )
            persistence_system.register_event_handler(
                PersistenceEvent.SYSTEM_SHUTDOWN, on_system_shutdown
            )
            
            logger.info("✅ Persistence hooks configured")
            
        except Exception as e:
            logger.error(f"Failed to setup persistence hooks: {e}")
    
    def save_game_state(self) -> bool:
        """
        Manually trigger a save of the current game state.
        
        Returns:
            True if save was successful
        """
        try:
            if SystemType.PERSISTENCE not in self.systems:
                logger.error("Persistence system not available")
                return False
            
            persistence_system = self.systems[SystemType.PERSISTENCE]
            
            # Collect current world state from all systems
            world_state = {
                'metadata': {
                    'session_id': self.session_id,
                    'player_id': self.player_id,
                    'saved_at': datetime.now().isoformat()
                },
                'shared_context': self.shared_context,
                'locations': {},
                'containers': {},
                'player': {}
            }
            
            # Get player state from inventory system
            if SystemType.INVENTORY in self.systems:
                try:
                    inventory_system = self.systems[SystemType.INVENTORY]
                    player_location = inventory_system.get_player_location(self.player_id)
                    player_inventory = inventory_system.get_entity_inventory(self.player_id)
                    
                    # Add current location to locations if it exists
                    if player_location:
                        world_state['locations'][player_location] = {
                            'location_id': player_location,
                            'name': player_location.replace('_', ' ').title(),
                            'description': f'Location: {player_location}',
                            'items': [],
                            'containers': {},
                            'visited': True
                        }
                        
                        # Add location containers if they exist
                        location_containers = inventory_system.location_container_system.get_containers_in_location(player_location)
                        if location_containers:
                            for container_id, container_data in location_containers.items():
                                world_state['containers'][container_id] = {
                                    'container_id': container_id,
                                    'location_id': player_location,
                                    'name': container_data.name,
                                    'items': [],  # Will need to get from container inventory
                                    'container_type': container_data.container_type.value if hasattr(container_data.container_type, 'value') else str(container_data.container_type),
                                    'is_locked': container_data.is_locked
                                }
                    
                    world_state['player'] = {
                        self.player_id: {
                            'player_id': self.player_id,
                            'current_location': player_location,
                            'inventory': player_inventory.get('items', []) if player_inventory else [],
                            'equipped_items': {},  # TODO: Get from equipment system
                            'stats': {},
                            'discovered_locations': [],  # Use list instead of set for JSON compatibility
                            'last_save': datetime.now().isoformat(),
                            'custom_data': {}
                        }
                    }
                except Exception as e:
                    logger.warning(f"Could not collect player state: {e}")
            
            # Save the world state
            result = persistence_system.save_world_state(world_state, force=True)
            
            if result:
                logger.info(f"Game state saved successfully for session {self.session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to save game state: {e}")
            return False
    
    def load_game_state(self, game_id: Optional[str] = None) -> bool:
        """
        Load a previously saved game state.
        
        Args:
            game_id: Game ID to load (uses current session if None)
            
        Returns:
            True if load was successful
        """
        try:
            if SystemType.PERSISTENCE not in self.systems:
                logger.error("Persistence system not available")
                return False
            
            persistence_system = self.systems[SystemType.PERSISTENCE]
            
            # Load the world state
            world_state = persistence_system.load_world_state(game_id)
            
            if not world_state:
                logger.warning(f"No saved state found for game {game_id or self.session_id}")
                return False
            
            # Restore shared context
            if 'shared_context' in world_state:
                self.shared_context.update(world_state['shared_context'])
            
            # Restore player state to inventory system
            if 'player' in world_state and SystemType.INVENTORY in self.systems:
                try:
                    inventory_system = self.systems[SystemType.INVENTORY]
                    player_data = world_state['player']
                    
                    # Handle both dictionary format and PlayerState object format
                    if hasattr(player_data, 'current_location'):
                        # PlayerState object format
                        current_location = player_data.current_location
                    elif isinstance(player_data, dict) and 'current_location' in player_data:
                        # Dictionary format
                        current_location = player_data['current_location']
                    else:
                        current_location = None
                    
                    # Restore player location
                    if current_location:
                        inventory_system.update_player_location(
                            self.player_id, 
                            current_location
                        )
                    
                    # TODO: Restore inventory items
                    # TODO: Restore equipped items
                    
                except Exception as e:
                    logger.warning(f"Could not restore player state: {e}")
            
            logger.info(f"Game state loaded successfully for session {game_id or self.session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load game state: {e}")
            return False
    
    def update_world_state(self, world_state: Dict[str, Any]):
        """
        Update the shared world state and notify persistence system.
        
        Args:
            world_state: Updated world state
        """
        try:
            # Update shared context
            self.shared_context['world_state'] = world_state
            
            # Update persistence system cache for auto-save
            if SystemType.PERSISTENCE in self.systems:
                persistence_system = self.systems[SystemType.PERSISTENCE]
                if hasattr(persistence_system, 'update_cached_world_state'):
                    persistence_system.update_cached_world_state(world_state)
            
            logger.debug("World state updated")
            
        except Exception as e:
            logger.error(f"Failed to update world state: {e}")
    
    def _update_world_state(self, changes: Dict[str, Any]):
        """
        Update the cached world state and trigger persistence if needed.
        
        Args:
            changes: Dictionary of changes to apply to world state
        """
        try:
            # Initialize world state structure if needed
            if 'world_state' not in self.shared_context:
                self.shared_context['world_state'] = {
                    'locations': {},
                    'containers': {},
                    'player': {},
                    'metadata': {
                        'last_updated': datetime.now().isoformat(),
                        'version': '1.0'
                    }
                }
            
            # Apply changes to world state
            world_state = self.shared_context['world_state']
            
            # Ensure metadata exists
            if 'metadata' not in world_state:
                world_state['metadata'] = {
                    'last_updated': datetime.now().isoformat(),
                    'version': '1.0'
                }
            
            # Handle structured updates
            for key, value in changes.items():
                if key in ['locations', 'containers', 'player']:
                    # Merge section-specific changes
                    if key not in world_state:
                        world_state[key] = {}
                    if isinstance(value, dict):
                        world_state[key].update(value)
                    else:
                        world_state[key] = value
                else:
                    # Direct assignment for other keys
                    world_state[key] = value
            
            # Update metadata
            world_state['metadata']['last_updated'] = datetime.now().isoformat()
            
            # Mark persistence system that world state has changed
            if SystemType.PERSISTENCE in self.systems:
                persistence_system = self.systems[SystemType.PERSISTENCE]
                
                # Mark appropriate sections as dirty based on changes
                for section in ['locations', 'containers', 'player']:
                    if section in changes:
                        persistence_system.mark_dirty(section)
                
                # Update cached world state in persistence system
                persistence_system.update_cached_world_state(world_state)
                
                # Trigger auto-save check with the constructed world state
                persistence_system.auto_save_check(world_state)
                
                logger.debug(f"🔄 World state updated with changes: {list(changes.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to update world state: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
