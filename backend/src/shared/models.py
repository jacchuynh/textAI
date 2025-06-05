from enum import Enum, auto
from typing import Dict, List, Optional, Union, Set, Any
from pydantic import BaseModel, Field, validator
import uuid
import random
from datetime import datetime


class DomainType(str, Enum):
    """Enumeration of the seven domains of life"""
    BODY = "body"         # Physical health, stamina, manual labor, illness resistance
    MIND = "mind"         # Logic, learning, memory, magic theory, problem solving
    SPIRIT = "spirit"     # Willpower, luck, intuition, empathy, divine favor
    SOCIAL = "social"     # Persuasion, negotiation, reputation, manipulation
    CRAFT = "craft"       # Practical skills, making, fixing, performance under time pressure
    AUTHORITY = "authority" # Leadership, command, strategy, decree enforcement
    AWARENESS = "awareness" # Perception, reaction time, timing in social or combat interactions


class TagCategory(str, Enum):
    """Categories of tags for organizing them"""
    COMBAT = "combat"     # Combat-related tags
    CRAFTING = "crafting" # Crafting-related tags
    SOCIAL = "social"     # Social interaction tags
    MAGIC = "magic"       # Magic-related tags
    SURVIVAL = "survival" # Survival and wilderness tags
    KINGDOM = "kingdom"   # Kingdom management tags
    GENERAL = "general"   # General purpose tags


