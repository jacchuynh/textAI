"""
Magic-Crafting Integration Tests

This module tests the integration between the magic system and the crafting system.
"""

import pytest
import random
from typing import Dict, List, Any

# Import core components when available
try:
    from game_engine.magic_system import (
        MagicSystem, MagicUser, LocationMagicProfile, Domain, 
        DamageType, EffectType, MagicTier, Enchantment, ItemMagicProfile
    )
    from magic_system.magic_crafting_integration import (
        MagicCraftingIntegration, ItemEnchanter, MagicalItemCrafter, MagicalPotionBrewer,
        CraftingMaterial, EnchantmentRecipe, MagicalItemType
    )
    MAGIC_CRAFTING_AVAILABLE = True
except ImportError:
    MAGIC_CRAFTING_AVAILABLE = False

# Set a seed for consistent random results in tests
random.seed(42)


# Skip the entire module if dependencies aren't available
pytestmark = pytest.mark.skipif(
    not MAGIC_CRAFTING_AVAILABLE,
    reason="Magic crafting integration components not available"
)


class TestMagicCraftingIntegration:
    """Tests for the integration between magic and crafting systems."""

    def test_available_enchantment_recipes(self, magic_crafting_integration, test_character_domains):
        """Test that enchantment recipes can be retrieved based on character domains."""
        # Get available enchantment recipes
        recipes = magic_crafting_integration.get_enchantment_recipes(test_character_domains)
        
        # Verify recipes were returned
        assert recipes is not None
        assert len(recipes) > 0
        
        # Check recipe structure
        for recipe in recipes:
            assert "id" in recipe
            assert "name" in recipe
            assert "description" in recipe
            assert "tier" in recipe
            assert "meets_requirements" in recipe
            assert "required_materials" in recipe
            assert "effects" in recipe
    
    def test_available_crafting_recipes(self, magic_crafting_integration, test_character_domains):
        """Test that crafting recipes can be retrieved based on character domains."""
        # Get available crafting recipes
        recipes = magic_crafting_integration.get_crafting_recipes(test_character_domains)
        
        # Verify recipes were returned
        assert recipes is not None
        assert len(recipes) > 0
        
        # Check recipe structure
        for recipe in recipes:
            assert "id" in recipe
            assert "name" in recipe
            assert "description" in recipe
            assert "item_type" in recipe
            assert "meets_requirements" in recipe
            assert "required_materials" in recipe
            assert "crafting_difficulty" in recipe
    
    def test_available_potion_recipes(self, magic_crafting_integration, test_character_domains):
        """Test that potion recipes can be retrieved based on character domains."""
        # Get available potion recipes
        recipes = magic_crafting_integration.get_potion_recipes(test_character_domains)
        
        # Verify recipes were returned
        assert recipes is not None
        assert len(recipes) > 0
        
        # Check recipe structure
        for recipe in recipes:
            assert "id" in recipe
            assert "name" in recipe
            assert "description" in recipe
            assert "meets_requirements" in recipe
            assert "required_materials" in recipe
            assert "brewing_difficulty" in recipe
            assert "effects" in recipe
    
    def test_available_materials(self, magic_crafting_integration):
        """Test that crafting materials can be retrieved."""
        # Get all materials
        materials = magic_crafting_integration.get_all_materials()
        
        # Verify materials were returned
        assert materials is not None
        assert len(materials) > 0
        
        # Check material structure
        for material in materials:
            assert "id" in material
            assert "name" in material
            assert "description" in material
            assert "rarity" in material
            assert "material_type" in material
            assert "magical_properties" in material
            assert "resonance" in material
    
    def test_item_enchantment(self, magic_crafting_integration, magic_user, test_character_domains, 
                              available_materials, location_magic_profile):
        """Test that items can be enchanted."""
        # Define a test item
        item_id = "test_sword"
        item_type = "weapon"
        
        # Find a suitable enchantment recipe for the test character
        recipes = magic_crafting_integration.get_enchantment_recipes(test_character_domains)
        compatible_recipes = [r for r in recipes if r["meets_requirements"] and item_type in r["compatible_item_types"]]
        
        # Skip if no compatible recipes
        if not compatible_recipes:
            pytest.skip("No compatible enchantment recipes for test character")
        
        recipe_id = compatible_recipes[0]["id"]
        
        # Perform the enchantment
        result = magic_crafting_integration.perform_enchantment(
            magic_user,
            test_character_domains,
            item_id,
            item_type,
            recipe_id,
            available_materials,
            location_magic_profile
        )
        
        # Verify the enchantment was successful
        assert result["success"] == True
        assert "enchantment" in result
        assert "item_magic_profile" in result
        
        # Check that materials were consumed
        assert "consumed_materials" in result
        assert len(result["consumed_materials"]) > 0
        
        # Check the enchantment details
        enchantment = result["enchantment"]
        assert "name" in enchantment
        assert "tier" in enchantment
        assert "effects" in enchantment
        
        # Check the item magic profile
        item_profile = result["item_magic_profile"]
        assert item_profile["is_enchanted"] == True
        assert "enchantment_id" in item_profile
        assert enchantment["id"] == item_profile["enchantment_id"]
    
    def test_craft_magical_item(self, magic_crafting_integration, magic_user, test_character_domains, 
                               available_materials, location_magic_profile):
        """Test that magical items can be crafted."""
        # Find a suitable crafting recipe for the test character
        recipes = magic_crafting_integration.get_crafting_recipes(test_character_domains)
        compatible_recipes = [r for r in recipes if r["meets_requirements"]]
        
        # Skip if no compatible recipes
        if not compatible_recipes:
            pytest.skip("No compatible crafting recipes for test character")
        
        recipe_id = compatible_recipes[0]["id"]
        
        # Craft the item
        result = magic_crafting_integration.craft_item(
            magic_user,
            test_character_domains,
            recipe_id,
            available_materials,
            location_magic_profile
        )
        
        # Verify the crafting was successful
        assert result["success"] == True
        assert "crafted_item" in result
        
        # Check that materials were consumed
        assert "consumed_materials" in result
        assert len(result["consumed_materials"]) > 0
        
        # Check the crafted item details
        item = result["crafted_item"]
        assert "id" in item
        assert "name" in item
        assert "description" in item
        assert "type" in item
        assert "magic_profile" in item
        
        # Check the item's magic profile
        magic_profile = item["magic_profile"]
        assert "mana_storage_capacity" in magic_profile
    
    def test_brew_potion(self, magic_crafting_integration, magic_user, test_character_domains, 
                         available_materials, location_magic_profile):
        """Test that potions can be brewed."""
        # Find a suitable potion recipe for the test character
        recipes = magic_crafting_integration.get_potion_recipes(test_character_domains)
        compatible_recipes = [r for r in recipes if r["meets_requirements"]]
        
        # Skip if no compatible recipes
        if not compatible_recipes:
            pytest.skip("No compatible potion recipes for test character")
        
        recipe_id = compatible_recipes[0]["id"]
        
        # Brew the potion
        result = magic_crafting_integration.brew_potion(
            magic_user,
            test_character_domains,
            recipe_id,
            available_materials,
            location_magic_profile
        )
        
        # Verify the brewing was successful
        assert result["success"] == True
        assert "potion" in result
        
        # Check that materials were consumed
        assert "consumed_materials" in result
        assert len(result["consumed_materials"]) > 0
        
        # Check the potion details
        potion = result["potion"]
        assert "id" in potion
        assert "name" in potion
        assert "description" in potion
        assert "type" in potion
        assert "effects" in potion
        
        # Check the potion effects
        effects = potion["effects"]
        assert len(effects) > 0
        for effect in effects:
            assert "type" in effect
            assert "potency" in effect
    
    def test_location_crafting_bonus(self, magic_crafting_integration, magic_user, test_character_domains, 
                                     available_materials, location_magic_profile):
        """Test that location magic profiles provide bonuses to crafting success."""
        # Find a suitable crafting recipe for the test character
        recipes = magic_crafting_integration.get_crafting_recipes(test_character_domains)
        compatible_recipes = [r for r in recipes if r["meets_requirements"]]
        
        # Skip if no compatible recipes
        if not compatible_recipes:
            pytest.skip("No compatible crafting recipes for test character")
        
        recipe_id = compatible_recipes[0]["id"]
        
        # Set seed to ensure consistent results
        random.seed(42)
        
        # Craft the item with location bonus
        result_with_bonus = magic_crafting_integration.craft_item(
            magic_user,
            test_character_domains,
            recipe_id,
            available_materials,
            location_magic_profile
        )
        
        # Reset seed to ensure consistent results
        random.seed(42)
        
        # Craft the item without location bonus
        result_without_bonus = magic_crafting_integration.craft_item(
            magic_user,
            test_character_domains,
            recipe_id,
            available_materials,
            None
        )
        
        # Both should succeed due to fixed random seed
        assert result_with_bonus["success"] == True
        assert result_without_bonus["success"] == True
        
        # But the success chance should be higher with the location bonus
        assert result_with_bonus["success_chance"] > result_without_bonus["success_chance"]
    
    def test_material_resonance(self, magic_crafting_integration):
        """Test that materials have appropriate magical resonance."""
        # Get all materials
        materials = magic_crafting_integration.get_all_materials()
        
        # Check that specific materials have the expected resonance
        fire_materials = [m for m in materials if m["id"] in ["fire_essence", "dragon_scale"]]
        for material in fire_materials:
            assert "FIRE" in material["resonance"]
        
        arcane_materials = [m for m in materials if m["id"] in ["arcane_dust", "mana_crystal"]]
        for material in arcane_materials:
            assert "ARCANE" in material["resonance"]
        
        # Materials with multiple resonances
        multi_resonance = [m for m in materials if len(m["resonance"]) > 1]
        assert len(multi_resonance) > 0
    
    def test_enchantment_effect_description(self, magic_crafting_integration):
        """Test that enchantment effects have proper descriptions."""
        # Get available enchantment recipes
        enchanter = magic_crafting_integration.enchanter
        recipes = enchanter.enchantment_recipes
        
        # Check that effect descriptions make sense for their purpose
        for recipe_id, recipe in recipes.items():
            assert len(recipe.effects) > 0
            
            for effect in recipe.effects:
                # Effect descriptions should be non-empty strings
                assert isinstance(effect, str)
                assert len(effect) > 0
                
                # Check for common effect patterns
                if "damage" in effect.lower():
                    assert any(term in effect.lower() for term in ["add", "deal", "increase"])
                
                if "resist" in effect.lower():
                    assert any(term in effect.lower() for term in ["reduce", "protect", "against"])


# Simple dummy test to ensure pytest discovers the module
class DummyTest:
    def test_dummy(self):
        assert True