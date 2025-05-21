"""
Monster database for the enhanced combat system.

This module loads monster definitions from YAML files and provides an interface
for creating instances of monsters based on these archetypes.
"""
from typing import Dict, List, Any, Optional, Tuple
import yaml
import os
import random
from enum import Enum, auto

from .monster_archetypes import ThreatTier, ThreatCategory, MonsterArchetype, MoveBehavior
from .combat_system_core import Combatant, CombatMove, Status, MoveType, Domain


class MonsterDatabase:
    """Database of monster archetypes loaded from YAML files"""
    
    def __init__(self):
        """Initialize the monster database"""
        self.archetypes: Dict[str, MonsterArchetype] = {}
        self.by_region: Dict[str, List[str]] = {}
        self.by_tier: Dict[ThreatTier, List[str]] = {}
        self.by_category: Dict[ThreatCategory, List[str]] = {}
    
    def load_from_yaml(self, yaml_file_path: str) -> None:
        """
        Load monster archetypes from a YAML file.
        
        Args:
            yaml_file_path: Path to the YAML file
        """
        try:
            with open(yaml_file_path, 'r') as yaml_file:
                data = yaml.safe_load(yaml_file)
                
            if not data or 'monster_archetypes' not in data:
                print(f"Warning: No monster archetypes found in {yaml_file_path}")
                return
            
            for monster_data in data['monster_archetypes']:
                archetype = self._create_archetype_from_yaml(monster_data)
                if archetype:
                    self.archetypes[archetype.id] = archetype
                    
                    # Add to tier index
                    tier = ThreatTier[monster_data.get('threat_tier', 'STANDARD').upper()]
                    if tier not in self.by_tier:
                        self.by_tier[tier] = []
                    self.by_tier[tier].append(archetype.id)
                    
                    # Add to category index
                    category_name = monster_data.get('category', 'Beast').split('/')[0].strip()
                    try:
                        category = ThreatCategory[category_name.upper()]
                    except KeyError:
                        category = ThreatCategory.BEAST
                    
                    if category not in self.by_category:
                        self.by_category[category] = []
                    self.by_category[category].append(archetype.id)
                    
                    # Extract region from file path
                    region = os.path.basename(yaml_file_path).split('_')[2].split('.')[0]
                    if region not in self.by_region:
                        self.by_region[region] = []
                    self.by_region[region].append(archetype.id)
            
            print(f"Loaded {len(data['monster_archetypes'])} monster archetypes from {yaml_file_path}")
        except Exception as e:
            print(f"Error loading monster archetypes from {yaml_file_path}: {e}")
    
    def _create_archetype_from_yaml(self, monster_data: Dict[str, Any]) -> Optional[MonsterArchetype]:
        """
        Create a monster archetype from YAML data.
        
        Args:
            monster_data: Dictionary of monster data from YAML
            
        Returns:
            MonsterArchetype or None if creation failed
        """
        try:
            name = monster_data.get('name', 'Unknown Monster')
            monster_id = name.lower().replace(' ', '_')
            
            # Parse description
            description = monster_data.get('description', '').strip()
            
            # Parse category
            category_str = monster_data.get('category', 'Beast')
            if '/' in category_str:
                # For dual categories, take the first one
                category_str = category_str.split('/')[0].strip()
            
            try:
                category = ThreatCategory[category_str.upper()]
            except KeyError:
                print(f"Warning: Unknown category '{category_str}' for monster '{name}', defaulting to BEAST")
                category = ThreatCategory.BEAST
            
            # Parse domains
            primary_domains = []
            for domain_str in monster_data.get('primary_domains', []):
                try:
                    primary_domains.append(Domain[domain_str])
                except KeyError:
                    print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
            
            weak_domains = []
            for domain_str in monster_data.get('weak_domains', []):
                try:
                    weak_domains.append(Domain[domain_str])
                except KeyError:
                    print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
            
            resistant_domains = []
            for domain_str in monster_data.get('resistant_domains', []):
                try:
                    resistant_domains.append(Domain[domain_str])
                except KeyError:
                    print(f"Warning: Unknown domain '{domain_str}' for monster '{name}'")
            
            # Parse threat tier
            tier_str = monster_data.get('threat_tier', 'standard').upper()
            try:
                tier = ThreatTier[tier_str]
            except KeyError:
                print(f"Warning: Unknown threat tier '{tier_str}' for monster '{name}', defaulting to STANDARD")
                tier = ThreatTier.STANDARD
            
            # Create move behaviors based on typical moves and special abilities
            move_behaviors = []
            
            # Parse typical moves
            for move_data in monster_data.get('typical_moves', []):
                move_name = move_data
                move_domain = None
                move_type = MoveType.FORCE
                
                # Check if move has domain specified in parentheses
                if '(' in move_data and ')' in move_data:
                    move_parts = move_data.split('(')
                    move_name = move_parts[0].strip()
                    domain_str = move_parts[1].strip(')').strip()
                    
                    try:
                        move_domain = Domain[domain_str]
                    except KeyError:
                        print(f"Warning: Unknown domain '{domain_str}' in move '{move_name}' for monster '{name}'")
                
                # Determine move type based on name hints
                if any(hint in move_name.lower() for hint in ['dodge', 'evade', 'hide', 'stealth', 'retreat']):
                    move_type = MoveType.DEFEND
                elif any(hint in move_name.lower() for hint in ['spell', 'magic', 'curse', 'hex', 'enchant']):
                    move_type = MoveType.FOCUS
                elif any(hint in move_name.lower() for hint in ['trick', 'deceive', 'confuse', 'distract']):
                    move_type = MoveType.TRICK
                elif any(hint in move_name.lower() for hint in ['utility', 'heal', 'buff', 'support']):
                    move_type = MoveType.UTILITY
                
                # Create move behavior
                domains = [move_domain] if move_domain else primary_domains[:1]
                
                move_behavior = MoveBehavior(
                    name=move_name,
                    description=f"{name} uses {move_name}",
                    move_type=move_type,
                    domains=domains,
                    priority=7,  # Default to medium-high priority
                    conditions={},
                    special_effects=[]
                )
                move_behaviors.append(move_behavior)
            
            # Parse special abilities for additional move behaviors or effects
            for ability in monster_data.get('special_abilities', []):
                # Add special effects to existing moves or create new utility moves
                for move in move_behaviors:
                    if any(keyword in ability.lower() for keyword in move.name.lower().split()):
                        move.special_effects.append(ability)
                        break
                else:
                    # Create a new utility move for this ability
                    move_behavior = MoveBehavior(
                        name=ability,
                        description=f"{name} uses {ability}",
                        move_type=MoveType.UTILITY,
                        domains=primary_domains[:1],
                        priority=5,  # Medium priority
                        conditions={},
                        special_effects=[ability]
                    )
                    move_behaviors.append(move_behavior)
            
            # Set stat modifiers based on threat tier
            health_mod = 1.0
            stamina_mod = 1.0
            focus_mod = 1.0
            spirit_mod = 1.0
            
            if tier == ThreatTier.MINION:
                health_mod = 0.7
                stamina_mod = 0.8
                focus_mod = 0.7
                spirit_mod = 0.7
            elif tier == ThreatTier.ELITE:
                health_mod = 1.5
                stamina_mod = 1.3
                focus_mod = 1.3
                spirit_mod = 1.3
            elif tier == ThreatTier.BOSS:
                health_mod = 2.5
                stamina_mod = 2.0
                focus_mod = 2.0
                spirit_mod = 2.0
            elif tier == ThreatTier.LEGENDARY:
                health_mod = 4.0
                stamina_mod = 3.0
                focus_mod = 3.0
                spirit_mod = 3.0
            
            # Create the archetype
            archetype = MonsterArchetype(
                id=monster_id,
                name=name,
                description=description,
                category=category,
                primary_domains=primary_domains,
                weak_domains=weak_domains,
                resistant_domains=resistant_domains,
                health_modifier=health_mod,
                stamina_modifier=stamina_mod,
                focus_modifier=focus_mod,
                spirit_modifier=spirit_mod,
                move_behaviors=move_behaviors,
                tier_adjustments=None,  # We'll use the default tier adjustments
                status_resistances=None,  # No specific status resistances
                status_vulnerabilities=None  # No specific status vulnerabilities
            )
            
            return archetype
        except Exception as e:
            print(f"Error creating monster archetype: {e}")
            return None
    
    def get_archetype(self, archetype_id: str) -> Optional[MonsterArchetype]:
        """
        Get a monster archetype by ID.
        
        Args:
            archetype_id: ID of the archetype
            
        Returns:
            MonsterArchetype or None if not found
        """
        return self.archetypes.get(archetype_id)
    
    def get_archetypes_by_region(self, region: str) -> List[MonsterArchetype]:
        """
        Get monster archetypes by region.
        
        Args:
            region: Region name
            
        Returns:
            List of MonsterArchetypes
        """
        archetype_ids = self.by_region.get(region, [])
        return [self.archetypes[archetype_id] for archetype_id in archetype_ids if archetype_id in self.archetypes]
    
    def get_archetypes_by_tier(self, tier: ThreatTier) -> List[MonsterArchetype]:
        """
        Get monster archetypes by threat tier.
        
        Args:
            tier: Threat tier
            
        Returns:
            List of MonsterArchetypes
        """
        archetype_ids = self.by_tier.get(tier, [])
        return [self.archetypes[archetype_id] for archetype_id in archetype_ids if archetype_id in self.archetypes]
    
    def get_archetypes_by_category(self, category: ThreatCategory) -> List[MonsterArchetype]:
        """
        Get monster archetypes by category.
        
        Args:
            category: Threat category
            
        Returns:
            List of MonsterArchetypes
        """
        archetype_ids = self.by_category.get(category, [])
        return [self.archetypes[archetype_id] for archetype_id in archetype_ids if archetype_id in self.archetypes]
    
    def get_random_archetype(self, 
                           region: Optional[str] = None, 
                           tier: Optional[ThreatTier] = None,
                           category: Optional[ThreatCategory] = None) -> Optional[MonsterArchetype]:
        """
        Get a random monster archetype with optional filters.
        
        Args:
            region: Optional region filter
            tier: Optional threat tier filter
            category: Optional category filter
            
        Returns:
            Random MonsterArchetype or None if no matches
        """
        filtered_ids = set(self.archetypes.keys())
        
        if region:
            region_ids = set(self.by_region.get(region, []))
            filtered_ids &= region_ids
        
        if tier:
            tier_ids = set(self.by_tier.get(tier, []))
            filtered_ids &= tier_ids
        
        if category:
            category_ids = set(self.by_category.get(category, []))
            filtered_ids &= category_ids
        
        if not filtered_ids:
            return None
        
        archetype_id = random.choice(list(filtered_ids))
        return self.archetypes.get(archetype_id)


