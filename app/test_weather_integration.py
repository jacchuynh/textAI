"""
Weather System Integration Test

This script demonstrates how the Weather System integrates with other game systems
such as combat, magic, NPC behavior, economy, etc.
"""

import logging
import time
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import random

from app.db.base import Base, engine, SessionLocal
from app.models.time_models import GameDateTime, TimeBlock, Season, GameTimeSettings
from app.models.weather_models import (
    WeatherType, PrecipitationType, WindDirection, VisibilityLevel, WeatherEffectType,
    DBWeatherCondition, DBWeatherPattern, DBActiveWeatherEffect
)
from app.services.time_service import TimeService
from app.services.weather_service import WeatherService
from app.events.event_bus import event_bus, EventType, GameEvent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("weather_integration_test")

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Mock services representing other game systems
class MockCombatSystem:
    """Mock combat system that reacts to weather changes."""
    
    def __init__(self):
        self.active_combats = {}
        event_bus.subscribe(EventType.WEATHER_CHANGE, self.handle_weather_change)
        logger.info("Combat System initialized and subscribed to weather changes")
    
    def handle_weather_change(self, event: GameEvent):
        """Handle weather change events and apply combat modifiers."""
        region_id = event.context.get("region_id")
        weather = event.context.get("current_weather_condition", {})
        weather_type = weather.get("weather_type")
        
        # Skip if no active combats in this region
        if region_id not in self.active_combats:
            return
        
        logger.info(f"Combat System: Adjusting combat in {region_id} due to {weather_type} weather")
        
        # Apply weather effects to combat
        if weather_type in ["FOG", "HEAVY_RAIN", "HEAVY_SNOW", "BLIZZARD", "DUST_STORM"]:
            # Reduced visibility affects ranged attacks and perception
            modifier = {"ranged_attack_penalty": -0.3, "perception_penalty": -0.4}
            logger.info(f"Combat System: Applying visibility penalties: {modifier}")
            
        if weather_type in ["HEAVY_RAIN", "HEAVY_SNOW", "BLIZZARD"]:
            # Difficult terrain affects movement and dodge
            modifier = {"movement_penalty": -0.4, "dodge_penalty": -0.2}
            logger.info(f"Combat System: Applying movement penalties: {modifier}")
            
        if weather_type in ["THUNDERSTORM"]:
            # Lightning hazards
            modifier = {"lightning_hazard": 0.1, "electrical_damage_boost": 0.3}
            logger.info(f"Combat System: Adding lightning hazards: {modifier}")
            
        # Update all combats in this region with the new modifiers
        for combat_id in self.active_combats[region_id]:
            logger.info(f"Combat System: Updated combat {combat_id} with weather modifiers")
    
    def start_combat(self, combat_id: str, region_id: str, participants: list):
        """Start a new combat encounter."""
        if region_id not in self.active_combats:
            self.active_combats[region_id] = set()
        
        self.active_combats[region_id].add(combat_id)
        logger.info(f"Combat System: Started combat {combat_id} in {region_id} with {len(participants)} participants")
    
    def end_combat(self, combat_id: str, region_id: str):
        """End a combat encounter."""
        if region_id in self.active_combats and combat_id in self.active_combats[region_id]:
            self.active_combats[region_id].remove(combat_id)
            logger.info(f"Combat System: Ended combat {combat_id} in {region_id}")

