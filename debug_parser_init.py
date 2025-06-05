#!/usr/bin/env python3
"""
Debug ParserEngine EntityRuler initialization
"""

import sys
import os

# Add the backend source to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

import spacy

def test_parser_engine_init():
    print("Testing ParserEngine EntityRuler initialization...")
    
    # Simulate the exact ParserEngine initialization
    nlp = spacy.load("en_core_web_sm")
    print(f"Loaded spaCy model. Pipeline: {nlp.pipe_names}")
    
    # Remove existing entity_ruler if present to avoid conflicts
    if "entity_ruler" in nlp.pipe_names:
        nlp.remove_pipe("entity_ruler")
        print("Removed existing entity_ruler")
    
    # Add fresh EntityRuler
    try:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        print(f"Added EntityRuler. Pipeline: {nlp.pipe_names}")
        
        # Test the pattern initialization
        patterns = [
            {"label": "FANTASY_ITEM", "pattern": "Moonblade", "id": "item_moonblade"},
            {"label": "FANTASY_NPC", "pattern": "Selene", "id": "npc_selene"},
            {"label": "FANTASY_LOCATION", "pattern": "Ironroot Caverns", "id": "loc_ironroot"},
            {"label": "FANTASY_ITEM", "pattern": [{"LOWER": "vorpal"}, {"LOWER": "sword"}], "id": "item_vorpal_sword"},
        ]
        
        ruler.add_patterns(patterns)
        print(f"Added {len(patterns)} patterns successfully")
        
        # Test the parser engine import
        print("Testing ParserEngine import...")
        from text_parser.parser_engine import ParserEngine
        print("✓ ParserEngine imported successfully")
        
        # Test creating an instance
        print("Creating ParserEngine instance...")
        parser = ParserEngine()
        print("✓ ParserEngine created successfully")
        
        if parser.ruler:
            print("✓ EntityRuler is available in ParserEngine")
        else:
            print("✗ EntityRuler is NOT available in ParserEngine")
        
        return True
        
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_parser_engine_init()