class Tag(BaseModel):
    """A tag represents a specific skill or knowledge area"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: TagCategory
    description: str
    domains: List[DomainType] = Field(description="Primary domains associated with this tag")
    rank: int = Field(default=0, ge=0, le=5, description="Current rank from 0-5")
    xp: int = Field(default=0, description="Experience points toward next rank")
    xp_required: int = Field(default=100, description="XP required for next rank")

    def gain_xp(self, amount: int) -> bool:
        """Add XP to this tag and return True if a rank up occurred"""
        self.xp += amount
        if self.xp >= self.xp_required and self.rank < 5:
            self.rank += 1
            self.xp = 0
            self.xp_required = self.xp_required * 2  # Double XP required for next rank
            return True
        return False


class GrowthTier(str, Enum):
    """Growth tiers for domains"""
    NOVICE = "novice"       # Range 0-2
    SKILLED = "skilled"     # Range 3-4
    EXPERT = "expert"       # Range 5-7
    MASTER = "master"       # Range 8-9
    PARAGON = "paragon"     # Range 10+


class GrowthLogEntry(BaseModel):
    """An entry in the domain growth log"""
    date: datetime = Field(default_factory=datetime.now)
    domain: DomainType
    action: str
    success: bool
    
    def __str__(self) -> str:
        return f"{self.date.strftime('%Y-%m-%d')} | {self.domain.value} | {self.action} | {'✅' if self.success else '❌'}"


# --- New Enums for Progression System ---
class ActionSignificanceTier(str, Enum):
    """Tiers for action significance in the progression system"""
    TRIVIAL = "trivial"
    MINOR = "minor"
    SIGNIFICANT = "significant"
    MAJOR = "major"
    LEGENDARY = "legendary"


class ResolutionMethod(str, Enum):
    """Methods for resolving actions"""
    DICE = "dice"
    PROBABILITY = "probability"
# --- End New Enums ---


class Domain(BaseModel):
    """A domain represents one of the seven core stats"""
    type: DomainType
    value: int = Field(default=0, ge=0, description="Current value, 0+ with higher tiers possible")
    growth_points: int = Field(default=0, description="Points accumulated toward next value increase")
    growth_required: int = Field(default=100, description="Points required for next value increase")
    usage_count: int = Field(default=0, description="How often this domain is used")
    growth_log: List[GrowthLogEntry] = Field(default_factory=list, description="Log of growth events")
    level_ups_required: int = Field(default=8, description="Number of log entries required for level up")
    
    def get_tier(self) -> GrowthTier:
        """Get the current growth tier based on value"""
        if self.value <= 2:
            return GrowthTier.NOVICE
        elif self.value <= 4:
            return GrowthTier.SKILLED
        elif self.value <= 7:
            return GrowthTier.EXPERT
        elif self.value <= 9:
            return GrowthTier.MASTER
        else:
            return GrowthTier.PARAGON
    
    def add_growth_log_entry(self, action: str, success: bool) -> bool:
        """Add a growth log entry and check for level up
        
        Args:
            action: Description of the action performed
            success: Whether the action was successful
            
        Returns:
            True if a level up occurred, False otherwise
        """
        # Add to log
        entry = GrowthLogEntry(
            domain=self.type,
            action=action,
            success=success
        )
        self.growth_log.append(entry)
        
        # Check if we have enough entries for a level up
        successful_entries = [e for e in self.growth_log if e.success]
        if len(successful_entries) >= self.level_ups_required:
            # Level up
            self.value += 1
            
            # Increase the required number of entries for next level
            self.level_ups_required += 1
            
            # Remove the entries we used for this level up
            # Keep the most recent ones that weren't used
            self.growth_log = self.growth_log[self.level_ups_required - 1:]
            
            return True
        return False
    
    def use(self, action: str, success: bool) -> bool:
        """Record a usage of this domain and return True if growth occurred"""
        self.usage_count += 1
        
        # Add growth points - more for success, less for failure
        points = 10 if success else 3  # "Hard Lesson" rule
        self.growth_points += points
        
        # Add to growth log
        level_up = self.add_growth_log_entry(action, success)
        
        return level_up


class Character(BaseModel):
    """Character model with domains and tags"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    character_class: Optional[str] = "Adventurer"
    background: Optional[str] = "Commoner"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Core domains
    domains: Dict[DomainType, Domain] = Field(default_factory=dict)
    
    # Character tags/skills
    tags: Dict[str, Tag] = Field(default_factory=dict)
    
    # Track domain usage history for the "drift" mechanic
    domain_history: Dict[DomainType, List[int]] = Field(default_factory=dict)
    
    # --- New Player Profile Attributes ---
    declared_goals: List[str] = Field(default_factory=list, description="Player-stated character development goals")
    learning_approach_preferences: List[str] = Field(default_factory=list, description="Player-stated learning preferences")
    value_system_preferences: List[str] = Field(default_factory=list, description="Player-stated value system")
    relationship_priorities: List[str] = Field(default_factory=list, description="Player-stated relationship priorities")
    
    demonstrated_values: Dict[str, int] = Field(default_factory=dict, description="Track consistency of demonstrated values (e.g., 'mercy': 5)")
    relationship_investments: Dict[str, int] = Field(default_factory=dict, description="Track investment with NPCs (e.g., 'npc_id_or_name': 10)")
    risk_tolerance: Optional[str] = Field(default="moderate", description="Player's general risk tolerance (e.g., 'cautious', 'moderate', 'bold')")
    
    # --- New Progression System Attributes ---
    insight_points: int = Field(default=0, description="Insight Points for alternative progression")
    mastery_paths: List[Dict[str, Any]] = Field(default_factory=list, description="Unlocked/active mastery paths, e.g., [{'path_name': 'Tactical Spellsword', 'domain': 'mind', 'active': True}]")
    growth_momentum: Dict[DomainType, float] = Field(default_factory=lambda: {domain: 1.0 for domain in DomainType}, description="Growth momentum multipliers per domain")
    # --- End New Attributes ---
    
    @validator('domains', pre=True, always=True)
    def set_domains(cls, domains):
        """Ensure all domains exist with default values"""
        result = domains or {}
        for domain_type in DomainType:
            if domain_type not in result:
                result[domain_type] = Domain(type=domain_type)
        return result
    
    class Config:
        """Pydantic configuration"""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            DomainType: lambda v: v.value if hasattr(v, 'value') else str(v),
            TagCategory: lambda v: v.value if hasattr(v, 'value') else str(v)
        }
        
    def model_dump(self, **kwargs):
        """Custom model dump to handle serialization issues"""
        data = super().model_dump(**kwargs)
        
        # Ensure domains are properly serialized
        if 'domains' in data:
            serialized_domains = {}
            for domain_type, domain in data['domains'].items():
                key = domain_type.value if hasattr(domain_type, 'value') else str(domain_type)
                serialized_domains[key] = domain
            data['domains'] = serialized_domains
            
        # Ensure tags are properly serialized
        if 'tags' in data:
            serialized_tags = {}
            for tag_name, tag in data['tags'].items():
                serialized_tags[tag_name] = tag
            data['tags'] = serialized_tags
            
        # Ensure domain_history is properly serialized
        if 'domain_history' in data:
            serialized_history = {}
            for domain_type, history in data['domain_history'].items():
                key = domain_type.value if hasattr(domain_type, 'value') else str(domain_type)
                serialized_history[key] = history
            data['domain_history'] = serialized_history
            
        return data
    
    def roll_check(self, domain_type: DomainType, tag_name: Optional[str] = None, difficulty: int = 10) -> dict:
        """Perform a domain check with optional tag bonus
        
        Args:
            domain_type: The primary domain to use
            tag_name: Optional tag to add if character has it
            difficulty: DC of the check (default 10)
            
        Returns:
            Result dict with success flag, roll details, and margin
        """
        import random
        
        # Get the domain
        domain = self.domains[domain_type]
        
        # Roll d20
        d20_roll = random.randint(1, 20)
        
        # Calculate total with domain bonus
        total = d20_roll + domain.value
        roll_breakdown = f"d20({d20_roll}) + {domain_type.value}({domain.value})"
        
        # Add tag bonus if applicable
        tag_bonus = 0
        if tag_name and tag_name in self.tags:
            tag = self.tags[tag_name]
            tag_bonus = tag.rank
            total += tag_bonus
            roll_breakdown += f" + {tag_name}({tag_bonus})"
        
        # Determine success and margin
        success = total >= difficulty
        margin = total - difficulty
        
        # Record domain usage
        domain.use("Domain check", success)
        
        # Record tag usage if applicable
        if tag_name and tag_name in self.tags and success:
            self.tags[tag_name].gain_xp(10)  # Award XP for successful use
        
        # Return result with details
        return {
            "success": success,
            "roll": d20_roll,
            "domain_bonus": domain.value,
            "tag_bonus": tag_bonus,
            "total": total,
            "difficulty": difficulty,
            "margin": margin,
            "breakdown": roll_breakdown
        }
    
    def get_domain_drift_candidates(self) -> List[DomainType]:
        """Return domains that are candidates for drifting (least used)"""
        # Sort domains by usage count
        sorted_domains = sorted(self.domains.values(), key=lambda d: d.usage_count)
        
        # Return the types of the least used domains (bottom 2)
        return [d.type for d in sorted_domains[:2]]
    
    def drift_domain(self, from_domain: DomainType, to_domain: DomainType) -> bool:
        """Shift a point from one domain to another (domain drift mechanic)"""
        if from_domain == to_domain:
            return False
            
        if self.domains[from_domain].value > 0 and self.domains[to_domain].value < 5:
            self.domains[from_domain].value -= 1
            self.domains[to_domain].value += 1
            
            # Record this for character development history
            if from_domain not in self.domain_history:
                self.domain_history[from_domain] = []
            if to_domain not in self.domain_history:
                self.domain_history[to_domain] = []
                
            self.domain_history[from_domain].append(-1)
            self.domain_history[to_domain].append(1)
            
            return True
        return False
    
    def roll_check_advanced(self, 
                           domain_type: DomainType, 
                           tag_name: Optional[str] = None, 
                           difficulty: int = 10,
                           action_data: Optional[Dict[str, Any]] = None,
                           target: Optional[Dict[str, Any]] = None,
                           combat_state: Optional[Dict[str, Any]] = None,
                           multiple_domains: Optional[List[DomainType]] = None,
                           multiple_tags: Optional[List[str]] = None) -> dict:
        """Perform an advanced domain check with comprehensive combat mechanics
        
        Args:
            domain_type: The primary domain to use
            tag_name: Optional primary tag to add if character has it
            difficulty: Base DC of the check (default 10)
            action_data: Optional action data with tags, effects, etc.
            target: Optional target for resistance/weakness calculations
            combat_state: Optional combat state for environmental factors
            multiple_domains: Optional list of additional domains to include
            multiple_tags: Optional list of additional tags to include
            
        Returns:
            Result dict with success flag, roll details, margin, and breakdown
        """
        import random
        
        # Roll d20
        d20_roll = random.randint(1, 20)
        
        # Initialize tracking variables
        breakdown_parts = [f"d20({d20_roll})"]
        domains_used = [domain_type]
        tags_used = []
        
        # Calculate primary domain bonus
        if domain_type not in self.domains:
            raise ValueError(f"Domain {domain_type} not found for character")
            
        domain = self.domains[domain_type]
        domain_bonus = domain.value
        total = d20_roll + domain_bonus
        breakdown_parts.append(f"{domain_type.value}({domain_bonus})")
        
        # Add multiple domains if specified
        if multiple_domains:
            for extra_domain in multiple_domains:
                if extra_domain in self.domains and extra_domain != domain_type:
                    extra_bonus = self.domains[extra_domain].value
                    total += extra_bonus
                    breakdown_parts.append(f"{extra_domain.value}({extra_bonus})")
                    domains_used.append(extra_domain)
        
        # Calculate tag bonuses
        tag_bonus = 0
        
        # Primary tag
        if tag_name and tag_name in self.tags:
            tag = self.tags[tag_name]
            tag_bonus += tag.rank
            breakdown_parts.append(f"{tag_name}({tag.rank})")
            tags_used.append(tag_name)
        
        # Multiple tags if specified
        if multiple_tags:
            for extra_tag in multiple_tags:
                if extra_tag in self.tags and extra_tag != tag_name:
                    tag = self.tags[extra_tag]
                    tag_bonus += tag.rank
                    breakdown_parts.append(f"{extra_tag}({tag.rank})")
                    tags_used.append(extra_tag)
        
        # Add tag bonuses from action_data
        if action_data and action_data.get("tags"):
            for action_tag in action_data["tags"]:
                if action_tag in self.tags and action_tag not in tags_used:
                    tag = self.tags[action_tag]
                    tag_bonus += tag.rank
                    breakdown_parts.append(f"{action_tag}({tag.rank})")
                    tags_used.append(action_tag)
        
        total += tag_bonus
        
        # Calculate final difficulty with all modifiers
        final_difficulty = difficulty
        difficulty_modifiers = []
        
        # Target-based modifiers
        if target:
            # Enemy level adjustment
            level_mod = target.get("level", 0)
            if level_mod > 0:
                final_difficulty += level_mod
                difficulty_modifiers.append(f"enemy_level(+{level_mod})")
            
            # Target resistances
            if action_data and action_data.get("tags"):
                for resistance in target.get("resistances", []):
                    if resistance in action_data["tags"]:
                        final_difficulty += 2
                        difficulty_modifiers.append(f"resistance(+2)")
                
                # Target weaknesses
                for weakness in target.get("weaknesses", []):
                    if weakness in action_data["tags"]:
                        final_difficulty -= 2
                        difficulty_modifiers.append(f"weakness(-2)")
        
        # Environmental modifiers
        if combat_state:
            for factor in combat_state.get("environment", []):
                if factor == "Darkness" and action_data and "light" not in action_data.get("tags", []):
                    final_difficulty += 1
                    difficulty_modifiers.append("darkness(+1)")
                elif factor == "Slippery Ground" and action_data and action_data.get("action_type") == "maneuver":
                    final_difficulty += 1
                    difficulty_modifiers.append("slippery(+1)")
                elif factor == "High Ground" and action_data and action_data.get("action_type") == "attack":
                    final_difficulty -= 1
                    difficulty_modifiers.append("high_ground(-1)")
                elif factor == "Poor Visibility":
                    final_difficulty += 1
                    difficulty_modifiers.append("visibility(+1)")
            
            # Momentum modifiers
            momentum = combat_state.get("momentum")
            if momentum == "player":
                final_difficulty -= 1
                difficulty_modifiers.append("momentum(-1)")
            elif momentum == "enemy":
                final_difficulty += 1
                difficulty_modifiers.append("momentum(+1)")
        
        # Action-specific difficulty modifier
        if action_data and action_data.get("difficulty_modifier"):
            mod = action_data["difficulty_modifier"]
            final_difficulty += mod
            if mod != 0:
                sign = "+" if mod > 0 else ""
                difficulty_modifiers.append(f"action({sign}{mod})")
        
        # Status effect modifiers (if character has them)
        status_bonus = 0
        if hasattr(self, 'status_effects'):
            for effect in getattr(self, 'status_effects', []):
                if effect.get("type") == "advantage":
                    status_bonus += 2
                    breakdown_parts.append("advantage(+2)")
                elif effect.get("type") == "disadvantage":
                    status_bonus -= 2
                    breakdown_parts.append("disadvantage(-2)")
                elif effect.get("type") == "blessed":
                    status_bonus += 1
                    breakdown_parts.append("blessed(+1)")
                elif effect.get("type") == "cursed":
                    status_bonus -= 1
                    breakdown_parts.append("cursed(-1)")
        
        total += status_bonus
        
        # Ensure difficulty is at least 5
        final_difficulty = max(5, final_difficulty)
        
        # Determine success and calculate margin
        success = total >= final_difficulty
        margin = total - final_difficulty
        
        # Handle critical success/failure
        critical_success = d20_roll == 20
        critical_failure = d20_roll == 1
        
        # Override success for natural 20/1 in some cases
        if critical_success and margin >= -5:  # Natural 20 succeeds unless DC is way too high
            success = True
        elif critical_failure and margin <= 5:  # Natural 1 fails unless roll is way too high
            success = False
        
        # Record domain usage for ALL domains used
        action_description = action_data.get("label", "Advanced check") if action_data else "Advanced check"
        for domain_used in domains_used:
            if domain_used in self.domains:
                self.domains[domain_used].use(action_description, success)
        
        # Record tag usage and award XP for successful use
        if success:
            for tag_used in tags_used:
                if tag_used in self.tags:
                    xp_gain = 10 if not critical_success else 15  # Bonus XP for crits
                    self.tags[tag_used].gain_xp(xp_gain)
        
        # Build comprehensive breakdown string
        roll_breakdown = " + ".join(breakdown_parts)
        if difficulty_modifiers:
            difficulty_breakdown = f"DC {difficulty} + " + " + ".join(difficulty_modifiers) + f" = {final_difficulty}"
        else:
            difficulty_breakdown = f"DC {final_difficulty}"
        
        # Return comprehensive result
        result = {
            "success": success,
            "roll": d20_roll,
            "domain_bonus": domain_bonus,
            "tag_bonus": tag_bonus,
            "status_bonus": status_bonus,
            "total": total,
            "difficulty": final_difficulty,
            "base_difficulty": difficulty,
            "margin": margin,
            "critical_success": critical_success,
            "critical_failure": critical_failure,
            "breakdown": roll_breakdown,
            "difficulty_breakdown": difficulty_breakdown,
            "domains_used": [d.value for d in domains_used],
            "tags_used": tags_used,
            "difficulty_modifiers": difficulty_modifiers
        }
        
        return result
    
    def roll_check_hybrid(self, 
                         domain_type: DomainType, 
                         tag_name: Optional[str] = None, 
                         difficulty: int = 10,
                         action_data: Optional[Dict[str, Any]] = None,
                         target: Optional[Dict[str, Any]] = None,
                         combat_state: Optional[Dict[str, Any]] = None,
                         force_dice: bool = False,
                         force_threshold: bool = False) -> dict:
        """Perform a hybrid check using the domain-appropriate method
        
        This method automatically chooses between dice rolls and threshold checks
        based on the domain type and situation, following the hybrid design framework:
        - Combat/Physical (Body): Dice-based + stat modifiers
        - Persuasion/Manipulation (Authority, Social): Threshold-based, dice for hard cases
        - Crafting (Craft): Mostly deterministic, dice for bonuses/failures
        - Awareness/Mind: Often passive, stat-gated
        - Spirit: Dice-based, modified by character state
        
        Args:
            domain_type: The primary domain to use
            tag_name: Optional tag to add if character has it
            difficulty: DC of the check (default 10)
            action_data: Optional action data with tags, effects, etc.
            target: Optional target for calculations
            combat_state: Optional combat state for environmental factors
            force_dice: Force a dice roll regardless of domain type
            force_threshold: Force a threshold check regardless of domain type
            
        Returns:
            Result dict with success flag, method used, and details
        """
        
        # Determine the appropriate method based on domain type and context
        use_dice = force_dice
        use_threshold = force_threshold
        method_reason = ""
        
        if not force_dice and not force_threshold:
            if domain_type == DomainType.BODY:
                # Combat/Physical actions - always use dice
                use_dice = True
                method_reason = "Body domain uses dice for combat actions"
                
            elif domain_type in [DomainType.AUTHORITY, DomainType.SOCIAL]:
                # Social actions - threshold for easy cases, dice for hard cases
                domain_value = self.domains[domain_type].value
                
                # Check if target makes this a "hard case"
                is_hard_case = False
                if target:
                    target_level = target.get("level", 1)
                    target_social_resistance = target.get("domains", {}).get(DomainType.SOCIAL, 1)
                    is_hard_case = (target_level > domain_value or 
                                  target_social_resistance > domain_value or
                                  difficulty > (10 + domain_value))
                elif difficulty > (10 + domain_value):
                    is_hard_case = True
                
                if is_hard_case:
                    use_dice = True
                    method_reason = f"{domain_type.value} domain uses dice for hard cases"
                else:
                    use_threshold = True
                    method_reason = f"{domain_type.value} domain uses threshold for routine cases"
                    
            elif domain_type == DomainType.CRAFT:
                # Crafting - mostly deterministic, dice for special cases
                action_type = action_data.get("action_type") if action_data else None
                
                # Use dice for time pressure, experimentation, or combat crafting
                if (action_type in ["combat_craft", "experimental", "rushed"] or
                    (combat_state and combat_state.get("status") == "active")):
                    use_dice = True
                    method_reason = "Craft domain uses dice for special circumstances"
                else:
                    use_threshold = True
                    method_reason = "Craft domain uses threshold for routine crafting"
                    
            elif domain_type in [DomainType.AWARENESS, DomainType.MIND]:
                # Awareness/Mind - often passive, threshold-based
                action_type = action_data.get("action_type") if action_data else None
                
                # Use dice for active perception in combat or contests
                if (action_type in ["active_search", "contest", "combat_awareness"] or
                    (combat_state and combat_state.get("status") == "active")):
                    use_dice = True
                    method_reason = f"{domain_type.value} domain uses dice for active checks"
                else:
                    use_threshold = True
                    method_reason = f"{domain_type.value} domain uses threshold for passive checks"
                    
            elif domain_type == DomainType.SPIRIT:
                # Spirit - usually dice-based for inner struggle/resistance
                use_dice = True
                method_reason = "Spirit domain uses dice for inner struggle and resistance"
                
            else:
                # Default to dice for unknown domains
                use_dice = True
                method_reason = "Unknown domain defaults to dice"
        
        # Perform the appropriate check
        if use_dice:
            # Use the advanced dice rolling method
            result = self.roll_check_advanced(
                domain_type=domain_type,
                tag_name=tag_name,
                difficulty=difficulty,
                action_data=action_data,
                target=target,
                combat_state=combat_state
            )
            result["method"] = "dice"
            result["method_reason"] = method_reason
            
        else:  # use_threshold
            # Use threshold-based check
            domain_value = self.domains[domain_type].value
            tag_bonus = 0
            tags_used = []
            
            # Add tag bonus
            if tag_name and tag_name in self.tags:
                tag_bonus += self.tags[tag_name].rank
                tags_used.append(tag_name)
            
            # Add action tags
            if action_data and action_data.get("tags"):
                for action_tag in action_data["tags"]:
                    if action_tag in self.tags and action_tag not in tags_used:
                        tag_bonus += self.tags[action_tag].rank
                        tags_used.append(action_tag)
            
            total_threshold = domain_value + tag_bonus
            
            # Apply target and environmental modifiers to difficulty
            adjusted_difficulty = difficulty
            modifiers = []
            
            if target:
                level_mod = target.get("level", 0)
                adjusted_difficulty += level_mod
                if level_mod > 0:
                    modifiers.append(f"enemy_level(+{level_mod})")
            
            if action_data and action_data.get("difficulty_modifier"):
                mod = action_data["difficulty_modifier"]
                adjusted_difficulty += mod
                if mod != 0:
                    sign = "+" if mod > 0 else ""
                    modifiers.append(f"action({sign}{mod})")
            
            # Determine success
            success = total_threshold >= adjusted_difficulty
            margin = total_threshold - adjusted_difficulty
            
            # Record domain usage
            action_description = action_data.get("label", "Threshold check") if action_data else "Threshold check"
            self.domains[domain_type].use(action_description, success)
            
            # Award tag XP for successful use
            if success:
                for tag_used in tags_used:
                    if tag_used in self.tags:
                        self.tags[tag_used].gain_xp(8)  # Slightly less XP than dice rolls
            
            # Build result
            breakdown = f"{domain_type.value}({domain_value})"
            if tag_bonus > 0:
                breakdown += f" + tags({tag_bonus})"
            
            difficulty_breakdown = f"DC {difficulty}"
            if modifiers:
                difficulty_breakdown += " + " + " + ".join(modifiers) + f" = {adjusted_difficulty}"
            
            result = {
                "success": success,
                "method": "threshold",
                "method_reason": method_reason,
                "domain_value": domain_value,
                "tag_bonus": tag_bonus,
                "total": total_threshold,
                "difficulty": adjusted_difficulty,
                "base_difficulty": difficulty,
                "margin": margin,
                "breakdown": breakdown,
                "difficulty_breakdown": difficulty_breakdown,
                "domains_used": [domain_type.value],
                "tags_used": tags_used,
                "critical_success": False,  # No crits for threshold checks
                "critical_failure": False,
                "roll": None  # No dice rolled
            }
        
        return result
