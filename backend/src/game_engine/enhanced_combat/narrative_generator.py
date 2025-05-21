"""
Narrative generator for enhanced combat.

This module creates rich, detailed narrative descriptions for combat,
integrating domain usage, environment, and combat outcomes.
"""
import random
from typing import List, Dict, Any, Optional

from ...events.event_bus import GameEvent, EventType, event_bus


class CombatNarrativeGenerator:
    """
    Generator for rich combat narratives based on combat outcomes and context.
    
    This uses templates and contextual information to generate descriptions
    that reflect the domains used, environment, and outcomes of combat actions.
    """
    def __init__(self):
        """Initialize the narrative generator"""
        self.narrative_templates = self._load_narrative_templates()
        self.descriptive_cache = {}  # Cache for common descriptions
    
    def _load_narrative_templates(self) -> Dict:
        """
        Load narrative templates for different combat situations.
        
        Returns:
            Dictionary of narrative templates
        """
        return {
            "move_success": [
                "{actor} executes {move} with precision. {target} {reaction}.",
                "With skillful application of {domain}, {actor}'s {move} lands true. {target} {reaction}.",
                "{actor} channels their {domain} expertise into a powerful {move}. {target} {reaction}."
            ],
            "move_failure": [
                "{target} anticipates {actor}'s {move} and {counter}.",
                "{actor}'s {move} fails to connect as {target} {counter}.",
                "Despite drawing on {domain}, {actor}'s {move} is thwarted when {target} {counter}."
            ],
            "status_applied": [
                "{target} is now {status} from the effects of {move}.",
                "The {move} leaves {target} {status}.",
                "{actor}'s {move} results in {target} becoming {status}."
            ],
            "critical_success": [
                "In a display of extraordinary skill, {actor}'s {move} strikes a critical weakness!",
                "{actor} executes {move} with uncanny precision, finding the perfect opening!",
                "A moment of perfect execution! {actor}'s {move} lands with devastating effect!"
            ],
            "environment_interaction": [
                "{actor} uses the {environment} to their advantage, {interaction_effect}.",
                "The {environment} becomes a weapon in {actor}'s hands, {interaction_effect}.",
                "Drawing on the surroundings, {actor} {interaction_effect} using the {environment}."
            ],
            "desperate_move": [
                "With reckless abandon, {actor} attempts a desperate {move}!",
                "In a high-risk gambit, {actor} throws everything into their {move}!",
                "Pushed to the edge, {actor} executes a desperate {move}!"
            ],
            "calculated_move": [
                "With careful precision, {actor} executes a calculated {move}.",
                "{actor} analyzes the situation and performs a methodical {move}.",
                "After a moment of strategic thought, {actor} delivers a calculated {move}."
            ],
            "domain_focused": {
                "BODY": [
                    "{actor} channels raw physical power into their {move}.",
                    "Drawing on physical strength, {actor} executes a powerful {move}.",
                    "With impressive physicality, {actor} performs a forceful {move}."
                ],
                "MIND": [
                    "{actor} calculates trajectories and weak points for their {move}.",
                    "Using tactical insight, {actor} performs a precise {move}.",
                    "{actor}'s mental acuity guides their {move} to maximum effect."
                ],
                "SPIRIT": [
                    "{actor}'s spiritual energy flows into their {move}.",
                    "Drawing on inner reserves, {actor} channels spirit into their {move}.",
                    "A flash of spiritual insight guides {actor}'s {move}."
                ],
                "SOCIAL": [
                    "{actor} uses psychological insight to enhance their {move}.",
                    "With exceptional social awareness, {actor} performs a distracting {move}.",
                    "{actor}'s understanding of social dynamics makes their {move} more effective."
                ],
                "CRAFT": [
                    "{actor} applies technical skill to perfect their {move}.",
                    "Years of practice and craft enhance {actor}'s {move}.",
                    "With practiced technique, {actor} executes a masterful {move}."
                ],
                "AUTHORITY": [
                    "{actor}'s commanding presence adds weight to their {move}.",
                    "With authoritative confidence, {actor} performs an imposing {move}.",
                    "{actor} projects authority into their {move}, making it more intimidating."
                ],
                "AWARENESS": [
                    "{actor}'s heightened awareness perfects the timing of their {move}.",
                    "Perceiving a brief opening, {actor} executes a perfectly timed {move}.",
                    "{actor}'s exceptional awareness guides their {move} to the perfect spot."
                ]
            }
        }
    
    def generate_combat_narrative(self, 
                                combat_result: Dict[str, Any],
                                actor_name: str, 
                                target_name: str,
                                move_name: str,
                                domains: List[str],
                                environment_tags: List[str] = None,
                                is_desperate: bool = False,
                                is_calculated: bool = False) -> Dict[str, str]:
        """
        Generate narrative descriptions for a combat round.
        
        Args:
            combat_result: Results of the combat round
            actor_name: Name of the actor
            target_name: Name of the target
            move_name: Name of the move used
            domains: List of domains used in the move
            environment_tags: List of environment tags
            is_desperate: Whether this was a desperate move
            is_calculated: Whether this was a calculated move
            
        Returns:
            Dictionary with different narrative elements
        """
        # Prepare the base context
        context = self._prepare_narrative_context(
            combat_result, 
            actor_name, 
            target_name, 
            move_name, 
            domains, 
            environment_tags,
            is_desperate,
            is_calculated
        )
        
        # Generate the narrative
        return self._generate_from_templates(context)
    
    def _prepare_narrative_context(self, 
                                 combat_result: Dict[str, Any],
                                 actor_name: str, 
                                 target_name: str,
                                 move_name: str,
                                 domains: List[str],
                                 environment_tags: List[str] = None,
                                 is_desperate: bool = False,
                                 is_calculated: bool = False) -> Dict[str, Any]:
        """
        Prepare context for narrative generation.
        
        Args:
            combat_result: Results of the combat round
            actor_name: Name of the actor
            target_name: Name of the target
            move_name: Name of the move used
            domains: List of domains used in the move
            environment_tags: List of environment tags
            is_desperate: Whether this was a desperate move
            is_calculated: Whether this was a calculated move
            
        Returns:
            Context dictionary for narrative generation
        """
        context = {
            "actor_name": actor_name,
            "target_name": target_name,
            "move_name": move_name,
            "domains": domains,
            "primary_domain": domains[0] if domains else "BODY",
            "success": combat_result.get("actor_success", False),
            "effect_magnitude": combat_result.get("effect_magnitude", 0),
            "environment": environment_tags or [],
            "narrative_hooks": combat_result.get("narrative_hooks", []),
            "damage_dealt": combat_result.get("damage_dealt", 0),
            "counter_damage": combat_result.get("counter_damage", 0),
            "status_applied": combat_result.get("status_applied"),
            "is_desperate": is_desperate,
            "is_calculated": is_calculated,
            "target_defeated": combat_result.get("target_defeated", False)
        }
        
        # Add reaction based on success
        if context["success"]:
            damage = combat_result.get("damage_dealt", 0)
            if damage > 20:
                context["target_reaction"] = "staggers backward, severely wounded"
            elif damage > 10:
                context["target_reaction"] = "winces in pain"
            else:
                context["target_reaction"] = "absorbs the blow"
            
            if combat_result.get("target_defeated", False):
                context["target_reaction"] = "falls, defeated"
        else:
            counter_damage = combat_result.get("counter_damage", 0)
            if counter_damage > 0:
                context["target_counter"] = "responds with a counter-attack"
            else:
                context["target_counter"] = "defends effectively"
                
        return context
    
    def _get_move_type_description(self, move_type: str) -> str:
        """
        Get a descriptive phrase for a move type.
        
        Args:
            move_type: Type of move
            
        Returns:
            Descriptive phrase
        """
        if not move_type:
            return "skillful attack"
            
        descriptions = {
            "FORCE": ["powerful", "forceful", "mighty", "overwhelming"],
            "TRICK": ["deceptive", "cunning", "tricky", "clever"],
            "FOCUS": ["precise", "calculated", "focused", "analytical"],
            "BUFF": ["supportive", "enhancing", "empowering", "strengthening"],
            "DEBUFF": ["weakening", "hindering", "disabling", "hampering"],
            "UTILITY": ["versatile", "resourceful", "adaptive", "practical"]
        }
        
        move_type_upper = move_type.upper() if isinstance(move_type, str) else ""
        options = descriptions.get(move_type_upper, ["skillful"])
        
        # Cache common descriptions
        cache_key = f"{move_type_upper}_desc"
        if cache_key not in self.descriptive_cache:
            self.descriptive_cache[cache_key] = random.choice(options)
            
        return self.descriptive_cache[cache_key]
    
    def _generate_from_templates(self, context: Dict[str, Any]) -> Dict[str, str]:
        """
        Generate narrative using templates.
        
        Args:
            context: Context for narrative generation
            
        Returns:
            Dictionary with different narrative elements
        """
        narratives = {}
        
        # Select the right template category
        if context["is_desperate"]:
            template_category = "desperate_move"
        elif context["is_calculated"]:
            template_category = "calculated_move"
        elif context["success"]:
            if context["effect_magnitude"] > 5:
                template_category = "critical_success"
            else:
                template_category = "move_success"
        else:
            template_category = "move_failure"
            
        # Select and fill a template for the main action
        templates = self.narrative_templates[template_category]
        template = random.choice(templates)
        
        # Basic replacements
        filled_template = template.replace("{actor}", context["actor_name"])
        filled_template = filled_template.replace("{target}", context["target_name"])
        filled_template = filled_template.replace("{move}", context["move_name"])
        
        # More complex replacements
        if "{domain}" in filled_template:
            if context["domains"]:
                domain = context["primary_domain"]
                filled_template = filled_template.replace("{domain}", domain)
            else:
                filled_template = filled_template.replace("{domain}", "skill")
                
        if "{reaction}" in filled_template and "target_reaction" in context:
            filled_template = filled_template.replace("{reaction}", context["target_reaction"])
            
        if "{counter}" in filled_template and "target_counter" in context:
            filled_template = filled_template.replace("{counter}", context["target_counter"])
            
        narratives["action_description"] = filled_template
        
        # Add domain-specific description
        if context["domains"]:
            domain = context["primary_domain"]
            if domain in self.narrative_templates["domain_focused"]:
                domain_templates = self.narrative_templates["domain_focused"][domain]
                domain_template = random.choice(domain_templates)
                
                domain_narrative = domain_template.replace("{actor}", context["actor_name"])
                domain_narrative = domain_narrative.replace("{move}", context["move_name"])
                
                narratives["domain_description"] = domain_narrative
        else:
            narratives["domain_description"] = ""
            
        # Add environment description if available
        if context["environment"]:
            env = random.choice(context["environment"])
            env_template = random.choice(self.narrative_templates["environment_interaction"])
            
            # Generate a random interaction effect
            effects = [
                "gains an advantage",
                "creates an opening",
                "improves their position",
                "finds a tactical opportunity"
            ]
            
            env_narrative = env_template.replace("{actor}", context["actor_name"])
            env_narrative = env_narrative.replace("{environment}", env)
            env_narrative = env_narrative.replace("{interaction_effect}", random.choice(effects))
            
            narratives["environment_description"] = env_narrative
        else:
            narratives["environment_description"] = ""
            
        # Add status effect description if available
        if context["status_applied"]:
            status_template = random.choice(self.narrative_templates["status_applied"])
            
            status_narrative = status_template.replace("{actor}", context["actor_name"])
            status_narrative = status_narrative.replace("{target}", context["target_name"])
            status_narrative = status_narrative.replace("{move}", context["move_name"])
            status_narrative = status_narrative.replace("{status}", context["status_applied"])
            
            narratives["status_description"] = status_narrative
        else:
            narratives["status_description"] = ""
            
        # Generate a basic consequence description
        if context["success"] and context["effect_magnitude"] > 3:
            consequence = f"This powerful strike might leave lasting damage on {context['target_name']}."
            narratives["consequence_description"] = consequence
        else:
            narratives["consequence_description"] = ""
            
        # Add all narrative hooks
        if context["narrative_hooks"]:
            narratives["narrative_hooks"] = "\n".join(context["narrative_hooks"])
        else:
            narratives["narrative_hooks"] = ""
            
        return narratives
    
    def publish_narrative_event(self, 
                               combat_id: str,
                               game_id: str,
                               actor_id: str,
                               narratives: Dict[str, str]) -> None:
        """
        Publish a narrative event to the event bus.
        
        Args:
            combat_id: ID of the combat
            game_id: ID of the game
            actor_id: ID of the acting entity
            narratives: Dictionary with narrative elements
        """
        narrative_text = narratives.get("action_description", "")
        if narratives.get("domain_description"):
            narrative_text += " " + narratives["domain_description"]
        if narratives.get("environment_description"):
            narrative_text += " " + narratives["environment_description"]
        if narratives.get("status_description"):
            narrative_text += " " + narratives["status_description"]
            
        # Create and publish the event
        event = GameEvent(
            type=EventType.COMBAT_NARRATIVE,
            actor=actor_id,
            context={
                "combat_id": combat_id,
                "narrative": narrative_text,
                "consequence": narratives.get("consequence_description", ""),
                "narrative_hooks": narratives.get("narrative_hooks", "").split("\n") if narratives.get("narrative_hooks") else []
            },
            tags=["combat", "narrative"],
            game_id=game_id
        )
        
        event_bus.publish(event)


# Create a global instance
narrative_generator = CombatNarrativeGenerator()