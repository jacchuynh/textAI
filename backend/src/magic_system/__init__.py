"""
Magic System Package

This package contains all the components of the game's magic system.
"""

# Import core classes for easier access
from .magic_system import (
    MagicSource, MagicTier, EffectType, TargetType, DamageType, ManaFluxLevel,
    Spell, Ritual, MagicUser, LocationMagicProfile, ItemMagicProfile
)

from .magical_material_service import MagicalMaterialService