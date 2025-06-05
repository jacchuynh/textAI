import random
from typing import Dict, Any, List, Optional, Tuple

class AIGMDialogueGenerator:
    """
    Generates contextually appropriate NPC dialogue for the AI GM based on
    dialogue themes, character relationships, and world state.
    """
    
    def __init__(self, template_processor):
        """
        Initialize the dialogue generator.
        
        Args:
            template_processor: TemplateProcessor instance for processing dialogue templates
        """
        self.template_processor = template_processor
        self.dialogue_patterns = self._load_dialogue_patterns()
    
    def generate_dialogue(self, 
                         npc_id: str,
                         dialogue_themes: List[str],
                         context: Dict[str, Any],
                         player_id: str = None) -> str:
        """
        Generate appropriate dialogue for an NPC.
        
        Args:
            npc_id: ID of the speaking NPC
            dialogue_themes: List of themes to incorporate (e.g., "suspicion", "respect")
            context: Full context dictionary with world state, NPC info, etc.
            player_id: Optional ID of the player character being addressed
            
        Returns:
            Generated dialogue string
        """
        # Prepare specialized context for dialogue
        dialogue_context = self._prepare_dialogue_context(npc_id, player_id, context)
        
        # First, look for patterns that match ALL provided themes
        precise_matches = self._find_matching_patterns(dialogue_themes, exact=True)
        
        if precise_matches and random.random() < 0.7:  # 70% chance to use precise match
            # Select a random pattern that matches all themes
            pattern = random.choice(precise_matches)
            return self.template_processor.process(pattern, dialogue_context)
        
        # If no precise match or we choose variety, combine elements from multiple themes
        partial_matches = self._find_matching_patterns(dialogue_themes, exact=False)
        
        if not partial_matches:
            # Fallback if nothing matches
            return self._generate_fallback_dialogue(npc_id, dialogue_context)
        
        # Combine a greeting, body and closing from different matching patterns
        parts = []
        
        # Add greeting (30% chance)
        if random.random() < 0.3 and self.dialogue_patterns.get('greetings'):
            greeting = random.choice(self.dialogue_patterns['greetings'])
            parts.append(self.template_processor.process(greeting, dialogue_context))
        
        # Add main dialogue from theme patterns
        theme_pattern = random.choice(partial_matches)
        parts.append(self.template_processor.process(theme_pattern, dialogue_context))
        
        # Add closing (20% chance)
        if random.random() < 0.2 and self.dialogue_patterns.get('closings'):
            closing = random.choice(self.dialogue_patterns['closings'])
            parts.append(self.template_processor.process(closing, dialogue_context))
        
        return " ".join(parts)
    
    def _find_matching_patterns(self, themes: List[str], exact: bool = False) -> List[str]:
        """
        Find dialogue patterns that match the given themes.
        
        Args:
            themes: List of themes to match
            exact: If True, match only patterns with all themes. If False, match any pattern with any theme.
            
        Returns:
            List of matching dialogue patterns
        """
        matches = []
        
        if exact:
            # Only include patterns that match ALL themes
            theme_key = "+".join(sorted(themes))
            if theme_key in self.dialogue_patterns:
                matches.extend(self.dialogue_patterns[theme_key])
        else:
            # Include patterns that match ANY theme
            for theme in themes:
                if theme in self.dialogue_patterns:
                    matches.extend(self.dialogue_patterns[theme])
        
        return matches
    
    def _prepare_dialogue_context(self, npc_id: str, player_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a specialized context for dialogue generation.
        
        Args:
            npc_id: ID of the speaking NPC
            player_id: ID of the player character
            context: Full base context
            
        Returns:
            Dialogue-specific context dictionary
        """
        dialogue_context = dict(context)  # Start with full context
        
        # Add speaker NPC as 'npc'
        npc_name = self._get_character_name(npc_id)
        npc_gender = self._get_character_gender(npc_id)
        
        dialogue_context['npc'] = {
            'id': npc_id,
            'name': npc_name,
            'gender': npc_gender
        }
        
        # Add player as 'player' if provided
        if player_id:
            player_name = self._get_character_name(player_id)
            player_gender = self._get_character_gender(player_id)
            
            dialogue_context['player'] = {
                'id': player_id,
                'name': player_name,
                'gender': player_gender
            }
            
            # Add relationship context if available
            if 'relationship' in context:
                dialogue_context['relationship'] = context['relationship']
            else:
                # Add placeholder relationship
                dialogue_context['relationship'] = {'exists': False, 'quality': 'neutral'}
        
        return dialogue_context
    
    def _generate_fallback_dialogue(self, npc_id: str, context: Dict[str, Any]) -> str:
        """
        Generate fallback dialogue when no matching patterns are found.
        
        Args:
            npc_id: ID of the speaking NPC
            context: Context dictionary
            
        Returns:
            Fallback dialogue string
        """
        npc_name = context.get('npc', {}).get('name', f"NPC {npc_id}")
        
        fallbacks = [
            f"{npc_name} speaks briefly, but seems distracted.",
            f"{npc_name} acknowledges you with a nod but says little.",
            f"{npc_name} mutters something indistinct.",
            f"{npc_name} seems unwilling to engage in conversation right now."
        ]
        
        return random.choice(fallbacks)
    
    def _get_character_name(self, character_id: str) -> str:
        """Get character name from ID - placeholder implementation."""
        # In a real implementation, this would query character data
        character_names = {
            "player_character_id": "Thorn",
            "mountain_elder": "Elder Krag",
            "rival_warrior": "Varek the Bold",
            "constable": "Constable Marrin",
            "fence": "Whisper",
            "smuggler_captain": "Captain Morvis",
            "city_guard_captain": "Captain Elora Stonehelm"
        }
        return character_names.get(character_id, f"Character {character_id}")
    
    def _get_character_gender(self, character_id: str) -> str:
        """Get character gender from ID - placeholder implementation."""
        # In a real implementation, this would query character data
        character_genders = {
            "player_character_id": "male",
            "mountain_elder": "male",
            "rival_warrior": "male",
            "constable": "female",
            "fence": "female",
            "smuggler_captain": "male",
            "city_guard_captain": "female"
        }
        return character_genders.get(character_id, "neutral")
    
    def _load_dialogue_patterns(self) -> Dict[str, List[str]]:
        """
        Load dialogue patterns organized by themes.
        In a real implementation, this would load from a data file.
        
        Returns:
            Dictionary mapping theme(s) to list of dialogue patterns
        """
        return {
            # Single themes
            "wisdom": [
                "The path you seek is not always the one you find, {player.name}.",
                "I have seen many like you come and go. {IF world_state.active_global_threats}These times test us all.{ELSE}Each finding their own way.{ENDIF}",
                "There is knowledge in patience that cannot be gained through action alone."
            ],
            "tradition": [
                "Our ways have endured for generations, {player.name}. There is reason in what may seem senseless to outsiders.",
                "The rituals we preserve connect us to those who came before. Honor them with your respect.",
                "In following the old ways, we maintain what our ancestors fought to protect."
            ],
            "testing": [
                "Not all who attempt this challenge succeed, {player.name}. Are you certain you're prepared?",
                "I will observe your trial, but I cannot assist. The test must be faced alone.",
                "Your {IF player.gender == 'female'}determination{ELSE}confidence{ENDIF} is noted, but this challenge has humbled many before you."
            ],
            "caution": [
                "Speak softly. {IF world_state.political_stability == 'UNREST'}The wrong ears might be listening.{ELSE}Some matters are best discussed privately.{ENDIF}",
                "I don't know you well enough yet. Prove yourself before seeking deeper confidence.",
                "{IF relationship.quality == 'negative'}I've learned to be wary around your kind.{ELSE}Careful now. Even these walls may have ears.{ENDIF}"
            ],
            "suspicion": [
                "{IF relationship.value < 0}What do you really want? I doubt it's as simple as you claim.{ELSE}I must be cautious about who I trust these days.{ENDIF}",
                "Your reputation precedes you, {player.name}. Not all that I've heard inspires confidence.",
                "{IF world_state.political_stability == 'UNREST' || world_state.political_stability == 'REBELLION'}These days, a stranger's intentions are never clear until it's too late.{ELSE}Something about your story doesn't quite add up.{ENDIF}"
            ],
            
            # Combined themes
            "wisdom+tradition": [
                "Our traditions endure because they contain wisdom that has served generations. Study them before seeking to change them.",
                "The oldest teachings often reveal the deepest truths, {player.name}. Our ancestors knew more than we credit them for."
            ],
            "suspicion+caution": [
                "Step closer if you must speak, but know that my blade is ready. {IF world_state.political_stability == 'UNREST'}These are dangerous times.{ENDIF} Trust is a luxury I cannot afford.",
                "I'll hear your words, but keep your hands visible. {IF relationship.quality == 'negative'}I remember what happened last time.{ENDIF}"
            ],
            "testing+wisdom": [
                "This challenge will reveal more than your strength, {player.name}. It will show the true nature of your spirit.",
                "Many seek to pass this test for glory or reward. Few understand its true purpose is to transform the seeker."
            ],
            
            # Special categories
            "greetings": [
                "{IF time_of_day == 'morning'}Morning to you.{ELIF time_of_day == 'evening' || time_of_day == 'night'}Evening, {player.name}.{ELSE}Well met.{ENDIF}",
                "{IF relationship.quality == 'positive'}Good to see you again, {player.name}.{ELIF relationship.quality == 'negative'}Oh. It's you.{ELSE}Hello there.{ENDIF}",
                "{IF world_state.active_global_threats}Dangerous times for a meeting, but welcome nonetheless.{ELSE}Welcome, traveler.{ENDIF}"
            ],
            "closings": [
                "That's all I'll say on the matter.",
                "Now I must return to my duties.",
                "{IF relationship.value > 3}Until next time, friend.{ELSE}We'll speak again, perhaps.{ENDIF}",
                "{IF world_state.political_stability == 'UNREST' || world_state.political_stability == 'WAR'}Stay safe out there.{ELSE}May your path be clear.{ENDIF}"
            ]
        }