import sys
import os
import logging
from dataclasses import asdict

# Adjust the Python path to include the project's root 'src' directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from text_parser.parser_engine import ParserEngine

# Setup basic logging to see output from ParserEngine
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# For more detailed logs from ParserEngine specifically:
logging.getLogger('text_parser.parser_engine').setLevel(logging.DEBUG)

def run_enhanced_rag_tests():
    """Tests designed to trigger RAG analysis with complex, ambiguous inputs."""
    logger.info("Initializing ParserEngine for enhanced RAG testing...")
    
    # Ensure necessary environment variables are set
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY environment variable not set. LLM calls may fail.")

    try:
        parser = ParserEngine()
        logger.info("ParserEngine initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize ParserEngine: {e}", exc_info=True)
        return

    # Enhanced test inputs designed to trigger RAG analysis
    # These are longer (>3 words), ambiguous, and relate to knowledge base content
    enhanced_rag_inputs = [
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
        
        # Vague exploration and discovery intents
        "I feel drawn to explore areas where ancient magic still lingers in the environment",
        "Something tells me there are hidden secrets related to the old civilization in this region",
        "I have a strong intuition that there's more to discover about the mystical properties of this place",
        "My character senses that understanding the local lore might reveal important magical knowledge here",
        
        # Open-ended character development goals
        "I want my character to become someone who bridges the gap between scholarly knowledge and practical application",
        "Help me understand what path would lead to mastering both combat effectiveness and magical versatility",
        "I'm interested in developing abilities that would make me respected among both warriors and mages",
        "My goal is to become the kind of person who can solve problems using unconventional magical approaches",
        
        # Narrative-style queries requiring interpretation
        "Tell me what I should know about the ancient conflicts between different schools of magic",
        "I'd like to learn about the historical significance of magical artifacts in shaping political power",
        "What can you tell me about the role that magical practitioners played in the great wars",
        "I'm interested in understanding how magical knowledge was preserved and passed down through generations",
        
        # Philosophical and ethical magical questions
        "I'm struggling with the moral implications of using mind-affecting magic on other people",
        "What are the ethical considerations around binding elemental spirits for personal magical power",
        "I need to understand the balance between pursuing magical knowledge and maintaining personal integrity",
        "How do I reconcile my desire for magical power with my commitment to protecting innocent people",
        
        # Complex situational queries
        "I find myself in a situation where normal magical approaches don't seem to be working as expected",
        "Something strange is happening with my magical abilities and I need to figure out what's causing it",
        "The magical energies in this area feel different somehow and I want to understand why",
        "I'm experiencing magical phenomena that don't match anything I've learned about in my studies",
        
        # Interdisciplinary magical knowledge requests
        "I want to understand how herbalism knowledge can enhance my understanding of potion brewing techniques",
        "What connections exist between understanding celestial movements and improving divination magic accuracy",
        "How does knowledge of ancient languages help with deciphering magical texts and inscriptions",
        "I'm curious about the relationship between musical theory and the casting of harmonic spell patterns"
    ]

    logger.info("\n--- Starting Enhanced RAG Analysis Tests ---")
    logger.info(f"Testing {len(enhanced_rag_inputs)} complex inputs designed to trigger RAG analysis")
    
    rag_triggered_count = 0
    high_confidence_rag_count = 0
    
    for i, text_input in enumerate(enhanced_rag_inputs, 1):
        logger.info(f"\n[Test {i:2d}/32] Testing: '{text_input[:60]}{'...' if len(text_input) > 60 else ''}'")
        logger.info(f"              Full input: '{text_input}'")
        
        try:
            parsed_command = parser.parse(text_input)
            if parsed_command:
                logger.info(f"  ✅ Parsed successfully")
                logger.info(f"     Action: {parsed_command.action}")
                logger.info(f"     Target: {parsed_command.target}")
                logger.info(f"     Confidence: {parsed_command.confidence:.3f}")
                
                # Check for RAG analysis
                if "rag_intent_analysis" in parsed_command.context:
                    rag_triggered_count += 1
                    rag_data = parsed_command.context["rag_intent_analysis"]
                    
                    logger.info(f"     🔮 RAG Analysis TRIGGERED (High Confidence)")
                    logger.info(f"        RAG Confidence: {rag_data.get('confidence', 0):.3f}")
                    logger.info(f"        Context Count: {rag_data.get('context_count', 0)}")
                    logger.info(f"        Max Relevance: {rag_data.get('max_relevance', 0):.3f}")
                    
                    if rag_data.get('confidence', 0) > 0.7:
                        high_confidence_rag_count += 1
                        logger.info(f"        ⭐ HIGH CONFIDENCE RAG ANALYSIS")
                    
                    # Show enhanced intent if available
                    enhanced_intent = rag_data.get('enhanced_intent', '')
                    if enhanced_intent and len(enhanced_intent) > 10:
                        logger.info(f"        Enhanced Intent: {enhanced_intent[:100]}...")
                        
                elif "rag_intent_analysis_fallback" in parsed_command.context:
                    logger.info(f"     🔽 RAG Analysis (Fallback/Low Confidence)")
                    fallback_data = parsed_command.context["rag_intent_analysis_fallback"]
                    logger.info(f"        Fallback Confidence: {fallback_data.get('confidence', 0):.3f}")
                else:
                    logger.info(f"     📝 Traditional parsing used (no RAG analysis)")
                    
                # Check word count to verify triggering condition
                word_count = len(text_input.split())
                logger.info(f"     Word count: {word_count} ({'✓' if word_count > 3 else '✗'} meets >3 requirement)")
                
            else:
                logger.warning(f"  ❌ Parse failed")
                
        except Exception as e:
            logger.error(f"  💥 Error: {e}", exc_info=True)
        
        logger.info("  " + "-" * 50)

    # Summary statistics
    logger.info(f"\n🎯 === ENHANCED RAG TEST SUMMARY ===")
    logger.info(f"Total inputs tested: {len(enhanced_rag_inputs)}")
    logger.info(f"RAG analysis triggered: {rag_triggered_count}")
    logger.info(f"High confidence RAG (>0.7): {high_confidence_rag_count}")
    logger.info(f"RAG trigger rate: {(rag_triggered_count/len(enhanced_rag_inputs)*100):.1f}%")
    logger.info(f"High confidence rate: {(high_confidence_rag_count/len(enhanced_rag_inputs)*100):.1f}%")
    
    if rag_triggered_count > 0:
        logger.info(f"\n✅ SUCCESS: RAG analysis is working and being triggered by complex inputs!")
    else:
        logger.warning(f"\n⚠️  RAG analysis was not triggered. Check:")
        logger.warning(f"   - RAG components initialization")
        logger.warning(f"   - Traditional parser confidence levels")
        logger.warning(f"   - Input complexity and ambiguity")

if __name__ == "__main__":
    run_enhanced_rag_tests()
