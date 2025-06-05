from typing import Dict, List, Optional, Any
import random

from ..shared.survival_models import SurvivalState, MoodState
from ..game_engine.survival_system import SurvivalSystem


class SurvivalNarrativeIntegration:
    """Integrates survival system with narrative generation"""
    
    def __init__(self, survival_system: SurvivalSystem = None):
        """Initialize the integration
        
        Args:
            survival_system: The survival system to integrate with
        """
        self.survival_system = survival_system
        
        # Narrative templates based on survival states
        self.narrative_templates = {
            # Hunger templates
            "hunger": {
                (0, 20): [
                    "Your stomach feels like a hollow pit. The gnawing pain of starvation is impossible to ignore.",
                    "Each step is a struggle as your body screams for nourishment. You need food desperately.",
                    "Your vision occasionally darkens as hunger pains wrack your body. You're starving."
                ],
                (21, 40): [
                    "Your stomach growls loudly. The persistent hunger makes it difficult to focus.",
                    "A sharp pang of hunger reminds you that you haven't eaten in quite some time.",
                    "Your thoughts keep drifting to food as your empty stomach complains."
                ],
                (41, 70): [
                    "You're starting to feel hungry. It's not urgent, but you should eat soon.",
                    "A mild hunger nags at you. Food would be welcome when convenient.",
                    "Your stomach occasionally rumbles, reminding you that you'll need to eat before long."
                ]
            },
            
            # Thirst templates
            "thirst": {
                (0, 20): [
                    "Your throat burns with thirst. Your tongue feels swollen and your lips are cracked.",
                    "Severe dehydration makes your head pound. You need water immediately.",
                    "Your movements are sluggish as dehydration takes its toll. Water has become your only thought."
                ],
                (21, 40): [
                    "Your mouth is dry and your thirst is becoming increasingly difficult to ignore.",
                    "You lick your dry lips, desperately wishing for something to drink.",
                    "The persistent thirst makes it hard to think about anything else."
                ],
                (41, 70): [
                    "You're getting thirsty. A drink would be welcome soon.",
                    "Your mouth feels a bit dry. You should find water when convenient.",
                    "A mild thirst reminds you that you haven't had anything to drink in a while."
                ]
            },
            
            # Fatigue templates
            "fatigue": {
                (80, 100): [
                    "Exhaustion weighs on you like a physical burden. Your limbs feel like lead.",
                    "Your eyelids droop as fatigue overwhelms you. You need rest desperately.",
                    "Each step requires conscious effort as exhaustion threatens to drop you where you stand."
                ],
                (60, 79): [
                    "Weariness seeps into your bones. You should rest soon before exhaustion takes over.",
                    "Your movements are becoming sluggish as fatigue builds. You need to find a place to rest.",
                    "A deep tiredness is settling in. Your body demands rest before long."
                ],
                (40, 59): [
                    "You're beginning to feel tired. Rest would be welcome when convenient.",
                    "The day's activities are catching up to you. You'll need to rest eventually.",
                    "A familiar tiredness tugs at you, nothing urgent but noticeable."
                ]
            },
            
            # Health templates (based on percentage of max health)
            "health_percent": {
                (0, 20): [
                    "Pain courses through your body. You're seriously wounded and need help.",
                    "Blood seeps through your makeshift bandages. Your injuries are severe.",
                    "Each movement sends waves of agony through your injured body. You need medical attention."
                ],
                (21, 40): [
                    "Your injuries throb with a persistent pain. They need proper treatment soon.",
                    "Wincing, you try to ignore your wounds, but they demand attention.",
                    "Your injuries are concerning and will worsen without care."
                ],
                (41, 70): [
                    "Minor aches and pains remind you of your recent scrapes and bruises.",
                    "You have some cuts and bruises that should heal on their own, but they're uncomfortable.",
                    "Your injuries are minor but noticeable when you move certain ways."
                ]
            },
            
            # Morale templates
            "morale": {
                (0, 30): [
                    "A cloud of despair hangs over you. It's hard to see any hope in your situation.",
                    "Demoralized and defeated, you question whether to continue at all.",
                    "Your spirit is crushed under the weight of recent events."
                ],
                (31, 60): [
                    "Your spirits are low. The challenges ahead seem daunting.",
                    "A sense of melancholy colors your perception of everything around you.",
                    "You try to stay positive, but doubt and worry keep creeping in."
                ]
            },
            
            # Clarity templates
            "clarity": {
                (0, 30): [
                    "Your thoughts are fragmented, slipping away before you can grasp them.",
                    "Reality seems to waver at the edges of your perception. You can't trust what you see.",
                    "Strange whispers tickle the back of your mind. Are they real or imagined?"
                ],
                (31, 60): [
                    "Concentration is difficult. Your thoughts drift and scatter easily.",
                    "The line between reality and imagination feels unexpectedly blurry.",
                    "You occasionally catch movement in the corner of your eye, but nothing's there when you look."
                ]
            }
        }
        
        # Mood-based description modifiers
        self.mood_modifiers = {
            MoodState.ELATED: {
                "perception": "Everything seems brighter and more vibrant. The world feels full of possibility.",
                "interactions": "You feel an unusual warmth toward everyone you meet."
            },
            MoodState.HAPPY: {
                "perception": "The world seems a bit brighter than usual. You notice beauty where you might normally miss it.",
                "interactions": "You find yourself smiling more easily at those around you."
            },
            MoodState.CONTENT: {
                "perception": "There's a comfortable steadiness to your thoughts and perceptions.",
                "interactions": "You feel at ease with others, neither seeking nor avoiding interaction."
            },
            MoodState.NEUTRAL: {
                "perception": "You perceive your surroundings with typical clarity, neither enhanced nor diminished.",
                "interactions": "Your social interactions feel normal and unremarkable."
            },
            MoodState.CONCERNED: {
                "perception": "You find yourself scanning for potential problems more than usual.",
                "interactions": "There's a guardedness to your interactions with others."
            },
            MoodState.STRESSED: {
                "perception": "The world feels slightly overwhelming. Details that wouldn't normally bother you now grate on your nerves.",
                "interactions": "You're more abrupt in conversation than you intend to be."
            },
            MoodState.ANXIOUS: {
                "perception": "Your surroundings seem filled with hidden threats. Ordinary situations feel charged with tension.",
                "interactions": "Social interactions feel fraught with unseen judgments and expectations."
            },
            MoodState.DEPRESSED: {
                "perception": "The world seems drained of color and joy. Everything feels pointless and hollow.",
                "interactions": "Engaging with others feels like an immense effort you can barely muster."
            },
            MoodState.PANICKED: {
                "perception": "Everything around you seems like a potential threat. Your senses are overwhelmed with danger signals.",
                "interactions": "You can barely focus on what others are saying through the rushing of blood in your ears."
            }
        }
    
    def enhance_narrative_context(self, context: Dict, character_id: str) -> Dict:
        """Enhance narrative context with survival-related data
        
        Args:
            context: Existing narrative context
            character_id: ID of the character
            
        Returns:
            Enhanced context
        """
        if not self.survival_system:
            return context
            
        # Get survival context
        survival_context = self.survival_system.get_narrative_context(character_id)
        if not survival_context:
            return context
            
        # Merge contexts
        merged_context = {**context}
        merged_context["survival"] = survival_context
        
        # Generate narrative hooks based on survival state
        hooks = self.generate_narrative_hooks(survival_context["survival_state"])
        merged_context["survival"]["narrative_hooks"] = hooks
        
        return merged_context
    
    def generate_narrative_hooks(self, state: Dict) -> List[str]:
        """Generate narrative hooks based on survival state
        
        Args:
            state: Current survival state values
            
        Returns:
            List of narrative hooks
        """
        hooks = []
        
        # Check each survival metric and add relevant hooks
        for metric, ranges in self.narrative_templates.items():
            # Special handling for health_percent
            if metric == "health_percent":
                # Calculate health percentage from current and max health
                current_health = state.get("current_health", 0)
                max_health = state.get("max_health", 100)
                value = int((current_health / max_health) * 100) if max_health > 0 else 0
            else:
                value = state.get(metric, 0)
            
            # Find the appropriate range
            for (min_val, max_val), templates in ranges.items():
                if min_val <= value <= max_val:
                    # Add a random template from the range
                    hooks.append(random.choice(templates))
                    break
        
        # Add mood-based perception if available
        mood = state.get("mood")
        if mood in self.mood_modifiers:
            # Add a perception or interaction modifier based on the mood
            modifier_type = "perception" if random.random() < 0.6 else "interactions"
            hooks.append(self.mood_modifiers[mood][modifier_type])
        
        return hooks
    
    def generate_survival_narrative(self, character_id: str) -> str:
        """Generate a narrative description based purely on survival state
        
        Args:
            character_id: ID of the character
            
        Returns:
            Narrative description
        """
        if not self.survival_system:
            return ""
            
        # Get survival context
        survival_context = self.survival_system.get_narrative_context(character_id)
        if not survival_context:
            return ""
            
        # Generate hooks
        hooks = self.generate_narrative_hooks(survival_context["survival_state"])
        
        # Build narrative
        if hooks:
            # Select 1-3 hooks randomly to avoid overwhelming the player
            selected_hooks = random.sample(hooks, min(len(hooks), random.randint(1, 3)))
            return " ".join(selected_hooks)
        else:
            return ""
    
    def generate_prompt_tags(self, character_id: str) -> str:
        """Generate tags for LLM prompt based on survival state
        
        Args:
            character_id: ID of the character
            
        Returns:
            Tag string for prompt
        """
        if not self.survival_system:
            return ""
            
        # Get survival context
        survival_context = self.survival_system.get_narrative_context(character_id)
        if not survival_context or "survival_tags" not in survival_context:
            return ""
            
        # Format tags for prompt
        tags = survival_context["survival_tags"]
        return "[" + ", ".join(tags) + "]"
    
    def adjust_hallucination_bias(self, character_id: str) -> float:
        """Calculate a hallucination bias modifier based on mental state
        
        Args:
            character_id: ID of the character
            
        Returns:
            Hallucination bias value between 0.0 (normal) and 1.0 (maximum)
        """
        if not self.survival_system:
            return 0.0
            
        state = self.survival_system.get_survival_state(character_id)
        if not state:
            return 0.0
            
        # Calculate based on clarity and fatigue
        clarity_factor = (100 - state.clarity) / 100.0  # Lower clarity = more hallucinations
        fatigue_factor = state.fatigue / 100.0  # Higher fatigue = more hallucinations
        
        # Weighted combination (clarity has more impact)
        hallucination_bias = (clarity_factor * 0.7) + (fatigue_factor * 0.3)
        
        # Ensure within range
        return max(0.0, min(1.0, hallucination_bias))
    
    def get_critical_state_effect(self, character_id: str) -> Optional[Dict[str, Any]]:
        """Get a critical state effect if any survival metric is in a critical range
        
        Args:
            character_id: ID of the character
            
        Returns:
            Effect dict or None if no critical states
        """
        if not self.survival_system:
            return None
            
        state = self.survival_system.get_survival_state(character_id)
        if not state:
            return None
        
        # Check for critical states
        effects = []
        
        # Severe hunger
        if state.hunger <= 15:
            effects.append({
                "type": "blackout",
                "description": "You collapse from starvation. Your vision fades to black...",
                "consequence": "hunger_collapse"
            })
        
        # Severe thirst
        if state.thirst <= 10:
            effects.append({
                "type": "blackout",
                "description": "Dehydration overtakes you. Your legs give out and the world spins away...",
                "consequence": "thirst_collapse"
            })
        
        # Extreme fatigue
        if state.fatigue >= 95:
            effects.append({
                "type": "sleep",
                "description": "Your body can't go on. You fall into an exhausted sleep where you stand...",
                "consequence": "fatigue_collapse"
            })
        
        # Critical health - using percentage of max health
        health_percent = int((state.current_health / state.max_health) * 100) if state.max_health > 0 else 0
        if health_percent <= 10:
            effects.append({
                "type": "injury",
                "description": "Your injuries are too severe. You fall to the ground, unable to continue...",
                "consequence": "health_collapse"
            })
        
        # Severe clarity loss
        if state.clarity <= 15:
            effects.append({
                "type": "hallucination",
                "description": "Reality fractures around you. You can no longer tell what's real and what's imagined...",
                "consequence": "clarity_collapse"
            })
        
        # Return a random effect if there are multiple
        if effects:
            return random.choice(effects)
            
        return None
