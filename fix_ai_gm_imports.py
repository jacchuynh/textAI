#!/usr/bin/env python3
"""
AI GM Integration Patch

This script fixes import issues in the AI GM components.
"""

import os
import sys
import re

def create_init_file():
    """Create __init__.py for ai_gm package."""
    init_path = os.path.join("backend", "src", "ai_gm", "__init__.py")
    
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write("""# AI GM package initialization
from enum import Enum, auto

# Common enums for world reaction system
class ActionSignificance(Enum):
    MINOR = auto()
    MODERATE = auto()
    MAJOR = auto()
    CRITICAL = auto()

class ReputationLevel(Enum):
    HOSTILE = auto()
    UNFRIENDLY = auto()
    NEUTRAL = auto()
    FRIENDLY = auto()
    ALLIED = auto()
""")
        print(f"✅ Created {init_path}")
    else:
        print(f"⚠️ File already exists: {init_path}")

def patch_world_reaction():
    """Add missing enum definitions to world reaction."""
    file_path = os.path.join("backend", "src", "ai_gm", "world_reaction_integration.py")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, "r") as f:
        content = f.read()
    
    if "except ImportError:" in content:
        new_content = re.sub(
            r"except ImportError:.*?WORLD_REACTION_AVAILABLE = False",
            """except ImportError:
    WORLD_REACTION_AVAILABLE = False
    print("World reaction system components not available.")
    
    # Define fallbacks for missing imports
    class ReputationLevel(Enum):
        HOSTILE = auto()
        UNFRIENDLY = auto() 
        NEUTRAL = auto()
        FRIENDLY = auto()
        ALLIED = auto()
    
    class ActionSignificance(Enum):
        MINOR = auto()
        MODERATE = auto()
        MAJOR = auto() 
        CRITICAL = auto()""",
            content,
            flags=re.DOTALL
        )
        
        if new_content != content:
            with open(file_path, "w") as f:
                f.write(new_content)
            print(f"✅ Patched {file_path}")
        else:
            print(f"⚠️ No changes needed for {file_path}")

def main():
    """Main function."""
    print("🔧 AI GM Integration Patch")
    print("=" * 60)
    
    # Ensure we're in the project root
    if not os.path.exists(os.path.join("backend", "src", "ai_gm")):
        print("❌ Please run this script from the project root directory")
        return 1
    
    # Create __init__.py
    create_init_file()
    
    # Patch world reaction integration
    patch_world_reaction()
    
    print("\n✅ Patching completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
