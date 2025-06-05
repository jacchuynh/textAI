#!/usr/bin/env python3
"""
Integration Setup Script for TextRealmsAI

This script installs missing dependencies and fixes common integration issues
to improve the overall system integration health.
"""

import os
import sys
import subprocess
import logging
from typing import List, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def check_package_installed(package: str) -> bool:
    """Check if a Python package is installed."""
    try:
        __import__(package)
        return True
    except ImportError:
        return False


def install_package(package: str, description: str = "") -> bool:
    """Install a Python package using pip."""
    try:
        logger.info(f"Installing {package} {description}...")
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', package
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Successfully installed {package}")
            return True
        else:
            logger.error(f"❌ Failed to install {package}: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Error installing {package}: {e}")
        return False


def check_and_install_dependencies() -> List[Tuple[str, bool]]:
    """Check and install missing dependencies."""
    
    dependencies = [
        ('yaml', 'pyyaml', 'for Text Parser configuration'),
        ('sqlalchemy', 'sqlalchemy', 'for Crafting and Economy systems'),
        ('psycopg2', 'psycopg2-binary', 'for PostgreSQL database support'),
        ('requests', 'requests', 'for external API integration'),
        ('asyncio', None, 'built-in Python module'),
        ('dataclasses', None, 'built-in Python module (Python 3.7+)'),
        ('enum', None, 'built-in Python module'),
        ('typing', None, 'built-in Python module'),
        ('datetime', None, 'built-in Python module'),
        ('logging', None, 'built-in Python module'),
    ]
    
    results = []
    
    print("🔍 Checking dependencies...")
    print("=" * 50)
    
    for import_name, pip_name, description in dependencies:
        if check_package_installed(import_name):
            print(f"✅ {import_name:<15} - Already installed")
            results.append((import_name, True))
        else:
            print(f"❌ {import_name:<15} - Missing {description}")
            if pip_name:
                success = install_package(pip_name, description)
                results.append((import_name, success))
            else:
                print(f"   {import_name} is a built-in module - check Python version")
                results.append((import_name, False))
    
    return results


def fix_import_paths():
    """Fix common import path issues."""
    print("\n🔧 Fixing import paths...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Ensure backend/src is in Python path
    backend_src = os.path.join(current_dir, 'backend', 'src')
    if os.path.exists(backend_src):
        print(f"✅ Backend source directory found: {backend_src}")
    else:
        print(f"❌ Backend source directory not found: {backend_src}")
    
    # Check for key directories
    key_dirs = [
        'backend/src/ai_gm',
        'backend/src/text_parser',
        'backend/src/crafting',
        'backend/src/magic_system',
        'backend/src/economy',
        'backend/src/business',
        'backend/src/npc',
        'backend/src/quest'
    ]
    
    for dir_path in key_dirs:
        full_path = os.path.join(current_dir, dir_path)
        if os.path.exists(full_path):
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path} - Directory missing")


def test_system_imports():
    """Test if systems can be imported after fixes."""
    print("\n🧪 Testing system imports...")
    
    # Add current directory to path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)
    sys.path.insert(0, os.path.join(current_dir, 'backend', 'src'))
    
    import_tests = [
        ('AI GM Brain', 'ai_gm_direct_test', 'create_unified_gm'),
        ('Text Parser', 'text_parser.parser_integrator', 'create_parser_integrator'),
        ('Crafting System', 'backend.src.crafting.services.crafting_integration_service', 'create_crafting_integration_service'),
        ('Magic System', 'backend.src.game_engine.magic_combat_integration', 'create_magic_integration_services'),
        ('Economy Service', 'economy.services.economy_service', 'EconomyService'),
        ('Business API', 'business.api.business_api', 'BusinessAPI'),
    ]
    
    results = []
    
    for system_name, module_name, class_name in import_tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {system_name:<20} - Import successful")
            results.append((system_name, True))
        except Exception as e:
            print(f"❌ {system_name:<20} - Import failed: {e}")
            results.append((system_name, False))
    
    return results


