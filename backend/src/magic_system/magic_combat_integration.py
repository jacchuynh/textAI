"""
Magic System Integration with Combat

This module integrates the magic system with the existing combat system,
allowing magical abilities to be used in combat scenarios.
"""

from typing import Dict, List, Any, Optional, Tuple
import random

from .magic_system import (
    MagicSystem, MagicUser, Spell, 
    MagicTier, MagicSource, EffectType, TargetType,
    LocationMagicProfile, DamageType
)
from .enhanced_combat.combat_system_core import (
    Combatant, CombatMove, Status, MoveType, Domain
)


class MagicalCombatManager:
    """
    Manager class for integrating magic with combat.
    
    This class handles:
    1. Converting spells to combat moves
    2. Processing magical effects in combat
    3. Handling magic-specific combat actions
    4. Managing magical resources during combat
    """
    
    def __init__(self, magic_system: MagicSystem):
        """Initialize the magical combat manager"""
        self.magic_system = magic_system
        self.combat_magic_profiles: Dict[str, MagicUser] = {}
        self.combat_location_magic: Optional[LocationMagicProfile] = None
    
    def initialize_combat(self, combatants: List[Combatant], location_description: str) -> None:
        """
        Initialize magic profiles for all combatants and the combat location.
        Called at the start of a combat encounter.
        """
        # Create a magic profile for the location
        self.combat_location_magic = self.magic_system.initialize_location_magic(location_description)
        
        # Create magic profiles for each combatant based on their domains
        for combatant in combatants:
            # Create magic profile
            magic_profile = self.magic_system.initialize_magic_user(combatant.domains)
            
            # Store in the dictionary
            self.combat_magic_profiles[combatant.name] = magic_profile
    
    def get_available_combat_spells(self, combatant: Combatant) -> List[Dict[str, Any]]:
        """
        Get all spells that can be used by the combatant in combat.
        Returns a list of spell details with associated combat move information.
        """
        # Get the magic profile for the combatant
        magic_profile = self.combat_magic_profiles.get(combatant.name)
        if not magic_profile:
            return []
        
        # Get all available spells organized by tier
        all_spells = self.magic_system.get_available_spells(magic_profile)
        
        # Flatten and filter to only include usable combat spells
        combat_spells = []
        
        # Process each tier of spells
        for tier, spells in all_spells.items():
            for spell_info in spells:
                # Only include known spells that can be cast
                if spell_info["known"] and spell_info["can_cast"]:
                    # Convert to combat move for display
                    spell = self.magic_system.casting_service.get_spell(spell_info["id"])
                    if spell:
                        combat_move = spell.to_combat_move()
                        
                        # Add to list with additional info
                        combat_spells.append({
                            "spell_id": spell_info["id"],
                            "name": spell_info["name"],
                            "description": spell_info["description"],
                            "tier": tier.name,
                            "mana_cost": spell_info["mana_cost"],
                            "ley_energy_cost": spell_info["ley_energy_cost"],
                            "combat_move": {
                                "name": combat_move.name,
                                "description": combat_move.description,
                                "move_type": combat_move.move_type.name,
                                "domains": [domain.name for domain in combat_move.domains],
                                "base_damage": combat_move.base_damage,
                                "stamina_cost": combat_move.stamina_cost,
                                "focus_cost": combat_move.focus_cost,
                                "spirit_cost": combat_move.spirit_cost,
                                "effects": combat_move.effects
                            }
                        })
        
        return combat_spells
    
    def execute_magical_combat_move(self, 
                                   actor: Combatant, 
                                   target: Combatant, 
                                   spell_id: str) -> Dict[str, Any]:
        """
        Execute a magical combat move based on a spell.
        Returns the result of the spell casting in a format suitable for combat.
        """
        # Get the magic profiles
        actor_magic = self.combat_magic_profiles.get(actor.name)
        if not actor_magic:
            return {
                "success": False,
                "message": f"No magic profile found for {actor.name}",
                "combat_narration": f"{actor.name} attempts to cast a spell, but something goes wrong."
            }
        
        # Cast the spell in combat
        result = self.magic_system.cast_combat_spell(
            caster=actor,
            caster_magic=actor_magic,
            spell_id=spell_id,
            target=target,
            location_magic=self.combat_location_magic or self.magic_system.initialize_location_magic("Neutral ground")
        )
        
        return result
    
    def update_magic_resources_end_of_turn(self, combatant: Combatant) -> Dict[str, Any]:
        """
        Update magical resources at the end of a combatant's turn.
        Returns a dictionary with the updated resource information.
        """
        # Get the magic profile
        magic_profile = self.combat_magic_profiles.get(combatant.name)
        if not magic_profile:
            return {}
        
        updates = {}
        
        # Regenerate mana if the combatant has a Mana Heart
        if magic_profile.has_mana_heart:
            mana_regenerated = magic_profile.regenerate_mana(seconds=6)  # 6 seconds per turn
            if mana_regenerated > 0:
                updates["mana_regenerated"] = mana_regenerated
                updates["current_mana"] = magic_profile.mana_current
                updates["max_mana"] = magic_profile.mana_max
        
        # Process active magical effects
        expired_effects = []
        for effect in magic_profile.active_magical_effects:
            # Reduce duration by one turn (6 seconds)
            if not effect.tick(seconds=6):
                # Effect has expired
                expired_effects.append(effect.effect_id)
        
        # Remove expired effects
        if expired_effects:
            magic_profile.active_magical_effects = [
                effect for effect in magic_profile.active_magical_effects 
                if effect.effect_id not in expired_effects
            ]
            updates["expired_effects"] = expired_effects
        
        return updates
    
    def draw_from_combat_leyline(self, combatant: Combatant, amount_desired: int) -> Dict[str, Any]:
        """
        Attempt to draw energy from the leylines during combat.
        Returns a dictionary with the result of the attempt.
        """
        # Get the magic profile
        magic_profile = self.combat_magic_profiles.get(combatant.name)
        if not magic_profile:
            return {
                "success": False,
                "message": f"No magic profile found for {combatant.name}"
            }
        
        # Get the location's leyline strength
        leyline_strength = 0
        if self.combat_location_magic:
            leyline_strength = self.combat_location_magic.leyline_strength
        
        # Attempt to draw energy
        amount_drawn = magic_profile.draw_from_leyline(leyline_strength, amount_desired)
        
        if amount_drawn > 0:
            return {
                "success": True,
                "message": f"Successfully drew {amount_drawn} ley energy",
                "amount_drawn": amount_drawn,
                "current_ley_energy": magic_profile.current_ley_energy,
                "combat_narration": f"{combatant.name} draws energy from the surrounding leylines, gathering {amount_drawn} points of magical energy."
            }
        else:
            # Check if corruption increased from failed attempt
            corruption_change = 0
            if magic_profile.corruption_level > 0:
                corruption_change = 1
            
            return {
                "success": False,
                "message": "Failed to draw ley energy",
                "corruption_increased": corruption_change > 0,
                "current_corruption": magic_profile.corruption_level,
                "combat_narration": f"{combatant.name} attempts to draw energy from the leylines but fails." + 
                                  (f" The magical backlash leaves a taint of corruption." if corruption_change > 0 else "")
            }
    
    def get_combatant_magic_status(self, combatant: Combatant) -> Dict[str, Any]:
        """
        Get the current magical status of a combatant.
        Returns a dictionary with the combatant's magical information.
        """
        # Get the magic profile
        magic_profile = self.combat_magic_profiles.get(combatant.name)
        if not magic_profile:
            return {
                "has_magic": False,
                "message": f"No magic profile found for {combatant.name}"
            }
        
        # Get basic magic information
        magic_status = {
            "has_magic": True,
            "has_mana_heart": magic_profile.has_mana_heart,
            "mana_current": magic_profile.mana_current,
            "mana_max": magic_profile.mana_max,
            "mana_regen_rate": magic_profile.mana_regeneration_rate,
            "ley_energy": magic_profile.current_ley_energy,
            "ley_sensitivity": magic_profile.ley_energy_sensitivity,
            "corruption_level": magic_profile.corruption_level,
            "known_spells_count": len(magic_profile.known_spells),
            "active_effects_count": len(magic_profile.active_magical_effects)
        }
        
        # Get any active magical effects
        if magic_profile.active_magical_effects:
            magic_status["active_effects"] = []
            for effect in magic_profile.active_magical_effects:
                magic_status["active_effects"].append({
                    "effect_id": effect.effect_id,
                    "effect_type": effect.source_effect.effect_type.name if effect.source_effect else "Unknown",
                    "remaining_duration": effect.remaining_duration,
                    "source_spell": effect.source_spell_id
                })
        
        # Get corruption effects if any
        if magic_profile.corruption_level > 0:
            corruption_info = self.magic_system.get_corruption_status(magic_profile)
            magic_status["corruption_tier"] = corruption_info["corruption_tier"]
            if corruption_info["effects"]:
                magic_status["corruption_effects"] = [e["name"] for e in corruption_info["effects"]]
        
        return magic_status
    
    def generate_magical_environment_effect(self) -> Optional[Dict[str, Any]]:
        """
        Generate a random magical environment effect based on the combat location.
        Returns a description and effect details, or None if no effect occurs.
        """
        # Check if the location has magical properties
        if not self.combat_location_magic or self.combat_location_magic.leyline_strength < 2:
            return None
        
        # Chance based on mana flux level
        flux_level = self.combat_location_magic.mana_flux_level.value
        chance = 0.05 * flux_level  # 5% per flux level
        
        if random.random() > chance:
            return None
        
        # Generate a random environmental effect
        effect_types = [
            "Wild magic surge",
            "Leyline flare",
            "Ambient energy shift",
            "Magical resonance",
            "Elemental manifestation"
        ]
        
        effect_type = random.choice(effect_types)
        
        # Get a random dominant aspect if available
        aspect = None
        if self.combat_location_magic.dominant_magic_aspects:
            aspect = random.choice(self.combat_location_magic.dominant_magic_aspects)
        
        # Generate effect details
        if effect_type == "Wild magic surge":
            description = "A surge of wild magic erupts from the leylines!"
            effect = "All spellcasting has increased power and backlash potential this turn."
        
        elif effect_type == "Leyline flare":
            description = "The leylines flare with energy, briefly visible to all!"
            effect = "Drawing from leylines is easier this turn, but may attract attention."
        
        elif effect_type == "Ambient energy shift":
            description = "The ambient magical energy shifts and flows unpredictably."
            effect = "Spells cost 1 less mana but have a 10% chance of unintended side effects."
        
        elif effect_type == "Magical resonance":
            description = "Magical energies begin to resonate with each other."
            effect = "Consecutive spells of the same type gain increased potency."
        
        elif effect_type == "Elemental manifestation":
            element = aspect.name if aspect else random.choice(["FIRE", "WATER", "EARTH", "AIR", "LIGHT", "DARKNESS"])
            description = f"A manifestation of {element} energy briefly appears!"
            effect = f"Spells using {element} energy are empowered, while opposing elements are weakened."
        
        return {
            "effect_type": effect_type,
            "description": description,
            "effect": effect,
            "aspect": aspect.name if aspect else None,
            "duration": "1 turn"
        }
    
    def cleanup_after_combat(self) -> None:
        """Clean up magical resources after combat ends"""
        # Reset the combat magic profiles
        self.combat_magic_profiles = {}
        self.combat_location_magic = None


