#!/usr/bin/env python3
"""
Patch script for fixing AI GM Brain imports.

This script modifies the AI GM components to use absolute imports
rather than relative imports, making them more compatible with
different execution contexts.
"""

import os
import sys
import re
import fileinput
from pathlib import Path

def patch_file(file_path, search_pattern, replacement):
    """Patch a file by replacing text matching a pattern."""
    print(f"Patching {file_path}...")
    
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Make the replacement
    new_content = re.sub(search_pattern, replacement, content)
    
    # Only write if changed
    if new_content != content:
        with open(file_path, 'w') as file:
            file.write(new_content)
        print(f"✅ Successfully patched {file_path}")
        return True
    else:
        print(f"⚠️ No changes made to {file_path}")
        return False

def patch_ai_gm_brain():
    """Patch AI GM Brain file to use absolute imports."""
    brain_path = os.path.join("backend", "src", "ai_gm", "ai_gm_brain.py")
    
    if not os.path.exists(brain_path):
        print(f"❌ File not found: {brain_path}")
        return False
    
    # Replace relative imports with absolute imports
    changes = [
        (
            r"from \.\.(events\.event_bus) import", 
            r"from backend.src.events.event_bus import"
        ),
        (
            r"from \.\.(memory\.memory_manager) import", 
            r"from backend.src.memory.memory_manager import"
        ),
        (
            r"from \.\.(text_parser) import", 
            r"from backend.src.text_parser import"
        )
    ]
    
    success = True
    for pattern, replacement in changes:
        if not patch_file(brain_path, pattern, replacement):
            success = False
    
    return success

def patch_world_reaction():
    """Patch World Reaction Integration file."""
    file_path = os.path.join("backend", "src", "ai_gm", "world_reaction_integration.py")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Add missing enum import
    pattern = r"import sys\nimport time"
    replacement = r"import sys\nimport time\nfrom enum import Enum, auto"
    
    success = patch_file(file_path, pattern, replacement)
    
    # Add fallback enum definitions
    pattern = r"except ImportError:[\s\S]+?WORLD_REACTION_AVAILABLE = False"
    replacement = r"""except ImportError:
    WORLD_REACTION_AVAILABLE = False
    print("World reaction system components not available.")
    
    # Define fallback enums
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
        CRITICAL = auto()"""
    
    if not patch_file(file_path, pattern, replacement):
        success = False
        
    return success

def patch_ai_gm_integration():
    """Patch AI GM Integration file."""
    file_path = os.path.join("backend", "src", "ai_gm", "ai_gm_integration.py")
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Fix import to use try/except pattern
    pattern = r"from backend\.src\.ai_gm\.world_reaction_integration import"
    replacement = r"""try:
    from .world_reaction_integration import
except ImportError:
    try:
        from backend.src.ai_gm.world_reaction_integration import"""
    
    success = patch_file(file_path, pattern, replacement)
    
    # Add missing exception handling for imports
    pattern = r"attach_world_reaction"
    replacement = r"""attach_world_reaction
    except ImportError:
        print("Warning: Could not import world_reaction_integration")
        WorldReactionIntegration = None
        attach_world_reaction = None"""
    
    if not patch_file(file_path, pattern, replacement):
        success = False
        
    return success

def create_integration_init():
    """Create an __init__.py file to help with imports."""
    init_path = os.path.join("backend", "src", "ai_gm", "__init__.py")
    
    if not os.path.exists(init_path):
        with open(init_path, 'w') as f:
            f.write("""# AI GM package initialization
# This file helps with imports and package structure

# Import common enums and types
from enum import Enum, auto

# Define common enums used across multiple modules
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
        return True
    else:
        print(f"⚠️ File already exists: {init_path}")
        return False

def create_absolute_import_file():
    """Create a helper file to make absolute imports work."""
    file_path = os.path.join("backend", "src", "ai_gm", "ai_gm_import_helper.py")
    
    content = """# AI GM import helper
# This file provides alternative import methods to help with different execution contexts

import os
import sys
import importlib.util
from pathlib import Path
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

# Common enums that might be needed across modules
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

class ProcessingMode(Enum):
    NORMAL = auto()
    OOC = auto()
    SYSTEM = auto()
    AMBIENT = auto()

class InputComplexity(Enum):
    SIMPLE_COMMAND = auto()
    COMPLEX_COMMAND = auto()
    CONVERSATION = auto()
    COMPLEX_QUERY = auto()
    OOC_COMMAND = auto()

def import_module(module_path: str, package_name: str = None):
    """Dynamically import a module by path."""
    try:
        # Try standard import first
        if package_name:
            return importlib.import_module(module_path, package=package_name)
        else:
            return importlib.import_module(module_path)
    except ImportError:
        # Fall back to spec-based import
        try:
            module_name = module_path.split('.')[-1]
            file_path = None
            
            # Try to find the module file
            search_paths = sys.path.copy()
            search_paths.append(os.path.dirname(os.path.dirname(__file__)))
            
            for path in search_paths:
                candidate = os.path.join(path, *module_path.split('.')) + '.py'
                if os.path.exists(candidate):
                    file_path = candidate
                    break
            
            if file_path and os.path.exists(file_path):
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
            else:
                raise ImportError(f"Could not find module file for {module_path}")
        except Exception as e:
            print(f"Error importing {module_path}: {e}")
            return None

# Example usage:
# event_bus_module = import_module('backend.src.events.event_bus')
# if event_bus_module:
#     event_bus = event_bus_module.event_bus
#     EventType = event_bus_module.EventType
"""
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Created helper file at {file_path}")
    return True

def main():
    """Main patch application function."""
    print("🔧 AI GM Integration Patch Script")
    print("=" * 60)
    
    # Ensure we're in the right directory
    textrealms_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(textrealms_dir)
    
    # Create init file
    create_integration_init()
    
    # Create import helper
    create_absolute_import_file()
    
    # Apply patches
    brain_success = patch_ai_gm_brain()
    world_success = patch_world_reaction()
    integration_success = patch_ai_gm_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Patch Results")
    print("=" * 60)
    print(f"AI GM Brain patch:           {'✅ SUCCESS' if brain_success else '❌ FAILED'}")
    print(f"World Reaction patch:        {'✅ SUCCESS' if world_success else '❌ FAILED'}")
    print(f"Integration patch:           {'✅ SUCCESS' if integration_success else '❌ FAILED'}")
    
    overall = brain_success and world_success and integration_success
    print(f"\nOverall Result: {'✅ COMPLETE' if overall else '⚠️ PARTIAL'}")
    
    return 0 if overall else 1

if __name__ == "__main__":
    sys.exit(main())
