#!/usr/bin/env python3
"""
Enhanced RAG System Testing with Optimization Modules

This script tests the optimized RAG system using the enhanced_rag_optimizer
and rag_integration_patch modules to validate improved trigger rates.
"""

import sys
import os
import logging
from dataclasses import asdict
from typing import Dict, List, Any

# Adjust the Python path to include the project's root 'src' directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from text_parser.parser_engine import ParserEngine
from text_parser.enhanced_rag_optimizer import EnhancedRAGOptimizer, RAGOptimizationConfig
from text_parser.rag_integration_patch import RAGIntegrationPatch
from text_parser.enhanced_rag_parser_integration import EnhancedRAGParserIntegration

# Setup detailed logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Enable debug logging for RAG components
logging.getLogger('text_parser.parser_engine').setLevel(logging.DEBUG)
logging.getLogger('text_parser.rag_optimizer').setLevel(logging.DEBUG)
logging.getLogger('text_parser.rag_patch').setLevel(logging.DEBUG)

def get_enhanced_test_inputs():
    """Get the same test inputs used in the original RAG testing."""
    return [
        # Ambiguous magical queries requiring deep understanding
        "I need to understand the essence behind elemental binding magic",
        "What kind of preparation is needed for advanced transmutation rituals",
        "Help me figure out the relationship between void magic and spirit channeling",
        "Can you explain the interaction between celestial alignments and arcane power",
        "I'm curious about the connection between ancient runes and modern enchantment techniques",
        
        # Complex crafting scenarios
        "I want to create something that combines both metal working and magical infusion techniques",
        "How should I approach crafting items that require multiple rare material components together",
        "What would be the best method for enhancing weapon durability using both physical and magical means",
        "I need guidance on combining alchemy principles with traditional blacksmithing approaches for better results",
        "Can you help me understand the process of embedding elemental stones into crafted armor pieces",
        
        # Character development and relationship queries
        "How do I build meaningful relationships with NPCs while maintaining my character's moral compass",
        "What are the long-term consequences of choosing dark magic paths versus light magic in character development",
        "I want to understand how different conversation choices affect my character's reputation across various factions",
        "How should I balance exploring dangerous areas while keeping my companions safe and happy",
        "What strategies work best for managing multiple questlines without conflicting story elements",
        
        # Meta-gaming and system understanding
        "I'm trying to understand the underlying mechanics that govern magic resistance calculations in combat",
        "How do environmental factors actually influence the success rates of different types of spells",
        "What are the hidden relationships between character stats and dialogue options availability",
        "Can you explain how the game's economy system determines pricing for rare magical components",
        "I need help understanding how skill synergies work across different character advancement trees",
        
        # Exploration and world-building questions
        "What should I know about the lore connections between different regions before exploring them",
        "How do I prepare for expeditions into areas where traditional magic might not work properly",
        "I want to understand the cultural significance of ancient sites before disturbing them during exploration",
        "What are the environmental storytelling clues I should watch for in abandoned magical locations",
        "How do I respectfully interact with different magical creature communities I encounter while exploring",
        
        # Problem-solving and creative scenarios
        "I'm stuck trying to solve a puzzle that seems to require both magical knowledge and practical engineering",
        "How can I creatively use my current abilities to overcome obstacles I wasn't specifically trained for",
        "What unconventional approaches might work for situations where standard magical solutions have failed",
        "I need ideas for how to approach diplomatic situations between conflicting magical and non-magical communities",
        "Can you suggest creative ways to use common magical items for purposes they weren't originally designed for",
        
        # Edge cases and boundary testing
        "Short query about magic",  # Short but relevant
        "Magic help please",  # Very short
        "What is magic exactly and how does it work in this world"  # Clear but broad
    ]

