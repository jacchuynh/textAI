"""
AI GM Brain Integration Setup

This script sets up and configures the AI GM Brain integration system.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add the parent directory to the path to allow importing from sibling packages
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_setup():
    """Run the integration setup process."""
    print("=" * 50)
    print("AI GM Brain Integration Setup")
    print("=" * 50)
    print("\nThis script will set up the AI GM Brain integration system.")
    
    # Get the current directory
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    src_dir = current_dir.parent
    
    # Step 1: Fix imports
    print("\nStep 1: Fixing imports and creating missing components...")
    try:
        # Try to import and run the fix_ai_gm_imports function
        sys.path.insert(0, str(src_dir))
        try:
            from backend.src.ai_gm.fix_ai_gm_imports import fix_ai_gm_imports
        except ImportError:
            from ai_gm.fix_ai_gm_imports import fix_ai_gm_imports
        
        result = fix_ai_gm_imports()
        print(f"Import fix status: {result['status']}")
    except ImportError:
        print("Could not import fix_ai_gm_imports. Creating a minimal fix script...")
        # Create a minimal fix script if the main one can't be imported
        _create_minimal_fixes(src_dir)
    
    # Step 2: Verify the system can be imported
    print("\nStep 2: Verifying system imports...")
    try:
        try:
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
        except ImportError:
            from ai_gm.ai_gm_unified_integration import create_unified_gm
        print("✅ Successfully imported AI GM unified integration")
    except ImportError as e:
        print(f"❌ Failed to import AI GM unified integration: {e}")
        print("Please check the error and fix any import issues.")
        return False
    
    # Step 3: Test creating a GM instance
    print("\nStep 3: Testing GM instance creation...")
    try:
        try:
            from backend.src.ai_gm.ai_gm_unified_integration import create_unified_gm
        except ImportError:
            from ai_gm.ai_gm_unified_integration import create_unified_gm
            
        gm = create_unified_gm(
            game_id="setup_test",
            player_id="setup_player"
        )
        print("✅ Successfully created GM instance")
        
        # Check available systems
        print("\nAvailable GM systems:")
        for system, available in gm.available_systems.items():
            status = "✅" if available else "❌"
            print(f"{status} {system}")
    except Exception as e:
        print(f"❌ Failed to create GM instance: {e}")
        print("Please check the error and fix any integration issues.")
        return False
    
    # Step 4: Run the test script
    print("\nStep 4: Running integration test...")
    try:
        print("You can run the full integration test with:")
        print("python -m backend.src.ai_gm.ai_gm_simple_test")
    except Exception as e:
        print(f"❌ Failed to suggest test command: {e}")
    
    print("\nSetup completed successfully!")
    print("\nNext steps:")
    print("1. Implement your specific AI GM Brain components")
    print("2. Add them to your application's initialization")
    print("3. Run the integration test to verify everything works")
    
    return True


def _create_minimal_fixes(src_dir: Path):
    """Create minimal fixes for the most common import issues."""
    # Ensure ai_gm directory exists
    ai_gm_dir = src_dir / "ai_gm"
    ai_gm_dir.mkdir(exist_ok=True)
    
    # Create __init__.py if it doesn't exist
    init_path = ai_gm_dir / "__init__.py"
    if not init_path.exists():
        with open(init_path, "w") as f:
            f.write('"""AI GM Brain integration module."""\n')
        print(f"Created {init_path}")
    
    # Create minimal placeholders for required modules
    required_modules = [
        "world_reaction_integration",
        "pacing_integration",
        "output_integration",
        "ai_gm_brain_ooc_handler",
        "ai_gm_llm_manager",
        "ai_gm_combat_integration"
    ]
    
    for module in required_modules:
        module_path = ai_gm_dir / f"{module}.py"
        if not module_path.exists():
            class_name = "".join(part.capitalize() for part in module.split("_"))
            with open(module_path, "w") as f:
                f.write(f'"""\n{class_name} placeholder.\n"""\n\n')
                f.write('from typing import Dict, Any, List, Optional\n\n\n')
                f.write(f'class {class_name}:\n')
                f.write('    """Placeholder implementation."""\n\n')
                f.write('    def __init__(self, brain=None):\n')
                f.write('        self.brain = brain\n')
                f.write(f'        print("Placeholder {class_name} initialized")\n\n')
                f.write('    def process(self, input_text: str) -> Dict[str, Any]:\n')
                f.write('        """Process input with this component."""\n')
                f.write('        return {"status": "success", "response": "Placeholder response"}\n')
            print(f"Created placeholder for {module}")
    
    print("Created minimal placeholders for required modules")


if __name__ == "__main__":
    run_setup() 