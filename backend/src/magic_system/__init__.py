"""
Magic System Package

This package contains all the components of the game's magic system.
Includes magic crafting, enchantment, leylines, and material handling.
"""

# Import core classes and systems for easier access
from .magic_system import (
    MagicSource, MagicTier, EffectType, TargetType, DamageType, ManaFluxLevel,
    Spell, Ritual, MagicUser, LocationMagicProfile, ItemMagicProfile
)

# Material and crafting services
from .magical_material_service import MagicalMaterialService
from .magic_crafting_models import (
    MagicalMaterial, MagicalMaterialInstance, MagicalGatheringLocation, 
    MagicalCraftingEvent
)

# Advanced features
from .advanced_magic_features import EnvironmentalMagicResonance
from .enchantment_service import EnchantmentService

# Leyline and world integration
from .leyline_crafting_service import LeylineCraftingService
from .magic_world_integration import MagicWorldIntegration, MagicalMaterialWorldIntegration

# API interfaces
from .magic_crafting_api import MagicCraftingAPI