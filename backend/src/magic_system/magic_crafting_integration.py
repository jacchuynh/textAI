"""
Magic Crafting Integration Module

This module integrates the magic system with the crafting system,
allowing for enchantment, magical item creation, and potion brewing.
"""

from typing import Dict, List, Any, Optional, Tuple, Set, Union
import random
import math
import uuid
from enum import Enum, auto
from datetime import datetime, timedelta

# Import the core magic system
from game_engine.magic_system import (
    MagicSystem, MagicUser, Domain, DamageType, EffectType,
    MagicTier, Enchantment, ItemMagicProfile, LocationMagicProfile
)


class CraftingMaterial:
    """
    Represents a material that can be used in magical crafting.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        rarity: str,
        material_type: str,
        magical_properties: List[str] = None,
        resonance: List[str] = None,
        tier: MagicTier = MagicTier.LESSER,
        value: int = 1
    ):
        self.id = id
        self.name = name
        self.description = description
        self.rarity = rarity  # common, uncommon, rare, legendary
        self.material_type = material_type  # mineral, herb, essence, creature_part, etc.
        self.magical_properties = magical_properties or []
        self.resonance = resonance or []  # List of domain names as strings
        self.tier = tier
        self.value = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "material_type": self.material_type,
            "magical_properties": self.magical_properties,
            "resonance": self.resonance,
            "tier": self.tier.name,
            "value": self.value
        }


class EnchantmentRecipe:
    """
    Represents a recipe for creating an enchantment.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        required_domains: List[Domain],
        effects: List[str],
        compatible_item_types: List[str],
        required_materials: Dict[str, int],
        minimum_caster_level: int = 1
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.required_domains = required_domains
        self.effects = effects
        self.compatible_item_types = compatible_item_types
        self.required_materials = required_materials
        self.minimum_caster_level = minimum_caster_level
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.name,
            "required_domains": [domain.name for domain in self.required_domains],
            "effects": self.effects,
            "compatible_item_types": self.compatible_item_types,
            "required_materials": self.required_materials,
            "minimum_caster_level": self.minimum_caster_level
        }
    
    def check_requirements(self, caster: MagicUser, domains: List[Domain]) -> bool:
        """Check if the caster meets the requirements for this recipe."""
        # Check caster level
        if caster.level < self.minimum_caster_level:
            return False
        
        # Check domains
        has_required_domain = False
        for required_domain in self.required_domains:
            if required_domain in domains:
                has_required_domain = True
                break
        
        return has_required_domain


class MagicalItemType(Enum):
    """Types of magical items that can be crafted."""
    WAND = auto()
    STAFF = auto()
    ORB = auto()
    AMULET = auto()
    RING = auto()
    ROBE = auto()
    SCROLL = auto()
    POTION = auto()
    TALISMAN = auto()
    RUNE = auto()
    FOCUS = auto()


