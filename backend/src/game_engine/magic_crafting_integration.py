"""
Magic System Integration with Crafting

This module integrates the magic system with the crafting system,
allowing for the creation of magical items, potions, and enchantments.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import random
import uuid

from .magic_system import (
    MagicSystem, MagicUser, ItemMagicProfile, Enchantment,
    MagicTier, MagicSource, EffectType, TargetType, DomainRequirement,
    Domain, DamageType, MagicalEffect, RecipeIngredient
)


class MagicalMaterial:
    """Represents a magical material used in crafting"""
    
    def __init__(self, 
                 id: str,
                 name: str,
                 description: str,
                 rarity: str,
                 primary_aspect: Optional[DamageType] = None,
                 secondary_aspects: List[DamageType] = None,
                 ley_energy_capacity: int = 0,
                 corruption_level: int = 0,
                 special_properties: List[str] = None):
        """
        Initialize a magical material.
        
        Args:
            id: Unique identifier
            name: Material name
            description: Material description
            rarity: Rarity level (Common, Uncommon, Rare, Very Rare, Legendary)
            primary_aspect: Primary magical aspect
            secondary_aspects: Secondary magical aspects
            ley_energy_capacity: Amount of ley energy it can store
            corruption_level: Level of magical corruption (0-100)
            special_properties: Special properties of the material
        """
        self.id = id
        self.name = name
        self.description = description
        self.rarity = rarity
        self.primary_aspect = primary_aspect
        self.secondary_aspects = secondary_aspects or []
        self.ley_energy_capacity = ley_energy_capacity
        self.corruption_level = corruption_level
        self.special_properties = special_properties or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "rarity": self.rarity,
            "primary_aspect": self.primary_aspect.name if self.primary_aspect else None,
            "secondary_aspects": [aspect.name for aspect in self.secondary_aspects],
            "ley_energy_capacity": self.ley_energy_capacity,
            "corruption_level": self.corruption_level,
            "special_properties": self.special_properties
        }


class EnchantingRecipe:
    """Recipe for creating enchanted items"""
    
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 enchantment_id: str,
                 tier: MagicTier,
                 required_materials: List[RecipeIngredient],
                 domain_requirements: List[DomainRequirement],
                 mana_cost: int,
                 ley_energy_cost: int,
                 crafting_time_minutes: int,
                 difficulty: int,
                 requires_ritual: bool = False,
                 requires_magical_location: bool = False,
                 lore_notes: Optional[str] = None):
        """
        Initialize an enchanting recipe.
        
        Args:
            id: Unique identifier
            name: Recipe name
            description: Recipe description
            enchantment_id: ID of the enchantment this recipe creates
            tier: Magic tier of the enchantment
            required_materials: Materials required for the enchantment
            domain_requirements: Domain requirements for the crafter
            mana_cost: Mana cost to perform the enchantment
            ley_energy_cost: Ley energy cost to perform the enchantment
            crafting_time_minutes: Time required to complete the enchantment
            difficulty: Difficulty level of the enchanting process
            requires_ritual: Whether a ritual is required
            requires_magical_location: Whether a magical location is required
            lore_notes: Lore notes about the recipe
        """
        self.id = id
        self.name = name
        self.description = description
        self.enchantment_id = enchantment_id
        self.tier = tier
        self.required_materials = required_materials
        self.domain_requirements = domain_requirements
        self.mana_cost = mana_cost
        self.ley_energy_cost = ley_energy_cost
        self.crafting_time_minutes = crafting_time_minutes
        self.difficulty = difficulty
        self.requires_ritual = requires_ritual
        self.requires_magical_location = requires_magical_location
        self.lore_notes = lore_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enchantment_id": self.enchantment_id,
            "tier": self.tier.name,
            "required_materials": [
                {
                    "name": material.name,
                    "quantity": material.quantity,
                    "consumed": material.consumed,
                    "description": material.description
                }
                for material in self.required_materials
            ],
            "domain_requirements": [
                {
                    "domain": req.domain.name,
                    "minimum_value": req.minimum_value
                }
                for req in self.domain_requirements
            ],
            "mana_cost": self.mana_cost,
            "ley_energy_cost": self.ley_energy_cost,
            "crafting_time_minutes": self.crafting_time_minutes,
            "difficulty": self.difficulty,
            "requires_ritual": self.requires_ritual,
            "requires_magical_location": self.requires_magical_location,
            "lore_notes": self.lore_notes
        }


class PotionRecipe:
    """Recipe for creating magical potions"""
    
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 effects: List[MagicalEffect],
                 required_materials: List[RecipeIngredient],
                 domain_requirements: List[DomainRequirement],
                 brewing_time_minutes: int,
                 difficulty: int,
                 produces_quantity: int = 1,
                 potency: int = 1,
                 duration_minutes: int = 30,
                 side_effects: List[str] = None,
                 lore_notes: Optional[str] = None):
        """
        Initialize a potion recipe.
        
        Args:
            id: Unique identifier
            name: Recipe name
            description: Recipe description
            effects: Magical effects the potion produces
            required_materials: Materials required for the potion
            domain_requirements: Domain requirements for the brewer
            brewing_time_minutes: Time required to brew the potion
            difficulty: Difficulty level of the brewing process
            produces_quantity: Number of potions produced
            potency: Potency level of the potion (1-5)
            duration_minutes: Duration of the potion's effects
            side_effects: Potential side effects
            lore_notes: Lore notes about the recipe
        """
        self.id = id
        self.name = name
        self.description = description
        self.effects = effects
        self.required_materials = required_materials
        self.domain_requirements = domain_requirements
        self.brewing_time_minutes = brewing_time_minutes
        self.difficulty = difficulty
        self.produces_quantity = produces_quantity
        self.potency = potency
        self.duration_minutes = duration_minutes
        self.side_effects = side_effects or []
        self.lore_notes = lore_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "effects": [
                {
                    "effect_type": effect.effect_type.name,
                    "description": effect.description_template,
                    "magnitude": str(effect.magnitude) if not isinstance(effect.magnitude, (int, float)) else effect.magnitude,
                    "target_type": effect.target_type.name,
                    "damage_type": effect.damage_type.name if effect.damage_type else None,
                    "duration_seconds": effect.duration_seconds
                }
                for effect in self.effects
            ],
            "required_materials": [
                {
                    "name": material.name,
                    "quantity": material.quantity,
                    "consumed": material.consumed,
                    "description": material.description
                }
                for material in self.required_materials
            ],
            "domain_requirements": [
                {
                    "domain": req.domain.name,
                    "minimum_value": req.minimum_value
                }
                for req in self.domain_requirements
            ],
            "brewing_time_minutes": self.brewing_time_minutes,
            "difficulty": self.difficulty,
            "produces_quantity": self.produces_quantity,
            "potency": self.potency,
            "duration_minutes": self.duration_minutes,
            "side_effects": self.side_effects,
            "lore_notes": self.lore_notes
        }


class RuneRecipe:
    """Recipe for creating magical runes"""
    
    def __init__(self,
                 id: str,
                 name: str,
                 description: str,
                 effects: List[MagicalEffect],
                 required_materials: List[RecipeIngredient],
                 domain_requirements: List[DomainRequirement],
                 inscription_time_minutes: int,
                 difficulty: int,
                 activation_type: str,
                 charges: Optional[int] = None,
                 target_surfaces: List[str] = None,
                 lore_notes: Optional[str] = None):
        """
        Initialize a rune recipe.
        
        Args:
            id: Unique identifier
            name: Recipe name
            description: Recipe description
            effects: Magical effects the rune produces
            required_materials: Materials required for the rune
            domain_requirements: Domain requirements for the inscriber
            inscription_time_minutes: Time required to inscribe the rune
            difficulty: Difficulty level of the inscription process
            activation_type: How the rune is activated (touch, proximity, command, etc.)
            charges: Number of charges (None for permanent)
            target_surfaces: Types of surfaces the rune can be inscribed on
            lore_notes: Lore notes about the recipe
        """
        self.id = id
        self.name = name
        self.description = description
        self.effects = effects
        self.required_materials = required_materials
        self.domain_requirements = domain_requirements
        self.inscription_time_minutes = inscription_time_minutes
        self.difficulty = difficulty
        self.activation_type = activation_type
        self.charges = charges
        self.target_surfaces = target_surfaces or ["stone", "wood", "metal"]
        self.lore_notes = lore_notes
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "effects": [
                {
                    "effect_type": effect.effect_type.name,
                    "description": effect.description_template,
                    "magnitude": str(effect.magnitude) if not isinstance(effect.magnitude, (int, float)) else effect.magnitude,
                    "target_type": effect.target_type.name,
                    "damage_type": effect.damage_type.name if effect.damage_type else None,
                    "duration_seconds": effect.duration_seconds
                }
                for effect in self.effects
            ],
            "required_materials": [
                {
                    "name": material.name,
                    "quantity": material.quantity,
                    "consumed": material.consumed,
                    "description": material.description
                }
                for material in self.required_materials
            ],
            "domain_requirements": [
                {
                    "domain": req.domain.name,
                    "minimum_value": req.minimum_value
                }
                for req in self.domain_requirements
            ],
            "inscription_time_minutes": self.inscription_time_minutes,
            "difficulty": self.difficulty,
            "activation_type": self.activation_type,
            "charges": self.charges,
            "target_surfaces": self.target_surfaces,
            "lore_notes": self.lore_notes
        }


class MagicalCraftingService:
    """
    Service for managing magical crafting.
    
    This class handles enchanting items, brewing potions, and creating magical devices.
    """
    
    def __init__(self, magic_system: MagicSystem):
        """Initialize the magical crafting service"""
        self.magic_system = magic_system
        
        # Initialize repositories
        self.materials: Dict[str, MagicalMaterial] = {}
        self.enchanting_recipes: Dict[str, EnchantingRecipe] = {}
        self.potion_recipes: Dict[str, PotionRecipe] = {}
        self.rune_recipes: Dict[str, RuneRecipe] = {}
        
        # Register basic content
        self._register_basic_magical_materials()
        self._register_basic_enchanting_recipes()
        self._register_basic_potion_recipes()
        self._register_basic_rune_recipes()
    
    def _register_basic_magical_materials(self):
        """Register basic magical materials"""
        # Ley Crystal
        ley_crystal = MagicalMaterial(
            id="material_ley_crystal",
            name="Ley Crystal",
            description="A crystal that has naturally formed along leylines, storing magical energy.",
            rarity="Uncommon",
            ley_energy_capacity=10,
            special_properties=["Stores ley energy", "Amplifies magical effects"]
        )
        self.materials[ley_crystal.id] = ley_crystal
        
        # Crimson Residue
        crimson_residue = MagicalMaterial(
            id="material_crimson_residue",
            name="Crimson Residue",
            description="A crystallized remnant of the Crimson Dissonance, crackling with unstable energy.",
            rarity="Rare",
            primary_aspect=DamageType.FIRE,
            secondary_aspects=[DamageType.ARCANE],
            ley_energy_capacity=5,
            corruption_level=30,
            special_properties=["Amplifies fire magic", "Chance of backlash", "Corrupting influence"]
        )
        self.materials[crimson_residue.id] = crimson_residue
        
        # Spiritbloom
        spiritbloom = MagicalMaterial(
            id="material_spiritbloom",
            name="Spiritbloom",
            description="A rare flower that only grows in areas with strong spiritual energy.",
            rarity="Uncommon",
            primary_aspect=DamageType.SPIRITUAL,
            ley_energy_capacity=3,
            special_properties=["Enhances spirit communication", "Preserves magical essence"]
        )
        self.materials[spiritbloom.id] = spiritbloom
        
        # Void Shard
        void_shard = MagicalMaterial(
            id="material_void_shard",
            name="Void Shard",
            description="A fragment of pure darkness that seems to absorb light and magic.",
            rarity="Rare",
            primary_aspect=DamageType.DARKNESS,
            secondary_aspects=[DamageType.NECROTIC],
            ley_energy_capacity=8,
            corruption_level=15,
            special_properties=["Absorbs magical energy", "Weakens nearby magical effects"]
        )
        self.materials[void_shard.id] = void_shard
        
        # Stormforge Iron
        stormforge_iron = MagicalMaterial(
            id="material_stormforge_iron",
            name="Stormforge Iron",
            description="Iron that has been struck by lightning multiple times, imbuing it with electrical properties.",
            rarity="Uncommon",
            primary_aspect=DamageType.LIGHTNING,
            secondary_aspects=[DamageType.AIR],
            special_properties=["Conducts magical energy", "Retains enchantments well"]
        )
        self.materials[stormforge_iron.id] = stormforge_iron
    
    def _register_basic_enchanting_recipes(self):
        """Register basic enchanting recipes"""
        # Flaming Weapon Enchantment Recipe
        flaming_weapon_recipe = EnchantingRecipe(
            id="recipe_flaming_weapon",
            name="Enchantment of Burning Wrath",
            description="A recipe for imbuing a weapon with burning flames that ignite enemies.",
            enchantment_id="enchant_flaming_weapon",
            tier=MagicTier.MANA_INFUSION,
            required_materials=[
                RecipeIngredient(name="material_ley_crystal", quantity=1, consumed=True),
                RecipeIngredient(name="material_crimson_residue", quantity=2, consumed=True),
                RecipeIngredient(name="Charcoal", quantity=5, consumed=True),
                RecipeIngredient(name="Weapon", quantity=1, consumed=False, description="The weapon to enchant")
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=3),
                DomainRequirement(domain=Domain.FIRE, minimum_value=2)
            ],
            mana_cost=15,
            ley_energy_cost=5,
            crafting_time_minutes=60,
            difficulty=4,
            requires_ritual=False,
            requires_magical_location=False,
            lore_notes="A common enchantment adapted from battle magic used during the Crimson Dissonance."
        )
        self.enchanting_recipes[flaming_weapon_recipe.id] = flaming_weapon_recipe
        
        # Protective Ward Enchantment Recipe
        protective_ward_recipe = EnchantingRecipe(
            id="recipe_protective_ward",
            name="Enchantment of the Stalwart Guardian",
            description="A recipe for creating a magical barrier on armor that occasionally absorbs damage.",
            enchantment_id="enchant_protective_ward",
            tier=MagicTier.MANA_INFUSION,
            required_materials=[
                RecipeIngredient(name="material_ley_crystal", quantity=2, consumed=True),
                RecipeIngredient(name="Silver dust", quantity=3, consumed=True),
                RecipeIngredient(name="material_spiritbloom", quantity=1, consumed=True),
                RecipeIngredient(name="Armor", quantity=1, consumed=False, description="The armor to enchant")
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=3),
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=2)
            ],
            mana_cost=20,
            ley_energy_cost=8,
            crafting_time_minutes=90,
            difficulty=5,
            requires_ritual=False,
            requires_magical_location=False,
            lore_notes="An enchantment developed by the defensive specialists of the Crimson Accord."
        )
        self.enchanting_recipes[protective_ward_recipe.id] = protective_ward_recipe
        
        # Swift Step Enchantment Recipe
        swift_step_recipe = EnchantingRecipe(
            id="recipe_swift_step",
            name="Enchantment of the Zephyr's Grace",
            description="A recipe for enchanting footwear with magical speed and agility.",
            enchantment_id="enchant_swift_step",
            tier=MagicTier.MANA_INFUSION,
            required_materials=[
                RecipeIngredient(name="material_ley_crystal", quantity=1, consumed=True),
                RecipeIngredient(name="Falcon feather", quantity=4, consumed=True),
                RecipeIngredient(name="Quicksilver", quantity=2, consumed=True),
                RecipeIngredient(name="Boots", quantity=1, consumed=False, description="The footwear to enchant")
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=2),
                DomainRequirement(domain=Domain.AIR, minimum_value=2)
            ],
            mana_cost=10,
            ley_energy_cost=5,
            crafting_time_minutes=45,
            difficulty=3,
            requires_ritual=False,
            requires_magical_location=False,
            lore_notes="An enchantment favored by scouts and messengers during the days of the Crimson Accord."
        )
        self.enchanting_recipes[swift_step_recipe.id] = swift_step_recipe
    
    def _register_basic_potion_recipes(self):
        """Register basic potion recipes"""
        # Healing Potion Recipe
        healing_potion_recipe = PotionRecipe(
            id="recipe_healing_potion",
            name="Potion of Vitality",
            description="A potion that rapidly heals wounds and restores vitality.",
            effects=[
                MagicalEffect(
                    effect_type=EffectType.HEAL,
                    description_template="A wave of healing energy flows through your body",
                    magnitude=15,
                    target_type=TargetType.SELF,
                    duration_seconds=10
                )
            ],
            required_materials=[
                RecipeIngredient(name="material_spiritbloom", quantity=1, consumed=True),
                RecipeIngredient(name="Red mushroom", quantity=3, consumed=True),
                RecipeIngredient(name="Honey", quantity=2, consumed=True),
                RecipeIngredient(name="Spring water", quantity=1, consumed=True)
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=2),
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=1)
            ],
            brewing_time_minutes=30,
            difficulty=2,
            produces_quantity=1,
            potency=2,
            duration_minutes=0,  # Instant effect
            side_effects=["Slight drowsiness"],
            lore_notes="One of the most common and valuable potions, used extensively during the Crimson Dissonance."
        )
        self.potion_recipes[healing_potion_recipe.id] = healing_potion_recipe
        
        # Mana Restoration Potion Recipe
        mana_potion_recipe = PotionRecipe(
            id="recipe_mana_potion",
            name="Potion of Arcane Restoration",
            description="A potion that restores magical energy to the Mana Heart.",
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="Magical energy surges through your Mana Heart",
                    magnitude="restore_mana_20",
                    target_type=TargetType.SELF,
                    duration_seconds=5
                )
            ],
            required_materials=[
                RecipeIngredient(name="material_ley_crystal", quantity=1, consumed=True),
                RecipeIngredient(name="Blue lotus", quantity=2, consumed=True),
                RecipeIngredient(name="Distilled moonlight", quantity=1, consumed=True),
                RecipeIngredient(name="Pure water", quantity=1, consumed=True)
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=2),
                DomainRequirement(domain=Domain.MIND, minimum_value=2)
            ],
            brewing_time_minutes=45,
            difficulty=3,
            produces_quantity=1,
            potency=2,
            duration_minutes=0,  # Instant effect
            side_effects=["Temporary heightened sensitivity to magic"],
            lore_notes="A staple potion for mages across the world, especially those who rely heavily on their Mana Heart."
        )
        self.potion_recipes[mana_potion_recipe.id] = mana_potion_recipe
        
        # Fire Resistance Potion Recipe
        fire_resistance_recipe = PotionRecipe(
            id="recipe_fire_resistance",
            name="Potion of Flame Ward",
            description="A potion that grants temporary resistance to fire and heat.",
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="Your skin takes on a reddish hue as it becomes resistant to heat",
                    magnitude="fire_resistance_50_percent",
                    target_type=TargetType.SELF,
                    duration_seconds=1800  # 30 minutes
                )
            ],
            required_materials=[
                RecipeIngredient(name="Salamander scales", quantity=2, consumed=True),
                RecipeIngredient(name="material_crimson_residue", quantity=1, consumed=True),
                RecipeIngredient(name="Ash bark", quantity=3, consumed=True),
                RecipeIngredient(name="Alchemical base", quantity=1, consumed=True)
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=3),
                DomainRequirement(domain=Domain.FIRE, minimum_value=1)
            ],
            brewing_time_minutes=60,
            difficulty=4,
            produces_quantity=1,
            potency=3,
            duration_minutes=30,
            side_effects=["Slightly elevated body temperature", "Occasional steam when sweating"],
            lore_notes="Developed during the Crimson Dissonance to protect against fire-based war magic."
        )
        self.potion_recipes[fire_resistance_recipe.id] = fire_resistance_recipe
    
    def _register_basic_rune_recipes(self):
        """Register basic rune recipes"""
        # Warding Rune Recipe
        warding_rune_recipe = RuneRecipe(
            id="recipe_warding_rune",
            name="Rune of Protection",
            description="A rune that creates a protective barrier when activated.",
            effects=[
                MagicalEffect(
                    effect_type=EffectType.WARD,
                    description_template="A glowing barrier springs up, blocking passage",
                    magnitude="block_passage",
                    target_type=TargetType.AREA_ALL,
                    duration_seconds=300  # 5 minutes
                )
            ],
            required_materials=[
                RecipeIngredient(name="material_ley_crystal", quantity=1, consumed=True),
                RecipeIngredient(name="Silver dust", quantity=2, consumed=True),
                RecipeIngredient(name="Protective ink", quantity=1, consumed=True)
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=3),
                DomainRequirement(domain=Domain.MIND, minimum_value=2),
                DomainRequirement(domain=Domain.SPIRIT, minimum_value=1)
            ],
            inscription_time_minutes=20,
            difficulty=3,
            activation_type="proximity",
            charges=3,
            target_surfaces=["stone", "wood", "metal", "cloth"],
            lore_notes="A common protective rune used to secure entrances and valuable items."
        )
        self.rune_recipes[warding_rune_recipe.id] = warding_rune_recipe
        
        # Explosive Rune Recipe
        explosive_rune_recipe = RuneRecipe(
            id="recipe_explosive_rune",
            name="Rune of Detonation",
            description="A rune that explodes with magical force when triggered.",
            effects=[
                MagicalEffect(
                    effect_type=EffectType.DAMAGE,
                    description_template="The rune explodes in a blast of magical energy",
                    magnitude=20,
                    target_type=TargetType.AREA_ENEMIES,
                    damage_type=DamageType.FIRE,
                    duration_seconds=0  # Instant
                )
            ],
            required_materials=[
                RecipeIngredient(name="material_crimson_residue", quantity=2, consumed=True),
                RecipeIngredient(name="Volatile essence", quantity=1, consumed=True),
                RecipeIngredient(name="Charcoal", quantity=3, consumed=True),
                RecipeIngredient(name="Binding ink", quantity=1, consumed=True)
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=4),
                DomainRequirement(domain=Domain.FIRE, minimum_value=2)
            ],
            inscription_time_minutes=30,
            difficulty=5,
            activation_type="trigger",
            charges=1,
            target_surfaces=["stone", "wood", "metal"],
            lore_notes="A dangerous remnant of war magic from the Crimson Dissonance, now used primarily for mining or as a last resort in defense."
        )
        self.rune_recipes[explosive_rune_recipe.id] = explosive_rune_recipe
        
        # Illumination Rune Recipe
        illumination_rune_recipe = RuneRecipe(
            id="recipe_illumination_rune",
            name="Rune of Illumination",
            description="A rune that emits magical light when activated.",
            effects=[
                MagicalEffect(
                    effect_type=EffectType.BUFF_STAT,
                    description_template="The rune glows with bright light, illuminating the area",
                    magnitude="bright_light_20ft_radius",
                    target_type=TargetType.ENVIRONMENT,
                    damage_type=DamageType.LIGHT,
                    duration_seconds=3600  # 1 hour
                )
            ],
            required_materials=[
                RecipeIngredient(name="Glowstone dust", quantity=2, consumed=True),
                RecipeIngredient(name="Light-catching crystal", quantity=1, consumed=True),
                RecipeIngredient(name="Phosphorescent ink", quantity=1, consumed=True)
            ],
            domain_requirements=[
                DomainRequirement(domain=Domain.CRAFT, minimum_value=2),
                DomainRequirement(domain=Domain.LIGHT, minimum_value=1)
            ],
            inscription_time_minutes=15,
            difficulty=2,
            activation_type="command",
            charges=10,
            target_surfaces=["stone", "wood", "metal", "glass"],
            lore_notes="A common utility rune used in homes, academic institutions, and for exploration."
        )
        self.rune_recipes[illumination_rune_recipe.id] = illumination_rune_recipe
    
    def get_material(self, material_id: str) -> Optional[MagicalMaterial]:
        """Get a magical material by ID"""
        return self.materials.get(material_id)
    
    def get_enchanting_recipe(self, recipe_id: str) -> Optional[EnchantingRecipe]:
        """Get an enchanting recipe by ID"""
        return self.enchanting_recipes.get(recipe_id)
    
    def get_potion_recipe(self, recipe_id: str) -> Optional[PotionRecipe]:
        """Get a potion recipe by ID"""
        return self.potion_recipes.get(recipe_id)
    
    def get_rune_recipe(self, recipe_id: str) -> Optional[RuneRecipe]:
        """Get a rune recipe by ID"""
        return self.rune_recipes.get(recipe_id)
    
    def list_all_materials(self) -> List[Dict[str, Any]]:
        """List all magical materials"""
        return [material.to_dict() for material in self.materials.values()]
    
    def list_all_enchanting_recipes(self) -> List[Dict[str, Any]]:
        """List all enchanting recipes"""
        return [recipe.to_dict() for recipe in self.enchanting_recipes.values()]
    
    def list_all_potion_recipes(self) -> List[Dict[str, Any]]:
        """List all potion recipes"""
        return [recipe.to_dict() for recipe in self.potion_recipes.values()]
    
    def list_all_rune_recipes(self) -> List[Dict[str, Any]]:
        """List all rune recipes"""
        return [recipe.to_dict() for recipe in self.rune_recipes.values()]
    
    def enchant_item(self, 
                    character_id: str,
                    character_magic: MagicUser,
                    recipe_id: str,
                    item_id: str,
                    available_materials: Dict[str, int],
                    character_domains: Dict[Domain, int]) -> Dict[str, Any]:
        """
        Attempt to enchant an item using a recipe.
        
        Args:
            character_id: ID of the enchanter
            character_magic: Magic profile of the enchanter
            recipe_id: ID of the enchanting recipe
            item_id: ID of the item to enchant
            available_materials: Dictionary of material IDs to quantities available
            character_domains: Character's domain values
            
        Returns:
            Result dictionary with enchantment details
        """
        # Get the recipe
        recipe = self.get_enchanting_recipe(recipe_id)
        if not recipe:
            return {
                "success": False,
                "message": f"Recipe {recipe_id} not found"
            }
        
        # Check if the character has the required domains
        for req in recipe.domain_requirements:
            domain_value = character_domains.get(req.domain, 0)
            if domain_value < req.minimum_value:
                return {
                    "success": False,
                    "message": f"Insufficient {req.domain.name} domain ({domain_value}/{req.minimum_value})"
                }
        
        # Check if the character has the required materials
        for material in recipe.required_materials:
            available = available_materials.get(material.name, 0)
            if available < material.quantity:
                return {
                    "success": False,
                    "message": f"Insufficient {material.name} ({available}/{material.quantity})"
                }
        
        # Check magical requirements
        if recipe.mana_cost and (not character_magic.has_mana_heart or character_magic.mana_current < recipe.mana_cost):
            return {
                "success": False,
                "message": f"Insufficient mana ({character_magic.mana_current}/{recipe.mana_cost})"
            }
        
        if recipe.ley_energy_cost and character_magic.current_ley_energy < recipe.ley_energy_cost:
            return {
                "success": False,
                "message": f"Insufficient ley energy ({character_magic.current_ley_energy}/{recipe.ley_energy_cost})"
            }
        
        # Get the enchantment
        enchantment = self.magic_system.enchantment_service.get_enchantment(recipe.enchantment_id)
        if not enchantment:
            return {
                "success": False,
                "message": f"Enchantment {recipe.enchantment_id} not found"
            }
        
        # Create an item magic profile
        item_magic = ItemMagicProfile(
            is_enchanted=True,
            enchantment_id=recipe.enchantment_id,
            is_relic=False,
            attunement_required=False,
            cursed_or_corrupted=False
        )
        
        # Consume resources
        if recipe.mana_cost:
            character_magic.use_mana(recipe.mana_cost)
        
        if recipe.ley_energy_cost:
            character_magic.use_ley_energy(recipe.ley_energy_cost)
        
        # In a real implementation, we would actually consume the materials from inventory here
        
        # Calculate success chance
        base_chance = 0.5  # 50% base chance
        
        # Domain bonuses
        domain_bonus = 0
        for req in recipe.domain_requirements:
            domain_value = character_domains.get(req.domain, 0)
            domain_bonus += (domain_value - req.minimum_value) * 0.05  # 5% per point above minimum
        
        # Skill bonus would be added here in a real implementation
        
        # Difficulty penalty
        difficulty_penalty = recipe.difficulty * 0.05  # 5% per difficulty level
        
        # Calculate final chance
        success_chance = min(0.95, max(0.05, base_chance + domain_bonus - difficulty_penalty))
        
        # Determine success
        is_success = random.random() <= success_chance
        
        if is_success:
            # Apply the enchantment to the item
            result = {
                "success": True,
                "message": f"Successfully enchanted item with {enchantment.name}",
                "item_id": item_id,
                "enchantment": {
                    "id": enchantment.id,
                    "name": enchantment.name,
                    "description": enchantment.description,
                    "tier": enchantment.tier.name,
                    "effects": [e.effect_type.name for e in enchantment.applied_effects],
                    "passive_or_triggered": enchantment.passive_or_triggered
                },
                "mana_used": recipe.mana_cost,
                "ley_energy_used": recipe.ley_energy_cost,
                "mana_remaining": character_magic.mana_current,
                "ley_energy_remaining": character_magic.current_ley_energy,
                "item_magic_profile": {
                    "is_enchanted": item_magic.is_enchanted,
                    "enchantment_id": item_magic.enchantment_id,
                    "is_relic": item_magic.is_relic
                }
            }
        else:
            # Enchantment failed
            # In a real implementation, we might have consequences for failure
            result = {
                "success": False,
                "message": "The enchantment failed",
                "mana_used": recipe.mana_cost,
                "ley_energy_used": recipe.ley_energy_cost,
                "mana_remaining": character_magic.mana_current,
                "ley_energy_remaining": character_magic.current_ley_energy
            }
        
        return result
    
    def brew_potion(self, 
                   character_id: str,
                   character_magic: MagicUser,
                   recipe_id: str,
                   available_materials: Dict[str, int],
                   character_domains: Dict[Domain, int]) -> Dict[str, Any]:
        """
        Attempt to brew a potion using a recipe.
        
        Args:
            character_id: ID of the brewer
            character_magic: Magic profile of the brewer
            recipe_id: ID of the potion recipe
            available_materials: Dictionary of material IDs to quantities available
            character_domains: Character's domain values
            
        Returns:
            Result dictionary with potion details
        """
        # Get the recipe
        recipe = self.get_potion_recipe(recipe_id)
        if not recipe:
            return {
                "success": False,
                "message": f"Recipe {recipe_id} not found"
            }
        
        # Check if the character has the required domains
        for req in recipe.domain_requirements:
            domain_value = character_domains.get(req.domain, 0)
            if domain_value < req.minimum_value:
                return {
                    "success": False,
                    "message": f"Insufficient {req.domain.name} domain ({domain_value}/{req.minimum_value})"
                }
        
        # Check if the character has the required materials
        for material in recipe.required_materials:
            available = available_materials.get(material.name, 0)
            if available < material.quantity:
                return {
                    "success": False,
                    "message": f"Insufficient {material.name} ({available}/{material.quantity})"
                }
        
        # Calculate success chance
        base_chance = 0.6  # 60% base chance
        
        # Domain bonuses
        domain_bonus = 0
        for req in recipe.domain_requirements:
            domain_value = character_domains.get(req.domain, 0)
            domain_bonus += (domain_value - req.minimum_value) * 0.05  # 5% per point above minimum
        
        # Skill bonus would be added here in a real implementation
        
        # Difficulty penalty
        difficulty_penalty = recipe.difficulty * 0.05  # 5% per difficulty level
        
        # Potency modifier
        potency_modifier = (recipe.potency - 1) * 0.05  # 5% penalty per potency level above 1
        
        # Calculate final chance
        success_chance = min(0.95, max(0.05, base_chance + domain_bonus - difficulty_penalty - potency_modifier))
        
        # Determine success
        is_success = random.random() <= success_chance
        
        if is_success:
            # Generate potion data
            potion_id = f"potion_{uuid.uuid4().hex[:8]}"
            
            result = {
                "success": True,
                "message": f"Successfully brewed {recipe.name}",
                "potion_id": potion_id,
                "potion": {
                    "name": recipe.name,
                    "description": recipe.description,
                    "effects": [e.effect_type.name for e in recipe.effects],
                    "potency": recipe.potency,
                    "duration_minutes": recipe.duration_minutes,
                    "side_effects": recipe.side_effects
                },
                "quantity_produced": recipe.produces_quantity
            }
        else:
            # Potion brewing failed
            result = {
                "success": False,
                "message": "The potion brewing failed",
                "wasted_materials": True
            }
        
        return result
    
    def inscribe_rune(self, 
                     character_id: str,
                     character_magic: MagicUser,
                     recipe_id: str,
                     target_surface: str,
                     available_materials: Dict[str, int],
                     character_domains: Dict[Domain, int]) -> Dict[str, Any]:
        """
        Attempt to inscribe a rune using a recipe.
        
        Args:
            character_id: ID of the inscriber
            character_magic: Magic profile of the inscriber
            recipe_id: ID of the rune recipe
            target_surface: Type of surface being inscribed
            available_materials: Dictionary of material IDs to quantities available
            character_domains: Character's domain values
            
        Returns:
            Result dictionary with rune details
        """
        # Get the recipe
        recipe = self.get_rune_recipe(recipe_id)
        if not recipe:
            return {
                "success": False,
                "message": f"Recipe {recipe_id} not found"
            }
        
        # Check if the surface is valid
        if target_surface not in recipe.target_surfaces:
            return {
                "success": False,
                "message": f"Cannot inscribe this rune on {target_surface}"
            }
        
        # Check if the character has the required domains
        for req in recipe.domain_requirements:
            domain_value = character_domains.get(req.domain, 0)
            if domain_value < req.minimum_value:
                return {
                    "success": False,
                    "message": f"Insufficient {req.domain.name} domain ({domain_value}/{req.minimum_value})"
                }
        
        # Check if the character has the required materials
        for material in recipe.required_materials:
            available = available_materials.get(material.name, 0)
            if available < material.quantity:
                return {
                    "success": False,
                    "message": f"Insufficient {material.name} ({available}/{material.quantity})"
                }
        
        # Calculate success chance
        base_chance = 0.55  # 55% base chance
        
        # Domain bonuses
        domain_bonus = 0
        for req in recipe.domain_requirements:
            domain_value = character_domains.get(req.domain, 0)
            domain_bonus += (domain_value - req.minimum_value) * 0.05  # 5% per point above minimum
        
        # Skill bonus would be added here in a real implementation
        
        # Difficulty penalty
        difficulty_penalty = recipe.difficulty * 0.05  # 5% per difficulty level
        
        # Calculate final chance
        success_chance = min(0.95, max(0.05, base_chance + domain_bonus - difficulty_penalty))
        
        # Determine success
        is_success = random.random() <= success_chance
        
        if is_success:
            # Generate rune data
            rune_id = f"rune_{uuid.uuid4().hex[:8]}"
            
            result = {
                "success": True,
                "message": f"Successfully inscribed {recipe.name}",
                "rune_id": rune_id,
                "rune": {
                    "name": recipe.name,
                    "description": recipe.description,
                    "effects": [e.effect_type.name for e in recipe.effects],
                    "activation_type": recipe.activation_type,
                    "charges": recipe.charges,
                    "surface": target_surface
                }
            }
        else:
            # Rune inscription failed
            result = {
                "success": False,
                "message": "The rune inscription failed",
                "wasted_materials": True
            }
        
        return result


# ======================================================================
# Integration with Crafting System
# ======================================================================

class MagicalCraftingIntegration:
    """
    Integration with the crafting system for magical crafting.
    
    This class provides an interface between the magic system and
    the existing crafting system.
    """
    
    def __init__(self, magic_system: MagicSystem, crafting_service: MagicalCraftingService):
        """
        Initialize the magical crafting integration.
        
        Args:
            magic_system: The magic system instance
            crafting_service: The magical crafting service instance
        """
        self.magic_system = magic_system
        self.crafting_service = crafting_service
    
    def register_magical_materials(self, crafting_system: Any) -> None:
        """
        Register magical materials with the existing crafting system.
        
        Args:
            crafting_system: The existing crafting system instance
        """
        # In a real implementation, we would register the magical materials
        # with the existing crafting system here
        pass
    
    def register_magical_recipes(self, crafting_system: Any) -> None:
        """
        Register magical recipes with the existing crafting system.
        
        Args:
            crafting_system: The existing crafting system instance
        """
        # In a real implementation, we would register the magical recipes
        # with the existing crafting system here
        pass
    
    def handle_crafting_result(self, crafting_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the result of a crafting action for magical implications.
        
        Args:
            crafting_result: The result of a crafting action
            
        Returns:
            Enhanced crafting result with magical information
        """
        # In a real implementation, we would process the crafting result
        # and add magical information to it
        return crafting_result


# ======================================================================
# Magic System Factory
# ======================================================================

def create_magical_crafting_services(magic_system: MagicSystem) -> Dict[str, Any]:
    """
    Create and return all magical crafting services.
    
    Args:
        magic_system: The magic system instance
        
    Returns:
        Dictionary containing the magical crafting services
    """
    # Create the magical crafting service
    crafting_service = MagicalCraftingService(magic_system)
    
    # Create the integration with the crafting system
    crafting_integration = MagicalCraftingIntegration(magic_system, crafting_service)
    
    return {
        "crafting_service": crafting_service,
        "crafting_integration": crafting_integration
    }


# Initialize magical crafting services with the existing magic system
from .magic_system import magic_system
magical_crafting = create_magical_crafting_services(magic_system)