class MockMagicSystem:
    """Mock magic system that reacts to weather changes."""
    
    def __init__(self):
        self.elemental_affinities = {
            "RAIN": ["WATER", "LIGHTNING"],
            "SNOW": ["WATER", "ICE"],
            "THUNDERSTORM": ["LIGHTNING", "AIR"],
            "BLIZZARD": ["ICE", "WATER", "AIR"],
            "CLEAR": ["FIRE", "LIGHT"],
            "FOG": ["WATER", "DARKNESS"],
            "DUST_STORM": ["EARTH", "AIR"]
        }
        self.active_spells = {}
        event_bus.subscribe(EventType.WEATHER_CHANGE, self.handle_weather_change)
        logger.info("Magic System initialized and subscribed to weather changes")
    
    def handle_weather_change(self, event: GameEvent):
        """Handle weather change events and apply magic modifiers."""
        region_id = event.context.get("region_id")
        weather = event.context.get("current_weather_condition", {})
        weather_type = weather.get("weather_type")
        precip_type = weather.get("precipitation_type")
        
        logger.info(f"Magic System: Weather changed to {weather_type} in {region_id}")
        
        # Determine which elements are enhanced and which are suppressed
        enhanced_elements = []
        suppressed_elements = []
        
        # Check precipitation type
        if precip_type == "RAIN":
            enhanced_elements.extend(["WATER", "LIGHTNING"])
            suppressed_elements.append("FIRE")
        elif precip_type == "SNOW":
            enhanced_elements.extend(["WATER", "ICE"])
            suppressed_elements.append("FIRE")
        
        # Check weather type
        if weather_type == "THUNDERSTORM":
            enhanced_elements.extend(["LIGHTNING", "AIR"])
        elif weather_type == "BLIZZARD":
            enhanced_elements.extend(["ICE", "WATER", "AIR"])
        elif weather_type == "CLEAR":
            enhanced_elements.extend(["FIRE", "LIGHT"])
        elif weather_type == "FOG":
            enhanced_elements.extend(["WATER", "DARKNESS"])
        elif weather_type == "DUST_STORM":
            enhanced_elements.extend(["EARTH", "AIR"])
        
        # Remove duplicates
        enhanced_elements = list(set(enhanced_elements))
        suppressed_elements = list(set(suppressed_elements))
        
        if enhanced_elements:
            logger.info(f"Magic System: Enhanced elements: {', '.join(enhanced_elements)}")
        if suppressed_elements:
            logger.info(f"Magic System: Suppressed elements: {', '.join(suppressed_elements)}")
        
        # Apply to active spells in the region
        if region_id in self.active_spells:
            for spell_id, spell_data in self.active_spells[region_id].items():
                spell_element = spell_data.get("element")
                
                if spell_element in enhanced_elements:
                    logger.info(f"Magic System: Spell {spell_id} ({spell_element}) enhanced by weather")
                elif spell_element in suppressed_elements:
                    logger.info(f"Magic System: Spell {spell_id} ({spell_element}) suppressed by weather")
    
    def cast_spell(self, spell_id: str, caster_id: str, region_id: str, spell_name: str, element: str):
        """Cast a spell in a region."""
        if region_id not in self.active_spells:
            self.active_spells[region_id] = {}
        
        self.active_spells[region_id][spell_id] = {
            "caster_id": caster_id,
            "spell_name": spell_name,
            "element": element,
            "cast_time": datetime.utcnow()
        }
        
        logger.info(f"Magic System: Spell {spell_id} ({spell_name}, {element}) cast in {region_id}")
    
    def end_spell(self, spell_id: str, region_id: str):
        """End a spell effect."""
        if region_id in self.active_spells and spell_id in self.active_spells[region_id]:
            del self.active_spells[region_id][spell_id]
            logger.info(f"Magic System: Spell {spell_id} ended in {region_id}")

