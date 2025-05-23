"""
AI GM Brain - Narrative Generator

This module provides narrative generation capabilities for the AI GM Brain,
creating rich descriptions, dialogues, and story elements.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Import from core brain
from .ai_gm_brain import AIGMBrain, ProcessingMode
from .ai_gm_decision_logic import DecisionType


class NarrativeStyle:
    """Defines different narrative styles for content generation."""
    
    HEROIC = {
        "tone": "epic and inspiring",
        "pacing": "swift and impactful",
        "description_style": "vivid and grand",
        "dialogue_style": "bold and memorable"
    }
    
    MYSTERIOUS = {
        "tone": "enigmatic and atmospheric",
        "pacing": "measured and suspenseful",
        "description_style": "shadowy and suggestive",
        "dialogue_style": "cryptic and meaningful"
    }
    
    GRITTY = {
        "tone": "harsh and realistic",
        "pacing": "relentless and tense",
        "description_style": "detailed and unflinching",
        "dialogue_style": "terse and raw"
    }
    
    WHIMSICAL = {
        "tone": "lighthearted and clever",
        "pacing": "playful and surprising",
        "description_style": "colorful and exaggerated",
        "dialogue_style": "witty and quirky"
    }
    
    DRAMATIC = {
        "tone": "emotional and intense",
        "pacing": "dynamic with strong beats",
        "description_style": "evocative and sensory",
        "dialogue_style": "passionate and revealing"
    }


class NarrativeGenerator:
    """
    Generator for narrative content including descriptions, dialogue, and story elements.
    
    This class creates rich, contextually appropriate narrative content
    for different game situations.
    """
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the narrative generator.
        
        Args:
            ai_gm_brain: Reference to the AI GM Brain instance
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger(f"NarrativeGen_{ai_gm_brain.game_id}")
        
        # Track narrative style and pacing
        self.current_style = NarrativeStyle.HEROIC
        self.tension_level = 0.5  # 0.0 to 1.0
        self.narrative_hooks: List[str] = []
        
        # Template collections
        self.environment_templates = {
            "forest": [
                "Tall trees surround you, their ancient trunks stretching skyward. {detail}",
                "Dappled sunlight filters through the leafy canopy above. {detail}",
                "The forest floor is carpeted with fallen leaves and soft moss. {detail}",
                "Thick undergrowth crowds the spaces between trees. {detail}"
            ],
            "mountain": [
                "Craggy peaks rise majestically around you. {detail}",
                "The thin mountain air fills your lungs with each breath. {detail}",
                "Rocky outcroppings provide treacherous footing on the mountainside. {detail}",
                "From this elevation, you can see for miles across the rugged landscape. {detail}"
            ],
            "cave": [
                "Darkness envelops you, broken only by {light_source}. {detail}",
                "The damp cave walls glisten with moisture. {detail}",
                "Stalactites hang menacingly from the cavern ceiling. {detail}",
                "A chill emanates from the stone around you. {detail}"
            ],
            "village": [
                "Simple buildings line the dirt streets of this settlement. {detail}",
                "Locals go about their daily business, occasionally glancing your way. {detail}",
                "The scent of hearth fires and cooking food fills the air. {detail}",
                "The village center bustles with activity. {detail}"
            ],
            "city": [
                "Towering buildings of stone and wood crowd together. {detail}",
                "The city streets pulse with life and commerce. {detail}",
                "A cacophony of sounds envelops you—merchants, animals, and conversations. {detail}",
                "The architectural styles speak of a place with rich history and culture. {detail}"
            ],
            "dungeon": [
                "Ancient stonework surrounds you, worn by time and darkness. {detail}",
                "The air is stale and heavy, carrying whispers of the past. {detail}",
                "Foreboding passages branch off in multiple directions. {detail}",
                "Remnants of those who came before lie scattered about. {detail}"
            ]
        }
        
        self.combat_templates = {
            "start": [
                "Tension fills the air as {enemy} moves into a threatening stance. Combat is inevitable.",
                "With a sudden flash of movement, {enemy} attacks! Defend yourself!",
                "{enemy} blocks your path, clearly hostile and ready for battle.",
                "The atmosphere shifts as {enemy} reveals its true intentions—violence."
            ],
            "hit": [
                "Your {attack} lands with devastating effect, causing {enemy} to {reaction}.",
                "A solid blow! Your {attack} connects with {enemy}, who {reaction}.",
                "{enemy} fails to dodge your {attack}, taking the full force of the blow.",
                "With perfect timing, your {attack} finds its mark. {enemy} {reaction}."
            ],
            "miss": [
                "Your {attack} misses its mark as {enemy} {evasion}.",
                "Despite your best effort, {enemy} {evasion}, causing your {attack} to fall short.",
                "{enemy} narrowly {evasion} your {attack}.",
                "Your {attack} fails to connect as {enemy} {evasion} with surprising agility."
            ],
            "enemy_hit": [
                "{enemy}'s {attack} catches you off guard, sending pain shooting through your body.",
                "You fail to evade as {enemy} strikes with {attack}, dealing a painful blow.",
                "A vicious {attack} from {enemy} breaks through your defenses.",
                "Pain erupts as {enemy}'s {attack} lands with precision."
            ],
            "enemy_miss": [
                "You {evasion} just in time to avoid {enemy}'s {attack}.",
                "{enemy}'s {attack} narrowly misses as you {evasion}.",
                "With a quick {evasion}, you avoid {enemy}'s {attack}.",
                "{enemy} attacks with {attack}, but you skillfully {evasion}."
            ],
            "victory": [
                "With a final decisive blow, you defeat {enemy}, who {defeat_reaction}.",
                "{enemy} {defeat_reaction}, unable to withstand your relentless assault.",
                "Your combat prowess proves superior as {enemy} {defeat_reaction}.",
                "The battle ends as {enemy} {defeat_reaction}, leaving you victorious but winded."
            ],
            "defeat": [
                "Your vision swims as {enemy}'s final attack overwhelms you. Darkness encroaches.",
                "Despite your best efforts, {enemy} proves too powerful. You collapse, defeated.",
                "The battle ends badly as {enemy} delivers a finishing blow. You fall.",
                "Pain overtakes you as {enemy} claims victory. You lose consciousness."
            ]
        }
        
        self.npc_dialogue_templates = {
            "friendly": [
                "\"Well met, traveler! {dialogue}\" {npc} says with genuine warmth.",
                "With a broad smile, {npc} greets you: \"{dialogue}\"",
                "\"{dialogue}\" {npc}'s friendly demeanor makes the conversation easy.",
                "{npc} approaches with an outstretched hand. \"{dialogue}\""
            ],
            "hostile": [
                "\"{dialogue}\" {npc} snarls, hand hovering near a weapon.",
                "Eyes narrowed, {npc} spits out the words: \"{dialogue}\"",
                "\"{dialogue}\" There's no mistaking the threat in {npc}'s voice.",
                "{npc} glares at you with undisguised contempt. \"{dialogue}\""
            ],
            "neutral": [
                "\"{dialogue}\" {npc} states matter-of-factly.",
                "With a measured tone, {npc} responds: \"{dialogue}\"",
                "\"{dialogue}\" {npc}'s expression remains unreadable.",
                "{npc} considers before speaking. \"{dialogue}\""
            ],
            "fearful": [
                "Eyes darting nervously, {npc} whispers: \"{dialogue}\"",
                "\"{dialogue}\" {npc}'s voice trembles with each word.",
                "{npc} keeps a careful distance as they say: \"{dialogue}\"",
                "With visible anxiety, {npc} manages: \"{dialogue}\""
            ],
            "mysterious": [
                "\"{dialogue}\" {npc}'s enigmatic words hang in the air.",
                "{npc} leans closer, voice barely audible: \"{dialogue}\"",
                "With knowing eyes, {npc} cryptically states: \"{dialogue}\"",
                "\"{dialogue}\" Something in {npc}'s tone suggests hidden meanings."
            ]
        }
        
        self.discovery_templates = [
            "You've discovered {item}! {description}",
            "Your attention is drawn to {item}. {description}",
            "Hidden among the surroundings, you find {item}. {description}",
            "Something catches your eye—{item}. {description}"
        ]
        
        self.logger.info("Narrative Generator initialized")
    
    def generate_location_description(self, 
                                    location_type: str,
                                    details: Dict[str, Any]) -> str:
        """
        Generate a description for a location.
        
        Args:
            location_type: Type of location (forest, city, etc.)
            details: Additional details about the location
            
        Returns:
            A rich location description
        """
        # Get templates for this location type or default to generic templates
        templates = self.environment_templates.get(
            location_type.lower(), 
            ["You find yourself in {location_type}. {detail}"]
        )
        
        # Select base template
        base_template = random.choice(templates)
        
        # Generate sensory details based on location
        sights = details.get('sights', self._generate_sensory_detail(location_type, 'sight'))
        sounds = details.get('sounds', self._generate_sensory_detail(location_type, 'sound'))
        smells = details.get('smells', self._generate_sensory_detail(location_type, 'smell'))
        
        # Combine templates with details
        description = base_template.format(
            location_type=location_type,
            detail=details.get('detail', ''),
            light_source=details.get('light_source', 'faint light')
        )
        
        # Add sensory details
        description += f" {sights} {sounds} {smells}"
        
        # Add narrative hook if tension is high
        if self.tension_level > 0.7 and self.narrative_hooks:
            hook = random.choice(self.narrative_hooks)
            description += f" {hook}"
        
        return description
    
    def generate_npc_dialogue(self, 
                            npc_name: str,
                            disposition: str,
                            dialogue_content: str) -> str:
        """
        Generate dialogue for an NPC.
        
        Args:
            npc_name: Name of the NPC
            disposition: Disposition towards player (friendly, hostile, etc.)
            dialogue_content: The content of what the NPC wants to say
            
        Returns:
            Formatted NPC dialogue with narration
        """
        # Get templates for this disposition or default to neutral
        templates = self.npc_dialogue_templates.get(
            disposition.lower(), 
            self.npc_dialogue_templates['neutral']
        )
        
        # Select base template
        template = random.choice(templates)
        
        # Format the dialogue
        return template.format(
            npc=npc_name,
            dialogue=dialogue_content
        )
    
    def generate_combat_narrative(self, 
                                combat_type: str,
                                combat_details: Dict[str, Any]) -> str:
        """
        Generate a narrative description for combat.
        
        Args:
            combat_type: Type of combat narrative (start, hit, miss, etc.)
            combat_details: Details about the combat
            
        Returns:
            Combat narrative description
        """
        # Get templates for this combat type or default to generic
        templates = self.combat_templates.get(
            combat_type.lower(),
            ["The combat continues with {enemy}."]
        )
        
        # Select base template
        template = random.choice(templates)
        
        # Format with combat details
        return template.format(**combat_details)
    
    def generate_discovery_narrative(self, 
                                   item_name: str,
                                   description: str) -> str:
        """
        Generate a narrative for discovering items or secrets.
        
        Args:
            item_name: Name of the discovered item
            description: Description of the item
            
        Returns:
            Discovery narrative
        """
        template = random.choice(self.discovery_templates)
        
        return template.format(
            item=item_name,
            description=description
        )
    
    def generate_quest_narrative(self, 
                               quest_type: str,
                               quest_details: Dict[str, Any]) -> str:
        """
        Generate a narrative for quest-related events.
        
        Args:
            quest_type: Type of quest narrative (offer, progress, completion)
            quest_details: Details about the quest
            
        Returns:
            Quest narrative
        """
        quest_giver = quest_details.get('giver', 'The individual')
        quest_name = quest_details.get('name', 'the task')
        
        if quest_type == 'offer':
            return f"{quest_giver} offers you a quest: {quest_name}. {quest_details.get('description', '')}"
        
        elif quest_type == 'progress':
            return f"You've made progress on {quest_name}. {quest_details.get('progress_description', '')}"
        
        elif quest_type == 'completion':
            return f"You've completed {quest_name}! {quest_details.get('completion_description', '')}"
        
        else:
            return f"Your quest {quest_name} continues. {quest_details.get('description', '')}"
    
    def change_narrative_style(self, style_name: str) -> None:
        """
        Change the current narrative style.
        
        Args:
            style_name: Name of the style to use
        """
        style_map = {
            'heroic': NarrativeStyle.HEROIC,
            'mysterious': NarrativeStyle.MYSTERIOUS,
            'gritty': NarrativeStyle.GRITTY,
            'whimsical': NarrativeStyle.WHIMSICAL,
            'dramatic': NarrativeStyle.DRAMATIC
        }
        
        if style_name.lower() in style_map:
            self.current_style = style_map[style_name.lower()]
            self.logger.info(f"Narrative style changed to {style_name}")
        else:
            self.logger.warning(f"Unknown narrative style: {style_name}")
    
    def adjust_tension(self, amount: float) -> None:
        """
        Adjust the tension level of the narrative.
        
        Args:
            amount: Amount to adjust tension by (positive or negative)
        """
        self.tension_level = max(0.0, min(1.0, self.tension_level + amount))
        self.logger.debug(f"Tension adjusted to {self.tension_level:.2f}")
        
        # If tension is very high, make a decision about narrative direction
        if self.tension_level > 0.8 and hasattr(self.ai_gm_brain, 'decision_logic'):
            context = {
                'tension': self.tension_level,
                'location': self.ai_gm_brain.current_location,
                'recent_events': [e.type.name for e in self.ai_gm_brain.recent_events[-5:]] if self.ai_gm_brain.recent_events else []
            }
            
            decision = self.ai_gm_brain.decision_logic.make_narrative_direction_decision(context)
            
            if decision.selected == 'provide_resolution':
                # Tension has peaked, start resolving it
                self.tension_level = max(0.0, self.tension_level - 0.2)
    
    def add_narrative_hook(self, hook: str) -> None:
        """
        Add a narrative hook to be used in descriptions.
        
        Args:
            hook: Narrative hook to add
        """
        self.narrative_hooks.append(hook)
        # Keep the list manageable
        if len(self.narrative_hooks) > 10:
            self.narrative_hooks = self.narrative_hooks[-10:]
    
    def _generate_sensory_detail(self, location_type: str, sense_type: str) -> str:
        """
        Generate a sensory detail for a location.
        
        Args:
            location_type: Type of location
            sense_type: Type of sensory detail (sight, sound, smell)
            
        Returns:
            Sensory detail description
        """
        # Dictionary of sensory details by location and sense
        sensory_details = {
            'forest': {
                'sight': [
                    "Shafts of sunlight pierce through the dense canopy.",
                    "Colorful mushrooms sprout from decaying logs.",
                    "A deer bounds away through the underbrush."
                ],
                'sound': [
                    "Birdsong echoes melodically through the trees.",
                    "Leaves rustle in the gentle breeze.",
                    "Branches creak and groan overhead."
                ],
                'smell': [
                    "The earthy scent of moss and wet soil fills your nostrils.",
                    "A hint of pine resin perfumes the air.",
                    "The sweet fragrance of wildflowers drifts on the breeze."
                ]
            },
            'mountain': {
                'sight': [
                    "Jagged peaks scrape the sky in the distance.",
                    "Hardy alpine flowers dot the rocky terrain.",
                    "An eagle soars on thermals high above."
                ],
                'sound': [
                    "The wind howls through craggy rock formations.",
                    "Loose stones clatter down the mountainside.",
                    "The distant cry of a bird of prey echoes across the valley."
                ],
                'smell': [
                    "The air carries the crisp scent of snow and stone.",
                    "Wild mountain herbs release their fragrance as you brush past.",
                    "The thin atmosphere feels pure in your lungs."
                ]
            },
            'cave': {
                'sight': [
                    "Crystal formations catch and reflect what little light there is.",
                    "Strange fungi glow with an eerie bioluminescence.",
                    "The cave narrows into a tunnel ahead."
                ],
                'sound': [
                    "Water drips steadily, echoing through the chamber.",
                    "Something skitters away into the darkness.",
                    "Your footsteps resonate strangely in the enclosed space."
                ],
                'smell': [
                    "The musty scent of dampness and decay pervades the air.",
                    "A mineral tang fills your nostrils.",
                    "There's a faint hint of something animal lingering nearby."
                ]
            },
            'village': {
                'sight': [
                    "Smoke rises from chimneys in lazy spirals.",
                    "Children play in the dirt street, pausing to stare at you.",
                    "Colorful laundry hangs between buildings, drying in the sun."
                ],
                'sound': [
                    "The rhythmic clang of a blacksmith's hammer rings out.",
                    "Livestock make noises from nearby pens.",
                    "Animated conversation drifts from the tavern door."
                ],
                'smell': [
                    "The aroma of fresh-baked bread makes your stomach rumble.",
                    "Woodsmoke mingles with the scent of cooking food.",
                    "Livestock and tanned leather create a distinctly rural bouquet."
                ]
            },
            'city': {
                'sight': [
                    "People of all descriptions bustle through the streets.",
                    "Elaborate signs hang above shop doorways.",
                    "Guards in uniform patrol the thoroughfare."
                ],
                'sound': [
                    "The cacophony of dozens of conversations fills the air.",
                    "Street vendors call out their wares in singsong voices.",
                    "The clatter of wagon wheels on cobblestones creates a constant backdrop."
                ],
                'smell': [
                    "A confusing mixture of spices, perfumes, and body odor wafts through the air.",
                    "The scent of street food vendors' cooking makes your mouth water.",
                    "The less pleasant smells of an urban area remind you of the city's darker side."
                ]
            },
            'dungeon': {
                'sight': [
                    "Ancient runes are carved into the weathered stone walls.",
                    "Cobwebs hang from corners and crevices.",
                    "Something has left claw marks on the floor."
                ],
                'sound': [
                    "A distant dripping echoes through the corridors.",
                    "The sound of your movement seems unnaturally loud in the stillness.",
                    "A faint whisper of air suggests passages to unknown places."
                ],
                'smell': [
                    "The stale air carries the mustiness of centuries.",
                    "A faint metallic tang suggests old bloodshed.",
                    "The unmistakable odor of decay pervades everything."
                ]
            }
        }
        
        # Get details for this location or use generic details
        location_details = sensory_details.get(location_type.lower(), {
            'sight': ["The view is unremarkable."],
            'sound': ["It's relatively quiet here."],
            'smell': ["The air carries no distinctive scent."]
        })
        
        # Get details for this sense or use a generic response
        sense_details = location_details.get(sense_type.lower(), ["Nothing notable."])
        
        # Return a random detail
        return random.choice(sense_details)


# Extension function to add narrative generation to AI GM Brain
def extend_ai_gm_brain_with_narrative(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with narrative generation capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create narrative generator
    narrative_generator = NarrativeGenerator(ai_gm_brain)
    
    # Store the narrative generator for future reference
    ai_gm_brain.narrative_generator = narrative_generator