# ======================================================================
# Monster Magic Integration
# ======================================================================

class MonsterMagicIntegration:
    """
    Integration class for adding magical abilities to monsters.
    
    This class handles:
    1. Generating magical abilities for monsters based on their domains
    2. Creating monster-specific spells and effects
    3. Enhancing monsters with magical traits
    """
    
    def __init__(self, magic_system: MagicSystem):
        """Initialize the monster magic integration"""
        self.magic_system = magic_system
    
    def enhance_monster_with_magic(self, 
                                  monster: Combatant, 
                                  monster_moves: List[CombatMove],
                                  threat_category: str,
                                  threat_tier: str) -> Tuple[Combatant, List[CombatMove], MagicUser]:
        """
        Enhance a monster with magical abilities based on its domains and threat level.
        Returns the enhanced monster, its moves (including magical ones), and its magic profile.
        """
        # Initialize a magic profile for the monster
        magic_profile = self.magic_system.initialize_magic_user(monster.domains)
        
        # Determine if the monster should have a Mana Heart based on tier
        if threat_tier in ["ELITE", "BOSS", "LEGENDARY"]:
            if not magic_profile.has_mana_heart:
                # Force a Mana Heart for higher-tier monsters
                magic_profile.has_mana_heart = True
                magic_profile.mana_max = 30 + (monster.get_avg_domain_value() * 3)
                magic_profile.mana_current = magic_profile.mana_max
                magic_profile.mana_regeneration_rate = 0.5
                magic_profile.known_skills.append("ManaHeartDeveloped")
        
        # Add magical abilities based on the monster's dominant domains
        dominant_domains = self._get_dominant_domains(monster)
        magical_moves = []
        
        # Add domain-specific magical abilities
        for domain in dominant_domains:
            # Generate appropriate magical moves
            domain_moves = self._generate_domain_magic_moves(domain, threat_tier, threat_category)
            magical_moves.extend(domain_moves)
            
            # Add the corresponding spells to the monster's known spells
            for move in domain_moves:
                if hasattr(move, "spell_id") and move.spell_id:
                    magic_profile.known_spells.append(move.spell_id)
        
        # Combine original moves and new magical moves
        all_moves = monster_moves + magical_moves
        
        return monster, all_moves, magic_profile
    
    def _get_dominant_domains(self, monster: Combatant) -> List[Domain]:
        """Get the monster's most powerful domains"""
        # Sort domains by value in descending order
        sorted_domains = sorted(monster.domains.items(), key=lambda x: x[1], reverse=True)
        
        # Take the top 2-3 domains
        count = min(3, len(sorted_domains))
        return [domain for domain, _ in sorted_domains[:count]]
    
    def _generate_domain_magic_moves(self, domain: Domain, threat_tier: str, threat_category: str) -> List[CombatMove]:
        """Generate magical combat moves based on a specific domain"""
        moves = []
        
        # Get power level multiplier based on threat tier
        power_multiplier = {
            "MINION": 0.5,
            "STANDARD": 1.0,
            "ELITE": 1.5,
            "BOSS": 2.0,
            "LEGENDARY": 3.0
        }.get(threat_tier, 1.0)
        
        # Generate domain-specific moves
        if domain == Domain.FIRE:
            # Create a fire attack move
            fire_move = CombatMove(
                name="Flame Burst",
                description="Unleashes a blast of magical fire",
                move_type=MoveType.FOCUS,
                domains=[Domain.FIRE, Domain.MIND],
                base_damage=int(10 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(5 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_FIRE"]
            )
            # Set a reference to a spell ID (would be created in a real implementation)
            setattr(fire_move, "spell_id", "monster_spell_flame_burst")
            moves.append(fire_move)
            
            if power_multiplier >= 1.5:
                # Add more powerful fire ability for stronger monsters
                inferno_move = CombatMove(
                    name="Inferno Vortex",
                    description="Creates a swirling vortex of intense flames",
                    move_type=MoveType.FOCUS,
                    domains=[Domain.FIRE, Domain.MIND],
                    base_damage=int(18 * power_multiplier),
                    stamina_cost=0,
                    focus_cost=int(10 * power_multiplier),
                    spirit_cost=0,
                    effects=["DAMAGE_FIRE", "AREA_EFFECT"]
                )
                setattr(inferno_move, "spell_id", "monster_spell_inferno_vortex")
                moves.append(inferno_move)
        
        elif domain == Domain.WATER:
            # Create a water attack move
            water_move = CombatMove(
                name="Crushing Wave",
                description="Summons a powerful wave of water",
                move_type=MoveType.FOCUS,
                domains=[Domain.WATER, Domain.MIND],
                base_damage=int(8 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(4 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_WATER", "KNOCKBACK"]
            )
            setattr(water_move, "spell_id", "monster_spell_crushing_wave")
            moves.append(water_move)
            
            if power_multiplier >= 1.5:
                # Add more powerful water ability for stronger monsters
                whirlpool_move = CombatMove(
                    name="Whirlpool",
                    description="Creates a powerful whirlpool that pulls and damages",
                    move_type=MoveType.FOCUS,
                    domains=[Domain.WATER, Domain.MIND],
                    base_damage=int(15 * power_multiplier),
                    stamina_cost=0,
                    focus_cost=int(8 * power_multiplier),
                    spirit_cost=0,
                    effects=["DAMAGE_WATER", "IMMOBILIZE"]
                )
                setattr(whirlpool_move, "spell_id", "monster_spell_whirlpool")
                moves.append(whirlpool_move)
        
        elif domain == Domain.EARTH:
            # Create an earth attack move
            earth_move = CombatMove(
                name="Stone Spikes",
                description="Causes stone spikes to erupt from the ground",
                move_type=MoveType.FOCUS,
                domains=[Domain.EARTH, Domain.MIND],
                base_damage=int(12 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(6 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_EARTH", "TERRAIN_CHANGE"]
            )
            setattr(earth_move, "spell_id", "monster_spell_stone_spikes")
            moves.append(earth_move)
            
            if power_multiplier >= 1.5:
                # Add defensive earth ability for stronger monsters
                stone_armor_move = CombatMove(
                    name="Stone Armor",
                    description="Covers the body in protective stone",
                    move_type=MoveType.DEFEND,
                    domains=[Domain.EARTH, Domain.BODY],
                    base_damage=0,
                    stamina_cost=0,
                    focus_cost=int(7 * power_multiplier),
                    spirit_cost=0,
                    effects=["DAMAGE_REDUCTION", "MOVEMENT_PENALTY"]
                )
                setattr(stone_armor_move, "spell_id", "monster_spell_stone_armor")
                moves.append(stone_armor_move)
        
        elif domain == Domain.AIR or domain == Domain.WIND:
            # Create an air attack move
            air_move = CombatMove(
                name="Lightning Strike",
                description="Calls down a bolt of lightning",
                move_type=MoveType.FOCUS,
                domains=[Domain.AIR if domain == Domain.AIR else Domain.WIND, Domain.MIND],
                base_damage=int(14 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(7 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_LIGHTNING", "STUN_CHANCE"]
            )
            setattr(air_move, "spell_id", "monster_spell_lightning_strike")
            moves.append(air_move)
            
            if power_multiplier >= 1.5:
                # Add mobility air ability for stronger monsters
                wind_rush_move = CombatMove(
                    name="Wind Rush",
                    description="Uses wind to dash with incredible speed",
                    move_type=MoveType.TRICK,
                    domains=[Domain.AIR if domain == Domain.AIR else Domain.WIND, Domain.AWARENESS],
                    base_damage=int(6 * power_multiplier),
                    stamina_cost=0,
                    focus_cost=int(5 * power_multiplier),
                    spirit_cost=0,
                    effects=["BONUS_ACTION", "POSITIONING"]
                )
                setattr(wind_rush_move, "spell_id", "monster_spell_wind_rush")
                moves.append(wind_rush_move)
        
        elif domain == Domain.LIGHT:
            # Create a light attack move
            light_move = CombatMove(
                name="Radiant Beam",
                description="Fires a beam of intense light",
                move_type=MoveType.FOCUS,
                domains=[Domain.LIGHT, Domain.MIND],
                base_damage=int(11 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(6 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_LIGHT", "BLIND_CHANCE"]
            )
            setattr(light_move, "spell_id", "monster_spell_radiant_beam")
            moves.append(light_move)
            
            if power_multiplier >= 1.5:
                # Add healing light ability for stronger monsters
                healing_light_move = CombatMove(
                    name="Healing Light",
                    description="Bathes in restorative light energy",
                    move_type=MoveType.UTILITY,
                    domains=[Domain.LIGHT, Domain.SPIRIT],
                    base_damage=0,
                    stamina_cost=0,
                    focus_cost=int(8 * power_multiplier),
                    spirit_cost=0,
                    effects=["HEAL_SELF", "REMOVE_DEBUFF"]
                )
                setattr(healing_light_move, "spell_id", "monster_spell_healing_light")
                moves.append(healing_light_move)
        
        elif domain == Domain.DARKNESS:
            # Create a darkness attack move
            darkness_move = CombatMove(
                name="Shadow Strike",
                description="Attacks with solidified shadows",
                move_type=MoveType.FOCUS,
                domains=[Domain.DARKNESS, Domain.MIND],
                base_damage=int(10 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(5 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_DARKNESS", "ENERGY_DRAIN"]
            )
            setattr(darkness_move, "spell_id", "monster_spell_shadow_strike")
            moves.append(darkness_move)
            
            if power_multiplier >= 1.5:
                # Add stealth darkness ability for stronger monsters
                shadow_meld_move = CombatMove(
                    name="Shadow Meld",
                    description="Becomes nearly invisible by merging with shadows",
                    move_type=MoveType.TRICK,
                    domains=[Domain.DARKNESS, Domain.AWARENESS],
                    base_damage=0,
                    stamina_cost=0,
                    focus_cost=int(7 * power_multiplier),
                    spirit_cost=0,
                    effects=["INVISIBILITY", "NEXT_ATTACK_BONUS"]
                )
                setattr(shadow_meld_move, "spell_id", "monster_spell_shadow_meld")
                moves.append(shadow_meld_move)
        
        elif domain == Domain.SPIRIT:
            # Create a spirit attack move
            spirit_move = CombatMove(
                name="Soul Drain",
                description="Drains spiritual energy from the target",
                move_type=MoveType.FOCUS,
                domains=[Domain.SPIRIT, Domain.MIND],
                base_damage=int(9 * power_multiplier),
                stamina_cost=0,
                focus_cost=0,
                spirit_cost=int(5 * power_multiplier),
                effects=["DAMAGE_SPIRITUAL", "RESOURCE_DRAIN", "LIFESTEAL"]
            )
            setattr(spirit_move, "spell_id", "monster_spell_soul_drain")
            moves.append(spirit_move)
            
            if power_multiplier >= 1.5:
                # Add summoning ability for stronger monsters
                summon_move = CombatMove(
                    name="Summon Lesser Spirit",
                    description="Calls forth a minor spirit to aid in battle",
                    move_type=MoveType.UTILITY,
                    domains=[Domain.SPIRIT, Domain.AUTHORITY],
                    base_damage=0,
                    stamina_cost=0,
                    focus_cost=0,
                    spirit_cost=int(10 * power_multiplier),
                    effects=["SUMMON_ALLY", "TEMPORARY"]
                )
                setattr(summon_move, "spell_id", "monster_spell_summon_lesser_spirit")
                moves.append(summon_move)
        
        elif domain == Domain.MIND:
            # Create a mind attack move
            mind_move = CombatMove(
                name="Psychic Assault",
                description="Launches a direct mental attack",
                move_type=MoveType.FOCUS,
                domains=[Domain.MIND],
                base_damage=int(8 * power_multiplier),
                stamina_cost=0,
                focus_cost=int(6 * power_multiplier),
                spirit_cost=0,
                effects=["DAMAGE_PSYCHIC", "FOCUS_DRAIN"]
            )
            setattr(mind_move, "spell_id", "monster_spell_psychic_assault")
            moves.append(mind_move)
            
            if power_multiplier >= 1.5:
                # Add control ability for stronger monsters
                control_move = CombatMove(
                    name="Mental Domination",
                    description="Attempts to seize control of the target's mind",
                    move_type=MoveType.FOCUS,
                    domains=[Domain.MIND, Domain.AUTHORITY],
                    base_damage=int(4 * power_multiplier),
                    stamina_cost=0,
                    focus_cost=int(10 * power_multiplier),
                    spirit_cost=0,
                    effects=["CONFUSION", "POSSIBLE_CONTROL"]
                )
                setattr(control_move, "spell_id", "monster_spell_mental_domination")
                moves.append(control_move)
        
        # Add more domain-specific moves for other domains as needed
        
        return moves


# ======================================================================
# Integration with Event System
# ======================================================================

class MagicEventIntegration:
    """
    Integration with the event system for magical events.
    
    This class handles:
    1. Registering event handlers for magic-related events
    2. Emitting events when magical actions occur
    3. Handling responses to other system events
    """
    
    def __init__(self, magic_system: MagicSystem):
        """Initialize the event integration"""
        self.magic_system = magic_system
    
    def register_event_handlers(self) -> None:
        """Register handlers for relevant events"""
        # In a real implementation, we would register with the event bus here
        pass
    
    def handle_domain_check_event(self, event_data: Dict[str, Any]) -> None:
        """
        Handle domain check events that might have magical implications.
        """
        # Extract event data
        character_id = event_data.get("actor")
        domain = event_data.get("domain")
        success = event_data.get("success", False)
        action = event_data.get("action", "Unknown action")
        
        # Check for SPIRIT domain usage that might unlock magical abilities
        if domain == "SPIRIT" and success:
            # This could trigger magical awareness or sensitivity increases
            pass
        
        # Check for magical domain usage
        if domain in ["FIRE", "WATER", "EARTH", "AIR", "LIGHT", "DARKNESS", "SPIRIT"] and success:
            # This could increment progress toward elemental attunement
            pass
    
    def emit_spell_cast_event(self, caster_id: str, spell_id: str, targets: List[str], result: Dict[str, Any]) -> None:
        """
        Emit an event when a spell is cast.
        """
        # In a real implementation, we would emit to the event bus here
        event_data = {
            "event_type": "SPELL_CAST",
            "caster_id": caster_id,
            "spell_id": spell_id,
            "targets": targets,
            "success": result.get("success", False),
            "effects": result.get("effect_results", []),
            "backlash": result.get("backlash_occurred", False)
        }
        
        # event_bus.emit("SPELL_CAST", event_data)
    
    def emit_magical_discovery_event(self, character_id: str, discovery_type: str, discovery_details: Dict[str, Any]) -> None:
        """
        Emit an event when a character makes a magical discovery.
        """
        # In a real implementation, we would emit to the event bus here
        event_data = {
            "event_type": "MAGICAL_DISCOVERY",
            "character_id": character_id,
            "discovery_type": discovery_type,
            "discovery_details": discovery_details
        }
        
        # event_bus.emit("MAGICAL_DISCOVERY", event_data)


# ======================================================================
# Magic System Factory
# ======================================================================

def create_magic_integration_services(magic_system: Optional[MagicSystem] = None) -> Dict[str, Any]:
    """
    Create and return all magic integration services.
    """
    # Create or use provided magic system
    magic_sys = magic_system or MagicSystem()
    
    # Create integration services
    combat_manager = MagicalCombatManager(magic_sys)
    monster_integration = MonsterMagicIntegration(magic_sys)
    event_integration = MagicEventIntegration(magic_sys)
    
    # Register event handlers
    event_integration.register_event_handlers()
    
    return {
        "magic_system": magic_sys,
        "combat_manager": combat_manager,
        "monster_integration": monster_integration,
        "event_integration": event_integration
    }


# Initialize magic integration services
magic_integration = create_magic_integration_services()