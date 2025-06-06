#!/usr/bin/env python3
"""
Test RAG functionality without requiring OpenRouter API key.
This demonstrates that the ChromaDB + SentenceTransformers integration is working.
"""
import sys
import os
import logging

# Add the backend source to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from text_parser.parser_engine import ParserEngine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_retrieval():
    """Test just the RAG retrieval functionality without LLM calls."""
    
    # Initialize parser
    parser = ParserEngine()
    
    if not parser.rag_available:
        print("❌ RAG not available")
        return
    
    print("✅ RAG components initialized successfully")
    print(f"📚 Knowledge base: {parser.knowledge_collection.count()} documents")
    
    # Test RAG retrieval directly
    test_queries = [
        "What materials do I need for crafting magical weapons?",
        "Tell me about fire crystals and their properties",
        "How do I forge enchanted armor?",
        "What creatures live in the deep forests?",
        "Ancient sword legends and artifacts"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Test direct RAG method
        rag_result = parser._extract_intents_with_rag(query)
        
        if rag_result.get("rag_available"):
            print(f"   Intent: {rag_result.get('enhanced_intent', 'Unknown')}")
            print(f"   Confidence: {rag_result.get('confidence', 0):.2f}")
            print(f"   Context count: {rag_result.get('context_count', 0)}")
            
            # Show top relevant context
            relevant_context = rag_result.get('relevant_context', [])
            if relevant_context:
                print("   📖 Top relevant context:")
                for i, ctx in enumerate(relevant_context[:2]):  # Show top 2
                    print(f"      {i+1}. {ctx['text'][:100]}... (relevance: {ctx['relevance_score']:.2f})")
        else:
            print(f"   ❌ RAG failed: {rag_result.get('reason', 'Unknown error')}")

if __name__ == "__main__":
    test_rag_retrieval()
