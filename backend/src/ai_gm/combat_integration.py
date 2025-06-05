"""
Combat Integration for AI GM Brain

This module provides integration between the AI GM Brain and the enhanced combat system,
handling combat-related AI decisions and responses.
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime

class CombatPhase(Enum):
    """Phases of combat."""
    PRE_COMBAT = auto()     # Before combat begins
    INITIATIVE = auto()     # Rolling initiative
    COMBAT_ROUND = auto()   # During combat rounds
    POST_COMBAT = auto()    # After combat ends
    RESOLUTION = auto()     # Handling aftermath

class CombatEventType(Enum):
    """Types of combat events."""
    COMBAT_START = auto()
    COMBAT_END = auto()
    ROUND_START = auto()
    ROUND_END = auto()
    ATTACK = auto()
    DAMAGE = auto()
    HEALING = auto()
    STATUS_EFFECT = auto()
    DEATH = auto()
    VICTORY = auto()

@dataclass
class CombatContext:
    """Context information for combat situations."""
    phase: CombatPhase
    round_number: int
    active_combatants: List[str]
    current_actor: Optional[str]
    environment: Dict[str, Any]
    special_conditions: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "phase": self.phase.name,
            "round_number": self.round_number,
            "active_combatants": self.active_combatants,
            "current_actor": self.current_actor,
            "environment": self.environment,
            "special_conditions": self.special_conditions
        }

@dataclass
class CombatEvent:
    """Represents a combat event."""
    event_type: CombatEventType
    actor: str
    target: Optional[str]
    details: Dict[str, Any]
    timestamp: datetime
    round_number: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "event_type": self.event_type.name,
            "actor": self.actor,
            "target": self.target,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
            "round_number": self.round_number
        }

class CombatAIAssistant:
    """AI assistant for combat decision making."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_combat_situation(self, context: CombatContext, combatant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the current combat situation."""
        analysis = {
            "threat_level": self._assess_threat_level(combatant_data),
            "tactical_suggestions": self._generate_tactical_suggestions(context, combatant_data),
            "environmental_factors": self._analyze_environment(context.environment),
            "status_assessment": self._assess_status_effects(combatant_data)
        }
        
        return analysis
    
    def _assess_threat_level(self, combatant_data: Dict[str, Any]) -> str:
        """Assess the overall threat level of the combat."""
        # Simple threat assessment based on health ratios
        player_health = combatant_data.get("player_health_ratio", 1.0)
        enemy_count = len(combatant_data.get("enemies", []))
        
        if player_health < 0.3:
            return "CRITICAL"
        elif player_health < 0.5 and enemy_count > 1:
            return "HIGH"
        elif player_health < 0.7 or enemy_count > 2:
            return "MODERATE"
        else:
            return "LOW"
    
    def _generate_tactical_suggestions(self, context: CombatContext, combatant_data: Dict[str, Any]) -> List[str]:
        """Generate tactical suggestions for the current situation."""
        suggestions = []
        
        player_health = combatant_data.get("player_health_ratio", 1.0)
        available_actions = combatant_data.get("available_actions", [])
        
        if player_health < 0.3:
            suggestions.append("Consider healing or defensive actions")
        
        if "retreat" in available_actions and len(combatant_data.get("enemies", [])) > 2:
            suggestions.append("Retreat might be wise against multiple enemies")
        
        if context.environment.get("cover_available"):
            suggestions.append("Use available cover for defensive advantage")
        
        if "special_attack" in available_actions:
            suggestions.append("Special attacks might turn the tide")
        
        return suggestions
    
    def _analyze_environment(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental factors affecting combat."""
        factors = {
            "terrain_type": environment.get("terrain", "normal"),
            "lighting": environment.get("lighting", "normal"),
            "weather": environment.get("weather", "clear"),
            "hazards": environment.get("hazards", []),
            "tactical_elements": []
        }
        
        # Identify tactical elements
        if environment.get("cover_available"):
            factors["tactical_elements"].append("cover")
        if environment.get("high_ground"):
            factors["tactical_elements"].append("elevation_advantage")
        if environment.get("difficult_terrain"):
            factors["tactical_elements"].append("movement_restriction")
        
        return factors
    
    def _assess_status_effects(self, combatant_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess status effects affecting combatants."""
        assessment = {
            "player_effects": combatant_data.get("player_status_effects", []),
            "enemy_effects": {},
            "effect_priorities": []
        }
        
        # Analyze player status effects
        for effect in assessment["player_effects"]:
            if effect.get("severity") == "CRITICAL":
                assessment["effect_priorities"].append(f"Address critical {effect.get('name')} effect")
        
        return assessment

class CombatIntegration:
    """Main integration class for combat system integration with AI GM Brain."""
    
    def __init__(self, game_id: str, player_id: str):
        self.game_id = game_id
        self.player_id = player_id
        self.logger = logging.getLogger(__name__)
        self.ai_assistant = CombatAIAssistant()
        self.combat_history: List[CombatEvent] = []
        self.current_context: Optional[CombatContext] = None
        self.combat_active = False
        
        self.logger.info(f"Combat Integration initialized for game {game_id} and player {player_id}")
    
    def start_combat(self, combatants: List[str], environment: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start a new combat encounter."""
        self.combat_active = True
        self.current_context = CombatContext(
            phase=CombatPhase.PRE_COMBAT,
            round_number=0,
            active_combatants=combatants,
            current_actor=None,
            environment=environment or {},
            special_conditions=[]
        )
        
        # Record combat start event
        event = CombatEvent(
            event_type=CombatEventType.COMBAT_START,
            actor="system",
            target=None,
            details={"combatants": combatants, "environment": environment},
            timestamp=datetime.utcnow(),
            round_number=0
        )
        self.combat_history.append(event)
        
        self.logger.info(f"Combat started with combatants: {combatants}")
        
        return {
            "success": True,
            "message": "Combat has begun!",
            "context": self.current_context.to_dict(),
            "combat_id": len(self.combat_history)
        }
    
    def end_combat(self, result: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """End the current combat encounter."""
        if not self.combat_active:
            return {"success": False, "message": "No active combat to end"}
        
        self.combat_active = False
        
        if self.current_context:
            self.current_context.phase = CombatPhase.POST_COMBAT
        
        # Record combat end event
        event = CombatEvent(
            event_type=CombatEventType.COMBAT_END,
            actor="system",
            target=None,
            details={"result": result, **(details or {})},
            timestamp=datetime.utcnow(),
            round_number=self.current_context.round_number if self.current_context else 0
        )
        self.combat_history.append(event)
        
        self.logger.info(f"Combat ended with result: {result}")
        
        return {
            "success": True,
            "message": f"Combat ended: {result}",
            "result": result,
            "details": details
        }
    
    def process_combat_round(self, round_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a combat round and provide AI assistance."""
        if not self.combat_active or not self.current_context:
            return {"success": False, "message": "No active combat"}
        
        # Update context
        self.current_context.round_number += 1
        self.current_context.phase = CombatPhase.COMBAT_ROUND
        self.current_context.current_actor = round_data.get("current_actor")
        
        # Record round start
        round_event = CombatEvent(
            event_type=CombatEventType.ROUND_START,
            actor="system",
            target=None,
            details=round_data,
            timestamp=datetime.utcnow(),
            round_number=self.current_context.round_number
        )
        self.combat_history.append(round_event)
        
        # Analyze situation
        analysis = self.ai_assistant.analyze_combat_situation(
            self.current_context, 
            round_data.get("combatant_data", {})
        )
        
        return {
            "success": True,
            "round_number": self.current_context.round_number,
            "analysis": analysis,
            "context": self.current_context.to_dict()
        }
    
    def record_combat_event(self, event_type: CombatEventType, actor: str, target: str = None, details: Dict[str, Any] = None) -> CombatEvent:
        """Record a combat event."""
        event = CombatEvent(
            event_type=event_type,
            actor=actor,
            target=target,
            details=details or {},
            timestamp=datetime.utcnow(),
            round_number=self.current_context.round_number if self.current_context else 0
        )
        
        self.combat_history.append(event)
        self.logger.debug(f"Recorded combat event: {event_type.name} by {actor}")
        
        return event
    
    def get_combat_analysis(self, player_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze player input in combat context."""
        if not self.combat_active:
            return {"in_combat": False}
        
        # Parse combat-related input
        analysis = {
            "in_combat": True,
            "action_type": self._classify_combat_action(player_input),
            "targets": self._identify_targets(player_input, context),
            "suggestions": [],
            "warnings": []
        }
        
        # Add AI suggestions if appropriate
        if self.current_context:
            combatant_data = context.get("combatant_data", {}) if context else {}
            ai_analysis = self.ai_assistant.analyze_combat_situation(self.current_context, combatant_data)
            analysis["ai_suggestions"] = ai_analysis.get("tactical_suggestions", [])
        
        return analysis
    
    def _classify_combat_action(self, player_input: str) -> str:
        """Classify the type of combat action from player input."""
        input_lower = player_input.lower()
        
        if any(word in input_lower for word in ["attack", "hit", "strike", "swing"]):
            return "attack"
        elif any(word in input_lower for word in ["defend", "block", "parry", "guard"]):
            return "defend"
        elif any(word in input_lower for word in ["cast", "spell", "magic"]):
            return "spell"
        elif any(word in input_lower for word in ["heal", "potion", "medicine"]):
            return "heal"
        elif any(word in input_lower for word in ["retreat", "flee", "run", "escape"]):
            return "retreat"
        elif any(word in input_lower for word in ["move", "position", "step"]):
            return "movement"
        else:
            return "other"
    
    def _identify_targets(self, player_input: str, context: Dict[str, Any] = None) -> List[str]:
        """Identify potential targets from player input."""
        targets = []
        
        if not context or not self.current_context:
            return targets
        
        # Look for enemy names in input
        enemies = context.get("enemies", [])
        input_lower = player_input.lower()
        
        for enemy in enemies:
            if enemy.lower() in input_lower:
                targets.append(enemy)
        
        return targets
    
    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat status."""
        return {
            "combat_active": self.combat_active,
            "current_context": self.current_context.to_dict() if self.current_context else None,
            "events_recorded": len(self.combat_history),
            "round_number": self.current_context.round_number if self.current_context else 0
        }
    
    def get_combat_history(self, count: int = 10) -> List[CombatEvent]:
        """Get recent combat events."""
        return self.combat_history[-count:] if count > 0 else self.combat_history[:]
    
    def get_combat_statistics(self) -> Dict[str, Any]:
        """Get combat statistics."""
        total_events = len(self.combat_history)
        
        event_counts = {}
        for event in self.combat_history:
            event_type = event.event_type.name
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
        
        return {
            "total_events": total_events,
            "events_by_type": event_counts,
            "combat_active": self.combat_active,
            "current_round": self.current_context.round_number if self.current_context else 0
        }
    
    def clear_combat_history(self):
        """Clear combat history."""
        self.combat_history.clear()
        self.logger.info("Combat history cleared")

# Convenience function for easy integration
def create_combat_integration(game_id: str, player_id: str) -> CombatIntegration:
    """Create and return a CombatIntegration instance."""
    return CombatIntegration(game_id, player_id)
