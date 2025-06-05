#!/usr/bin/env python3
"""
Debug spaCy EntityRuler initialization
"""

import spacy
from spacy.pipeline import EntityRuler

def test_entity_ruler():
    print("Testing spaCy EntityRuler initialization...")
    
    # Load spaCy model
    nlp = spacy.load("en_core_web_sm")
    print(f"Initial pipeline: {nlp.pipe_names}")
    
    # Remove existing entity_ruler if present
    if "entity_ruler" in nlp.pipe_names:
        nlp.remove_pipe("entity_ruler")
        print("Removed existing entity_ruler")
    
    # Add fresh EntityRuler
    try:
        ruler = nlp.add_pipe("entity_ruler", before="ner")
        print(f"Added EntityRuler successfully. Pipeline: {nlp.pipe_names}")
        
        # Test adding patterns
        patterns = [
            {"label": "FANTASY_ITEM", "pattern": "test sword", "id": "item_test_sword"},
            {"label": "FANTASY_NPC", "pattern": [{"LOWER": "test"}, {"LOWER": "npc"}], "id": "npc_test"}
        ]
        
        ruler.add_patterns(patterns)
        print(f"Added {len(patterns)} patterns successfully")
        
        # Test entity recognition
        text = "I want to take the test sword and talk to test npc"
        doc = nlp(text)
        
        print(f"Testing text: '{text}'")
        print("Entities found:")
        for ent in doc.ents:
            print(f"  - {ent.text} ({ent.label_})")
        
        print("EntityRuler test successful!")
        return True
        
    except Exception as e:
        print(f"EntityRuler test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_entity_ruler()
