#!/usr/bin/env python3
"""
AI GM LLM Integration Setup Utility

This script helps set up and validate the OpenRouter API key for the AI GM LLM integration.
It also tests the LLM integration to ensure it's working properly.
"""

import os
import sys
import time
import logging
import traceback
import argparse
from datetime import datetime

try:
    # Try to import the AI GM LLM integration
    from ai_gm_unified_integration_full import create_ai_gm, check_openrouter_api_key
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False

def setup_api_key(api_key=None):
    """
    Set up the OpenRouter API key.
    
    Args:
        api_key: The API key to set. If None, will prompt for it.
    
    Returns:
        bool: Whether the API key was set successfully
    """
    if api_key is None:
        # Check if it's already set
        current_key = os.environ.get('OPENROUTER_API_KEY')
        if current_key:
            print(f"OpenRouter API key is already set: {current_key[:4]}...{current_key[-4:]}")
            response = input("Do you want to replace it? (y/N): ").strip().lower()
            if response != 'y':
                return True
        
        # Prompt for the API key
        api_key = input("Enter your OpenRouter API key: ").strip()
        if not api_key:
            print("No API key provided. Setup aborted.")
            return False
    
    # Set the API key in the environment
    os.environ['OPENROUTER_API_KEY'] = api_key
    print(f"OpenRouter API key set: {api_key[:4]}...{api_key[-4:]}")
    
    # Provide instructions for permanent setup
    print("\nTo make this permanent, add the following to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
    print(f"export OPENROUTER_API_KEY='{api_key}'")
    
    return True

def validate_integration():
    """
    Validate that the AI GM LLM integration is working properly.
    
    Returns:
        bool: Whether the integration is working properly
    """
    if not INTEGRATION_AVAILABLE:
        print("❌ AI GM LLM integration is not available!")
        print("Make sure the ai_gm_unified_integration_full.py file exists and is importable.")
        return False
    
    if not check_openrouter_api_key():
        print("❌ OpenRouter API key is not set! Use --setup to set it.")
        return False
    
    print("✅ OpenRouter API key is set!")
    
    # Create a minimal test AI GM
    print("Testing AI GM LLM integration...")
    try:
        gm = create_ai_gm(
            game_id="test_setup",
            player_id="test_player",
            initial_context={
                "player_name": "Tester",
                "location_name": "Test Area",
                "location_description": "A simple test environment."
            }
        )
        
        status = gm.get_system_status()
        print(f"✅ AI GM created successfully!")
        print(f"  LLM Support: {'Available' if status.get('llm_support', False) else 'Not Available'}")
        print(f"  OpenRouter API Key: {status.get('openrouter_api_key', 'Not Set')}")
        
        if not status.get('llm_support', False):
            print("❌ LLM support is not available in the AI GM!")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI GM LLM integration: {e}")
        traceback.print_exc()
        return False

def test_llm_response():
    """
    Test generating an LLM response.
    
    Returns:
        bool: Whether the test was successful
    """
    if not INTEGRATION_AVAILABLE:
        print("❌ AI GM LLM integration is not available!")
        return False
    
    if not check_openrouter_api_key():
        print("❌ OpenRouter API key is not set! Use --setup to set it.")
        return False
    
    print("Testing LLM response generation...")
    try:
        gm = create_ai_gm(
            game_id="test_llm",
            player_id="test_player",
            initial_context={
                "player_name": "Adventurer",
                "location_name": "Enchanted Grove",
                "location_description": "A serene grove with ancient trees and magical flowers.",
                "recent_events": ["You found a strange glowing mushroom"],
                "character_info": {
                    "domains": {
                        "Magic": 3,
                        "Nature": 4
                    }
                }
            }
        )
        
        print("Sending test command to LLM...")
        test_input = "examine the glowing mushroom"
        
        # Try to get the LLM manager directly
        try:
            llm_manager = gm.get_llm_manager()
            print("✅ Successfully retrieved LLM manager")
            
            if hasattr(llm_manager, 'api_key') and llm_manager.api_key:
                print("✅ LLM manager has API key configured")
            else:
                print("❌ LLM manager does not have API key configured!")
        except Exception as e:
            print(f"⚠️ Could not access LLM manager directly: {e}")
        
        # Process the test input
        print(f"\nSending command: '{test_input}'")
        response = gm.process_player_input(test_input)
        
        print("\nResponse received:")
        print(f"{response['response_text']}")
        
        if "error" in response:
            print(f"❌ Error in response: {response.get('error', 'Unknown error')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LLM response: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Set up and validate the AI GM LLM integration")
    parser.add_argument("--setup", action="store_true", help="Set up the OpenRouter API key")
    parser.add_argument("--key", help="Directly provide the OpenRouter API key")
    parser.add_argument("--validate", action="store_true", help="Validate the AI GM LLM integration")
    parser.add_argument("--test", action="store_true", help="Test generating an LLM response")
    args = parser.parse_args()
    
    print("=" * 60)
    print("AI GM LLM Integration Setup Utility")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Set up the API key if requested
    if args.setup or args.key:
        setup_api_key(args.key)
    
    # Validate the integration if requested
    if args.validate or not (args.setup or args.key or args.test):
        print("\nValidating AI GM LLM integration...")
        validate_integration()
    
    # Test the LLM response if requested
    if args.test:
        print("\nTesting LLM response generation...")
        test_llm_response()
    
    print("\nSetup utility completed!")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 