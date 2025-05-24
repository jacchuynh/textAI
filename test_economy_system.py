
"""
Test script for the economy system.

This script demonstrates the basic functionality of the economy system,
including market interactions, buying/selling, business management, and more.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List

# Import the economy system
from backend.src.game_engine.economy_system import economy_system
from backend.src.events.event_bus import event_bus, GameEvent, EventType

# Import world state for testing economic conditions
from backend.src.narrative_engine.world_state import world_state_manager, EconomicStatus, PoliticalStability

# Mock character for testing
class MockCharacter:
    def __init__(self, char_id, name, gold=500):
        self.id = char_id
        self.name = name
        self.gold = gold
        self.inventory = []
        self.businesses = []
        self.domains = {}
        self.reputation = {}


# Mock character storage
mock_characters = {}

def get_character(character_id):
    return mock_characters.get(character_id)

def save_character(character):
    mock_characters[str(character.id)] = character
    return True

# Patch the import
import backend.src.storage.character_storage
backend.src.storage.character_storage.get_character = get_character
backend.src.storage.character_storage.save_character = save_character


async def test_market_entry():
    """Test entering a market."""
    print("\n=== Testing Market Entry ===")
    
    # Create a test character
    test_char = MockCharacter("player1", "Tester")
    mock_characters[str(test_char.id)] = test_char
    
    # Enter market
    result = economy_system.enter_market(str(test_char.id), "Ashkar Vale")
    
    print(f"Entered market: {result['name']}")
    print(f"Prosperity: {result['prosperity']}")
    print(f"Dominant Faction: {result['dominant_faction']}")
    print(f"Notable Shops:")
    for shop in result["notable_shops"]:
        print(f"  - {shop['name']} ({shop['type']})")


async def test_shop_browse():
    """Test browsing a shop."""
    print("\n=== Testing Shop Browsing ===")
    
    # Create a test character
    test_char = MockCharacter("player1", "Tester")
    mock_characters[str(test_char.id)] = test_char
    
    # Browse shop
    result = economy_system.browse_shop(str(test_char.id), "The Healing Hand")
    
    print(f"Browsing shop: {result['name']} ({result['type']})")
    print(f"Owner: {result['owner']['name']} ({result['owner']['race']} {result['owner']['personality']})")
    print(f"Inventory:")
    for item in result["inventory"]:
        notes = f" ({', '.join(item['pricing_notes'])})" if item['pricing_notes'] else ""
        print(f"  - {item['name']}: {item['price']}g{notes}")


async def test_buying_selling():
    """Test buying and selling items."""
    print("\n=== Testing Buying and Selling ===")
    
    # Create a test character with money
    test_char = MockCharacter("player1", "Tester", gold=200)
    mock_characters[str(test_char.id)] = test_char
    
    # Buy an item
    print("Attempting to buy a Minor Healing Potion...")
    buy_result = economy_system.buy_item(str(test_char.id), "The Healing Hand", "Minor Healing Potion", 1)
    
    if "error" in buy_result:
        print(f"Error: {buy_result['error']}")
    else:
        print(f"Success: {buy_result['message']}")
        print(f"Gold remaining: {buy_result['gold_remaining']}")
        
        # Print inventory
        print(f"Inventory now contains {len(test_char.inventory)} items")
        for item in test_char.inventory:
            print(f"  - {item['name']} (value: {item['value']}g)")
        
        # Now try selling it back
        print("\nAttempting to sell the potion back...")
        sell_result = economy_system.sell_item(str(test_char.id), "The Healing Hand", "Minor Healing Potion", 1)
        
        if "error" in sell_result:
            print(f"Error: {sell_result['error']}")
        else:
            print(f"Success: {sell_result['message']}")
            print(f"Gold gained: {sell_result['gold_gained']}")
            print(f"Total gold: {sell_result['gold_total']}")
            print(f"Inventory now contains {len(test_char.inventory)} items")


async def test_business_operations():
    """Test business operations."""
    print("\n=== Testing Business Operations ===")
    
    # Create a test character with money
    test_char = MockCharacter("player1", "Tester", gold=1000)
    mock_characters[str(test_char.id)] = test_char
    
    # Open a business
    print("Opening an apothecary business...")
    business_result = economy_system.open_business(str(test_char.id), "Tester's Tonics", "apothecary", "Ashkar Vale")
    
    if "error" in business_result:
        print(f"Error: {business_result['error']}")
    else:
        print(f"Success: {business_result['message']}")
        print(f"Gold remaining: {business_result['gold_remaining']}")
        
        # Check business status
        print("\nChecking business status...")
        status = economy_system.check_business(str(test_char.id), "Tester's Tonics")
        
        if "error" in status:
            print(f"Error: {status['error']}")
        else:
            print(f"{status['name']} | {status['type'].title()}, {status['city']}")
            print(f"Income: {status['income']}g/week | Expenses: {status['expenses']}g/week")
            print(f"Profit: {status['profit']}g/week")
            print(f"Stock: {', '.join(status['stock'])}")
            print(f"Reputation: {status['reputation']}")
            print(f"Risk: {status['risk']} ({status['risk_reason']})")
            
            # Hire a worker
            print("\nHiring a worker...")
            hire_result = economy_system.hire_worker(str(test_char.id), "Tester's Tonics", "Eliza", "alchemist")
            
            if "error" in hire_result:
                print(f"Error: {hire_result['error']}")
            else:
                print(f"Success: {hire_result['message']}")
                print(f"Weekly wage: {hire_result['weekly_wage']}g")
                print(f"Gold remaining: {hire_result['gold_remaining']}")
                
                # Check business again
                print("\nChecking business status after hiring...")
                status = economy_system.check_business(str(test_char.id), "Tester's Tonics")
                
                print(f"{status['name']} | {status['type'].title()}, {status['city']}")
                print(f"Income: {status['income']}g/week | Expenses: {status['expenses']}g/week")
                print(f"Profit: {status['profit']}g/week")
                print(f"Workers: {', '.join(status['workers'])}")


async def test_market_report():
    """Test market report."""
    print("\n=== Testing Market Report ===")
    
    # Create a test character
    test_char = MockCharacter("player1", "Tester")
    mock_characters[str(test_char.id)] = test_char
    
    # View market report
    print("Viewing market report for Skarport...")
    report = economy_system.view_market_report(str(test_char.id), "Skarport")
    
    if "error" in report:
        print(f"Error: {report['error']}")
    else:
        print(f"Market Report: {report['city']}")
        print(f"Prosperity: {report['prosperity']}")
        print(f"Faction Influence: {report['faction_influence']}")
        print(f"Goods Status:")
        for good in report["goods_status"]:
            print(f"  - {good['item']}: {good['status']} (prices {good['price_trend']})")
        print(f"Smuggling Activity: {report['smuggling_activity']}")
        print(f"Tax Rate: {report['tax_rate']}")
        print(f"Suggested Ventures:")
        for venture in report["suggested_ventures"]:
            print(f"  - {venture}")


async def test_market_manipulation():
    """Test market manipulation."""
    print("\n=== Testing Market Manipulation ===")
    
    # Create a test character with money
    test_char = MockCharacter("player1", "Tester", gold=500)
    mock_characters[str(test_char.id)] = test_char
    
    # Add domains for skill checks
    test_char.domains = {
        "COMMERCE": type('Domain', (), {'value': 3}),
        "SUBTERFUGE": type('Domain', (), {'value': 2}),
        "INFLUENCE": type('Domain', (), {'value': 2}),
    }
    
    # Try manipulation
    print("Attempting to undercut prices in Skarport...")
    result = economy_system.manipulate_market(str(test_char.id), "Skarport", "undercut", "enchanted textiles")
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Success: {result['message']}")
        print(f"Cost: {result['cost']}g")
        print(f"Effects:")
        for effect in result["effects"]:
            print(f"  - {effect}")
        print(f"Gold remaining: {result['gold_remaining']}")


async def test_economic_shifts():
    """Test economic shifts in the world."""
    print("\n=== Testing Economic Shifts ===")
    
    # Test different economic conditions
    print("Testing recession effects...")
    world_state_manager.update_economic_status(EconomicStatus.RECESSION)
    economy_system._update_markets_for_economic_change(EconomicStatus.RECESSION.value)
    
    # Browse shop during recession
    test_char = MockCharacter("player1", "Tester")
    mock_characters[str(test_char.id)] = test_char
    
    recession_shop = economy_system.browse_shop(str(test_char.id), "The Healing Hand")
    
    print(f"During recession, prices at {recession_shop['name']}:")
    for item in recession_shop["inventory"][:3]:  # Just show first 3 items
        notes = f" ({', '.join(item['pricing_notes'])})" if item['pricing_notes'] else ""
        print(f"  - {item['name']}: {item['price']}g{notes}")
    
    # Now test boom economy
    print("\nTesting boom effects...")
    world_state_manager.update_economic_status(EconomicStatus.BOOM)
    economy_system._update_markets_for_economic_change(EconomicStatus.BOOM.value)
    
    boom_shop = economy_system.browse_shop(str(test_char.id), "The Healing Hand")
    
    print(f"During economic boom, prices at {boom_shop['name']}:")
    for item in boom_shop["inventory"][:3]:  # Just show first 3 items
        notes = f" ({', '.join(item['pricing_notes'])})" if item['pricing_notes'] else ""
        print(f"  - {item['name']}: {item['price']}g{notes}")
    
    # Reset to stable economy
    world_state_manager.update_economic_status(EconomicStatus.STABLE)
    economy_system._update_markets_for_economic_change(EconomicStatus.STABLE.value)


async def main():
    """Run all tests."""
    print("=== Testing Economy System ===\n")
    
    await test_market_entry()
    await test_shop_browse()
    await test_buying_selling()
    await test_business_operations()
    await test_market_report()
    await test_market_manipulation()
    await test_economic_shifts()
    
    print("\n=== All economy tests completed ===")


if __name__ == "__main__":
    # Initialize the system before running tests
    economy_system._initialize_default_data()
    
    asyncio.run(main())