def test_optimizer_directly():
    """Test the RAG optimizer directly to understand its decision-making."""
    logger.info("=" * 60)
    logger.info("TESTING RAG OPTIMIZER DIRECTLY")
    logger.info("=" * 60)
    
    optimizer = EnhancedRAGOptimizer()
    test_inputs = get_enhanced_test_inputs()
    
    trigger_count = 0
    high_priority_count = 0
    
    for i, text in enumerate(test_inputs, 1):
        # Test with different confidence levels
        for conf in [0.9, 0.7, 0.5, 0.3]:
            should_trigger, reason, priority = optimizer.should_trigger_rag(text, conf)
            
            logger.info(f"Test {i} (conf={conf}): '{text[:50]}...'")
            logger.info(f"  Trigger: {should_trigger}, Reason: {reason}, Priority: {priority:.3f}")
            
            if should_trigger:
                trigger_count += 1
                if priority >= 0.7:
                    high_priority_count += 1
            break  # Only test with the first confidence level for summary
    
    logger.info(f"\nOptimizer Direct Test Results:")
    logger.info(f"Total tests: {len(test_inputs)}")
    logger.info(f"RAG triggers: {trigger_count} ({trigger_count/len(test_inputs)*100:.1f}%)")
    logger.info(f"High priority: {high_priority_count} ({high_priority_count/len(test_inputs)*100:.1f}%)")

def test_integrated_rag_system():
    """Test the full integrated RAG system with optimization patches."""
    logger.info("=" * 60)
    logger.info("TESTING INTEGRATED OPTIMIZED RAG SYSTEM")
    logger.info("=" * 60)
    
    # Initialize ParserEngine and RAG patch
    try:
        parser = ParserEngine()
        logger.info("ParserEngine initialized successfully.")
        
        # Initialize RAG integration patch
        rag_patch = RAGIntegrationPatch(parser)
        logger.info("RAG integration patch initialized.")
        
        # Apply enhanced RAG integration patch (replaces core parse method)
        enhanced_integration = EnhancedRAGParserIntegration()
        enhanced_integration.apply_enhanced_integration_to_parser(parser)
        logger.info("Enhanced RAG integration patch applied.")
        
    except Exception as e:
        logger.error(f"Failed to initialize system: {e}", exc_info=True)
        return
    
    test_inputs = get_enhanced_test_inputs()
    
    results = {
        "total_tests": len(test_inputs),
        "rag_triggered": 0,
        "high_confidence_rag": 0,
        "traditional_parsing": 0,
        "hybrid_approach": 0,
        "detailed_results": []
    }
    
    for i, input_text in enumerate(test_inputs, 1):
        logger.info(f"\n--- Test {i}: '{input_text[:60]}...' ---")
        
        try:
            # Parse with the enhanced integrated system
            parse_result = parser.parse(input_text)
            
            # Check if RAG was actually used in the integrated system
            rag_was_used = False
            rag_confidence = 0.0
            final_confidence = getattr(parse_result, 'confidence', 0.5)
            
            # Check for RAG enhancement markers
            if hasattr(parse_result, 'rag_enhanced'):
                rag_was_used = parse_result.rag_enhanced
                rag_confidence = getattr(parse_result, 'rag_confidence', 0.0)
                logger.info(f"✅ RAG ENHANCED RESULT - RAG Confidence: {rag_confidence:.3f}, Final Confidence: {final_confidence:.3f}")
            elif hasattr(parse_result, 'context') and parse_result.context:
                # Check context for RAG usage indicators
                if 'rag_intent_analysis' in parse_result.context:
                    rag_was_used = True
                    rag_analysis = parse_result.context['rag_intent_analysis']
                    rag_confidence = rag_analysis.get('adjusted_confidence', rag_analysis.get('confidence', 0.0))
                    logger.info(f"✅ RAG CONTEXT FOUND - RAG Confidence: {rag_confidence:.3f}, Final Confidence: {final_confidence:.3f}")
                elif 'enhanced_rag_analysis' in parse_result.context:
                    enhanced_rag = parse_result.context['enhanced_rag_analysis']
                    if enhanced_rag.get('triggered', False):
                        rag_was_used = True
                        rag_confidence = enhanced_rag.get('adjusted_confidence', enhanced_rag.get('confidence', 0.0))
                        logger.info(f"✅ ENHANCED RAG FOUND - RAG Confidence: {rag_confidence:.3f}, Final Confidence: {final_confidence:.3f}")
            
            if not rag_was_used:
                logger.info(f"❌ Traditional parsing - Final Confidence: {final_confidence:.3f}")
            
            test_result = {
                "input": input_text,
                "rag_was_used": rag_was_used,
                "rag_confidence": rag_confidence,
                "final_confidence": final_confidence,
                "parse_result_type": type(parse_result).__name__ if parse_result else "None"
            }
            
            # Count results based on actual RAG usage
            if rag_was_used:
                results["rag_triggered"] += 1
                if rag_confidence >= 0.7:
                    results["high_confidence_rag"] += 1
            else:
                results["traditional_parsing"] += 1
            
            results["detailed_results"].append(test_result)
            
        except Exception as e:
            logger.error(f"Error in test {i}: {e}", exc_info=True)
            results["detailed_results"].append({
                "input": input_text,
                "error": str(e),
                "rag_was_used": False,
                "rag_confidence": 0.0,
                "final_confidence": 0.0
            })
            results["traditional_parsing"] += 1
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("INTEGRATED RAG SYSTEM TEST RESULTS")
    logger.info("=" * 60)
    
    total = results["total_tests"]
    logger.info(f"Total tests: {total}")
    logger.info(f"RAG triggered: {results['rag_triggered']} ({results['rag_triggered']/total*100:.1f}%)")
    logger.info(f"High confidence RAG: {results['high_confidence_rag']} ({results['high_confidence_rag']/total*100:.1f}%)")
    logger.info(f"Traditional parsing: {results['traditional_parsing']} ({results['traditional_parsing']/total*100:.1f}%)")
    
    return results