class MockNPCSystem:
    """Mock NPC system that reacts to weather changes."""
    
    def __init__(self):
        self.npcs = {}
        self.weather_behaviors = {
            "HEAVY_RAIN": "seek_shelter",
            "HEAVY_SNOW": "seek_shelter",
            "BLIZZARD": "seek_shelter",
            "THUNDERSTORM": "seek_shelter",
            "DUST_STORM": "seek_shelter",
            "CLEAR": "outdoor_activities",
            "PARTLY_CLOUDY": "outdoor_activities",
            "LIGHT_RAIN": "carry_umbrella",
            "LIGHT_SNOW": "wear_warm_clothes",
            "FOG": "move_cautiously",
            "WINDY": "secure_belongings",
            "GALE": "seek_shelter"
        }
        event_bus.subscribe(EventType.WEATHER_CHANGE, self.handle_weather_change)
        logger.info("NPC System initialized and subscribed to weather changes")
    
    def handle_weather_change(self, event: GameEvent):
        """Handle weather change events and update NPC behaviors."""
        region_id = event.context.get("region_id")
        weather = event.context.get("current_weather_condition", {})
        weather_type = weather.get("weather_type")
        temperature = weather.get("temperature", 0)
        
        # Skip if no NPCs in this region
        if region_id not in self.npcs:
            return
        
        logger.info(f"NPC System: Weather changed to {weather_type} in {region_id}")
        
        # Determine appropriate behavior
        behavior = self.weather_behaviors.get(weather_type, "normal_activities")
        
        # Apply temperature considerations
        if temperature < 0 and behavior != "seek_shelter":
            behavior = "wear_warm_clothes"
        elif temperature > 30 and behavior != "seek_shelter":
            behavior = "seek_shade"
        
        # Update all NPCs in the region
        for npc_id in self.npcs[region_id]:
            logger.info(f"NPC System: {npc_id} is now {behavior} due to {weather_type} weather")
            # In a real system, this would update the NPC's behavior state and schedule
    
    def spawn_npc(self, npc_id: str, npc_name: str, region_id: str):
        """Spawn an NPC in a region."""
        if region_id not in self.npcs:
            self.npcs[region_id] = set()
        
        self.npcs[region_id].add(npc_id)
        logger.info(f"NPC System: Spawned {npc_name} ({npc_id}) in {region_id}")
    
    def move_npc(self, npc_id: str, from_region: str, to_region: str):
        """Move an NPC from one region to another."""
        if from_region in self.npcs and npc_id in self.npcs[from_region]:
            self.npcs[from_region].remove(npc_id)
            
            if to_region not in self.npcs:
                self.npcs[to_region] = set()
            
            self.npcs[to_region].add(npc_id)
            logger.info(f"NPC System: Moved {npc_id} from {from_region} to {to_region}")

