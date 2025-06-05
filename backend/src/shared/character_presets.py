"""
Character creation presets for TextRealms.
These presets define starting conditions for different campaign types and player fantasies.
"""
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid

from .character_creation_models import CharacterCreationPreset
from .models import GrowthTier, DomainType

class CampaignTone(str, Enum):
    """Campaign tones that influence preset design"""
    SURVIVAL = "survival"
    COMBAT = "combat"
    SLICE_OF_LIFE = "slice_of_life"
    MYSTERY = "mystery"
    KINGDOM = "kingdom"
    EPIC = "epic"
    HORROR = "horror"
    EXPLORATION = "exploration"
    DIPLOMATIC = "diplomatic"
    HEIST = "heist"

class MagicTier(str, Enum):
    """Tiers of magical ability"""
    NOVICE = "novice"          # Basic magical awareness
    APPRENTICE = "apprentice"  # Can perform simple spells
    PRACTITIONER = "practitioner"  # Competent magic user
    ADEPT = "adept"            # Advanced magical abilities
    MASTER = "master"          # Exceptional magical power

class CharacterPresets:
    """Collection of character creation presets for different campaign types"""
    
    @staticmethod
    def commoner() -> CharacterCreationPreset:
        """A humble, realistic start with limited skills."""
        return CharacterCreationPreset(
            name="Commoner",
            description="A humble, realistic start with limited skills. Ideal for survival or slice-of-life campaigns that focus on growth from humble beginnings.",
            campaign_type="slice_of_life",
            domain_points=10,  # Reduced from 14
            max_per_domain=2,  # Reduced from 3
            min_per_domain=1,
            starting_tag_points=2,
            bonus_traits=[],
            starting_tier=GrowthTier.NOVICE,
            base_health=45,
            health_per_body=8,
            base_clarity=15,
            clarity_per_spirit=4,
            base_stamina=80,
            stamina_per_body=4,
            base_focus=15,
            focus_per_mind=4,
            starting_items={"simple_clothes": 2, "rations": 3, "waterskin": 1},
            starting_currency=10
        )
    
    @staticmethod
    def survivor() -> CharacterCreationPreset:
        """Focused on endurance with slightly better starting gear."""
        return CharacterCreationPreset(
            name="Survivor",
            description="Someone who has learned to endure harsh conditions through necessity. Ideal for survival campaigns, wilderness exploration, or post-apocalyptic settings.",
            campaign_type="survival",
            domain_points=12,  # Reduced from 17
            max_per_domain=3,  # Reduced from 4
            min_per_domain=1,
            starting_tag_points=3,
            bonus_traits=["Resourceful"],
            starting_tier=GrowthTier.NOVICE,
            base_health=60,
            health_per_body=10,
            base_clarity=15,
            clarity_per_spirit=4,
            base_stamina=100,
            stamina_per_body=6,
            base_focus=15,
            focus_per_mind=4,
            starting_items={"sturdy_clothes": 1, "hunting_knife": 1, "flint": 1, "rope": 1, "rations": 5},
            starting_currency=20
        )
    
    @staticmethod
    def scholar() -> CharacterCreationPreset:
        """An academic with specialized knowledge and basic magical training."""
        return CharacterCreationPreset(
            name="Scholar",
            description="An educated individual with specialized academic knowledge and basic magical training. Well-suited for campaigns involving ancient mysteries, arcane research, or historical discoveries.",
            campaign_type="mystery",
            domain_points=15,  # Reduced from 20
            max_per_domain=4,  # Reduced from 5
            min_per_domain=1,
            starting_tag_points=5,
            bonus_traits=["Well Read", "Analytical"],
            starting_tier=GrowthTier.NOVICE,
            base_health=40,
            health_per_body=7,
            base_clarity=30,  # Higher base clarity for magic
            clarity_per_spirit=8,  # Better clarity scaling
            base_stamina=60,
            stamina_per_body=3,
            base_focus=30,  # Higher base focus
            focus_per_mind=8,  # Better focus scaling
            starting_items={"books": 3, "writing_set": 1, "lantern": 1, "ink": 3, "parchment": 10},
            starting_currency=50,
            # Magic system integration
            has_mana_heart=True,
            starting_mana=30,
            mana_regen_rate=1.5,
            starting_spells=["detect_magic", "light", "comprehend_language"],
            magic_tier=MagicTier.NOVICE
        )
    
    @staticmethod
    def adventurer() -> CharacterCreationPreset:
        """A balanced start with moderate skills and equipment."""
        return CharacterCreationPreset(
            name="Adventurer",
            description="A balanced start with moderate skills and equipment. Perfect for traditional fantasy adventure campaigns with a mix of combat, exploration and social interaction.",
            campaign_type="exploration",
            domain_points=16,  # Reduced from 21
            max_per_domain=4,  # Reduced from 5
            min_per_domain=1,
            starting_tag_points=5,
            bonus_traits=["Traveler"],
            starting_tier=GrowthTier.NOVICE,
            base_health=60,
            health_per_body=10,
            base_clarity=20,
            clarity_per_spirit=5,
            base_stamina=100,
            stamina_per_body=5,
            base_focus=20,
            focus_per_mind=5,
            starting_items={"travelers_clothes": 1, "backpack": 1, "bedroll": 1, "rations": 5, "torch": 3, "waterskin": 1},
            starting_currency=50
        )
    
    @staticmethod
    def veteran() -> CharacterCreationPreset:
        """An experienced character with specialized skills."""
        return CharacterCreationPreset(
            name="Veteran",
            description="An experienced character with specialized skills from previous conflicts. Well-suited for combat-focused campaigns or ones that start after significant character development.",
            campaign_type="combat",
            domain_points=21,  # Reduced from 28
            max_per_domain=5,  # Reduced from 7
            min_per_domain=2,
            starting_tag_points=8,
            bonus_traits=["Battle Scarred", "Tactical Mind"],
            starting_tier=GrowthTier.SKILLED,  # One tier higher than normal
            base_health=80,
            health_per_body=12,
            base_clarity=25,
            clarity_per_spirit=6,
            base_stamina=120,
            stamina_per_body=7,
            base_focus=25,
            focus_per_mind=6,
            starting_items={"armor": 1, "weapon": 1, "healing_kit": 1, "rations": 7, "waterskin": 1, "bedroll": 1},
            starting_currency=100
        )
    
    @staticmethod
    def mystic() -> CharacterCreationPreset:
        """A spiritually attuned individual with supernatural insight."""
        return CharacterCreationPreset(
            name="Mystic",
            description="A spiritually attuned individual with supernatural insight or powers. Ideal for mystical, spiritual, or magical campaigns focused on inner development.",
            campaign_type="epic",
            domain_points=18,  # Reduced from 22
            max_per_domain=5,  # Reduced from 7
            min_per_domain=1,
            starting_tag_points=6,
            bonus_traits=["Spiritual Connection", "Intuitive"],
            starting_tier=GrowthTier.NOVICE,
            base_health=45,
            health_per_body=8,
            base_clarity=40,  # Very high base clarity
            clarity_per_spirit=10,  # Excellent clarity scaling
            base_stamina=70,
            stamina_per_body=4,
            base_focus=35,  # High base focus
            focus_per_mind=9,  # Excellent focus scaling
            starting_items={"ritual_robes": 1, "focus_item": 1, "incense": 5, "ritual_components": 3},
            starting_currency=40,
            # Magic system integration
            has_mana_heart=True,
            starting_mana=50,  # Higher starting mana
            mana_regen_rate=2.0,  # Better mana regen
            starting_spells=["sense_emotion", "guidance", "minor_healing", "warding_gesture"],
            starting_rituals=["commune_with_spirits"],
            magic_tier=MagicTier.APPRENTICE,  # Starts at apprentice level
            ley_energy_sensitivity=3  # Better at sensing leylines
        )
    
    @staticmethod
    def get_all_presets() -> List[CharacterCreationPreset]:
        """Get all available character creation presets."""
        return [
            CharacterPresets.commoner(),
            CharacterPresets.survivor(),
            CharacterPresets.scholar(),
            CharacterPresets.adventurer(),
            CharacterPresets.veteran(),
            CharacterPresets.mystic()
        ]
    
    @staticmethod
    def get_preset_by_name(name: str) -> Optional[CharacterCreationPreset]:
        """Get a preset by name (case-insensitive)."""
        name_lower = name.lower()
        for preset in CharacterPresets.get_all_presets():
            if preset.name.lower() == name_lower:
                return preset
        return None
    
    @staticmethod
    def get_presets_by_campaign_type(campaign_type: str) -> List[CharacterCreationPreset]:
        """Get all presets suitable for a specific campaign type."""
        return [
            preset for preset in CharacterPresets.get_all_presets()
            if preset.campaign_type.lower() == campaign_type.lower()
        ]
