"""
Magic Crafting Integration Module

This module integrates the magic system with the crafting system,
allowing for the creation of magical items, enchantments, and
imbuing items with magical properties.
"""

import random
from typing import Dict, List, Any, Optional, Tuple, Union
from enum import Enum, auto
from datetime import datetime, timedelta

# Import magic system components
from game_engine.magic_system import (
    MagicSystem,
    MagicUser,
    Enchantment,
    ItemMagicProfile,
    MagicTier,
    DamageType,
    Domain,
    LocationMagicProfile
)

class CraftingMaterial:
    """A material that can be used in crafting."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        rarity: str,
        material_type: str,
        magical_properties: List[str] = None,
        resonance: List[DamageType] = None,
        value: int = 0,
        source_locations: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.rarity = rarity
        self.material_type = material_type
        self.magical_properties = magical_properties or []
        self.resonance = resonance or []
        self.value = value
        self.source_locations = source_locations or []
    
    def __str__(self) -> str:
        return f"{self.name} ({self.rarity} {self.material_type})"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the material to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "material_type": self.material_type,
            "magical_properties": self.magical_properties,
            "resonance": [r.name for r in self.resonance] if self.resonance else [],
            "value": self.value,
            "source_locations": self.source_locations
        }

class EnchantmentRecipe:
    """A recipe for creating an enchantment."""
    
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        required_materials: Dict[str, int],
        required_domain_values: Dict[Domain, int],
        enchanting_difficulty: int,
        effects: List[str],
        enchantment_duration: Optional[int] = None,  # in days, None for permanent
        enchantment_charges: Optional[int] = None,  # None for unlimited
        compatible_item_types: List[str] = None,
        incompatible_enchantments: List[str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.required_materials = required_materials
        self.required_domain_values = required_domain_values
        self.enchanting_difficulty = enchanting_difficulty
        self.effects = effects
        self.enchantment_duration = enchantment_duration
        self.enchantment_charges = enchantment_charges
        self.compatible_item_types = compatible_item_types or []
        self.incompatible_enchantments = incompatible_enchantments or []
    
    def __str__(self) -> str:
        return f"{self.name} ({self.tier.name} enchantment)"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the recipe to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.name,
            "required_materials": self.required_materials,
            "required_domain_values": {d.name: v for d, v in self.required_domain_values.items()},
            "enchanting_difficulty": self.enchanting_difficulty,
            "effects": self.effects,
            "enchantment_duration": self.enchantment_duration,
            "enchantment_charges": self.enchantment_charges,
            "compatible_item_types": self.compatible_item_types,
            "incompatible_enchantments": self.incompatible_enchantments
        }

class MagicalItemType(Enum):
    """Types of magical items that can be crafted."""
    WAND = auto()
    STAFF = auto()
    AMULET = auto()
    RING = auto()
    ROBE = auto()
    CRYSTAL = auto()
    TOME = auto()
    POTION = auto()
    SCROLL = auto()
    RUNE = auto()
    TALISMAN = auto()
    WEAPON = auto()
    ARMOR = auto()

class ItemEnchanter:
    """Manages the enchantment of items."""
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the item enchanter.
        
        Args:
            magic_system: The magic system
        """
        self.magic_system = magic_system
        self.enchantment_recipes = self._get_mock_enchantment_recipes()
        self.materials = self._get_mock_materials()
    
    def _get_mock_enchantment_recipes(self) -> Dict[str, EnchantmentRecipe]:
        """Get mock enchantment recipes for demonstration."""
        recipes = {}
        
        # Basic fire enchantment
        fire_weapon = EnchantmentRecipe(
            id="enchant_recipe_fire_weapon",
            name="Flaming Weapon",
            description="Enchants a weapon to deal additional fire damage.",
            tier=MagicTier.ADEPT,
            required_materials={
                "fire_essence": 2,
                "resonant_crystal": 1,
                "dragon_scale": 1
            },
            required_domain_values={
                Domain.FIRE: 3,
                Domain.CRAFT: 2
            },
            enchanting_difficulty=40,
            effects=[
                "Adds 5 fire damage to attacks",
                "Weapon emits light equivalent to a torch",
                "Weapon ignites flammable materials on contact"
            ],
            enchantment_duration=7,  # 7 days
            enchantment_charges=None,  # Unlimited uses while active
            compatible_item_types=["weapon", "staff", "wand"]
        )
        recipes[fire_weapon.id] = fire_weapon
        
        # Basic protection enchantment
        protection_armor = EnchantmentRecipe(
            id="enchant_recipe_protection_armor",
            name="Arcane Protection",
            description="Enchants armor to provide protection against magical damage.",
            tier=MagicTier.ADEPT,
            required_materials={
                "arcane_dust": 3,
                "moonstone": 1,
                "ethereal_silk": 2
            },
            required_domain_values={
                Domain.CRAFT: 3,
                Domain.MIND: 2
            },
            enchanting_difficulty=45,
            effects=[
                "Reduces magical damage by 10%",
                "Grants advantage on saving throws against magical effects",
                "Emits a faint blue glow when magic is nearby"
            ],
            enchantment_duration=14,  # 14 days
            enchantment_charges=None,  # Unlimited uses while active
            compatible_item_types=["armor", "robe", "amulet"]
        )
        recipes[protection_armor.id] = protection_armor
        
        # Mana storage enchantment
        mana_storage = EnchantmentRecipe(
            id="enchant_recipe_mana_storage",
            name="Mana Reservoir",
            description="Enchants an item to store mana for later use.",
            tier=MagicTier.EXPERT,
            required_materials={
                "mana_crystal": 3,
                "arcane_dust": 2,
                "celestial_prism": 1
            },
            required_domain_values={
                Domain.MIND: 3,
                Domain.CRAFT: 3,
                Domain.SPIRIT: 2
            },
            enchanting_difficulty=60,
            effects=[
                "Stores up to 50 mana",
                "Can be drawn from to cast spells",
                "Glows with intensity proportional to stored mana"
            ],
            enchantment_duration=None,  # Permanent
            enchantment_charges=None,  # Unlimited uses
            compatible_item_types=["crystal", "staff", "wand", "ring", "amulet"]
        )
        recipes[mana_storage.id] = mana_storage
        
        return recipes
    
    def _get_mock_materials(self) -> Dict[str, CraftingMaterial]:
        """Get mock crafting materials for demonstration."""
        materials = {}
        
        # Fire essence
        fire_essence = CraftingMaterial(
            id="fire_essence",
            name="Fire Essence",
            description="A volatile substance that embodies the element of fire.",
            rarity="uncommon",
            material_type="essence",
            magical_properties=["Volatile", "Ignites at high concentrations", "Radiates heat"],
            resonance=[DamageType.FIRE],
            value=75,
            source_locations=["volcano", "fire_plane", "dragon_lair"]
        )
        materials[fire_essence.id] = fire_essence
        
        # Resonant crystal
        resonant_crystal = CraftingMaterial(
            id="resonant_crystal",
            name="Resonant Crystal",
            description="A crystal that resonates with magical energy, amplifying spells.",
            rarity="uncommon",
            material_type="crystal",
            magical_properties=["Amplifies magic", "Resonates with magical frequencies", "Stores energy"],
            resonance=[DamageType.ARCANE],
            value=60,
            source_locations=["crystal_cave", "magic_node", "ancient_ruins"]
        )
        materials[resonant_crystal.id] = resonant_crystal
        
        # Dragon scale
        dragon_scale = CraftingMaterial(
            id="dragon_scale",
            name="Dragon Scale",
            description="A scale from a dragon, highly resistant to fire and magic.",
            rarity="rare",
            material_type="monster_part",
            magical_properties=["Fire resistant", "Magic resistant", "Durable"],
            resonance=[DamageType.FIRE, DamageType.ARCANE],
            value=200,
            source_locations=["dragon_lair", "monster_hunter", "ancient_battlefield"]
        )
        materials[dragon_scale.id] = dragon_scale
        
        # Arcane dust
        arcane_dust = CraftingMaterial(
            id="arcane_dust",
            name="Arcane Dust",
            description="Fine dust that contains pure magical energy.",
            rarity="common",
            material_type="reagent",
            magical_properties=["Magical catalyst", "Dissolves in liquid", "Glows in darkness"],
            resonance=[DamageType.ARCANE],
            value=30,
            source_locations=["wizard_tower", "magic_node", "enchanted_forest"]
        )
        materials[arcane_dust.id] = arcane_dust
        
        # Moonstone
        moonstone = CraftingMaterial(
            id="moonstone",
            name="Moonstone",
            description="A stone that absorbs and channels lunar energy.",
            rarity="uncommon",
            material_type="gem",
            magical_properties=["Lunar resonance", "Light manipulation", "Enhances illusion magic"],
            resonance=[DamageType.ARCANE, DamageType.LIGHT],
            value=85,
            source_locations=["mountain_peak", "ancient_shrine", "lunar_temple"]
        )
        materials[moonstone.id] = moonstone
        
        # Ethereal silk
        ethereal_silk = CraftingMaterial(
            id="ethereal_silk",
            name="Ethereal Silk",
            description="Silk woven from the strands of extraplanar beings.",
            rarity="rare",
            material_type="fabric",
            magical_properties=["Lightweight", "Disrupts magical effects", "Semi-translucent"],
            resonance=[DamageType.ARCANE, DamageType.LIGHT],
            value=150,
            source_locations=["planar_rift", "spirit_realm", "ancient_temple"]
        )
        materials[ethereal_silk.id] = ethereal_silk
        
        # Mana crystal
        mana_crystal = CraftingMaterial(
            id="mana_crystal",
            name="Mana Crystal",
            description="A crystal that naturally stores magical energy.",
            rarity="uncommon",
            material_type="crystal",
            magical_properties=["Stores mana", "Conducts magical energy", "Self-recharging"],
            resonance=[DamageType.ARCANE],
            value=100,
            source_locations=["leyline_nexus", "crystal_cave", "wizard_tower"]
        )
        materials[mana_crystal.id] = mana_crystal
        
        # Celestial prism
        celestial_prism = CraftingMaterial(
            id="celestial_prism",
            name="Celestial Prism",
            description="A prism that refracts light from other planes of existence.",
            rarity="rare",
            material_type="gem",
            magical_properties=["Refracts planar energy", "Enhances scrying", "Splits magical energy"],
            resonance=[DamageType.ARCANE, DamageType.LIGHT],
            value=225,
            source_locations=["celestial_plane", "ancient_observatory", "wizard_sanctum"]
        )
        materials[celestial_prism.id] = celestial_prism
        
        return materials
    
    def get_enchantment_recipe_by_id(self, recipe_id: str) -> Optional[EnchantmentRecipe]:
        """
        Get an enchantment recipe by its ID.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            The recipe or None if not found
        """
        return self.enchantment_recipes.get(recipe_id)
    
    def get_material_by_id(self, material_id: str) -> Optional[CraftingMaterial]:
        """
        Get a crafting material by its ID.
        
        Args:
            material_id: The material ID
            
        Returns:
            The material or None if not found
        """
        return self.materials.get(material_id)
    
    def get_available_enchantment_recipes(self, character_domains: Dict[Domain, int]) -> List[Dict[str, Any]]:
        """
        Get available enchantment recipes based on character domains.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            List of available recipe information
        """
        available_recipes = []
        
        for recipe_id, recipe in self.enchantment_recipes.items():
            # Check if the character meets the domain requirements
            meets_requirements = True
            for domain, required_value in recipe.required_domain_values.items():
                if domain not in character_domains or character_domains[domain] < required_value:
                    meets_requirements = False
                    break
            
            available_recipes.append({
                "id": recipe_id,
                "name": recipe.name,
                "description": recipe.description,
                "tier": recipe.tier.name,
                "meets_requirements": meets_requirements,
                "required_materials": recipe.required_materials,
                "effects": recipe.effects,
                "compatible_item_types": recipe.compatible_item_types
            })
        
        return available_recipes
    
    def enchant_item(
        self,
        enchanter: MagicUser,
        enchanter_domains: Dict[Domain, int],
        item_id: str,
        item_type: str,
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Enchant an item using a recipe.
        
        Args:
            enchanter: The magic user performing the enchantment
            enchanter_domains: The enchanter's domain values
            item_id: The ID of the item to enchant
            item_type: The type of the item
            recipe_id: The ID of the enchantment recipe
            available_materials: Dict mapping material IDs to quantities
            location_magic: Optional magic profile of the location
            
        Returns:
            Dict with result information
        """
        # Get the recipe
        recipe = self.get_enchantment_recipe_by_id(recipe_id)
        if not recipe:
            return {
                "success": False,
                "message": f"Enchantment recipe {recipe_id} not found"
            }
        
        # Check domain requirements
        for domain, required_value in recipe.required_domain_values.items():
            if domain not in enchanter_domains or enchanter_domains[domain] < required_value:
                return {
                    "success": False,
                    "message": f"Domain requirement not met: {domain.name} {required_value}+"
                }
        
        # Check if the item type is compatible
        if recipe.compatible_item_types and item_type not in recipe.compatible_item_types:
            return {
                "success": False,
                "message": f"Item type {item_type} is not compatible with this enchantment"
            }
        
        # Check material requirements
        for material_id, required_quantity in recipe.required_materials.items():
            if material_id not in available_materials or available_materials[material_id] < required_quantity:
                return {
                    "success": False,
                    "message": f"Not enough {material_id}: {available_materials.get(material_id, 0)}/{required_quantity}"
                }
        
        # Calculate enchanting success chance
        base_chance = 100 - recipe.enchanting_difficulty
        
        # Bonus from enchanter's skill
        skill_bonus = enchanter.enchanting_skill / 2
        
        # Bonus from location magic
        location_bonus = 0
        if location_magic and location_magic.allows_ritual_sites:
            location_bonus = 10
        
        success_chance = min(95, base_chance + skill_bonus + location_bonus)
        
        # Roll for success
        roll = random.randint(1, 100)
        
        if roll > success_chance:
            # Enchantment failed
            
            # Consume some materials
            consumed_materials = {}
            for material_id, required_quantity in recipe.required_materials.items():
                # Consume half the materials on failure
                consumed_quantity = max(1, required_quantity // 2)
                consumed_materials[material_id] = consumed_quantity
            
            return {
                "success": False,
                "message": "The enchantment failed",
                "roll": roll,
                "success_chance": success_chance,
                "consumed_materials": consumed_materials
            }
        
        # Enchantment succeeded
        
        # Consume all required materials
        consumed_materials = {}
        for material_id, required_quantity in recipe.required_materials.items():
            consumed_materials[material_id] = required_quantity
        
        # Create the enchantment
        enchantment = Enchantment(
            id=f"{recipe.id}_{item_id}_{int(datetime.now().timestamp())}",
            name=recipe.name,
            description=recipe.description,
            tier=recipe.tier,
            effects=recipe.effects,
            duration=recipe.enchantment_duration,
            charges=recipe.enchantment_charges,
            keywords=[material.name for material_id, _ in consumed_materials.items() if (material := self.get_material_by_id(material_id))]
        )
        
        # Create a magic profile for the item
        item_magic_profile = ItemMagicProfile(
            item_id=item_id,
            is_enchanted=True,
            enchantment_id=enchantment.id,
            enchantment=enchantment,
            material_properties=[material.name for material_id, _ in consumed_materials.items() if (material := self.get_material_by_id(material_id))]
        )
        
        return {
            "success": True,
            "message": f"Successfully enchanted {item_id} with {recipe.name}",
            "roll": roll,
            "success_chance": success_chance,
            "consumed_materials": consumed_materials,
            "enchantment": enchantment.get_details(),
            "item_magic_profile": item_magic_profile.get_details()
        }

class MagicalItemCrafter:
    """Manages the crafting of magical items."""
    
    def __init__(self, magic_system: MagicSystem, enchanter: ItemEnchanter):
        """
        Initialize the magical item crafter.
        
        Args:
            magic_system: The magic system
            enchanter: The item enchanter
        """
        self.magic_system = magic_system
        self.enchanter = enchanter
        self.crafting_recipes = self._get_mock_crafting_recipes()
    
    def _get_mock_crafting_recipes(self) -> Dict[str, Dict[str, Any]]:
        """Get mock crafting recipes for demonstration."""
        recipes = {}
        
        # Basic wand
        wand_recipe = {
            "id": "craft_wand_basic",
            "name": "Basic Wand",
            "description": "A simple wand that can channel magical energy.",
            "item_type": MagicalItemType.WAND.name,
            "required_materials": {
                "resonant_crystal": 1,
                "arcane_dust": 2,
                "wooden_shaft": 1
            },
            "required_domain_values": {
                Domain.CRAFT.name: 2,
                Domain.MIND.name: 1
            },
            "crafting_difficulty": 30,
            "crafting_time": 60,  # minutes
            "result_properties": {
                "mana_storage_capacity": 20,
                "attunement_required": False,
                "base_enchantability": 50
            }
        }
        recipes[wand_recipe["id"]] = wand_recipe
        
        # Basic staff
        staff_recipe = {
            "id": "craft_staff_basic",
            "name": "Basic Staff",
            "description": "A simple staff that can channel larger amounts of magical energy.",
            "item_type": MagicalItemType.STAFF.name,
            "required_materials": {
                "resonant_crystal": 2,
                "arcane_dust": 3,
                "wooden_shaft": 2,
                "leather_binding": 1
            },
            "required_domain_values": {
                Domain.CRAFT.name: 3,
                Domain.MIND.name: 2
            },
            "crafting_difficulty": 40,
            "crafting_time": 120,  # minutes
            "result_properties": {
                "mana_storage_capacity": 50,
                "attunement_required": True,
                "base_enchantability": 70
            }
        }
        recipes[staff_recipe["id"]] = staff_recipe
        
        # Mana crystal
        mana_crystal_recipe = {
            "id": "craft_crystal_mana",
            "name": "Mana Crystal",
            "description": "A crystal specifically designed to store magical energy.",
            "item_type": MagicalItemType.CRYSTAL.name,
            "required_materials": {
                "mana_crystal": 2,
                "arcane_dust": 1,
                "resonant_crystal": 1
            },
            "required_domain_values": {
                Domain.CRAFT.name: 2,
                Domain.MIND.name: 2
            },
            "crafting_difficulty": 35,
            "crafting_time": 90,  # minutes
            "result_properties": {
                "mana_storage_capacity": 100,
                "attunement_required": False,
                "base_enchantability": 60
            }
        }
        recipes[mana_crystal_recipe["id"]] = mana_crystal_recipe
        
        return recipes
    
    def get_crafting_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a crafting recipe by its ID.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            The recipe or None if not found
        """
        return self.crafting_recipes.get(recipe_id)
    
    def get_available_crafting_recipes(self, character_domains: Dict[Domain, int]) -> List[Dict[str, Any]]:
        """
        Get available crafting recipes based on character domains.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            List of available recipe information
        """
        available_recipes = []
        
        for recipe_id, recipe in self.crafting_recipes.items():
            # Check if the character meets the domain requirements
            meets_requirements = True
            for domain_name, required_value in recipe["required_domain_values"].items():
                domain = Domain[domain_name]
                if domain not in character_domains or character_domains[domain] < required_value:
                    meets_requirements = False
                    break
            
            available_recipes.append({
                "id": recipe_id,
                "name": recipe["name"],
                "description": recipe["description"],
                "item_type": recipe["item_type"],
                "meets_requirements": meets_requirements,
                "required_materials": recipe["required_materials"],
                "crafting_difficulty": recipe["crafting_difficulty"],
                "crafting_time": recipe["crafting_time"]
            })
        
        return available_recipes
    
    def craft_magical_item(
        self,
        crafter: MagicUser,
        crafter_domains: Dict[Domain, int],
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Craft a magical item using a recipe.
        
        Args:
            crafter: The magic user performing the crafting
            crafter_domains: The crafter's domain values
            recipe_id: The ID of the crafting recipe
            available_materials: Dict mapping material IDs to quantities
            location_magic: Optional magic profile of the location
            
        Returns:
            Dict with result information
        """
        # Get the recipe
        recipe = self.get_crafting_recipe_by_id(recipe_id)
        if not recipe:
            return {
                "success": False,
                "message": f"Crafting recipe {recipe_id} not found"
            }
        
        # Check domain requirements
        for domain_name, required_value in recipe["required_domain_values"].items():
            domain = Domain[domain_name]
            if domain not in crafter_domains or crafter_domains[domain] < required_value:
                return {
                    "success": False,
                    "message": f"Domain requirement not met: {domain.name} {required_value}+"
                }
        
        # Check material requirements
        for material_id, required_quantity in recipe["required_materials"].items():
            if material_id not in available_materials or available_materials[material_id] < required_quantity:
                return {
                    "success": False,
                    "message": f"Not enough {material_id}: {available_materials.get(material_id, 0)}/{required_quantity}"
                }
        
        # Calculate crafting success chance
        base_chance = 100 - recipe["crafting_difficulty"]
        
        # Bonus from crafter's domains
        craft_bonus = crafter_domains.get(Domain.CRAFT, 0) * 5
        
        # Bonus from location magic
        location_bonus = 0
        if location_magic:
            location_bonus = int(location_magic.leyline_strength * 5)
        
        success_chance = min(95, base_chance + craft_bonus + location_bonus)
        
        # Roll for success
        roll = random.randint(1, 100)
        
        if roll > success_chance:
            # Crafting failed
            
            # Consume some materials
            consumed_materials = {}
            for material_id, required_quantity in recipe["required_materials"].items():
                # Consume half the materials on failure
                consumed_quantity = max(1, required_quantity // 2)
                consumed_materials[material_id] = consumed_quantity
            
            return {
                "success": False,
                "message": "The crafting attempt failed",
                "roll": roll,
                "success_chance": success_chance,
                "consumed_materials": consumed_materials
            }
        
        # Crafting succeeded
        
        # Consume all required materials
        consumed_materials = {}
        for material_id, required_quantity in recipe["required_materials"].items():
            consumed_materials[material_id] = required_quantity
        
        # Generate item ID
        item_id = f"{recipe['item_type'].lower()}_{int(datetime.now().timestamp())}"
        
        # Create magic profile for the item
        item_magic_profile = ItemMagicProfile(
            item_id=item_id,
            is_enchanted=False,
            mana_storage_capacity=recipe["result_properties"]["mana_storage_capacity"],
            current_mana_stored=0,
            attunement_required=recipe["result_properties"]["attunement_required"],
            material_properties=[material_id for material_id in consumed_materials.keys()]
        )
        
        # Create the crafted item
        crafted_item = {
            "id": item_id,
            "name": recipe["name"],
            "description": recipe["description"],
            "type": recipe["item_type"],
            "crafter": crafter.character_id,
            "creation_date": datetime.now().isoformat(),
            "materials_used": consumed_materials,
            "enchantability": recipe["result_properties"]["base_enchantability"],
            "magic_profile": item_magic_profile.get_details()
        }
        
        return {
            "success": True,
            "message": f"Successfully crafted {recipe['name']}",
            "roll": roll,
            "success_chance": success_chance,
            "consumed_materials": consumed_materials,
            "crafted_item": crafted_item
        }

class MagicalPotionBrewer:
    """Manages the brewing of magical potions."""
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the magical potion brewer.
        
        Args:
            magic_system: The magic system
        """
        self.magic_system = magic_system
        self.potion_recipes = self._get_mock_potion_recipes()
    
    def _get_mock_potion_recipes(self) -> Dict[str, Dict[str, Any]]:
        """Get mock potion recipes for demonstration."""
        recipes = {}
        
        # Minor healing potion
        minor_healing = {
            "id": "potion_minor_healing",
            "name": "Minor Healing Potion",
            "description": "A potion that restores a small amount of health.",
            "required_materials": {
                "healing_herb": 2,
                "pure_water": 1,
                "alchemical_catalyst": 1
            },
            "required_domain_values": {
                Domain.CRAFT.name: 1,
                Domain.SPIRIT.name: 1
            },
            "brewing_difficulty": 20,
            "brewing_time": 30,  # minutes
            "effects": [
                {
                    "type": "healing",
                    "potency": 15,
                    "duration": 0
                }
            ]
        }
        recipes[minor_healing["id"]] = minor_healing
        
        # Minor mana potion
        minor_mana = {
            "id": "potion_minor_mana",
            "name": "Minor Mana Potion",
            "description": "A potion that restores a small amount of mana.",
            "required_materials": {
                "mana_crystal": 1,
                "arcane_dust": 1,
                "pure_water": 1
            },
            "required_domain_values": {
                Domain.CRAFT.name: 1,
                Domain.MIND.name: 1
            },
            "brewing_difficulty": 25,
            "brewing_time": 30,  # minutes
            "effects": [
                {
                    "type": "mana_restoration",
                    "potency": 20,
                    "duration": 0
                }
            ]
        }
        recipes[minor_mana["id"]] = minor_mana
        
        # Fire resistance potion
        fire_resistance = {
            "id": "potion_fire_resistance",
            "name": "Fire Resistance Potion",
            "description": "A potion that grants temporary resistance to fire damage.",
            "required_materials": {
                "fire_essence": 1,
                "dragon_scale": 1,
                "alchemical_catalyst": 1,
                "pure_water": 1
            },
            "required_domain_values": {
                Domain.CRAFT.name: 2,
                Domain.FIRE.name: 1
            },
            "brewing_difficulty": 35,
            "brewing_time": 45,  # minutes
            "effects": [
                {
                    "type": "resistance",
                    "damage_type": "fire",
                    "potency": 50,  # 50% resistance
                    "duration": 1800  # 30 minutes
                }
            ]
        }
        recipes[fire_resistance["id"]] = fire_resistance
        
        return recipes
    
    def get_potion_recipe_by_id(self, recipe_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a potion recipe by its ID.
        
        Args:
            recipe_id: The recipe ID
            
        Returns:
            The recipe or None if not found
        """
        return self.potion_recipes.get(recipe_id)
    
    def get_available_potion_recipes(self, character_domains: Dict[Domain, int]) -> List[Dict[str, Any]]:
        """
        Get available potion recipes based on character domains.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            List of available recipe information
        """
        available_recipes = []
        
        for recipe_id, recipe in self.potion_recipes.items():
            # Check if the character meets the domain requirements
            meets_requirements = True
            for domain_name, required_value in recipe["required_domain_values"].items():
                domain = Domain[domain_name]
                if domain not in character_domains or character_domains[domain] < required_value:
                    meets_requirements = False
                    break
            
            available_recipes.append({
                "id": recipe_id,
                "name": recipe["name"],
                "description": recipe["description"],
                "meets_requirements": meets_requirements,
                "required_materials": recipe["required_materials"],
                "brewing_difficulty": recipe["brewing_difficulty"],
                "brewing_time": recipe["brewing_time"],
                "effects": recipe["effects"]
            })
        
        return available_recipes
    
    def brew_potion(
        self,
        brewer: MagicUser,
        brewer_domains: Dict[Domain, int],
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Brew a potion using a recipe.
        
        Args:
            brewer: The magic user performing the brewing
            brewer_domains: The brewer's domain values
            recipe_id: The ID of the potion recipe
            available_materials: Dict mapping material IDs to quantities
            location_magic: Optional magic profile of the location
            
        Returns:
            Dict with result information
        """
        # Get the recipe
        recipe = self.get_potion_recipe_by_id(recipe_id)
        if not recipe:
            return {
                "success": False,
                "message": f"Potion recipe {recipe_id} not found"
            }
        
        # Check domain requirements
        for domain_name, required_value in recipe["required_domain_values"].items():
            domain = Domain[domain_name]
            if domain not in brewer_domains or brewer_domains[domain] < required_value:
                return {
                    "success": False,
                    "message": f"Domain requirement not met: {domain.name} {required_value}+"
                }
        
        # Check material requirements
        for material_id, required_quantity in recipe["required_materials"].items():
            if material_id not in available_materials or available_materials[material_id] < required_quantity:
                return {
                    "success": False,
                    "message": f"Not enough {material_id}: {available_materials.get(material_id, 0)}/{required_quantity}"
                }
        
        # Calculate brewing success chance
        base_chance = 100 - recipe["brewing_difficulty"]
        
        # Bonus from brewer's domains
        craft_bonus = brewer_domains.get(Domain.CRAFT, 0) * 3
        
        # Bonus from location magic
        location_bonus = 0
        if location_magic:
            location_bonus = int(location_magic.leyline_strength * 3)
        
        success_chance = min(95, base_chance + craft_bonus + location_bonus)
        
        # Roll for success
        roll = random.randint(1, 100)
        
        if roll > success_chance:
            # Brewing failed
            
            # Consume some materials
            consumed_materials = {}
            for material_id, required_quantity in recipe["required_materials"].items():
                # Consume half the materials on failure
                consumed_quantity = max(1, required_quantity // 2)
                consumed_materials[material_id] = consumed_quantity
            
            return {
                "success": False,
                "message": "The brewing attempt failed",
                "roll": roll,
                "success_chance": success_chance,
                "consumed_materials": consumed_materials
            }
        
        # Brewing succeeded
        
        # Consume all required materials
        consumed_materials = {}
        for material_id, required_quantity in recipe["required_materials"].items():
            consumed_materials[material_id] = required_quantity
        
        # Generate potion ID
        potion_id = f"potion_{recipe_id}_{int(datetime.now().timestamp())}"
        
        # Create the potion
        potion = {
            "id": potion_id,
            "name": recipe["name"],
            "description": recipe["description"],
            "type": "potion",
            "brewer": brewer.character_id,
            "creation_date": datetime.now().isoformat(),
            "materials_used": consumed_materials,
            "effects": recipe["effects"]
        }
        
        return {
            "success": True,
            "message": f"Successfully brewed {recipe['name']}",
            "roll": roll,
            "success_chance": success_chance,
            "consumed_materials": consumed_materials,
            "potion": potion
        }

class MagicCraftingIntegration:
    """Integrates magic with the crafting system."""
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the magic crafting integration.
        
        Args:
            magic_system: The magic system
        """
        self.magic_system = magic_system
        self.enchanter = ItemEnchanter(magic_system)
        self.item_crafter = MagicalItemCrafter(magic_system, self.enchanter)
        self.potion_brewer = MagicalPotionBrewer(magic_system)
    
    def get_enchantment_recipes(self, character_domains: Dict[Domain, int]) -> List[Dict[str, Any]]:
        """
        Get available enchantment recipes.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            List of available enchantment recipes
        """
        return self.enchanter.get_available_enchantment_recipes(character_domains)
    
    def get_crafting_recipes(self, character_domains: Dict[Domain, int]) -> List[Dict[str, Any]]:
        """
        Get available crafting recipes.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            List of available crafting recipes
        """
        return self.item_crafter.get_available_crafting_recipes(character_domains)
    
    def get_potion_recipes(self, character_domains: Dict[Domain, int]) -> List[Dict[str, Any]]:
        """
        Get available potion recipes.
        
        Args:
            character_domains: The character's domain values
            
        Returns:
            List of available potion recipes
        """
        return self.potion_brewer.get_available_potion_recipes(character_domains)
    
    def get_all_materials(self) -> List[Dict[str, Any]]:
        """
        Get all available crafting materials.
        
        Returns:
            List of all material information
        """
        return [material.to_dict() for material in self.enchanter.materials.values()]
    
    def perform_enchantment(
        self,
        enchanter: MagicUser,
        enchanter_domains: Dict[Domain, int],
        item_id: str,
        item_type: str,
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Perform an enchantment.
        
        Args:
            enchanter: The magic user performing the enchantment
            enchanter_domains: The enchanter's domain values
            item_id: The ID of the item to enchant
            item_type: The type of the item
            recipe_id: The ID of the enchantment recipe
            available_materials: Dict mapping material IDs to quantities
            location_magic: Optional magic profile of the location
            
        Returns:
            Dict with result information
        """
        return self.enchanter.enchant_item(
            enchanter,
            enchanter_domains,
            item_id,
            item_type,
            recipe_id,
            available_materials,
            location_magic
        )
    
    def craft_item(
        self,
        crafter: MagicUser,
        crafter_domains: Dict[Domain, int],
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Craft a magical item.
        
        Args:
            crafter: The magic user performing the crafting
            crafter_domains: The crafter's domain values
            recipe_id: The ID of the crafting recipe
            available_materials: Dict mapping material IDs to quantities
            location_magic: Optional magic profile of the location
            
        Returns:
            Dict with result information
        """
        return self.item_crafter.craft_magical_item(
            crafter,
            crafter_domains,
            recipe_id,
            available_materials,
            location_magic
        )
    
    def brew_potion(
        self,
        brewer: MagicUser,
        brewer_domains: Dict[Domain, int],
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Brew a potion.
        
        Args:
            brewer: The magic user performing the brewing
            brewer_domains: The brewer's domain values
            recipe_id: The ID of the potion recipe
            available_materials: Dict mapping material IDs to quantities
            location_magic: Optional magic profile of the location
            
        Returns:
            Dict with result information
        """
        return self.potion_brewer.brew_potion(
            brewer,
            brewer_domains,
            recipe_id,
            available_materials,
            location_magic
        )

# Initialize magic crafting integration
def create_magic_crafting_integration(magic_system: Optional[MagicSystem] = None) -> MagicCraftingIntegration:
    """
    Create and return the magic crafting integration.
    
    Args:
        magic_system: Optional magic system to use
    
    Returns:
        The magic crafting integration
    """
    # Create or use provided magic system
    magic_sys = magic_system or MagicSystem()
    
    # Create integration
    return MagicCraftingIntegration(magic_sys)