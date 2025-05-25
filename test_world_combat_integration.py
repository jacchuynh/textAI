#!/usr/bin/env python3
"""
World Generator and Combat System Integration Test

This script tests how the world generation system integrates with the monster
combat system, specifically:
1. Creating a world with regions, biomes, and POIs
2. Spawning monsters appropriate to those regions/biomes
3. Testing combat between characters and region-appropriate monsters
"""

import sys
import os
import logging
import random
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("world_combat_test")

def print_section(title):
    """Print a section header for test output."""
    print("\n" + "="*80)
    print(f" {title}")
    print("="*80)

def setup_imports():
    """Add necessary directories to path and import required modules."""
    # Add backend/src to path if needed
    backend_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'src')
    if os.path.exists(backend_src) and backend_src not in sys.path:
        sys.path.append(backend_src)
        print(f"Added {backend_src} to Python path")
    
    # Import world generation components
    global WorldModel, BiomeType, POIType, POIState
    global DBRegion, DBBiome, DBPointOfInterest, DBGeneratedLocationDetails
    global POIPlacementService, WorldPersistenceManager
    global LocationGeneratorFactory, VillageGenerator, BaseLocationGenerator
    global CombatController, Combatant, CombatMove, Domain, MoveType, ThreatTier
    
    try:
        # Import world generation components
        from world_generation.world_model import (
            BiomeType, POIType, POIState,
            DBRegion, DBBiome, DBPointOfInterest, DBGeneratedLocationDetails
        )
        from world_generation.poi_placement_service import POIPlacementService
        from world_generation.world_persistence_manager import WorldPersistenceManager
        
        # Import location generators
        from location_generators.generator_factory import LocationGeneratorFactory
        from location_generators.village_generator import VillageGenerator
        from location_generators.base_generator import BaseLocationGenerator
        
        # Import combat system
        from monster_combat_test import (
            CombatController, Combatant, CombatMove, Domain, MoveType, 
            ThreatTier, create_monster_from_archetype
        )
        
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False

def create_test_world():
    """Create a test world with regions, biomes, and POIs."""
    print_section("Creating Test World")
    
    # Create a simple world model
    try:
        # Create a region
        region = DBRegion(
            name="Test Wilderness",
            description="A wild region for testing monster encounters",
            dominant_races=["human", "elf", "beastfolk"]
        )
        
        print(f"✓ Created region: {region.name}")
        
        # Create biomes within the region
        biomes = []
        
        forest_biome = DBBiome(
            region_id=region.id,
            name="Dense Forest",
            biome_type=BiomeType.WHISPERING_WOODS.value,
            description="A thick forest with ancient trees",
            poi_density=0.8,
            flora_fauna=["wolves", "deer", "hawks", "ancient_trees"],
            atmospheric_tags=["mysterious", "ancient", "shadowy"],
            hazards=["quicksand", "poisonous_plants"]
        )
        biomes.append(forest_biome)
        
        mountain_biome = DBBiome(
            region_id=region.id,
            name="Highland Peaks",
            biome_type=BiomeType.CRYSTAL_HIGHLANDS.value,
            description="Rugged mountain terrain with exposed minerals",
            poi_density=0.5,
            flora_fauna=["mountain_goats", "eagles", "alpine_flowers"],
            atmospheric_tags=["windy", "exposed", "majestic"],
            hazards=["rockslides", "steep_cliffs"]
        )
        biomes.append(mountain_biome)
        
        print(f"✓ Created {len(biomes)} biomes")
        
        # Create POIs in each biome
        pois = []
        
        # Forest POIs
        forest_village = DBPointOfInterest(
            biome_id=forest_biome.id,
            poi_type=POIType.VILLAGE.value,
            generated_name="Oakrest",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["near_river", "forest_clearing"]
        )
        pois.append(forest_village)
        
        forest_cave = DBPointOfInterest(
            biome_id=forest_biome.id,
            poi_type=POIType.CAVE.value,
            generated_name="Shadow Hollow",
            current_state=POIState.UNDISCOVERED.value,
            relative_location_tags=["hillside", "hidden"]
        )
        pois.append(forest_cave)
        
        # Mountain POIs
        mountain_ruins = DBPointOfInterest(
            biome_id=mountain_biome.id,
            poi_type=POIType.RUIN.value,
            generated_name="Frostwatch Ruins",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["mountain_peak", "exposed"]
        )
        pois.append(mountain_ruins)
        
        mountain_shrine = DBPointOfInterest(
            biome_id=mountain_biome.id,
            poi_type=POIType.SHRINE.value,
            generated_name="Crystal Altar",
            current_state=POIState.UNDISCOVERED.value,
            relative_location_tags=["hidden_valley", "near_waterfall"]
        )
        pois.append(mountain_shrine)
        
        print(f"✓ Created {len(pois)} POIs")
        
        # Return all created objects
        return {
            "region": region,
            "biomes": biomes,
            "pois": pois
        }
    
    except Exception as e:
        print(f"❌ Error creating test world: {e}")
        return None