# Initialize the global monster database
monster_database = MonsterDatabase()


def load_monster_database(data_dir: str = './data/monsters') -> None:
    """
    Load all monster YAML files from the data directory.
    
    Args:
        data_dir: Directory containing monster YAML files
    """
    try:
        if os.path.exists(data_dir):
            for filename in os.listdir(data_dir):
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    file_path = os.path.join(data_dir, filename)
                    monster_database.load_from_yaml(file_path)
        else:
            print(f"Monster data directory {data_dir} does not exist. No monsters loaded.")
    except Exception as e:
        print(f"Error loading monster database: {e}")


def get_monster_by_id(monster_id: str) -> Optional[MonsterArchetype]:
    """
    Get a monster by ID.
    
    Args:
        monster_id: ID of the monster
        
    Returns:
        MonsterArchetype or None if not found
    """
    return monster_database.get_archetype(monster_id)


def create_monster(
    archetype_id: str,
    name: Optional[str] = None,
    tier: Optional[ThreatTier] = None,
    level: int = 1,
    variant_type: Optional[str] = None
) -> Tuple[Combatant, List[CombatMove]]:
    """
    Create a monster from the database.
    
    Args:
        archetype_id: ID of the archetype
        name: Optional custom name for the monster
        tier: Optional override for the monster's tier
        level: Level of the monster
        variant_type: Optional variant type
        
    Returns:
        Tuple containing (monster_combatant, available_moves)
    """
    from .monster_archetypes import create_monster_from_archetype
    
    archetype = monster_database.get_archetype(archetype_id)
    if not archetype:
        raise ValueError(f"Monster archetype '{archetype_id}' not found")
    
    # Use provided name or generate one from the archetype
    if not name:
        name = archetype.name
    
    # Use provided tier or default to the archetype's tier
    if not tier:
        # Try to determine tier from archetype ID if available
        for t in ThreatTier:
            if t.name.lower() in archetype_id.lower():
                tier = t
                break
    
    return create_monster_from_archetype(
        archetype=archetype,
        name=name,
        tier=tier,
        level=level,
        variant_type=variant_type
    )


def get_random_monster(
    region: Optional[str] = None,
    tier: Optional[ThreatTier] = None,
    category: Optional[ThreatCategory] = None,
    level: int = 1
) -> Tuple[Combatant, List[CombatMove]]:
    """
    Get a random monster from the database with optional filters.
    
    Args:
        region: Optional region filter
        tier: Optional threat tier filter
        category: Optional category filter
        level: Level of the monster
        
    Returns:
        Tuple containing (monster_combatant, available_moves)
    """
    archetype = monster_database.get_random_archetype(region, tier, category)
    if not archetype:
        raise ValueError(f"No monster found matching the criteria (region={region}, tier={tier}, category={category})")
    
    return create_monster(
        archetype_id=archetype.id,
        tier=tier,
        level=level
    )