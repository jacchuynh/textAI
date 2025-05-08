"""
Memory connector module that integrates the memory system with events.

This module subscribes to game events and automatically manages memories.
"""
from typing import Dict, Any, Optional
from datetime import datetime

from ..events.event_bus import event_bus, GameEvent, EventType
from .memory_manager import memory_manager, MemoryTier, MemoryType
from .state_compression import StateCompressor, PriorityStateQueue


class MemoryConnector:
    """
    Connects game events to the memory system.
    
    This class:
    1. Listens for game events
    2. Creates appropriate memories based on events
    3. Manages memory importance and relevance
    4. Provides context to the AI system
    """
    
    def __init__(self):
        """Initialize the memory connector."""
        self.priority_queues: Dict[str, PriorityStateQueue] = {}  # One per game
        self._register_event_handlers()
    
    def _register_event_handlers(self):
        """Register event handlers for all relevant event types."""
        # Character events
        event_bus.subscribe(EventType.CHARACTER_CREATED, self._handle_character_event)
        event_bus.subscribe(EventType.CHARACTER_UPDATED, self._handle_character_event)
        event_bus.subscribe(EventType.LEVEL_UP, self._handle_character_event)
        event_bus.subscribe(EventType.DOMAIN_INCREASED, self._handle_character_event)
        event_bus.subscribe(EventType.TAG_INCREASED, self._handle_character_event)
        
        # Action events
        event_bus.subscribe(EventType.ACTION_PERFORMED, self._handle_action_event)
        event_bus.subscribe(EventType.DOMAIN_CHECK, self._handle_action_event)
        
        # Location events
        event_bus.subscribe(EventType.LOCATION_DISCOVERED, self._handle_location_event)
        event_bus.subscribe(EventType.LOCATION_ENTERED, self._handle_location_event)
        
        # NPC events
        event_bus.subscribe(EventType.NPC_INTERACTION, self._handle_npc_event)
        event_bus.subscribe(EventType.NPC_RELATIONSHIP_CHANGED, self._handle_npc_event)
        
        # Combat events
        event_bus.subscribe(EventType.COMBAT_STARTED, self._handle_combat_event)
        event_bus.subscribe(EventType.COMBAT_ENDED, self._handle_combat_event)
        event_bus.subscribe(EventType.ENEMY_DEFEATED, self._handle_combat_event)
        event_bus.subscribe(EventType.CHARACTER_DEFEATED, self._handle_combat_event)
        
        # Quest events
        event_bus.subscribe(EventType.QUEST_STARTED, self._handle_quest_event)
        event_bus.subscribe(EventType.QUEST_COMPLETED, self._handle_quest_event)
        event_bus.subscribe(EventType.QUEST_FAILED, self._handle_quest_event)
        
        # Game session events
        event_bus.subscribe(EventType.GAME_STARTED, self._handle_game_event)
        event_bus.subscribe(EventType.GAME_SAVED, self._handle_game_event)
        event_bus.subscribe(EventType.GAME_LOADED, self._handle_game_event)
        event_bus.subscribe(EventType.GAME_ENDED, self._handle_game_event)
    
    def _handle_character_event(self, event: GameEvent):
        """Handle character-related events."""
        game_id = event.game_id
        if not game_id:
            return
            
        # Default importance by event type
        importance_by_type = {
            EventType.CHARACTER_CREATED: 8,
            EventType.CHARACTER_UPDATED: 3,
            EventType.LEVEL_UP: 9,
            EventType.DOMAIN_INCREASED: 7,
            EventType.TAG_INCREASED: 6
        }
        
        # Get base importance for this event type
        base_importance = importance_by_type.get(event.type, 5)
        
        # Adjust importance based on context
        importance = base_importance
        if event.type == EventType.DOMAIN_INCREASED:
            # Check if this is a tier change
            if "tier" in event.context:
                importance = 8  # Tier changes are more important
                
        elif event.type == EventType.TAG_INCREASED:
            # Higher ranks are more important
            if "new_rank" in event.context:
                new_rank = event.context["new_rank"]
                if isinstance(new_rank, (int, float)) and new_rank >= 3:
                    importance = 7
        
        # Determine memory type and tier
        memory_type = MemoryType.IMPORTANT
        
        # Level ups, tier changes, and character creation go in long-term memory
        memory_tier = MemoryTier.MEDIUM_TERM
        if importance >= 8 or event.type in [EventType.CHARACTER_CREATED, EventType.LEVEL_UP]:
            memory_tier = MemoryTier.LONG_TERM
        
        # Create formatted content based on event type
        content = self._format_character_event(event)
        
        # Extract tags from event
        tags = event.tags.copy() if event.tags else []
        tags.append("character")
        
        # Add memory
        memory_manager.add_memory(
            type=memory_type,
            content=content,
            importance=importance,
            tier=memory_tier,
            tags=tags,
            metadata=event.context,
            game_id=game_id
        )
        
        # Update priority queue
        self._update_priority_queue(
            game_id=game_id,
            id=f"character_{event.type.name}_{datetime.utcnow().isoformat()}",
            content=content,
            category="character",
            priority=importance / 10.0,
            metadata=event.context
        )
    
    def _format_character_event(self, event: GameEvent) -> str:
        """Format a character event into a readable description."""
        if event.type == EventType.CHARACTER_CREATED:
            return f"Character {event.actor} was created"
            
        elif event.type == EventType.LEVEL_UP:
            level = event.context.get("new_level", "?")
            return f"{event.actor} reached level {level}"
            
        elif event.type == EventType.DOMAIN_INCREASED:
            domain = event.context.get("domain", "unknown")
            value = event.context.get("new_value", "?")
            tier = event.context.get("tier", "").lower()
            
            if tier:
                return f"{event.actor}'s {domain} domain increased to {value} ({tier} tier)"
            else:
                return f"{event.actor}'s {domain} domain increased to {value}"
                
        elif event.type == EventType.TAG_INCREASED:
            tag = event.context.get("tag", "unknown")
            rank = event.context.get("new_rank", "?")
            return f"{event.actor}'s {tag} skill increased to rank {rank}"
            
        else:
            return f"Character {event.actor} was updated"
    
    def _handle_action_event(self, event: GameEvent):
        """Handle action-related events."""
        game_id = event.game_id
        if not game_id:
            return
            
        # For domain checks, only remember successful or spectacularly failed ones
        if event.type == EventType.DOMAIN_CHECK:
            success = event.context.get("success", False)
            margin = event.context.get("margin", 0)
            
            # Skip recording average checks
            if not success and abs(margin) < 5:
                return
                
            # Only significant checks are worth remembering
            if not success and abs(margin) < 10 and "difficulty" in event.context:
                difficulty = event.context["difficulty"]
                if isinstance(difficulty, (int, float)) and difficulty < 15:
                    return
            
            domain = event.context.get("domain", "unknown")
            success_str = "succeeded" if success else "failed"
            action = event.context.get("action", "an action")
            
            # Format content based on margin
            if success and margin >= 10:
                content = f"{event.actor} brilliantly succeeded at {action} using {domain}"
                importance = 6
            elif success:
                content = f"{event.actor} succeeded at {action} using {domain}"
                importance = 4
            elif margin <= -10:
                content = f"{event.actor} catastrophically failed at {action} using {domain}"
                importance = 6
            else:
                content = f"{event.actor} failed at {action} using {domain}"
                importance = 4
                
            # Domain checks go in short or medium term depending on significance
            memory_tier = MemoryTier.SHORT_TERM
            if importance >= 6:
                memory_tier = MemoryTier.MEDIUM_TERM
                
            # Add memory
            memory_manager.add_memory(
                type=MemoryType.PLAYER_ACTION,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=["action", domain.lower(), success_str],
                metadata=event.context,
                game_id=game_id
            )
            
        # For general actions, record most of them
        elif event.type == EventType.ACTION_PERFORMED:
            action = event.context.get("action", "an action")
            content = f"{event.actor} performed {action}"
            
            # Determine importance based on tags
            importance = 4  # Default
            if event.tags:
                if "important" in event.tags:
                    importance = 7
                elif "quest" in event.tags:
                    importance = 6
                elif "combat" in event.tags:
                    importance = 5
            
            # Add memory (medium term for important actions, short term otherwise)
            memory_tier = MemoryTier.SHORT_TERM
            if importance >= 6:
                memory_tier = MemoryTier.MEDIUM_TERM
                
            memory_manager.add_memory(
                type=MemoryType.PLAYER_ACTION,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["action"],
                metadata=event.context,
                game_id=game_id
            )
    
    def _handle_location_event(self, event: GameEvent):
        """Handle location-related events."""
        game_id = event.game_id
        if not game_id:
            return
            
        # Location discoveries are important
        if event.type == EventType.LOCATION_DISCOVERED:
            location_name = event.context.get("name", "a new location")
            content = f"{event.actor} discovered {location_name}"
            
            # Location discoveries are medium to long term
            importance = 7
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Special locations go in long-term memory
            if "special" in event.tags or "important" in event.tags:
                importance = 8
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.DISCOVERY,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["location", "discovery"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue with high priority for new discoveries
            self._update_priority_queue(
                game_id=game_id,
                id=f"location_discovery_{event.context.get('location_id', '')}",
                content=content,
                category="location",
                priority=importance / 10.0,
                metadata=event.context
            )
            
        # Location entries are less important but worth tracking
        elif event.type == EventType.LOCATION_ENTERED:
            location_name = event.context.get("name", "a location")
            content = f"{event.actor} entered {location_name}"
            
            # Location entries are usually short term
            importance = 4
            memory_tier = MemoryTier.SHORT_TERM
            
            # Unless it's an important location
            if "important" in event.tags:
                importance = 6
                memory_tier = MemoryTier.MEDIUM_TERM
                
            memory_manager.add_memory(
                type=MemoryType.WORLD_EVENT,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["location", "movement"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue with location info (always relevant to current state)
            self._update_priority_queue(
                game_id=game_id,
                id=f"current_location_{event.context.get('location_id', '')}",
                content=f"You are currently in {location_name}.",
                category="location",
                priority=0.9,  # Current location is very important for context
                metadata=event.context
            )
    
    def _handle_npc_event(self, event: GameEvent):
        """Handle NPC-related events."""
        game_id = event.game_id
        if not game_id:
            return
            
        if event.type == EventType.NPC_INTERACTION:
            # Get NPC name and dialogue
            npc_name = event.context.get("npc_name", "someone")
            dialogue = event.context.get("dialogue", "")
            player_action = event.context.get("player_action", "")
            
            # Format content
            if dialogue and player_action:
                content = f"{event.actor} spoke with {npc_name}. Player: \"{player_action}\" NPC: \"{dialogue}\""
            elif dialogue:
                content = f"{npc_name} said to {event.actor}: \"{dialogue}\""
            elif player_action:
                content = f"{event.actor} said to {npc_name}: \"{player_action}\""
            else:
                content = f"{event.actor} interacted with {npc_name}"
                
            # Determine importance based on context and tags
            importance = 5  # Default
            if "important" in event.tags:
                importance = 7
            elif "quest" in event.tags:
                importance = 6
                
            # First encounters are more important
            if event.context.get("first_encounter", False):
                importance += 1
                
            # Determine memory tier
            memory_tier = MemoryTier.MEDIUM_TERM
            if importance >= 7:
                memory_tier = MemoryTier.LONG_TERM
                
            # Add memory
            memory_manager.add_memory(
                type=MemoryType.NPC_INTERACTION,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["npc", "dialogue"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue (NPCs are relevant to the current state)
            self._update_priority_queue(
                game_id=game_id,
                id=f"npc_{event.context.get('npc_id', '')}",
                content=f"{npc_name} is currently here. Your last interaction: \"{player_action}\"",
                category="npc",
                priority=0.7,  # NPCs are important for context
                metadata=event.context
            )
            
        elif event.type == EventType.NPC_RELATIONSHIP_CHANGED:
            npc_name = event.context.get("npc_name", "someone")
            old_attitude = event.context.get("old_attitude", "unknown")
            new_attitude = event.context.get("new_attitude", "unknown")
            
            content = f"{npc_name}'s attitude toward {event.actor} changed from {old_attitude} to {new_attitude}"
            
            # Relationship changes are usually medium-term memories
            importance = 6
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Big changes are more important
            if (old_attitude == "hostile" and new_attitude == "friendly") or \
               (old_attitude == "friendly" and new_attitude == "hostile"):
                importance = 8
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.NPC_INTERACTION,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=["npc", "relationship", new_attitude],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue with relationship info
            self._update_priority_queue(
                game_id=game_id,
                id=f"npc_relationship_{event.context.get('npc_id', '')}",
                content=f"{npc_name} is {new_attitude} toward you.",
                category="npc",
                priority=0.7,
                metadata=event.context
            )
    
    def _handle_combat_event(self, event: GameEvent):
        """Handle combat-related events."""
        game_id = event.game_id
        if not game_id:
            return
            
        if event.type == EventType.COMBAT_STARTED:
            enemy_name = event.context.get("enemy_name", "an enemy")
            content = f"{event.actor} entered combat with {enemy_name}"
            
            # Combat starts are medium-term memories
            importance = 5
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Boss fights are more important
            if "boss" in event.tags or "important" in event.tags:
                importance = 7
                
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["combat", "enemy"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue with current combat state
            self._update_priority_queue(
                game_id=game_id,
                id=f"combat_state_{event.context.get('enemy_id', '')}",
                content=f"You are currently in combat with {enemy_name}.",
                category="combat",
                priority=0.95,  # Combat is highest priority while active
                metadata=event.context
            )
            
        elif event.type == EventType.COMBAT_ENDED:
            enemy_name = event.context.get("enemy_name", "an enemy")
            result = event.context.get("result", "unknown")
            
            if result == "victory":
                content = f"{event.actor} defeated {enemy_name} in combat"
            elif result == "defeat":
                content = f"{event.actor} was defeated by {enemy_name} in combat"
            elif result == "fled":
                content = f"{event.actor} fled from combat with {enemy_name}"
            else:
                content = f"{event.actor}'s combat with {enemy_name} ended"
                
            # Combat endings are medium-term memories
            importance = 5
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Significant battles are more important
            if "boss" in event.tags or "important" in event.tags:
                importance = 7
                memory_tier = MemoryTier.LONG_TERM
                
            # Defeats are more memorable
            if result == "defeat":
                importance += 1
                
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["combat", result],
                metadata=event.context,
                game_id=game_id
            )
            
            # Remove the active combat state from priority queue
            if game_id in self.priority_queues:
                queue = self.priority_queues[game_id]
                # Remove entries by finding ones with combat_state_ prefix
                entries = queue.get_entries(categories=["combat"])
                for entry in entries:
                    if entry["id"].startswith("combat_state_"):
                        # Instead of removing, just lower priority significantly
                        self._update_priority_queue(
                            game_id=game_id,
                            id=entry["id"],
                            content=f"Your last combat was with {enemy_name}, which ended in {result}.",
                            category="combat",
                            priority=0.4,  # Lower priority since combat is over
                            metadata=event.context
                        )
            
        elif event.type == EventType.ENEMY_DEFEATED:
            enemy_name = event.context.get("enemy_name", "an enemy")
            content = f"{event.actor} defeated {enemy_name}"
            
            # Enemy defeats are medium-term memories
            importance = 5
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Significant enemies are more important
            if "boss" in event.tags or "important" in event.tags:
                importance = 7
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["combat", "victory"],
                metadata=event.context,
                game_id=game_id
            )
            
        elif event.type == EventType.CHARACTER_DEFEATED:
            enemy_name = event.context.get("enemy_name", "an enemy")
            content = f"{event.actor} was defeated by {enemy_name}"
            
            # Character defeats are medium-term memories and more important
            importance = 6
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Significant defeats are more important
            if "boss" in event.tags or "important" in event.tags:
                importance = 8
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.COMBAT,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["combat", "defeat"],
                metadata=event.context,
                game_id=game_id
            )
    
    def _handle_quest_event(self, event: GameEvent):
        """Handle quest-related events."""
        game_id = event.game_id
        if not game_id:
            return
            
        if event.type == EventType.QUEST_STARTED:
            quest_title = event.context.get("title", "a quest")
            content = f"{event.actor} started the quest: {quest_title}"
            
            # Quest starts are medium-term memories
            importance = 6
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Main quests are more important
            if "main" in event.tags or "important" in event.tags:
                importance = 8
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.QUEST,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["quest", "started"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue with active quest
            self._update_priority_queue(
                game_id=game_id,
                id=f"quest_active_{event.context.get('quest_id', '')}",
                content=f"Active quest: {quest_title}",
                category="quest",
                priority=0.8,  # Active quests are important for context
                metadata=event.context
            )
            
        elif event.type == EventType.QUEST_COMPLETED:
            quest_title = event.context.get("title", "a quest")
            content = f"{event.actor} completed the quest: {quest_title}"
            
            # Quest completions are medium-term to long-term memories
            importance = 7
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Main quests are more important
            if "main" in event.tags or "important" in event.tags:
                importance = 9
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.QUEST,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["quest", "completed"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue: move from active to completed
            self._update_priority_queue(
                game_id=game_id,
                id=f"quest_active_{event.context.get('quest_id', '')}",
                content=f"Completed quest: {quest_title}",
                category="quest",
                priority=0.5,  # Lower priority once completed
                metadata=event.context
            )
            
        elif event.type == EventType.QUEST_FAILED:
            quest_title = event.context.get("title", "a quest")
            content = f"{event.actor} failed the quest: {quest_title}"
            
            # Quest failures are medium-term memories
            importance = 6
            memory_tier = MemoryTier.MEDIUM_TERM
            
            # Main quest failures are more important
            if "main" in event.tags or "important" in event.tags:
                importance = 8
                memory_tier = MemoryTier.LONG_TERM
                
            memory_manager.add_memory(
                type=MemoryType.QUEST,
                content=content,
                importance=importance,
                tier=memory_tier,
                tags=event.tags or ["quest", "failed"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Update priority queue: move from active to failed
            self._update_priority_queue(
                game_id=game_id,
                id=f"quest_active_{event.context.get('quest_id', '')}",
                content=f"Failed quest: {quest_title}",
                category="quest",
                priority=0.4,  # Lower priority once failed
                metadata=event.context
            )
    
    def _handle_game_event(self, event: GameEvent):
        """Handle game session events."""
        game_id = event.game_id
        if not game_id:
            return
            
        if event.type == EventType.GAME_STARTED:
            # Initialize a new priority queue for this game
            if game_id not in self.priority_queues:
                self.priority_queues[game_id] = PriorityStateQueue()
                
            content = f"Game session {game_id} started"
            
            # Game starts are long-term memories
            memory_manager.add_memory(
                type=MemoryType.IMPORTANT,
                content=content,
                importance=8,
                tier=MemoryTier.LONG_TERM,
                tags=["game", "session", "started"],
                metadata=event.context,
                game_id=game_id
            )
            
        elif event.type == EventType.GAME_ENDED:
            content = f"Game session {game_id} ended"
            
            # Game ends are long-term memories
            memory_manager.add_memory(
                type=MemoryType.IMPORTANT,
                content=content,
                importance=8,
                tier=MemoryTier.LONG_TERM,
                tags=["game", "session", "ended"],
                metadata=event.context,
                game_id=game_id
            )
            
            # Clean up priority queue
            if game_id in self.priority_queues:
                del self.priority_queues[game_id]
    
    def _update_priority_queue(self, 
                              game_id: str, 
                              id: str, 
                              content: str,
                              category: str,
                              priority: float,
                              metadata: Optional[Dict[str, Any]] = None):
        """Update the priority queue for a game."""
        # Create the queue if it doesn't exist
        if game_id not in self.priority_queues:
            self.priority_queues[game_id] = PriorityStateQueue()
            
        # Add/update the entry
        self.priority_queues[game_id].add_entry(
            id=id,
            content=content,
            category=category,
            priority=priority,
            metadata=metadata
        )
    
    def get_ai_context(self, 
                      game_id: str, 
                      query: Optional[str] = None, 
                      token_limit: int = 1000) -> str:
        """
        Get context for AI prompt generation.
        
        This combines:
        1. High-priority state elements (character, location, active quests)
        2. Relevant memories based on the query
        3. Recent significant events
        
        Args:
            game_id: The game ID
            query: Optional query to find relevant memories
            token_limit: Approximate token limit for context
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        # Add priority queue elements (current state)
        if game_id in self.priority_queues:
            state_context = self.priority_queues[game_id].get_formatted_context(
                min_priority=0.6,
                limit=10
            )
            if state_context:
                context_parts.append(state_context)
        
        # Add relevant memories
        if query:
            memory_context = memory_manager.get_relevant_context(
                game_id=game_id,
                query=query,
                token_limit=token_limit // 2  # Use half the tokens for memories
            )
            if memory_context:
                context_parts.append(memory_context)
        else:
            # Without a query, add recent important memories
            recent_memories = memory_manager.get_memories(
                game_id=game_id,
                tiers=[MemoryTier.SHORT_TERM, MemoryTier.MEDIUM_TERM],
                min_importance=7,
                limit=5
            )
            
            if recent_memories:
                memory_lines = ["## Recent Significant Events"]
                for memory in recent_memories:
                    memory_lines.append(f"- {memory.content}")
                context_parts.append("\n".join(memory_lines))
        
        # Combine all parts
        full_context = "\n\n".join(context_parts)
        
        # Apply token limit
        if len(full_context) > token_limit * 4:  # Rough estimate: 4 chars per token
            full_context = full_context[:token_limit * 4] + "...\n[Context truncated due to length]"
            
        return full_context
    
    def prune_old_memories(self, game_id: Optional[str] = None) -> int:
        """
        Prune old memories for efficient storage.
        
        Args:
            game_id: Optional game ID to prune memories for
            
        Returns:
            Number of memories pruned
        """
        # Short-term memories are aggressively pruned
        short_term_count = memory_manager.prune_old_memories(
            game_id=game_id, 
            hours=6,  # 6 hours for short-term
            min_importance=4
        )
        
        # Medium-term memories are moderately pruned
        medium_term_count = memory_manager.prune_old_memories(
            game_id=game_id,
            hours=72,  # 3 days for medium-term
            min_importance=6
        )
        
        # Long-term memories are lightly pruned
        long_term_count = memory_manager.prune_old_memories(
            game_id=game_id,
            hours=720,  # 30 days for long-term
            min_importance=8
        )
        
        # Update priorities in queue
        if game_id and game_id in self.priority_queues:
            self.priority_queues[game_id].update_priorities()
        elif game_id is None:
            for queue in self.priority_queues.values():
                queue.update_priorities()
                
        return short_term_count + medium_term_count + long_term_count


# Global memory connector instance
memory_connector = MemoryConnector()