def create_monsters_for_biome(biome):
    """Create monsters appropriate for a specific biome."""
    print(f"Creating monsters for biome: {biome.name}")
    
    try:
        # Import monster database and archetype functions
        from monster_combat_test import (
            MonsterDatabase, 
            create_monster_from_archetype,
            ThreatTier
        )
        
        # Create and load monster database
        monster_db = MonsterDatabase()
        
        # Map biome types to appropriate monster categories
        biome_to_category = {
            BiomeType.WHISPERING_WOODS.value: "BEAST",
            BiomeType.CRYSTAL_HIGHLANDS.value: "ELEMENTAL",
            BiomeType.VERDANT_FRONTIER.value: "BEAST",
            BiomeType.EMBER_WASTES.value: "ELEMENTAL",
            BiomeType.SHIMMERING_MARSHES.value: "ABERRATION",
            BiomeType.FROSTBOUND_TUNDRA.value: "ELEMENTAL",
            BiomeType.CRIMSON_SCARS.value: "UNDEAD",
            BiomeType.RELIC_ZONES.value: "CONSTRUCT"
        }
        
        # Get appropriate category for this biome
        category = biome_to_category.get(biome.biome_type, "BEAST")
        
        # Get random monster archetypes appropriate for this biome
        archetypes = []
        for i in range(3):  # Get 3 different monster types
            try:
                archetype = monster_db.get_random_archetype(
                    category=getattr(monster_db, f"ThreatCategory.{category}", None)
                )
                if archetype:
                    archetypes.append(archetype)
            except Exception as inner_e:
                print(f"Could not get archetype: {inner_e}")
        
        # Create monster instances from archetypes
        monsters = []
        for archetype in archetypes:
            # Create different threat tiers
            tiers = [ThreatTier.MINION, ThreatTier.STANDARD, ThreatTier.ELITE]
            for tier in tiers:
                try:
                    monster, moves = create_monster_from_archetype(
                        archetype,
                        tier=tier,
                        level=random.randint(1, 3)
                    )
                    monsters.append((monster, moves))
                except Exception as inner_e:
                    print(f"Could not create monster: {inner_e}")
        
        print(f"✓ Created {len(monsters)} monsters for {biome.name}")
        return monsters
    
    except Exception as e:
        print(f"❌ Error creating monsters: {e}")
        return []

def create_test_player():
    """Create a test player character for combat."""
    try:
        # Import necessary combat classes
        from monster_combat_test import Combatant, CombatMove, Domain, MoveType
        
        # Create player domains
        domains = {
            Domain.BODY: 3,
            Domain.MIND: 2,
            Domain.CRAFT: 2,
            Domain.AWARENESS: 3,
            Domain.SOCIAL: 1,
            Domain.AUTHORITY: 1,
            Domain.SPIRIT: 2,
            Domain.FIRE: 1,
            Domain.WATER: 1,
            Domain.EARTH: 1,
            Domain.AIR: 1,
            Domain.LIGHT: 1,
            Domain.DARKNESS: 0,
            Domain.SOUND: 0,
            Domain.WIND: 1,
            Domain.ICE: 0
        }
        
        # Create player
        player = Combatant(
            name="Test Adventurer",
            domains=domains,
            max_health=30,
            current_health=30,
            max_stamina=20,
            current_stamina=20,
            max_focus=15,
            current_focus=15,
            max_spirit=10,
            current_spirit=10
        )
        
        # Create player moves
        moves = [
            CombatMove(
                name="Sword Strike",
                description="A powerful strike with a sword",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY],
                base_damage=5,
                stamina_cost=2
            ),
            CombatMove(
                name="Precise Thrust",
                description="A precise thrust targeting a weak point",
                move_type=MoveType.FOCUS,
                domains=[Domain.AWARENESS, Domain.BODY],
                base_damage=3,
                stamina_cost=1,
                focus_cost=2
            ),
            CombatMove(
                name="Defensive Stance",
                description="A defensive stance to ward off attacks",
                move_type=MoveType.DEFEND,
                domains=[Domain.BODY, Domain.AWARENESS],
                base_damage=0,
                stamina_cost=1
            ),
            CombatMove(
                name="Elemental Strike",
                description="A strike enhanced with elemental power",
                move_type=MoveType.FORCE,
                domains=[Domain.BODY, Domain.FIRE],
                base_damage=7,
                stamina_cost=3,
                spirit_cost=2
            )
        ]
        
        print(f"✓ Created player character: {player.name}")
        return player, moves
    
    except Exception as e:
        print(f"❌ Error creating player: {e}")
        return None, None

