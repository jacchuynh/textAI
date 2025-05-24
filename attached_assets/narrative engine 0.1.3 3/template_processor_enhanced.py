import re
import random
from typing import Dict, Any, List, Match, Optional

class TemplateProcessor:
    """
    Advanced template processor supporting extended conditional syntax, randomization,
    and contextual formatting for rich narrative generation.
    """
    def __init__(self):
        self.pronoun_sets = {
            "male": {
                "subjective": "he", "objective": "him", 
                "possessive": "his", "possessive_adj": "his", "reflexive": "himself"
            },
            "female": {
                "subjective": "she", "objective": "her", 
                "possessive": "hers", "possessive_adj": "her", "reflexive": "herself"
            },
            "neutral": {
                "subjective": "they", "objective": "them", 
                "possessive": "theirs", "possessive_adj": "their", "reflexive": "themselves"
            }
        }
        
        # Enhanced regex patterns for more complex conditions
        self._conditional_pattern = re.compile(r'\{IF\s+([^{}]+?)\}(.*?)(?:\{ELSE\}(.*?))?\{ENDIF\}', re.DOTALL)
        self._random_pattern = re.compile(r'\{RANDOM\[(.*?)\]\}')
        self._pronoun_pattern = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*?)\.([a-z_]+)\}')
        self._plural_conditional = re.compile(r'(\w+)\{IF\s+([^{}]+?)\}(\|s|\|es|\|ies)\{ENDIF\}')
        self._capitalize_pattern = re.compile(r'\{([A-Z][a-zA-Z_]*?)\.([a-z_]+)\}')
        self._nested_path_pattern = re.compile(r'\{([a-zA-Z_][a-zA-Z0-9_]*?)\.([a-zA-Z0-9_.]+)\}')

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

        # First iteration: Process regular conditionals 
        result = self._process_conditionals(template, context)
        
        # Second: Handle complex syntax like pluralization and capitalization
        result = self._process_plural_conditionals(result, context)
        result = self._process_capitalization(result, context)
        
        # Third: Process randomization
        result = self._process_random_choices(result)
        
        # Fourth: Process pronouns and nested paths
        result = self._process_pronouns(result, context)
        result = self._process_nested_paths(result, context)
        
        # Finally: Process standard variable replacements
        for key, value in context.items():
            if isinstance(value, (str, int, float, bool)):
                placeholder = "{" + key + "}"
                if placeholder in result:
                    result = result.replace(placeholder, str(value))
        
        return result

    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process conditional sections with support for logical operators.
        Handles: {IF condition}...{ELSE}...{ENDIF}
        """
        def replace_conditional(match: Match) -> str:
            condition_expr = match.group(1).strip()
            if_text = match.group(2)
            else_text = match.group(3) if match.group(3) else ""
            
            # Support for logical operators
            if "||" in condition_expr:
                conditions = condition_expr.split("||")
                result = any(self._evaluate_condition(cond.strip(), context) for cond in conditions)
            elif "&&" in condition_expr:
                conditions = condition_expr.split("&&")
                result = all(self._evaluate_condition(cond.strip(), context) for cond in conditions)
            else:
                result = self._evaluate_condition(condition_expr, context)
                
            return if_text if result else else_text
        
        return self._conditional_pattern.sub(replace_conditional, template)
    
    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a single condition string against the context.
        Handles comparison operators: ==, !=, >, <, >=, <=
        """
        # Check for comparison operators
        if "==" in condition:
            left, right = condition.split("==", 1)
            left_val = self._resolve_value(left.strip(), context)
            right_val = self._resolve_value(right.strip(), context)
            return left_val == right_val
        elif "!=" in condition:
            left, right = condition.split("!=", 1)
            left_val = self._resolve_value(left.strip(), context)
            right_val = self._resolve_value(right.strip(), context)
            return left_val != right_val
        elif ">=" in condition:
            left, right = condition.split(">=", 1)
            left_val = self._resolve_value(left.strip(), context)
            right_val = self._resolve_value(right.strip(), context)
            return left_val >= right_val
        elif "<=" in condition:
            left, right = condition.split("<=", 1)
            left_val = self._resolve_value(left.strip(), context)
            right_val = self._resolve_value(right.strip(), context)
            return left_val <= right_val
        elif ">" in condition:
            left, right = condition.split(">", 1)
            left_val = self._resolve_value(left.strip(), context)
            right_val = self._resolve_value(right.strip(), context)
            return left_val > right_val
        elif "<" in condition:
            left, right = condition.split("<", 1)
            left_val = self._resolve_value(left.strip(), context)
            right_val = self._resolve_value(right.strip(), context)
            return left_val < right_val
        
        # Simple boolean check
        return bool(self._resolve_value(condition, context))
    
    def _resolve_value(self, value_expr: str, context: Dict[str, Any]) -> Any:
        """
        Resolve a value expression that might be a path into context or a literal.
        """
        # Check if it's a quoted string
        if (value_expr.startswith("'") and value_expr.endswith("'")) or \
           (value_expr.startswith('"') and value_expr.endswith('"')):
            return value_expr[1:-1]
        
        # Check if it's a number
        try:
            return int(value_expr)
        except ValueError:
            try:
                return float(value_expr)
            except ValueError:
                pass
        
        # Check if it's a dotted path in context
        if "." in value_expr:
            parts = value_expr.split(".")
            current = context
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif hasattr(current, part):
                    current = getattr(current, part)
                else:
                    return None
            return current
        
        # It's a direct context key
        return context.get(value_expr)

    def _process_random_choices(self, template: str) -> str:
        """Process {RANDOM[option1|option2|option3]} syntax."""
        def replace_random(match: Match) -> str:
            choices = match.group(1).split('|')
            choices = [choice.strip() for choice in choices]
            return random.choice(choices)
        
        return self._random_pattern.sub(replace_random, template)

    def _process_plural_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process pluralization conditionals like: 
        attempt{IF gender == 'neutral'}|s{ENDIF}
        """
        def replace_plural(match: Match) -> str:
            word = match.group(1)
            condition = match.group(2)
            suffix = match.group(3)[1:]  # Remove the pipe
            
            if self._evaluate_condition(condition, context):
                return word  # No suffix for condition=true
            else:
                return word + suffix
                
        return self._plural_conditional.sub(replace_plural, template)
    
    def _process_capitalization(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process capitalization markers like {Actor.subjective} → "He" instead of "he"
        """
        def replace_capitalized(match: Match) -> str:
            entity = match.group(1).lower()  # Convert Actor → actor
            pronoun_type = match.group(2)
            
            # Get the regular pronoun first
            result = ""
            if entity in context:
                entity_data = context[entity]
                if isinstance(entity_data, dict) and "gender" in entity_data:
                    gender = entity_data["gender"]
                    pronouns = self.pronoun_sets.get(gender, self.pronoun_sets["neutral"])
                    if pronoun_type in pronouns:
                        result = pronouns[pronoun_type]
                        
            if not result:
                # Fallback
                result = self.pronoun_sets["neutral"].get(pronoun_type, "they")
                
            # Capitalize first letter
            if result:
                result = result[0].upper() + result[1:]
                
            return result
            
        return self._capitalize_pattern.sub(replace_capitalized, template)

    def _process_pronouns(self, template: str, context: Dict[str, Any]) -> str:
        """Process pronoun references like {entity.subjective}."""
        def replace_pronoun(match: Match) -> str:
            entity = match.group(1)
            pronoun_type = match.group(2)
            
            if entity in context:
                entity_data = context[entity]
                if isinstance(entity_data, dict) and "gender" in entity_data:
                    gender = entity_data["gender"]
                    pronouns = self.pronoun_sets.get(gender, self.pronoun_sets["neutral"])
                    if pronoun_type in pronouns:
                        return pronouns[pronoun_type]
            
            # Default to neutral pronouns
            return self.pronoun_sets["neutral"].get(pronoun_type, "they")
        
        return self._pronoun_pattern.sub(replace_pronoun, template)

    def _process_nested_paths(self, template: str, context: Dict[str, Any]) -> str:
        """
        Process nested paths like {actor.emotions.joy} by traversing objects.
        """
        def replace_nested_path(match: Match) -> str:
            root_key = match.group(1)
            path = match.group(2)
            
            if root_key not in context:
                return f"[{root_key} not found]"
                
            current = context[root_key]
            for part in path.split('.'):
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif hasattr(current, part):
                    current = getattr(current, part)
                else:
                    return f"[{root_key}.{path} not valid]"
                    
            return str(current)
            
        return self._nested_path_pattern.sub(replace_nested_path, template)
    
    def process_batch(self, templates: List[str], context: Dict[str, Any]) -> List[str]:
        """Process multiple templates with the same context."""
        return [self.process(template, context) for template in templates]