def compare_with_baseline():
    """Compare optimized results with baseline performance."""
    logger.info("\n" + "=" * 60)
    logger.info("PERFORMANCE COMPARISON")
    logger.info("=" * 60)
    
    # Baseline results from previous testing (from conversation summary)
    baseline = {
        "total_tests": 33,
        "rag_triggered": 3,  # 9.1%
        "high_confidence_rag": 2,  # 6.1%
    }
    
    logger.info("Baseline Performance (Original System):")
    logger.info(f"  RAG trigger rate: {baseline['rag_triggered']}/{baseline['total_tests']} = {baseline['rag_triggered']/baseline['total_tests']*100:.1f}%")
    logger.info(f"  High confidence rate: {baseline['high_confidence_rag']}/{baseline['total_tests']} = {baseline['high_confidence_rag']/baseline['total_tests']*100:.1f}%")
    
    # Run optimized test
    optimized_results = test_integrated_rag_system()
    
    if optimized_results:
        logger.info("\nOptimized Performance (Enhanced System):")
        total = optimized_results["total_tests"]
        rag_triggered = optimized_results["rag_triggered"]
        high_conf = optimized_results["high_confidence_rag"]
        
        logger.info(f"  RAG trigger rate: {rag_triggered}/{total} = {rag_triggered/total*100:.1f}%")
        logger.info(f"  High confidence rate: {high_conf}/{total} = {high_conf/total*100:.1f}%")
        
        # Calculate improvements
        trigger_improvement = (rag_triggered/total*100) - (baseline['rag_triggered']/baseline['total_tests']*100)
        confidence_improvement = (high_conf/total*100) - (baseline['high_confidence_rag']/baseline['total_tests']*100)
        
        logger.info(f"\nImprovement Analysis:")
        logger.info(f"  RAG trigger rate improvement: +{trigger_improvement:.1f} percentage points")
        logger.info(f"  High confidence rate improvement: +{confidence_improvement:.1f} percentage points")
        
        if trigger_improvement > 0:
            logger.info(f"  ✅ RAG triggering improved by {trigger_improvement:.1f}%")
        else:
            logger.info(f"  ❌ RAG triggering decreased by {abs(trigger_improvement):.1f}%")

def main():
    """Main test execution function."""
    logger.info("Starting Enhanced RAG System Testing")
    
    # Ensure environment is set up
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY environment variable not set. LLM calls may fail.")
    
    try:
        # Test 1: Direct optimizer testing
        test_optimizer_directly()
        
        # Test 2: Full integrated system testing
        test_integrated_rag_system()
        
        # Test 3: Performance comparison
        compare_with_baseline()
        
    except Exception as e:
        logger.error(f"Test execution failed: {e}", exc_info=True)
    
    logger.info("Enhanced RAG System Testing Complete")

if __name__ == "__main__":
    main()