def test_combat_in_location(poi, monster_tuple):
    """Test combat between a player and a monster in a specific location."""
    monster, monster_moves = monster_tuple
    
    print(f"\nTesting combat at {poi.generated_name} ({poi.poi_type})")
    
    try:
        # Create player
        player, player_moves = create_test_player()
        
        # Create combat controller
        combat_controller = CombatController(
            environment_name=f"{poi.generated_name} ({poi.poi_type})"
        )
        
        # Print combatant stats
        print(f"\nPlayer: {player.name}")
        print(f"Health: {player.current_health}/{player.max_health}")
        print(f"Stamina: {player.current_stamina}/{player.max_stamina}")
        print(f"Focus: {player.current_focus}/{player.max_focus}")
        print(f"Spirit: {player.current_spirit}/{player.max_spirit}")
        
        print(f"\nMonster: {monster.name}")
        print(f"Health: {monster.current_health}/{monster.max_health}")
        print(f"Stamina: {monster.current_stamina}/{monster.max_stamina}")
        print(f"Focus: {monster.current_focus}/{monster.max_focus}")
        print(f"Spirit: {monster.current_spirit}/{monster.max_spirit}")
        
        # Simulate a few rounds of combat
        for round_num in range(1, 4):  # 3 rounds
            print(f"\n--- Round {round_num} ---")
            
            # Select random moves
            player_move = random.choice(player_moves)
            monster_move = random.choice(monster_moves)
            
            print(f"Player uses {player_move.name}")
            print(f"Monster uses {monster_move.name}")
            
            # Resolve combat
            result = combat_controller.resolve_combat_exchange(
                actor_name=player.name,
                actor_move=player_move,
                target_name=monster.name,
                target_move=monster_move,
                actor=player,
                target=monster
            )
            
            # Print results
            print(f"\nCombat result: {result['narrative']}")
            print(f"Player health: {player.current_health}/{player.max_health}")
            print(f"Monster health: {monster.current_health}/{monster.max_health}")
            
            # Check if combat is over
            if player.is_defeated() or monster.is_defeated():
                winner = "Monster" if player.is_defeated() else "Player"
                print(f"\nCombat over! {winner} wins!")
                break
        
        return True
    
    except Exception as e:
        print(f"❌ Error in combat: {e}")
        return False

def main():
    """Main test function."""
    print_section("World Generator and Combat System Integration Test")
    
    # Setup imports
    if not setup_imports():
        print("❌ Failed to import required modules")
        return
    
    # Create test world
    world_data = create_test_world()
    if not world_data:
        print("❌ Failed to create test world")
        return
    
    # Create monsters for each biome
    biome_monsters = {}
    for biome in world_data["biomes"]:
        monsters = create_monsters_for_biome(biome)
        if monsters:
            biome_monsters[biome.id] = monsters
    
    if not biome_monsters:
        print("❌ Failed to create any monsters")
        return
    
    # Test combat in each POI
    for poi in world_data["pois"]:
        # Get monsters for this POI's biome
        biome_id = poi.biome_id
        if biome_id in biome_monsters and biome_monsters[biome_id]:
            # Select a random monster for this POI
            monster_tuple = random.choice(biome_monsters[biome_id])
            test_combat_in_location(poi, monster_tuple)
    
    print_section("Integration Test Complete")
    print("✓ World generator and combat system integration test completed")

if __name__ == "__main__":
    main()