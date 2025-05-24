import re
import random
from typing import Dict, Any, List

class TemplateProcessor:
    """
    Advanced narrative template processor supporting:
    - Conditionals: {IF is_familiar}...{ELSE}...{ENDIF}
    - Randomization: {RANDOM[option1|option2|option3]}
    - Pronouns: {entity.subjective}, {entity.possessive}, etc.
    - Variable insertion: {variable_name}
    """

    def __init__(self):
        """Initialize the template processor with pronoun sets."""
        self.pronoun_sets = {
            "male": {
                "subjective": "he", 
                "objective": "him", 
                "possessive": "his", 
                "possessive_adj": "his",
                "reflexive": "himself"
            },
            "female": {
                "subjective": "she", 
                "objective": "her", 
                "possessive": "hers",
                "possessive_adj": "her", 
                "reflexive": "herself"
            },
            "neutral": {
                "subjective": "they", 
                "objective": "them", 
                "possessive": "theirs",
                "possessive_adj": "their", 
                "reflexive": "themselves"
            }
        }
        
        # Cache compiled regex patterns for performance
        self._conditional_pattern = re.compile(r'\{IF\s+([a-zA-Z0-9_]+)\}(.*?)\{ELSE\}(.*?)\{ENDIF\}', re.DOTALL)
        self._random_pattern = re.compile(r'\{RANDOM\[(.*?)\]\}')
        self._pronoun_pattern = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*?)\.([a-z_]+)\}')

    def process(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process a template with all advanced features.
        
        Args:
            template: Template string with placeholders and special syntax
            context: Dictionary of values to replace placeholders
            
        Returns:
            Processed template with all replacements made
        """
        if not template:
            return ""
            
        # Process special syntax in specific order
        result = template
        result = self._process_conditionals(result, context)
        result = self._process_random_choices(result)
        result = self._process_pronouns(result, context)
        
        # Process standard variable replacements
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                placeholder = "{" + key + "}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
        
        return result

    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Process conditional sections in template."""
        def replace_conditional(match):
            condition = match.group(1)
            if_text = match.group(2)
            else_text = match.group(3)
            
            # Check if condition exists and is truthy
            if context.get(condition):
                return if_text
            else:
                return else_text
        
        # Replace all conditional blocks
        return self._conditional_pattern.sub(replace_conditional, template)
    
    def _process_random_choices(self, template: str) -> str:
        """Process random choice sections in template."""
        def replace_random(match):
            choices = match.group(1).split('|')
            # Strip whitespace from each choice
            choices = [choice.strip() for choice in choices]
            return random.choice(choices)
        
        # Replace all random choice blocks
        return self._random_pattern.sub(replace_random, template)
    
    def _process_pronouns(self, template: str, context: Dict[str, Any]) -> str:
        """Process pronoun references in template."""
        def replace_pronoun(match):
            entity = match.group(1)
            pronoun_type = match.group(2)
            
            # Check if entity exists in context
            if entity in context:
                entity_data = context[entity]
                if isinstance(entity_data, dict) and "gender" in entity_data:
                    gender = entity_data["gender"]
                    pronouns = self.pronoun_sets.get(gender, self.pronoun_sets["neutral"])
                    
                    if pronoun_type in pronouns:
                        return pronouns[pronoun_type]
            
            # Default to neutral pronouns
            return self.pronoun_sets["neutral"].get(pronoun_type, "they")
        
        # Replace all pronoun references
        return self._pronoun_pattern.sub(replace_pronoun, template)
    
    def process_batch(self, templates: List[str], context: Dict[str, Any]) -> List[str]:
        """Process multiple templates with the same context."""
        return [self.process(template, context) for template in templates]