class CraftingRecipe:
    """
    Represents a recipe for crafting a magical item.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        item_type: MagicalItemType,
        tier: MagicTier,
        required_domains: List[Domain],
        required_materials: Dict[str, int],
        crafting_difficulty: int,  # 1-10
        minimum_caster_level: int = 1,
        mana_cost: int = 0,
        production_time_minutes: int = 60,
        creates_item_id: str = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.item_type = item_type
        self.tier = tier
        self.required_domains = required_domains
        self.required_materials = required_materials
        self.crafting_difficulty = crafting_difficulty
        self.minimum_caster_level = minimum_caster_level
        self.mana_cost = mana_cost
        self.production_time_minutes = production_time_minutes
        self.creates_item_id = creates_item_id or f"item_{id}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.name,
            "tier": self.tier.name,
            "required_domains": [domain.name for domain in self.required_domains],
            "required_materials": self.required_materials,
            "crafting_difficulty": self.crafting_difficulty,
            "minimum_caster_level": self.minimum_caster_level,
            "mana_cost": self.mana_cost,
            "production_time_minutes": self.production_time_minutes
        }
    
    def check_requirements(self, caster: MagicUser, domains: List[Domain]) -> bool:
        """Check if the caster meets the requirements for this recipe."""
        # Check caster level
        if caster.level < self.minimum_caster_level:
            return False
        
        # Check domains
        has_required_domain = False
        for required_domain in self.required_domains:
            if required_domain in domains:
                has_required_domain = True
                break
        
        return has_required_domain


class PotionRecipe:
    """
    Represents a recipe for brewing a magical potion.
    """
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        tier: MagicTier,
        required_domains: List[Domain],
        effects: List[Dict[str, Any]],
        required_materials: Dict[str, int],
        brewing_difficulty: int,  # 1-10
        minimum_caster_level: int = 1,
        mana_cost: int = 0,
        brewing_time_minutes: int = 30
    ):
        self.id = id
        self.name = name
        self.description = description
        self.tier = tier
        self.required_domains = required_domains
        self.effects = effects
        self.required_materials = required_materials
        self.brewing_difficulty = brewing_difficulty
        self.minimum_caster_level = minimum_caster_level
        self.mana_cost = mana_cost
        self.brewing_time_minutes = brewing_time_minutes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tier": self.tier.name,
            "required_domains": [domain.name for domain in self.required_domains],
            "effects": self.effects,
            "required_materials": self.required_materials,
            "brewing_difficulty": self.brewing_difficulty,
            "minimum_caster_level": self.minimum_caster_level,
            "mana_cost": self.mana_cost,
            "brewing_time_minutes": self.brewing_time_minutes
        }
    
    def check_requirements(self, caster: MagicUser, domains: List[Domain]) -> bool:
        """Check if the caster meets the requirements for this recipe."""
        # Check caster level
        if caster.level < self.minimum_caster_level:
            return False
        
        # Check domains
        has_required_domain = False
        for required_domain in self.required_domains:
            if required_domain in domains:
                has_required_domain = True
                break
        
        return has_required_domain


class ItemEnchanter:
    """
    Handles the enchantment of items with magical properties.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
        # Initialize with basic enchantment recipes
        self.enchantment_recipes = self._get_initial_enchantment_recipes()
    
    def _get_initial_enchantment_recipes(self) -> Dict[str, EnchantmentRecipe]:
        """Get the initial set of enchantment recipes."""
        recipes = {}
        
        # Fire Damage Enchantment
        recipes["fire_damage"] = EnchantmentRecipe(
            id="fire_damage",
            name="Enchantment of Flame",
            description="Imbues a weapon with fiery energy, causing it to deal additional fire damage.",
            tier=MagicTier.LESSER,
            required_domains=[Domain.ELEMENTAL],
            effects=["Deals additional fire damage on hit", "Weapon glows with an inner flame"],
            compatible_item_types=["weapon", "staff", "wand"],
            required_materials={"fire_essence": 2, "mana_crystal": 1},
            minimum_caster_level=3
        )
        
        # Protection Enchantment
        recipes["protection"] = EnchantmentRecipe(
            id="protection",
            name="Enchantment of Warding",
            description="Creates a protective barrier around armor or clothing, reducing damage taken.",
            tier=MagicTier.LESSER,
            required_domains=[Domain.DIVINE, Domain.ARCANE],
            effects=["Reduces physical damage taken", "Glows briefly when absorbing damage"],
            compatible_item_types=["armor", "robe", "cloak", "amulet"],
            required_materials={"divine_light": 1, "mana_crystal": 2},
            minimum_caster_level=3
        )
        
        # Mana Regeneration Enchantment
        recipes["mana_regen"] = EnchantmentRecipe(
            id="mana_regen",
            name="Enchantment of Arcane Flow",
            description="Enhances the natural flow of mana, increasing regeneration rate.",
            tier=MagicTier.MODERATE,
            required_domains=[Domain.ARCANE],
            effects=["Increases mana regeneration rate", "Item feels slightly tingly to the touch"],
            compatible_item_types=["ring", "amulet", "staff", "orb"],
            required_materials={"arcane_dust": 3, "mana_crystal": 2},
            minimum_caster_level=5
        )
        
        # Mind Shielding Enchantment
        recipes["mind_shield"] = EnchantmentRecipe(
            id="mind_shield",
            name="Enchantment of Mental Fortress",
            description="Protects the wearer's mind from external influence and mental attacks.",
            tier=MagicTier.MODERATE,
            required_domains=[Domain.MIND],
            effects=["Reduces effectiveness of mind-affecting spells", "Grants resistance to fear and charm effects"],
            compatible_item_types=["helmet", "circlet", "amulet"],
            required_materials={"mind_crystal": 2, "shadow_residue": 1},
            minimum_caster_level=6
        )
        
        # Life Drain Enchantment
        recipes["life_drain"] = EnchantmentRecipe(
            id="life_drain",
            name="Enchantment of Vitality Theft",
            description="Channels a portion of damage dealt back to the wielder as healing.",
            tier=MagicTier.GREATER,
            required_domains=[Domain.BLOOD, Domain.SHADOW],
            effects=["Converts a percentage of damage dealt to healing", "Weapon pulses with a dark red aura when active"],
            compatible_item_types=["weapon", "staff", "wand"],
            required_materials={"blood_essence": 3, "shadow_residue": 2, "void_fragment": 1},
            minimum_caster_level=10
        )
        
        return recipes
    
    def enchant_item(
        self,
        caster: MagicUser,
        item_id: str,
        item_type: str,
        enchantment_id: str,
        available_materials: Dict[str, int],
        location_magic_profile: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Attempt to enchant an item with a specific enchantment.
        
        Args:
            caster: The magic user performing the enchantment
            item_id: The ID of the item to enchant
            item_type: The type of the item (weapon, armor, etc.)
            enchantment_id: The ID of the enchantment to apply
            available_materials: Dictionary of material_id -> quantity
            location_magic_profile: Optional magical profile of the location
            
        Returns:
            A dictionary with the result of the enchantment attempt
        """
        # Check if the enchantment recipe exists
        if enchantment_id not in self.enchantment_recipes:
            return {
                "success": False,
                "message": f"Unknown enchantment: {enchantment_id}"
            }
        
        recipe = self.enchantment_recipes[enchantment_id]
        
        # Check if item type is compatible
        if item_type not in recipe.compatible_item_types:
            return {
                "success": False,
                "message": f"This enchantment cannot be applied to {item_type}"
            }
        
        # Check caster level requirement
        if caster.level < recipe.minimum_caster_level:
            return {
                "success": False,
                "message": f"Enchanter level too low. Requires level {recipe.minimum_caster_level}."
            }
        
        # Check domain requirements
        caster_domains = caster.primary_domains + caster.secondary_domains
        has_required_domain = any(domain in caster_domains for domain in recipe.required_domains)
        
        if not has_required_domain:
            domain_names = [domain.name for domain in recipe.required_domains]
            return {
                "success": False,
                "message": f"Missing required magical domain. Needs one of: {', '.join(domain_names)}"
            }
        
        # Check material requirements
        missing_materials = []
        for material_id, required_amount in recipe.required_materials.items():
            available_amount = available_materials.get(material_id, 0)
            if available_amount < required_amount:
                missing_materials.append(f"{material_id} (need {required_amount}, have {available_amount})")
        
        if missing_materials:
            return {
                "success": False,
                "message": f"Missing required materials: {', '.join(missing_materials)}"
            }
        
        # Calculate success chance
        base_success_chance = 0.7  # 70% base chance
        
        # Adjust based on caster level vs. required level
        level_factor = min(1.0, (caster.level - recipe.minimum_caster_level) * 0.05 + 0.1)
        
        # Adjust based on domain affinity
        domain_factor = 0.1
        for domain in recipe.required_domains:
            if domain in caster.primary_domains:
                domain_factor += 0.15  # Bigger bonus for primary domains
            elif domain in caster.secondary_domains:
                domain_factor += 0.08  # Smaller bonus for secondary domains
        
        # Adjust based on location magic profile
        location_factor = 0.0
        if location_magic_profile:
            # Check if location has resonant domains
            for domain in recipe.required_domains:
                if domain in location_magic_profile.dominant_magic_aspects:
                    location_factor += 0.1
            
            # Adjust based on leyline strength
            location_factor += location_magic_profile.leyline_strength * 0.2
            
            # Adjust based on mana flux
            flux_multiplier = {
                "VERY_LOW": 0.5,
                "LOW": 0.8,
                "MEDIUM": 1.0,
                "HIGH": 1.2,
                "VERY_HIGH": 1.5
            }
            location_factor *= flux_multiplier.get(location_magic_profile.mana_flux_level.name, 1.0)
        
        # Calculate final success chance
        success_chance = min(0.95, base_success_chance + level_factor + domain_factor + location_factor)
        
        # Roll for success
        roll = random.random()
        success = roll <= success_chance
        
        # If success, create the enchantment and item magic profile
        if success:
            # Consume materials
            consumed_materials = {}
            for material_id, required_amount in recipe.required_materials.items():
                consumed_materials[material_id] = required_amount
                available_materials[material_id] -= required_amount
            
            # Create the enchantment
            enchantment = Enchantment(
                id=f"{enchantment_id}_{uuid.uuid4().hex[:8]}",
                name=recipe.name,
                description=recipe.description,
                tier=recipe.tier,
                domains=recipe.required_domains,
                effects=recipe.effects,
                item_types=recipe.compatible_item_types,
                power_level=self._calculate_enchantment_power(caster, recipe, location_magic_profile),
                duration_days=None,  # Permanent
                charges=None,  # Unlimited
                required_materials=recipe.required_materials,
                tags=[domain.name for domain in recipe.required_domains]
            )
            
            # Create or update the item's magic profile
            item_magic_profile = ItemMagicProfile(
                item_id=item_id,
                is_magical=True,
                is_enchanted=True,
                is_artifact=False,
                enchantment_id=enchantment.id,
                inherent_magical_properties=recipe.effects,
                mana_storage_capacity=int(20 * recipe.tier.value / MagicTier.LEGENDARY.value),
                stored_mana=0,
                resonance_domains=recipe.required_domains,
                crafting_tier=recipe.tier,
                creation_date=datetime.now()
            )
            
            # Register with magic system if available
            if self.magic_system:
                self.magic_system.register_enchantment(enchantment)
                self.magic_system.register_item_profile(item_magic_profile)
            
            return {
                "success": True,
                "message": f"Successfully enchanted {item_type} with {recipe.name}",
                "enchantment": enchantment.__dict__,
                "item_magic_profile": item_magic_profile.__dict__,
                "consumed_materials": consumed_materials,
                "success_chance": success_chance
            }
        else:
            # Failed enchantment - consume half the materials
            consumed_materials = {}
            for material_id, required_amount in recipe.required_materials.items():
                consumed_amount = max(1, required_amount // 2)
                consumed_materials[material_id] = consumed_amount
                available_materials[material_id] -= consumed_amount
            
            return {
                "success": False,
                "message": f"Enchantment failed. Some materials were consumed in the attempt.",
                "consumed_materials": consumed_materials,
                "success_chance": success_chance
            }
    
    def _calculate_enchantment_power(
        self, 
        caster: MagicUser, 
        recipe: EnchantmentRecipe,
        location_magic_profile: Optional[LocationMagicProfile]
    ) -> float:
        """Calculate the power level of an enchantment based on various factors."""
        # Base power from recipe tier
        base_power = {
            MagicTier.CANTRIP: 1.0,
            MagicTier.LESSER: 2.0,
            MagicTier.MODERATE: 3.0,
            MagicTier.GREATER: 4.0,
            MagicTier.MASTER: 5.0,
            MagicTier.LEGENDARY: 6.0
        }.get(recipe.tier, 1.0)
        
        # Adjust based on caster level
        level_factor = 1.0 + (caster.level * 0.05)
        
        # Adjust based on domain affinity
        domain_factor = 1.0
        for domain in recipe.required_domains:
            if domain in caster.primary_domains:
                domain_factor += 0.2  # Bigger bonus for primary domains
            elif domain in caster.secondary_domains:
                domain_factor += 0.1  # Smaller bonus for secondary domains
        
        # Adjust based on location
        location_factor = 1.0
        if location_magic_profile:
            # Check for resonant domains
            for domain in recipe.required_domains:
                if domain in location_magic_profile.dominant_magic_aspects:
                    location_factor += 0.15
            
            # Adjust based on leyline strength
            location_factor += location_magic_profile.leyline_strength * 0.3
        
        # Calculate final power
        return base_power * level_factor * domain_factor * location_factor
    
    def get_available_enchantments(
        self, 
        caster: MagicUser, 
        item_type: str, 
        available_materials: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Get a list of enchantments that the caster can apply to an item.
        
        Args:
            caster: The magic user performing the enchantment
            item_type: The type of the item (weapon, armor, etc.)
            available_materials: Dictionary of material_id -> quantity
            
        Returns:
            A list of dictionaries with enchantment details
        """
        available_enchantments = []
        caster_domains = caster.primary_domains + caster.secondary_domains
        
        for enchantment_id, recipe in self.enchantment_recipes.items():
            # Check if item type is compatible
            if item_type not in recipe.compatible_item_types:
                continue
            
            # Check domain requirements
            has_required_domain = any(domain in caster_domains for domain in recipe.required_domains)
            if not has_required_domain:
                continue
            
            # Check material requirements and count missing materials
            missing_materials = []
            for material_id, required_amount in recipe.required_materials.items():
                available_amount = available_materials.get(material_id, 0)
                if available_amount < required_amount:
                    missing_materials.append(f"{material_id} (need {required_amount}, have {available_amount})")
            
            # Check caster level
            meets_level_req = caster.level >= recipe.minimum_caster_level
            
            # Add to available enchantments with requirements info
            enchantment_info = recipe.to_dict()
            enchantment_info["meets_requirements"] = meets_level_req and not missing_materials
            enchantment_info["missing_materials"] = missing_materials
            enchantment_info["compatible_item_types"] = recipe.compatible_item_types
            
            available_enchantments.append(enchantment_info)
        
        return available_enchantments


class MagicalItemCrafter:
    """
    Handles the crafting of magical items from raw materials.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
        # Initialize with basic crafting recipes
        self.crafting_recipes = self._get_initial_crafting_recipes()
    
    def _get_initial_crafting_recipes(self) -> Dict[str, CraftingRecipe]:
        """Get the initial set of crafting recipes."""
        recipes = {}
        
        # Basic Wand
        recipes["basic_wand"] = CraftingRecipe(
            id="basic_wand",
            name="Apprentice's Wand",
            description="A simple wand that can channel magical energy for beginner mages.",
            item_type=MagicalItemType.WAND,
            tier=MagicTier.LESSER,
            required_domains=[Domain.ARCANE],
            required_materials={"wood": 1, "mana_crystal": 1},
            crafting_difficulty=2,
            minimum_caster_level=1,
            mana_cost=10,
            production_time_minutes=30
        )
        
        # Focus Orb
        recipes["focus_orb"] = CraftingRecipe(
            id="focus_orb",
            name="Mage's Focus Orb",
            description="A crystal orb that enhances concentration and spell precision.",
            item_type=MagicalItemType.ORB,
            tier=MagicTier.MODERATE,
            required_domains=[Domain.ARCANE, Domain.MIND],
            required_materials={"mana_crystal": 2, "mind_crystal": 1, "silver": 1},
            crafting_difficulty=4,
            minimum_caster_level=3,
            mana_cost=25,
            production_time_minutes=60
        )
        
        # Elemental Staff
        recipes["elemental_staff"] = CraftingRecipe(
            id="elemental_staff",
            name="Elemental Channeling Staff",
            description="A staff designed to channel and amplify elemental magic.",
            item_type=MagicalItemType.STAFF,
            tier=MagicTier.MODERATE,
            required_domains=[Domain.ELEMENTAL],
            required_materials={"hardwood": 2, "elemental_essence": 2, "mana_crystal": 1},
            crafting_difficulty=5,
            minimum_caster_level=5,
            mana_cost=35,
            production_time_minutes=120
        )
        
        # Protection Amulet
        recipes["protection_amulet"] = CraftingRecipe(
            id="protection_amulet",
            name="Amulet of Warding",
            description="An amulet that provides magical protection to the wearer.",
            item_type=MagicalItemType.AMULET,
            tier=MagicTier.MODERATE,
            required_domains=[Domain.DIVINE, Domain.ARCANE],
            required_materials={"silver": 1, "gold": 1, "divine_light": 1, "mana_crystal": 1},
            crafting_difficulty=4,
            minimum_caster_level=4,
            mana_cost=30,
            production_time_minutes=90
        )
        
        # Arcane Ring
        recipes["arcane_ring"] = CraftingRecipe(
            id="arcane_ring",
            name="Ring of Arcane Power",
            description="A ring that stores magical energy and enhances spell power.",
            item_type=MagicalItemType.RING,
            tier=MagicTier.GREATER,
            required_domains=[Domain.ARCANE],
            required_materials={"gold": 1, "platinum": 1, "arcane_dust": 2, "mana_crystal": 2},
            crafting_difficulty=6,
            minimum_caster_level=7,
            mana_cost=50,
            production_time_minutes=180
        )
        
        return recipes
    
    def craft_item(
        self,
        caster: MagicUser,
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic_profile: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Attempt to craft a magical item using a recipe.
        
        Args:
            caster: The magic user performing the crafting
            recipe_id: The ID of the crafting recipe to use
            available_materials: Dictionary of material_id -> quantity
            location_magic_profile: Optional magical profile of the location
            
        Returns:
            A dictionary with the result of the crafting attempt
        """
        # Check if the recipe exists
        if recipe_id not in self.crafting_recipes:
            return {
                "success": False,
                "message": f"Unknown recipe: {recipe_id}"
            }
        
        recipe = self.crafting_recipes[recipe_id]
        
        # Check caster level requirement
        if caster.level < recipe.minimum_caster_level:
            return {
                "success": False,
                "message": f"Crafter level too low. Requires level {recipe.minimum_caster_level}."
            }
        
        # Check domain requirements
        caster_domains = caster.primary_domains + caster.secondary_domains
        has_required_domain = any(domain in caster_domains for domain in recipe.required_domains)
        
        if not has_required_domain:
            domain_names = [domain.name for domain in recipe.required_domains]
            return {
                "success": False,
                "message": f"Missing required magical domain. Needs one of: {', '.join(domain_names)}"
            }
        
        # Check material requirements
        missing_materials = []
        for material_id, required_amount in recipe.required_materials.items():
            available_amount = available_materials.get(material_id, 0)
            if available_amount < required_amount:
                missing_materials.append(f"{material_id} (need {required_amount}, have {available_amount})")
        
        if missing_materials:
            return {
                "success": False,
                "message": f"Missing required materials: {', '.join(missing_materials)}"
            }
        
        # Check mana cost
        if caster.mana_current < recipe.mana_cost:
            return {
                "success": False,
                "message": f"Not enough mana. Requires {recipe.mana_cost}, have {caster.mana_current}."
            }
        
        # Calculate success chance
        base_success_chance = 0.8 - (recipe.crafting_difficulty * 0.05)  # Harder recipes have lower base chance
        
        # Adjust based on caster level vs. required level
        level_factor = min(0.3, (caster.level - recipe.minimum_caster_level) * 0.05)
        
        # Adjust based on domain affinity
        domain_factor = 0.0
        for domain in recipe.required_domains:
            if domain in caster.primary_domains:
                domain_factor += 0.1  # Bigger bonus for primary domains
            elif domain in caster.secondary_domains:
                domain_factor += 0.05  # Smaller bonus for secondary domains
        
        # Adjust based on location magic profile
        location_factor = 0.0
        if location_magic_profile:
            # Check if location has resonant domains
            for domain in recipe.required_domains:
                if domain in location_magic_profile.dominant_magic_aspects:
                    location_factor += 0.08
            
            # Adjust based on leyline strength
            location_factor += location_magic_profile.leyline_strength * 0.15
        
        # Calculate final success chance
        success_chance = min(0.95, base_success_chance + level_factor + domain_factor + location_factor)
        
        # Roll for success
        roll = random.random()
        success = roll <= success_chance
        
        # Spend mana regardless of outcome
        caster.spend_mana(recipe.mana_cost)
        
        # If success, create the item
        if success:
            # Consume materials
            consumed_materials = {}
            for material_id, required_amount in recipe.required_materials.items():
                consumed_materials[material_id] = required_amount
                available_materials[material_id] -= required_amount
            
            # Create a unique ID for the crafted item
            item_id = f"{recipe.item_type.name.lower()}_{uuid.uuid4().hex[:8]}"
            
            # Create the item's magic profile
            item_magic_profile = ItemMagicProfile(
                item_id=item_id,
                is_magical=True,
                is_enchanted=False,
                is_artifact=False,
                enchantment_id=None,
                inherent_magical_properties=[],
                mana_storage_capacity=int(30 * recipe.tier.value / MagicTier.LEGENDARY.value),
                stored_mana=0,
                resonance_domains=recipe.required_domains,
                crafting_tier=recipe.tier,
                creation_date=datetime.now()
            )
            
            # Register with magic system if available
            if self.magic_system:
                self.magic_system.register_item_profile(item_magic_profile)
            
            # Create the crafted item data
            crafted_item = {
                "id": item_id,
                "name": recipe.name,
                "description": recipe.description,
                "type": recipe.item_type.name,
                "tier": recipe.tier.name,
                "quality": self._calculate_item_quality(success_chance, roll),
                "crafted_by": caster.name,
                "domains": [domain.name for domain in recipe.required_domains],
                "magic_profile": item_magic_profile.__dict__,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "message": f"Successfully crafted {recipe.name}",
                "crafted_item": crafted_item,
                "consumed_materials": consumed_materials,
                "success_chance": success_chance,
                "mana_spent": recipe.mana_cost
            }
        else:
            # Failed crafting - consume half the materials
            consumed_materials = {}
            for material_id, required_amount in recipe.required_materials.items():
                consumed_amount = max(1, required_amount // 2)
                consumed_materials[material_id] = consumed_amount
                available_materials[material_id] -= consumed_amount
            
            return {
                "success": False,
                "message": f"Crafting failed. Some materials were consumed in the attempt.",
                "consumed_materials": consumed_materials,
                "success_chance": success_chance,
                "mana_spent": recipe.mana_cost
            }
    
    def _calculate_item_quality(self, success_chance: float, roll: float) -> str:
        """Calculate the quality of a crafted item based on how well the roll succeeded."""
        if success_chance - roll > 0.3:
            return "masterwork"  # Greatly exceeded required roll
        elif success_chance - roll > 0.1:
            return "exceptional"  # Comfortably exceeded required roll
        else:
            return "standard"  # Just barely succeeded
    
    def get_available_recipes(
        self, 
        caster: MagicUser, 
        available_materials: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Get a list of crafting recipes that the caster can use.
        
        Args:
            caster: The magic user performing the crafting
            available_materials: Dictionary of material_id -> quantity
            
        Returns:
            A list of dictionaries with recipe details
        """
        available_recipes = []
        caster_domains = caster.primary_domains + caster.secondary_domains
        
        for recipe_id, recipe in self.crafting_recipes.items():
            # Check domain requirements
            has_required_domain = any(domain in caster_domains for domain in recipe.required_domains)
            
            # Check material requirements and count missing materials
            missing_materials = []
            for material_id, required_amount in recipe.required_materials.items():
                available_amount = available_materials.get(material_id, 0)
                if available_amount < required_amount:
                    missing_materials.append(f"{material_id} (need {required_amount}, have {available_amount})")
            
            # Check caster level
            meets_level_req = caster.level >= recipe.minimum_caster_level
            
            # Check mana cost
            has_enough_mana = caster.mana_current >= recipe.mana_cost
            
            # Add to available recipes with requirements info
            recipe_info = recipe.to_dict()
            recipe_info["meets_requirements"] = meets_level_req and has_required_domain and has_enough_mana and not missing_materials
            recipe_info["missing_materials"] = missing_materials
            recipe_info["has_enough_mana"] = has_enough_mana
            
            available_recipes.append(recipe_info)
        
        return available_recipes


class MagicalPotionBrewer:
    """
    Handles the brewing of magical potions.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
        # Initialize with basic potion recipes
        self.potion_recipes = self._get_initial_potion_recipes()
    
    def _get_initial_potion_recipes(self) -> Dict[str, PotionRecipe]:
        """Get the initial set of potion recipes."""
        recipes = {}
        
        # Healing Potion
        recipes["healing_potion"] = PotionRecipe(
            id="healing_potion",
            name="Minor Healing Potion",
            description="A potion that restores a small amount of health when consumed.",
            tier=MagicTier.LESSER,
            required_domains=[Domain.NATURAL, Domain.DIVINE],
            effects=[{"type": "healing", "potency": 20}],
            required_materials={"healing_herb": 2, "pure_water": 1},
            brewing_difficulty=2,
            minimum_caster_level=1,
            mana_cost=10,
            brewing_time_minutes=15
        )
        
        # Mana Potion
        recipes["mana_potion"] = PotionRecipe(
            id="mana_potion",
            name="Minor Mana Potion",
            description="A potion that restores a small amount of mana when consumed.",
            tier=MagicTier.LESSER,
            required_domains=[Domain.ARCANE],
            effects=[{"type": "mana_restoration", "potency": 25}],
            required_materials={"mana_crystal": 1, "pure_water": 1},
            brewing_difficulty=2,
            minimum_caster_level=1,
            mana_cost=5,
            brewing_time_minutes=15
        )
        
        # Fire Resistance Potion
        recipes["fire_resistance"] = PotionRecipe(
            id="fire_resistance",
            name="Fire Resistance Potion",
            description="A potion that grants temporary resistance to fire damage.",
            tier=MagicTier.MODERATE,
            required_domains=[Domain.ELEMENTAL],
            effects=[{"type": "resistance", "damage_type": "FIRE", "potency": 0.5, "duration_minutes": 30}],
            required_materials={"frost_extract": 2, "elemental_essence": 1, "pure_water": 1},
            brewing_difficulty=4,
            minimum_caster_level=3,
            mana_cost=20,
            brewing_time_minutes=30
        )
        
        # Clarity Potion
        recipes["clarity_potion"] = PotionRecipe(
            id="clarity_potion",
            name="Potion of Mental Clarity",
            description="A potion that temporarily enhances mental focus and clarity.",
            tier=MagicTier.MODERATE,
            required_domains=[Domain.MIND],
            effects=[
                {"type": "buff", "stat": "concentration", "potency": 3, "duration_minutes": 60},
                {"type": "buff", "stat": "spellcasting", "potency": 2, "duration_minutes": 60}
            ],
            required_materials={"mind_crystal": 1, "clarity_herb": 2, "pure_water": 1},
            brewing_difficulty=4,
            minimum_caster_level=4,
            mana_cost=25,
            brewing_time_minutes=45
        )
        
        # Invisibility Potion
        recipes["invisibility_potion"] = PotionRecipe(
            id="invisibility_potion",
            name="Potion of Invisibility",
            description="A potion that renders the drinker invisible for a short time.",
            tier=MagicTier.GREATER,
            required_domains=[Domain.ARCANE, Domain.SHADOW],
            effects=[{"type": "invisibility", "potency": 0.9, "duration_minutes": 10}],
            required_materials={"shadow_residue": 2, "ghost_flower": 1, "mana_crystal": 1, "pure_water": 1},
            brewing_difficulty=6,
            minimum_caster_level=7,
            mana_cost=40,
            brewing_time_minutes=60
        )
        
        return recipes
    
    def brew_potion(
        self,
        caster: MagicUser,
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic_profile: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Attempt to brew a potion using a recipe.
        
        Args:
            caster: The magic user performing the brewing
            recipe_id: The ID of the potion recipe to use
            available_materials: Dictionary of material_id -> quantity
            location_magic_profile: Optional magical profile of the location
            
        Returns:
            A dictionary with the result of the brewing attempt
        """
        # Check if the recipe exists
        if recipe_id not in self.potion_recipes:
            return {
                "success": False,
                "message": f"Unknown recipe: {recipe_id}"
            }
        
        recipe = self.potion_recipes[recipe_id]
        
        # Check caster level requirement
        if caster.level < recipe.minimum_caster_level:
            return {
                "success": False,
                "message": f"Brewer level too low. Requires level {recipe.minimum_caster_level}."
            }
        
        # Check domain requirements
        caster_domains = caster.primary_domains + caster.secondary_domains
        has_required_domain = any(domain in caster_domains for domain in recipe.required_domains)
        
        if not has_required_domain:
            domain_names = [domain.name for domain in recipe.required_domains]
            return {
                "success": False,
                "message": f"Missing required magical domain. Needs one of: {', '.join(domain_names)}"
            }
        
        # Check material requirements
        missing_materials = []
        for material_id, required_amount in recipe.required_materials.items():
            available_amount = available_materials.get(material_id, 0)
            if available_amount < required_amount:
                missing_materials.append(f"{material_id} (need {required_amount}, have {available_amount})")
        
        if missing_materials:
            return {
                "success": False,
                "message": f"Missing required materials: {', '.join(missing_materials)}"
            }
        
        # Check mana cost
        if caster.mana_current < recipe.mana_cost:
            return {
                "success": False,
                "message": f"Not enough mana. Requires {recipe.mana_cost}, have {caster.mana_current}."
            }
        
        # Calculate success chance
        base_success_chance = 0.85 - (recipe.brewing_difficulty * 0.05)  # Harder recipes have lower base chance
        
        # Adjust based on caster level vs. required level
        level_factor = min(0.3, (caster.level - recipe.minimum_caster_level) * 0.05)
        
        # Adjust based on domain affinity
        domain_factor = 0.0
        for domain in recipe.required_domains:
            if domain in caster.primary_domains:
                domain_factor += 0.1  # Bigger bonus for primary domains
            elif domain in caster.secondary_domains:
                domain_factor += 0.05  # Smaller bonus for secondary domains
        
        # Adjust based on location magic profile
        location_factor = 0.0
        if location_magic_profile:
            # Check if location has resonant domains
            for domain in recipe.required_domains:
                if domain in location_magic_profile.dominant_magic_aspects:
                    location_factor += 0.08
            
            # Adjust based on leyline strength
            location_factor += location_magic_profile.leyline_strength * 0.15
        
        # Calculate final success chance
        success_chance = min(0.95, base_success_chance + level_factor + domain_factor + location_factor)
        
        # Roll for success
        roll = random.random()
        success = roll <= success_chance
        
        # Spend mana regardless of outcome
        caster.spend_mana(recipe.mana_cost)
        
        # If success, create the potion
        if success:
            # Consume materials
            consumed_materials = {}
            for material_id, required_amount in recipe.required_materials.items():
                consumed_materials[material_id] = required_amount
                available_materials[material_id] -= required_amount
            
            # Create a unique ID for the brewed potion
            potion_id = f"potion_{uuid.uuid4().hex[:8]}"
            
            # Adjust effect potency based on brewer skill and roll success
            potency_multiplier = 1.0 + ((success_chance - roll) / success_chance * 0.5)
            adjusted_effects = []
            
            for effect in recipe.effects:
                adjusted_effect = effect.copy()
                if "potency" in adjusted_effect:
                    adjusted_effect["potency"] = adjusted_effect["potency"] * potency_multiplier
                adjusted_effects.append(adjusted_effect)
            
            # Create the potion data
            potion = {
                "id": potion_id,
                "name": recipe.name,
                "description": recipe.description,
                "type": "POTION",
                "tier": recipe.tier.name,
                "quality": self._calculate_potion_quality(success_chance, roll),
                "brewed_by": caster.name,
                "domains": [domain.name for domain in recipe.required_domains],
                "effects": adjusted_effects,
                "created_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "message": f"Successfully brewed {recipe.name}",
                "potion": potion,
                "consumed_materials": consumed_materials,
                "success_chance": success_chance,
                "mana_spent": recipe.mana_cost
            }
        else:
            # Failed brewing - consume half the materials
            consumed_materials = {}
            for material_id, required_amount in recipe.required_materials.items():
                consumed_amount = max(1, required_amount // 2)
                consumed_materials[material_id] = consumed_amount
                available_materials[material_id] -= consumed_amount
            
            return {
                "success": False,
                "message": f"Brewing failed. Some materials were consumed in the attempt.",
                "consumed_materials": consumed_materials,
                "success_chance": success_chance,
                "mana_spent": recipe.mana_cost
            }
    
    def _calculate_potion_quality(self, success_chance: float, roll: float) -> str:
        """Calculate the quality of a brewed potion based on how well the roll succeeded."""
        if success_chance - roll > 0.3:
            return "masterwork"  # Greatly exceeded required roll
        elif success_chance - roll > 0.1:
            return "exceptional"  # Comfortably exceeded required roll
        else:
            return "standard"  # Just barely succeeded
    
    def get_available_recipes(
        self, 
        caster: MagicUser, 
        available_materials: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Get a list of potion recipes that the caster can use.
        
        Args:
            caster: The magic user performing the brewing
            available_materials: Dictionary of material_id -> quantity
            
        Returns:
            A list of dictionaries with recipe details
        """
        available_recipes = []
        caster_domains = caster.primary_domains + caster.secondary_domains
        
        for recipe_id, recipe in self.potion_recipes.items():
            # Check domain requirements
            has_required_domain = any(domain in caster_domains for domain in recipe.required_domains)
            
            # Check material requirements and count missing materials
            missing_materials = []
            for material_id, required_amount in recipe.required_materials.items():
                available_amount = available_materials.get(material_id, 0)
                if available_amount < required_amount:
                    missing_materials.append(f"{material_id} (need {required_amount}, have {available_amount})")
            
            # Check caster level
            meets_level_req = caster.level >= recipe.minimum_caster_level
            
            # Check mana cost
            has_enough_mana = caster.mana_current >= recipe.mana_cost
            
            # Add to available recipes with requirements info
            recipe_info = recipe.to_dict()
            recipe_info["meets_requirements"] = meets_level_req and has_required_domain and has_enough_mana and not missing_materials
            recipe_info["missing_materials"] = missing_materials
            recipe_info["has_enough_mana"] = has_enough_mana
            
            available_recipes.append(recipe_info)
        
        return available_recipes


class MagicCraftingIntegration:
    """
    Integrates the magic system with the crafting system.
    """
    def __init__(self, magic_system: MagicSystem = None):
        self.magic_system = magic_system
        self.enchanter = ItemEnchanter(magic_system)
        self.crafter = MagicalItemCrafter(magic_system)
        self.brewer = MagicalPotionBrewer(magic_system)
        
        # Mock materials database
        self.materials_database = self._initialize_materials_database()
    
    def _initialize_materials_database(self) -> Dict[str, CraftingMaterial]:
        """Initialize a database of crafting materials."""
        materials = {}
        
        # Basic materials
        materials["wood"] = CraftingMaterial(
            id="wood",
            name="Common Wood",
            description="Basic wood suitable for simple crafting.",
            rarity="common",
            material_type="wood",
            resonance=["NATURAL"]
        )
        
        materials["hardwood"] = CraftingMaterial(
            id="hardwood",
            name="Hardwood",
            description="Strong, dense wood ideal for magical implements.",
            rarity="common",
            material_type="wood",
            resonance=["NATURAL"],
            tier=MagicTier.LESSER
        )
        
        materials["silver"] = CraftingMaterial(
            id="silver",
            name="Silver",
            description="A metal with natural magical conductivity.",
            rarity="common",
            material_type="metal",
            resonance=["ARCANE", "DIVINE"],
            tier=MagicTier.LESSER
        )
        
        materials["gold"] = CraftingMaterial(
            id="gold",
            name="Gold",
            description="A precious metal that stores magical energy efficiently.",
            rarity="uncommon",
            material_type="metal",
            resonance=["ARCANE"],
            tier=MagicTier.MODERATE
        )
        
        materials["platinum"] = CraftingMaterial(
            id="platinum",
            name="Platinum",
            description="A rare metal with excellent magical properties.",
            rarity="rare",
            material_type="metal",
            resonance=["ARCANE", "MIND"],
            tier=MagicTier.GREATER
        )
        
        materials["pure_water"] = CraftingMaterial(
            id="pure_water",
            name="Pure Water",
            description="Water free of impurities, ideal as a potion base.",
            rarity="common",
            material_type="liquid",
            resonance=["WATER"]
        )
        
        # Magical materials
        materials["mana_crystal"] = CraftingMaterial(
            id="mana_crystal",
            name="Mana Crystal",
            description="A crystal that naturally stores magical energy.",
            rarity="uncommon",
            material_type="crystal",
            magical_properties=["Stores mana", "Enhances magical conductivity"],
            resonance=["ARCANE"],
            tier=MagicTier.MODERATE
        )
        
        materials["fire_essence"] = CraftingMaterial(
            id="fire_essence",
            name="Fire Essence",
            description="The distilled essence of fire magic.",
            rarity="uncommon",
            material_type="essence",
            magical_properties=["Emits heat", "Enhances fire magic"],
            resonance=["FIRE", "ELEMENTAL"],
            tier=MagicTier.MODERATE
        )
        
        materials["mind_crystal"] = CraftingMaterial(
            id="mind_crystal",
            name="Mind Crystal",
            description="A crystal that resonates with mental energies.",
            rarity="uncommon",
            material_type="crystal",
            magical_properties=["Enhances focus", "Protects against mental intrusion"],
            resonance=["MIND"],
            tier=MagicTier.MODERATE
        )
        
        materials["arcane_dust"] = CraftingMaterial(
            id="arcane_dust",
            name="Arcane Dust",
            description="Crystallized arcane energy in powder form.",
            rarity="uncommon",
            material_type="powder",
            magical_properties=["Enhances arcane spells", "Catalyst for enchantments"],
            resonance=["ARCANE"],
            tier=MagicTier.MODERATE
        )
        
        materials["elemental_essence"] = CraftingMaterial(
            id="elemental_essence",
            name="Elemental Essence",
            description="A blend of various elemental energies.",
            rarity="uncommon",
            material_type="essence",
            magical_properties=["Enhances elemental magic", "Changes properties based on environment"],
            resonance=["ELEMENTAL"],
            tier=MagicTier.MODERATE
        )
        
        materials["divine_light"] = CraftingMaterial(
            id="divine_light",
            name="Divine Light",
            description="Captured rays of divine light.",
            rarity="rare",
            material_type="essence",
            magical_properties=["Purifies", "Enhances divine magic", "Weakens undead"],
            resonance=["DIVINE", "LIGHT"],
            tier=MagicTier.GREATER
        )
        
        materials["shadow_residue"] = CraftingMaterial(
            id="shadow_residue",
            name="Shadow Residue",
            description="Condensed magical darkness.",
            rarity="rare",
            material_type="essence",
            magical_properties=["Conceals", "Enhances shadow magic"],
            resonance=["SHADOW", "DARKNESS"],
            tier=MagicTier.GREATER
        )
        
        materials["blood_essence"] = CraftingMaterial(
            id="blood_essence",
            name="Blood Essence",
            description="Magically preserved blood with powerful properties.",
            rarity="rare",
            material_type="essence",
            magical_properties=["Life force manipulation", "Enhances blood magic"],
            resonance=["BLOOD"],
            tier=MagicTier.GREATER
        )
        
        materials["void_fragment"] = CraftingMaterial(
            id="void_fragment",
            name="Void Fragment",
            description="A fragment of the void between realities.",
            rarity="legendary",
            material_type="exotic",
            magical_properties=["Distorts space", "Nullifies magic nearby"],
            resonance=["VOID"],
            tier=MagicTier.MASTER
        )
        
        # Brewing ingredients
        materials["healing_herb"] = CraftingMaterial(
            id="healing_herb",
            name="Healing Herb",
            description="A herb with natural healing properties.",
            rarity="common",
            material_type="herb",
            magical_properties=["Accelerates healing"],
            resonance=["NATURAL", "LIFE"],
            tier=MagicTier.LESSER
        )
        
        materials["clarity_herb"] = CraftingMaterial(
            id="clarity_herb",
            name="Clarity Herb",
            description="A herb that enhances mental clarity.",
            rarity="uncommon",
            material_type="herb",
            magical_properties=["Enhances focus", "Clears mind"],
            resonance=["MIND", "NATURAL"],
            tier=MagicTier.MODERATE
        )
        
        materials["frost_extract"] = CraftingMaterial(
            id="frost_extract",
            name="Frost Extract",
            description="Extract from plants that grow in extreme cold.",
            rarity="uncommon",
            material_type="extract",
            magical_properties=["Lowers temperature", "Resists fire"],
            resonance=["ICE", "ELEMENTAL"],
            tier=MagicTier.MODERATE
        )
        
        materials["ghost_flower"] = CraftingMaterial(
            id="ghost_flower",
            name="Ghost Flower",
            description="A rare flower that grows in haunted places.",
            rarity="rare",
            material_type="herb",
            magical_properties=["Invisibility", "Spirit communication"],
            resonance=["SPIRIT", "SHADOW"],
            tier=MagicTier.GREATER
        )
        
        return materials
    
    def get_enchantment_recipes(self, character_domains: List[Domain]) -> List[Dict[str, Any]]:
        """
        Get available enchantment recipes for a character with the given domains.
        
        Args:
            character_domains: List of magical domains the character has access to
            
        Returns:
            List of enchantment recipe details
        """
        # Create a mock magic user for checking recipe requirements
        mock_user = MagicUser(
            id="mock_user",
            name="Mock User",
            level=10,  # High level to focus on domain requirements
            primary_domains=character_domains[:1] if character_domains else [],
            secondary_domains=character_domains[1:] if len(character_domains) > 1 else []
        )
        
        # Get all available materials for testing
        all_materials = {material_id: 999 for material_id in self.materials_database.keys()}
        
        # Get available enchantments
        return self.enchanter.get_available_enchantments(mock_user, "any", all_materials)
    
    def get_crafting_recipes(self, character_domains: List[Domain]) -> List[Dict[str, Any]]:
        """
        Get available crafting recipes for a character with the given domains.
        
        Args:
            character_domains: List of magical domains the character has access to
            
        Returns:
            List of crafting recipe details
        """
        # Create a mock magic user for checking recipe requirements
        mock_user = MagicUser(
            id="mock_user",
            name="Mock User",
            level=10,  # High level to focus on domain requirements
            mana_current=999,  # High mana to focus on domain requirements
            primary_domains=character_domains[:1] if character_domains else [],
            secondary_domains=character_domains[1:] if len(character_domains) > 1 else []
        )
        
        # Get all available materials for testing
        all_materials = {material_id: 999 for material_id in self.materials_database.keys()}
        
        # Get available recipes
        return self.crafter.get_available_recipes(mock_user, all_materials)
    
    def get_potion_recipes(self, character_domains: List[Domain]) -> List[Dict[str, Any]]:
        """
        Get available potion recipes for a character with the given domains.
        
        Args:
            character_domains: List of magical domains the character has access to
            
        Returns:
            List of potion recipe details
        """
        # Create a mock magic user for checking recipe requirements
        mock_user = MagicUser(
            id="mock_user",
            name="Mock User",
            level=10,  # High level to focus on domain requirements
            mana_current=999,  # High mana to focus on domain requirements
            primary_domains=character_domains[:1] if character_domains else [],
            secondary_domains=character_domains[1:] if len(character_domains) > 1 else []
        )
        
        # Get all available materials for testing
        all_materials = {material_id: 999 for material_id in self.materials_database.keys()}
        
        # Get available recipes
        return self.brewer.get_available_recipes(mock_user, all_materials)
    
    def get_all_materials(self) -> List[Dict[str, Any]]:
        """
        Get all available crafting materials.
        
        Returns:
            List of material details
        """
        return [material.to_dict() for material in self.materials_database.values()]
    
    def perform_enchantment(
        self,
        magic_user: MagicUser,
        character_domains: List[Domain],
        item_id: str,
        item_type: str,
        enchantment_id: str,
        available_materials: Dict[str, int],
        location_magic_profile: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Perform an enchantment on an item.
        
        Args:
            magic_user: The magic user performing the enchantment
            character_domains: List of magical domains the character has access to
            item_id: ID of the item to enchant
            item_type: Type of the item (weapon, armor, etc.)
            enchantment_id: ID of the enchantment to apply
            available_materials: Dictionary of material_id -> quantity
            location_magic_profile: Optional magical profile of the location
            
        Returns:
            Dictionary with the result of the enchantment
        """
        # Ensure the magic user has the character domains
        magic_user.primary_domains = character_domains[:1] if character_domains else []
        magic_user.secondary_domains = character_domains[1:] if len(character_domains) > 1 else []
        
        return self.enchanter.enchant_item(
            magic_user,
            item_id,
            item_type,
            enchantment_id,
            available_materials,
            location_magic_profile
        )
    
    def craft_item(
        self,
        magic_user: MagicUser,
        character_domains: List[Domain],
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic_profile: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Craft a magical item.
        
        Args:
            magic_user: The magic user performing the crafting
            character_domains: List of magical domains the character has access to
            recipe_id: ID of the crafting recipe to use
            available_materials: Dictionary of material_id -> quantity
            location_magic_profile: Optional magical profile of the location
            
        Returns:
            Dictionary with the result of the crafting
        """
        # Ensure the magic user has the character domains
        magic_user.primary_domains = character_domains[:1] if character_domains else []
        magic_user.secondary_domains = character_domains[1:] if len(character_domains) > 1 else []
        
        return self.crafter.craft_item(
            magic_user,
            recipe_id,
            available_materials,
            location_magic_profile
        )
    
    def brew_potion(
        self,
        magic_user: MagicUser,
        character_domains: List[Domain],
        recipe_id: str,
        available_materials: Dict[str, int],
        location_magic_profile: Optional[LocationMagicProfile] = None
    ) -> Dict[str, Any]:
        """
        Brew a magical potion.
        
        Args:
            magic_user: The magic user performing the brewing
            character_domains: List of magical domains the character has access to
            recipe_id: ID of the potion recipe to use
            available_materials: Dictionary of material_id -> quantity
            location_magic_profile: Optional magical profile of the location
            
        Returns:
            Dictionary with the result of the brewing
        """
        # Ensure the magic user has the character domains
        magic_user.primary_domains = character_domains[:1] if character_domains else []
        magic_user.secondary_domains = character_domains[1:] if len(character_domains) > 1 else []
        
        return self.brewer.brew_potion(
            magic_user,
            recipe_id,
            available_materials,
            location_magic_profile
        )