"""
Character creation presets for TextRealms.
These presets define starting conditions for different campaign types and player fantasies.
"""
from typing import Dict, List, Optional
from enum import Enum

from .character_creation_models import CharacterCreationPreset
from .models import GrowthTier, DomainType

class CampaignTone(str, Enum):
    """Campaign tones that influence preset design"""
    SURVIVAL = "survival"
    COMBAT = "combat"
    SLICE_OF_LIFE = "slice_of_life"
    MYSTERY = "mystery"
    KINGDOM = "kingdom"
    EPIC = "epic"
    HORROR = "horror"
    EXPLORATION = "exploration"
    DIPLOMATIC = "diplomatic"
    HEIST = "heist"

class CharacterPresets:
    """Collection of character creation presets for different campaign types"""
    
    @staticmethod
    def commoner() -> CharacterCreationPreset:
        """A humble, realistic start with limited skills."""
        return CharacterCreationPreset(
            name="Commoner",
            description="A humble, realistic start with limited skills. Ideal for survival or slice-of-life campaigns that focus on growth from humble beginnings.",
            campaign_type=CampaignTone.SLICE_OF_LIFE,
            domain_points=14,
            max_per_domain=3,
            min_per_domain=1,
            starting_tag_points=2,
            bonus_traits=[],
            starting_tier=GrowthTier.NOVICE,
            base_health=50,
            health_per_body=10,
            base_clarity=20,
            clarity_per_spirit=5,
            base_stamina=100,
            stamina_per_body=5,
            base_focus=20,
            focus_per_mind=5,
            starting_items={"bread": 2, "water_flask": 1}
        )
    
    @staticmethod
    def survivor() -> CharacterCreationPreset:
        """Focused on endurance with slightly better starting gear."""
        return CharacterCreationPreset(
            name="Survivor",
            description="Someone who has learned to endure harsh conditions through necessity. Ideal for survival campaigns, wilderness exploration, or post-apocalyptic settings.",
            campaign_type=CampaignTone.SURVIVAL,
            domain_points=17,
            max_per_domain=4,
            min_per_domain=1,
            starting_tag_points=3,
            bonus_traits=["Resourceful"],
            starting_tier=GrowthTier.SKILLED,
            base_health=75,
            health_per_body=12,
            base_clarity=15,
            clarity_per_spirit=4,
            base_stamina=120,
            stamina_per_body=8,
            base_focus=15,
            focus_per_mind=4,
            starting_items={"dried_meat": 3, "water_flask": 1, "hunting_knife": 1, "flint": 1}
        )
    
    @staticmethod
    def adventurer() -> CharacterCreationPreset:
        """A balanced start with moderate skills and equipment."""
        return CharacterCreationPreset(
            name="Adventurer",
            description="A balanced start with moderate skills and equipment. Perfect for traditional fantasy adventure campaigns with a mix of combat, exploration and social interaction.",
            campaign_type=CampaignTone.EXPLORATION,
            domain_points=21,
            max_per_domain=5,
            min_per_domain=1,
            starting_tag_points=5,
            bonus_traits=["Traveler"],
            starting_tier=GrowthTier.SKILLED,
            base_health=75,
            health_per_body=15,
            base_clarity=25,
            clarity_per_spirit=5,
            base_stamina=100,
            stamina_per_body=5,
            base_focus=25,
            focus_per_mind=5,
            starting_items={"bread": 4, "water_flask": 1, "torch": 2, "bedroll": 1},
            starting_currency=50
        )
    
    @staticmethod
    def veteran() -> CharacterCreationPreset:
        """An experienced character with specialized skills."""
        return CharacterCreationPreset(
            name="Veteran",
            description="An experienced character with specialized skills from previous conflicts. Well-suited for combat-focused campaigns or ones that start after significant character development.",
            campaign_type=CampaignTone.COMBAT,
            domain_points=28,
            max_per_domain=7,
            min_per_domain=2,
            starting_tag_points=8,
            bonus_traits=["Battle Scarred", "Survivor"],
            starting_tier=GrowthTier.EXPERT,
            base_health=100,
            health_per_body=20,
            base_clarity=30,
            clarity_per_spirit=5,
            base_stamina=120,
            stamina_per_body=8,
            base_focus=30,
            focus_per_mind=6,
            starting_items={"rations": 6, "water_flask": 2, "torch": 4, "bedroll": 1, "bandages": 3},
            starting_currency=200
        )
    
    @staticmethod
    def detective() -> CharacterCreationPreset:
        """A perceptive investigator with keen awareness."""
        return CharacterCreationPreset(
            name="Detective",
            description="A perceptive investigator with specialized skills for uncovering secrets. Perfect for mystery, noir, or investigation-focused campaigns where observation is key.",
            campaign_type=CampaignTone.MYSTERY,
            domain_points=24,
            max_per_domain=6,
            min_per_domain=1,
            starting_tag_points=7,
            bonus_traits=["Keen Eye", "Logical"],
            starting_tier=GrowthTier.SKILLED,
            base_health=60,
            health_per_body=12,
            base_clarity=35,
            clarity_per_spirit=6,
            base_stamina=90,
            stamina_per_body=4,
            base_focus=40,
            focus_per_mind=8,
            starting_items={"notebook": 1, "pen": 2, "magnifying_glass": 1, "lantern": 1},
            starting_currency=150
        )
    
    @staticmethod
    def noble() -> CharacterCreationPreset:
        """An aristocrat with social influence and education."""
        return CharacterCreationPreset(
            name="Noble",
            description="A member of the aristocracy with social influence and education. Ideal for political intrigue, kingdom management, or courtly drama campaigns.",
            campaign_type=CampaignTone.KINGDOM,
            domain_points=26,
            max_per_domain=6,
            min_per_domain=1,
            starting_tag_points=6,
            bonus_traits=["Noble Birth", "Well Connected"],
            starting_tier=GrowthTier.SKILLED,
            base_health=60,
            health_per_body=10,
            base_clarity=30,
            clarity_per_spirit=5,
            base_stamina=80,
            stamina_per_body=4,
            base_focus=30,
            focus_per_mind=6,
            starting_items={"fine_clothes": 2, "signet_ring": 1, "writing_set": 1},
            starting_currency=500
        )
    
    @staticmethod
    def scholar() -> CharacterCreationPreset:
        """An academic with specialized knowledge."""
        return CharacterCreationPreset(
            name="Scholar",
            description="An educated individual with specialized academic knowledge. Well-suited for campaigns involving ancient mysteries, arcane research, or historical discoveries.",
            campaign_type=CampaignTone.MYSTERY,
            domain_points=20,
            max_per_domain=6,
            min_per_domain=1,
            starting_tag_points=6,
            bonus_traits=["Well Read", "Analytical"],
            starting_tier=GrowthTier.SKILLED,
            base_health=45,
            health_per_body=8,
            base_clarity=30,
            clarity_per_spirit=5,
            base_stamina=70,
            stamina_per_body=3,
            base_focus=40,
            focus_per_mind=8,
            starting_items={"books": 3, "writing_set": 1, "spectacles": 1, "lantern": 1},
            starting_currency=100
        )
    
    @staticmethod
    def artisan() -> CharacterCreationPreset:
        """A skilled craftsperson with practical abilities."""
        return CharacterCreationPreset(
            name="Artisan",
            description="A skilled craftsperson with practical creative abilities. Perfect for slice-of-life campaigns focused on community building or creating meaningful items.",
            campaign_type=CampaignTone.SLICE_OF_LIFE,
            domain_points=18,
            max_per_domain=5,
            min_per_domain=1,
            starting_tag_points=5,
            bonus_traits=["Skilled Hands", "Eye for Detail"],
            starting_tier=GrowthTier.SKILLED,
            base_health=60,
            health_per_body=10,
            base_clarity=25,
            clarity_per_spirit=4,
            base_stamina=90,
            stamina_per_body=5,
            base_focus=30,
            focus_per_mind=5,
            starting_items={"tools": 1, "materials": 3, "apron": 1},
            starting_currency=120
        )
    
    @staticmethod
    def outcast() -> CharacterCreationPreset:
        """A loner with survival skills and distrust of society."""
        return CharacterCreationPreset(
            name="Outcast",
            description="Someone living on society's fringes, either by choice or circumstance. Suitable for gritty survival, criminal underworld, or redemption arc campaigns.",
            campaign_type=CampaignTone.SURVIVAL,
            domain_points=16,
            max_per_domain=4,
            min_per_domain=1,
            starting_tag_points=4,
            bonus_traits=["Street Smart", "Suspicious"],
            starting_tier=GrowthTier.NOVICE,
            base_health=65,
            health_per_body=12,
            base_clarity=20,
            clarity_per_spirit=4,
            base_stamina=110,
            stamina_per_body=7,
            base_focus=20,
            focus_per_mind=4,
            starting_items={"makeshift_weapon": 1, "tattered_cloak": 1, "lockpicks": 1},
            starting_currency=15
        )
    
    @staticmethod
    def mystic() -> CharacterCreationPreset:
        """A spiritually attuned individual with supernatural insight."""
        return CharacterCreationPreset(
            name="Mystic",
            description="A spiritually attuned individual with supernatural insight or powers. Ideal for mystical, spiritual, or magical campaigns focused on inner development.",
            campaign_type=CampaignTone.EPIC,
            domain_points=22,
            max_per_domain=7,
            min_per_domain=1,
            starting_tag_points=5,
            bonus_traits=["Inner Sight", "Spiritual Connection"],
            starting_tier=GrowthTier.SKILLED,
            base_health=50,
            health_per_body=8,
            base_clarity=50,
            clarity_per_spirit=10,
            base_stamina=80,
            stamina_per_body=4,
            base_focus=35,
            focus_per_mind=7,
            starting_items={"ritual_components": 3, "ceremonial_robe": 1, "incense": 5},
            starting_currency=50
        )
    
    @staticmethod
    def hero() -> CharacterCreationPreset:
        """A legendary character with exceptional abilities."""
        return CharacterCreationPreset(
            name="Hero",
            description="A legendary character with exceptional abilities and destiny. Perfect for epic high-fantasy campaigns or stories about chosen ones and world-shaking events.",
            campaign_type=CampaignTone.EPIC,
            domain_points=35,
            max_per_domain=9,
            min_per_domain=3,
            starting_tag_points=12,
            bonus_traits=["Chosen One", "Famous", "Heroic"],
            starting_tier=GrowthTier.MASTER,
            base_health=150,
            health_per_body=25,
            base_clarity=50,
            clarity_per_spirit=8,
            base_stamina=150,
            stamina_per_body=10,
            base_focus=50,
            focus_per_mind=8,
            starting_items={"magical_weapon": 1, "heroic_attire": 1, "healing_potion": 3, "relic": 1},
            starting_currency=500
        )
    
    @staticmethod
    def rogue() -> CharacterCreationPreset:
        """A cunning character specializing in stealth and subterfuge."""
        return CharacterCreationPreset(
            name="Rogue",
            description="A character with skills in stealth, subterfuge and dexterity. Excellent for heist campaigns, criminal underworld stories, or any scenario requiring finesse over force.",
            campaign_type=CampaignTone.HEIST,
            domain_points=23,
            max_per_domain=6,
            min_per_domain=1,
            starting_tag_points=7,
            bonus_traits=["Light Fingers", "Shadow Step"],
            starting_tier=GrowthTier.SKILLED,
            base_health=60,
            health_per_body=10,
            base_clarity=30,
            clarity_per_spirit=5,
            base_stamina=90,
            stamina_per_body=6,
            base_focus=35,
            focus_per_mind=6,
            starting_items={"lockpicks": 1, "dark_clothing": 1, "dagger": 1, "rope": 1, "smoke_bomb": 2},
            starting_currency=120
        )
    
    @staticmethod
    def diplomat() -> CharacterCreationPreset:
        """A skilled negotiator with political connections."""
        return CharacterCreationPreset(
            name="Diplomat",
            description="A skilled negotiator with political acumen and social connections. Ideal for diplomatic campaigns, political intrigue, or peace-making narratives.",
            campaign_type=CampaignTone.DIPLOMATIC,
            domain_points=25,
            max_per_domain=7,
            min_per_domain=1,
            starting_tag_points=6,
            bonus_traits=["Silver Tongue", "Cultural Knowledge"],
            starting_tier=GrowthTier.EXPERT,
            base_health=55,
            health_per_body=9,
            base_clarity=35,
            clarity_per_spirit=6,
            base_stamina=70,
            stamina_per_body=3,
            base_focus=40,
            focus_per_mind=7,
            starting_items={"formal_attire": 2, "diplomatic_seal": 1, "correspondence_kit": 1},
            starting_currency=300
        )
    
    @staticmethod
    def get_all_presets() -> List[CharacterCreationPreset]:
        """Get all available character creation presets."""
        return [
            CharacterPresets.commoner(),
            CharacterPresets.survivor(),
            CharacterPresets.adventurer(),
            CharacterPresets.veteran(),
            CharacterPresets.detective(),
            CharacterPresets.noble(),
            CharacterPresets.scholar(),
            CharacterPresets.artisan(),
            CharacterPresets.outcast(),
            CharacterPresets.mystic(),
            CharacterPresets.hero(),
            CharacterPresets.rogue(),
            CharacterPresets.diplomat()
        ]
    
    @staticmethod
    def get_preset_by_name(name: str) -> Optional[CharacterCreationPreset]:
        """Get a preset by name"""
        name_lower = name.lower()
        for preset in CharacterPresets.get_all_presets():
            if preset.name.lower() == name_lower:
                return preset
        return None
    
    @staticmethod
    def get_presets_by_campaign_type(campaign_type: CampaignTone) -> List[CharacterCreationPreset]:
        """Get all presets suitable for a specific campaign type"""
        return [
            preset for preset in CharacterPresets.get_all_presets()
            if preset.campaign_type == campaign_type
        ]
