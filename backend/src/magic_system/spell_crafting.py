"""
Spell Crafting System - Mechanics for creating and modifying spells

This module provides systems for crafting and customizing spells, with
special attention to how location and environment affect spell properties.
"""

import random
import math
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any, Set

from world_generation.world_model import BiomeType, POIType, DBRegion, DBBiome, DBPointOfInterest
from magic_system.leyline_manager import LeylineManager, LeylineType


class SpellElement(str, Enum):
    """Primary magical elements that can compose a spell."""
    FIRE = "fire"
    WATER = "water"
    EARTH = "earth"
    AIR = "air"
    LIGHT = "light"
    SHADOW = "shadow"
    LIFE = "life"
    DEATH = "death"
    MIND = "mind"
    VOID = "void"
    TIME = "time"
    SPACE = "space"


class SpellPurpose(str, Enum):
    """Primary purpose or category of a spell."""
    ATTACK = "attack"
    DEFENSE = "defense"
    HEALING = "healing"
    UTILITY = "utility"
    DIVINATION = "divination"
    ENHANCEMENT = "enhancement"
    TRANSFORMATION = "transformation"
    SUMMONING = "summoning"
    BINDING = "binding"
    ILLUSION = "illusion"


class SpellComplexity(str, Enum):
    """Complexity level of a spell, affecting casting difficulty."""
    SIMPLE = "simple"
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    COMPLEX = "complex"
    MASTERWORK = "masterwork"


class SpellDuration(str, Enum):
    """Duration type for a spell's effects."""
    INSTANT = "instant"
    BRIEF = "brief"       # Seconds to minutes
    SHORT = "short"       # Minutes to an hour
    MEDIUM = "medium"     # Hours
    LONG = "long"         # Days
    EXTENDED = "extended" # Weeks or longer
    PERMANENT = "permanent"


class SpellRange(str, Enum):
    """Range category for a spell's effects."""
    SELF = "self"
    TOUCH = "touch"
    SHORT = "short"       # Several meters
    MEDIUM = "medium"     # Dozens of meters
    LONG = "long"         # Hundreds of meters
    EXTENDED = "extended" # Kilometers
    SIGHT = "sight"       # As far as can be seen
    UNLIMITED = "unlimited"


class SpellArea(str, Enum):
    """Area of effect for a spell."""
    SINGLE = "single"     # Single target
    SMALL = "small"       # Small area (1-2m radius)
    MEDIUM = "medium"     # Medium area (3-5m radius)
    LARGE = "large"       # Large area (6-15m radius)
    HUGE = "huge"         # Huge area (16-50m radius)
    MASSIVE = "massive"   # Massive area (>50m radius)


class SpellTemplate:
    """
    Template for a spell, containing its base properties.
    """
    def __init__(
        self,
        template_id: str,
        name: str,
        description: str,
        base_elements: List[SpellElement],
        purpose: SpellPurpose,
        complexity: SpellComplexity,
        base_power: float,
        base_duration: SpellDuration,
        base_range: SpellRange,
        base_area: SpellArea,
        mana_cost: int,
        focus_required: int,
        casting_time: float,  # In seconds
        components_required: List[str] = None,
        ritual_required: bool = False,
        tags: List[str] = None
    ):
        self.id = template_id
        self.name = name
        self.description = description
        self.base_elements = base_elements
        self.purpose = purpose
        self.complexity = complexity
        self.base_power = base_power
        self.base_duration = base_duration
        self.base_range = base_range
        self.base_area = base_area
        self.mana_cost = mana_cost
        self.focus_required = focus_required
        self.casting_time = casting_time
        self.components_required = components_required or []
        self.ritual_required = ritual_required
        self.tags = tags or []
    
    def __str__(self):
        return f"{self.name} ({self.purpose}, {self.complexity})"