class MockEconomySystem:
    """Mock economy system that reacts to weather changes."""
    
    def __init__(self):
        self.regional_markets = {}
        self.weather_price_modifiers = {
            "HEAVY_RAIN": {"umbrellas": 1.5, "boats": 1.3, "crops": 0.8},
            "HEAVY_SNOW": {"warm_clothes": 1.5, "firewood": 1.4, "sleds": 1.3},
            "BLIZZARD": {"warm_clothes": 2.0, "firewood": 1.8, "food": 1.5},
            "THUNDERSTORM": {"umbrellas": 1.5, "lightning_rods": 1.4},
            "DUST_STORM": {"masks": 1.8, "water": 1.5, "cleaning_supplies": 1.3},
            "CLEAR": {"outdoor_equipment": 1.2, "sunglasses": 1.3},
            "LIGHT_RAIN": {"umbrellas": 1.2},
            "LIGHT_SNOW": {"warm_clothes": 1.2, "sleds": 1.1}
        }
        self.weather_production_modifiers = {
            "HEAVY_RAIN": {"farming": 0.7, "logging": 0.6, "mining": 0.8},
            "HEAVY_SNOW": {"farming": 0.5, "logging": 0.7, "fishing": 0.6},
            "BLIZZARD": {"farming": 0.3, "logging": 0.4, "mining": 0.5, "fishing": 0.3},
            "THUNDERSTORM": {"farming": 0.6, "logging": 0.5, "fishing": 0.4},
            "DUST_STORM": {"farming": 0.4, "logging": 0.6, "mining": 0.7},
            "CLEAR": {"farming": 1.2, "logging": 1.1, "fishing": 1.2},
            "LIGHT_RAIN": {"farming": 1.1},
            "LIGHT_SNOW": {"farming": 0.9, "logging": 0.9}
        }
        event_bus.subscribe(EventType.WEATHER_CHANGE, self.handle_weather_change)
        logger.info("Economy System initialized and subscribed to weather changes")
    
    def handle_weather_change(self, event: GameEvent):
        """Handle weather change events and update economy."""
        region_id = event.context.get("region_id")
        weather = event.context.get("current_weather_condition", {})
        weather_type = weather.get("weather_type")
        
        # Skip if no market in this region
        if region_id not in self.regional_markets:
            return
        
        logger.info(f"Economy System: Weather changed to {weather_type} in {region_id}")
        
        # Update prices based on weather
        price_modifiers = self.weather_price_modifiers.get(weather_type, {})
        for item, modifier in price_modifiers.items():
            logger.info(f"Economy System: Price of {item} adjusted by x{modifier} due to {weather_type}")
        
        # Update production rates based on weather
        production_modifiers = self.weather_production_modifiers.get(weather_type, {})
        for activity, modifier in production_modifiers.items():
            logger.info(f"Economy System: {activity} productivity adjusted by x{modifier} due to {weather_type}")
    
    def create_market(self, region_id: str):
        """Create a market in a region."""
        self.regional_markets[region_id] = {
            "items": {
                "umbrellas": {"base_price": 10, "stock": 20},
                "warm_clothes": {"base_price": 25, "stock": 15},
                "boats": {"base_price": 100, "stock": 5},
                "sleds": {"base_price": 50, "stock": 8},
                "firewood": {"base_price": 5, "stock": 50},
                "food": {"base_price": 8, "stock": 100},
                "water": {"base_price": 2, "stock": 200},
                "masks": {"base_price": 5, "stock": 30},
                "cleaning_supplies": {"base_price": 12, "stock": 25},
                "outdoor_equipment": {"base_price": 40, "stock": 10},
                "sunglasses": {"base_price": 15, "stock": 15},
                "lightning_rods": {"base_price": 80, "stock": 3}
            },
            "production": {
                "farming": {"base_rate": 10, "workers": 5},
                "logging": {"base_rate": 8, "workers": 3},
                "mining": {"base_rate": 5, "workers": 2},
                "fishing": {"base_rate": 12, "workers": 4}
            }
        }
        logger.info(f"Economy System: Created market in {region_id}")

