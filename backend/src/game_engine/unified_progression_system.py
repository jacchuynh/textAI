"""
Unified Progression System for the game engine.

This module handles the new unified progression system that replaces the old domain system
with a more sophisticated approach that considers player intent, action significance,
and provides both dice-based and probability-based resolution methods.
"""
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random
from datetime import datetime
from dataclasses import dataclass, field
import json
import logging

from shared.models import (
    Character, DomainType, Tag, ResolutionMethod, ActionSignificanceTier,
    Domain, GrowthTier
)
# from ..events.event_bus import event_bus, GameEvent, EventType # For later integration

# --- Constants for Probability Assessment ---
BASE_SUCCESS_CHANCE = 50
DOMAIN_VALUE_MULTIPLIER = 5
TAG_RANK_MULTIPLIER = 8

# --- Constants for Growth Point Tiers ---
GROWTH_POINTS_MAP = {
    ActionSignificanceTier.TRIVIAL: (1, 2),
    ActionSignificanceTier.MINOR: (3, 5),
    ActionSignificanceTier.SIGNIFICANT: (6, 10),
    ActionSignificanceTier.MAJOR: (12, 20),
    ActionSignificanceTier.LEGENDARY: (25, 30)  # Base range, bonuses separate
}
FAILURE_GROWTH_POINT_MULTIPLIER = 0.6

# --- Constants for Insight Points ---
INSIGHT_POINTS_ON_FAILURE_MAP = {
    ActionSignificanceTier.TRIVIAL: (1, 2),
    ActionSignificanceTier.MINOR: (2, 3),
    ActionSignificanceTier.SIGNIFICANT: (3, 4),
    ActionSignificanceTier.MAJOR: (4, 5),
    ActionSignificanceTier.LEGENDARY: (5, 6),
}

# --- Phase 5: Constants for Domain Progression Tiers ---
DOMAIN_PROGRESSION_TIERS = {
    "Novice": {"min_points": 0, "max_points": 7, "advancement_cost": 8},
    "Skilled": {"min_points": 8, "max_points": 12, "advancement_cost": 13},
    "Adept": {"min_points": 13, "max_points": 17, "advancement_cost": 18},
    "Expert": {"min_points": 18, "max_points": 22, "advancement_cost": 23},
    "Master": {"min_points": 23, "max_points": 27, "advancement_cost": 28},
    "Grandmaster": {"min_points": 28, "max_points": 32, "advancement_cost": 33},
    "Legendary": {"min_points": 33, "max_points": 50, "advancement_cost": None}  # No further advancement
}

# --- Phase 5: Insight Point Spending Options ---
INSIGHT_SPENDING_OPTIONS = {
    "reroll_failed_action": {"cost": 3, "description": "Reroll a failed action immediately"},
    "bonus_growth_points": {"cost": 5, "description": "Add +2 growth points to the next action"},
    "temporary_tag_boost": {"cost": 4, "description": "Temporarily increase a tag rank by 1 for one action"},
    "unlock_creative_solution": {"cost": 6, "description": "Access alternative approaches to problem-solving"},
    "accelerated_learning": {"cost": 8, "description": "Double growth points for the next significant action"},
    "mastery_path_progress": {"cost": 10, "description": "Make progress on current mastery path"},
    "domain_cross_training": {"cost": 7, "description": "Apply learning from one domain to another"},
    "wisdom_guidance": {"cost": 5, "description": "Gain insight into optimal approaches for current situation"}
}


# --- Advanced Intent Analysis System ---

class IntentType(Enum):
    GOAL = "goal"  # What player wants to achieve
    APPROACH = "approach"  # How they want to do it
    VALUE = "value"  # What principles guide them
    CONSTRAINT = "constraint"  # What they won't do
    RELATIONSHIP = "relationship"  # Social priorities
    TIMELINE = "timeline"  # When they want results
    EMOTIONAL_STATE = "emotional_state"  # How they feel
    HESITATION = "hesitation"  # Uncertainty
    CONTRADICTION = "contradiction"  # Conflicts with past statements
    SUBCONSCIOUS = "subconscious"  # Implied but not stated

@dataclass
class Intent:
    """Comprehensive player intention model"""
    # Core properties
    category: str  # Main intent category
    subcategory: str  # Specific intent type
    confidence: float  # 0.0-1.0
    text_span: str  # Original text that generated this intent
    
    # Extended properties
    domains_involved: List[str] = field(default_factory=list)  # Which domains this affects
    timeline: str = "immediate"  # "immediate", "short_term", "long_term"
    priority: int = 3  # 1-5 (5 = highest)
    emotional_weight: float = 0.5  # Emotional intensity
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    context_tags: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    world_evaluation: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentConflict:
    """Represents conflicting intentions"""
    intent_a: Intent
    intent_b: Intent
    conflict_type: str  # "direct_opposition", "resource_competition", "value_conflict"
    severity: float  # 0.0-1.0
    resolution_suggestions: List[str]

@dataclass
class IntentAnalysisResult:
    """Complete analysis of player input"""
    primary_intents: List[Intent]
    secondary_intents: List[Intent]
    conflicts: List[IntentConflict]
    overall_confidence: float
    analysis_confidence: float
    paralysis_detected: bool = False
    paralysis_severity: str = "none"  # "none", "mild", "moderate", "severe"
    context_coherence: float = 1.0
    recommended_clarifications: List[str] = field(default_factory=list)
    dominant_intent: Optional[Intent] = None
    arbitration_result: Dict[str, Any] = field(default_factory=dict)

