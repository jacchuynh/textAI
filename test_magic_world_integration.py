#!/usr/bin/env python3
"""
Magic System and World Generator Integration Test

This script tests how the magic system integrates with the world generation system,
specifically:
1. How leylines affect different regions and POIs
2. How different locations affect spell properties
3. How magical materials are distributed based on location types
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

logger = logging.getLogger("magic_world_test")

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
    global DBRegion, DBBiome, DBPointOfInterest
    global POIPlacementService, WorldPersistenceManager
    global LocationGeneratorFactory, VillageGenerator
    
    # Import magic system components
    global LeylineManager, LeylineType, LeylineStrength, LeylineStatus
    global SpellCraftingSystem, SpellElement, SpellPurpose, SpellTemplate
    global MagicalMaterialsManager, MaterialType, MaterialRarity
    
    try:
        # Import world generation components
        from world_generation.world_model import (
            WorldModel, BiomeType, POIType, POIState,
            DBRegion, DBBiome, DBPointOfInterest
        )
        from world_generation.poi_placement_service import POIPlacementService
        from world_generation.world_persistence_manager import WorldPersistenceManager
        
        # Import location generators
        from location_generators.generator_factory import LocationGeneratorFactory
        from location_generators.village_generator import VillageGenerator
        
        print("✓ World generation imports successful")
        
        # Import magic system components
        from magic_system.leyline_manager import (
            LeylineManager, LeylineType, LeylineStrength, LeylineStatus
        )
        from magic_system.spell_crafting import (
            SpellCraftingSystem, SpellElement, SpellPurpose, SpellTemplate
        )
        from magic_system.magical_materials import (
            MagicalMaterialsManager, MaterialType, MaterialRarity
        )
        
        print("✓ Magic system imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False

def create_test_world():
    """Create a test world with regions, biomes, and POIs."""
    print_section("Creating Test World")
    
    # Create a simple world model
    try:
        world_model = WorldModel()
        
        # Create a region
        region = DBRegion(
            id="test_region_1",
            name="Arcane Wilderness",
            description="A wild region with strong magical currents",
            dominant_races=["human", "elf", "beastfolk"]
        )
        
        world_model.add_region(region)
        print(f"✓ Created region: {region.name}")
        
        # Create biomes within the region
        biomes = []
        
        forest_biome = DBBiome(
            id="forest_biome_1",
            region_id=region.id,
            name="Whispering Woods",
            biome_type=BiomeType.WHISPERING_WOODS.value,
            description="A thick forest with ancient trees and magical auras",
            poi_density=0.8,
            flora_fauna=["wolves", "deer", "hawks", "ancient_trees", "magical_mushrooms"],
            atmospheric_tags=["mysterious", "ancient", "magical", "shadowy"],
            hazards=["wild_magic", "guardian_spirits", "mana_storms"]
        )
        biomes.append(forest_biome)
        
        crystal_biome = DBBiome(
            id="crystal_biome_1",
            region_id=region.id,
            name="Crystal Highlands",
            biome_type=BiomeType.CRYSTAL_HIGHLANDS.value,
            description="Rugged mountain terrain with exposed crystals and minerals",
            poi_density=0.5,
            flora_fauna=["mountain_goats", "crystal_beetles", "mana_falcons", "resonant_flowers"],
            atmospheric_tags=["resonant", "exposed", "majestic", "elemental"],
            hazards=["crystal_storms", "resonance_tremors", "elemental_rifts"]
        )
        biomes.append(crystal_biome)
        
        marsh_biome = DBBiome(
            id="marsh_biome_1",
            region_id=region.id,
            name="Shimmering Marshes",
            biome_type=BiomeType.SHIMMERING_MARSHES.value,
            description="A mysterious wetland where reality seems fluid",
            poi_density=0.6,
            flora_fauna=["glow_frogs", "dream_lilies", "mist_serpents", "illusion_birds"],
            atmospheric_tags=["misty", "illusory", "shifting", "reflective"],
            hazards=["will-o-wisps", "memory_pools", "reality_shifts"]
        )
        biomes.append(marsh_biome)
        
        print(f"✓ Created {len(biomes)} biomes")
        
        # Create POIs in each biome
        pois = []
        
        # Forest POIs
        forest_village = DBPointOfInterest(
            id="forest_village_1",
            biome_id=forest_biome.id,
            poi_type=POIType.VILLAGE.value,
            generated_name="Eldertree Haven",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["near_ancient_tree", "forest_clearing", "leyline_nexus"],
            position=(30, 50)  # x, y coordinates
        )
        pois.append(forest_village)
        
        forest_shrine = DBPointOfInterest(
            id="forest_shrine_1",
            biome_id=forest_biome.id,
            poi_type=POIType.SHRINE.value,
            generated_name="Whisperleaf Shrine",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["hidden_grove", "ancient_stones", "magical_spring"],
            position=(45, 60)
        )
        pois.append(forest_shrine)
        
        forest_ruin = DBPointOfInterest(
            id="forest_ruin_1",
            biome_id=forest_biome.id,
            poi_type=POIType.RUIN.value,
            generated_name="Arcane Academy Ruins",
            current_state=POIState.UNDISCOVERED.value,
            relative_location_tags=["overgrown", "magical_residue", "collapsed_towers"],
            position=(20, 70)
        )
        pois.append(forest_ruin)
        
        # Crystal Highland POIs
        crystal_mine = DBPointOfInterest(
            id="crystal_mine_1",
            biome_id=crystal_biome.id,
            poi_type=POIType.MINE.value,
            generated_name="Resonance Mine",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["crystal_cavern", "mountain_face", "magical_deposits"],
            position=(80, 30)
        )
        pois.append(crystal_mine)
        
        crystal_tower = DBPointOfInterest(
            id="crystal_tower_1",
            biome_id=crystal_biome.id,
            poi_type=POIType.TOWER.value,
            generated_name="Spire of Elements",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["mountain_peak", "elemental_convergence", "ancient_magic"],
            position=(90, 40)
        )
        pois.append(crystal_tower)
        
        # Marsh POIs
        marsh_village = DBPointOfInterest(
            id="marsh_village_1",
            biome_id=marsh_biome.id,
            poi_type=POIType.VILLAGE.value,
            generated_name="Misthollow",
            current_state=POIState.DISCOVERED.value,
            relative_location_tags=["stilt_houses", "foggy", "lantern_lit"],
            position=(60, 80)
        )
        pois.append(marsh_village)
        
        marsh_shrine = DBPointOfInterest(
            id="marsh_shrine_1",
            biome_id=marsh_biome.id,
            poi_type=POIType.SHRINE.value,
            generated_name="Veil Shrine",
            current_state=POIState.UNDISCOVERED.value,
            relative_location_tags=["illusion_veiled", "reality_thin", "dream_nexus"],
            position=(70, 90)
        )
        pois.append(marsh_shrine)
        
        print(f"✓ Created {len(pois)} POIs")
        
        # Return all created objects
        return {
            "world_model": world_model,
            "region": region,
            "biomes": biomes,
            "pois": pois
        }
    
    except Exception as e:
        print(f"❌ Error creating test world: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_leyline_generation(world_data):
    """Test the generation of leylines for the world."""
    print_section("Testing Leyline Generation")
    
    try:
        # Create leyline manager
        leyline_manager = LeylineManager()
        
        # Generate leylines for the region
        leylines = leyline_manager.generate_leylines_for_region(world_data["region"])
        
        print(f"✓ Generated {len(leylines)} leylines for {world_data['region'].name}")
        
        # Print leyline information
        for leyline in leylines:
            print(f"  - {leyline.name}: {leyline.leyline_type}, {leyline.strength}, {leyline.status}")
            print(f"    Path points: {len(leyline.path_points)}")
            print(f"    Width: {leyline.width}, Depth: {leyline.depth}")
            print(f"    Magical affinities: {', '.join([f'{k}: {v:.2f}' for k, v in leyline.magical_affinity.items()])}")
            print()
        
        # Assign leylines to POIs
        for biome in world_data["biomes"]:
            # Get POIs for this biome
            biome_pois = [poi for poi in world_data["pois"] if poi.biome_id == biome.id]
            leyline_manager.assign_leylines_to_pois(world_data["region"].id, biome_pois)
        
        # Check POI leyline assignments
        for poi in world_data["pois"]:
            poi_leylines = leyline_manager.get_leylines_for_poi(poi.id)
            if poi_leylines:
                print(f"POI '{poi.generated_name}' is affected by {len(poi_leylines)} leylines:")
                for leyline in poi_leylines:
                    print(f"  - {leyline.name} ({leyline.leyline_type})")
            else:
                print(f"POI '{poi.generated_name}' is not affected by any leylines")
        
        # Get magical properties for each POI
        print("\nMagical properties for each POI:")
        for poi in world_data["pois"]:
            props = leyline_manager.get_magical_properties_for_poi(poi.id)
            print(f"\nPOI: {poi.generated_name} ({poi.poi_type})")
            print(f"  Magical strength: {props['magical_strength']:.2f}")
            print(f"  Stability: {props['stability']}")
            
            # Print major affinities
            affinities = sorted(props['affinities'].items(), key=lambda x: x[1], reverse=True)
            if affinities:
                print("  Major affinities:")
                for element, value in affinities[:3]:  # Show top 3
                    if value > 0.3:
                        print(f"    - {element}: {value:.2f}")
            
            # Print phenomena
            if props['magical_phenomena']:
                print("  Magical phenomena:")
                for phenomenon in props['magical_phenomena']:
                    print(f"    - {phenomenon}")
        
        return leyline_manager
    
    except Exception as e:
        print(f"❌ Error testing leylines: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_spell_location_effects(world_data, leyline_manager):
    """Test how different locations affect spell properties."""
    print_section("Testing Spell Location Effects")
    
    try:
        # Create spell crafting system
        spell_system = SpellCraftingSystem(leyline_manager)
        
        # Test spells at different locations
        test_spells = ["fireball", "ice_spike", "stone_skin", "light", "teleport"]
        
        # Select a few POIs to test
        test_pois = [
            world_data["pois"][0],  # Forest village
            world_data["pois"][1],  # Forest shrine
            world_data["pois"][4],  # Crystal tower
            world_data["pois"][6]   # Marsh shrine
        ]
        
        for poi in test_pois:
            print(f"\nTesting spells at {poi.generated_name} ({poi.poi_type}):")
            
            # Get magical properties
            props = leyline_manager.get_magical_properties_for_poi(poi.id)
            print(f"Location magical strength: {props['magical_strength']:.2f}")
            print(f"Location stability: {props['stability']}")
            
            # Top affinities
            affinities = sorted(props['affinities'].items(), key=lambda x: x[1], reverse=True)
            if affinities:
                print("Top affinities:")
                for element, value in affinities[:2]:
                    print(f"  - {element}: {value:.2f}")
            
            # Test each spell
            for spell_id in test_spells:
                # Create the spell at this location
                spell = spell_system.create_spell_from_template(
                    template_id=spell_id,
                    location_id=poi.id
                )
                
                if not spell:
                    print(f"  Could not create spell {spell_id}")
                    continue
                
                # Print spell information
                print(f"\n  Spell: {spell.get_display_name()} ({spell.template.purpose})")
                
                # Show modifications
                if spell.modifications:
                    print("  Modifications:")
                    for mod_name, mod_value in spell.modifications.items():
                        if mod_name == 'added_elements':
                            print(f"    - Added elements: {', '.join([e.value for e in mod_value])}")
                        else:
                            print(f"    - {mod_name}: {mod_value}")
                
                # Show actual properties
                print("  Properties:")
                print(f"    - Power: {spell.actual_power:.1f}")
                print(f"    - Duration: {spell.actual_duration}")
                print(f"    - Range: {spell.actual_range}")
                print(f"    - Area: {spell.actual_area}")
                print(f"    - Mana cost: {spell.actual_mana_cost}")
                print(f"    - Focus required: {spell.actual_focus_required}")
                print(f"    - Casting time: {spell.actual_casting_time:.1f}s")
                
                # Generate a narrative for a successful casting
                narrative = spell_system.generate_spell_outcome_narrative(
                    spell=spell,
                    caster_name="Archmage Thalidor",
                    target_name="the target" if spell.template.purpose == SpellPurpose.ATTACK else None,
                    location_name=poi.generated_name,
                    success_level=0.8  # Good success
                )
                
                print(f"\n  Narrative: {narrative}")
        
        return spell_system
    
    except Exception as e:
        print(f"❌ Error testing spell location effects: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_magical_materials(world_data, leyline_manager):
    """Test the generation and distribution of magical materials."""
    print_section("Testing Magical Materials")
    
    try:
        # Create magical materials manager
        materials_manager = MagicalMaterialsManager(leyline_manager)
        
        # Test material generation for each POI
        for poi in world_data["pois"]:
            # Get the biome type
            biome = next((b for b in world_data["biomes"] if b.id == poi.biome_id), None)
            if not biome:
                continue
            
            biome_type = BiomeType(biome.biome_type)
            poi_type = POIType(poi.poi_type)
            
            print(f"\nGenerating materials for {poi.generated_name} ({poi_type.value}):")
            
            # Generate materials with different search efforts and skills
            effort_levels = [0.3, 0.7, 1.0]  # Low, medium, high effort
            skill_levels = [0.3, 0.7, 0.9]   # Low, medium, high skill
            
            for effort in effort_levels:
                for skill in skill_levels:
                    # Only test a selection of combinations to keep output manageable
                    if (effort == 0.3 and skill == 0.7) or (effort == 0.7 and skill == 0.3):
                        continue
                    
                    # Generate materials
                    materials = materials_manager.generate_materials_for_location(
                        location_id=poi.id,
                        biome_type=biome_type,
                        poi_type=poi_type,
                        search_effort=effort,
                        searcher_skill=skill
                    )
                    
                    print(f"\n  With effort {effort:.1f} and skill {skill:.1f}:")
                    print(f"  Found {len(materials)} materials:")
                    
                    for i, material_instance in enumerate(materials, 1):
                        material = material_instance.material
                        print(f"    {i}. {material_instance}")
                        print(f"       Type: {material.material_type.value}, Rarity: {material.rarity.value}")
                        print(f"       Elements: {material.primary_element} + {', '.join(material.secondary_elements)}")
                        
                        # Print special traits if any
                        if material_instance.special_traits:
                            print(f"       Special traits: {', '.join(material_instance.special_traits)}")
                        
                        # Print value
                        print(f"       Value: {material_instance.get_value()} gold")
                    
                    # If more than 2 materials found, test compatibility
                    if len(materials) >= 2:
                        # Get the first two materials
                        mat1 = materials[0]
                        mat2 = materials[1]
                        
                        # Test compatibility
                        compatibility, description = materials_manager.get_crafting_compatibility(
                            material1_id=mat1.material.id,
                            material2_id=mat2.material.id
                        )
                        
                        print(f"\n  Compatibility between {mat1.material.name} and {mat2.material.name}:")
                        print(f"  Score: {compatibility:.2f}")
                        print(f"  Description: {description}")
                        
                        # Test enchantment options if compatible
                        if compatibility > 0.4:
                            enchantment_options = materials_manager.generate_enchantment_options(
                                material_instance_ids=[mat1.id, mat2.id],
                                enchantment_purpose="weapon"
                            )
                            
                            if enchantment_options:
                                print("\n  Possible enchantment options:")
                                for i, option in enumerate(enchantment_options, 1):
                                    print(f"    {i}. {option['name']}")
                                    print(f"       {option['description']}")
                                    print(f"       Effects: {', '.join([e['effect'] for e in option['effects']])}")
                                    print(f"       Difficulty: {option['difficulty']}/10")
                                    print(f"       Success chance: {option['success_chance']:.0f}%")
                            else:
                                print("\n  No viable enchantment options found.")
        
        return materials_manager
    
    except Exception as e:
        print(f"❌ Error testing magical materials: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_location_enhancement(world_data, leyline_manager):
    """Test how the magic system enhances location details."""
    print_section("Testing Location Enhancement")
    
    try:
        # Generate enhanced details for each POI
        for poi in world_data["pois"]:
            print(f"\nEnhanced details for {poi.generated_name} ({poi.poi_type}):")
            
            # Get magical details
            magical_details = leyline_manager.modify_poi_based_on_leylines(poi)
            
            # Print magical strength and stability
            print(f"  Magical strength: {magical_details['magical_strength']:.2f}")
            print(f"  Magical stability: {magical_details['magical_stability']}")
            
            # Print major affinities
            if magical_details['major_affinities']:
                print("  Major affinities:")
                for affinity in magical_details['major_affinities']:
                    print(f"    - {affinity}")
            
            # Print magical phenomena
            if magical_details['magical_phenomena']:
                print("  Magical phenomena:")
                for phenomenon in magical_details['magical_phenomena']:
                    print(f"    - {phenomenon}")
            
            # Print magical resources
            if magical_details['magical_resources']:
                print("  Magical resources:")
                for resource in magical_details['magical_resources']:
                    print(f"    - {resource['name']} ({resource['rarity']})")
                    print(f"      Quantity: {resource['quantity']}, Quality: {resource['quality']}")
                    print(f"      Use: {resource['use']}")
            
            # Print magical hazards
            if magical_details['magical_hazards']:
                print("  Magical hazards:")
                for hazard in magical_details['magical_hazards']:
                    print(f"    - {hazard['name']} ({hazard['severity']})")
                    print(f"      Effect: {hazard['effect']}")
                    print(f"      Frequency: {hazard['frequency']}, Detectability: {hazard['detectability']}")
        
        return True
    
    except Exception as e:
        print(f"❌ Error testing location enhancement: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main test function."""
    print_section("Magic System and World Generator Integration Test")
    
    # Setup imports
    if not setup_imports():
        print("❌ Failed to import required modules")
        return
    
    # Create test world
    world_data = create_test_world()
    if not world_data:
        print("❌ Failed to create test world")
        return
    
    # Test leyline generation
    leyline_manager = test_leyline_generation(world_data)
    if not leyline_manager:
        print("❌ Failed to test leylines")
        return
    
    # Test spell location effects
    spell_system = test_spell_location_effects(world_data, leyline_manager)
    if not spell_system:
        print("❌ Failed to test spell location effects")
        return
    
    # Test magical materials
    materials_manager = test_magical_materials(world_data, leyline_manager)
    if not materials_manager:
        print("❌ Failed to test magical materials")
        return
    
    # Test location enhancement
    location_enhancement = test_location_enhancement(world_data, leyline_manager)
    if not location_enhancement:
        print("❌ Failed to test location enhancement")
        return
    
    print_section("Integration Test Complete")
    print("✓ Magic system and world generator integration test completed successfully")

if __name__ == "__main__":
    main()