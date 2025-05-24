from typing import Dict, Any, List, Optional, Tuple

class WorldStateSkillModifier:
    """
    Applies dynamic difficulty modifiers to skill checks based on world state.
    This class examines branch definitions and current world state to determine
    appropriate adjustments to skill check difficulty.
    """
    
    def __init__(self, world_state_manager):
        """
        Initialize the skill modifier.
        
        Args:
            world_state_manager: The WorldState instance to query
        """
        self.world_state_manager = world_state_manager
        
    def calculate_difficulty_modifier(self, 
                                     branch_definition: Dict[str, Any], 
                                     stage_definition: Dict[str, Any], 
                                     skill_check: Dict[str, Any]) -> Tuple[int, str]:
        """
        Calculate a difficulty modifier based on world state effects.
        
        Args:
            branch_definition: The full branch definition
            stage_definition: The current stage definition
            skill_check: The skill check parameters
            
        Returns:
            Tuple of (modifier_value, explanation)
        """
        modifier = 0
        explanations = []
        
        # If no world state manager, no modifications possible
        if not self.world_state_manager:
            return (0, "No world state manager available")
            
        # Get current world state
        world_state = self.world_state_manager.get_current_state_summary()
        
        # Check stage definition for world state effects
        stage_effects = stage_definition.get('world_state_effects', {})
        for state_key, effects in stage_effects.items():
            current_value = world_state.get(state_key)
            if not current_value:
                continue
                
            # Handle different types of effect definitions
            if isinstance(effects, dict) and current_value in effects:
                # Format: {"DEPRESSION": "Text explaining -2 modifier", "BOOM": "Text explaining +2"}
                effect_text = effects.get(current_value)
                if effect_text:
                    # Extract numeric modifier from text
                    import re
                    modifier_match = re.search(r'([+-]\d+)', effect_text)
                    if modifier_match:
                        effect_mod = int(modifier_match.group(1))
                        modifier += effect_mod
                        explanations.append(effect_text)
            elif isinstance(effects, dict):
                # General modifiers not tied to specific values
                for condition, effect in effects.items():
                    if self._check_world_state_condition(condition, world_state):
                        # Parse the effect which could be a number or description
                        if isinstance(effect, int):
                            modifier += effect
                            explanations.append(f"{condition}: {effect:+d}")
                        elif isinstance(effect, str) and any(c.isdigit() for c in effect):
                            # Extract numeric modifier from text
                            import re
                            modifier_match = re.search(r'([+-]\d+)', effect)
                            if modifier_match:
                                effect_mod = int(modifier_match.group(1))
                                modifier += effect_mod
                                explanations.append(effect)
        
        # Look for direct effects on the specific domain being checked
        domain = skill_check.get('domain')
        if domain and f"{domain.lower()}_difficulty_mod" in stage_effects:
            domain_mod = stage_effects[f"{domain.lower()}_difficulty_mod"]
            if isinstance(domain_mod, int):
                modifier += domain_mod
                explanations.append(f"{domain} check adjustment: {domain_mod:+d}")
        
        # Check if any global threats impact this domain
        if domain and 'active_global_threats' in world_state and world_state['active_global_threats']:
            threat_modifiers = self._get_threat_modifiers_for_domain(domain, world_state['active_global_threats'])
            if threat_modifiers:
                for threat, mod, reason in threat_modifiers:
                    modifier += mod
                    explanations.append(f"{threat}: {mod:+d} ({reason})")
        
        # Combine explanations
        explanation = "; ".join(explanations) if explanations else "No world state modifiers"
        
        return (modifier, explanation)
    
    def _check_world_state_condition(self, condition: str, world_state: Dict[str, Any]) -> bool:
        """
        Check if a world state condition is met.
        
        Args:
            condition: Condition string (e.g., "economic_status == RECESSION")
            world_state: Current world state dict
            
        Returns:
            True if condition is met, False otherwise
        """
        if "==" in condition:
            key, value = condition.split("==", 1)
            key, value = key.strip(), value.strip()
            return str(world_state.get(key, "")).upper() == value.upper()
        elif "!=" in condition:
            key, value = condition.split("!=", 1)
            key, value = key.strip(), value.strip()
            return str(world_state.get(key, "")).upper() != value.upper()
        elif ">" in condition:
            key, value = condition.split(">", 1)
            key, value = key.strip(), value.strip()
            try:
                return float(world_state.get(key, 0)) > float(value)
            except ValueError:
                return False
        elif "<" in condition:
            key, value = condition.split("<", 1)
            key, value = key.strip(), value.strip()
            try:
                return float(world_state.get(key, 0)) < float(value)
            except ValueError:
                return False
        elif "in" in condition:
            # "threat_name in active_global_threats"
            key, collection = condition.split("in", 1)
            key, collection = key.strip(), collection.strip()
            collection_data = world_state.get(collection, [])
            if isinstance(collection_data, list):
                return key in collection_data
        
        # Default case: check if the condition key exists and is truthy
        return bool(world_state.get(condition, False))
    
    def _get_threat_modifiers_for_domain(self, 
                                        domain: str, 
                                        threats: List[str]) -> List[Tuple[str, int, str]]:
        """
        Get modifiers for skill checks based on active threats.
        
        Args:
            domain: The domain being checked (e.g., "STRENGTH")
            threats: List of active global threats
            
        Returns:
            List of (threat_name, modifier_value, reason) tuples
        """
        # This would typically load from configuration or data
        # Here's an example implementation
        threat_domain_impacts = {
            "Dragon Menace Nearby": {
                "STRENGTH": (-2, "Fear inhibits physical performance"),
                "COURAGE": (2, "Greater need to display bravery"),
                "AWARENESS": (1, "Heightened alertness due to danger"),
                "STEALTH": (2, "Greater incentive to remain undetected")
            },
            "Undead Plague": {
                "ENDURANCE": (-1, "Risk of infection decreases stamina"),
                "MEDICINE": (2, "Practical experience treating symptoms"),
                "WILLPOWER": (2, "Mental fortitude more practiced amid horror")
            },
            "Economic Collapse": {
                "CRAFTING": (2, "Necessity breeds resourcefulness"),
                "HAGGLING": (3, "Every coin counts in desperate times"),
                "SURVIVAL": (1, "Self-sufficiency becomes common")
            }
        }
        
        results = []
        for threat in threats:
            if threat in threat_domain_impacts and domain in threat_domain_impacts[threat]:
                modifier, reason = threat_domain_impacts[threat][domain]
                results.append((threat, modifier, reason))
        
        return results