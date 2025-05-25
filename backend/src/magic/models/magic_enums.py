"""
Magic System Enumerations

This module defines the core enumerations used throughout the magic system.
"""

from enum import Enum
from typing import List, Dict, Optional, Any, Tuple


class MagicSource(str, Enum):
    """Sources of magical power"""
    DOMAIN_RESONANCE = "domain_resonance"    # Tied to domain system
    MANA_HEART = "mana_heart"                # Internal energy cultivation
    ARCANE_STUDY = "arcane_study"            # Academic magical knowledge
    DIVINE_FAVOR = "divine_favor"            # Spirit domain enhancement
    ELEMENTAL_PACT = "elemental_pact"        # Environmental magic
    ARTIFACT_CHANNEL = "artifact_channel"    # Magic through items


class MagicTier(str, Enum):
    """Tiers of magical practice"""
    SPIRITUAL_UTILITY = "spiritual_utility"  # Tier 1: Basic life enhancement
    MANA_INFUSION = "mana_infusion"          # Tier 2: Energy manipulation
    ARCANE_MASTERY = "arcane_mastery"        # Tier 3: Reality manipulation


class MagicSchool(str, Enum):
    """Schools of magical practice"""
    # Tier 1 - Spiritual Utility
    ENHANCEMENT = "enhancement"              # Body/performance improvements
    DIVINATION = "divination"                # Information gathering
    COMMUNION = "communion"                  # Social/spiritual connections
    
    # Tier 2 - Mana Infusion
    ELEMENTAL = "elemental"                  # Fire, ice, lightning, earth
    TRANSMUTATION = "transmutation"          # Matter manipulation
    WARD = "ward"                            # Protection and barriers
    
    # Tier 3 - Arcane Mastery
    REALITY_WEAVING = "reality_weaving"      # Fundamental reality changes
    TEMPORAL = "temporal"                    # Time manipulation
    DIMENSIONAL = "dimensional"              # Space and plane shifting


class ManaHeartStage(str, Enum):
    """Stages of mana heart development"""
    DORMANT = "dormant"                      # No mana heart
    AWAKENING = "awakening"                  # Initial development
    FLOWING = "flowing"                      # Basic mana circulation
    RESERVOIR = "reservoir"                  # Expanded capacity
    TORRENT = "torrent"                      # High-power output
    TRANSCENDENT = "transcendent"            # Beyond normal limits


class ElementType(str, Enum):
    """Types of elemental magic"""
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHTNING = "lightning"
    ICE = "ice"
    METAL = "metal"
    WOOD = "wood"
    LIGHT = "light"
    SHADOW = "shadow"


class SpellComplexity(str, Enum):
    """Complexity levels for spells"""
    SIMPLE = "simple"                 # Basic spells, minimal training
    MODERATE = "moderate"             # Intermediate spells, formal training
    COMPLEX = "complex"               # Advanced spells, extensive study
    INTRICATE = "intricate"           # Master-level spells, rare knowledge
    LEGENDARY = "legendary"           # Mythical spells, ancient wisdom


class MagicEventType(str, Enum):
    """Types of magic-related events"""
    SPELL_CAST = "spell_cast"
    SPELL_LEARNED = "spell_learned"
    MANA_HEART_ADVANCED = "mana_heart_advanced"
    ENCHANTMENT_CREATED = "enchantment_created"
    MAGIC_CORRUPTION_GAINED = "magic_corruption_gained"
    MAGICAL_DISCOVERY = "magical_discovery"
    MAGICAL_ITEM_USED = "magical_item_used"
    MAGIC_RITUAL_PERFORMED = "magic_ritual_performed"
    MAGICAL_ATTUNEMENT_CHANGED = "magical_attunement_changed"


class SpellFailureType(str, Enum):
    """Types of spell failures"""
    MINOR_MISCAST = "minor_miscast"       # Spell fails with minimal effects
    MAJOR_MISCAST = "major_miscast"       # Spell fails with significant side effects
    CATASTROPHIC_FAILURE = "catastrophic_failure"  # Spell fails dangerously
    CORRUPTION_SURGE = "corruption_surge"  # Spell succeeds but corrupts the caster
    MANA_DEPLETION = "mana_depletion"     # Spell drains excessive mana
    DOMAIN_REJECTION = "domain_rejection"  # Domains reject the magical pattern


class EnchantmentType(str, Enum):
    """Types of item enchantments"""
    ENHANCEMENT = "enhancement"        # Improves item's base properties
    ELEMENTAL = "elemental"            # Adds elemental effects
    UTILITY = "utility"                # Adds special utilities
    PROTECTIVE = "protective"          # Adds defensive properties
    MOBILITY = "mobility"              # Adds movement properties
    PERCEPTION = "perception"          # Adds sensory properties
    BINDING = "binding"                # Binds item to user
    CONDITIONAL = "conditional"        # Activates under conditions


class MagicItemRarity(str, Enum):
    """Rarity tiers for magical items"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    MYTHICAL = "mythical"
    ARTIFACT = "artifact"