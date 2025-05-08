"""
Example usage of the memory and state compression systems.

This module demonstrates how to use these systems in various scenarios.
"""
from datetime import datetime
from typing import Dict, List, Any

from ..shared.models import Character, Location, NPC, Domain, DomainType, GrowthTier, Tag
from .memory_manager import memory_manager, MemoryTier, MemoryType
from .state_compression import StateCompressor, PriorityStateQueue


def example_memory_usage():
    """Example of using the memory manager."""
    print("\n=== Memory Manager Example ===")
    
    # Example game ID
    game_id = "example_game_123"
    
    # Add memories of different types and importance
    memory_manager.add_memory(
        type=MemoryType.WORLD_EVENT,
        content="You discovered the ancient ruins of Eldoria.",
        importance=8,  # Very important
        tier=MemoryTier.LONG_TERM,  # This should be remembered for a long time
        tags=["discovery", "ruins", "eldoria"],
        game_id=game_id
    )
    
    memory_manager.add_memory(
        type=MemoryType.NPC_INTERACTION,
        content="Arcanist Lyra told you about the lost artifact of Zephyr.",
        importance=7,
        tier=MemoryTier.MEDIUM_TERM,
        tags=["conversation", "quest", "artifact"],
        metadata={"npc_id": "lyra_001", "location": "Academy of Magic"},
        game_id=game_id
    )
    
    memory_manager.add_memory(
        type=MemoryType.COMBAT,
        content="You defeated a pack of dire wolves near the western forest.",
        importance=4,  # Moderately important
        tier=MemoryTier.SHORT_TERM,  # This will be forgotten relatively soon
        tags=["combat", "victory", "forest"],
        metadata={"enemies": ["dire_wolf"], "difficulty": "medium"},
        game_id=game_id
    )
    
    memory_manager.remember_conversation(
        game_id=game_id,
        speaker="Blacksmith Thorgar",
        target="Player",
        dialogue="Bring me 5 iron ingots and 2 ancient cores, and I'll forge you a weapon worthy of legend.",
        importance=6
    )
    
    # Retrieve memories by type
    combat_memories = memory_manager.get_memories(
        game_id=game_id,
        types=[MemoryType.COMBAT],
        limit=5
    )
    
    print(f"Combat memories: {len(combat_memories)}")
    for memory in combat_memories:
        print(f"- {memory.content}")
    
    # Retrieve memories by tags
    quest_related = memory_manager.get_memories(
        game_id=game_id,
        tags=["quest", "artifact"],
        limit=5
    )
    
    print(f"\nQuest-related memories: {len(quest_related)}")
    for memory in quest_related:
        print(f"- {memory.content}")
    
    # Get a narrative summary
    narrative = memory_manager.get_recent_narrative(game_id)
    print(f"\nNarrative summary:\n{narrative}")
    
    # Get relevant context for a specific query
    context = memory_manager.get_relevant_context(
        game_id=game_id,
        query="artifact Zephyr Lyra",
        token_limit=200
    )
    
    print(f"\nContext for 'artifact Zephyr':\n{context}")
    
    # Consolidate important memories
    consolidated = memory_manager.consolidate_memories(game_id)
    print(f"\nConsolidated memories:\n{consolidated}")


