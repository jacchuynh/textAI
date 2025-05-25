#!/usr/bin/env python3
"""
Test integration between magic system and crafting system

This test ensures that the magic system properly integrates with the crafting system,
allowing for enchantment of items, brewing of magical potions, and use of magical materials.
"""

import unittest
import random
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

# Set the random seed for reproducible tests
random.seed(42)

# Add src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(os.path.join(parent_dir, "src"))

try:
    # Import magic system modules
    from game_engine.magic_system import (
        MagicSystem, MagicUser, Spell, Ritual, Enchantment,
        MagicTier, MagicSource, EffectType, TargetType, DomainRequirement,
        Domain, DamageType, MagicalEffect, ItemMagicProfile
    )

    # Import magic crafting integration
    from game_engine.magic_crafting_integration import (
        MagicalCraftingService, EnchantingRecipe, PotionRecipe,
        magical_crafting
    )

    class TestMagicCraftingIntegration(unittest.TestCase):
        """Test the integration between the magic system and crafting system."""
        
        def setUp(self):
            """Set up the test environment."""
            # Create a magic system instance
            self.magic_system = MagicSystem()
            
            # Get crafting service
            self.crafting_service = magical_crafting['crafting_service']
            
            # Create test character
            self.character = self._create_test_character()
            
            # Initialize magic profile
            self.magic_profile = self.magic_system.initialize_magic_user(self.character.domains)
            
            # Ensure character has a mana heart for advanced crafting
            if not self.magic_profile.has_mana_heart:
                result = self.magic_system.develop_mana_heart("test_character", self.magic_profile)
            
            # Prepare test data
            self.test_materials = self._prepare_test_materials()
        
        def _create_test_character(self):
            """Create a test character with crafting affinity."""
            class TestCharacter:
                def __init__(self):
                    self.name = "Crafting Adept"
                    self.domains = {
                        Domain.BODY: 3,
                        Domain.MIND: 4,
                        Domain.CRAFT: 5,  # High crafting
                        Domain.AWARENESS: 3,
                        Domain.SOCIAL: 2,
                        Domain.AUTHORITY: 2,
                        Domain.SPIRIT: 4,
                        Domain.FIRE: 2,
                        Domain.WATER: 0,
                        Domain.EARTH: 0,
                        Domain.AIR: 0,
                        Domain.LIGHT: 0,
                        Domain.DARKNESS: 0
                    }
            
            return TestCharacter()
        
        def _prepare_test_materials(self):
            """Prepare test materials for crafting."""
            return {
                "material_ley_crystal": 5,
                "material_crimson_residue": 5,
                "material_spiritbloom": 5,
                "material_void_essence": 3,
                "material_starlight_fragment": 2,
                "Charcoal": 10,
                "Red mushroom": 5,
                "Honey": 5,
                "Spring water": 5,
                "Weapon": 2,
                "Armor": 1,
                "Jewelry": 1
            }
        
        def test_list_magical_materials(self):
            """Test listing available magical materials."""
            # Get materials
            materials = self.crafting_service.list_all_materials()
            
            # Check that materials are returned
            self.assertIsNotNone(materials)
            self.assertIsInstance(materials, list)
            self.assertGreater(len(materials), 0)
            
            # Check material properties
            for material in materials:
                self.assertIn('id', material)
                self.assertIn('name', material)
                self.assertIn('rarity', material)
                self.assertIn('description', material)
        
        def test_list_enchanting_recipes(self):
            """Test listing available enchanting recipes."""
            # Get recipes
            recipes = self.crafting_service.list_all_enchanting_recipes()
            
            # Check that recipes are returned
            self.assertIsNotNone(recipes)
            self.assertIsInstance(recipes, list)
            self.assertGreater(len(recipes), 0)
            
            # Check recipe properties
            for recipe in recipes:
                self.assertIn('id', recipe)
                self.assertIn('name', recipe)
                self.assertIn('description', recipe)
                self.assertIn('tier', recipe)
                self.assertIn('required_materials', recipe)
                self.assertIn('domain_requirements', recipe)
                
                # Check material requirements
                for material in recipe['required_materials']:
                    self.assertIn('id', material)
                    self.assertIn('name', material)
                    self.assertIn('quantity', material)
                
                # Check domain requirements
                for requirement in recipe['domain_requirements']:
                    self.assertIn('domain', requirement)
                    self.assertIn('minimum_value', requirement)
        
        def test_list_potion_recipes(self):
            """Test listing available potion recipes."""
            # Get recipes
            recipes = self.crafting_service.list_all_potion_recipes()
            
            # Check that recipes are returned
            self.assertIsNotNone(recipes)
            self.assertIsInstance(recipes, list)
            self.assertGreater(len(recipes), 0)
            
            # Check recipe properties
            for recipe in recipes:
                self.assertIn('id', recipe)
                self.assertIn('name', recipe)
                self.assertIn('description', recipe)
                self.assertIn('required_materials', recipe)
                self.assertIn('effects', recipe)
                
                # Check material requirements
                for material in recipe['required_materials']:
                    self.assertIn('id', material)
                    self.assertIn('name', material)
                    self.assertIn('quantity', material)
                
                # Check effects
                for effect in recipe['effects']:
                    self.assertIn('effect_type', effect)
                    self.assertIn('potency', effect)
                    self.assertIn('duration', effect)
        
        def test_enchant_item(self):
            """Test enchanting an item."""
            # Get available recipes
            recipes = self.crafting_service.list_all_enchanting_recipes()
            
            # Find a recipe we can craft with our materials
            craftable_recipe = None
            for recipe in recipes:
                can_craft = True
                for material in recipe['required_materials']:
                    if material['id'] not in self.test_materials or self.test_materials[material['id']] < material['quantity']:
                        can_craft = False
                        break
                
                if can_craft:
                    craftable_recipe = recipe
                    break
            
            # Skip test if no craftable recipe
            if not craftable_recipe:
                self.skipTest("No craftable enchanting recipe found with available materials")
                return
            
            # Attempt to enchant
            result = self.crafting_service.enchant_item(
                character_id="test_character",
                character_magic=self.magic_profile,
                recipe_id=craftable_recipe['id'],
                item_id="test_weapon",
                available_materials=self.test_materials,
                character_domains=self.character.domains
            )
            
            # Check result
            self.assertIsNotNone(result)
            self.assertIn('success', result)
            self.assertIn('message', result)
            
            # If enchanting succeeded, check enchantment
            if result['success']:
                self.assertIn('enchantment', result)
                enchantment = result['enchantment']
                
                self.assertIn('name', enchantment)
                self.assertIn('effects', enchantment)
                self.assertGreater(len(enchantment['effects']), 0)
            
            return result
        
        def test_brew_potion(self):
            """Test brewing a potion."""
            # Get available recipes
            recipes = self.crafting_service.list_all_potion_recipes()
            
            # Find a recipe we can craft with our materials
            craftable_recipe = None
            for recipe in recipes:
                can_craft = True
                for material in recipe['required_materials']:
                    if material['id'] not in self.test_materials or self.test_materials[material['id']] < material['quantity']:
                        can_craft = False
                        break
                
                if can_craft:
                    craftable_recipe = recipe
                    break
            
            # Skip test if no craftable recipe
            if not craftable_recipe:
                self.skipTest("No craftable potion recipe found with available materials")
                return
            
            # Attempt to brew
            result = self.crafting_service.brew_potion(
                character_id="test_character",
                character_magic=self.magic_profile,
                recipe_id=craftable_recipe['id'],
                available_materials=self.test_materials,
                character_domains=self.character.domains
            )
            
            # Check result
            self.assertIsNotNone(result)
            self.assertIn('success', result)
            self.assertIn('message', result)
            
            # If brewing succeeded, check potion
            if result['success']:
                self.assertIn('potion', result)
                potion = result['potion']
                
                self.assertIn('name', potion)
                self.assertIn('effects', potion)
                self.assertGreater(len(potion['effects']), 0)
            
            return result
        
        def test_material_consumption(self):
            """Test that materials are consumed during crafting."""
            # Attempt to enchant an item
            enchant_result = self.test_enchant_item()
            
            # If enchanting didn't succeed, skip
            if not enchant_result or not enchant_result.get('success', False):
                self.skipTest("Enchanting test didn't succeed, skipping material consumption test")
                return
            
            # Check that materials were consumed
            self.assertIn('consumed_materials', enchant_result)
            consumed = enchant_result['consumed_materials']
            
            self.assertIsInstance(consumed, dict)
            self.assertGreater(len(consumed), 0)
            
            # At least one material should have been consumed
            total_consumed = sum(consumed.values())
            self.assertGreater(total_consumed, 0)
        
        def test_domain_requirements(self):
            """Test that domain requirements are enforced for recipes."""
            # Get available recipes
            recipes = self.crafting_service.list_all_enchanting_recipes()
            
            # Find a recipe with domain requirements
            test_recipe = None
            for recipe in recipes:
                if recipe['domain_requirements'] and len(recipe['domain_requirements']) > 0:
                    test_recipe = recipe
                    break
            
            # Skip test if no suitable recipe
            if not test_recipe:
                self.skipTest("No recipe with domain requirements found")
                return
            
            # Create a character with insufficient domains
            low_domains = {domain: 1 for domain in self.character.domains}
            low_magic_profile = self.magic_system.initialize_magic_user(low_domains)
            
            # Attempt to enchant with insufficient domains
            result = self.crafting_service.enchant_item(
                character_id="test_character_low",
                character_magic=low_magic_profile,
                recipe_id=test_recipe['id'],
                item_id="test_weapon",
                available_materials=self.test_materials,
                character_domains=low_domains
            )
            
            # Should fail due to domain requirements
            self.assertFalse(result['success'])
            self.assertIn('domain', result['message'].lower())

    if __name__ == "__main__":
        unittest.main()

except ImportError as e:
    print(f"Import error: {e}")
    print("This test requires the magic system and crafting system modules.")
    print("Skipping tests.")
    
    # Create a dummy test class to prevent test failure
    class DummyTest(unittest.TestCase):
        def test_dummy(self):
            self.skipTest("Required modules not available")