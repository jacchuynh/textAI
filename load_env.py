#!/usr/bin/env python3
"""
Load environment variables from .env file
"""

import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file"""
    env_path = Path("/Users/jacc/Downloads/TextRealmsAI/.env")
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print(f"✅ Loaded environment variables from {env_path}")
        return True
    else:
        print(f"❌ .env file not found at {env_path}")
        return False

if __name__ == "__main__":
    load_env()
    
    # Test if API key is loaded
    key = os.environ.get('OPENROUTER_API_KEY')
    if key:
        print(f"✅ OPENROUTER_API_KEY loaded (ends with: ...{key[-8:]})")
    else:
        print("❌ OPENROUTER_API_KEY not found")
