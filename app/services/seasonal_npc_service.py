
"""
Seasonal NPC Service

This module manages how NPCs adapt their behavior, schedules, and dialogue
based on seasonal changes.
"""

import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from app.models.time_models import Season, TimeBlock
from app.models.season_models import SeasonChangeEvent, SeasonalSchedule
from app.events.event_bus import event_bus, EventType

logger = logging.getLogger(__name__)


class NPCRole(str, Enum):
    """NPC role types that have different seasonal behaviors."""
    FARMER = "farmer"
    MERCHANT = "merchant"
    GUARD = "guard"
    BLACKSMITH = "blacksmith"
    INNKEEPER = "innkeeper"
    HUNTER = "hunter"
    HERBALIST = "herbalist"
    SCHOLAR = "scholar"
    PRIEST = "priest"


class SeasonalNPCService:
    """Service for managing seasonal NPC behavior changes."""
    
    def __init__(self, db: Session, game_id: str):
        self.db = db
        self.game_id = game_id
        
        # Subscribe to seasonal change events
        event_bus.subscribe(EventType.SEASON_CHANGED, self._handle_season_change)
        
        # Initialize seasonal schedules and behaviors
        self.seasonal_schedules = self._initialize_seasonal_schedules()
        self.seasonal_dialogue = self._initialize_seasonal_dialogue()
        self.seasonal_appearances = self._initialize_seasonal_appearances()
        
        self.current_season = Season.SPRING
    
    def _initialize_seasonal_schedules(self) -> Dict[NPCRole, Dict[Season, SeasonalSchedule]]:
        """Initialize seasonal schedules for different NPC roles."""
        return {
            NPCRole.FARMER: {
                Season.SPRING: SeasonalSchedule(
                    schedule_id="farmer_spring",
                    season=Season.SPRING,
                    daily_activities={
                        "DAWN": "preparing tools and checking soil conditions",
                        "MORNING": "planting crops and tending seedlings",
                        "MIDDAY": "irrigating fields and repairing fences",
                        "AFTERNOON": "continuing planting work",
                        "DUSK": "securing tools and planning tomorrow's work",
                        "EVENING": "resting at home, planning crop rotations"
                    },
                    preferred_locations=["fields", "barn", "tool_shed", "home"],
                    dialogue_tags=["planting", "hope", "growth", "hard_work"],
                    appearance_modifiers={"clothing": "work_clothes", "accessories": "farming_tools"}
                ),
                Season.SUMMER: SeasonalSchedule(
                    schedule_id="farmer_summer",
                    season=Season.SUMMER,
                    daily_activities={
                        "DAWN": "early morning watering to avoid heat",
                        "MORNING": "tending crops and checking for pests",
                        "MIDDAY": "resting in shade, maintaining equipment",
                        "AFTERNOON": "harvesting early crops, weeding",
                        "DUSK": "evening watering and crop inspection",
                        "EVENING": "market planning and record keeping"
                    },
                    preferred_locations=["fields", "shade_areas", "market", "home"],
                    dialogue_tags=["harvest", "heat", "abundance", "market_prices"],
                    appearance_modifiers={"clothing": "light_work_clothes", "accessories": "wide_hat", "condition": "sun_weathered"}
                ),
                Season.AUTUMN: SeasonalSchedule(
                    schedule_id="farmer_autumn",
                    season=Season.AUTUMN,
                    daily_activities={
                        "DAWN": "checking weather for harvest conditions",
                        "MORNING": "harvesting main crops",
                        "MIDDAY": "processing and storing harvest",
                        "AFTERNOON": "continuing harvest work",
                        "DUSK": "securing stored grain and produce",
                        "EVENING": "celebrating harvest, planning winter preparations"
                    },
                    preferred_locations=["fields", "granary", "storage_areas", "tavern"],
                    dialogue_tags=["harvest_festival", "abundance", "winter_prep", "celebration"],
                    appearance_modifiers={"clothing": "warm_work_clothes", "mood": "satisfied"}
                ),
                Season.WINTER: SeasonalSchedule(
                    schedule_id="farmer_winter",
                    season=Season.WINTER,
                    daily_activities={
                        "DAWN": "checking on stored livestock",
                        "MORNING": "maintaining equipment and planning next year",
                        "MIDDAY": "indoor work, repairing tools",
                        "AFTERNOON": "processing preserved foods",
                        "DUSK": "securing animals for the night",
                        "EVENING": "fireside planning and rest"
                    },
                    preferred_locations=["barn", "workshop", "home", "tavern"],
                    dialogue_tags=["winter_rest", "planning", "equipment", "stories"],
                    appearance_modifiers={"clothing": "thick_winter_clothes", "accessories": "heavy_cloak"}
                )
            },
            NPCRole.MERCHANT: {
                Season.SPRING: SeasonalSchedule(
                    schedule_id="merchant_spring",
                    season=Season.SPRING,
                    daily_activities={
                        "DAWN": "reviewing inventory and travel plans",
                        "MORNING": "organizing caravan supplies",
                        "MIDDAY": "conducting business meetings",
                        "AFTERNOON": "negotiating contracts for summer trade",
                        "DUSK": "finalizing shipping arrangements",
                        "EVENING": "entertaining clients and gathering information"
                    },
                    preferred_locations=["market", "warehouse", "tavern", "port"],
                    dialogue_tags=["new_opportunities", "trade_routes", "optimism", "expansion"],
                    appearance_modifiers={"clothing": "travel_ready_attire", "mood": "optimistic"}
                ),
                Season.SUMMER: SeasonalSchedule(
                    schedule_id="merchant_summer",
                    season=Season.SUMMER,
                    daily_activities={
                        "DAWN": "early departure preparations",
                        "MORNING": "traveling or managing remote operations",
                        "MIDDAY": "conducting peak season trade",
                        "AFTERNOON": "managing multiple transactions",
                        "DUSK": "counting profits and planning next moves",
                        "EVENING": "networking and establishing new connections"
                    },
                    preferred_locations=["market", "trade_post", "caravan_routes", "wealthy_districts"],
                    dialogue_tags=["profit", "busy_season", "opportunities", "connections"],
                    appearance_modifiers={"clothing": "fine_merchant_attire", "mood": "busy", "wealth_display": "obvious"}
                ),
                Season.AUTUMN: SeasonalSchedule(
                    schedule_id="merchant_autumn",
                    season=Season.AUTUMN,
                    daily_activities={
                        "DAWN": "preparing for final major trades",
                        "MORNING": "purchasing harvest goods at bulk",
                        "MIDDAY": "negotiating winter storage deals",
                        "AFTERNOON": "finalizing pre-winter contracts",
                        "DUSK": "securing valuable goods for winter",
                        "EVENING": "planning winter business strategy"
                    },
                    preferred_locations=["market", "granary", "warehouse", "guild_hall"],
                    dialogue_tags=["final_deals", "winter_prep", "bulk_buying", "storage"],
                    appearance_modifiers={"clothing": "practical_merchant_wear", "mood": "calculating"}
                ),
                Season.WINTER: SeasonalSchedule(
                    schedule_id="merchant_winter",
                    season=Season.WINTER,
                    daily_activities={
                        "DAWN": "checking on stored inventory",
                        "MORNING": "managing reduced winter operations",
                        "MIDDAY": "indoor business meetings",
                        "AFTERNOON": "planning next year's ventures",
                        "DUSK": "securing premises against weather",
                        "EVENING": "entertaining important clients indoors"
                    },
                    preferred_locations=["warehouse", "office", "tavern", "guild_hall"],
                    dialogue_tags=["winter_business", "planning", "reduced_activity", "patience"],
                    appearance_modifiers={"clothing": "warm_fine_clothes", "mood": "patient"}
                )
            },
            NPCRole.HUNTER: {
                Season.SPRING: SeasonalSchedule(
                    schedule_id="hunter_spring",
                    season=Season.SPRING,
                    daily_activities={
                        "DAWN": "tracking animal migration patterns",
                        "MORNING": "hunting small game and birds",
                        "MIDDAY": "setting traps in new locations",
                        "AFTERNOON": "gathering information about game movements",
                        "DUSK": "checking traps and preparing equipment",
                        "EVENING": "sharing hunting stories and tips"
                    },
                    preferred_locations=["forest", "hunting_paths", "trappers_cabin", "tavern"],
                    dialogue_tags=["animal_behavior", "new_tracks", "spring_hunting", "migration"],
                    appearance_modifiers={"clothing": "light_hunting_gear", "equipment": "tracking_tools"}
                ),
                Season.SUMMER: SeasonalSchedule(
                    schedule_id="hunter_summer",
                    season=Season.SUMMER,
                    daily_activities={
                        "DAWN": "early morning hunting to avoid heat",
                        "MORNING": "fishing in cool streams",
                        "MIDDAY": "resting and maintaining equipment",
                        "AFTERNOON": "gathering medicinal herbs and plants",
                        "DUSK": "evening hunt for nocturnal game",
                        "EVENING": "preserving meat and preparing supplies"
                    },
                    preferred_locations=["forest_streams", "shaded_areas", "hunting_lodge", "herb_patches"],
                    dialogue_tags=["summer_hunting", "preservation", "fishing", "herbs"],
                    appearance_modifiers={"clothing": "minimal_hunting_gear", "condition": "adapted_to_heat"}
                ),
                Season.AUTUMN: SeasonalSchedule(
                    schedule_id="hunter_autumn",
                    season=Season.AUTUMN,
                    daily_activities={
                        "DAWN": "prime hunting time for fattened game",
                        "MORNING": "major hunting expeditions",
                        "MIDDAY": "processing large game kills",
                        "AFTERNOON": "continued hunting - peak season",
                        "DUSK": "securing valuable pelts and meat",
                        "EVENING": "trading with furriers and butchers"
                    },
                    preferred_locations=["deep_forest", "hunting_grounds", "processing_areas", "market"],
                    dialogue_tags=["prime_hunting", "valuable_pelts", "abundance", "trading"],
                    appearance_modifiers={"clothing": "full_hunting_gear", "mood": "satisfied", "wealth": "increased"}
                ),
                Season.WINTER: SeasonalSchedule(
                    schedule_id="hunter_winter",
                    season=Season.WINTER,
                    daily_activities={
                        "DAWN": "checking winter snares and traps",
                        "MORNING": "tracking in snow conditions",
                        "MIDDAY": "ice fishing and winter survival",
                        "AFTERNOON": "hunting winter-active prey",
                        "DUSK": "securing kills from harsh weather",
                        "EVENING": "crafting and repairing gear by fire"
                    },
                    preferred_locations=["winter_hunting_grounds", "ice_fishing_spots", "warm_shelter", "cabin"],
                    dialogue_tags=["winter_survival", "harsh_conditions", "skill", "endurance"],
                    appearance_modifiers={"clothing": "heavy_winter_hunting_gear", "equipment": "winter_specialized"}
                )
            }
        }
    
    def _initialize_seasonal_dialogue(self) -> Dict[Season, Dict[str, List[str]]]:
        """Initialize seasonal dialogue options."""
        return {
            Season.SPRING: {
                "greetings": [
                    "The spring air brings new possibilities!",
                    "What a lovely time of year for new beginnings.",
                    "Can you feel the energy of the awakening world?"
                ],
                "weather_comments": [
                    "The gentle rains are perfect for new growth.",
                    "The warming sun feels wonderful after winter's chill.",
                    "Everything is coming back to life!"
                ],
                "general": [
                    "I love watching the world wake up from winter's sleep.",
                    "There's so much work to be done this season.",
                    "The birds returning always fills my heart with joy."
                ]
            },
            Season.SUMMER: {
                "greetings": [
                    "Beautiful summer day, isn't it?",
                    "The heat can be intense, but the abundance makes it worth it!",
                    "Peak season is always the busiest time."
                ],
                "weather_comments": [
                    "This heat is perfect for ripening crops.",
                    "The long days give us so much time to work.",
                    "A cooling breeze would be welcome right about now."
                ],
                "general": [
                    "Summer is when all our hard work pays off.",
                    "The markets are overflowing with fresh goods.",
                    "Everyone seems more energetic in the warm weather."
                ]
            },
            Season.AUTUMN: {
                "greetings": [
                    "The harvest season greets you well!",
                    "What a time of abundance and preparation.",
                    "The changing leaves remind us time moves ever forward."
                ],
                "weather_comments": [
                    "The crisp air is perfect for heavy work.",
                    "These cool mornings are refreshing after summer's heat.",
                    "The changing colors make even hard work feel magical."
                ],
                "general": [
                    "Harvest time is both rewarding and exhausting.",
                    "We must prepare well for the winter ahead.",
                    "There's a bittersweet beauty to autumn."
                ]
            },
            Season.WINTER: {
                "greetings": [
                    "Winter's peace be with you.",
                    "Stay warm, friend. The cold can be harsh.",
                    "The quiet season has its own rewards."
                ],
                "weather_comments": [
                    "The snow blankets everything in peaceful silence.",
                    "Cold as it is, winter has its own stark beauty.",
                    "A warm fire and good company make winter bearable."
                ],
                "general": [
                    "Winter teaches us patience and reflection.",
                    "The preserved foods from harvest are keeping us well.",
                    "These long nights are perfect for planning and crafting."
                ]
            }
        }
    
    def _initialize_seasonal_appearances(self) -> Dict[Season, Dict[str, Any]]:
        """Initialize seasonal appearance modifications."""
        return {
            Season.SPRING: {
                "general_mood": "hopeful and energetic",
                "clothing_style": "practical with lighter layers",
                "common_accessories": ["light_cloak", "work_gloves", "simple_tools"],
                "color_preferences": ["fresh_green", "earth_brown", "sky_blue"]
            },
            Season.SUMMER: {
                "general_mood": "busy and productive",
                "clothing_style": "light and practical for heat",
                "common_accessories": ["wide_hat", "light_scarf", "cooling_cloth"],
                "color_preferences": ["bright_yellow", "light_blue", "white", "tan"]
            },
            Season.AUTUMN: {
                "general_mood": "satisfied but preparing",
                "clothing_style": "layered for changing temperatures",
                "common_accessories": ["warm_cloak", "harvest_basket", "preservation_tools"],
                "color_preferences": ["deep_orange", "rich_brown", "golden_yellow", "dark_red"]
            },
            Season.WINTER: {
                "general_mood": "patient and contemplative",
                "clothing_style": "heavy and warm",
                "common_accessories": ["thick_cloak", "warm_boots", "hand_warmers", "wool_scarf"],
                "color_preferences": ["deep_blue", "dark_green", "charcoal_gray", "warm_brown"]
            }
        }
    
    def _handle_season_change(self, event: SeasonChangeEvent) -> None:
        """Handle seasonal change events by updating NPC behaviors."""
        if event.context.get("game_id") != self.game_id:
            return
        
        new_season = Season(event.context.get("current_season"))
        self.current_season = new_season
        
        logger.info(f"NPC system responding to seasonal change: {new_season}")
        
        # Update all NPC schedules and behaviors
        self._update_npc_schedules(new_season)
        self._update_npc_appearances(new_season)
        self._trigger_seasonal_npc_events(new_season)
    
    def _update_npc_schedules(self, season: Season) -> None:
        """Update NPC schedules for the new season."""
        for role, seasonal_schedules in self.seasonal_schedules.items():
            if season in seasonal_schedules:
                schedule = seasonal_schedules[season]
                logger.info(f"Updated {role.value} schedule for {season.value}")
                # In a full implementation, this would update NPCs in the database
    
    def _update_npc_appearances(self, season: Season) -> None:
        """Update NPC appearances for the new season."""
        appearance_data = self.seasonal_appearances.get(season, {})
        logger.info(f"Updated NPC appearances for {season.value}: {appearance_data.get('general_mood', 'normal')}")
    
    def _trigger_seasonal_npc_events(self, season: Season) -> None:
        """Trigger season-specific NPC events and festivals."""
        seasonal_events = {
            Season.SPRING: [
                "Farmers gather to bless the planting season",
                "Merchants organize the first trade expeditions",
                "Young people celebrate the spring awakening festival"
            ],
            Season.SUMMER: [
                "The Midsummer Festival brings joy to all",
                "Trade caravans reach peak activity",
                "Outdoor markets expand with abundant goods"
            ],
            Season.AUTUMN: [
                "The Great Harvest Festival unites the community",
                "Hunters return with valuable pelts and meat",
                "Craftsmen display their finest seasonal work"
            ],
            Season.WINTER: [
                "The Winter Solstice brings people together",
                "Storytellers share tales by warm fires",
                "Craftsmen focus on indoor projects and commissions"
            ]
        }
        
        events = seasonal_events.get(season, [])
        for event_description in events:
            logger.info(f"Seasonal NPC event: {event_description}")
    
    def get_npc_schedule(self, npc_role: NPCRole, season: Optional[Season] = None) -> Optional[SeasonalSchedule]:
        """Get the seasonal schedule for an NPC role."""
        if season is None:
            season = self.current_season
        
        return self.seasonal_schedules.get(npc_role, {}).get(season)
    
    def get_seasonal_dialogue(self, dialogue_type: str, season: Optional[Season] = None) -> List[str]:
        """Get seasonal dialogue options."""
        if season is None:
            season = self.current_season
        
        return self.seasonal_dialogue.get(season, {}).get(dialogue_type, [])
    
    def get_npc_activity_for_time(self, npc_role: NPCRole, time_block: TimeBlock, season: Optional[Season] = None) -> str:
        """Get what an NPC should be doing at a specific time of day."""
        schedule = self.get_npc_schedule(npc_role, season)
        if not schedule:
            return "going about their usual business"
        
        return schedule.daily_activities.get(time_block.value, "resting or taking a break")
    
    def get_seasonal_npc_summary(self, season: Optional[Season] = None) -> Dict[str, Any]:
        """Get a summary of seasonal NPC behaviors."""
        if season is None:
            season = self.current_season
        
        appearance_data = self.seasonal_appearances.get(season, {})
        
        return {
            "season": season.value,
            "general_mood": appearance_data.get("general_mood", "normal"),
            "clothing_style": appearance_data.get("clothing_style", "practical"),
            "active_schedules": len([role for role in NPCRole if season in self.seasonal_schedules.get(role, {})]),
            "available_dialogue_types": list(self.seasonal_dialogue.get(season, {}).keys())
        }