class Spell:
    """
    An instance of a spell, which can be modified by location, caster, and other factors.
    """
    def __init__(
        self,
        spell_id: str,
        template: SpellTemplate,
        caster_id: Optional[str] = None,
        location_id: Optional[str] = None,
        modifications: Dict[str, Any] = None,
        custom_name: Optional[str] = None
    ):
        self.id = spell_id
        self.template = template
        self.caster_id = caster_id
        self.location_id = location_id
        self.modifications = modifications or {}
        self.custom_name = custom_name
        
        # Derived properties, calculated based on template and modifications
        self.actual_power = self.template.base_power
        self.actual_duration = self.template.base_duration
        self.actual_range = self.template.base_range
        self.actual_area = self.template.base_area
        self.actual_mana_cost = self.template.mana_cost
        self.actual_focus_required = self.template.focus_required
        self.actual_casting_time = self.template.casting_time
        self.elements = self.template.base_elements.copy()
        
        # Apply modifications if any
        if self.modifications:
            self._apply_modifications()
    
    def _apply_modifications(self):
        """Apply stored modifications to the spell's properties."""
        # Power modification
        if 'power_mod' in self.modifications:
            self.actual_power *= (1 + self.modifications['power_mod'])
        
        # Duration modification
        if 'duration_mod' in self.modifications:
            duration_levels = list(SpellDuration)
            current_idx = duration_levels.index(self.template.base_duration)
            mod = self.modifications['duration_mod']
            
            # Calculate new index with bounds checking
            new_idx = min(max(0, current_idx + mod), len(duration_levels) - 1)
            self.actual_duration = duration_levels[new_idx]
        
        # Range modification
        if 'range_mod' in self.modifications:
            range_levels = list(SpellRange)
            current_idx = range_levels.index(self.template.base_range)
            mod = self.modifications['range_mod']
            
            # Calculate new index with bounds checking
            new_idx = min(max(0, current_idx + mod), len(range_levels) - 1)
            self.actual_range = range_levels[new_idx]
        
        # Area modification
        if 'area_mod' in self.modifications:
            area_levels = list(SpellArea)
            current_idx = area_levels.index(self.template.base_area)
            mod = self.modifications['area_mod']
            
            # Calculate new index with bounds checking
            new_idx = min(max(0, current_idx + mod), len(area_levels) - 1)
            self.actual_area = area_levels[new_idx]
        
        # Cost modifications
        if 'mana_cost_mod' in self.modifications:
            self.actual_mana_cost = max(1, int(self.template.mana_cost * (1 + self.modifications['mana_cost_mod'])))
        
        if 'focus_required_mod' in self.modifications:
            self.actual_focus_required = max(1, int(self.template.focus_required * (1 + self.modifications['focus_required_mod'])))
        
        # Casting time modification
        if 'casting_time_mod' in self.modifications:
            self.actual_casting_time = max(0.1, self.template.casting_time * (1 + self.modifications['casting_time_mod']))
        
        # Element additions
        if 'added_elements' in self.modifications:
            for element in self.modifications['added_elements']:
                if element not in self.elements:
                    self.elements.append(element)
    
    def get_display_name(self) -> str:
        """Get the display name of the spell, using custom name if available."""
        if self.custom_name:
            return self.custom_name
        return self.template.name
    
    def __str__(self):
        return f"{self.get_display_name()} ({self.template.purpose}, Power: {self.actual_power:.1f})"


