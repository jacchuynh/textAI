import sys
import os
import logging
from dataclasses import asdict

# Adjust the Python path to include the project's root 'src' directory
# This allows us to import modules from src (e.g., text_parser)
# Assumes this script is in backend/src/text_parser/
# and the main src directory is one level up from 'text_parser'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from text_parser.parser_engine import ParserEngine
# Assuming ParsedCommand is in parser_engine.py or accessible via this import path
# If ParsedCommand is elsewhere, adjust the import accordingly.
# from text_parser.models import ParsedCommand # Example if it's in models.py

# Setup basic logging to see output from ParserEngine
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# For more detailed logs from ParserEngine specifically:
logging.getLogger('text_parser.parser_engine').setLevel(logging.DEBUG)

def run_parser_tests():
    """Initializes ParserEngine and tests it with sample inputs."""
    logger.info("Initializing ParserEngine for testing...")
    
    # Ensure necessary environment variables are set (e.g., for OpenRouterLLM)
    if not os.getenv("OPENROUTER_API_KEY"):
        logger.warning("OPENROUTER_API_KEY environment variable not set. LLM calls may fail.")

    try:
        parser = ParserEngine()
        logger.info("ParserEngine initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize ParserEngine: {e}", exc_info=True)
        return

    sample_inputs = [
        "I want to find the ancient sword of Azmar.",
        "Look at the glowing inscription on the wall.",
        "Go north towards the Whispering Woods.",
        "Attack the goblin with my rusty dagger!",
        "Unequip my helmet.",
        "Talk to the merchant about the price of potions.",
        "Use the strange key on the ornate chest.",
        "What is the history of this cursed amulet?", # More open-ended, good for RAG
        "I feel like exploring the dark cave system.", # Goal-oriented
        "My character wants to become a master blacksmith.", # Long-term goal
        "Combine the blue flower with the red mushroom.", # Crafting-like intent
        "Give the guard a gold coin to let me pass."
    ]

    logger.info("\n--- Starting Parser Tests with RAG Integration ---")
    for text_input in sample_inputs:
        logger.info(f"\n>>> Testing input: '{text_input}'")
        try:
            parsed_command = parser.parse(text_input)
            if parsed_command:
                # Convert dataclass to dict for cleaner printing, if desired
                # Or print fields directly
                logger.info(f"Parsed Output: ")
                logger.info(f"  Action: {parsed_command.action}")
                logger.info(f"  Target: {parsed_command.target}")
                logger.info(f"  Modifiers: {parsed_command.modifiers}")
                logger.info(f"  Confidence: {parsed_command.confidence:.2f}")
                logger.info(f"  Raw Text: '{parsed_command.raw_text}'")
                # Check for RAG specific context
                if "rag_intent_analysis" in parsed_command.context:
                    logger.info("  RAG Analysis (High Confidence): Present")
                    # You can choose to print more details from rag_intent_analysis if needed
                    # e.g., logger.info(f"    Dominant Intent Category: {parsed_command.context['rag_intent_analysis']['dominant_intent']['category']}")
                elif "rag_intent_analysis_fallback" in parsed_command.context:
                    logger.info("  RAG Analysis (Fallback/Low Confidence): Present")
                else:
                    logger.info("  RAG Analysis: Not present or not triggered by this input.")
                
                # For very detailed inspection of the full context:
                # logger.debug(f"  Full Context: {asdict(parsed_command.context) if hasattr(parsed_command.context, '__dict__') else parsed_command.context}")

            else:
                logger.info("Parsed Output: None (Parser could not determine command)")
        except Exception as e:
            logger.error(f"Error parsing input '{text_input}': {e}", exc_info=True)
        logger.info("---")

if __name__ == "__main__":
    run_parser_tests()
