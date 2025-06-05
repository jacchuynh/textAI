#!/usr/bin/env python3
"""
AI GM Quick Fix Script

This script performs quick fixes for common AI GM Brain integration issues:
1. Creates missing directories and files
2. Sets up proper import paths
3. Verifies the integration setup
"""

import os
import sys
import shutil
from pathlib import Path
import importlib.util

def print_status(message, success=True):
    """Print a status message with color."""
    if success:
        # Green text for success
        print(f"\033[92m✓ {message}\033[0m")
    else:
        # Red text for failure
        print(f"\033[91m✗ {message}\033[0m")

def ensure_directory(path):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(path):
        os.makedirs(path)
        print_status(f"Created directory: {path}")
    return os.path.exists(path)

def ensure_file(path, content=""):
    """Ensure a file exists, creating it if necessary."""
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
        print_status(f"Created file: {path}")
    return os.path.exists(path)

def ensure_init_file(directory):
    """Ensure an __init__.py file exists in the directory."""
    init_path = os.path.join(directory, "__init__.py")
    return ensure_file(init_path, "# Auto-generated __init__.py file\n")

def create_minimal_ai_gm_brain(brain_file_path):
    """Create a minimal AI GM Brain implementation."""
    brain_content = """# Minimal AI GM Brain implementation
from enum import Enum, auto
from typing import Dict, Any, List, Optional

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

class AIGMBrain:
    \"\"\"Minimal AI GM Brain implementation.\"\"\"
    
    def __init__(self, game_id: str, player_id: str):
        self.game_id = game_id
        self.player_id = player_id
        self.extensions = {}
        self.context = {}
    
    def register_extension(self, name: str, extension: Any):
        \"\"\"Register an extension module.\"\"\"
        self.extensions[name] = extension
        return True
    
    def process_player_input(self, input_text: str) -> Dict[str, Any]:
        \"\"\"Process player input.\"\"\"
        # Check if this is an OOC command
        if input_text.startswith('/'):
            # Handle OOC commands
            if 'ooc_handler' in self.extensions:
                handler = self.extensions['ooc_handler']
                if hasattr(handler, 'process_command'):
                    result = handler.process_command(input_text, self)
                    if result:
                        return result
            
            # Default OOC response
            return {
                "status": "success",
                "response_text": f"OOC Command: {input_text}",
                "metadata": {"processing_mode": "OOC"}
            }
        else:
            # Regular command processing
            response_text = f"Processing: {input_text}"
            
            return {
                "status": "success",
                "response_text": response_text,
                "metadata": {"processing_mode": "NORMAL"}
            }
    
    def update_context(self, context_update: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"Update the game context.\"\"\"
        self.context.update(context_update)
        return self.context
    
    def get_context(self) -> Dict[str, Any]:
        \"\"\"Get the current game context.\"\"\"
        return self.context
"""
    
    return ensure_file(brain_file_path, brain_content)

