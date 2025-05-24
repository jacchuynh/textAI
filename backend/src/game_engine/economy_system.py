
"""
Dynamic economy system for the game engine.

This module handles market simulation, trading, business operations,
and economic interactions between players and NPCs.
"""
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
import random

from ..shared.models import Character
from ..events.event_bus import event_bus, GameEvent, EventType
from ..narrative_engine.world_state import world_state_manager, EconomicStatus


class EconomySystem:
    """
    System for managing dynamic economy, markets, and trading.
    
    This class handles:
    - Item buying and selling with dynamic pricing
    - Business operations and management
    - Market simulation and fluctuations
    - Trade routes and caravans
    - Economic impacts from player actions
    """
    
    def __init__(self):
        """Initialize the economy system."""
        # City markets with their goods and pricing
        self._city_markets: Dict[str, Dict[str, Any]] = {}
        
        # Player businesses
        self._player_businesses: Dict[str, Dict[str, Any]] = {}
        
        # Trade routes and caravans
        self._active_caravans: List[Dict[str, Any]] = []
        
        # Regional modifiers
        self._regional_modifiers: Dict[str, float] = {}
        
        # Register event handlers
        self._register_event_handlers()
        
        # Initialize default data
        self._initialize_default_data()
    
    def _register_event_handlers(self):
        """Register event handlers for the economy system."""
        event_bus.subscribe(EventType.ITEM_PURCHASED, self._handle_item_purchase)
        event_bus.subscribe(EventType.ITEM_SOLD, self._handle_item_sold)
        event_bus.subscribe(EventType.BUSINESS_OPENED, self._handle_business_opened)
        event_bus.subscribe(EventType.CARAVAN_SENT, self._handle_caravan_sent)
        event_bus.subscribe(EventType.MARKET_MANIPULATION, self._handle_market_manipulation)
        event_bus.subscribe(EventType.WORLD_STATE_CHANGED, self._handle_world_state_change)
    
    def _initialize_default_data(self):
        """Initialize default economy data."""
        # Example cities with basic market data
        self._city_markets = {
            "Ashkar Vale": {
                "prosperity": 0.7,
                "dominant_faction": "Verdant Keepers",
                "specialty_goods": ["healing_potions", "herbal_remedies"],
                "goods": {
                    "healing_potion": {"base_price": 15, "supply": 0.6, "demand": 0.8},
                    "iron_sword": {"base_price": 20, "supply": 0.5, "demand": 0.5},
                    "dream_root_elixir": {"base_price": 25, "supply": 0.3, "demand": 0.6}
                },
                "smuggling_activity": 0.2,
                "tax_rate": 0.05
            },
            "Skarport": {
                "prosperity": 0.8,
                "dominant_faction": "Crimson Accord High Council",
                "specialty_goods": ["enchanted_textiles", "mana_filters"],
                "goods": {
                    "enchanted_textile": {"base_price": 30, "supply": 0.9, "demand": 0.4},
                    "mana_filter": {"base_price": 45, "supply": 0.2, "demand": 0.9},
                    "reinforced_boots": {"base_price": 18, "supply": 0.4, "demand": 0.7}
                },
                "smuggling_activity": 0.5,
                "tax_rate": 0.08
            },
            "Thal-Zirad": {
                "prosperity": 0.6,
                "dominant_faction": "Artificers Guild",
                "specialty_goods": ["mechanical_components", "alchemical_reagents"],
                "goods": {
                    "repair_kit": {"base_price": 12, "supply": 0.7, "demand": 0.6},
                    "mechanical_gear": {"base_price": 8, "supply": 0.8, "demand": 0.5},
                    "alchemical_reagent": {"base_price": 22, "supply": 0.4, "demand": 0.8}
                },
                "smuggling_activity": 0.3,
                "tax_rate": 0.06
            },
            "Stonewake": {
                "prosperity": 0.5,
                "dominant_faction": "Miners Coalition",
                "specialty_goods": ["raw_ore", "forged_weapons"],
                "goods": {
                    "raw_ore": {"base_price": 10, "supply": 0.9, "demand": 0.6},
                    "steel_hammer": {"base_price": 35, "supply": 0.6, "demand": 0.5},
                    "dwarven_ale": {"base_price": 8, "supply": 0.7, "demand": 0.8}
                },
                "smuggling_activity": 0.1,
                "tax_rate": 0.04
            }
        }
        
        # Regional modifiers based on world state
        economic_status = world_state_manager.economic_status.value
        if economic_status == EconomicStatus.BOOM.value:
            default_modifier = 1.2
        elif economic_status == EconomicStatus.STABLE.value:
            default_modifier = 1.0
        elif economic_status == EconomicStatus.RECESSION.value:
            default_modifier = 0.8
        else:  # DEPRESSION
            default_modifier = 0.6
            
        # Apply seasonal effects
        current_season = world_state_manager.current_season
        seasonal_effects = {
            "spring": {"herbal_remedies": 1.2, "agricultural_goods": 0.8},
            "summer": {"travel_goods": 1.2, "cooling_items": 1.5},
            "autumn": {"preserves": 1.3, "harvested_goods": 0.7},
            "winter": {"furs": 1.4, "heating_items": 1.5, "travel_goods": 0.8}
        }
        
        for city in self._city_markets:
            self._regional_modifiers[city] = default_modifier
    
    def enter_market(self, character_id: str, market_name: str) -> Dict[str, Any]:
        """
        Player enters a market.
        
        Args:
            character_id: ID of the character entering the market
            market_name: Name of the market/city
            
        Returns:
            Market overview information
        """
        if market_name not in self._city_markets:
            return {"error": f"Market {market_name} not found"}
            
        market = self._city_markets[market_name]
        
        # Create market snapshot
        snapshot = {
            "name": market_name,
            "prosperity": market["prosperity"],
            "dominant_faction": market["dominant_faction"],
            "specialty_goods": market["specialty_goods"],
            "tax_rate": market["tax_rate"],
            "regional_modifier": self._regional_modifiers.get(market_name, 1.0),
            "notable_shops": self._get_shops_in_city(market_name),
            "economic_activity": self._get_economic_status_description(market)
        }
        
        # Publish event
        event = GameEvent(
            type=EventType.MARKET_ENTERED,
            actor=character_id,
            context={
                "market": market_name,
                "prosperity": market["prosperity"],
                "faction": market["dominant_faction"]
            },
            tags=["economy", "market", market_name.lower().replace(" ", "_")]
        )
        event_bus.publish(event)
        
        return snapshot
    
    def browse_shop(self, character_id: str, shop_name: str) -> Dict[str, Any]:
        """
        Browse items in a shop.
        
        Args:
            character_id: ID of the character browsing
            shop_name: Name of the shop
            
        Returns:
            Shop inventory with prices
        """
        # In a real implementation, you'd look up the shop in a database
        # For now we'll generate a mock shop based on the name
        
        # Find which city this shop is in
        shop_city = None
        for city, data in self._city_markets.items():
            city_shops = self._get_shops_in_city(city)
            if shop_name in [s["name"] for s in city_shops]:
                shop_city = city
                break
        
        if not shop_city:
            return {"error": f"Shop {shop_name} not found"}
            
        # Get shop type based on name
        shop_type = self._determine_shop_type(shop_name)
        
        # Get character for relationship modifier
        from ..storage.character_storage import get_character
        character = get_character(character_id)
        relationship_modifier = 1.0
        if character and hasattr(character, "reputation"):
            # Apply relationship discount based on reputation in this city
            city_rep = getattr(character.reputation, shop_city.lower().replace(" ", "_"), 0)
            relationship_modifier = max(0.8, 1.0 - (city_rep * 0.05))  # Up to 20% discount
        
        # Generate inventory based on shop type and city
        inventory = self._generate_shop_inventory(shop_city, shop_type, relationship_modifier)
        
        # Create shop snapshot
        shop_data = {
            "name": shop_name,
            "type": shop_type,
            "city": shop_city,
            "owner": self._generate_shop_owner(shop_name, shop_type),
            "inventory": inventory,
            "relationship_modifier": relationship_modifier
        }
        
        # Publish event
        event = GameEvent(
            type=EventType.SHOP_BROWSED,
            actor=character_id,
            context={
                "shop": shop_name,
                "shop_type": shop_type,
                "city": shop_city,
                "item_count": len(inventory)
            },
            tags=["economy", "shop", shop_type.lower()]
        )
        event_bus.publish(event)
        
        return shop_data
    
    def buy_item(self, character_id: str, shop_name: str, item_name: str, 
                quantity: int = 1) -> Dict[str, Any]:
        """
        Buy an item from a shop.
        
        Args:
            character_id: ID of the character buying
            shop_name: Name of the shop
            item_name: Name of the item to buy
            quantity: Quantity to buy
            
        Returns:
            Result of the purchase
        """
        # Get character
        from ..storage.character_storage import get_character, save_character
        character = get_character(character_id)
        if not character:
            return {"error": "Character not found"}
            
        # Find shop
        shop_data = self.browse_shop(character_id, shop_name)
        if "error" in shop_data:
            return shop_data
            
        # Find item in inventory
        item_found = False
        item_price = 0
        item_details = {}
        
        for item in shop_data["inventory"]:
            if item["name"].lower() == item_name.lower():
                item_found = True
                item_price = item["price"]
                item_details = item
                break
                
        if not item_found:
            return {"error": f"Item {item_name} not found in {shop_name}"}
            
        # Check if character has enough gold
        total_price = item_price * quantity
        if character.gold < total_price:
            return {"error": f"Not enough gold. Need {total_price}g but have {character.gold}g"}
            
        # Process purchase
        character.gold -= total_price
        
        # Add item to inventory (simplified)
        if not hasattr(character, "inventory"):
            character.inventory = []
            
        for i in range(quantity):
            character.inventory.append({
                "name": item_details["name"],
                "type": item_details["type"],
                "quality": item_details.get("quality", "standard"),
                "value": item_price,
                "acquired_from": shop_name,
                "acquired_date": datetime.utcnow().isoformat()
            })
            
        # Update market supply/demand
        city = shop_data["city"]
        if city in self._city_markets:
            item_key = item_name.lower().replace(" ", "_")
            if item_key in self._city_markets[city]["goods"]:
                # Decrease supply, increase demand slightly
                self._city_markets[city]["goods"][item_key]["supply"] = max(
                    0.1, self._city_markets[city]["goods"][item_key]["supply"] - (0.05 * quantity)
                )
                self._city_markets[city]["goods"][item_key]["demand"] = min(
                    1.0, self._city_markets[city]["goods"][item_key]["demand"] + (0.02 * quantity)
                )
        
        # Save character
        save_character(character)
        
        # Publish event
        event = GameEvent(
            type=EventType.ITEM_PURCHASED,
            actor=character_id,
            context={
                "shop": shop_name,
                "city": shop_data["city"],
                "item": item_name,
                "quantity": quantity,
                "total_price": total_price
            },
            tags=["economy", "purchase", item_details["type"].lower()],
            effects=[
                {"type": "gold_change", "amount": -total_price},
                {"type": "inventory_change", "item": item_name, "quantity": quantity}
            ]
        )
        event_bus.publish(event)
        
        return {
            "success": True,
            "message": f"Purchased {quantity}x {item_name} for {total_price}g",
            "item": item_details,
            "gold_remaining": character.gold
        }
    
    def sell_item(self, character_id: str, shop_name: str, item_name: str, 
                 quantity: int = 1) -> Dict[str, Any]:
        """
        Sell an item to a shop.
        
        Args:
            character_id: ID of the character selling
            shop_name: Name of the shop
            item_name: Name of the item to sell
            quantity: Quantity to sell
            
        Returns:
            Result of the sale
        """
        # Get character
        from ..storage.character_storage import get_character, save_character
        character = get_character(character_id)
        if not character:
            return {"error": "Character not found"}
            
        # Check if character has the items
        if not hasattr(character, "inventory"):
            return {"error": "You have no items to sell"}
            
        # Count matching items
        matching_items = [item for item in character.inventory 
                         if item["name"].lower() == item_name.lower()]
        
        if len(matching_items) < quantity:
            return {"error": f"You only have {len(matching_items)}x {item_name}"}
            
        # Find shop
        shop_data = self.browse_shop(character_id, shop_name)
        if "error" in shop_data:
            return shop_data
            
        # Determine sell price (typically 40-60% of buy price)
        base_sell_value = matching_items[0]["value"] * 0.5
        shop_type_bonus = 0.1 if self._is_shop_interested_in_item(shop_data["type"], item_name) else 0
        
        # Calculate final price with modifiers
        sell_price_per_item = base_sell_value * (1 + shop_type_bonus)
        total_sell_price = int(sell_price_per_item * quantity)
        
        # Process sale
        character.gold += total_sell_price
        
        # Remove items from inventory
        for i in range(quantity):
            for idx, item in enumerate(character.inventory):
                if item["name"].lower() == item_name.lower():
                    character.inventory.pop(idx)
                    break
        
        # Update market supply/demand
        city = shop_data["city"]
        if city in self._city_markets:
            item_key = item_name.lower().replace(" ", "_")
            if item_key in self._city_markets[city]["goods"]:
                # Increase supply, decrease demand slightly
                self._city_markets[city]["goods"][item_key]["supply"] = min(
                    1.0, self._city_markets[city]["goods"][item_key]["supply"] + (0.03 * quantity)
                )
                self._city_markets[city]["goods"][item_key]["demand"] = max(
                    0.1, self._city_markets[city]["goods"][item_key]["demand"] - (0.01 * quantity)
                )
        
        # Save character
        save_character(character)
        
        # Publish event
        event = GameEvent(
            type=EventType.ITEM_SOLD,
            actor=character_id,
            context={
                "shop": shop_name,
                "city": shop_data["city"],
                "item": item_name,
                "quantity": quantity,
                "total_price": total_sell_price
            },
            tags=["economy", "sale"],
            effects=[
                {"type": "gold_change", "amount": total_sell_price},
                {"type": "inventory_change", "item": item_name, "quantity": -quantity}
            ]
        )
        event_bus.publish(event)
        
        return {
            "success": True,
            "message": f"Sold {quantity}x {item_name} for {total_sell_price}g",
            "gold_gained": total_sell_price,
            "gold_total": character.gold
        }
    
    def open_business(self, character_id: str, business_name: str, 
                    business_type: str, city: str) -> Dict[str, Any]:
        """
        Open a new player business.
        
        Args:
            character_id: ID of the character opening the business
            business_name: Name of the business
            business_type: Type of business (shop, forge, caravan, apothecary, etc.)
            city: City where the business is located
            
        Returns:
            Result of business creation
        """
        # Get character
        from ..storage.character_storage import get_character, save_character
        character = get_character(character_id)
        if not character:
            return {"error": "Character not found"}
            
        # Check if character already has a business
        business_key = f"{character_id}:{business_name}"
        if business_key in self._player_businesses:
            return {"error": f"You already own the business {business_name}"}
            
        # Check if city exists
        if city not in self._city_markets:
            return {"error": f"City {city} not found"}
            
        # Determine startup costs
        startup_costs = {
            "shop": 200,
            "forge": 500,
            "caravan": 300,
            "apothecary": 250,
            "farm": 150,
            "tavern": 400,
            "crafting": 200
        }
        
        base_cost = startup_costs.get(business_type.lower(), 300)
        city_modifier = self._city_markets[city]["prosperity"]
        license_fee = int(base_cost * 0.2)
        supplies_cost = int(base_cost * 0.3)
        total_cost = int(base_cost * (1 + city_modifier))
        
        # Check if character has enough gold
        if character.gold < total_cost:
            return {"error": f"Not enough gold. Need {total_cost}g but have {character.gold}g"}
            
        # Process purchase
        character.gold -= total_cost
        
        # Create business
        business_data = {
            "name": business_name,
            "type": business_type,
            "city": city,
            "owner": character_id,
            "established": datetime.utcnow().isoformat(),
            "level": 1,
            "workers": [],
            "stock": [],
            "income": 0,
            "expenses": int(base_cost * 0.1),  # 10% of base cost as weekly expenses
            "reputation": 0.5,  # Neutral reputation
            "risk": self._calculate_business_risk(city, business_type)
        }
        
        # Add to player businesses
        self._player_businesses[business_key] = business_data
        
        # Save character
        save_character(character)
        
        # Add to character's business list
        if not hasattr(character, "businesses"):
            character.businesses = []
            
        character.businesses.append({
            "name": business_name,
            "type": business_type,
            "city": city,
            "established": business_data["established"]
        })
        
        # Publish event
        event = GameEvent(
            type=EventType.BUSINESS_OPENED,
            actor=character_id,
            context={
                "business": business_name,
                "type": business_type,
                "city": city,
                "cost": total_cost
            },
            tags=["economy", "business", business_type.lower()],
            effects=[
                {"type": "gold_change", "amount": -total_cost},
                {"type": "business_acquired", "name": business_name}
            ]
        )
        event_bus.publish(event)
        
        return {
            "success": True,
            "message": f"Opened {business_name} in {city} for {total_cost}g",
            "business": business_data,
            "gold_remaining": character.gold,
            "costs_breakdown": {
                "base_cost": base_cost,
                "license_fee": license_fee,
                "supplies": supplies_cost,
                "city_modifier": city_modifier
            }
        }
    
    def check_business(self, character_id: str, business_name: str) -> Dict[str, Any]:
        """
        Check status of a player business.
        
        Args:
            character_id: ID of the character checking
            business_name: Name of the business
            
        Returns:
            Business status information
        """
        # Look for the business
        business_key = f"{character_id}:{business_name}"
        alt_keys = [k for k in self._player_businesses.keys() 
                   if self._player_businesses[k]["name"] == business_name and
                   self._player_businesses[k]["owner"] == character_id]
        
        if business_key not in self._player_businesses and not alt_keys:
            return {"error": f"Business {business_name} not found"}
            
        # Get business data
        if business_key in self._player_businesses:
            business = self._player_businesses[business_key]
        else:
            business = self._player_businesses[alt_keys[0]]
            
        # Calculate current values
        income_per_worker = 10 + (business["reputation"] * 10)
        num_workers = len(business["workers"])
        weekly_income = int(income_per_worker * num_workers * (0.8 + (business["level"] * 0.2)))
        
        # Update business data
        business["income"] = weekly_income
        
        # Format stock list
        stock_summary = []
        for item in business["stock"]:
            stock_summary.append(f"{item['quantity']}x {item['name']}")
            
        if not stock_summary:
            stock_summary = ["No items in stock"]
            
        # Get risk level text
        risk_level = "Low"
        if business["risk"] > 0.7:
            risk_level = "High"
        elif business["risk"] > 0.3:
            risk_level = "Medium"
            
        # Get reputation text
        reputation_text = "Unknown"
        rep = business["reputation"]
        if rep > 0.8:
            reputation_text = "Renowned"
        elif rep > 0.6:
            reputation_text = "Trusted"
        elif rep > 0.4:
            reputation_text = "Neutral"
        elif rep > 0.2:
            reputation_text = "Suspicious"
        else:
            reputation_text = "Distrusted"
            
        # Prepare business status
        status = {
            "name": business["name"],
            "type": business["type"],
            "city": business["city"],
            "level": business["level"],
            "established": business["established"],
            "workers": [w["name"] for w in business["workers"]],
            "income": business["income"],
            "expenses": business["expenses"],
            "profit": business["income"] - business["expenses"],
            "stock": stock_summary,
            "stock_count": len(business["stock"]),
            "reputation": reputation_text,
            "risk": risk_level,
            "risk_reason": self._get_risk_reason(business)
        }
        
        # Publish event
        event = GameEvent(
            type=EventType.BUSINESS_CHECKED,
            actor=character_id,
            context={
                "business": business_name,
                "income": business["income"],
                "expenses": business["expenses"],
                "workers": len(business["workers"])
            },
            tags=["economy", "business", business["type"].lower()]
        )
        event_bus.publish(event)
        
        return status
    
    def hire_worker(self, character_id: str, business_name: str, 
                   worker_name: str, worker_class: str) -> Dict[str, Any]:
        """
        Hire a worker for a player business.
        
        Args:
            character_id: ID of the character hiring
            business_name: Name of the business
            worker_name: Name of the worker
            worker_class: Class/type of the worker
            
        Returns:
            Result of hiring
        """
        # Get character
        from ..storage.character_storage import get_character, save_character
        character = get_character(character_id)
        if not character:
            return {"error": "Character not found"}
            
        # Look for the business
        business_key = f"{character_id}:{business_name}"
        alt_keys = [k for k in self._player_businesses.keys() 
                   if self._player_businesses[k]["name"] == business_name and
                   self._player_businesses[k]["owner"] == character_id]
        
        if business_key not in self._player_businesses and not alt_keys:
            return {"error": f"Business {business_name} not found"}
            
        # Get business data
        if business_key in self._player_businesses:
            business = self._player_businesses[business_key]
        else:
            business = self._player_businesses[alt_keys[0]]
            
        # Check if worker with this name already exists
        if any(w["name"] == worker_name for w in business["workers"]):
            return {"error": f"Worker named {worker_name} already hired"}
            
        # Determine hiring costs
        worker_costs = {
            "apprentice": 30,
            "journeyman": 60,
            "master": 120,
            "merchant": 80,
            "guard": 50,
            "alchemist": 90,
            "blacksmith": 70,
            "farmer": 40
        }
        
        base_cost = worker_costs.get(worker_class.lower(), 50)
        city_modifier = self._city_markets[business["city"]]["prosperity"]
        hiring_cost = int(base_cost * (1 + city_modifier))
        weekly_wage = int(base_cost * 0.2)  # 20% of hiring cost as weekly wage
        
        # Check if character has enough gold
        if character.gold < hiring_cost:
            return {"error": f"Not enough gold. Need {hiring_cost}g but have {character.gold}g"}
            
        # Process hiring
        character.gold -= hiring_cost
        
        # Determine worker skill based on class
        skill_levels = {
            "apprentice": 0.3,
            "journeyman": 0.6,
            "master": 0.9
        }
        
        skill = skill_levels.get(worker_class.lower(), random.uniform(0.3, 0.8))
        
        # Create worker
        worker = {
            "name": worker_name,
            "class": worker_class,
            "hired_date": datetime.utcnow().isoformat(),
            "skill": skill,
            "morale": 0.7,  # Initial morale
            "wage": weekly_wage
        }
        
        # Add worker to business
        business["workers"].append(worker)
        
        # Update business expenses
        business["expenses"] += weekly_wage
        
        # Save character
        save_character(character)
        
        # Publish event
        event = GameEvent(
            type=EventType.WORKER_HIRED,
            actor=character_id,
            context={
                "business": business_name,
                "worker": worker_name,
                "class": worker_class,
                "cost": hiring_cost
            },
            tags=["economy", "business", "hiring"],
            effects=[
                {"type": "gold_change", "amount": -hiring_cost},
                {"type": "business_update", "name": business_name}
            ]
        )
        event_bus.publish(event)
        
        return {
            "success": True,
            "message": f"Hired {worker_name} ({worker_class}) for {hiring_cost}g",
            "worker": worker,
            "gold_remaining": character.gold,
            "weekly_wage": weekly_wage
        }
    
    def send_caravan(self, character_id: str, origin_city: str, destination_city: str,
                    goods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send a caravan with goods between cities.
        
        Args:
            character_id: ID of the character sending the caravan
            origin_city: City where the caravan starts
            destination_city: City where the caravan is going
            goods: List of goods being transported
            
        Returns:
            Result of caravan dispatch
        """
        # Get character
        from ..storage.character_storage import get_character, save_character
        character = get_character(character_id)
        if not character:
            return {"error": "Character not found"}
            
        # Check if cities exist
        if origin_city not in self._city_markets:
            return {"error": f"City {origin_city} not found"}
            
        if destination_city not in self._city_markets:
            return {"error": f"City {destination_city} not found"}
            
        # Check if goods are valid and owned by player
        if not hasattr(character, "inventory"):
            return {"error": "You have no items to send"}
            
        total_goods = 0
        valid_goods = []
        for good in goods:
            item_name = good.get("name", "")
            quantity = good.get("quantity", 0)
            
            if not item_name or quantity <= 0:
                continue
                
            # Count matching items
            matching_items = [item for item in character.inventory 
                             if item["name"].lower() == item_name.lower()]
            
            if len(matching_items) < quantity:
                return {"error": f"You only have {len(matching_items)}x {item_name}"}
                
            valid_goods.append({
                "name": item_name,
                "quantity": quantity,
                "unit_value": matching_items[0]["value"]
            })
            total_goods += quantity
            
        if not valid_goods:
            return {"error": "No valid goods to send"}
            
        # Calculate caravan costs
        base_cost = 50  # Base cost for sending a caravan
        distance_factor = 1.0  # Would calculate based on city distances
        goods_factor = 0.1 * total_goods  # Cost increases with more goods
        risk_factor = self._calculate_route_risk(origin_city, destination_city)
        
        total_cost = int(base_cost * (1 + distance_factor) * (1 + goods_factor))
        
        # Check if character has enough gold
        if character.gold < total_cost:
            return {"error": f"Not enough gold. Need {total_cost}g but have {character.gold}g"}
            
        # Process caravan creation
        character.gold -= total_cost
        
        # Remove goods from inventory
        for good in valid_goods:
            item_name = good["name"]
            quantity = good["quantity"]
            
            for i in range(quantity):
                for idx, item in enumerate(character.inventory):
                    if item["name"].lower() == item_name.lower():
                        character.inventory.pop(idx)
                        break
        
        # Calculate travel time (days)
        travel_time = random.randint(3, 10)  # Would be based on distance
        
        # Create caravan
        caravan_id = str(len(self._active_caravans) + 1)
        arrival_date = datetime.utcnow()  # Would add travel_time days
        
        caravan = {
            "id": caravan_id,
            "owner": character_id,
            "origin": origin_city,
            "destination": destination_city,
            "goods": valid_goods,
            "departure_date": datetime.utcnow().isoformat(),
            "estimated_arrival": arrival_date.isoformat(),
            "travel_time": travel_time,
            "status": "en_route",
            "risk": risk_factor
        }
        
        # Add to active caravans
        self._active_caravans.append(caravan)
        
        # Save character
        save_character(character)
        
        # Publish event
        event = GameEvent(
            type=EventType.CARAVAN_SENT,
            actor=character_id,
            context={
                "origin": origin_city,
                "destination": destination_city,
                "goods_count": total_goods,
                "travel_time": travel_time,
                "cost": total_cost
            },
            tags=["economy", "caravan", "trade"],
            effects=[
                {"type": "gold_change", "amount": -total_cost}
            ]
        )
        event_bus.publish(event)
        
        return {
            "success": True,
            "message": f"Sent caravan from {origin_city} to {destination_city} with {total_goods} goods",
            "caravan_id": caravan_id,
            "cost": total_cost,
            "estimated_arrival": f"{travel_time} days",
            "risk_level": self._get_risk_level_text(risk_factor),
            "gold_remaining": character.gold
        }
    
    def view_market_report(self, character_id: str, city: str) -> Dict[str, Any]:
        """
        View a market report for a city.
        
        Args:
            character_id: ID of the character viewing the report
            city: Name of the city
            
        Returns:
            Market report information
        """
        if city not in self._city_markets:
            return {"error": f"City {city} not found"}
            
        market = self._city_markets[city]
        
        # Get supply/demand status for each good
        goods_status = []
        for item_name, data in market["goods"].items():
            supply = data["supply"]
            demand = data["demand"]
            
            status = "Balanced"
            if supply > 0.7 and demand < 0.3:
                status = "Surplus (prices down)"
            elif supply > 0.6 and demand < 0.4:
                status = "Oversupply"
            elif supply < 0.3 and demand > 0.7:
                status = "High demand"
            elif supply < 0.4 and demand > 0.6:
                status = "Undersupply"
                
            goods_status.append({
                "item": item_name.replace("_", " ").title(),
                "status": status,
                "price_trend": self._get_price_trend(supply, demand)
            })
            
        # Get suggested ventures
        suggested_ventures = self._generate_venture_suggestions(city)
        
        # Format smuggling activity
        smuggling_level = "None"
        if market["smuggling_activity"] > 0.7:
            smuggling_level = "High"
        elif market["smuggling_activity"] > 0.3:
            smuggling_level = "Medium"
        elif market["smuggling_activity"] > 0.1:
            smuggling_level = "Low"
            
        # Create market report
        report = {
            "city": city,
            "prosperity": market["prosperity"],
            "faction_influence": market["dominant_faction"],
            "goods_status": goods_status,
            "smuggling_activity": smuggling_level,
            "tax_rate": f"{market['tax_rate'] * 100}%",
            "suggested_ventures": suggested_ventures
        }
        
        # Publish event
        event = GameEvent(
            type=EventType.MARKET_REPORT_VIEWED,
            actor=character_id,
            context={
                "city": city,
                "prosperity": market["prosperity"],
                "smuggling": smuggling_level
            },
            tags=["economy", "market", "report"]
        )
        event_bus.publish(event)
        
        return report
    
    def manipulate_market(self, character_id: str, city: str, action: str, 
                         target: str) -> Dict[str, Any]:
        """
        Attempt to manipulate a market.
        
        Args:
            character_id: ID of the character manipulating
            city: Name of the city
            action: Type of manipulation (undercut, sabotage, etc.)
            target: Target of the manipulation
            
        Returns:
            Result of the manipulation attempt
        """
        # Get character
        from ..storage.character_storage import get_character, save_character
        character = get_character(character_id)
        if not character:
            return {"error": "Character not found"}
            
        # Check if city exists
        if city not in self._city_markets:
            return {"error": f"City {city} not found"}
            
        # Validate action
        valid_actions = ["undercut", "sabotage", "monopolize", "influence", "smuggle"]
        if action.lower() not in valid_actions:
            return {"error": f"Invalid action. Choose from: {', '.join(valid_actions)}"}
            
        # Calculate base cost and difficulty
        action_costs = {
            "undercut": 100,
            "sabotage": 200,
            "monopolize": 500,
            "influence": 300,
            "smuggle": 150
        }
        
        base_cost = action_costs.get(action.lower(), 200)
        city_modifier = self._city_markets[city]["prosperity"]
        total_cost = int(base_cost * (1 + city_modifier))
        
        # Calculate difficulty
        base_difficulty = {
            "undercut": 10,
            "sabotage": 15,
            "monopolize": 18,
            "influence": 14,
            "smuggle": 12
        }
        
        difficulty = base_difficulty.get(action.lower(), 15)
        
        # Apply modifiers based on city and faction influence
        # This would ideally use the domain system for skill checks
        if hasattr(character, "domains"):
            # Just a basic check for demonstration purposes
            from ..game_engine.domain_system import domain_system
            
            # Different actions use different domains
            domain_mapping = {
                "undercut": "COMMERCE",
                "sabotage": "STEALTH",
                "monopolize": "INFLUENCE",
                "influence": "SOCIAL",
                "smuggle": "SUBTERFUGE"
            }
            
            domain_type = domain_mapping.get(action.lower(), "COMMERCE")
            
            # Perform domain check
            result = domain_system.roll_check(
                character=character,
                domain_type=domain_type,
                difficulty=difficulty
            )
            
            success = result["success"]
        else:
            # Fallback random chance if domains aren't available
            success = random.random() > (difficulty / 20)
            
        # Check if character has enough gold
        if character.gold < total_cost:
            return {"error": f"Not enough gold. Need {total_cost}g but have {character.gold}g"}
            
        # Process action cost
        character.gold -= total_cost
        
        # Apply market effects based on action and success
        effects = []
        if success:
            if action.lower() == "undercut":
                # Decrease prices for target good category
                for item_name, data in self._city_markets[city]["goods"].items():
                    if target.lower() in item_name:
                        data["supply"] = min(1.0, data["supply"] + 0.2)
                        
                effects.append(f"Prices for {target} goods have dropped")
                effects.append("Local merchants are unhappy with the competition")
                
            elif action.lower() == "sabotage":
                # Target production of a specific good
                for item_name, data in self._city_markets[city]["goods"].items():
                    if target.lower() in item_name:
                        data["supply"] = max(0.1, data["supply"] - 0.3)
                        
                effects.append(f"{target} production has been disrupted")
                effects.append("Guards are investigating the incident")
                
            elif action.lower() == "monopolize":
                # Increase prices by controlling supply
                for item_name, data in self._city_markets[city]["goods"].items():
                    if target.lower() in item_name:
                        data["supply"] = max(0.1, data["supply"] - 0.4)
                        data["demand"] = min(1.0, data["demand"] + 0.2)
                        
                effects.append(f"You've gained significant control over {target} trade")
                effects.append("Your reputation with merchants has decreased")
                
            elif action.lower() == "influence":
                # Change faction influence
                self._city_markets[city]["dominant_faction"] = target
                effects.append(f"Your influence has shifted power toward {target}")
                
            elif action.lower() == "smuggle":
                # Increase smuggling activity
                self._city_markets[city]["smuggling_activity"] = min(
                    1.0, self._city_markets[city]["smuggling_activity"] + 0.3
                )
                effects.append("Smuggling routes have been established")
                effects.append("Guard patrols have increased in response")
        else:
            effects.append("Your attempt failed and raised suspicions")
            effects.append("Your reputation in the city has decreased slightly")
            
        # Save character
        save_character(character)
        
        # Publish event
        event = GameEvent(
            type=EventType.MARKET_MANIPULATION,
            actor=character_id,
            context={
                "city": city,
                "action": action,
                "target": target,
                "success": success,
                "cost": total_cost
            },
            tags=["economy", "manipulation", action.lower()],
            effects=[
                {"type": "gold_change", "amount": -total_cost},
                {"type": "market_change", "city": city, "details": effects}
            ]
        )
        event_bus.publish(event)
        
        return {
            "success": success,
            "message": f"{'Successfully' if success else 'Failed to'} {action} {target} in {city}",
            "cost": total_cost,
            "effects": effects,
            "gold_remaining": character.gold
        }
    
    def _handle_item_purchase(self, event: GameEvent):
        """Handle item purchase events."""
        # Update market data based on purchases
        context = event.context
        city = context.get("city")
        item = context.get("item")
        quantity = context.get("quantity", 1)
        
        if not city or not item or city not in self._city_markets:
            return
            
        item_key = item.lower().replace(" ", "_")
        if item_key in self._city_markets[city]["goods"]:
            # Decrease supply, increase demand
            self._city_markets[city]["goods"][item_key]["supply"] = max(
                0.1, self._city_markets[city]["goods"][item_key]["supply"] - (0.05 * quantity)
            )
            self._city_markets[city]["goods"][item_key]["demand"] = min(
                1.0, self._city_markets[city]["goods"][item_key]["demand"] + (0.02 * quantity)
            )
    
    def _handle_item_sold(self, event: GameEvent):
        """Handle item sold events."""
        # Update market data based on sales
        context = event.context
        city = context.get("city")
        item = context.get("item")
        quantity = context.get("quantity", 1)
        
        if not city or not item or city not in self._city_markets:
            return
            
        item_key = item.lower().replace(" ", "_")
        if item_key in self._city_markets[city]["goods"]:
            # Increase supply, decrease demand
            self._city_markets[city]["goods"][item_key]["supply"] = min(
                1.0, self._city_markets[city]["goods"][item_key]["supply"] + (0.03 * quantity)
            )
            self._city_markets[city]["goods"][item_key]["demand"] = max(
                0.1, self._city_markets[city]["goods"][item_key]["demand"] - (0.01 * quantity)
            )
    
    def _handle_business_opened(self, event: GameEvent):
        """Handle business opened events."""
        # Update city data with new business
        context = event.context
        city = context.get("city")
        business_type = context.get("type")
        
        if not city or not business_type or city not in self._city_markets:
            return
            
        # Slight increase in prosperity
        self._city_markets[city]["prosperity"] = min(
            1.0, self._city_markets[city]["prosperity"] + 0.01
        )
    
    def _handle_caravan_sent(self, event: GameEvent):
        """Handle caravan sent events."""
        # Queue caravan arrival
        # In a real implementation, you'd schedule this for later processing
        pass
    
    def _handle_market_manipulation(self, event: GameEvent):
        """Handle market manipulation events."""
        # Update market data based on manipulation
        context = event.context
        city = context.get("city")
        action = context.get("action")
        target = context.get("target")
        success = context.get("success", False)
        
        if not city or not action or not target or city not in self._city_markets:
            return
            
        if not success:
            return
            
        # Effects already applied in manipulate_market method
    
    def _handle_world_state_change(self, event: GameEvent):
        """Handle world state changes."""
        context = event.context
        change = context.get("change")
        new_value = context.get("new_value")
        
        if change == "economic_status":
            self._update_markets_for_economic_change(new_value)
        elif change == "political_stability":
            self._update_markets_for_political_change(new_value)
        elif change == "current_season":
            self._update_markets_for_seasonal_change(new_value)
    
    def _update_markets_for_economic_change(self, economic_status: str):
        """Update markets based on economic status change."""
        modifier = 1.0
        if economic_status == EconomicStatus.BOOM.value:
            modifier = 1.2
        elif economic_status == EconomicStatus.STABLE.value:
            modifier = 1.0
        elif economic_status == EconomicStatus.RECESSION.value:
            modifier = 0.8
        else:  # DEPRESSION
            modifier = 0.6
            
        # Apply to all cities
        for city in self._city_markets:
            self._regional_modifiers[city] = modifier
    
    def _update_markets_for_political_change(self, political_status: str):
        """Update markets based on political stability change."""
        # Adjust smuggling activity and risk based on political stability
        for city, market in self._city_markets.items():
            if political_status == "peaceful":
                market["smuggling_activity"] = max(0.1, market["smuggling_activity"] - 0.2)
            elif political_status == "unrest":
                market["smuggling_activity"] = min(0.9, market["smuggling_activity"] + 0.2)
            elif political_status == "rebellion":
                market["smuggling_activity"] = min(1.0, market["smuggling_activity"] + 0.4)
    
    def _update_markets_for_seasonal_change(self, season: str):
        """Update markets based on seasonal change."""
        seasonal_effects = {
            "spring": {"herbal_remedies": 1.2, "agricultural_goods": 0.8},
            "summer": {"travel_goods": 1.2, "cooling_items": 1.5},
            "autumn": {"preserves": 1.3, "harvested_goods": 0.7},
            "winter": {"furs": 1.4, "heating_items": 1.5, "travel_goods": 0.8}
        }
        
        effects = seasonal_effects.get(season, {})
        
        # Apply seasonal effects to goods
        for city, market in self._city_markets.items():
            for item_name, data in market["goods"].items():
                for category, modifier in effects.items():
                    if category in item_name:
                        # Adjust supply and demand based on season
                        if modifier > 1:  # More expensive (higher demand or lower supply)
                            data["demand"] = min(1.0, data["demand"] + 0.2)
                        else:  # Cheaper (lower demand or higher supply)
                            data["supply"] = min(1.0, data["supply"] + 0.2)
    
    def _get_shops_in_city(self, city: str) -> List[Dict[str, Any]]:
        """Get a list of shops in a city."""
        # In a real implementation, you'd query a database
        # For now, generate some sample shops
        if city == "Ashkar Vale":
            return [
                {"name": "The Healing Hand", "type": "apothecary"},
                {"name": "Verdant Armory", "type": "weaponsmith"},
                {"name": "Nature's Bounty", "type": "general goods"}
            ]
        elif city == "Skarport":
            return [
                {"name": "The Arcane Spur", "type": "magical goods"},
                {"name": "Portside Outfitters", "type": "clothing"},
                {"name": "The Golden Scale", "type": "jewelry"}
            ]
        elif city == "Thal-Zirad":
            return [
                {"name": "Artificer's Workshop", "type": "gadgets"},
                {"name": "The Bubbling Cauldron", "type": "alchemy"},
                {"name": "Clockwork Emporium", "type": "mechanical devices"}
            ]
        elif city == "Stonewake":
            return [
                {"name": "The Cracked Anvil", "type": "forge"},
                {"name": "Deep Delver's Supply", "type": "mining equipment"},
                {"name": "Stone's Throw Tavern", "type": "food and drink"}
            ]
        else:
            return [
                {"name": f"{city} General Store", "type": "general goods"},
                {"name": f"{city} Armory", "type": "weapons and armor"},
                {"name": f"{city} Trading Post", "type": "miscellaneous"}
            ]
    
    def _determine_shop_type(self, shop_name: str) -> str:
        """Determine shop type from name."""
        shop_name_lower = shop_name.lower()
        
        if any(term in shop_name_lower for term in ["potion", "elixir", "remedy", "healing", "cauldron"]):
            return "apothecary"
        elif any(term in shop_name_lower for term in ["sword", "armor", "anvil", "forge", "armory"]):
            return "weaponsmith"
        elif any(term in shop_name_lower for term in ["magic", "arcane", "spell", "wizard"]):
            return "magical goods"
        elif any(term in shop_name_lower for term in ["cloth", "outfit", "garment", "tailor"]):
            return "clothing"
        elif any(term in shop_name_lower for term in ["gem", "gold", "silver", "jewel"]):
            return "jewelry"
        elif any(term in shop_name_lower for term in ["device", "gadget", "artifice", "clockwork"]):
            return "gadgets"
        elif any(term in shop_name_lower for term in ["food", "drink", "tavern", "inn"]):
            return "food and drink"
        else:
            return "general goods"
    
    def _generate_shop_inventory(self, city: str, shop_type: str, 
                               relationship_modifier: float) -> List[Dict[str, Any]]:
        """Generate inventory for a shop."""
        inventory = []
        
        # Get city market data
        city_market = self._city_markets.get(city, {})
        regional_modifier = self._regional_modifiers.get(city, 1.0)
        
        # Base items for each shop type
        base_items = {
            "apothecary": [
                {"name": "Minor Healing Potion", "type": "potion", "base_price": 15},
                {"name": "Dream Root Elixir", "type": "elixir", "base_price": 25},
                {"name": "Antidote", "type": "potion", "base_price": 20},
                {"name": "Herbal Salve", "type": "remedy", "base_price": 10},
                {"name": "Vitality Tonic", "type": "potion", "base_price": 30}
            ],
            "weaponsmith": [
                {"name": "Iron Sword", "type": "weapon", "base_price": 20},
                {"name": "Steel Dagger", "type": "weapon", "base_price": 15},
                {"name": "Reinforced Boots", "type": "armor", "base_price": 18},
                {"name": "Leather Armor", "type": "armor", "base_price": 25},
                {"name": "Iron Shield", "type": "armor", "base_price": 22}
            ],
            "magical goods": [
                {"name": "Mana Filter", "type": "magical", "base_price": 45},
                {"name": "Enchanted Textile", "type": "magical", "base_price": 30},
                {"name": "Glowing Crystal", "type": "magical", "base_price": 35},
                {"name": "Arcane Scroll", "type": "magical", "base_price": 40},
                {"name": "Enchanter's Dust", "type": "magical", "base_price": 28}
            ],
            "general goods": [
                {"name": "Traveler's Pack", "type": "gear", "base_price": 12},
                {"name": "Rope (50ft)", "type": "gear", "base_price": 5},
                {"name": "Lantern", "type": "gear", "base_price": 8},
                {"name": "Waterskin", "type": "gear", "base_price": 2},
                {"name": "Rations (1 week)", "type": "consumable", "base_price": 10}
            ]
        }
        
        # Get base items for this shop type
        shop_items = base_items.get(shop_type, base_items["general goods"])
        
        # Add each item with price adjustments
        for item in shop_items:
            item_name = item["name"]
            base_price = item["base_price"]
            
            # Check if we have market data for this item
            item_key = item_name.lower().replace(" ", "_")
            supply_demand_ratio = 1.0
            
            if city_market and "goods" in city_market and item_key in city_market["goods"]:
                supply = city_market["goods"][item_key]["supply"]
                demand = city_market["goods"][item_key]["demand"]
                supply_demand_ratio = (1.0 + (1.0 - supply)) * (1.0 + demand) / 2
            
            # Calculate final price with all modifiers
            price = int(base_price * regional_modifier * supply_demand_ratio * relationship_modifier)
            
            # Add pricing notes
            pricing_notes = []
            if regional_modifier > 1.1:
                pricing_notes.append("prices high due to local economy")
            elif regional_modifier < 0.9:
                pricing_notes.append("prices depressed with economy")
                
            if supply_demand_ratio > 1.2:
                pricing_notes.append("rare due to high demand")
            elif supply_demand_ratio < 0.8:
                pricing_notes.append("common and affordable")
                
            if relationship_modifier < 0.9:
                pricing_notes.append("discounted for you")
                
            # Add quality variations occasionally
            quality = "standard"
            quality_modifier = 1.0
            if random.random() < 0.2:  # 20% chance
                quality = "superior"
                quality_modifier = 1.5
                price = int(price * quality_modifier)
            elif random.random() < 0.1:  # 10% chance
                quality = "masterwork"
                quality_modifier = 2.0
                price = int(price * quality_modifier)
            
            # Create inventory item
            inventory_item = {
                "name": item["name"],
                "type": item["type"],
                "price": price,
                "base_price": base_price,
                "quality": quality,
                "quantity_available": random.randint(1, 10),
                "pricing_notes": pricing_notes
            }
            
            inventory.append(inventory_item)
            
        # Add a few random items
        random_item_count = random.randint(1, 3)
        all_items = [item for items in base_items.values() for item in items]
        random_selections = random.sample(all_items, min(random_item_count, len(all_items)))
        
        for item in random_selections:
            if item["name"] not in [i["name"] for i in inventory]:
                # Calculate price with a bit of randomness
                random_factor = random.uniform(0.9, 1.1)
                price = int(item["base_price"] * regional_modifier * random_factor * relationship_modifier)
                
                inventory_item = {
                    "name": item["name"],
                    "type": item["type"],
                    "price": price,
                    "base_price": item["base_price"],
                    "quality": "standard",
                    "quantity_available": random.randint(1, 5),
                    "pricing_notes": ["special stock"]
                }
                
                inventory.append(inventory_item)
        
        return inventory
    
    def _generate_shop_owner(self, shop_name: str, shop_type: str) -> Dict[str, Any]:
        """Generate a shop owner NPC."""
        # In a real implementation, you'd query a database or use a more sophisticated generator
        
        # Name lists
        first_names = ["Galen", "Thora", "Brandis", "Eliza", "Merric", "Sybil", "Durin", "Isolde", "Fendrel", "Lyra"]
        last_names = ["Thornwood", "Ironfist", "Silverleaf", "Grimtide", "Emberforge", "Nightshade", "Stormborn", "Frostbeard"]
        
        # Generate a name
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate personality traits
        personalities = ["friendly", "stern", "mysterious", "eccentric", "shrewd", "jovial", "suspicious", "wise"]
        personality = random.choice(personalities)
        
        # Determine race
        races = ["human", "elf", "dwarf", "halfling", "gnome", "half-orc", "tiefling"]
        race = random.choice(races)
        
        # Determine age
        age_ranges = ["young", "middle-aged", "older", "elderly"]
        age = random.choice(age_ranges)
        
        # Create shop owner
        owner = {
            "name": full_name,
            "race": race,
            "age": age,
            "personality": personality,
            "occupation": shop_type,
            "shop": shop_name
        }
        
        return owner
    
    def _is_shop_interested_in_item(self, shop_type: str, item_name: str) -> bool:
        """Determine if a shop is interested in an item type."""
        item_lower = item_name.lower()
        
        if shop_type == "apothecary" and any(term in item_lower for term in ["potion", "herb", "ingredient", "elixir"]):
            return True
        elif shop_type == "weaponsmith" and any(term in item_lower for term in ["sword", "dagger", "armor", "shield"]):
            return True
        elif shop_type == "magical goods" and any(term in item_lower for term in ["magic", "enchanted", "scroll", "crystal"]):
            return True
        elif shop_type == "clothing" and any(term in item_lower for term in ["cloth", "garment", "boot", "hat"]):
            return True
        elif shop_type == "jewelry" and any(term in item_lower for term in ["gem", "gold", "silver", "necklace", "ring"]):
            return True
        elif shop_type == "gadgets" and any(term in item_lower for term in ["device", "gadget", "gear", "mechanical"]):
            return True
        elif shop_type == "food and drink" and any(term in item_lower for term in ["food", "drink", "ale", "wine"]):
            return True
            
        return False
    
    def _calculate_business_risk(self, city: str, business_type: str) -> float:
        """Calculate risk level for a business."""
        base_risk = 0.3  # Base risk level
        
        # Adjust for city
        if city in self._city_markets:
            # Higher smuggling activity means higher risk
            base_risk += self._city_markets[city]["smuggling_activity"] * 0.3
            
            # Lower prosperity means higher risk
            base_risk += (1.0 - self._city_markets[city]["prosperity"]) * 0.2
            
        # Adjust for business type
        if business_type.lower() == "caravan":
            base_risk += 0.2  # Caravans are riskier
        elif business_type.lower() in ["shop", "tavern"]:
            base_risk -= 0.1  # Shops and taverns are safer
            
        # Check world state for additional risk factors
        world_summary = world_state_manager.get_current_state_summary()
        
        # Political instability increases risk
        if world_summary["political_stability"] == "unrest":
            base_risk += 0.1
        elif world_summary["political_stability"] == "rebellion":
            base_risk += 0.2
        elif world_summary["political_stability"] == "at war":
            base_risk += 0.3
            
        # Economic problems increase risk
        if world_summary["economic_status"] == "recession":
            base_risk += 0.1
        elif world_summary["economic_status"] == "depression":
            base_risk += 0.2
            
        # Cap risk between 0.1 and 1.0
        return max(0.1, min(1.0, base_risk))
    
    def _get_risk_reason(self, business: Dict[str, Any]) -> str:
        """Get a reason for the business risk level."""
        risk = business["risk"]
        city = business["city"]
        business_type = business["type"]
        
        if risk > 0.7:
            if city in self._city_markets and self._city_markets[city]["smuggling_activity"] > 0.5:
                return "high criminal activity in the area"
            elif business_type.lower() == "caravan":
                return "dangerous routes between cities"
            else:
                return "general economic instability"
        elif risk > 0.3:
            if world_state_manager.political_stability.value == "unrest":
                return "political tensions affecting business"
            else:
                return "normal business risks"
        else:
            if business["reputation"] > 0.7:
                return f"protected by good reputation"
            elif city in self._city_markets and self._city_markets[city]["prosperity"] > 0.7:
                return f"thriving local economy"
            else:
                return "well-established business model"
    
    def _calculate_route_risk(self, origin: str, destination: str) -> float:
        """Calculate risk level for a trade route."""
        base_risk = 0.3  # Base risk level
        
        # Adjust for cities
        if origin in self._city_markets and destination in self._city_markets:
            # Higher smuggling activity means higher risk
            origin_smuggling = self._city_markets[origin]["smuggling_activity"]
            dest_smuggling = self._city_markets[destination]["smuggling_activity"]
            base_risk += (origin_smuggling + dest_smuggling) * 0.2
            
        # Check world state for additional risk factors
        world_summary = world_state_manager.get_current_state_summary()
        
        # Political instability increases risk
        if world_summary["political_stability"] == "unrest":
            base_risk += 0.1
        elif world_summary["political_stability"] == "rebellion":
            base_risk += 0.2
        elif world_summary["political_stability"] == "at war":
            base_risk += 0.3
            
        # Seasonal effects
        if world_summary["current_season"] == "winter":
            base_risk += 0.2  # Winter travel is more dangerous
            
        # Global threats
        if world_summary["active_global_threats"]:
            base_risk += 0.2  # Active threats make travel riskier
            
        # Random factor (routes might have random dangers)
        base_risk += random.uniform(-0.1, 0.1)
            
        # Cap risk between 0.1 and 1.0
        return max(0.1, min(1.0, base_risk))
    
    def _get_risk_level_text(self, risk: float) -> str:
        """Convert risk float to text description."""
        if risk > 0.7:
            return "High"
        elif risk > 0.3:
            return "Medium"
        else:
            return "Low"
    
    def _get_economic_status_description(self, market: Dict[str, Any]) -> str:
        """Get a description of economic activity."""
        prosperity = market["prosperity"]
        
        if prosperity > 0.8:
            return "bustling with activity and wealth"
        elif prosperity > 0.6:
            return "showing signs of healthy commerce"
        elif prosperity > 0.4:
            return "maintaining steady but unremarkable trade"
        elif prosperity > 0.2:
            return "struggling with visible economic hardship"
        else:
            return "suffering severe economic depression"
    
    def _get_price_trend(self, supply: float, demand: float) -> str:
        """Get price trend text based on supply and demand."""
        ratio = demand / supply if supply > 0 else 2.0
        
        if ratio > 1.5:
            return "rapidly rising"
        elif ratio > 1.2:
            return "rising"
        elif ratio > 0.8:
            return "stable"
        elif ratio > 0.5:
            return "falling"
        else:
            return "rapidly falling"
    
    def _generate_venture_suggestions(self, city: str) -> List[str]:
        """Generate venture suggestions for a city."""
        suggestions = []
        
        # Check which goods are in high demand but low supply
        if city in self._city_markets:
            market = self._city_markets[city]
            
            # Find opportunities in this market
            for item_name, data in market["goods"].items():
                if data["demand"] > 0.7 and data["supply"] < 0.4:
                    readable_name = item_name.replace("_", " ").title()
                    
                    # Find a potential source city
                    source_city = None
                    for other_city, other_market in self._city_markets.items():
                        if other_city != city and item_name in other_market["goods"]:
                            if other_market["goods"][item_name]["supply"] > 0.6:
                                source_city = other_city
                                break
                    
                    if source_city:
                        suggestions.append(f"Import {readable_name} from {source_city}")
        
        # Add generic suggestions if we don't have enough
        if len(suggestions) < 2:
            generic_suggestions = [
                f"Invest in local {random.choice(['smithing', 'tailoring', 'alchemy', 'farming'])} businesses",
                f"Look for arbitrage opportunities with {random.choice(list(self._city_markets.keys()))}",
                f"Consider establishing a trade route to a neighboring settlement"
            ]
            
            for suggestion in generic_suggestions:
                if suggestion not in suggestions:
                    suggestions.append(suggestion)
                    if len(suggestions) >= 3:
                        break
        
        return suggestions[:3]  # Return at most 3 suggestions


# Global economy system instance
economy_system = EconomySystem()
