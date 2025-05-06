import random
from typing import Dict, List, Optional, Tuple, Any, Union
import uuid
from datetime import datetime

from ..shared.models import (
    Character, 
    Domain, 
    DomainType, 
    Tag,
    TagCategory,
    GrowthTier,
    GrowthLogEntry
)
from .shadow_profile import ShadowProfile


class GameEngine:
    """Core game engine that handles game mechanics and state transitions"""
    
    def __init__(self, storage=None, memory_manager=None, ai_service=None):
        """Initialize the game engine
        
        Args:
            storage: Storage service for persistence
            memory_manager: Memory manager for game history
            ai_service: AI service for narrative generation
        """
        self.storage = storage
        self.memory_manager = memory_manager
        self.ai_service = ai_service
        
        # Initialize standard tags - these would typically be loaded from a database
        self.standard_tags = self._initialize_standard_tags()
        
        # Track character shadow profiles
        self.shadow_profiles: Dict[str, ShadowProfile] = {}
    
    def _initialize_standard_tags(self) -> Dict[str, Tag]:
        """Create the standard tags for the game"""
        tags = {}
        
        # Combat Tags
        tags["melee"] = Tag(
            name="Melee",
            category=TagCategory.COMBAT,
            description="Close-quarters combat with weapons",
            domains=[DomainType.BODY, DomainType.AWARENESS]
        )
        tags["archery"] = Tag(
            name="Archery",
            category=TagCategory.COMBAT,
            description="Ranged combat with bows and similar weapons",
            domains=[DomainType.AWARENESS, DomainType.BODY]
        )
        tags["tactics"] = Tag(
            name="Tactics",
            category=TagCategory.COMBAT,
            description="Battle planning and strategic combat",
            domains=[DomainType.MIND, DomainType.AUTHORITY]
        )
        
        # Crafting Tags
        tags["blacksmith"] = Tag(
            name="Blacksmith",
            category=TagCategory.CRAFTING,
            description="Forging and metalworking",
            domains=[DomainType.CRAFT, DomainType.BODY]
        )
        tags["alchemy"] = Tag(
            name="Alchemy",
            category=TagCategory.CRAFTING,
            description="Creating potions and chemical substances",
            domains=[DomainType.CRAFT, DomainType.MIND]
        )
        tags["cooking"] = Tag(
            name="Cooking",
            category=TagCategory.CRAFTING,
            description="Food preparation and culinary arts",
            domains=[DomainType.CRAFT, DomainType.AWARENESS]
        )
        
        # Social Tags
        tags["persuasion"] = Tag(
            name="Persuasion",
            category=TagCategory.SOCIAL,
            description="Convincing others through argument",
            domains=[DomainType.SOCIAL, DomainType.MIND]
        )
        tags["intimidation"] = Tag(
            name="Intimidation",
            category=TagCategory.SOCIAL,
            description="Using fear to influence others",
            domains=[DomainType.SOCIAL, DomainType.BODY]
        )
        tags["deception"] = Tag(
            name="Deception",
            category=TagCategory.SOCIAL,
            description="Lying and misleading others convincingly",
            domains=[DomainType.SOCIAL, DomainType.AWARENESS]
        )
        
        # Magic Tags 
        tags["elemental"] = Tag(
            name="Elemental Magic",
            category=TagCategory.MAGIC,
            description="Control of natural elements",
            domains=[DomainType.MIND, DomainType.SPIRIT]
        )
        tags["divination"] = Tag(
            name="Divination",
            category=TagCategory.MAGIC,
            description="Seeing the future and sensing the unknown",
            domains=[DomainType.SPIRIT, DomainType.AWARENESS]
        )
        
        # Kingdom Tags
        tags["leadership"] = Tag(
            name="Leadership",
            category=TagCategory.KINGDOM,
            description="Inspiring and directing groups",
            domains=[DomainType.AUTHORITY, DomainType.SOCIAL]
        )
        tags["economics"] = Tag(
            name="Economics",
            category=TagCategory.KINGDOM,
            description="Managing finances and trade",
            domains=[DomainType.MIND, DomainType.SOCIAL]
        )
        tags["politics"] = Tag(
            name="Politics",
            category=TagCategory.KINGDOM,
            description="Navigating political systems and power structures",
            domains=[DomainType.SOCIAL, DomainType.AUTHORITY]
        )
        
        return tags
    
    def create_character(self, name: str) -> Character:
        """Create a new character with default attributes"""
        character = Character(name=name)
        
        # Give starting character some standard tags
        character.tags["melee"] = self.standard_tags["melee"]
        character.tags["persuasion"] = self.standard_tags["persuasion"]
        
        # Default starting domain distribution (allowing player to customize this later)
        character.domains[DomainType.BODY].value = 2
        character.domains[DomainType.MIND].value = 2
        character.domains[DomainType.SOCIAL].value = 1
        character.domains[DomainType.AWARENESS].value = 1
        
        # Create a shadow profile for this character
        self.shadow_profiles[character.id] = ShadowProfile(character.id)
        
        return character
    
    def perform_action(self, character: Character, action_type: str, 
                     domain_type: DomainType, tag_name: Optional[str] = None,
                     difficulty: int = 10) -> dict:
        """Perform a character action using the domain+tag system
        
        Args:
            character: The character performing the action
            action_type: Description of the action being performed
            domain_type: Primary domain being used
            tag_name: Optional specific tag/skill being applied
            difficulty: Difficulty class (DC) of the check
            
        Returns:
            Result dictionary with success/failure and details
        """
        # Perform the check
        result = character.roll_check(domain_type, tag_name, difficulty)
        
        # Add action context
        result["action"] = action_type
        result["domain"] = domain_type.value
        result["tag"] = tag_name if tag_name else None
        
        # Add some narrative flavor based on the margin of success/failure
        if result["success"]:
            if result["margin"] >= 10:
                result["quality"] = "exceptional"
            elif result["margin"] >= 5:
                result["quality"] = "good"
            else:
                result["quality"] = "adequate"
        else:
            if result["margin"] <= -10:
                result["quality"] = "disastrous"
            elif result["margin"] <= -5:
                result["quality"] = "bad"
            else:
                result["quality"] = "near miss"
        
        # Update the character's domain growth log with the action
        domain = character.domains[domain_type]
        domain.add_growth_log_entry(action_type, result["success"])
        
        # Update shadow profile
        if character.id in self.shadow_profiles:
            # Weight by difficulty and margin
            weight = max(1, int(difficulty / 5))  # Base weight from difficulty
            if result["success"]:
                weight += max(1, int(result["margin"] / 3))  # Bonus from high margin
                
            # Log the domain use in the shadow profile
            self.shadow_profiles[character.id].log_domain_use(
                domain=domain_type, 
                action=action_type,
                amount=weight
            )
        
        return result
    
    def add_tag_to_character(self, character: Character, tag_name: str) -> bool:
        """Add a tag to a character if it exists in standard tags"""
        if tag_name in self.standard_tags and tag_name not in character.tags:
            character.tags[tag_name] = self.standard_tags[tag_name]
            return True
        return False
    
    def process_domain_drift(self, character: Character, life_event: str) -> dict:
        """Process domain drift based on character lifestyle changes
        
        Args:
            character: The character experiencing drift
            life_event: Description of the life change causing the drift
            
        Returns:
            Dictionary with drift results
        """
        # Find least used domains
        drift_candidates = character.get_domain_drift_candidates()
        
        # For now, just suggest the drift - in a full implementation
        # this would be more sophisticated based on the life_event
        return {
            "can_drift": len(drift_candidates) > 0,
            "drift_from_options": drift_candidates,
            "life_event": life_event,
            "domain_usage": {d.type.value: d.usage_count for d in character.domains.values()}
        }
    
    def apply_domain_drift(self, character: Character, 
                         from_domain: DomainType, to_domain: DomainType) -> bool:
        """Apply domain drift by shifting points between domains"""
        return character.drift_domain(from_domain, to_domain)
        
    def get_character_shadow_profile(self, character_id: str) -> dict:
        """Get shadow profile information for a character
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary with shadow profile details
        """
        if character_id not in self.shadow_profiles:
            return {"error": "Shadow profile not found"}
        
        profile = self.shadow_profiles[character_id]
        
        # Get dominant domains
        dominant_domains = profile.get_dominant_domains(3)
        dominant_formatted = []
        for domain, count in dominant_domains:
            dominant_formatted.append({
                "domain": domain.value,
                "count": count
            })
        
        # Get recent trend
        recent_trend = profile.get_recent_trend(7)
        recent_formatted = {}
        for domain, count in recent_trend.items():
            recent_formatted[domain.value] = count
        
        # Get personality profile
        personality = profile.get_personality_profile()
        
        return {
            "dominant_domains": dominant_formatted,
            "recent_trend": recent_formatted,
            "personality_profile": personality,
            "updated_at": profile.updated_at.isoformat()
        }