class SpellCraftingSystem:
    """
    System for crafting and modifying spells based on location, materials, and other factors.
    """
    def __init__(self, leyline_manager: Optional[LeylineManager] = None):
        self.templates: Dict[str, SpellTemplate] = {}
        self.spells: Dict[str, Spell] = {}
        self.leyline_manager = leyline_manager or LeylineManager()
        
        # Load default templates
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load a set of default spell templates."""
        # Basic attack spells
        self.templates["fireball"] = SpellTemplate(
            template_id="fireball",
            name="Fireball",
            description="A ball of fire that explodes on impact, dealing damage in a small area.",
            base_elements=[SpellElement.FIRE],
            purpose=SpellPurpose.ATTACK,
            complexity=SpellComplexity.BASIC,
            base_power=10.0,
            base_duration=SpellDuration.INSTANT,
            base_range=SpellRange.MEDIUM,
            base_area=SpellArea.SMALL,
            mana_cost=15,
            focus_required=10,
            casting_time=1.5,
            components_required=["verbal", "somatic"],
            tags=["fire", "explosion", "projectile"]
        )
        
        self.templates["ice_spike"] = SpellTemplate(
            template_id="ice_spike",
            name="Ice Spike",
            description="A sharp spike of ice that pierces a single target.",
            base_elements=[SpellElement.WATER],
            purpose=SpellPurpose.ATTACK,
            complexity=SpellComplexity.BASIC,
            base_power=12.0,
            base_duration=SpellDuration.INSTANT,
            base_range=SpellRange.MEDIUM,
            base_area=SpellArea.SINGLE,
            mana_cost=12,
            focus_required=8,
            casting_time=1.0,
            components_required=["somatic"],
            tags=["ice", "piercing", "projectile"]
        )
        
        # Basic defense spells
        self.templates["stone_skin"] = SpellTemplate(
            template_id="stone_skin",
            name="Stone Skin",
            description="Hardens the caster's skin, providing protection against physical attacks.",
            base_elements=[SpellElement.EARTH],
            purpose=SpellPurpose.DEFENSE,
            complexity=SpellComplexity.BASIC,
            base_power=8.0,
            base_duration=SpellDuration.MEDIUM,
            base_range=SpellRange.SELF,
            base_area=SpellArea.SINGLE,
            mana_cost=20,
            focus_required=15,
            casting_time=2.0,
            components_required=["verbal", "somatic"],
            tags=["earth", "protection", "physical"]
        )
        
        # Basic healing spells
        self.templates["healing_touch"] = SpellTemplate(
            template_id="healing_touch",
            name="Healing Touch",
            description="A gentle touch that heals wounds and restores vitality.",
            base_elements=[SpellElement.LIFE],
            purpose=SpellPurpose.HEALING,
            complexity=SpellComplexity.BASIC,
            base_power=15.0,
            base_duration=SpellDuration.INSTANT,
            base_range=SpellRange.TOUCH,
            base_area=SpellArea.SINGLE,
            mana_cost=25,
            focus_required=20,
            casting_time=3.0,
            components_required=["somatic"],
            tags=["healing", "life", "restoration"]
        )
        
        # Utility spells
        self.templates["light"] = SpellTemplate(
            template_id="light",
            name="Light",
            description="Creates a hovering ball of light that illuminates the area.",
            base_elements=[SpellElement.LIGHT],
            purpose=SpellPurpose.UTILITY,
            complexity=SpellComplexity.SIMPLE,
            base_power=5.0,
            base_duration=SpellDuration.LONG,
            base_range=SpellRange.TOUCH,
            base_area=SpellArea.MEDIUM,
            mana_cost=5,
            focus_required=3,
            casting_time=0.5,
            components_required=["verbal"],
            tags=["light", "illumination"]
        )
        
        # More advanced spells
        self.templates["teleport"] = SpellTemplate(
            template_id="teleport",
            name="Teleport",
            description="Instantly transports the caster to a known location within range.",
            base_elements=[SpellElement.SPACE],
            purpose=SpellPurpose.UTILITY,
            complexity=SpellComplexity.ADVANCED,
            base_power=30.0,
            base_duration=SpellDuration.INSTANT,
            base_range=SpellRange.LONG,
            base_area=SpellArea.SINGLE,
            mana_cost=50,
            focus_required=40,
            casting_time=5.0,
            components_required=["verbal", "somatic", "material"],
            tags=["teleportation", "movement", "space"]
        )
        
        self.templates["summon_elemental"] = SpellTemplate(
            template_id="summon_elemental",
            name="Summon Elemental",
            description="Summons an elemental being to serve the caster for a limited time.",
            base_elements=[SpellElement.FIRE, SpellElement.WATER, SpellElement.EARTH, SpellElement.AIR],
            purpose=SpellPurpose.SUMMONING,
            complexity=SpellComplexity.COMPLEX,
            base_power=25.0,
            base_duration=SpellDuration.MEDIUM,
            base_range=SpellRange.SHORT,
            base_area=SpellArea.SMALL,
            mana_cost=60,
            focus_required=45,
            casting_time=10.0,
            components_required=["verbal", "somatic", "material", "focus"],
            ritual_required=True,
            tags=["summoning", "elemental", "conjuration"]
        )
    
    def create_spell_from_template(
        self,
        template_id: str,
        caster_id: Optional[str] = None,
        location_id: Optional[str] = None,
        custom_name: Optional[str] = None
    ) -> Optional[Spell]:
        """
        Create a new spell instance from a template, potentially modified by location.
        
        Args:
            template_id: ID of the template to use
            caster_id: ID of the caster (optional)
            location_id: ID of the location where the spell is being cast (optional)
            custom_name: Custom name for the spell (optional)
            
        Returns:
            New spell instance or None if template not found
        """
        if template_id not in self.templates:
            return None
        
        template = self.templates[template_id]
        spell_id = f"spell_{template_id}_{len(self.spells)}"
        
        # Generate base spell without modifications
        spell = Spell(
            spell_id=spell_id,
            template=template,
            caster_id=caster_id,
            location_id=location_id,
            custom_name=custom_name
        )
        
        # Apply location-based modifications if a location is specified
        if location_id:
            location_mods = self.generate_location_modifications(location_id, template)
            spell.modifications = location_mods
            spell._apply_modifications()
        
        # Store and return the spell
        self.spells[spell_id] = spell
        return spell
    
    def generate_location_modifications(
        self,
        location_id: str,
        template: SpellTemplate
    ) -> Dict[str, Any]:
        """
        Generate modifications to a spell based on the magical properties of a location.
        
        Args:
            location_id: ID of the location
            template: Spell template being modified
            
        Returns:
            Dictionary of modifications to apply to the spell
        """
        # Get magical properties for this location from the leyline manager
        magical_props = self.leyline_manager.get_magical_properties_for_poi(location_id)
        
        if not magical_props or magical_props["magical_strength"] < 0.1:
            # Location has minimal magical influence
            return {}
        
        # Start with empty modifications
        modifications = {}
        
        # Base modifier scales with magical strength
        base_modifier = magical_props["magical_strength"] * 0.5  # 0.0 to 0.5
        
        # Adjust based on magical stability
        stability_multiplier = {
            "very_stable": 1.0,
            "stable": 0.9,
            "fluctuating": 0.7,
            "unstable": 0.5,
            "chaotic": 0.3
        }.get(magical_props["stability"], 0.8)
        
        # Check element affinities for this location
        affinities = magical_props["affinities"]
        element_match = False
        element_boost = 0.0
        
        # Convert template elements to strings for comparison
        template_elements = [e.value for e in template.base_elements]
        
        # Check if any template elements match location affinities
        for element in template_elements:
            if element in affinities:
                element_match = True
                element_boost += affinities[element] * 0.3  # 0.0 to 0.3 per matching element
        
        if not element_match:
            # If no elements match, slightly negative modification
            element_boost = -0.1
        
        # Purpose-specific adjustments
        purpose_mod = 0.0
        
        # Some locations may favor certain spell purposes
        if template.purpose == SpellPurpose.ATTACK and "fire" in affinities and affinities["fire"] > 0.5:
            purpose_mod += 0.2
        elif template.purpose == SpellPurpose.HEALING and "life" in affinities and affinities["life"] > 0.5:
            purpose_mod += 0.2
        elif template.purpose == SpellPurpose.DEFENSE and "earth" in affinities and affinities["earth"] > 0.5:
            purpose_mod += 0.2
        elif template.purpose == SpellPurpose.DIVINATION and "mind" in affinities and affinities["mind"] > 0.5:
            purpose_mod += 0.2
        
        # Calculate final power modifier
        power_mod = base_modifier + element_boost + purpose_mod
        power_mod *= stability_multiplier
        
        # Apply some randomness to make it interesting
        power_mod += random.uniform(-0.1, 0.1)
        
        # Cap the modifier to reasonable bounds
        power_mod = max(-0.5, min(1.0, power_mod))
        
        # Set power modification
        modifications["power_mod"] = power_mod
        
        # Potentially modify other spell properties based on location
        
        # Duration modification
        duration_mod = int(power_mod * 2)  # -1, 0, +1, or +2
        if duration_mod != 0:
            modifications["duration_mod"] = duration_mod
        
        # Range modification
        range_mod = int(power_mod * 1.5)  # -1, 0, or +1
        if range_mod != 0:
            modifications["range_mod"] = range_mod
        
        # Area modification
        area_mod = int(power_mod * 1.5)  # -1, 0, or +1
        if area_mod != 0:
            modifications["area_mod"] = area_mod
        
        # Cost modifications
        # If power is increased, cost typically increases too, but less dramatically
        if power_mod > 0:
            modifications["mana_cost_mod"] = power_mod * 0.7
            modifications["focus_required_mod"] = power_mod * 0.6
        else:
            # If power is decreased, cost decreases slightly
            modifications["mana_cost_mod"] = power_mod * 0.5
            modifications["focus_required_mod"] = power_mod * 0.4
        
        # Casting time modification
        # Positive power mod can sometimes decrease casting time
        if power_mod > 0.3 and random.random() < 0.5:
            modifications["casting_time_mod"] = -0.2
        elif power_mod < -0.2:
            # Negative power mod can increase casting time
            modifications["casting_time_mod"] = 0.3
        
        # Potentially add elemental aspects based on location affinities
        added_elements = []
        for affinity, value in affinities.items():
            if value > 0.7 and random.random() < 0.3:
                try:
                    # Try to convert the affinity to a SpellElement
                    element = SpellElement(affinity)
                    if element not in template.base_elements:
                        added_elements.append(element)
                except ValueError:
                    # Not all affinities map to SpellElements
                    pass
        
        if added_elements:
            modifications["added_elements"] = added_elements
        
        return modifications
    
    def get_template(self, template_id: str) -> Optional[SpellTemplate]:
        """Get a spell template by ID."""
        return self.templates.get(template_id)
    
    def get_spell(self, spell_id: str) -> Optional[Spell]:
        """Get a spell instance by ID."""
        return self.spells.get(spell_id)
    
    def get_templates_by_element(self, element: SpellElement) -> List[SpellTemplate]:
        """Get all templates that use a specific element."""
        return [t for t in self.templates.values() if element in t.base_elements]
    
    def get_templates_by_purpose(self, purpose: SpellPurpose) -> List[SpellTemplate]:
        """Get all templates with a specific purpose."""
        return [t for t in self.templates.values() if t.purpose == purpose]
    
    def get_templates_by_complexity(self, complexity: SpellComplexity) -> List[SpellTemplate]:
        """Get all templates with a specific complexity level."""
        return [t for t in self.templates.values() if t.complexity == complexity]
    
    def add_custom_template(self, template: SpellTemplate) -> bool:
        """Add a custom spell template to the system."""
        if template.id in self.templates:
            return False
        
        self.templates[template.id] = template
        return True
    
    def create_custom_spell(
        self,
        name: str,
        description: str,
        elements: List[SpellElement],
        purpose: SpellPurpose,
        complexity: SpellComplexity,
        power: float,
        duration: SpellDuration,
        range_val: SpellRange,
        area: SpellArea,
        mana_cost: int,
        focus_required: int,
        casting_time: float,
        components: List[str] = None,
        ritual_required: bool = False,
        tags: List[str] = None,
        caster_id: Optional[str] = None,
        location_id: Optional[str] = None
    ) -> Spell:
        """
        Create a completely custom spell from scratch.
        
        Returns:
            The newly created spell
        """
        # Create a unique template ID
        template_id = f"custom_{name.lower().replace(' ', '_')}_{len(self.templates)}"
        
        # Create the template
        template = SpellTemplate(
            template_id=template_id,
            name=name,
            description=description,
            base_elements=elements,
            purpose=purpose,
            complexity=complexity,
            base_power=power,
            base_duration=duration,
            base_range=range_val,
            base_area=area,
            mana_cost=mana_cost,
            focus_required=focus_required,
            casting_time=casting_time,
            components_required=components,
            ritual_required=ritual_required,
            tags=tags
        )
        
        # Add the template
        self.templates[template_id] = template
        
        # Create a spell from this template
        return self.create_spell_from_template(
            template_id=template_id,
            caster_id=caster_id,
            location_id=location_id
        )
    
    def modify_spell(
        self,
        spell_id: str,
        modifications: Dict[str, Any]
    ) -> Optional[Spell]:
        """
        Apply custom modifications to an existing spell.
        
        Args:
            spell_id: ID of the spell to modify
            modifications: Dictionary of modifications to apply
            
        Returns:
            The modified spell or None if spell not found
        """
        if spell_id not in self.spells:
            return None
        
        spell = self.spells[spell_id]
        
        # Update the modifications
        for key, value in modifications.items():
            spell.modifications[key] = value
        
        # Re-apply all modifications
        spell._apply_modifications()
        
        return spell
    
    def get_recommended_casting_locations(
        self,
        template_id: str,
        region_id: str,
        poi_list: List[str]
    ) -> List[Tuple[str, float]]:
        """
        Get recommended locations for casting a specific spell in a region.
        
        Args:
            template_id: ID of the spell template
            region_id: ID of the region to search in
            poi_list: List of POI IDs in the region
            
        Returns:
            List of (poi_id, score) tuples, sorted by score (higher is better)
        """
        if template_id not in self.templates:
            return []
        
        template = self.templates[template_id]
        
        results = []
        for poi_id in poi_list:
            # Get this location's magical properties
            magical_props = self.leyline_manager.get_magical_properties_for_poi(poi_id)
            
            if not magical_props:
                continue
            
            # Base score is the location's magical strength
            score = magical_props["magical_strength"] * 10  # 0-10 points
            
            # Bonus for stability
            stability_bonus = {
                "very_stable": 3.0,
                "stable": 2.0,
                "fluctuating": 1.0,
                "unstable": 0.0,
                "chaotic": -1.0
            }.get(magical_props["stability"], 0.0)
            score += stability_bonus
            
            # Check for element affinities
            template_elements = [e.value for e in template.base_elements]
            for element in template_elements:
                if element in magical_props["affinities"]:
                    score += magical_props["affinities"][element] * 5  # 0-5 points per element
            
            # Purpose-specific bonuses
            if template.purpose == SpellPurpose.ATTACK and "fire" in magical_props["affinities"]:
                score += magical_props["affinities"]["fire"] * 2
            elif template.purpose == SpellPurpose.HEALING and "life" in magical_props["affinities"]:
                score += magical_props["affinities"]["life"] * 2
            
            # Add some randomness to make it interesting
            score += random.uniform(-0.5, 0.5)
            
            results.append((poi_id, score))
        
        # Sort by score, highest first
        return sorted(results, key=lambda x: x[1], reverse=True)
    
    def generate_spell_outcome_narrative(
        self,
        spell: Spell,
        caster_name: str,
        target_name: Optional[str] = None,
        location_name: Optional[str] = None,
        success_level: float = 1.0  # 0.0 to 1.0
    ) -> str:
        """
        Generate a narrative description of a spell's casting and outcome.
        
        Args:
            spell: The spell being cast
            caster_name: Name of the caster
            target_name: Name of the target (if applicable)
            location_name: Name of the location (if applicable)
            success_level: How successful the casting was (0.0 to 1.0)
            
        Returns:
            Narrative description of the spell's outcome
        """
        # Determine outcome category based on success level
        if success_level >= 0.95:
            outcome = "exceptional_success"
        elif success_level >= 0.8:
            outcome = "strong_success"
        elif success_level >= 0.6:
            outcome = "success"
        elif success_level >= 0.4:
            outcome = "partial_success"
        elif success_level >= 0.2:
            outcome = "weak_effect"
        else:
            outcome = "failure"
        
        # Build the narrative
        narrative = ""
        
        # Opening - describe the casting
        casting_descriptions = {
            SpellPurpose.ATTACK: [
                f"{caster_name} channels destructive energy",
                f"{caster_name} gathers power for an attack",
                f"{caster_name} focuses on offensive magic"
            ],
            SpellPurpose.DEFENSE: [
                f"{caster_name} weaves protective energies",
                f"{caster_name} raises magical defenses",
                f"{caster_name} creates a magical barrier"
            ],
            SpellPurpose.HEALING: [
                f"{caster_name} channels restorative magic",
                f"{caster_name} focuses on healing energies",
                f"{caster_name} summons the power of restoration"
            ],
            SpellPurpose.UTILITY: [
                f"{caster_name} weaves practical magic",
                f"{caster_name} channels useful energies",
                f"{caster_name} focuses on magical utility"
            ],
            SpellPurpose.DIVINATION: [
                f"{caster_name} opens their mind to hidden knowledge",
                f"{caster_name} seeks magical insight",
                f"{caster_name} channels divinatory energies"
            ],
            SpellPurpose.ENHANCEMENT: [
                f"{caster_name} focuses on strengthening magic",
                f"{caster_name} channels empowering energies",
                f"{caster_name} weaves enhancement magic"
            ],
            SpellPurpose.TRANSFORMATION: [
                f"{caster_name} begins to shape transmutation magic",
                f"{caster_name} focuses on changing reality",
                f"{caster_name} channels transformative energies"
            ],
            SpellPurpose.SUMMONING: [
                f"{caster_name} opens a pathway to another realm",
                f"{caster_name} calls forth extradimensional energies",
                f"{caster_name} weaves summoning magic"
            ],
            SpellPurpose.BINDING: [
                f"{caster_name} prepares binding magic",
                f"{caster_name} weaves constraining energies",
                f"{caster_name} focuses on magical restraint"
            ],
            SpellPurpose.ILLUSION: [
                f"{caster_name} begins crafting false reality",
                f"{caster_name} weaves illusion magic",
                f"{caster_name} channels deceptive energies"
            ]
        }.get(spell.template.purpose, [f"{caster_name} casts a spell"])
        
        narrative += random.choice(casting_descriptions)
        
        # Add location detail if provided
        if location_name:
            location_phrases = [
                f" in {location_name}",
                f" while at {location_name}",
                f" from within {location_name}"
            ]
            narrative += random.choice(location_phrases)
        
        # Add spell name and target
        narrative += f", casting {spell.get_display_name()}"
        
        if target_name and spell.template.purpose in [SpellPurpose.ATTACK, SpellPurpose.HEALING, SpellPurpose.ENHANCEMENT]:
            narrative += f" at {target_name}"
        
        # Describe the elements involved
        if spell.elements:
            element_descriptions = []
            for element in spell.elements:
                if element == SpellElement.FIRE:
                    element_descriptions.append("flames lick around their fingers")
                elif element == SpellElement.WATER:
                    element_descriptions.append("water droplets form in the air")
                elif element == SpellElement.EARTH:
                    element_descriptions.append("the ground trembles slightly")
                elif element == SpellElement.AIR:
                    element_descriptions.append("a gentle breeze swirls around them")
                elif element == SpellElement.LIGHT:
                    element_descriptions.append("light gathers and intensifies")
                elif element == SpellElement.SHADOW:
                    element_descriptions.append("shadows deepen and dance")
                elif element == SpellElement.LIFE:
                    element_descriptions.append("a gentle green glow emanates")
                elif element == SpellElement.DEATH:
                    element_descriptions.append("a cold chill spreads outward")
                elif element == SpellElement.MIND:
                    element_descriptions.append("their eyes glow with mental energy")
                elif element == SpellElement.VOID:
                    element_descriptions.append("reality seems to waver")
                elif element == SpellElement.TIME:
                    element_descriptions.append("time seems to stutter briefly")
                elif element == SpellElement.SPACE:
                    element_descriptions.append("space warps and bends")
            
            if element_descriptions:
                narrative += ". As they cast, " + element_descriptions[0]
                if len(element_descriptions) > 1:
                    narrative += " and " + element_descriptions[1]
            
        # Describe the outcome based on success level
        narrative += ". "
        
        outcome_descriptions = {
            "exceptional_success": [
                f"The spell manifests with extraordinary power, far exceeding expectations!",
                f"An incredible surge of magical energy makes the spell exceptionally potent!",
                f"The spell works flawlessly, with effects more powerful than {caster_name} anticipated!"
            ],
            "strong_success": [
                f"The spell works very well, with impressive results.",
                f"The magic flows powerfully, creating strong effects.",
                f"The spell manifests with greater than usual strength."
            ],
            "success": [
                f"The spell works as intended.",
                f"The magic takes effect successfully.",
                f"The spell manifests according to {caster_name}'s will."
            ],
            "partial_success": [
                f"The spell works, but with somewhat diminished effects.",
                f"The magic is unstable, producing a weaker version of the intended effect.",
                f"The spell partially succeeds, though not at full strength."
            ],
            "weak_effect": [
                f"The spell barely works, producing only minimal effects.",
                f"The magic fizzles, leaving only a weak trace of the intended spell.",
                f"The spell's energy dissipates quickly, leaving little impact."
            ],
            "failure": [
                f"The spell fails, the magical energies dispersing harmlessly.",
                f"The magic collapses before manifesting any significant effect.",
                f"The spell fizzles out completely, failing to achieve its purpose."
            ]
        }
        
        narrative += random.choice(outcome_descriptions[outcome])
        
        # Add specific details based on the spell's purpose and outcome
        if outcome in ["exceptional_success", "strong_success", "success"] and target_name:
            if spell.template.purpose == SpellPurpose.ATTACK:
                damage_descriptions = [
                    f" {target_name} is struck with devastating force!",
                    f" {target_name} takes significant damage from the magical assault!",
                    f" The attack connects powerfully with {target_name}!"
                ]
                narrative += random.choice(damage_descriptions)
            elif spell.template.purpose == SpellPurpose.HEALING:
                healing_descriptions = [
                    f" {target_name}'s wounds close and heal rapidly!",
                    f" Restorative energy flows through {target_name}, mending injuries!",
                    f" {target_name} feels vitality return as the healing magic takes effect!"
                ]
                narrative += random.choice(healing_descriptions)
        
        # Add environmental effects for powerful spells
        if outcome in ["exceptional_success", "strong_success"] and spell.actual_power > 10:
            environment_effects = [
                " The surrounding area briefly resonates with magical energy.",
                " Nearby objects vibrate in response to the magical disturbance.",
                " The air shimmers with residual magical power.",
                " A burst of magical feedback sends ripples through the local environment."
            ]
            narrative += random.choice(environment_effects)
        
        return narrative