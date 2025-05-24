"""
Template Processor Module

This module handles the processing of narrative templates with dynamic variables.
It supports simple replacements as well as more complex conditional logic.
"""

from typing import Dict, Any, List, Optional, Set, Union, Callable
import logging
import json
import random
import re
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class TemplateProcessor:
    """
    Processes narrative templates with variable substitution and conditional logic.
    
    Supports basic variable substitution (e.g., {character_name}), as well as
    conditional sections and template variations.
    """
    
    def __init__(self):
        """Initialize the template processor."""
        self.variable_pattern = re.compile(r'\{([^{}]*)\}')
        self.conditional_pattern = re.compile(r'\[\[if\s+([^]]*?)\]\](.*?)\[\[else\]\](.*?)\[\[endif\]\]', re.DOTALL)
        self.variation_pattern = re.compile(r'\[\[variation\]\](.*?)\[\[endvariation\]\]', re.DOTALL)
        self.template_cache = {}
    
    def process_template(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Process a template with variables.
        
        Args:
            template: Template string
            variables: Variables to substitute
            
        Returns:
            Processed template
        """
        # Process conditionals
        template = self._process_conditionals(template, variables)
        
        # Process variations
        template = self._process_variations(template)
        
        # Process variables
        template = self._substitute_variables(template, variables)
        
        return template
    
    def _substitute_variables(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in a template.
        
        Args:
            template: Template string
            variables: Variables to substitute
            
        Returns:
            Template with variables substituted
        """
        def replace_var(match):
            var_name = match.group(1).strip()
            
            # Check for nested properties (e.g., character.name)
            if '.' in var_name:
                parts = var_name.split('.')
                value = variables
                for part in parts:
                    if isinstance(value, dict) and part in value:
                        value = value[part]
                    else:
                        # Property not found, return empty string
                        return ""
                return str(value)
            
            # Simple variable
            if var_name in variables:
                return str(variables[var_name])
            else:
                # Variable not found, return empty string
                return ""
                
        return self.variable_pattern.sub(replace_var, template)
    
    def _process_conditionals(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Process conditional sections in a template.
        
        Args:
            template: Template string
            variables: Variables to evaluate conditions
            
        Returns:
            Template with conditionals processed
        """
        def replace_conditional(match):
            condition = match.group(1).strip()
            if_content = match.group(2)
            else_content = match.group(3)
            
            # Evaluate the condition
            if self._evaluate_condition(condition, variables):
                return if_content
            else:
                return else_content
                
        return self.conditional_pattern.sub(replace_conditional, template)
    
    def _process_variations(self, template: str) -> str:
        """
        Process variation sections in a template.
        
        Args:
            template: Template string
            
        Returns:
            Template with variations processed
        """
        def replace_variation(match):
            variations = match.group(1).strip().split('\n')
            variations = [v.strip() for v in variations if v.strip()]
            
            if variations:
                return random.choice(variations)
            else:
                return ""
                
        return self.variation_pattern.sub(replace_variation, template)
    
    def _evaluate_condition(self, condition: str, variables: Dict[str, Any]) -> bool:
        """
        Evaluate a condition string.
        
        Args:
            condition: Condition string
            variables: Variables to use in evaluation
            
        Returns:
            Result of condition evaluation
        """
        # Simple variable existence check
        if condition.startswith('exists '):
            var_name = condition[7:].strip()
            return var_name in variables
            
        # Equality check
        if ' == ' in condition:
            left, right = condition.split(' == ', 1)
            left = left.strip()
            right = right.strip()
            
            # Get left value
            left_value = variables.get(left, left)
            
            # Check if right is a variable or literal
            if right.startswith('"') and right.endswith('"'):
                right_value = right[1:-1]  # Remove quotes
            else:
                right_value = variables.get(right, right)
                
            return str(left_value) == str(right_value)
            
        # Greater than check
        if ' > ' in condition:
            left, right = condition.split(' > ', 1)
            left = left.strip()
            right = right.strip()
            
            # Get values
            left_value = float(variables.get(left, left))
            right_value = float(variables.get(right, right))
            
            return left_value > right_value
            
        # Less than check
        if ' < ' in condition:
            left, right = condition.split(' < ', 1)
            left = left.strip()
            right = right.strip()
            
            # Get values
            left_value = float(variables.get(left, left))
            right_value = float(variables.get(right, right))
            
            return left_value < right_value
            
        # Not equal check
        if ' != ' in condition:
            left, right = condition.split(' != ', 1)
            left = left.strip()
            right = right.strip()
            
            # Get left value
            left_value = variables.get(left, left)
            
            # Check if right is a variable or literal
            if right.startswith('"') and right.endswith('"'):
                right_value = right[1:-1]  # Remove quotes
            else:
                right_value = variables.get(right, right)
                
            return str(left_value) != str(right_value)
            
        # Default to False for unknown conditions
        logger.warning(f"Unknown condition: {condition}")
        return False
    
    def process_template_group(self, template_group: Dict[str, str], 
                            variables: Dict[str, Any], 
                            select_key: str = None) -> Dict[str, str]:
        """
        Process a group of templates.
        
        Args:
            template_group: Dictionary of templates
            variables: Variables to substitute
            select_key: Specific template key to process (if None, process all)
            
        Returns:
            Dictionary of processed templates
        """
        result = {}
        
        if select_key:
            # Process only the selected template
            if select_key in template_group:
                result[select_key] = self.process_template(template_group[select_key], variables)
        else:
            # Process all templates in the group
            for key, template in template_group.items():
                result[key] = self.process_template(template, variables)
                
        return result
    
    def select_and_process_template(self, templates: List[str], variables: Dict[str, Any]) -> str:
        """
        Select a random template from a list and process it.
        
        Args:
            templates: List of template strings
            variables: Variables to substitute
            
        Returns:
            Processed template
        """
        if not templates:
            return ""
            
        # Select a random template
        template = random.choice(templates)
        
        # Process the template
        return self.process_template(template, variables)
    
    def get_template_variables(self, template: str) -> Set[str]:
        """
        Extract all variables from a template.
        
        Args:
            template: Template string
            
        Returns:
            Set of variable names
        """
        variables = set()
        
        # Find all variable matches
        for match in self.variable_pattern.finditer(template):
            var_name = match.group(1).strip()
            
            # Handle nested properties (e.g., character.name)
            if '.' in var_name:
                var_name = var_name.split('.')[0]
                
            variables.add(var_name)
            
        return variables
    
    def validate_template(self, template: str) -> List[str]:
        """
        Validate a template for syntax errors.
        
        Args:
            template: Template string
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Check for unmatched conditional tags
        if_count = template.count('[[if')
        endif_count = template.count('[[endif]]')
        else_count = template.count('[[else]]')
        
        if if_count != endif_count:
            errors.append(f"Unmatched conditional tags: {if_count} [[if]] but {endif_count} [[endif]]")
            
        if else_count > if_count:
            errors.append(f"Too many [[else]] tags: {else_count} [[else]] but only {if_count} [[if]]")
            
        # Check for unmatched variation tags
        variation_count = template.count('[[variation]]')
        endvariation_count = template.count('[[endvariation]]')
        
        if variation_count != endvariation_count:
            errors.append(f"Unmatched variation tags: {variation_count} [[variation]] but {endvariation_count} [[endvariation]]")
            
        # Check for unmatched variable braces
        open_braces = template.count('{')
        close_braces = template.count('}')
        
        if open_braces != close_braces:
            errors.append(f"Unmatched variable braces: {open_braces} {{ but {close_braces} }}")
            
        return errors
    
    def load_templates_from_dict(self, templates_dict: Dict[str, Any]) -> None:
        """
        Load templates from a dictionary into the cache.
        
        Args:
            templates_dict: Dictionary of templates
        """
        self.template_cache.update(templates_dict)
    
    def load_templates_from_json(self, json_str: str) -> None:
        """
        Load templates from a JSON string into the cache.
        
        Args:
            json_str: JSON string containing templates
        """
        try:
            templates_dict = json.loads(json_str)
            self.load_templates_from_dict(templates_dict)
        except json.JSONDecodeError as e:
            logger.error(f"Error loading templates from JSON: {e}")
    
    def get_cached_template(self, template_key: str) -> Optional[str]:
        """
        Get a template from the cache.
        
        Args:
            template_key: Template key
            
        Returns:
            Template string or None if not found
        """
        return self.template_cache.get(template_key)
    
    def process_cached_template(self, template_key: str, variables: Dict[str, Any]) -> Optional[str]:
        """
        Process a template from the cache.
        
        Args:
            template_key: Template key
            variables: Variables to substitute
            
        Returns:
            Processed template or None if template not found
        """
        template = self.get_cached_template(template_key)
        
        if template is None:
            return None
            
        return self.process_template(template, variables)


# Create a singleton instance for global use
_template_processor = None

def get_template_processor() -> TemplateProcessor:
    """
    Get the global template processor instance.
    
    Returns:
        Global template processor instance
    """
    global _template_processor
    
    if _template_processor is None:
        _template_processor = TemplateProcessor()
        
    return _template_processor