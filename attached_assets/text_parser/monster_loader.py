"""
Monster loader for the parser engine.

This module handles loading monster data from YAML files and
preprocessing it for use by the parser.
"""
from typing import Dict, List, Any, Optional, Union
import os
import yaml


def load_monster_yaml(file_path: str) -> Dict[str, Any]:
    """
    Load monster data from a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Dictionary of monster data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading monster file {file_path}: {e}")
        return {}


def load_all_monsters(yaml_files: Union[str, List[str]]) -> List[Dict]:
    """
    Load all monsters from the given YAML files.
    
    Args:
        yaml_files: Path to a directory containing YAML files, 
                  or a list of specific YAML file paths
    
    Returns:
        List of monster dictionaries
    """
    monster_list = []
    
    # Handle directory path
    if isinstance(yaml_files, str) and os.path.isdir(yaml_files):
        file_list = [os.path.join(yaml_files, f) for f in os.listdir(yaml_files) 
                    if f.endswith('.yaml') or f.endswith('.yml')]
    else:
        # Handle list of files
        file_list = yaml_files if isinstance(yaml_files, list) else [yaml_files]
    
    # Process each file
    for file_path in file_list:
        if not os.path.exists(file_path):
            print(f"Warning: File {file_path} does not exist")
            continue
        
        data = load_monster_yaml(file_path)
        
        # Extract monster archetypes
        if "monster_archetypes" in data:
            monster_list.extend(data["monster_archetypes"])
    
    # Add aliases for monsters
    for monster in monster_list:
        if 'aliases' not in monster:
            monster['aliases'] = []
            
        # Add threat tier as alias
        if 'threat_tier' in monster:
            monster['aliases'].append(monster['threat_tier'])
            
        # Add last word of name as alias (e.g., "Vine Weasel" -> "Weasel")
        name_parts = monster['name'].split()
        if len(name_parts) > 1 and name_parts[-1] not in monster['aliases']:
            monster['aliases'].append(name_parts[-1])
    
    return monster_list


def enrich_monster_data(monster_list: List[Dict]) -> List[Dict]:
    """
    Enrich monster data with derived fields.
    
    Args:
        monster_list: List of monster dictionaries
        
    Returns:
        Enriched list of monster dictionaries
    """
    for monster in monster_list:
        # Ensure required fields
        if 'name' not in monster:
            monster['name'] = "Unknown Monster"
            
        # Add adjectives array if not present
        if 'adjectives' not in monster:
            monster['adjectives'] = []
            
            # Extract adjectives from category
            if 'category' in monster:
                categories = monster['category'].split('/')
                for cat in categories:
                    monster['adjectives'].append(cat.strip())
            
            # Add threat tier as adjective
            if 'threat_tier' in monster:
                monster['adjectives'].append(monster['threat_tier'])
    
    return monster_list