#!/usr/bin/env python3
"""
Secure API Key Setup for TextRealmsAI Phase 3
This script helps you set up your OpenRouter API key securely.
"""

import os
import subprocess
import sys

def setup_openrouter_api_key():
    """Setup OpenRouter API key in environment"""
    print("=== OpenRouter API Key Setup ===\n")
    
    # Check if key is already set
    current_key = os.environ.get('OPENROUTER_API_KEY')
    if current_key:
        print(f"✓ OPENROUTER_API_KEY is already set (ends with: ...{current_key[-8:]})")
        return True
    
    print("OPENROUTER_API_KEY is not set in your environment.")
    print("\nFor security, please set it manually using one of these methods:")
    print("\n1. Temporary (current terminal session only):")
    print("   export OPENROUTER_API_KEY='your-api-key-here'")
    
    print("\n2. Permanent (add to ~/.zshrc):")
    print("   echo 'export OPENROUTER_API_KEY=\"your-api-key-here\"' >> ~/.zshrc")
    print("   source ~/.zshrc")
    
    print("\n3. Using a .env file (recommended for development):")
    print("   Create a .env file in the project root with:")
    print("   OPENROUTER_API_KEY=your-api-key-here")
    
    return False

def create_env_file_template():
    """Create a .env template file"""
    env_path = "/Users/jacc/Downloads/TextRealmsAI/.env.example"
    
    with open(env_path, 'w') as f:
        f.write("""# TextRealmsAI Environment Variables
# Copy this file to .env and add your actual API keys

# OpenRouter API Key for LangChain Phase 3 integration
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Other AI service keys
# OPENAI_API_KEY=your-openai-key-here
# ANTHROPIC_API_KEY=your-anthropic-key-here

# Database settings (if needed)
# DATABASE_URL=your-database-url-here
""")
    
    print(f"✓ Created .env.example template at: {env_path}")
    print("  Copy this to .env and add your actual API keys")

def test_api_key_access():
    """Test if the API key is accessible"""
    key = os.environ.get('OPENROUTER_API_KEY')
    if not key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    if key.startswith('sk-or-v1-'):
        print("✓ API key format looks correct")
        return True
    else:
        print("⚠ API key format may be incorrect (should start with 'sk-or-v1-')")
        return False

def main():
    print("Setting up secure API key configuration...\n")
    
    # Create .env template
    create_env_file_template()
    
    # Check current setup
    if setup_openrouter_api_key():
        print("\n=== Testing API Key ===")
        if test_api_key_access():
            print("\n✅ API key setup appears correct!")
            print("You can now run the Phase 3 tests with full LangChain functionality.")
        else:
            print("\n⚠ API key may need verification")
    else:
        print("\n📝 Please set up your API key using one of the methods above.")
        print("Then re-run this script to verify the setup.")

if __name__ == "__main__":
    main()