def run_integration_test():
    """Run a demonstration of weather integration with other systems."""
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create game time settings
        settings = GameTimeSettings()
        
        # Create a time service for a specific game
        game_id = "integration_test_001"
        time_service = TimeService(db, settings, game_id)
        
        # Create a weather service
        weather_service = WeatherService(db, time_service)
        
        # Initialize mock systems
        combat_system = MockCombatSystem()
        magic_system = MockMagicSystem()
        npc_system = MockNPCSystem()
        economy_system = MockEconomySystem()
        
        # Set up test regions with default weather patterns
        regions = ["forest_region", "mountain_region", "coastal_region", "desert_region"]
        
        for region_id in regions:
            for season in ["SPRING", "SUMMER", "AUTUMN", "WINTER"]:
                # Create weather patterns
                pattern_data = {
                    "region_id": region_id,
                    "season": season,
                    "weather_type_probabilities": {
                        "CLEAR": 0.3,
                        "PARTLY_CLOUDY": 0.2,
                        "CLOUDY": 0.1,
                        "LIGHT_RAIN": 0.1,
                        "HEAVY_RAIN": 0.05,
                        "THUNDERSTORM": 0.05,
                        "FOG": 0.05,
                        "LIGHT_SNOW": 0.05,
                        "HEAVY_SNOW": 0.05,
                        "BLIZZARD": 0.01,
                        "WINDY": 0.03,
                        "GALE": 0.01,
                        "DUST_STORM": 0.01,
                        "HAIL": 0.01
                    },
                    "temperature_base_min": 10,
                    "temperature_base_max": 25,
                    "humidity_range_min": 0.3,
                    "humidity_range_max": 0.8,
                    "default_wind_speeds": {
                        "min": 5.0,
                        "max": 15.0,
                        "gust_chance": 0.1,
                        "gust_max_multiplier": 1.5
                    },
                    "precipitation_chances": {
                        "NONE": 0.7,
                        "RAIN": 0.2,
                        "SNOW": 0.05,
                        "HAIL": 0.05
                    },
                    "cloud_cover_range_min": 0.0,
                    "cloud_cover_range_max": 1.0,
                    "transition_matrices": {}  # This would be populated in a real implementation
                }
                
                # Check if pattern already exists
                existing = db.query(DBWeatherPattern).filter(
                    DBWeatherPattern.region_id == region_id,
                    DBWeatherPattern.season == season
                ).first()
                
                if not existing:
                    pattern = DBWeatherPattern(**pattern_data)
                    db.add(pattern)
        
        # Commit changes
        db.commit()
        logger.info("Weather patterns created for test regions")
        
        # Set up game entities
        # Create NPCs
        npc_system.spawn_npc("npc_001", "Forest Guardian", "forest_region")
        npc_system.spawn_npc("npc_002", "Mountain Guide", "mountain_region")
        npc_system.spawn_npc("npc_003", "Fisherman", "coastal_region")
        npc_system.spawn_npc("npc_004", "Desert Nomad", "desert_region")
        
        # Create markets
        for region in regions:
            economy_system.create_market(region)
        
        # Get current time state
        current_dt = time_service.get_current_datetime()
        current_block = time_service.get_current_time_block()
        current_season = time_service.get_current_season()
        
        logger.info("\n=== INITIAL GAME STATE ===")
        logger.info(f"Current DateTime: {current_dt.format()}")
        logger.info(f"Current TimeBlock: {current_block.value}")
        logger.info(f"Current Season: {current_season.value}")
        
        # Generate initial weather for all regions
        logger.info("\n=== GENERATING INITIAL WEATHER ===")
        results = weather_service.update_weather_for_all_regions()
        logger.info(f"Generated weather for {len(results)} regions")
        
        # Run scenarios demonstrating integration
        logger.info("\n=== SCENARIO 1: COMBAT IN RAIN ===")
        # Force rainy weather in forest region
        forest_pattern = db.query(DBWeatherPattern).filter(
            DBWeatherPattern.region_id == "forest_region",
            DBWeatherPattern.season == current_season.value
        ).first()
        
        if forest_pattern:
            # Temporarily modify pattern to guarantee rain
            original_probs = forest_pattern.weather_type_probabilities.copy()
            forest_pattern.weather_type_probabilities = {
                "HEAVY_RAIN": 1.0
            }
            db.commit()
            
            # Update weather
            weather_service._calculate_and_apply_new_weather_for_region("forest_region")
            
            # Start a combat
            combat_system.start_combat("combat_001", "forest_region", ["player_001", "npc_001", "enemy_001"])
            
            # Wait for events to propagate
            time.sleep(1)
            
            # Restore original probabilities
            forest_pattern.weather_type_probabilities = original_probs
            db.commit()
        
        logger.info("\n=== SCENARIO 2: SPELLCASTING IN THUNDERSTORM ===")
        # Force thunderstorm in mountain region
        mountain_pattern = db.query(DBWeatherPattern).filter(
            DBWeatherPattern.region_id == "mountain_region",
            DBWeatherPattern.season == current_season.value
        ).first()
        
        if mountain_pattern:
            # Temporarily modify pattern to guarantee thunderstorm
            original_probs = mountain_pattern.weather_type_probabilities.copy()
            mountain_pattern.weather_type_probabilities = {
                "THUNDERSTORM": 1.0
            }
            db.commit()
            
            # Update weather
            weather_service._calculate_and_apply_new_weather_for_region("mountain_region")
            
            # Cast some spells
            magic_system.cast_spell("spell_001", "player_001", "mountain_region", "Fireball", "FIRE")
            magic_system.cast_spell("spell_002", "player_001", "mountain_region", "Lightning Bolt", "LIGHTNING")
            
            # Wait for events to propagate
            time.sleep(1)
            
            # Restore original probabilities
            mountain_pattern.weather_type_probabilities = original_probs
            db.commit()
        
        logger.info("\n=== SCENARIO 3: ECONOMY DURING BLIZZARD ===")
        # Force blizzard in coastal region
        coastal_pattern = db.query(DBWeatherPattern).filter(
            DBWeatherPattern.region_id == "coastal_region",
            DBWeatherPattern.season == current_season.value
        ).first()
        
        if coastal_pattern:
            # Temporarily modify pattern to guarantee blizzard
            original_probs = coastal_pattern.weather_type_probabilities.copy()
            coastal_pattern.weather_type_probabilities = {
                "BLIZZARD": 1.0
            }
            db.commit()
            
            # Update weather
            weather_service._calculate_and_apply_new_weather_for_region("coastal_region")
            
            # Wait for events to propagate
            time.sleep(1)
            
            # Restore original probabilities
            coastal_pattern.weather_type_probabilities = original_probs
            db.commit()
        
        logger.info("\n=== SCENARIO 4: NPC BEHAVIOR IN DUST STORM ===")
        # Force dust storm in desert region
        desert_pattern = db.query(DBWeatherPattern).filter(
            DBWeatherPattern.region_id == "desert_region",
            DBWeatherPattern.season == current_season.value
        ).first()
        
        if desert_pattern:
            # Temporarily modify pattern to guarantee dust storm
            original_probs = desert_pattern.weather_type_probabilities.copy()
            desert_pattern.weather_type_probabilities = {
                "DUST_STORM": 1.0
            }
            db.commit()
            
            # Update weather
            weather_service._calculate_and_apply_new_weather_for_region("desert_region")
            
            # Wait for events to propagate
            time.sleep(1)
            
            # Restore original probabilities
            desert_pattern.weather_type_probabilities = original_probs
            db.commit()
        
        logger.info("\n=== SCENARIO 5: TIME PROGRESSION AND SEASONAL CHANGES ===")
        
        # Advance through several time periods
        for i in range(3):
            logger.info(f"\n--- Time Advancement #{i+1} ---")
            
            # Advance a significant amount of time
            if i == 0:
                # Advance to next time block
                next_block = time_service.get_next_time_block()
                minutes = time_service.calculate_time_until_block(next_block)
                logger.info(f"Advancing {minutes} minutes to reach {next_block.value} time block")
                new_dt = time_service.advance_until_block(next_block)
            elif i == 1:
                # Advance a month (approximate)
                days = 30
                minutes = days * 24 * 60
                logger.info(f"Advancing {minutes} minutes ({days} days)")
                new_dt = time_service.advance_minutes(minutes)
            else:
                # Advance to next season (approximate)
                days = 90
                minutes = days * 24 * 60
                logger.info(f"Advancing {minutes} minutes ({days} days)")
                new_dt = time_service.advance_minutes(minutes)
            
            # Display new time state
            current_block = time_service.get_current_time_block()
            current_season = time_service.get_current_season()
            logger.info(f"New DateTime: {new_dt.format()}")
            logger.info(f"New TimeBlock: {current_block.value}")
            logger.info(f"Current Season: {current_season.value}")
            
            # Update weather for all regions
            results = weather_service.update_weather_for_all_regions()
            logger.info(f"Updated weather for {len(results)} regions")
            
            # Wait for events to propagate
            time.sleep(1)
        
        logger.info("\n=== INTEGRATION TEST COMPLETE ===")
        logger.info("The Weather System successfully integrates with other game systems")
        logger.info("Weather changes trigger appropriate responses in combat, magic, NPCs, and economy")
        
    finally:
        # Clean up
        db.close()

if __name__ == "__main__":
    logger.info("Starting Weather Integration Test")
    run_integration_test()