class SimpleIntentAnalyzer:
    """
    Simplified intent analyzer that works without external dependencies.
    Provides sophisticated analysis using pattern matching and heuristics.
    """
    
    def __init__(self):
        self.goal_keywords = {
            "combat": ["master", "learn", "become", "sword", "combat", "fighting", "warrior", "battle", "weapons"],
            "social": ["diplomat", "negotiator", "leader", "influence", "persuade", "charm", "friends"],
            "magic": ["mage", "wizard", "magic", "arcane", "spells", "enchant", "ritual", "power"],
            "craft": ["craft", "create", "build", "make", "forge", "construct", "design"],
            "knowledge": ["learn", "study", "understand", "discover", "research", "investigate"],
            "authority": ["lead", "command", "rule", "govern", "authority", "power", "control"],
            "survival": ["survive", "endure", "live", "escape", "flee", "hide"]
        }
        
        self.approach_keywords = {
            "honorable": ["honor", "honorable", "noble", "righteous", "just", "fair", "moral"],
            "pragmatic": ["practical", "efficient", "whatever", "works", "realistic", "sensible"],
            "sneaky": ["stealth", "sneaky", "shadows", "quiet", "hidden", "subtle", "covert"],
            "aggressive": ["force", "aggressive", "attack", "violent", "brutal", "direct"],
            "creative": ["creative", "innovative", "clever", "unique", "original", "artistic"]
        }
        
        self.value_keywords = {
            "protection": ["protect", "defend", "save", "help", "guard", "shield", "rescue"],
            "power": ["power", "strength", "dominate", "control", "rule", "conquer"],
            "knowledge": ["truth", "wisdom", "understanding", "learning", "enlightenment"],
            "freedom": ["freedom", "liberty", "independence", "choice", "autonomy"],
            "justice": ["justice", "fairness", "equality", "rights", "law"]
        }
        
        self.constraint_keywords = {
            "moral": ["never", "won't", "refuse", "kill", "harm", "innocent", "murder"],
            "independence": ["independent", "alone", "solo", "myself", "own"],
            "peaceful": ["peaceful", "nonviolent", "diplomatic", "negotiation"]
        }
        
        self.emotion_keywords = {
            "confident": ["certain", "sure", "confident", "resolved", "determined"],
            "conflicted": ["torn", "conflicted", "unsure", "confused", "uncertain"],
            "hesitant": ["maybe", "perhaps", "might", "unsure", "confused", "worried"],
            "excited": ["excited", "eager", "enthusiastic", "thrilled", "passionate"],
            "anxious": ["anxious", "worried", "nervous", "concerned", "afraid"]
        }
    
    def analyze_intent(self, text: str, character: Character, action_data: Optional[Dict[str, Any]] = None) -> IntentAnalysisResult:
        """Main analysis method that processes player input"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Extract different types of intents
        goals = self._extract_goals(text_lower, words, character)
        approaches = self._extract_approaches(text_lower, words)
        values = self._extract_values(text_lower, words)
        constraints = self._extract_constraints(text_lower, words)
        emotions = self._extract_emotions(text_lower, words)
        
        # Combine all intents
        all_intents = goals + approaches + values + constraints + emotions
        
        # Detect conflicts
        conflicts = self._detect_conflicts(all_intents)
        
        # Prioritize intents
        primary_intents, secondary_intents = self._prioritize_intents(all_intents)
        
        # Calculate confidence scores
        overall_confidence = self._calculate_overall_confidence(all_intents)
        analysis_confidence = self._calculate_analysis_confidence(text, all_intents)
        
        # Detect paralysis
        paralysis_detected, paralysis_severity = self._detect_paralysis(conflicts, emotions)
        
        # Find dominant intent
        dominant_intent = primary_intents[0] if primary_intents else None
        
        return IntentAnalysisResult(
            primary_intents=primary_intents,
            secondary_intents=secondary_intents,
            conflicts=conflicts,
            overall_confidence=overall_confidence,
            analysis_confidence=analysis_confidence,
            paralysis_detected=paralysis_detected,
            paralysis_severity=paralysis_severity,
            dominant_intent=dominant_intent,
            recommended_clarifications=self._generate_clarifications(conflicts, paralysis_detected)
        )
    
    def _extract_goals(self, text: str, words: List[str], character: Character) -> List[Intent]:
        """Extract goal-related intents"""
        intents = []
        
        for domain, keywords in self.goal_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    confidence = self._calculate_keyword_confidence(keyword, text, words)
                    intent = Intent(
                        category="goal",
                        subcategory=f"{domain}_mastery",
                        confidence=confidence,
                        text_span=self._extract_span(text, keyword),
                        domains_involved=[domain],
                        timeline=self._infer_timeline(text),
                        priority=self._calculate_priority(keyword, text)
                    )
                    intents.append(intent)
        
        # Check alignment with declared goals
        for goal in character.declared_goals:
            if any(word in goal.lower() for word in words):
                intent = Intent(
                    category="goal",
                    subcategory="declared_goal_alignment",
                    confidence=0.9,
                    text_span=goal,
                    timeline="long_term",
                    priority=5
                )
                intents.append(intent)
        
        return intents
    
    def _extract_approaches(self, text: str, words: List[str]) -> List[Intent]:
        """Extract approach-related intents"""
        intents = []
        
        for approach, keywords in self.approach_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    confidence = self._calculate_keyword_confidence(keyword, text, words)
                    intent = Intent(
                        category="approach",
                        subcategory=approach,
                        confidence=confidence,
                        text_span=self._extract_span(text, keyword),
                        domains_involved=self._map_approach_to_domains(approach),
                        priority=4
                    )
                    intents.append(intent)
        
        return intents
    
    def _extract_values(self, text: str, words: List[str]) -> List[Intent]:
        """Extract value-related intents"""
        intents = []
        
        for value, keywords in self.value_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    confidence = self._calculate_keyword_confidence(keyword, text, words)
                    intent = Intent(
                        category="value",
                        subcategory=value,
                        confidence=confidence,
                        text_span=self._extract_span(text, keyword),
                        timeline="long_term",
                        priority=3,
                        emotional_weight=0.7
                    )
                    intents.append(intent)
        
        return intents
    
    def _extract_constraints(self, text: str, words: List[str]) -> List[Intent]:
        """Extract constraint-related intents"""
        intents = []
        
        for constraint, keywords in self.constraint_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    confidence = self._calculate_keyword_confidence(keyword, text, words)
                    intent = Intent(
                        category="constraint",
                        subcategory=constraint,
                        confidence=confidence,
                        text_span=self._extract_span(text, keyword),
                        priority=5,  # Constraints are high priority
                        emotional_weight=0.8
                    )
                    intents.append(intent)
        
        return intents
    
    def _extract_emotions(self, text: str, words: List[str]) -> List[Intent]:
        """Extract emotional state intents"""
        intents = []
        
        for emotion, keywords in self.emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    confidence = self._calculate_keyword_confidence(keyword, text, words)
                    intent = Intent(
                        category="emotional_state",
                        subcategory=emotion,
                        confidence=confidence,
                        text_span=self._extract_span(text, keyword),
                        timeline="immediate",
                        priority=2,
                        emotional_weight=1.0
                    )
                    intents.append(intent)
        
        return intents
    
    def _detect_conflicts(self, intents: List[Intent]) -> List[IntentConflict]:
        """Detect conflicts between intents"""
        conflicts = []
        
        for i, intent_a in enumerate(intents):
            for intent_b in intents[i+1:]:
                conflict = self._check_intent_pair_conflict(intent_a, intent_b)
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_intent_pair_conflict(self, intent_a: Intent, intent_b: Intent) -> Optional[IntentConflict]:
        """Check if two intents conflict"""
        # Direct opposition conflicts
        opposition_pairs = [
            ("honorable", "sneaky"),
            ("peaceful", "aggressive"),
            ("independent", "social"),
            ("power", "protection")
        ]
        
        for pair in opposition_pairs:
            if (intent_a.subcategory in pair and intent_b.subcategory in pair and 
                intent_a.subcategory != intent_b.subcategory):
                return IntentConflict(
                    intent_a=intent_a,
                    intent_b=intent_b,
                    conflict_type="direct_opposition",
                    severity=0.8,
                    resolution_suggestions=[
                        f"Consider finding a balance between {intent_a.subcategory} and {intent_b.subcategory}",
                        f"Choose which value is more important in this situation",
                        f"Look for creative solutions that honor both approaches"
                    ]
                )
        
        # Resource competition conflicts
        if (intent_a.category == "goal" and intent_b.category == "goal" and
            len(set(intent_a.domains_involved) & set(intent_b.domains_involved)) > 0):
            return IntentConflict(
                intent_a=intent_a,
                intent_b=intent_b,
                conflict_type="resource_competition",
                severity=0.6,
                resolution_suggestions=[
                    "Focus on one goal at a time",
                    "Find ways to pursue both goals simultaneously",
                    "Prioritize based on immediate needs"
                ]
            )
        
        return None
    
    def _prioritize_intents(self, intents: List[Intent]) -> Tuple[List[Intent], List[Intent]]:
        """Split intents into primary and secondary based on priority and confidence"""
        # Sort by priority (descending) and confidence (descending)
        sorted_intents = sorted(intents, key=lambda x: (x.priority, x.confidence), reverse=True)
        
        # Primary intents: high priority (4-5) with good confidence (>0.6)
        primary = [i for i in sorted_intents if i.priority >= 4 and i.confidence > 0.6][:3]
        
        # Secondary intents: the rest
        secondary = [i for i in sorted_intents if i not in primary]
        
        return primary, secondary
    
    def _detect_paralysis(self, conflicts: List[IntentConflict], emotions: List[Intent]) -> Tuple[bool, str]:
        """Detect if player is experiencing decision paralysis"""
        # Check for conflicted emotions
        conflicted_emotions = [e for e in emotions if e.subcategory in ["conflicted", "hesitant", "anxious"]]
        
        # High-severity conflicts
        severe_conflicts = [c for c in conflicts if c.severity > 0.7]
        
        if len(severe_conflicts) >= 2 or (len(severe_conflicts) >= 1 and len(conflicted_emotions) >= 1):
            return True, "severe"
        elif len(severe_conflicts) >= 1 or len(conflicted_emotions) >= 2:
            return True, "moderate"
        elif len(conflicted_emotions) >= 1:
            return True, "mild"
        
        return False, "none"
    
    def _calculate_keyword_confidence(self, keyword: str, text: str, words: List[str]) -> float:
        """Calculate confidence based on keyword context and frequency"""
        base_confidence = 0.7
        
        # Boost for exact word match vs partial
        if keyword in words:
            base_confidence += 0.2
        
        # Boost for emphasis words nearby
        emphasis_words = ["really", "very", "extremely", "definitely", "absolutely"]
        for emphasis in emphasis_words:
            if emphasis in text and abs(text.find(keyword) - text.find(emphasis)) < 20:
                base_confidence += 0.1
                break
        
        return min(base_confidence, 1.0)
    
    def _extract_span(self, text: str, keyword: str) -> str:
        """Extract the text span around a keyword"""
        start = max(0, text.find(keyword) - 10)
        end = min(len(text), text.find(keyword) + len(keyword) + 10)
        return text[start:end].strip()
    
    def _infer_timeline(self, text: str) -> str:
        """Infer timeline from text"""
        if any(word in text for word in ["now", "immediately", "urgent", "quickly"]):
            return "immediate"
        elif any(word in text for word in ["eventually", "someday", "future", "long-term"]):
            return "long_term"
        else:
            return "short_term"
    
    def _calculate_priority(self, keyword: str, text: str) -> int:
        """Calculate intent priority based on context"""
        # High priority words
        if any(word in text for word in ["must", "need", "important", "crucial", "essential"]):
            return 5
        elif any(word in text for word in ["want", "would like", "hope", "wish"]):
            return 4
        elif any(word in text for word in ["maybe", "perhaps", "might", "could"]):
            return 2
        else:
            return 3
    
    def _map_approach_to_domains(self, approach: str) -> List[str]:
        """Map approach types to relevant domains"""
        mapping = {
            "honorable": ["authority", "social"],
            "pragmatic": ["mind", "craft"],
            "sneaky": ["awareness", "social"],
            "aggressive": ["body", "authority"],
            "creative": ["mind", "craft", "spirit"]
        }
        return mapping.get(approach, [])
    
    def _calculate_overall_confidence(self, intents: List[Intent]) -> float:
        """Calculate overall confidence in the analysis"""
        if not intents:
            return 0.0
        return sum(i.confidence for i in intents) / len(intents)
    
    def _calculate_analysis_confidence(self, text: str, intents: List[Intent]) -> float:
        """Calculate confidence in the analysis methodology"""
        base_confidence = 0.8
        
        # Reduce confidence for very short text
        if len(text.split()) < 5:
            base_confidence -= 0.2
        
        # Reduce confidence if no clear intents found
        if len(intents) == 0:
            base_confidence -= 0.3
        
        return max(base_confidence, 0.1)
    
    def _generate_clarifications(self, conflicts: List[IntentConflict], paralysis_detected: bool) -> List[str]:
        """Generate clarification questions based on conflicts and paralysis"""
        clarifications = []
        
        if paralysis_detected:
            clarifications.append("You seem to have conflicting feelings about this. Would you like to talk through your options?")
        
        for conflict in conflicts:
            if conflict.conflict_type == "direct_opposition":
                clarifications.append(f"I notice you want both {conflict.intent_a.subcategory} and {conflict.intent_b.subcategory} approaches. Which is more important to you right now?")
            elif conflict.conflict_type == "resource_competition":
                clarifications.append(f"Both goals seem important to you. Which would you like to focus on first?")
        
        return clarifications[:3]  # Limit to 3 clarifications


class UnifiedProgressionSystem:
    """
    Unified system for handling character progression, action resolution,
    and growth point calculation based on player intent and action significance.
    """
    
    # --- Phase 6: Enhanced Mastery Path Generation and Anti-Grinding ---
    
    # Mastery Path Templates
    MASTERY_PATH_TEMPLATES = {
        DomainType.BODY: [
            {"name": "Warrior's Path", "requirements": {"domains": {"body": 15}, "tags": ["combat", "weapons"]}, 
             "benefits": {"combat_damage": 1.2, "physical_endurance": 1.3}},
            {"name": "Acrobatic Master", "requirements": {"domains": {"body": 12, "awareness": 10}, "tags": ["acrobatics", "dodge"]},
             "benefits": {"evasion": 1.4, "movement_speed": 1.3}},
            {"name": "Fortress Guardian", "requirements": {"domains": {"body": 18, "spirit": 12}, "tags": ["defense", "protection"]},
             "benefits": {"damage_resistance": 1.5, "ally_protection": 1.2}}
        ],
        DomainType.MIND: [
            {"name": "Scholar's Wisdom", "requirements": {"domains": {"mind": 15}, "tags": ["research", "knowledge"]},
             "benefits": {"learning_speed": 1.4, "insight_generation": 1.3}},
            {"name": "Tactical Genius", "requirements": {"domains": {"mind": 12, "awareness": 10}, "tags": ["strategy", "tactics"]},
             "benefits": {"party_coordination": 1.3, "battle_planning": 1.4}},
            {"name": "Arcane Theorist", "requirements": {"domains": {"mind": 18, "spirit": 10}, "tags": ["magic", "theory"]},
             "benefits": {"spell_efficiency": 1.3, "magical_understanding": 1.5}}
        ],
        DomainType.SPIRIT: [
            {"name": "Divine Channel", "requirements": {"domains": {"spirit": 15}, "tags": ["faith", "divine"]},
             "benefits": {"divine_power": 1.4, "blessing_strength": 1.3}},
            {"name": "Willpower Master", "requirements": {"domains": {"spirit": 12, "mind": 10}, "tags": ["willpower", "resistance"]},
             "benefits": {"mental_resistance": 1.5, "fear_immunity": True}},
            {"name": "Nature's Bond", "requirements": {"domains": {"spirit": 14, "awareness": 8}, "tags": ["nature", "animals"]},
             "benefits": {"nature_communication": 1.4, "environmental_harmony": 1.3}}
        ],
        DomainType.CRAFT: [
            {"name": "Master Artisan", "requirements": {"domains": {"craft": 15}, "tags": ["crafting", "tools"]},
             "benefits": {"creation_quality": 1.4, "resource_efficiency": 1.3}},
            {"name": "Inventor's Vision", "requirements": {"domains": {"craft": 12, "mind": 10}, "tags": ["invention", "innovation"]},
             "benefits": {"innovation_chance": 1.5, "prototype_success": 1.3}},
            {"name": "Enchanter's Art", "requirements": {"domains": {"craft": 14, "spirit": 10}, "tags": ["enchanting", "magic"]},
             "benefits": {"enchantment_power": 1.4, "magical_crafting": 1.5}}
        ],
        DomainType.SOCIAL: [
            {"name": "Diplomat's Grace", "requirements": {"domains": {"social": 15}, "tags": ["diplomacy", "negotiation"]},
             "benefits": {"persuasion_power": 1.4, "conflict_resolution": 1.3}},
            {"name": "Inspiring Leader", "requirements": {"domains": {"social": 12, "authority": 10}, "tags": ["leadership", "inspiration"]},
             "benefits": {"ally_morale": 1.5, "group_coordination": 1.3}},
            {"name": "Shadow Manipulator", "requirements": {"domains": {"social": 14, "awareness": 8}, "tags": ["deception", "intrigue"]},
             "benefits": {"information_gathering": 1.4, "social_stealth": 1.5}}
        ],
        DomainType.AUTHORITY: [
            {"name": "Natural Commander", "requirements": {"domains": {"authority": 15}, "tags": ["command", "leadership"]},
             "benefits": {"command_range": 1.4, "order_effectiveness": 1.3}},
            {"name": "Judge's Wisdom", "requirements": {"domains": {"authority": 12, "mind": 10}, "tags": ["justice", "judgment"]},
             "benefits": {"truth_detection": 1.3, "fair_judgment": 1.4}},
            {"name": "Royal Presence", "requirements": {"domains": {"authority": 18, "social": 10}, "tags": ["nobility", "presence"]},
             "benefits": {"intimidation": 1.5, "social_influence": 1.4}}
        ],
        DomainType.AWARENESS: [
            {"name": "Master Scout", "requirements": {"domains": {"awareness": 15}, "tags": ["scouting", "tracking"]},
             "benefits": {"detection_range": 1.5, "tracking_accuracy": 1.4}},
            {"name": "Danger Sense", "requirements": {"domains": {"awareness": 12, "spirit": 8}, "tags": ["intuition", "danger"]},
             "benefits": {"threat_detection": 1.6, "surprise_immunity": True}},
            {"name": "Information Broker", "requirements": {"domains": {"awareness": 14, "social": 10}, "tags": ["information", "networks"]},
             "benefits": {"information_access": 1.4, "network_influence": 1.3}}
        ]
    }
    
    # Anti-grinding tracking
    ACTION_GRINDING_TRACKER = {}  # Will track repeated actions per character
    GRINDING_PENALTIES = {
        "repeated_threshold": 3,  # After 3 same actions in short time
        "growth_penalty": 0.5,   # 50% reduced growth
        "insight_penalty": 0.3,  # 30% reduced insight
        "time_window": 300       # 5 minutes in seconds
    }
    
    def __init__(self):
        """Initialize the unified progression system."""
        # Initialize the sophisticated intent analyzer
        self.intent_analyzer = SimpleIntentAnalyzer()
        
        # Initialize player profile tracking
        self.player_profiles = {}  # character_id -> profile data
        
        # Initialize any necessary state or configurations
        pass

    def _analyze_player_intent(self, character: Character, action_data: Optional[Dict[str, Any]], 
                             player_input: str = None, player_approach_description: str = None) -> Dict[str, Any]:
        """
        Advanced player intent analysis using the sophisticated intent analysis system.
        
        Args:
            character: The character performing the action
            action_data: Data about the action being performed
            player_input: Raw player input text
            player_approach_description: Player's description of their approach
        
        Returns:
            Enhanced intent analysis with sophisticated understanding
        """
        # Combine available text for analysis
        analysis_text = ""
        if player_input:
            analysis_text += player_input + " "
        if player_approach_description:
            analysis_text += player_approach_description + " "
        if action_data and action_data.get("description"):
            analysis_text += action_data["description"] + " "
        
        # If no text available, fall back to simple analysis
        if not analysis_text.strip():
            return self._simple_intent_analysis(character, action_data)
        
        # Use sophisticated intent analyzer
        intent_result = self.intent_analyzer.analyze_intent(analysis_text.strip(), character, action_data)
        
        # Convert to the format expected by the progression system
        analysis = {
            "goals_aligned": [],
            "approach_novelty": 0,
            "value_consistent": False,
            "emotional_state": "neutral",
            "confidence_level": intent_result.overall_confidence,
            "paralysis_detected": intent_result.paralysis_detected,
            "conflicts_detected": len(intent_result.conflicts) > 0,
            "dominant_intent": intent_result.dominant_intent,
            "primary_intents": intent_result.primary_intents,
            "recommended_clarifications": intent_result.recommended_clarifications,
            
            # Enhanced analysis data
            "intent_analysis_result": intent_result,
            "approach_consistency": self._calculate_approach_consistency(character, intent_result),
            "goal_alignment_strength": self._calculate_goal_alignment_strength(character, intent_result),
            "creative_approach_detected": self._detect_creative_approach(intent_result),
            "value_alignment_score": self._calculate_value_alignment(character, intent_result)
        }
        
        # Extract goal alignments
        for intent in intent_result.primary_intents:
            if intent.category == "goal":
                # Check against declared goals
                for goal in character.declared_goals:
                    if any(keyword in goal.lower() for keyword in intent.domains_involved):
                        analysis["goals_aligned"].append(goal)
                
                # Check for goal subcategory matches
                if intent.subcategory == "declared_goal_alignment":
                    analysis["goals_aligned"].append(intent.text_span)
        
        # Assess approach novelty
        creative_intents = [i for i in intent_result.primary_intents if i.subcategory == "creative"]
        if creative_intents:
            analysis["approach_novelty"] = max(i.confidence for i in creative_intents)
        
        # Check value consistency
        value_intents = [i for i in intent_result.primary_intents if i.category == "value"]
        if value_intents:
            # Check against demonstrated values
            for intent in value_intents:
                if intent.subcategory in character.demonstrated_values:
                    analysis["value_consistent"] = True
                    break
        
        # Extract emotional state
        emotion_intents = [i for i in intent_result.primary_intents if i.category == "emotional_state"]
        if emotion_intents:
            # Use the highest confidence emotion
            dominant_emotion = max(emotion_intents, key=lambda x: x.confidence)
            analysis["emotional_state"] = dominant_emotion.subcategory
        
        # Update player profile tracking
        self._update_player_profile(character, intent_result, analysis)
        
        return analysis
    
    def _simple_intent_analysis(self, character: Character, action_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Fallback simple intent analysis when no text is available"""
        analysis = {
            "goals_aligned": [],
            "approach_novelty": 0,
            "value_consistent": False,
            "emotional_state": "neutral",
            "confidence_level": 0.5,
            "paralysis_detected": False,
            "conflicts_detected": False,
            "dominant_intent": None,
            "primary_intents": [],
            "recommended_clarifications": []
        }
        
        if action_data and action_data.get("aligns_with_goal"):
            if action_data["aligns_with_goal"] in character.declared_goals:
                analysis["goals_aligned"].append(action_data["aligns_with_goal"])

        # Example: Check if action description suggests novelty
        if action_data and "creative" in action_data.get("description", "").lower():
            analysis["approach_novelty"] = 1

        return analysis
    
    def _calculate_approach_consistency(self, character: Character, intent_result: IntentAnalysisResult) -> float:
        """Calculate how consistent this approach is with the character's past choices"""
        # Get approach preferences from character
        preferences = character.learning_approach_preferences
        
        approach_intents = [i for i in intent_result.primary_intents if i.category == "approach"]
        if not approach_intents or not preferences:
            return 0.5  # Neutral if no data
        
        matches = 0
        for intent in approach_intents:
            if intent.subcategory in preferences:
                matches += 1
        
        return matches / len(approach_intents) if approach_intents else 0.5
    
    def _calculate_goal_alignment_strength(self, character: Character, intent_result: IntentAnalysisResult) -> float:
        """Calculate how strongly this action aligns with character goals"""
        goal_intents = [i for i in intent_result.primary_intents if i.category == "goal"]
        declared_goals = character.declared_goals
        
        if not goal_intents or not declared_goals:
            return 0.0
        
        alignment_scores = []
        for intent in goal_intents:
            max_score = 0
            for goal in declared_goals:
                # Simple keyword matching - could be enhanced
                goal_words = set(goal.lower().split())
                intent_words = set(intent.text_span.lower().split())
                overlap = len(goal_words & intent_words) / len(goal_words) if goal_words else 0
                max_score = max(max_score, overlap * intent.confidence)
            alignment_scores.append(max_score)
        
        return sum(alignment_scores) / len(alignment_scores)
    
    def _detect_creative_approach(self, intent_result: IntentAnalysisResult) -> bool:
        """Detect if the player is using a creative approach"""
        creative_indicators = ["creative", "innovative", "unique", "original", "clever"]
        
        for intent in intent_result.primary_intents:
            if intent.subcategory in creative_indicators:
                return True
            if any(indicator in intent.text_span.lower() for indicator in creative_indicators):
                return True
        
        return False
    
    def _calculate_value_alignment(self, character: Character, intent_result: IntentAnalysisResult) -> float:
        """Calculate how well this action aligns with character values"""
        value_intents = [i for i in intent_result.primary_intents if i.category == "value"]
        demonstrated_values = character.demonstrated_values
        
        if not value_intents:
            return 0.5  # Neutral if no value intents detected
        
        alignment_score = 0.0
        for intent in value_intents:
            if intent.subcategory in demonstrated_values:
                # Weight by both intent confidence and demonstrated value strength
                value_strength = demonstrated_values[intent.subcategory] / 10.0  # Normalize to 0-1
                alignment_score += intent.confidence * value_strength
        
        return min(alignment_score / len(value_intents), 1.0) if value_intents else 0.5
    
    def _update_player_profile(self, character: Character, intent_result: IntentAnalysisResult, analysis: Dict[str, Any]):
        """Update the player profile based on intent analysis"""
        profile_key = character.name  # Using name as key for simplicity
        
        if profile_key not in self.player_profiles:
            self.player_profiles[profile_key] = {
                "intent_history": [],
                "approach_patterns": {},
                "value_patterns": {},
                "goal_patterns": {},
                "consistency_score": 0.5,
                "analysis_count": 0
            }
        
        profile = self.player_profiles[profile_key]
        profile["analysis_count"] += 1
        
        # Store recent intent analysis
        profile["intent_history"].append({
            "timestamp": datetime.now().timestamp(),
            "intent_result": intent_result,
            "analysis": analysis
        })
        
        # Keep only recent history (last 20 analyses)
        if len(profile["intent_history"]) > 20:
            profile["intent_history"] = profile["intent_history"][-20:]
        
        # Update pattern tracking
        for intent in intent_result.primary_intents:
            if intent.category == "approach":
                profile["approach_patterns"][intent.subcategory] = profile["approach_patterns"].get(intent.subcategory, 0) + 1
            elif intent.category == "value":
                profile["value_patterns"][intent.subcategory] = profile["value_patterns"].get(intent.subcategory, 0) + 1
            elif intent.category == "goal":
                profile["goal_patterns"][intent.subcategory] = profile["goal_patterns"].get(intent.subcategory, 0) + 1

    def _determine_resolution_method(self, 
                    character: Character, 
                    domain_type: DomainType,
                    action_data: Optional[Dict[str, Any]] = None,
                    target: Optional[Dict[str, Any]] = None,
                    combat_state: Optional[Dict[str, Any]] = None,
                    force_dice: bool = False,
                    force_probability: bool = False) -> Tuple[ResolutionMethod, str]:
        """
        Determines whether to use dice or probability assessment.
        This will adapt logic from your Character.roll_check_hybrid and the new framework.
        """
        if force_dice:
            return ResolutionMethod.DICE, "Dice roll forced by caller."
        if force_probability:
            return ResolutionMethod.PROBABILITY, "Probability assessment forced by caller."

        action_type = action_data.get("action_type") if action_data else "general"

        # Rule mapping based on the framework:
        if domain_type == DomainType.BODY or action_type in ["combat_attack", "physical_challenge", "environmental_hazard"]:
            return ResolutionMethod.DICE, f"{domain_type.value} or {action_type} typically uses dice."

        if domain_type in [DomainType.AUTHORITY, DomainType.SOCIAL]:
            # Simplified: use probability unless it's a "contested action" or high stakes
            if action_type == "contested_social" or (action_data and action_data.get("high_stakes")):
                return ResolutionMethod.DICE, f"Contested/high-stakes {domain_type.value} uses dice."
            return ResolutionMethod.PROBABILITY, f"{domain_type.value} typically uses probability."

        if domain_type == DomainType.CRAFT:
            if action_type in ["combat_craft", "experimental_craft", "rushed_craft"] or (combat_state and combat_state.get("active")):
                return ResolutionMethod.DICE, f"Special circumstance {domain_type.value} uses dice."
            return ResolutionMethod.PROBABILITY, f"Routine {domain_type.value} uses probability."

        if domain_type in [DomainType.AWARENESS, DomainType.MIND]:
            if action_type in ["active_search_combat", "mental_contest"] or (combat_state and combat_state.get("active")):
                return ResolutionMethod.DICE, f"Active/contested {domain_type.value} uses dice."
            return ResolutionMethod.PROBABILITY, f"Passive/routine {domain_type.value} uses probability."

        if domain_type == DomainType.SPIRIT:
            return ResolutionMethod.DICE, f"{domain_type.value} typically uses dice for resistance/willpower."

        # Default or fallback
        if action_data and action_data.get("is_external_challenge", False):
            return ResolutionMethod.DICE, "Defaulting to dice for external challenge."
        return ResolutionMethod.PROBABILITY, "Defaulting to probability for internal/creative action."

    def _resolve_dice_check(self, 
                character: Character, 
                domain_type: DomainType, 
                tag_name: Optional[str] = None, 
                difficulty: int = 10,
                action_data: Optional[Dict[str, Any]] = None,
                target: Optional[Dict[str, Any]] = None,
                combat_state: Optional[Dict[str, Any]] = None,
                multiple_domains: Optional[List[DomainType]] = None,
                multiple_tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Performs a dice roll. Adapts logic from Character.roll_check_advanced.
        """
        if domain_type not in character.domains:
            raise ValueError(f"Domain {domain_type} not found for character {character.name}")

        domain_obj = character.domains[domain_type]
        d20_roll = random.randint(1, 20)
        domain_bonus = domain_obj.value
        total = d20_roll + domain_bonus
        roll_breakdown_parts = [f"d20({d20_roll})", f"{domain_type.value}({domain_bonus})"]
        tags_used_for_roll = []
        tag_bonus = 0

        # Primary tag
        if tag_name and tag_name in character.tags:
            primary_tag_obj = character.tags[tag_name]
            tag_bonus += primary_tag_obj.rank
            roll_breakdown_parts.append(f"{tag_name}({primary_tag_obj.rank})")
            tags_used_for_roll.append(tag_name)

        # Multiple tags
        if multiple_tags:
            for mt_name in multiple_tags:
                if mt_name in character.tags and mt_name not in tags_used_for_roll:
                    mt_obj = character.tags[mt_name]
                    tag_bonus += mt_obj.rank
                    roll_breakdown_parts.append(f"{mt_name}({mt_obj.rank})")
                    tags_used_for_roll.append(mt_name)
        
        total += tag_bonus

        # Calculate final difficulty
        final_difficulty = difficulty
        if action_data and action_data.get("difficulty_modifier"):
            final_difficulty += action_data["difficulty_modifier"]

        success = total >= final_difficulty
        margin = total - final_difficulty
        crit_success = d20_roll == 20
        crit_failure = d20_roll == 1

        # Natural 20s and 1s
        if crit_success and not success:
            success = True  # Nat 20 often succeeds
        if crit_failure and success:
            success = False  # Nat 1 often fails

        return {
            "success": success,
            "roll": d20_roll,
            "total": total,
            "final_difficulty": final_difficulty,
            "margin": margin,
            "critical_success": crit_success,
            "critical_failure": crit_failure,
            "breakdown": " + ".join(roll_breakdown_parts) + f" vs DC {final_difficulty}",
            "domains_used": [domain_type] + (multiple_domains or []),
            "tags_used": tags_used_for_roll,
            "method": ResolutionMethod.DICE.value
        }

    def _assess_probability_outcome(self, 
                    character: Character, 
                    domain_type: DomainType,
                    tag_name: Optional[str] = None,
                    action_data: Optional[Dict[str, Any]] = None,
                    target: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Assesses outcome based on probability.
        Success Chance = Base(50%) + Domain Value(×5) + Tag Rank(×8) + Modifiers
        """
        if domain_type not in character.domains:
            raise ValueError(f"Domain {domain_type} not found for character {character.name}")

        domain_obj = character.domains[domain_type]
        success_chance = BASE_SUCCESS_CHANCE
        success_chance += domain_obj.value * DOMAIN_VALUE_MULTIPLIER

        tag_bonus_calc = 0
        tags_used_for_calc = []
        if tag_name and tag_name in character.tags:
            primary_tag_obj = character.tags[tag_name]
            tag_bonus_calc += primary_tag_obj.rank * TAG_RANK_MULTIPLIER
            tags_used_for_calc.append(tag_name)

        success_chance += tag_bonus_calc

        # Modifiers (placeholders, expand based on action_data, target, intent)
        modifiers_applied = []
        if action_data:
            prep_quality = action_data.get("preparation_quality_modifier", 0)  # -20 to 30
            success_chance += prep_quality
            if prep_quality != 0:
                modifiers_applied.append(f"Prep({prep_quality}%)")

            approach_eff = action_data.get("approach_effectiveness_modifier", 0)  # -30 to 25
            success_chance += approach_eff
            if approach_eff != 0:
                modifiers_applied.append(f"Approach({approach_eff}%)")

        if target:
            npc_disposition = target.get("disposition_modifier", 0)  # -40 to 20
            success_chance += npc_disposition
            if npc_disposition != 0:
                modifiers_applied.append(f"NPC Disposition({npc_disposition}%)")

            relationship_mod = target.get("relationship_modifier", 0)  # -25 to 25
            success_chance += relationship_mod
            if relationship_mod != 0:
                modifiers_applied.append(f"Relationship({relationship_mod}%)")

        success_chance = max(0, min(100, success_chance))  # Clamp to 0-100%

        # Determine outcome based on probability ranges
        roll_percentile = random.randint(1, 100)
        success = False
        outcome_description = ""

        if success_chance >= 90:
            success = True
            outcome_description = "Automatic Success (Excellent Alignment/Prep)"
        elif success_chance <= 14:
            success = False
            outcome_description = "Automatic Failure (Overwhelming Obstacles/Poor Prep)"
        else:
            if roll_percentile <= success_chance:
                success = True
                outcome_description = f"Success (Rolled {roll_percentile} <= {success_chance}%)"
            else:
                success = False
                outcome_description = f"Failure (Rolled {roll_percentile} > {success_chance}%)"

        # Determine likelihood category
        if success_chance >= 70 and success_chance < 90:
            likelihood = "Very Likely"
        elif success_chance >= 40 and success_chance < 70:
            likelihood = "Uncertain"
        elif success_chance > 14 and success_chance < 40:
            likelihood = "Risky"
        elif success_chance >= 90:
            likelihood = "Almost Certain Success"
        else:
            likelihood = "Almost Certain Failure"

        return {
            "success": success,
            "success_chance": success_chance,
            "roll_percentile": roll_percentile if 14 < success_chance < 90 else None,
            "outcome_description": outcome_description,
            "likelihood_category": likelihood,
            "breakdown": f"Base(50) + Domain({domain_obj.value*DOMAIN_VALUE_MULTIPLIER}) + Tag({tag_bonus_calc}) + Modifiers({' '.join(modifiers_applied)}) = {success_chance}%",
            "domains_used": [domain_type],
            "tags_used": tags_used_for_calc,
            "method": ResolutionMethod.PROBABILITY.value
        }

    def _determine_action_significance(self,
                      character: Character,
                      outcome_result: Dict[str, Any],
                      intent_analysis: Dict[str, Any],
                      action_data: Optional[Dict[str, Any]] = None
                      ) -> Tuple[ActionSignificanceTier, float, List[str]]:
        """
        Determines the significance tier of an action and any multipliers.
        Returns: (tier, risk_multiplier, reasons_for_significance)
        """
        base_tier = ActionSignificanceTier.MINOR  # Default
        reasons = []

        # Player Intent Alignment
        if intent_analysis.get("goals_aligned"):
            base_tier = ActionSignificanceTier.SIGNIFICANT
            reasons.append(f"Aligned with goal(s): {', '.join(intent_analysis['goals_aligned'])}")

        # Narrative Impact (from action_data)
        narrative_impact_level = action_data.get("narrative_impact", 0) if action_data else 0  # 0=none, 1=minor, 2=major, 3=pivot
        if narrative_impact_level >= 3:  # Major pivot
            base_tier = ActionSignificanceTier.MAJOR
            reasons.append("Major narrative pivot.")
        elif narrative_impact_level == 2 and base_tier == ActionSignificanceTier.MINOR:  # Story advancing
            base_tier = ActionSignificanceTier.SIGNIFICANT
            reasons.append("Story-advancing action.")

        # Creative Approach
        if intent_analysis.get("approach_novelty", 0) > 0:
            reasons.append("Creative approach noted.")

        # Risk Level (from action_data or inferred)
        risk_level_input = action_data.get("risk_level", "medium") if action_data else "medium"  # low, medium, high, extreme
        risk_multiplier = 1.0
        if risk_level_input == "low":
            risk_multiplier = 0.75
        elif risk_level_input == "high":
            risk_multiplier = 1.25
        elif risk_level_input == "extreme":
            risk_multiplier = 1.5
        if risk_multiplier != 1.0:
            reasons.append(f"Risk level: {risk_level_input} (x{risk_multiplier})")

        # Explicit tier from action_data can override
        if action_data and action_data.get("explicit_significance_tier"):
            try:
                base_tier = ActionSignificanceTier(action_data["explicit_significance_tier"])
                reasons.append(f"Explicitly set to {base_tier.value}.")
            except ValueError:
                pass  # Invalid tier ignored

        return base_tier, risk_multiplier, reasons

    def _calculate_growth_and_insight(self,
                     character: Character,
                     outcome_result: Dict[str, Any],
                     intent_analysis: Dict[str, Any],
                     action_data: Optional[Dict[str, Any]] = None
                     ) -> Dict[str, Any]:
        """
        Calculates growth points for domains/tags and insight points.
        """
        significance_tier, risk_multiplier, sig_reasons = self._determine_action_significance(
            character, outcome_result, intent_analysis, action_data
        )

        # Check for anti-grinding penalties
        grinding_penalty = self._check_grinding_penalty(character, action_data or {})
        
        base_gp_min, base_gp_max = GROWTH_POINTS_MAP.get(significance_tier, (1, 2))
        base_gp = random.randint(base_gp_min, base_gp_max)

        final_gp = 0
        insight_points_gained = 0
        xp_for_tags = 0

        # Bonuses
        creative_bonus_gp = 0
        if intent_analysis.get("approach_novelty", 0) > 0:
            creative_bonus_gp = random.randint(3, 5)  # Creative approach bonus

        if outcome_result["success"]:
            final_gp = int(base_gp * risk_multiplier * grinding_penalty) + creative_bonus_gp
            xp_for_tags = final_gp  # Or a fraction, e.g., 5-15 based on significance/success
            if outcome_result.get("critical_success"):
                xp_for_tags = int(xp_for_tags * 1.5)
        else:  # Failure
            final_gp = int(base_gp * risk_multiplier * FAILURE_GROWTH_POINT_MULTIPLIER * grinding_penalty) + creative_bonus_gp

            # Insight Points
            ip_min, ip_max = INSIGHT_POINTS_ON_FAILURE_MAP.get(significance_tier, (1, 1))
            insight_points_gained = random.randint(ip_min, ip_max)
            if intent_analysis.get("approach_novelty", 0) > 0:
                insight_points_gained += 2  # Creative attempt bonus IP
            if risk_multiplier > 1.0:  # Higher risk
                insight_points_gained += random.randint(1, 3)

        return {
            "growth_points_awarded": final_gp,
            "insight_points_gained": insight_points_gained,
            "xp_for_tags_awarded": xp_for_tags,
            "significance_tier_determined": significance_tier.value,
            "significance_reasons": sig_reasons,
            "risk_multiplier_applied": risk_multiplier,
            "creative_bonus_gp": creative_bonus_gp,
            "grinding_penalty_applied": grinding_penalty,
        }

    def _apply_progression_changes(self, 
                    character: Character, 
                    outcome_result: Dict[str, Any], 
                    growth_result: Dict[str, Any]):
        """
        Applies calculated growth points, XP, and insight points to the character.
        Handles domain level-ups and tag rank-ups.
        """
        # Apply Insight Points
        character.insight_points += growth_result.get("insight_points_gained", 0)

        # Apply Growth Points to Domains
        domains_affected = outcome_result.get("domains_used", [])
        gp_awarded = growth_result.get("growth_points_awarded", 0)

        if gp_awarded > 0 and domains_affected:
            # Distribute GP to primary domain for now
            primary_domain_type = domains_affected[0]
            domain_obj = character.domains[primary_domain_type]

            # Log usage
            domain_obj.usage_count += 1
            
            # Apply growth points to the existing growth_points system
            # This maintains compatibility with the existing system while transitioning
            domain_obj.growth_points += gp_awarded
            
            # Check for level up using existing logic
            if domain_obj.growth_points >= domain_obj.growth_required:
                domain_obj.value += 1
                domain_obj.growth_points -= domain_obj.growth_required
                # Increase requirements for next level
                domain_obj.growth_required = int(domain_obj.growth_required * 1.2)
                print(f"Domain {primary_domain_type.value} increased to {domain_obj.value}!")

        # Apply XP to Tags
        xp_to_tags = growth_result.get("xp_for_tags_awarded", 0)
        if xp_to_tags > 0:
            for tag_name in outcome_result.get("tags_used", []):
                if tag_name in character.tags:
                    if character.tags[tag_name].gain_xp(xp_to_tags):
                        print(f"Tag {tag_name} ranked up to {character.tags[tag_name].rank}!")

        # Update character's last updated time
        character.updated_at = datetime.now()

    def _check_and_offer_mastery_paths(self, character: Character, domain_type: DomainType):
        """Checks if a character is eligible for new mastery paths and generates them."""
        # Get enhanced mastery paths
        available_paths = self._generate_enhanced_mastery_paths(character, domain_type)
        
        for path_info in available_paths:
            if path_info["can_unlock"] and path_info["status"] == "available":
                # Auto-offer new paths that meet requirements
                print(f"New mastery path available: {path_info['name']} for {domain_type.value}")
                print(f"Description: {path_info.get('description', 'No description available')}")

    # --- Phase 5: Insight Point Spending Methods ---
    
    def get_available_insight_options(self, character: Character, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Get available insight point spending options based on character's current state and context.
        """
        available_options = []
        
        for option_key, option_data in INSIGHT_SPENDING_OPTIONS.items():
            if character.insight_points >= option_data["cost"]:
                option_info = {
                    "key": option_key,
                    "cost": option_data["cost"],
                    "description": option_data["description"],
                    "available": True
                }
                
                # Add contextual information
                if context:
                    if option_key == "reroll_failed_action" and not context.get("last_action_failed"):
                        option_info["available"] = False
                        option_info["reason"] = "No failed action to reroll"
                    elif option_key == "mastery_path_progress" and not character.mastery_paths:
                        option_info["available"] = False
                        option_info["reason"] = "No active mastery paths"
                
                available_options.append(option_info)
        
        return available_options
    
    def spend_insight_points(self, character: Character, option_key: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Spend insight points on the specified option.
        """
        if option_key not in INSIGHT_SPENDING_OPTIONS:
            return {"success": False, "message": f"Unknown insight option: {option_key}"}
        
        option_data = INSIGHT_SPENDING_OPTIONS[option_key]
        cost = option_data["cost"]
        
        if character.insight_points < cost:
            return {"success": False, "message": f"Insufficient insight points. Need {cost}, have {character.insight_points}"}
        
        # Apply the insight effect
        effect_result = self._apply_insight_effect(character, option_key, context)
        
        if effect_result["success"]:
            character.insight_points -= cost
            character.updated_at = datetime.now()
            
            return {
                "success": True,
                "message": f"Successfully spent {cost} insight points on {option_data['description']}",
                "effect": effect_result,
                "remaining_points": character.insight_points
            }
        else:
            return {"success": False, "message": effect_result.get("message", "Failed to apply insight effect")}
    
    def _apply_insight_effect(self, character: Character, option_key: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Apply the specific insight point effect.
        """
        context = context or {}
        
        if option_key == "reroll_failed_action":
            # This would typically be handled by the calling system
            return {"success": True, "type": "reroll", "message": "Reroll granted"}
        
        elif option_key == "bonus_growth_points":
            # Set a temporary bonus flag
            if not hasattr(character, '_temp_bonuses'):
                character._temp_bonuses = {}
            character._temp_bonuses["next_action_growth_bonus"] = 2
            return {"success": True, "type": "growth_bonus", "bonus": 2}
        
        elif option_key == "temporary_tag_boost":
            tag_name = context.get("target_tag")
            if not tag_name or tag_name not in character.tags:
                return {"success": False, "message": "Invalid or missing target tag"}
            
            if not hasattr(character, '_temp_bonuses'):
                character._temp_bonuses = {}
            character._temp_bonuses[f"tag_boost_{tag_name}"] = 1
            return {"success": True, "type": "tag_boost", "tag": tag_name, "boost": 1}
        
        elif option_key == "unlock_creative_solution":
            return {"success": True, "type": "creative_solution", "message": "Creative approaches unlocked"}
        
        elif option_key == "accelerated_learning":
            if not hasattr(character, '_temp_bonuses'):
                character._temp_bonuses = {}
            character._temp_bonuses["next_significant_action_double_growth"] = True
            return {"success": True, "type": "accelerated_learning"}
        
        elif option_key == "mastery_path_progress":
            active_paths = [path for path in character.mastery_paths if path.get("active", False)]
            if not active_paths:
                return {"success": False, "message": "No active mastery paths"}
            
            # Progress the first active path
            target_path = active_paths[0]
            current_progress = target_path.get("progress", 0)
            target_path["progress"] = current_progress + 1
            
            return {"success": True, "type": "mastery_progress", "path": target_path["path_name"], "new_progress": target_path["progress"]}
        
        elif option_key == "domain_cross_training":
            source_domain = context.get("source_domain")
            target_domain = context.get("target_domain")
            if not source_domain or not target_domain:
                return {"success": False, "message": "Source and target domains required"}
            
            # Apply cross-training bonus
            if not hasattr(character, '_temp_bonuses'):
                character._temp_bonuses = {}
            character._temp_bonuses[f"cross_training_{target_domain}"] = 0.5  # 50% bonus from source domain
            
            return {"success": True, "type": "cross_training", "source": source_domain, "target": target_domain}
        
        elif option_key == "wisdom_guidance":
            return {"success": True, "type": "wisdom_guidance", "message": "Wisdom guidance provided"}
        
        return {"success": False, "message": "Unknown insight option"}
    
    def get_domain_progression_tier(self, domain_value: int) -> str:
        """
        Determine the current progression tier based on domain value.
        """
        for tier_name, tier_data in DOMAIN_PROGRESSION_TIERS.items():
            if tier_data["min_points"] <= domain_value <= tier_data["max_points"]:
                return tier_name
        return "Legendary"  # Fallback for very high values
    
    def get_advancement_cost(self, current_tier: str) -> Optional[int]:
        """
        Get the cost to advance from the current tier to the next.
        """
        return DOMAIN_PROGRESSION_TIERS.get(current_tier, {}).get("advancement_cost")
    
    def can_advance_domain(self, character: Character, domain_type: DomainType) -> Dict[str, Any]:
        """
        Check if a domain can be advanced and return advancement information.
        """
        domain = character.domains.get(domain_type)
        if not domain:
            return {"can_advance": False, "message": "Domain not found"}
        
        current_tier = self.get_domain_progression_tier(domain.value)
        advancement_cost = self.get_advancement_cost(current_tier)
        
        if advancement_cost is None:
            return {"can_advance": False, "message": "Already at maximum tier"}
        
        accumulated_points = domain.growth_points
        
        return {
            "can_advance": accumulated_points >= advancement_cost,
            "current_tier": current_tier,
            "current_points": accumulated_points,
            "advancement_cost": advancement_cost,
            "points_needed": max(0, advancement_cost - accumulated_points)
        }

    # --- Phase 6: Enhanced Mastery Path Generation and Anti-Grinding Methods ---
    
    def _generate_enhanced_mastery_paths(self, character: Character, domain_type: DomainType) -> List[Dict[str, Any]]:
        """
        Generate available mastery paths based on character's current state.
        """
        available_paths = []
        templates = self.MASTERY_PATH_TEMPLATES.get(domain_type, [])
        
        for template in templates:
            path_info = template.copy()
            can_unlock = self._check_mastery_requirements(character, template["requirements"])
            
            path_info["can_unlock"] = can_unlock["eligible"]
            path_info["missing_requirements"] = can_unlock.get("missing", [])
            path_info["domain"] = domain_type.value
            
            # Check if already unlocked
            existing_path = next((p for p in character.mastery_paths 
                                if p.get("path_name") == template["name"]), None)
            if existing_path:
                path_info["status"] = "unlocked"
                path_info["progress"] = existing_path.get("progress", 0)
                path_info["active"] = existing_path.get("active", False)
            else:
                path_info["status"] = "available" if can_unlock["eligible"] else "locked"
                path_info["progress"] = 0
                path_info["active"] = False
            
            available_paths.append(path_info)
        
        return available_paths
    
    def _check_mastery_requirements(self, character: Character, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check if character meets mastery path requirements.
        """
        missing = []
        
        # Check domain requirements
        if "domains" in requirements:
            for domain_name, required_value in requirements["domains"].items():
                try:
                    domain_type = DomainType(domain_name)
                    domain = character.domains.get(domain_type)
                    if not domain or domain.value < required_value:
                        missing.append(f"{domain_name.title()} domain level {required_value} (current: {domain.value if domain else 0})")
                except ValueError:
                    missing.append(f"Unknown domain: {domain_name}")
        
        # Check tag requirements
        if "tags" in requirements:
            for required_tag in requirements["tags"]:
                if required_tag not in character.tags:
                    missing.append(f"Tag: {required_tag}")
                # Could also check tag rank if needed
        
        return {
            "eligible": len(missing) == 0,
            "missing": missing
        }
    
    def unlock_mastery_path(self, character: Character, path_name: str, domain_type: DomainType) -> Dict[str, Any]:
        """
        Unlock a mastery path for the character.
        """
        templates = self.MASTERY_PATH_TEMPLATES.get(domain_type, [])
        template = next((t for t in templates if t["name"] == path_name), None)
        
        if not template:
            return {"success": False, "message": f"Mastery path '{path_name}' not found"}
        
        # Check if already unlocked
        existing = next((p for p in character.mastery_paths 
                        if p.get("path_name") == path_name), None)
        if existing:
            return {"success": False, "message": f"Mastery path '{path_name}' already unlocked"}
        
        # Check requirements
        requirements_check = self._check_mastery_requirements(character, template["requirements"])
        if not requirements_check["eligible"]:
            return {
                "success": False, 
                "message": f"Requirements not met: {', '.join(requirements_check['missing'])}"
            }
        
        # Unlock the path
        new_path = {
            "path_name": path_name,
            "domain": domain_type.value,
            "progress": 0,
            "active": False,
            "unlocked_at": datetime.now().isoformat(),
            "benefits": template["benefits"]
        }
        
        character.mastery_paths.append(new_path)
        character.updated_at = datetime.now()
        
        return {"success": True, "message": f"Mastery path '{path_name}' unlocked!", "path": new_path}
    
    def activate_mastery_path(self, character: Character, path_name: str) -> Dict[str, Any]:
        """
        Activate/deactivate a mastery path.
        """
        path = next((p for p in character.mastery_paths 
                    if p.get("path_name") == path_name), None)
        
        if not path:
            return {"success": False, "message": f"Mastery path '{path_name}' not found"}
        
        # Toggle active state
        path["active"] = not path.get("active", False)
        character.updated_at = datetime.now()
        
        status = "activated" if path["active"] else "deactivated"
        return {"success": True, "message": f"Mastery path '{path_name}' {status}"}
    
    def get_mastery_path_info(self, character: Character, domain_type: Optional[DomainType] = None) -> Dict[str, Any]:
        """
        Get information about available, unlocked, and active mastery paths.
        """
        if domain_type:
            available_paths = self._generate_enhanced_mastery_paths(character, domain_type)
        else:
            available_paths = []
            for dt in DomainType:
                available_paths.extend(self._generate_enhanced_mastery_paths(character, dt))
        
        unlocked_paths = [p for p in available_paths if p["status"] == "unlocked"]
        active_paths = [p for p in unlocked_paths if p["active"]]
        available_to_unlock = [p for p in available_paths if p["can_unlock"] and p["status"] == "available"]
        
        return {
            "total_available": len(available_paths),
            "unlocked": len(unlocked_paths),
            "active": len(active_paths),
            "can_unlock": len(available_to_unlock),
            "unlocked_paths": unlocked_paths,
            "active_paths": active_paths,
            "available_to_unlock": available_to_unlock
        }
    
    def _check_grinding_penalty(self, character: Character, action_data: Dict[str, Any]) -> float:
        """
        Check for and apply anti-grinding penalties.
        """
        char_id = character.id
        current_time = datetime.now().timestamp()
        
        # Create action signature for tracking
        action_signature = f"{action_data.get('action_type', 'unknown')}_{action_data.get('domain', 'unknown')}_{action_data.get('tag', 'unknown')}"
        
        # Initialize tracking for character if needed
        if char_id not in self.ACTION_GRINDING_TRACKER:
            self.ACTION_GRINDING_TRACKER[char_id] = {}
        
        char_tracker = self.ACTION_GRINDING_TRACKER[char_id]
        
        # Clean old entries (outside time window)
        time_window = self.GRINDING_PENALTIES["time_window"]
        char_tracker[action_signature] = [
            timestamp for timestamp in char_tracker.get(action_signature, [])
            if current_time - timestamp < time_window
        ]
        
        # Add current action
        if action_signature not in char_tracker:
            char_tracker[action_signature] = []
        char_tracker[action_signature].append(current_time)
        
        # Check for grinding
        repeated_count = len(char_tracker[action_signature])
        repeated_threshold = self.GRINDING_PENALTIES["repeated_threshold"]
        
        if repeated_count > repeated_threshold:
            # Apply escalating penalty
            penalty_multiplier = 1.0 - (self.GRINDING_PENALTIES["growth_penalty"] * (repeated_count - repeated_threshold))
            return max(0.1, penalty_multiplier)  # Minimum 10% effectiveness
        
        return 1.0  # No penalty

    def process_action(self, 
                 character: Character, 
                 domain_type: DomainType,
                 action_description: str,  # e.g., "Persuade the guard", "Craft a healing potion"
                 tag_name: Optional[str] = None,
                 action_data: Optional[Dict[str, Any]] = None,  # For difficulty, modifiers, type, etc.
                 target: Optional[Dict[str, Any]] = None,
                 combat_state: Optional[Dict[str, Any]] = None,
                 # Player inputs for intent:
                 player_declared_goal_alignment: Optional[str] = None, 
                 player_approach_description: Optional[str] = None,
                 force_resolution_method: Optional[ResolutionMethod] = None
                 ) -> Dict[str, Any]:
        """
        Main entry point to process a player action.
        """
        # 1. Analyze player intent (simplified for now)
        current_action_data = action_data.copy() if action_data else {}
        if player_declared_goal_alignment:
            current_action_data["aligns_with_goal"] = player_declared_goal_alignment
        if player_approach_description:
            current_action_data.setdefault("description", "")
            current_action_data["description"] += " " + player_approach_description

        intent_analysis = self._analyze_player_intent(character, current_action_data)

        # 2. Determine resolution method
        difficulty = current_action_data.get("difficulty", 10)  # Base difficulty if applicable

        resolution_type, reason = self._determine_resolution_method(
            character, domain_type, current_action_data, target, combat_state,
            force_dice=(force_resolution_method == ResolutionMethod.DICE),
            force_probability=(force_resolution_method == ResolutionMethod.PROBABILITY)
        )

        # 3. Calculate outcome
        outcome_result = {}
        if resolution_type == ResolutionMethod.DICE:
            outcome_result = self._resolve_dice_check(
                character, domain_type, tag_name, difficulty, current_action_data, target, combat_state
            )
        else:  # PROBABILITY
            outcome_result = self._assess_probability_outcome(
                character, domain_type, tag_name, current_action_data, target
            )

        outcome_result["resolution_reason"] = reason

        # 4. Calculate growth points & insight points
        growth_result = self._calculate_growth_and_insight(character, outcome_result, intent_analysis, current_action_data)

        # 5. Update character progression
        self._apply_progression_changes(character, outcome_result, growth_result)

        # 6. Check for mastery paths
        self._check_and_offer_mastery_paths(character, domain_type)

        # Combine results
        final_result = {**outcome_result, **growth_result}
        return final_result

    # --- Phase 7: World Response Integration and AI-Driven Analysis ---
    
    def analyze_world_impact(self, character: Character, action_result: Dict[str, Any], world_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze how the character's action affects the world and generates appropriate responses.
        """
        action_significance = action_result.get("significance_tier_determined", "minor")
        success = action_result.get("success", False)
        domains_used = action_result.get("domains_used", [])
        
        world_impact = {
            "reputation_changes": {},
            "relationship_effects": {},
            "environment_changes": [],
            "economic_effects": {},
            "political_ramifications": [],
            "narrative_consequences": []
        }
        
        # Analyze reputation impact
        if domains_used:
            primary_domain = domains_used[0].value if domains_used else "unknown"
            reputation_change = self._calculate_reputation_impact(
                character, primary_domain, action_significance, success, world_context
            )
            world_impact["reputation_changes"] = reputation_change
        
        # Analyze relationship effects
        if "npcs_present" in world_context:
            relationship_effects = self._analyze_relationship_impact(
                character, action_result, world_context["npcs_present"]
            )
            world_impact["relationship_effects"] = relationship_effects
        
        # Economic impact for craft/trade actions
        if DomainType.CRAFT in domains_used:
            economic_effects = self._analyze_economic_impact(character, action_result, world_context)
            world_impact["economic_effects"] = economic_effects
        
        # Political ramifications for authority/social actions
        if any(domain in domains_used for domain in [DomainType.AUTHORITY, DomainType.SOCIAL]):
            political_effects = self._analyze_political_impact(character, action_result, world_context)
            world_impact["political_ramifications"] = political_effects
        
        return world_impact
    
    def _calculate_reputation_impact(self, character: Character, domain: str, significance: str, success: bool, world_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate reputation changes based on action results.
        """
        reputation_changes = {}
        
        # Base reputation change
        base_change = {
            "trivial": 1, "minor": 2, "significant": 5, "major": 10, "legendary": 20
        }.get(significance.lower(), 1)
        
        if not success:
            base_change = -abs(base_change) // 2  # Negative for failures, but smaller magnitude
        
        # Domain-specific reputation categories
        domain_reputation_map = {
            "body": ["warrior", "athlete", "guardian"],
            "mind": ["scholar", "strategist", "wise"],
            "spirit": ["holy", "inspirational", "mystical"], 
            "craft": ["artisan", "inventor", "creator"],
            "social": ["diplomat", "entertainer", "friend"],
            "authority": ["leader", "judge", "commander"],
            "awareness": ["scout", "investigator", "perceptive"]
        }
        
        relevant_categories = domain_reputation_map.get(domain, ["general"])
        
        for category in relevant_categories:
            reputation_changes[category] = base_change
        
        # Location-specific modifiers
        location = world_context.get("current_location", {})
        if location.get("type") == "city" and domain in ["social", "authority"]:
            reputation_changes["political"] = base_change // 2
        elif location.get("type") == "wilderness" and domain in ["body", "awareness"]:
            reputation_changes["survivalist"] = base_change
        
        return reputation_changes
    
    def _analyze_relationship_impact(self, character: Character, action_result: Dict[str, Any], npcs_present: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze how the action affects relationships with NPCs.
        """
        relationship_effects = {}
        success = action_result.get("success", False)
        domains_used = action_result.get("domains_used", [])
        
        for npc in npcs_present:
            npc_id = npc.get("id", npc.get("name", "unknown"))
            npc_personality = npc.get("personality", {})
            
            # Base relationship change
            relationship_change = 0
            
            # Success generally improves relationships
            if success:
                relationship_change += 2
            else:
                # Failure might hurt or help depending on NPC personality
                if npc_personality.get("forgiving", False):
                    relationship_change += 1  # Appreciates the attempt
                else:
                    relationship_change -= 1
            
            # Domain-specific relationship modifiers
            if DomainType.SOCIAL in domains_used:
                if npc_personality.get("sociable", True):
                    relationship_change += 2
            elif DomainType.AUTHORITY in domains_used:
                if npc_personality.get("respects_authority", True):
                    relationship_change += 1
                else:
                    relationship_change -= 1
            
            # Character demonstrated values alignment
            npc_values = npc.get("values", [])
            character_values = character.demonstrated_values
            
            for value in npc_values:
                if value in character_values and character_values[value] > 3:
                    relationship_change += 1  # Shared values
            
            if relationship_change != 0:
                relationship_effects[npc_id] = {
                    "change": relationship_change,
                    "reason": f"Response to {domains_used[0].value if domains_used else 'action'} action",
                    "new_disposition": npc.get("disposition", "neutral")
                }
        
        return relationship_effects
    
    def _analyze_economic_impact(self, character: Character, action_result: Dict[str, Any], world_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze economic effects of craft/trade actions.
        """
        economic_effects = {}
        success = action_result.get("success", False)
        
        if success:
            # Successful craft actions affect local economy
            location = world_context.get("current_location", {})
            if location.get("type") == "settlement":
                economic_effects["local_supply"] = {
                    "change": "increased",
                    "items": world_context.get("items_created", []),
                    "value_impact": "minor_deflation" if len(world_context.get("items_created", [])) > 1 else "none"
                }
            
            # Character's craft reputation affects pricing
            craft_reputation = character.demonstrated_values.get("craftsmanship", 0)
            if craft_reputation > 5:
                economic_effects["pricing_modifier"] = 1.2  # 20% premium for known quality
        
        return economic_effects
    
    def _analyze_political_impact(self, character: Character, action_result: Dict[str, Any], world_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze political ramifications of authority/social actions.
        """
        political_effects = []
        success = action_result.get("success", False)
        significance = action_result.get("significance_tier_determined", "minor")
        
        if significance in ["major", "legendary"]:
            location = world_context.get("current_location", {})
            political_entities = world_context.get("political_entities", [])
            
            for entity in political_entities:
                entity_type = entity.get("type", "unknown")
                entity_influence = entity.get("influence_level", "low")
                
                if success and entity_type in ["guild", "faction", "government"]:
                    political_effects.append({
                        "entity": entity.get("name", "Unknown Entity"),
                        "effect": "positive_attention",
                        "magnitude": entity_influence,
                        "consequence": "May offer opportunities or request services"
                    })
                elif not success and entity_type == "government":
                    political_effects.append({
                        "entity": entity.get("name", "Local Government"),
                        "effect": "scrutiny_increased",
                        "magnitude": "low",
                        "consequence": "May investigate or monitor character"
                    })
        
        return political_effects
    
    def generate_narrative_consequences(self, character: Character, action_result: Dict[str, Any], world_impact: Dict[str, Any]) -> List[str]:
        """
        Generate narrative consequences based on action results and world impact.
        """
        consequences = []
        
        # Reputation-based consequences
        rep_changes = world_impact.get("reputation_changes", {})
        for category, change in rep_changes.items():
            if abs(change) >= 5:
                if change > 0:
                    consequences.append(f"Your reputation as a {category} grows. People begin to recognize your capabilities.")
                else:
                    consequences.append(f"Your reputation as a {category} suffers. Some question your abilities.")
        
        # Relationship consequences
        rel_effects = world_impact.get("relationship_effects", {})
        significant_changes = [npc for npc, data in rel_effects.items() if abs(data.get("change", 0)) >= 3]
        if significant_changes:
            consequences.append(f"Your actions significantly affect your relationships with {', '.join(significant_changes[:2])}{'...' if len(significant_changes) > 2 else ''}.")
        
        # Political consequences
        political_effects = world_impact.get("political_ramifications", [])
        for effect in political_effects:
            if effect.get("magnitude") in ["high", "very_high"]:
                consequences.append(f"The {effect.get('entity')} takes notice of your actions. {effect.get('consequence')}")
        
        # Economic consequences
        economic_effects = world_impact.get("economic_effects", {})
        if "pricing_modifier" in economic_effects and economic_effects["pricing_modifier"] > 1.1:
            consequences.append("Your reputation for quality craftsmanship commands premium prices.")
        
        return consequences
    
    def suggest_adaptive_challenges(self, character: Character, recent_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Suggest adaptive challenges based on character's recent performance and growth patterns.
        """
        challenges = []
        
        # Analyze recent performance patterns
        recent_successes = [action for action in recent_actions if action.get("success", False)]
        recent_failures = [action for action in recent_actions if not action.get("success", False)]
        
        success_rate = len(recent_successes) / len(recent_actions) if recent_actions else 0.5
        
        # Analyze domain usage patterns
        domain_usage = {}
        for action in recent_actions:
            for domain in action.get("domains_used", []):
                domain_usage[domain.value] = domain_usage.get(domain.value, 0) + 1
        
        most_used_domain = max(domain_usage.items(), key=lambda x: x[1])[0] if domain_usage else None
        
        # Generate appropriate challenges
        if success_rate > 0.8:  # Very high success rate - increase difficulty
            challenges.append({
                "type": "difficulty_escalation",
                "description": f"Consider introducing more complex {most_used_domain} challenges",
                "suggested_modifiers": {"difficulty_increase": 3, "narrative_stakes": "higher"}
            })
        
        elif success_rate < 0.3:  # Low success rate - provide alternatives
            challenges.append({
                "type": "alternative_approaches",
                "description": "Suggest creative problem-solving options or insight point usage",
                "suggested_modifiers": {"insight_hints": True, "creative_bonus": 2}
            })
        
        # Cross-domain challenges for growth
        underused_domains = [domain.value for domain in DomainType if domain.value not in domain_usage or domain_usage[domain.value] < 2]
        if underused_domains:
            challenges.append({
                "type": "cross_domain_opportunity",
                "description": f"Create opportunities to use {underused_domains[0]} in combination with {most_used_domain}",
                "suggested_modifiers": {"cross_training_bonus": True}
            })
        
        return challenges


# Global instance for singleton pattern
unified_progression_system = UnifiedProgressionSystem()
unified_progression_system = UnifiedProgressionSystem()