def test_integration_system():
    """Test the integration system itself."""
    print("\n🔗 Testing integration system...")
    
    try:
        from system_integration_manager import create_integrated_session
        
        # Create test session
        session = create_integrated_session(
            session_id="setup_test",
            player_id="setup_player"
        )
        
        # Get status
        status = session.get_system_status()
        health_score = status['integration_health']['health_score']
        active_systems = status['integration_health']['active_systems']
        
        print(f"✅ Integration system working")
        print(f"📊 Integration Health: {health_score:.1f}%")
        print(f"🔧 Active Systems: {active_systems}/11")
        
        # Test basic functionality
        response = session.process_player_input("test input")
        print(f"✅ Basic processing working: {len(response['response_text'])} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration system failed: {e}")
        return False


def create_integration_status_report():
    """Create a detailed integration status report."""
    print("\n📋 Creating integration status report...")
    
    try:
        from system_integration_manager import create_integrated_session
        
        session = create_integrated_session("status_check", "status_player")
        status = session.get_system_status()
        
        report = f"""
# TextRealmsAI Integration Status Report
Generated: {status.get('timestamp', 'Unknown')}

## Overall Health
- **Integration Health Score**: {status['integration_health']['health_score']:.1f}%
- **Active Systems**: {status['integration_health']['active_systems']}/{status['integration_health']['total_systems']}
- **Status**: {status['integration_health']['status'].upper()}

## System Status
"""
        
        for system_name, system_info in status['systems'].items():
            status_icon = "✅" if system_info['active'] else "❌"
            report += f"- {status_icon} **{system_name.replace('_', ' ').title()}**: {'Active' if system_info['active'] else 'Inactive'}\n"
        
        report += f"""
## Session Information
- **Session ID**: {status['session_id']}
- **Player ID**: {status['player_id']}
- **Uptime**: {status['uptime']}
- **Events Processed**: {status.get('events_processed', 0)}

## Recommendations
"""
        
        health_score = status['integration_health']['health_score']
        if health_score < 40:
            report += "- 🚨 **CRITICAL**: Install missing dependencies immediately\n"
            report += "- 🔧 Run dependency installation script\n"
        elif health_score < 70:
            report += "- ⚠️ **DEGRADED**: Some systems are missing\n"
            report += "- 🔧 Check import paths and dependencies\n"
        else:
            report += "- ✅ **HEALTHY**: System integration is working well\n"
            report += "- 🚀 Consider adding remaining optional systems\n"
        
        # Save report
        with open('integration_status_report.md', 'w') as f:
            f.write(report)
        
        print(f"✅ Status report saved to: integration_status_report.md")
        
    except Exception as e:
        print(f"❌ Failed to create status report: {e}")


def main():
    """Main setup function."""
    print("🚀 TextRealmsAI Integration Setup")
    print("=" * 50)
    
    # Step 1: Check and install dependencies
    dependency_results = check_and_install_dependencies()
    
    # Step 2: Fix import paths
    fix_import_paths()
    
    # Step 3: Test system imports
    import_results = test_system_imports()
    
    # Step 4: Test integration system
    integration_working = test_integration_system()
    
    # Step 5: Create status report
    create_integration_status_report()
    
    # Summary
    print("\n📊 Setup Summary")
    print("=" * 30)
    
    successful_deps = sum(1 for _, success in dependency_results if success)
    total_deps = len(dependency_results)
    print(f"Dependencies: {successful_deps}/{total_deps} installed")
    
    successful_imports = sum(1 for _, success in import_results if success)
    total_imports = len(import_results)
    print(f"System Imports: {successful_imports}/{total_imports} working")
    
    print(f"Integration System: {'✅ Working' if integration_working else '❌ Failed'}")
    
    if integration_working:
        print("\n🎉 Setup completed successfully!")
        print("💡 Run the integration manager to start using the system:")
        print("   python3 system_integration_manager.py")
    else:
        print("\n⚠️ Setup completed with issues")
        print("🔧 Check the error messages above and try running setup again")
    
    print("\n📋 Check 'integration_status_report.md' for detailed status")


if __name__ == "__main__":
    main()
