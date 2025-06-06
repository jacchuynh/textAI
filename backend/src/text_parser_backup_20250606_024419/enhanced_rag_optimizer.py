#!/usr/bin/env python3
"""
Enhanced RAG Optimizer for TextRealmsAI Parser Engine

This module provides optimizations for the RAG triggering logic and confidence
thresholds to improve semantic understanding of complex magical and crafting queries.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

@dataclass
class RAGOptimizationConfig:
    """Configuration for RAG optimization"""
    
    # Confidence thresholds
    high_confidence_threshold: float = 0.7
    medium_confidence_threshold: float = 0.5
    fallback_confidence_threshold: float = 0.3
    
    # Word count thresholds
    min_word_count: int = 4  # Reduced from 3 to catch more complex queries
    complex_query_word_count: int = 8
    
    # Semantic complexity indicators
    semantic_complexity_boost: float = 0.2
    philosophical_query_boost: float = 0.3
    multi_domain_query_boost: float = 0.25


class EnhancedRAGOptimizer:
    """
    Enhanced RAG optimization system for better semantic understanding.
    """
    
    def __init__(self, config: Optional[RAGOptimizationConfig] = None):
        self.config = config or RAGOptimizationConfig()
        self.logger = logging.getLogger("text_parser.rag_optimizer")
        
        # Semantic complexity indicators
        self.complexity_indicators = {
            "philosophical": [
                "understand", "meaning", "essence", "relationship", "connection",
                "balance", "implications", "significance", "nature", "purpose",
                "why", "how", "what", "moral", "ethical", "philosophy"
            ],
            "multi_domain": [
                "between", "and", "with", "combining", "relationship",
                "interaction", "bridge", "connect", "merge", "integrate"
            ],
            "magical_theory": [
                "magic", "magical", "spell", "enchantment", "arcane", "mystical",
                "elemental", "divination", "transmutation", "binding", "channeling",
                "celestial", "ancient", "runes", "void", "spirit"
            ],
            "crafting_theory": [
                "crafting", "blacksmithing", "alchemy", "brewing", "forging",
                "materials", "components", "techniques", "enhancement", "durability",
                "infusion", "herbalism", "potion"
            ],
            "exploration_curiosity": [
                "explore", "discover", "find", "search", "investigate", "curious",
                "secrets", "hidden", "ancient", "mysteries", "lore", "knowledge"
            ],
            "character_development": [
                "become", "develop", "master", "learn", "grow", "path", "goal",
                "abilities", "skills", "respected", "character", "journey"
            ]
        }
        
        # Query type patterns for better categorization
        self.query_patterns = {
            "help_request": r'\b(help|guide|assistance|advice)\b',
            "understanding_seeking": r'\b(understand|comprehend|grasp|figure out)\b',
            "relationship_query": r'\b(relationship|connection|interaction|between)\b',
            "method_inquiry": r'\b(how|what.*method|approach|way|technique)\b',
            "philosophical": r'\b(why|meaning|essence|moral|ethical|implications)\b',
            "exploration": r'\b(explore|discover|find|secrets|hidden|ancient)\b'
        }

    def should_trigger_rag(self, input_text: str, traditional_confidence: float) -> Tuple[bool, str, float]:
        """
        Determine if RAG should be triggered based on enhanced criteria.
        
        Args:
            input_text: The user's input text
            traditional_confidence: Confidence from traditional parsing
            
        Returns:
            Tuple of (should_trigger, reason, priority_score)
        """
        word_count = len(input_text.split())
        
        # Always trigger for longer queries regardless of confidence
        if word_count >= self.config.complex_query_word_count:
            return True, "complex_length", 0.9
        
        # Trigger for medium-length queries with semantic complexity
        if word_count >= self.config.min_word_count:
            complexity_score = self._calculate_semantic_complexity(input_text)
            
            # Trigger RAG if high semantic complexity detected
            if complexity_score > 0.6:
                return True, f"semantic_complexity_{complexity_score:.2f}", complexity_score
            
            # Trigger for specific query types even with high traditional confidence
            query_type_score = self._analyze_query_type(input_text)
            if query_type_score > 0.7:
                return True, f"query_type_{query_type_score:.2f}", query_type_score
            
            # Trigger if traditional confidence is questionable
            if traditional_confidence < self.config.high_confidence_threshold:
                return True, f"low_confidence_{traditional_confidence:.2f}", 0.6
        
        return False, "criteria_not_met", 0.0

    def _calculate_semantic_complexity(self, text: str) -> float:
        """Calculate semantic complexity score based on content analysis."""
        text_lower = text.lower()
        total_score = 0.0
        max_possible = len(self.complexity_indicators)
        
        for category, indicators in self.complexity_indicators.items():
            category_matches = sum(1 for indicator in indicators if indicator in text_lower)
            if category_matches > 0:
                # Weight different categories
                if category == "philosophical":
                    total_score += min(category_matches * 0.3, 1.0)
                elif category == "multi_domain":
                    total_score += min(category_matches * 0.25, 1.0)
                else:
                    total_score += min(category_matches * 0.2, 1.0)
        
        return min(total_score, 1.0)

    def _analyze_query_type(self, text: str) -> float:
        """Analyze query type to determine RAG suitability."""
        max_score = 0.0
        
        for query_type, pattern in self.query_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Different query types have different RAG suitability
                type_scores = {
                    "help_request": 0.8,
                    "understanding_seeking": 0.9,
                    "relationship_query": 0.85,
                    "method_inquiry": 0.8,
                    "philosophical": 0.95,
                    "exploration": 0.7
                }
                max_score = max(max_score, type_scores.get(query_type, 0.6))
        
        return max_score

    def optimize_rag_confidence_threshold(self, input_text: str, rag_confidence: float) -> Tuple[str, float]:
        """
        Determine the appropriate confidence threshold and routing for RAG results.
        
        Args:
            input_text: The user's input text
            rag_confidence: RAG analysis confidence score
            
        Returns:
            Tuple of (routing_decision, adjusted_confidence)
        """
        complexity_score = self._calculate_semantic_complexity(input_text)
        query_type_score = self._analyze_query_type(input_text)
        
        # Adjust confidence based on content analysis
        adjusted_confidence = rag_confidence
        
        # Boost confidence for appropriate content types
        if complexity_score > 0.7:
            adjusted_confidence += self.config.semantic_complexity_boost
        
        if query_type_score > 0.8:
            adjusted_confidence += self.config.philosophical_query_boost
        
        # Multi-domain queries benefit from RAG
        if "and" in input_text.lower() and complexity_score > 0.5:
            adjusted_confidence += self.config.multi_domain_query_boost
        
        # Cap at 1.0
        adjusted_confidence = min(adjusted_confidence, 1.0)
        
        # Determine routing
        if adjusted_confidence >= self.config.high_confidence_threshold:
            return "high_confidence_rag", adjusted_confidence
        elif adjusted_confidence >= self.config.medium_confidence_threshold:
            return "medium_confidence_rag", adjusted_confidence
        elif adjusted_confidence >= self.config.fallback_confidence_threshold:
            return "fallback_rag", adjusted_confidence
        else:
            return "no_rag", adjusted_confidence

    def should_prefer_rag_over_traditional(self, input_text: str, traditional_confidence: float, rag_confidence: float) -> bool:
        """
        Determine if RAG results should be preferred over traditional parsing.
        
        Args:
            input_text: The user's input text
            traditional_confidence: Traditional parsing confidence
            rag_confidence: RAG analysis confidence
            
        Returns:
            True if RAG should be preferred
        """
        # Always prefer RAG for highly semantic content
        if self._calculate_semantic_complexity(input_text) > 0.8:
            return True
        
        # Prefer RAG for philosophical/understanding queries
        if self._analyze_query_type(input_text) > 0.85:
            return True
        
        # Prefer RAG if it's significantly more confident
        if rag_confidence > traditional_confidence + 0.2:
            return True
        
        # Prefer RAG for complex multi-domain queries
        word_count = len(input_text.split())
        if word_count > 10 and rag_confidence > 0.6:
            return True
        
        return False

    def generate_optimization_report(self, input_text: str, traditional_result: Dict[str, Any], rag_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a detailed optimization analysis report."""
        
        complexity_score = self._calculate_semantic_complexity(input_text)
        query_type_score = self._analyze_query_type(input_text)
        word_count = len(input_text.split())
        
        should_trigger, trigger_reason, trigger_priority = self.should_trigger_rag(
            input_text, traditional_result.get("confidence", 0.0)
        )
        
        routing_decision, adjusted_confidence = self.optimize_rag_confidence_threshold(
            input_text, rag_result.get("confidence", 0.0)
        )
        
        prefer_rag = self.should_prefer_rag_over_traditional(
            input_text,
            traditional_result.get("confidence", 0.0),
            rag_result.get("confidence", 0.0)
        )
        
        return {
            "input_analysis": {
                "word_count": word_count,
                "semantic_complexity": complexity_score,
                "query_type_score": query_type_score,
                "complexity_category": self._get_complexity_category(complexity_score)
            },
            "rag_triggering": {
                "should_trigger": should_trigger,
                "trigger_reason": trigger_reason,
                "trigger_priority": trigger_priority
            },
            "confidence_optimization": {
                "original_rag_confidence": rag_result.get("confidence", 0.0),
                "adjusted_rag_confidence": adjusted_confidence,
                "routing_decision": routing_decision
            },
            "final_recommendation": {
                "prefer_rag": prefer_rag,
                "reasoning": self._get_preference_reasoning(input_text, traditional_result, rag_result)
            }
        }

    def _get_complexity_category(self, score: float) -> str:
        """Get human-readable complexity category."""
        if score >= 0.8:
            return "very_high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "minimal"

    def _get_preference_reasoning(self, input_text: str, traditional_result: Dict[str, Any], rag_result: Dict[str, Any]) -> str:
        """Generate reasoning for RAG vs traditional preference."""
        reasons = []
        
        complexity = self._calculate_semantic_complexity(input_text)
        if complexity > 0.7:
            reasons.append(f"High semantic complexity ({complexity:.2f})")
        
        query_type = self._analyze_query_type(input_text)
        if query_type > 0.8:
            reasons.append(f"Query type highly suitable for RAG ({query_type:.2f})")
        
        trad_conf = traditional_result.get("confidence", 0.0)
        rag_conf = rag_result.get("confidence", 0.0)
        
        if rag_conf > trad_conf + 0.2:
            reasons.append(f"RAG significantly more confident ({rag_conf:.2f} vs {trad_conf:.2f})")
        
        word_count = len(input_text.split())
        if word_count > 10:
            reasons.append(f"Complex length query ({word_count} words)")
        
        return "; ".join(reasons) if reasons else "Traditional parsing sufficient"


# Example usage and testing functions
def test_rag_optimizer():
    """Test the RAG optimizer with sample inputs."""
    optimizer = EnhancedRAGOptimizer()
    
    test_cases = [
        "I need to understand the essence behind elemental binding magic",
        "Help me figure out the relationship between void magic and spirit channeling",
        "What kind of preparation is needed for advanced transmutation rituals",
        "go north",
        "take sword"
    ]
    
    for test_input in test_cases:
        should_trigger, reason, priority = optimizer.should_trigger_rag(test_input, 0.8)
        complexity = optimizer._calculate_semantic_complexity(test_input)
        query_type = optimizer._analyze_query_type(test_input)
        
        print(f"\nInput: '{test_input}'")
        print(f"  Should trigger RAG: {should_trigger} (reason: {reason}, priority: {priority:.2f})")
        print(f"  Semantic complexity: {complexity:.2f}")
        print(f"  Query type score: {query_type:.2f}")


if __name__ == "__main__":
    test_rag_optimizer()
