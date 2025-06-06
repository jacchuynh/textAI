#!/usr/bin/env python3
"""
RAG Integration Patch for TextRealmsAI Parser Engine

This script provides an enhanced RAG integration system that improves
the triggering logic and confidence thresholds for better semantic understanding.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

class RAGIntegrationPatch:
    """
    Patch for enhancing RAG integration in the ParserEngine.
    """
    
    def __init__(self, parser_engine):
        self.parser_engine = parser_engine
        self.logger = logging.getLogger("text_parser.rag_patch")
        
        # Import the optimizer
        try:
            from .enhanced_rag_optimizer import EnhancedRAGOptimizer, RAGOptimizationConfig
            self.optimizer = EnhancedRAGOptimizer()
            self.logger.info("RAG optimizer loaded successfully")
        except ImportError:
            self.logger.warning("RAG optimizer not available, using fallback logic")
            self.optimizer = None

    def enhanced_rag_analysis(self, input_text: str, traditional_confidence: float) -> Dict[str, Any]:
        """
        Enhanced RAG analysis with improved triggering logic.
        
        Args:
            input_text: The user's input text
            traditional_confidence: Confidence from traditional parsing
            
        Returns:
            Enhanced RAG analysis results
        """
        if not self.parser_engine.rag_available:
            return {"rag_available": False, "reason": "RAG components not initialized"}
        
        # Use optimizer to determine if RAG should be triggered
        should_trigger = True  # Default to trigger for now
        trigger_reason = "enhanced_logic"
        trigger_priority = 0.7
        
        if self.optimizer:
            should_trigger, trigger_reason, trigger_priority = self.optimizer.should_trigger_rag(
                input_text, traditional_confidence
            )
        else:
            # Fallback logic - more liberal triggering
            word_count = len(input_text.split())
            should_trigger = (
                word_count >= 4 or  # Reduced from 3
                traditional_confidence < 0.7 or  # Lower threshold
                self._contains_semantic_indicators(input_text)
            )
        
        if not should_trigger:
            return {
                "rag_available": True,
                "triggered": False,
                "reason": f"Not triggered: {trigger_reason}",
                "confidence": 0.1
            }
        
        # Perform RAG analysis
        try:
            rag_result = self.parser_engine._extract_intents_with_rag(input_text, confidence_threshold=0.3)
            
            if self.optimizer and rag_result.get("rag_available"):
                # Use optimizer to enhance the result
                routing_decision, adjusted_confidence = self.optimizer.optimize_rag_confidence_threshold(
                    input_text, rag_result.get("confidence", 0.0)
                )
                
                rag_result["routing_decision"] = routing_decision
                rag_result["original_confidence"] = rag_result.get("confidence", 0.0)
                rag_result["adjusted_confidence"] = adjusted_confidence
                rag_result["confidence"] = adjusted_confidence  # Update the confidence
                
                # Determine if RAG should be preferred
                prefer_rag = self.optimizer.should_prefer_rag_over_traditional(
                    input_text, traditional_confidence, adjusted_confidence
                )
                rag_result["prefer_rag"] = prefer_rag
            
            rag_result["triggered"] = True
            rag_result["trigger_reason"] = trigger_reason
            rag_result["trigger_priority"] = trigger_priority
            
            return rag_result
            
        except Exception as e:
            self.logger.error(f"Enhanced RAG analysis failed: {e}")
            return {
                "rag_available": True,
                "triggered": False,
                "error": str(e),
                "confidence": 0.1
            }

    def _contains_semantic_indicators(self, text: str) -> bool:
        """Check if text contains semantic complexity indicators."""
        semantic_indicators = [
            "understand", "relationship", "between", "connection", "essence",
            "meaning", "how", "why", "what", "help me", "explain",
            "figure out", "balance", "combination", "approach"
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in semantic_indicators)

    def integrate_rag_into_parsing(self, input_text: str, traditional_result: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Integrate RAG analysis into the parsing flow.
        
        Args:
            input_text: The user's input text
            traditional_result: Results from traditional parsing
            
        Returns:
            Integrated parsing results with RAG enhancement
        """
        traditional_confidence = traditional_result.get("confidence", 0.5) if traditional_result else 0.5
        
        # Perform enhanced RAG analysis
        rag_analysis = self.enhanced_rag_analysis(input_text, traditional_confidence)
        
        result = {
            "input_text": input_text,
            "traditional_result": traditional_result,
            "rag_analysis": rag_analysis,
            "integration_decision": "traditional"  # Default
        }
        
        # Determine integration strategy
        if rag_analysis.get("triggered") and rag_analysis.get("rag_available"):
            rag_confidence = rag_analysis.get("confidence", 0.0)
            
            # High confidence RAG analysis
            if rag_confidence >= 0.7:
                result["integration_decision"] = "high_confidence_rag"
                result["final_confidence"] = rag_confidence
                result["enhanced_intent"] = rag_analysis.get("enhanced_intent", "")
                
            # Medium confidence RAG - combine with traditional
            elif rag_confidence >= 0.5:
                result["integration_decision"] = "hybrid_rag_traditional"
                result["final_confidence"] = max(traditional_confidence, rag_confidence * 0.8)
                result["enhanced_intent"] = rag_analysis.get("enhanced_intent", "")
                
            # Low confidence RAG - use as fallback context
            elif rag_confidence >= 0.3:
                result["integration_decision"] = "rag_context_supplement"
                result["final_confidence"] = traditional_confidence
                result["context_supplement"] = rag_analysis.get("enhanced_intent", "")
        
        # Use optimizer recommendation if available
        if self.optimizer and rag_analysis.get("prefer_rag"):
            result["integration_decision"] = "optimizer_prefers_rag"
            result["final_confidence"] = rag_analysis.get("confidence", traditional_confidence)
        
        return result

    def generate_enhanced_context(self, input_text: str, integration_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate enhanced context for the parsed command.
        
        Args:
            input_text: The user's input text
            integration_result: Results from RAG integration
            
        Returns:
            Enhanced context dictionary
        """
        context = {
            "rag_integration_enabled": True,
            "integration_decision": integration_result.get("integration_decision", "traditional"),
            "word_count": len(input_text.split())
        }
        
        rag_analysis = integration_result.get("rag_analysis", {})
        
        if rag_analysis.get("triggered"):
            context["rag_triggered"] = True
            context["rag_trigger_reason"] = rag_analysis.get("trigger_reason", "unknown")
            context["rag_confidence"] = rag_analysis.get("confidence", 0.0)
            
            if rag_analysis.get("enhanced_intent"):
                context["rag_enhanced_intent"] = rag_analysis.get("enhanced_intent")
                
            if rag_analysis.get("relevant_context"):
                context["rag_context_count"] = len(rag_analysis.get("relevant_context", []))
                context["rag_max_relevance"] = max(
                    (ctx.get("relevance_score", 0.0) for ctx in rag_analysis.get("relevant_context", [])),
                    default=0.0
                )
        else:
            context["rag_triggered"] = False
            context["rag_skip_reason"] = rag_analysis.get("reason", "unknown")
        
        # Add optimizer analysis if available
        if self.optimizer:
            complexity = self.optimizer._calculate_semantic_complexity(input_text)
            query_type = self.optimizer._analyze_query_type(input_text)
            
            context["semantic_complexity"] = complexity
            context["query_type_score"] = query_type
            context["complexity_category"] = self.optimizer._get_complexity_category(complexity)
        
        return context


def patch_parser_engine_with_enhanced_rag(parser_engine):
    """
    Patch an existing ParserEngine instance with enhanced RAG capabilities.
    
    Args:
        parser_engine: The ParserEngine instance to patch
        
    Returns:
        The patched parser engine with enhanced RAG integration
    """
    # Create the RAG integration patch
    rag_patch = RAGIntegrationPatch(parser_engine)
    
    # Store original methods
    parser_engine._original_extract_intents_with_rag = parser_engine._extract_intents_with_rag
    
    # Patch the RAG extraction method
    def enhanced_extract_intents_with_rag(input_text: str, confidence_threshold: float = 0.3) -> Dict[str, Any]:
        traditional_confidence = 0.7  # Assume traditional parsing would have medium confidence
        return rag_patch.enhanced_rag_analysis(input_text, traditional_confidence)
    
    parser_engine._extract_intents_with_rag = enhanced_extract_intents_with_rag
    parser_engine.rag_patch = rag_patch
    
    logging.getLogger("text_parser.rag_patch").info("ParserEngine patched with enhanced RAG integration")
    
    return parser_engine


# Test function for the patch
def test_enhanced_rag_patch():
    """Test the enhanced RAG patch functionality."""
    import sys
    import os
    from pathlib import Path
    
    # Add backend src to path
    backend_dir = Path(__file__).parent.parent.parent / "backend" / "src"
    sys.path.insert(0, str(backend_dir))
    
    try:
        from text_parser.parser_engine import ParserEngine
        
        # Create parser engine
        parser = ParserEngine()
        
        # Patch with enhanced RAG
        patched_parser = patch_parser_engine_with_enhanced_rag(parser)
        
        # Test cases
        test_cases = [
            "I need to understand the essence behind elemental binding magic",
            "Help me figure out the relationship between void magic and spirit channeling",
            "go north",
            "What kind of preparation is needed for advanced transmutation rituals"
        ]
        
        print("Testing Enhanced RAG Integration:")
        print("=" * 50)
        
        for test_input in test_cases:
            print(f"\nInput: '{test_input}'")
            
            # Test the enhanced RAG analysis
            rag_result = patched_parser._extract_intents_with_rag(test_input)
            
            print(f"  RAG Triggered: {rag_result.get('triggered', False)}")
            print(f"  Confidence: {rag_result.get('confidence', 0.0):.3f}")
            print(f"  Trigger Reason: {rag_result.get('trigger_reason', 'N/A')}")
            
            if rag_result.get("enhanced_intent"):
                print(f"  Enhanced Intent: {rag_result['enhanced_intent'][:100]}...")
        
        print(f"\n✅ Enhanced RAG patch test completed successfully")
        
    except Exception as e:
        print(f"❌ Enhanced RAG patch test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_enhanced_rag_patch()