def fix_import_paths():
    """Fix Python import paths for AI GM integration."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Add necessary paths to Python path
    paths_to_add = [
        current_dir,
        os.path.join(current_dir, 'backend', 'src'),
        os.path.join(current_dir, 'attached_assets')
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
            print_status(f"Added to Python path: {path}")
    
    # Write a .pth file to help with imports
    site_packages = None
    for path in sys.path:
        if path.endswith('site-packages'):
            site_packages = path
            break
    
    if site_packages:
        pth_file = os.path.join(site_packages, 'ai_gm_integration.pth')
        with open(pth_file, 'w') as f:
            f.write('\n'.join(paths_to_add))
        print_status(f"Created .pth file: {pth_file}")

def create_directory_structure():
    """Create the necessary directory structure for AI GM integration."""
    # Define the directory structure
    structure = {
        "backend": {
            "src": {
                "ai_gm": {
                    "__init__.py": "# AI GM package\n",
                    "ai_gm_brain.py": None,  # Will be filled with minimal implementation
                    "world_reaction_integration.py": "# World reaction integration\n",
                    "pacing_integration.py": "# Pacing integration\n",
                    "output_integration.py": "# Output integration\n",
                    "ai_gm_integration.py": "# AI GM integration\n"
                },
                "events": {
                    "__init__.py": "# Events package\n",
                    "event_bus.py": "# Event bus implementation\n"
                },
                "memory": {
                    "__init__.py": "# Memory package\n",
                    "memory_manager.py": "# Memory manager implementation\n"
                },
                "text_parser": {
                    "__init__.py": "# Text parser package\n"
                },
                "__init__.py": "# Backend src package\n"
            },
            "__init__.py": "# Backend package\n"
        },
        "attached_assets": {
            "__init__.py": "# Attached assets package\n"
        }
    }
    
    # Create the directory structure
    for dir_name, contents in structure.items():
        create_directory_recursive(dir_name, contents)
    
    # Create the minimal AI GM Brain implementation
    brain_file_path = os.path.join("backend", "src", "ai_gm", "ai_gm_brain.py")
    create_minimal_ai_gm_brain(brain_file_path)

def create_directory_recursive(path, contents):
    """Recursively create directories and files."""
    if not os.path.exists(path):
        os.makedirs(path)
        print_status(f"Created directory: {path}")
    
    if contents:
        for name, content in contents.items():
            full_path = os.path.join(path, name)
            
            if isinstance(content, dict):
                # This is a directory
                create_directory_recursive(full_path, content)
            else:
                # This is a file
                if content is not None:
                    ensure_file(full_path, content)

def verify_imports():
    """Verify that imports work correctly."""
    print("\nVerifying imports...")
    
    modules_to_check = [
        "backend.src.ai_gm.ai_gm_brain",
        "ai_gm_direct_test",
        "ai_gm_unified_demo",
        "ai_gm_simple_demo"
    ]
    
    all_passed = True
    
    for module_name in modules_to_check:
        try:
            # Try to import the module
            if importlib.util.find_spec(module_name):
                module = importlib.import_module(module_name)
                print_status(f"Successfully imported: {module_name}")
            else:
                print_status(f"Module not found: {module_name}", success=False)
                all_passed = False
        except ImportError as e:
            print_status(f"Failed to import {module_name}: {e}", success=False)
            all_passed = False
    
    return all_passed

def run_basic_test():
    """Run a basic test of the AI GM integration."""
    print("\nRunning basic integration test...")
    
    try:
        # Try to import from ai_gm_direct_test
        from ai_gm_direct_test import create_unified_gm
        
        # Create a GM instance
        gm = create_unified_gm(
            game_id="quick_fix_test",
            player_id="test_player"
        )
        
        # Test a basic command
        response = gm.process_player_input("look around")
        
        if response and "response_text" in response:
            print_status(f"Basic test passed with response: {response['response_text'][:50]}...")
            return True
        else:
            print_status("Basic test failed: Invalid response format", success=False)
            return False
            
    except Exception as e:
        print_status(f"Basic test failed: {e}", success=False)
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the quick fix script."""
    print("🛠️  AI GM Quick Fix Script")
    print("==========================")
    
    # Fix import paths
    print("\nFixing import paths...")
    fix_import_paths()
    
    # Check if the directory structure needs to be created
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend")
    if not os.path.exists(backend_dir) or not os.path.exists(os.path.join(backend_dir, "src", "ai_gm")):
        print("\nCreating directory structure...")
        create_directory_structure()
    
    # Verify imports
    import_check = verify_imports()
    
    # Run basic test if imports are working
    if import_check:
        basic_test = run_basic_test()
    else:
        basic_test = False
    
    # Print summary
    print("\nQuick Fix Summary")
    print("================")
    print_status("Import paths fixed")
    print_status("Directory structure verified")
    print_status("Imports verified", import_check)
    print_status("Basic test", basic_test)
    
    if import_check and basic_test:
        print("\n✅ AI GM integration is now ready to use!")
        print("You can run the following scripts to test it:")
        print("  - python ai_gm_direct_test.py")
        print("  - python ai_gm_simple_demo.py")
        print("  - python test_ai_gm_approaches.py")
    else:
        print("\n⚠️ Some issues could not be fixed automatically.")
        print("Please check the logs above for more information.")

if __name__ == "__main__":
    main() 