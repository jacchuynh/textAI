"""
Magic Combat Integration Module

This module integrates the magic system with the combat system,
allowing for spells to be cast during combat, magical effects to influence
combat outcomes, and environmental magic to affect combat scenarios.
"""

import random
from typing import Dict, List, Any, Optional, Tuple, Union

# Import magic system components
from game_engine.magic_system import (
    MagicSystem,
    MagicUser,
    Spell,
    DamageType,
    EffectType,
    LocationMagicProfile
)

class Combatant:
    """Basic combatant class for combat system."""
    
    def __init__(
        self,
        name: str,
        domains: Dict,
        max_health: int,
        current_health: int,
        max_stamina: int,
        current_stamina: int,
        max_focus: int,
        current_focus: int,
        max_spirit: int,
        current_spirit: int
    ):
        self.name = name
        self.domains = domains
        self.max_health = max_health
        self.current_health = current_health
        self.max_stamina = max_stamina
        self.current_stamina = current_stamina
        self.max_focus = max_focus
        self.current_focus = current_focus
        self.max_spirit = max_spirit
        self.current_spirit = current_spirit
        self.status_effects = []
        self.magic_profile = None  # Will be set by the combat manager
    
    def is_alive(self) -> bool:
        """Check if the combatant is alive."""
        return self.current_health > 0
    
    def take_damage(self, amount: int, damage_type: Optional[DamageType] = None) -> int:
        """
        Apply damage to the combatant.
        
        Args:
            amount: The amount of damage to apply
            damage_type: Optional type of damage
            
        Returns:
            The actual amount of damage applied
        """
        # Apply resistances if applicable
        actual_damage = amount
        if damage_type and hasattr(self, 'magic_profile') and self.magic_profile:
            if hasattr(self.magic_profile, 'resistance') and damage_type in self.magic_profile.resistance:
                resistance = self.magic_profile.resistance[damage_type]
                actual_damage = int(amount * (1.0 - resistance))
        
        # Apply damage
        self.current_health = max(0, self.current_health - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Heal the combatant.
        
        Args:
            amount: The amount to heal
            
        Returns:
            The actual amount healed
        """
        original_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        return self.current_health - original_health
    
    def add_status_effect(self, effect: Any) -> None:
        """
        Add a status effect to the combatant.
        
        Args:
            effect: The effect to add
        """
        self.status_effects.append(effect)
    
    def update_status_effects(self) -> List[Dict[str, Any]]:
        """
        Update status effects, removing expired ones.
        
        Returns:
            List of expired effect data
        """
        active_effects = []
        expired_effects = []
        
        for effect in self.status_effects:
            if effect.is_active():
                active_effects.append(effect)
            else:
                expired_effects.append({
                    "name": effect.name if hasattr(effect, 'name') else "Unknown Effect",
                    "description": effect.description if hasattr(effect, 'description') else "",
                    "type": effect.effect_type.name if hasattr(effect, 'effect_type') else "Unknown"
                })
        
        self.status_effects = active_effects
        return expired_effects

class CombatMove:
    """A move that can be performed in combat."""
    
    def __init__(
        self,
        name: str,
        description: str,
        move_type: 'MoveType',
        domains: List,
        base_damage: int,
        stamina_cost: int,
        focus_cost: int,
        spirit_cost: int,
        spell_id: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.move_type = move_type
        self.domains = domains
        self.base_damage = base_damage
        self.stamina_cost = stamina_cost
        self.focus_cost = focus_cost
        self.spirit_cost = spirit_cost
        self.spell_id = spell_id  # If this move is a spell, the spell ID

class MoveType:
    """Types of combat moves."""
    FORCE = "FORCE"       # Offensive, damage-dealing moves
    DEFEND = "DEFEND"     # Defensive, damage-reducing moves
    FOCUS = "FOCUS"       # Utility, buff/debuff moves
    SPECIAL = "SPECIAL"   # Special moves with unique effects
    SPELL = "SPELL"       # Magical spell moves

class Status:
    """Status effects that can be applied during combat."""
    POISONED = "POISONED"
    BURNING = "BURNING"
    FROZEN = "FROZEN"
    STUNNED = "STUNNED"
    BLEEDING = "BLEEDING"
    PROTECTED = "PROTECTED"
    EMPOWERED = "EMPOWERED"
    WEAKENED = "WEAKENED"

class MagicalCombatManager:
    """Manages the integration of magic with combat."""
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the magical combat manager.
        
        Args:
            magic_system: The magic system
        """
        self.magic_system = magic_system
        self.combatants = []
        self.location_magic = None
        self.combat_active = False
        self.turn_number = 0
        self.combatant_magic_profiles = {}  # Map of combatant to magic profile
    
    def initialize_combat(self, combatants: List[Combatant], location_description: Optional[str] = None) -> Dict[str, Any]:
        """
        Initialize combat with the given combatants.
        
        Args:
            combatants: The combatants participating in combat
            location_description: Optional description of the combat location
            
        Returns:
            Dict with result information
        """
        self.combatants = combatants
        self.combat_active = True
        self.turn_number = 0
        
        # Initialize location magic if description provided
        if location_description:
            self.location_magic = self.magic_system.initialize_location_magic(location_description)
        else:
            self.location_magic = None
        
        # Initialize magic profiles for combatants
        for combatant in combatants:
            if not hasattr(combatant, 'magic_profile') or combatant.magic_profile is None:
                # Create a magic profile for the combatant
                magic_profile = self.magic_system.initialize_magic_user(combatant.domains)
                combatant.magic_profile = magic_profile
                self.combatant_magic_profiles[combatant] = magic_profile
        
        return {
            "success": True,
            "message": f"Combat initialized with {len(combatants)} combatants",
            "combatants": [combatant.name for combatant in combatants],
            "location_magic": self.location_magic.get_details() if self.location_magic else None
        }
    
    def get_combatants(self) -> List[Combatant]:
        """Get the list of combatants."""
        return self.combatants
    
    def get_location_magic(self) -> Optional[LocationMagicProfile]:
        """Get the location magic profile."""
        return self.location_magic
    
    def get_combatant_magic_status(self, combatant: Combatant) -> Dict[str, Any]:
        """
        Get the magic status of a combatant.
        
        Args:
            combatant: The combatant
            
        Returns:
            Dict with magic status information
        """
        if combatant not in self.combatant_magic_profiles:
            return {
                "has_mana_heart": False,
                "mana_current": 0,
                "mana_max": 0,
                "ley_energy": 0,
                "known_spells_count": 0,
                "active_effects_count": 0
            }
        
        magic_profile = self.combatant_magic_profiles[combatant]
        return {
            "has_mana_heart": magic_profile.has_mana_heart,
            "mana_current": magic_profile.mana_current,
            "mana_max": magic_profile.mana_max,
            "mana_regeneration": magic_profile.mana_regeneration_rate,
            "ley_energy": magic_profile.current_ley_energy,
            "known_spells_count": len(magic_profile.known_spells),
            "active_effects_count": len(magic_profile.active_effects)
        }
    
    def get_available_combat_spells(self, combatant: Combatant) -> List[Dict[str, Any]]:
        """
        Get available combat spells for a combatant.
        
        Args:
            combatant: The combatant
            
        Returns:
            List of available spell information
        """
        if combatant not in self.combatant_magic_profiles:
            return []
        
        magic_profile = self.combatant_magic_profiles[combatant]
        
        # Get all known spells
        available_spells = []
        for spell_id in magic_profile.known_spells:
            spell = self.magic_system.get_spell_by_id(spell_id)
            if not spell:
                continue
            
            # Check if the spell can be cast
            can_cast, reason = spell.can_cast(magic_profile, combatant.domains)
            
            # Create a combat move for this spell
            combat_move = self._create_combat_move_from_spell(spell)
            
            available_spells.append({
                "spell_id": spell_id,
                "name": spell.name,
                "description": spell.description,
                "tier": spell.tier.name,
                "mana_cost": spell.mana_cost,
                "ley_energy_cost": spell.ley_energy_cost,
                "can_cast": can_cast,
                "reason": reason if not can_cast else "",
                "combat_move": {
                    "name": combat_move.name,
                    "description": combat_move.description,
                    "move_type": combat_move.move_type,
                    "base_damage": combat_move.base_damage,
                    "stamina_cost": combat_move.stamina_cost,
                    "focus_cost": combat_move.focus_cost,
                    "spirit_cost": combat_move.spirit_cost
                }
            })
        
        return available_spells
    
    def _create_combat_move_from_spell(self, spell: Spell) -> CombatMove:
        """
        Create a combat move from a spell.
        
        Args:
            spell: The spell
            
        Returns:
            A combat move
        """
        # Determine base damage based on spell effects
        base_damage = 0
        for effect in spell.effects:
            if effect.effect_type == EffectType.DAMAGE:
                base_damage += effect.potency
        
        # Map spell domains to combatant domains
        domains = []
        for req in spell.domain_requirements:
            domains.append(req.domain)
        
        # Determine move type based on spell effects
        move_type = MoveType.SPELL
        for effect in spell.effects:
            if effect.effect_type == EffectType.DAMAGE:
                move_type = MoveType.FORCE
                break
            elif effect.effect_type == EffectType.BUFF:
                move_type = MoveType.FOCUS
                break
            elif effect.effect_type == EffectType.CONTROL:
                move_type = MoveType.SPECIAL
                break
        
        # Create the combat move
        return CombatMove(
            name=spell.name,
            description=spell.description,
            move_type=move_type,
            domains=domains,
            base_damage=base_damage,
            stamina_cost=0,
            focus_cost=int(spell.mana_cost / 10),  # Convert mana cost to focus cost
            spirit_cost=0,
            spell_id=spell.id
        )
    
    def draw_from_combat_leyline(self, combatant: Combatant, max_draw: int) -> Dict[str, Any]:
        """
        Draw energy from the combat location's leyline.
        
        Args:
            combatant: The combatant drawing energy
            max_draw: The maximum amount to draw
            
        Returns:
            Dict with result information
        """
        if combatant not in self.combatant_magic_profiles:
            return {
                "success": False,
                "message": "Combatant does not have a magic profile"
            }
        
        if not self.location_magic:
            return {
                "success": False,
                "message": "No leyline detected in this location"
            }
        
        magic_profile = self.combatant_magic_profiles[combatant]
        
        # Draw energy
        leyline_strength = self.location_magic.leyline_strength
        amount_drawn = magic_profile.draw_from_leyline(leyline_strength, max_draw)
        
        return {
            "success": True,
            "message": f"Drew {amount_drawn} ley energy from the combat location",
            "amount_drawn": amount_drawn,
            "current_ley_energy": magic_profile.current_ley_energy
        }
    
    def execute_magical_combat_move(self, caster: Combatant, target: Combatant, spell_id: str) -> Dict[str, Any]:
        """
        Execute a magical combat move (cast a spell).
        
        Args:
            caster: The combatant casting the spell
            target: The target combatant
            spell_id: The ID of the spell to cast
            
        Returns:
            Dict with result information
        """
        if not self.combat_active:
            return {
                "success": False,
                "message": "Combat is not active"
            }
        
        if caster not in self.combatant_magic_profiles:
            return {
                "success": False,
                "message": "Caster does not have a magic profile"
            }
        
        magic_profile = self.combatant_magic_profiles[caster]
        
        # Check if the spell is known
        if spell_id not in magic_profile.known_spells:
            return {
                "success": False,
                "message": f"Spell {spell_id} is not known"
            }
        
        # Get the spell
        spell = self.magic_system.get_spell_by_id(spell_id)
        if not spell:
            return {
                "success": False,
                "message": f"Spell {spell_id} not found in the magic system"
            }
        
        # Cast the spell
        result = spell.cast(
            caster_id=caster.name,
            caster_magic=magic_profile,
            caster_domains=caster.domains,
            targets=[target],
            location_magic=self.location_magic
        )
        
        # If the spell failed, return the failure
        if not result.get("success", False):
            return result
        
        # Process spell effects
        combat_effects = []
        for target_data in result.get("effect_results", []):
            target_obj = target_data.get("target")
            for effect_result in target_data.get("results", []):
                # Process effect based on type
                effect_type = effect_result.get("effect_details", {}).get("type")
                
                if effect_type == EffectType.DAMAGE.name:
                    damage = effect_result.get("damage_dealt", 0)
                    damage_type = effect_result.get("effect_details", {}).get("damage_type")
                    combat_effects.append({
                        "type": "damage",
                        "amount": damage,
                        "damage_type": damage_type,
                        "target": target_obj.name
                    })
                
                elif effect_type == EffectType.HEALING.name:
                    healing = effect_result.get("healing_done", 0)
                    combat_effects.append({
                        "type": "healing",
                        "amount": healing,
                        "target": target_obj.name
                    })
                
                # Handle other effect types
        
        # Generate combat narration
        combat_narration = f"{caster.name} casts {spell.name}!"
        
        for effect in combat_effects:
            if effect["type"] == "damage":
                combat_narration += f" {effect['target']} takes {effect['amount']} {effect['damage_type']} damage!"
            elif effect["type"] == "healing":
                combat_narration += f" {effect['target']} is healed for {effect['amount']} health!"
        
        return {
            "success": True,
            "message": result["message"],
            "combat_narration": combat_narration,
            "combat_effects": combat_effects,
            "mana_used": result["mana_used"],
            "ley_energy_used": result["ley_energy_used"]
        }
    
    def generate_magical_environment_effect(self) -> Optional[Dict[str, Any]]:
        """
        Generate a random magical environment effect based on the location.
        
        Returns:
            Dict with effect information or None if no effect
        """
        if not self.location_magic or self.location_magic.leyline_strength < 0.5:
            return None
        
        # Higher chance of effects in magical locations
        chance = min(0.3, self.location_magic.leyline_strength * 0.1)
        if random.random() > chance:
            return None
        
        # Potential effect types
        effect_types = [
            "mana_surge",
            "leyline_fluctuation",
            "elemental_manifestation",
            "arcane_disturbance",
            "magical_resonance"
        ]
        
        # Select an effect type
        effect_type = random.choice(effect_types)
        
        # Generate effect details based on type and location magic
        if effect_type == "mana_surge":
            return {
                "effect_type": effect_type,
                "description": "A surge of mana flows through the area, enhancing magical abilities.",
                "effect": "All spells cost 25% less mana this turn"
            }
        
        elif effect_type == "leyline_fluctuation":
            return {
                "effect_type": effect_type,
                "description": "The leylines fluctuate, causing unpredictable magical effects.",
                "effect": "Random spell effects may be amplified or diminished"
            }
        
        elif effect_type == "elemental_manifestation":
            # Choose an element based on dominant aspects
            elements = [aspect.name.lower() for aspect in self.location_magic.dominant_magic_aspects]
            element = random.choice(elements) if elements else "arcane"
            
            return {
                "effect_type": effect_type,
                "description": f"The {element} energy in the area manifests briefly, affecting the battlefield.",
                "effect": f"All {element} spells are 50% more effective this turn"
            }
        
        elif effect_type == "arcane_disturbance":
            return {
                "effect_type": effect_type,
                "description": "A disturbance in the arcane field makes it harder to control magic.",
                "effect": "Spellcasting requires a focus check or may fail"
            }
        
        elif effect_type == "magical_resonance":
            return {
                "effect_type": effect_type,
                "description": "The area resonates with magical energy, enhancing certain magical properties.",
                "effect": "Drawing from leylines is twice as effective this turn"
            }
        
        return None
    
    def update_magic_resources_end_of_turn(self, combatant: Combatant) -> Dict[str, Any]:
        """
        Update magic resources at the end of a turn.
        
        Args:
            combatant: The combatant
            
        Returns:
            Dict with update information
        """
        if combatant not in self.combatant_magic_profiles:
            return {}
        
        magic_profile = self.combatant_magic_profiles[combatant]
        
        # Regenerate mana
        mana_regenerated = magic_profile.update_mana_regeneration()
        
        # Update active effects
        expired_effects = magic_profile.update_active_effects()
        
        # Apply location bonus if applicable
        location_bonus = 0
        if self.location_magic:
            regen_bonus = self.location_magic.get_mana_regeneration_bonus()
            location_bonus = int(magic_profile.mana_max * regen_bonus * 0.01)
            if location_bonus > 0:
                old_mana = magic_profile.mana_current
                magic_profile.mana_current = min(magic_profile.mana_current + location_bonus, magic_profile.mana_max)
                location_bonus = magic_profile.mana_current - old_mana
        
        return {
            "mana_regenerated": mana_regenerated + location_bonus,
            "current_mana": magic_profile.mana_current,
            "max_mana": magic_profile.mana_max,
            "expired_effects": expired_effects
        }
    
    def simulate_combat_victory(self, victor_id: str) -> Dict[str, Any]:
        """
        Simulate a combat victory for testing purposes.
        
        Args:
            victor_id: The ID of the victor
            
        Returns:
            Dict with victory information
        """
        # Find the victor
        victor = None
        for combatant in self.combatants:
            if combatant.name == victor_id:
                victor = combatant
                break
        
        if not victor:
            return {
                "success": False,
                "message": f"Combatant {victor_id} not found"
            }
        
        # Set all other combatants to 0 health
        for combatant in self.combatants:
            if combatant != victor:
                combatant.current_health = 0
        
        # End combat
        self.combat_active = False
        
        return {
            "success": True,
            "message": f"{victor_id} is victorious!",
            "victor": victor_id,
            "defeated": [c.name for c in self.combatants if c != victor]
        }

class MonsterMagicIntegration:
    """Integrates magic with monsters for combat."""
    
    def __init__(self, magic_system: MagicSystem):
        """
        Initialize the monster magic integration.
        
        Args:
            magic_system: The magic system
        """
        self.magic_system = magic_system
    
    def enhance_monster_with_magic(
        self,
        monster: Combatant,
        monster_moves: List[CombatMove],
        monster_type: str,
        monster_tier: str
    ) -> Tuple[Combatant, List[CombatMove], MagicUser]:
        """
        Enhance a monster with magical abilities.
        
        Args:
            monster: The monster to enhance
            monster_moves: The monster's current moves
            monster_type: The type of monster (e.g., "MAGICAL", "ELEMENTAL")
            monster_tier: The tier of the monster (e.g., "NORMAL", "ELITE", "BOSS")
            
        Returns:
            Tuple of (enhanced monster, enhanced moves, magic profile)
        """
        # Initialize magic profile for the monster
        magic_profile = self.magic_system.initialize_magic_user(monster.domains)
        
        # Apply enhancements based on monster type and tier
        if monster_type == "MAGICAL":
            # Magical monsters always have a mana heart
            if not magic_profile.has_mana_heart:
                self.magic_system.develop_mana_heart(monster.name, magic_profile)
            
            # Add bonus mana based on tier
            if monster_tier == "ELITE":
                magic_profile.mana_max *= 1.5
                magic_profile.mana_current = magic_profile.mana_max
            elif monster_tier == "BOSS":
                magic_profile.mana_max *= 2.0
                magic_profile.mana_current = magic_profile.mana_max
        
        elif monster_type == "ELEMENTAL":
            # Elemental monsters have affinity with their element
            elemental_domains = [domain for domain in monster.domains if domain in [
                Domain.FIRE, Domain.WATER, Domain.EARTH, Domain.AIR, 
                Domain.LIGHT, Domain.DARKNESS
            ]]
            
            if elemental_domains:
                primary_element = max(elemental_domains, key=lambda d: monster.domains[d])
                
                # Map domain to damage type
                element_map = {
                    Domain.FIRE: DamageType.FIRE,
                    Domain.WATER: DamageType.WATER,
                    Domain.EARTH: DamageType.EARTH,
                    Domain.AIR: DamageType.AIR,
                    Domain.LIGHT: DamageType.LIGHT,
                    Domain.DARKNESS: DamageType.DARKNESS
                }
                
                element_type = element_map.get(primary_element)
                if element_type:
                    # Add elemental affinity
                    if not magic_profile.affinity:
                        magic_profile.affinity = {}
                    magic_profile.affinity[element_type] = 0.5  # 50% increased effectiveness
                    
                    # Add resistance to the same element
                    if not magic_profile.resistance:
                        magic_profile.resistance = {}
                    magic_profile.resistance[element_type] = 0.5  # 50% resistance
        
        # Add spells based on monster's domains and tier
        self._add_monster_spells(monster, magic_profile, monster_tier)
        
        # Create new magical combat moves
        enhanced_moves = list(monster_moves)  # Start with existing moves
        
        # Add magical moves based on known spells
        for spell_id in magic_profile.known_spells:
            spell = self.magic_system.get_spell_by_id(spell_id)
            if spell:
                # Create a combat move from this spell
                move = self._create_monster_spell_move(spell)
                enhanced_moves.append(move)
        
        # Assign magic profile to monster
        monster.magic_profile = magic_profile
        
        return monster, enhanced_moves, magic_profile
    
    def _add_monster_spells(self, monster: Combatant, magic_profile: MagicUser, monster_tier: str) -> None:
        """
        Add appropriate spells to a monster based on its domains and tier.
        
        Args:
            monster: The monster
            magic_profile: The monster's magic profile
            monster_tier: The tier of the monster
        """
        # Determine number of spells based on tier
        num_spells = 1  # Normal monsters get 1 spell
        if monster_tier == "ELITE":
            num_spells = 2
        elif monster_tier == "BOSS":
            num_spells = 3
        
        # Find the monster's highest domains
        sorted_domains = sorted(monster.domains.items(), key=lambda x: x[1], reverse=True)
        primary_domains = [domain for domain, value in sorted_domains[:3] if value >= 2]
        
        # Get available spells from the magic system
        available_spells = []
        for spell_id, spell in self.magic_system._spells.items():
            # Check if the monster meets the domain requirements
            meets_requirements = True
            for req in spell.domain_requirements:
                if not req.check_requirement(monster.domains):
                    meets_requirements = False
                    break
            
            if meets_requirements:
                available_spells.append(spell)
        
        # Filter to appropriate tier
        tier_map = {
            "NORMAL": [MagicTier.CANTRIP, MagicTier.APPRENTICE],
            "ELITE": [MagicTier.CANTRIP, MagicTier.APPRENTICE, MagicTier.ADEPT],
            "BOSS": [MagicTier.APPRENTICE, MagicTier.ADEPT, MagicTier.EXPERT]
        }
        
        allowed_tiers = tier_map.get(monster_tier, [MagicTier.CANTRIP, MagicTier.APPRENTICE])
        available_spells = [spell for spell in available_spells if spell.tier in allowed_tiers]
        
        # If no spells available, add a basic spell
        if not available_spells and "FIRE" in monster.domains and monster.domains["FIRE"] >= 2:
            magic_profile.learn_spell("spell_fire_bolt")
            num_spells -= 1
        
        # Add random spells from available ones
        for _ in range(min(num_spells, len(available_spells))):
            spell = random.choice(available_spells)
            magic_profile.learn_spell(spell.id)
            available_spells.remove(spell)
    
    def _create_monster_spell_move(self, spell: Spell) -> CombatMove:
        """
        Create a combat move from a spell for a monster.
        
        Args:
            spell: The spell
            
        Returns:
            A combat move
        """
        # Determine base damage based on spell effects
        base_damage = 0
        for effect in spell.effects:
            if effect.effect_type == EffectType.DAMAGE:
                base_damage += effect.potency
        
        # Map spell domains to combatant domains
        domains = []
        for req in spell.domain_requirements:
            domains.append(req.domain)
        
        # Determine move type based on spell effects
        move_type = MoveType.SPELL
        for effect in spell.effects:
            if effect.effect_type == EffectType.DAMAGE:
                move_type = MoveType.FORCE
                break
            elif effect.effect_type == EffectType.BUFF:
                move_type = MoveType.FOCUS
                break
            elif effect.effect_type == EffectType.CONTROL:
                move_type = MoveType.SPECIAL
                break
        
        # Create the combat move
        return CombatMove(
            name=spell.name,
            description=spell.description,
            move_type=move_type,
            domains=domains,
            base_damage=base_damage,
            stamina_cost=0,
            focus_cost=int(spell.mana_cost / 10),  # Convert mana cost to focus cost
            spirit_cost=0,
            spell_id=spell.id
        )

# Initialize magic combat integration services
def create_magic_integration_services(magic_system: Optional[MagicSystem] = None) -> Dict[str, Any]:
    """
    Create and return all magic integration services.
    """
    # Create or use provided magic system
    magic_sys = magic_system or MagicSystem()
    
    # Create integration services
    combat_manager = MagicalCombatManager(magic_sys)
    monster_integration = MonsterMagicIntegration(magic_sys)
    
    return {
        "magic_system": magic_sys,
        "combat_manager": combat_manager,
        "monster_integration": monster_integration
    }

# Initialize magic integration services
magic_integration = create_magic_integration_services()