def create_example_game_state() -> Dict[str, Any]:
    """Create an example game state for compression tests."""
    # Create character with domains
    character = Character(
        id=1,
        name="Thalia Stormbringer",
        class_="Battlemage",
        background="War Orphan",
        level=5,
        xp=1250,
        stats={
            "strength": 12,
            "dexterity": 14,
            "intelligence": 16,
            "charisma": 13
        },
        max_health=85,
        current_health=65,
        max_mana=60,
        current_mana=42
    )
    
    # Add domains
    character.domains = {
        DomainType.BODY: Domain(
            type=DomainType.BODY,
            value=3,
            growth_points=42,
            growth_required=100,
            usage_count=28,
            growth_log=[],
            level_ups_required=9
        ),
        DomainType.MIND: Domain(
            type=DomainType.MIND,
            value=4,
            growth_points=76,
            growth_required=100,
            usage_count=35,
            growth_log=[],
            level_ups_required=9
        ),
        DomainType.SPIRIT: Domain(
            type=DomainType.SPIRIT,
            value=2,
            growth_points=15,
            growth_required=100,
            usage_count=12,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.SOCIAL: Domain(
            type=DomainType.SOCIAL,
            value=2,
            growth_points=33,
            growth_required=100,
            usage_count=15,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.CRAFT: Domain(
            type=DomainType.CRAFT,
            value=1,
            growth_points=50,
            growth_required=100,
            usage_count=8,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.AUTHORITY: Domain(
            type=DomainType.AUTHORITY,
            value=1,
            growth_points=10,
            growth_required=100,
            usage_count=4,
            growth_log=[],
            level_ups_required=8
        ),
        DomainType.AWARENESS: Domain(
            type=DomainType.AWARENESS,
            value=2,
            growth_points=55,
            growth_required=100,
            usage_count=20,
            growth_log=[],
            level_ups_required=8
        )
    }
    
    # Create current location with NPCs
    npcs = [
        NPC(
            id=101,
            name="Master Arcanist Lyra",
            description="A stern woman with silver-streaked hair and eyes that sparkle with arcane energy. She's known for her vast knowledge of ancient magical artifacts.",
            attitude="neutral",
            dialogue=[],
            domain_bias={
                DomainType.MIND: 2,  # Favors intellectual pursuits
                DomainType.CRAFT: 1,
                DomainType.SOCIAL: -1,  # Dislikes social manipulation
            },
            first_encounter=False
        ),
        NPC(
            id=102,
            name="Apprentice Elian",
            description="A nervous young man with ink-stained fingers and disheveled robes. He follows Lyra everywhere, taking notes on her every word.",
            attitude="friendly",
            dialogue=[],
            domain_bias={
                DomainType.MIND: 1,
                DomainType.SOCIAL: 1,
            },
            first_encounter=True
        )
    ]
    
    location = Location(
        id=201,
        name="Tower of Arcane Studies",
        description="An imposing tower of blue-gray stone that reaches toward the clouds. Inside, the air hums with magical energy, and the walls are lined with ancient tomes and scrolls. The smell of parchment and arcane reagents fills the air.",
        type="magical_academy",
        connections=[202, 203, 205],
        npcs=npcs
    )
    
    # Create game state object
    game_state = {
        "game_id": "example_game_123",
        "character": character,
        "location": location,
        "inventory": {
            "max_weight": 100,
            "current_weight": 32,
            "items": [
                {
                    "id": 301,
                    "name": "Apprentice's Staff",
                    "description": "A wooden staff with a small blue crystal at the top.",
                    "quantity": 1,
                    "weight": 3,
                    "type": "weapon",
                    "properties": {
                        "damage": 8,
                        "effects": [
                            {
                                "type": "mana_regen",
                                "value": 2
                            }
                        ]
                    }
                },
                {
                    "id": 302,
                    "name": "Health Potion",
                    "description": "A small vial of red liquid that heals wounds.",
                    "quantity": 5,
                    "weight": 0.5,
                    "type": "consumable",
                    "properties": {
                        "effects": [
                            {
                                "type": "healing",
                                "value": 20
                            }
                        ]
                    }
                },
                {
                    "id": 303,
                    "name": "Ancient Rune Fragment",
                    "description": "A piece of stone with strange markings. It seems to be part of something larger.",
                    "quantity": 1,
                    "weight": 1,
                    "type": "quest_item"
                }
            ]
        },
        "quests": [
            {
                "id": 401,
                "title": "The Lost Artifact of Zephyr",
                "description": "Master Arcanist Lyra has tasked you with finding the fragments of the lost artifact of Zephyr, said to control the winds themselves.",
                "status": "active"
            },
            {
                "id": 402,
                "title": "Apprentice in Peril",
                "description": "Elian has gone missing while researching in the catacombs beneath the tower. Find him before it's too late.",
                "status": "active"
            },
            {
                "id": 403,
                "title": "Wolves at the Gate",
                "description": "Clear the western road of dire wolves that have been attacking travelers.",
                "status": "completed"
            }
        ],
        "narrative_content": "You stand in the grand study of the Tower of Arcane Studies, surrounded by floating tomes and glittering magical apparatuses. Master Arcanist Lyra eyes you with careful assessment as her apprentice, Elian, scribbles furiously in a notebook nearby. 'So,' she says, 'you've found the first fragment. Impressive... but three more remain scattered across the realm.'"
    }
    
    return game_state


def example_state_compression():
    """Example of using the state compression utilities."""
    print("\n=== State Compression Example ===")
    
    # Create example game state
    game_state = create_example_game_state()
    
    # Create low-detail summary
    low_detail = StateCompressor.create_game_state_summary(game_state, "low")
    print("Low detail summary size:", len(str(low_detail)), "characters")
    
    # Create medium-detail summary
    medium_detail = StateCompressor.create_game_state_summary(game_state, "medium")
    print("Medium detail summary size:", len(str(medium_detail)), "characters")
    
    # Create high-detail summary
    high_detail = StateCompressor.create_game_state_summary(game_state, "high")
    print("High detail summary size:", len(str(high_detail)), "characters")
    print("Full game state size:", len(str(game_state)), "characters")
    
    # Create narrative summary
    narrative = StateCompressor.create_narrative_state_summary(game_state)
    print(f"\nNarrative State Summary:\n{narrative[:500]}...\n(truncated)")


def example_priority_queue():
    """Example of using the priority state queue."""
    print("\n=== Priority Queue Example ===")
    
    # Create a priority queue
    queue = PriorityStateQueue(max_entries=20)
    
    # Add various entries with different priorities
    queue.add_entry(
        id="location_tower",
        content="You are in the Tower of Arcane Studies, a center of magical learning.",
        category="location",
        priority=0.9,  # Very high priority
        metadata={"location_id": 201}
    )
    
    queue.add_entry(
        id="npc_lyra",
        content="Master Arcanist Lyra is a stern woman with silver-streaked hair who specializes in magical artifacts.",
        category="npc",
        priority=0.85,
        metadata={"npc_id": 101}
    )
    
    queue.add_entry(
        id="quest_artifact",
        content="You are searching for the fragments of the lost artifact of Zephyr, which can control the winds.",
        category="quest",
        priority=0.8,
        metadata={"quest_id": 401}
    )
    
    queue.add_entry(
        id="npc_elian",
        content="Apprentice Elian is a nervous young man who has gone missing in the catacombs.",
        category="npc",
        priority=0.75,
        metadata={"npc_id": 102}
    )
    
    queue.add_entry(
        id="player_status",
        content="You are a level 5 Battlemage named Thalia Stormbringer with moderate injuries (65/85 HP).",
        category="character",
        priority=0.95,  # Highest priority
        metadata={"character_id": 1}
    )
    
    queue.add_entry(
        id="recent_event",
        content="You recently found a fragment of the ancient rune you're searching for.",
        category="event",
        priority=0.7,
        metadata={"event_time": datetime.utcnow().isoformat()}
    )
    
    # Get all entries
    all_entries = queue.get_entries()
    print(f"All entries ({len(all_entries)}):")
    for i, entry in enumerate(all_entries):
        print(f"{i+1}. [{entry['category']}] {entry['content']} (Priority: {entry['priority']:.2f})")
    
    # Get only character and quest entries
    char_quest = queue.get_entries(categories=["character", "quest"])
    print(f"\nCharacter and quest entries ({len(char_quest)}):")
    for i, entry in enumerate(char_quest):
        print(f"{i+1}. [{entry['category']}] {entry['content']} (Priority: {entry['priority']:.2f})")
    
    # Get formatted context
    context = queue.get_formatted_context(min_priority=0.7)
    print(f"\nFormatted context:\n{context}")
    
    # Update priorities to simulate aging
    print("\nUpdating priorities to simulate aging...")
    queue.update_priorities()
    
    # Get updated entries
    updated = queue.get_entries()
    print(f"\nUpdated entries ({len(updated)}):")
    for i, entry in enumerate(updated):
        print(f"{i+1}. [{entry['category']}] {entry['content']} (Priority: {entry['priority']:.2f})")


def run_all_examples():
    """Run all examples."""
    example_memory_usage()
    example_state_compression()
    example_priority_queue()


if __name__ == "__main__":
    run_all_examples()