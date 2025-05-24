"""
World Event Service

This module manages dynamic world events that affect the game's economy,
such as natural disasters, wars, festivals, and other occurrences that
can change market conditions across regions.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import random
from datetime import datetime, timedelta
import asyncio
from sqlalchemy.orm import Session

# Import models
from backend.src.economy.models.pydantic_models import MarketRegionInfo
from backend.src.economy.models.db_models import (
    DBMarketRegionInfo, DBLocation, DBItem, DBCharacter, DBShop, DBResource, DBBusiness
)

# Import Celery integration for async processing
from backend.src.narrative_engine.celery_integration import NarrativeEngineCeleryIntegration
from backend.src.narrative_engine.event_bus import get_event_bus, Event

logger = logging.getLogger(__name__)

class WorldEventService:
    """
    Service for managing world events that impact the economy.
    """
    
    def __init__(self):
        """Initialize the world event service."""
        self.logger = logging.getLogger("WorldEventService")
        self.event_bus = get_event_bus()
        
        # Initialize Celery integration for async operations
        self.celery_integration = NarrativeEngineCeleryIntegration()
        
        # Subscribe to relevant events
        self.event_bus.subscribe("world_event_triggered", self._handle_world_event)
        self.event_bus.subscribe("festival_start", self._handle_festival_start)
        self.event_bus.subscribe("war_declaration", self._handle_war_declaration)
        
        # Event types and their probabilities
        self.event_types = {
            "natural_disaster": 0.1,
            "trade_boom": 0.15,
            "resource_discovery": 0.2,
            "bandit_activity": 0.15,
            "festival": 0.2,
            "disease_outbreak": 0.1,
            "technological_breakthrough": 0.1
        }
    
    async def generate_random_event(self,
                                 db: Session,
                                 region_id: Optional[str] = None,
                                 specific_event_type: Optional[str] = None,
                                 async_processing: bool = True) -> Dict[str, Any]:
        """
        Generate a random world event.
        
        Args:
            db: Database session
            region_id: Optional specific region for the event
            specific_event_type: Optional specific event type
            async_processing: Whether to process asynchronously
            
        Returns:
            Event information
        """
        # If no region specified, pick a random one
        if not region_id:
            regions = db.query(DBMarketRegionInfo).all()
            if not regions:
                return {"error": "No regions found in the database"}
            
            # Select a random region
            region = random.choice(regions)
            region_id = region.region_id
        else:
            # Get the specified region
            region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
            if not region:
                return {"error": f"Region {region_id} not found"}
        
        # Determine event type
        if specific_event_type and specific_event_type in self.event_types:
            event_type = specific_event_type
        else:
            # Weighted random selection
            event_type = self._weighted_random_event_type()
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.process_world_event_task",
                task_args=[region_id, event_type],
                task_kwargs={}
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "generate_world_event",
                "region_id": region_id,
                "event_type": event_type,
                "status": "processing",
                "message": f"World event '{event_type}' dispatched for asynchronous processing"
            }
        
        # For synchronous processing, generate the event here
        # This is a simplified implementation
        
        # Generate event details based on type
        event_details = self._generate_event_details(db, region_id, event_type)
        
        # Calculate economic impacts
        economic_impacts = self._calculate_event_economic_impacts(event_type, event_details)
        
        # Apply impacts to the region
        self._apply_event_impacts(db, region_id, economic_impacts)
        
        # Store the event in the region's history
        self._record_event_in_region_history(db, region_id, event_type, event_details, economic_impacts)
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="world_event_triggered",
            data={
                "region_id": region_id,
                "event_type": event_type,
                "event_details": event_details,
                "economic_impacts": economic_impacts,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="world_event_service"
        ))
        
        return {
            "action": "generate_world_event",
            "status": "success",
            "region_id": region_id,
            "region_name": region.name,
            "event_type": event_type,
            "event_details": event_details,
            "economic_impacts": economic_impacts,
            "duration_days": event_details.get("duration_days", 0)
        }
    
    async def schedule_festival(self,
                             db: Session,
                             region_id: str,
                             festival_name: str,
                             boosted_categories: List[str],
                             duration_days: int = 7,
                             boost_factor: float = 1.5,
                             async_processing: bool = True) -> Dict[str, Any]:
        """
        Schedule a festival event in a region.
        
        Args:
            db: Database session
            region_id: Region identifier
            festival_name: Name of the festival
            boosted_categories: Item categories to boost during festival
            duration_days: How long the festival lasts
            boost_factor: How much to boost trade (1.5 = 50% boost)
            async_processing: Whether to process asynchronously
            
        Returns:
            Festival information
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.schedule_festival_task",
                task_args=[region_id, festival_name],
                task_kwargs={
                    "boosted_categories": boosted_categories,
                    "duration_days": duration_days,
                    "boost_factor": boost_factor
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "schedule_festival",
                "region_id": region_id,
                "festival_name": festival_name,
                "status": "processing",
                "message": f"Festival '{festival_name}' dispatched for asynchronous processing"
            }
        
        # For synchronous processing, schedule the festival here
        # This is a simplified implementation
        
        # Calculate economic impacts
        festival_impacts = {
            "categories": {},
            "prosperity_modifier": 1.1,  # Festivals increase overall prosperity
            "price_modifiers": {},
            "supply_modifiers": {}
        }
        
        # Apply boosts to specified categories
        for category in boosted_categories:
            festival_impacts["price_modifiers"][category] = boost_factor
            festival_impacts["supply_modifiers"][category] = boost_factor * 1.2  # Supply increases more than prices
        
        # Apply impacts to the region
        self._apply_event_impacts(db, region_id, festival_impacts)
        
        # Store the festival in the region's calendar
        custom_data = region.custom_data or {}
        festivals = custom_data.get("festivals", [])
        
        new_festival = {
            "name": festival_name,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
            "boosted_categories": boosted_categories,
            "boost_factor": boost_factor,
            "is_active": True
        }
        
        festivals.append(new_festival)
        custom_data["festivals"] = festivals
        region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="festival_start",
            data={
                "region_id": region_id,
                "region_name": region.name,
                "festival_name": festival_name,
                "boosted_categories": boosted_categories,
                "duration_days": duration_days,
                "boost_factor": boost_factor,
                "economic_impacts": festival_impacts,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="world_event_service"
        ))
        
        return {
            "action": "schedule_festival",
            "status": "success",
            "region_id": region_id,
            "region_name": region.name,
            "festival_name": festival_name,
            "boosted_categories": boosted_categories,
            "duration_days": duration_days,
            "boost_factor": boost_factor,
            "start_date": datetime.utcnow().isoformat(),
            "end_date": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
            "economic_impacts": festival_impacts
        }
    
    async def declare_war(self,
                       db: Session,
                       aggressor_region_id: str,
                       defender_region_id: str,
                       war_intensity: float = 0.7,  # 0.0 to 1.0
                       duration_months: int = 6,
                       async_processing: bool = True) -> Dict[str, Any]:
        """
        Declare war between two regions, affecting their economies.
        
        Args:
            db: Database session
            aggressor_region_id: Region starting the war
            defender_region_id: Region being attacked
            war_intensity: Intensity of the conflict (0.0 to 1.0)
            duration_months: Expected duration in months
            async_processing: Whether to process asynchronously
            
        Returns:
            War declaration information
        """
        # Get the regions
        aggressor = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == aggressor_region_id).first()
        defender = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == defender_region_id).first()
        
        if not aggressor or not defender:
            return {"error": "One or both regions not found"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.declare_war_task",
                task_args=[aggressor_region_id, defender_region_id],
                task_kwargs={
                    "war_intensity": war_intensity,
                    "duration_months": duration_months
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "declare_war",
                "aggressor_region_id": aggressor_region_id,
                "defender_region_id": defender_region_id,
                "status": "processing",
                "message": f"War declaration between {aggressor.name} and {defender.name} dispatched for asynchronous processing"
            }
        
        # For synchronous processing, declare the war here
        # This is a simplified implementation
        
        # Calculate war impacts for aggressor
        aggressor_impacts = {
            "categories": {
                "weapon": {"demand": 2.0, "price": 1.8},
                "armor": {"demand": 1.8, "price": 1.6},
                "food": {"demand": 1.5, "price": 1.4},
                "potion": {"demand": 1.7, "price": 1.5},
                "luxury": {"demand": 0.7, "price": 0.8}  # Luxury items less important during war
            },
            "prosperity_modifier": max(0.5, 1.0 - (war_intensity * 0.3)),  # Wars hurt prosperity
            "price_modifiers": {},
            "supply_modifiers": {}
        }
        
        # Calculate war impacts for defender
        defender_impacts = {
            "categories": {
                "weapon": {"demand": 2.2, "price": 2.0},  # Defenders need weapons more
                "armor": {"demand": 2.0, "price": 1.8},   # Defenders need armor more
                "food": {"demand": 1.8, "price": 1.6},    # Food shortages for defenders
                "potion": {"demand": 1.9, "price": 1.7},
                "luxury": {"demand": 0.5, "price": 0.6}   # Even less luxury demand for defenders
            },
            "prosperity_modifier": max(0.3, 1.0 - (war_intensity * 0.5)),  # Defenders hurt more
            "price_modifiers": {},
            "supply_modifiers": {}
        }
        
        # Apply category impacts to price and supply modifiers
        for impacts, region_impacts in [(aggressor_impacts, aggressor_impacts), (defender_impacts, defender_impacts)]:
            for category, values in impacts["categories"].items():
                region_impacts["price_modifiers"][category] = values["price"]
                region_impacts["supply_modifiers"][category] = values["demand"]
        
        # Apply impacts to both regions
        self._apply_event_impacts(db, aggressor_region_id, aggressor_impacts)
        self._apply_event_impacts(db, defender_region_id, defender_impacts)
        
        # Store the war in both regions' data
        for region_id, region, impacts in [
            (aggressor_region_id, aggressor, aggressor_impacts), 
            (defender_region_id, defender, defender_impacts)
        ]:
            custom_data = region.custom_data or {}
            wars = custom_data.get("wars", [])
            
            is_aggressor = region_id == aggressor_region_id
            
            new_war = {
                "is_aggressor": is_aggressor,
                "opponent_region_id": defender_region_id if is_aggressor else aggressor_region_id,
                "opponent_name": defender.name if is_aggressor else aggressor.name,
                "start_date": datetime.utcnow().isoformat(),
                "expected_end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat(),
                "intensity": war_intensity,
                "is_active": True,
                "economic_impacts": impacts
            }
            
            wars.append(new_war)
            custom_data["wars"] = wars
            region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="war_declaration",
            data={
                "aggressor_region_id": aggressor_region_id,
                "aggressor_name": aggressor.name,
                "defender_region_id": defender_region_id,
                "defender_name": defender.name,
                "war_intensity": war_intensity,
                "duration_months": duration_months,
                "aggressor_impacts": aggressor_impacts,
                "defender_impacts": defender_impacts,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="world_event_service"
        ))
        
        return {
            "action": "declare_war",
            "status": "success",
            "aggressor_region_id": aggressor_region_id,
            "aggressor_name": aggressor.name,
            "defender_region_id": defender_region_id,
            "defender_name": defender.name,
            "war_intensity": war_intensity,
            "duration_months": duration_months,
            "start_date": datetime.utcnow().isoformat(),
            "expected_end_date": (datetime.utcnow() + timedelta(days=duration_months * 30)).isoformat(),
            "aggressor_impacts": aggressor_impacts,
            "defender_impacts": defender_impacts
        }
    
    async def create_natural_disaster(self,
                                   db: Session,
                                   region_id: str,
                                   disaster_type: str,
                                   severity: float = 0.7,  # 0.0 to 1.0
                                   affected_resources: Optional[List[str]] = None,
                                   async_processing: bool = True) -> Dict[str, Any]:
        """
        Create a natural disaster in a region, affecting its economy.
        
        Args:
            db: Database session
            region_id: Region identifier
            disaster_type: Type of disaster (earthquake, flood, drought, etc.)
            severity: Severity of the disaster (0.0 to 1.0)
            affected_resources: Optional list of specific resources to affect
            async_processing: Whether to process asynchronously
            
        Returns:
            Disaster information
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Determine which resources are affected if not specified
        if not affected_resources:
            # Get resources in the region
            resources = db.query(DBResource).join(
                DBLocation, DBResource.location_id == DBLocation.id
            ).filter(
                DBLocation.region_id == region_id
            ).all()
            
            # Select random resources based on severity
            if resources:
                num_affected = max(1, int(len(resources) * severity))
                affected_resources = [resource.id for resource in random.sample(resources, num_affected)]
            else:
                affected_resources = []
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.create_natural_disaster_task",
                task_args=[region_id, disaster_type],
                task_kwargs={
                    "severity": severity,
                    "affected_resources": affected_resources
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "create_natural_disaster",
                "region_id": region_id,
                "disaster_type": disaster_type,
                "status": "processing",
                "message": f"Natural disaster '{disaster_type}' dispatched for asynchronous processing"
            }
        
        # For synchronous processing, create the disaster here
        # This is a simplified implementation
        
        # Determine impact factors based on disaster type
        impact_factors = self._get_disaster_impact_factors(disaster_type)
        
        # Calculate economic impacts
        disaster_impacts = {
            "prosperity_modifier": max(0.2, 1.0 - (severity * impact_factors["prosperity"])),
            "price_modifiers": {},
            "supply_modifiers": {},
            "affected_resources": {}
        }
        
        # Apply impacts to resource categories
        for category, factor in impact_factors["categories"].items():
            price_modifier = 1.0 + (severity * factor["price"])
            supply_modifier = max(0.1, 1.0 - (severity * factor["supply"]))
            
            disaster_impacts["price_modifiers"][category] = price_modifier
            disaster_impacts["supply_modifiers"][category] = supply_modifier
        
        # Apply specific impacts to affected resources
        for resource_id in affected_resources:
            resource = db.query(DBResource).filter(DBResource.id == resource_id).first()
            if not resource:
                continue
                
            # Increase depletion based on severity and disaster type
            resource_depletion = severity * impact_factors.get("resource_depletion", 0.5)
            new_depletion_level = min(1.0, resource.depletion_level + resource_depletion)
            
            # Update the resource
            resource.depletion_level = new_depletion_level
            
            # Record in impacts
            disaster_impacts["affected_resources"][resource_id] = {
                "name": resource.name,
                "old_depletion": resource.depletion_level,
                "new_depletion": new_depletion_level,
                "depletion_increase": resource_depletion
            }
        
        # Apply impacts to the region
        self._apply_event_impacts(db, region_id, disaster_impacts)
        
        # Store the disaster in the region's history
        custom_data = region.custom_data or {}
        disasters = custom_data.get("natural_disasters", [])
        
        new_disaster = {
            "type": disaster_type,
            "severity": severity,
            "date": datetime.utcnow().isoformat(),
            "affected_resources": affected_resources,
            "economic_impacts": disaster_impacts
        }
        
        disasters.append(new_disaster)
        custom_data["natural_disasters"] = disasters
        region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="natural_disaster",
            data={
                "region_id": region_id,
                "region_name": region.name,
                "disaster_type": disaster_type,
                "severity": severity,
                "affected_resources": affected_resources,
                "economic_impacts": disaster_impacts,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="world_event_service"
        ))
        
        recovery_time = int(severity * 30)  # Rough estimate: 1 month for max severity
        
        return {
            "action": "create_natural_disaster",
            "status": "success",
            "region_id": region_id,
            "region_name": region.name,
            "disaster_type": disaster_type,
            "severity": severity,
            "affected_resources_count": len(affected_resources),
            "affected_resources": disaster_impacts["affected_resources"],
            "economic_impacts": {
                "prosperity_change": f"{(disaster_impacts['prosperity_modifier'] - 1.0) * 100:.1f}%",
                "price_changes": {k: f"{(v - 1.0) * 100:.1f}%" for k, v in disaster_impacts["price_modifiers"].items()},
                "supply_changes": {k: f"{(v - 1.0) * 100:.1f}%" for k, v in disaster_impacts["supply_modifiers"].items()}
            },
            "estimated_recovery_time": f"{recovery_time} days"
        }
    
    async def discover_resource(self,
                             db: Session,
                             region_id: str,
                             resource_type: str,
                             abundance: float = 0.7,  # 0.0 to 1.0
                             location_name: Optional[str] = None,
                             async_processing: bool = True) -> Dict[str, Any]:
        """
        Discover a new resource in a region.
        
        Args:
            db: Database session
            region_id: Region identifier
            resource_type: Type of resource discovered
            abundance: How abundant the resource is (0.0 to 1.0)
            location_name: Optional specific location name
            async_processing: Whether to process asynchronously
            
        Returns:
            Resource discovery information
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return {"error": f"Region {region_id} not found"}
        
        # Get or create location
        if location_name:
            location = db.query(DBLocation).filter(
                DBLocation.region_id == region_id,
                DBLocation.name == location_name
            ).first()
        else:
            # Get random location in the region
            locations = db.query(DBLocation).filter(DBLocation.region_id == region_id).all()
            if locations:
                location = random.choice(locations)
                location_name = location.name
            else:
                return {"error": f"No locations found in region {region_id}"}
        
        if not location:
            return {"error": f"Location {location_name} not found in region {region_id}"}
        
        # Use Celery for async processing
        if async_processing:
            task_info = await self.celery_integration.dispatch_custom_task(
                task_name="backend.src.economy.tasks.discover_resource_task",
                task_args=[region_id, resource_type],
                task_kwargs={
                    "abundance": abundance,
                    "location_id": location.id
                }
            )
            
            return {
                "task_id": task_info.get("task_id", "unknown"),
                "action": "discover_resource",
                "region_id": region_id,
                "resource_type": resource_type,
                "location_name": location_name,
                "status": "processing",
                "message": f"Resource discovery '{resource_type}' dispatched for asynchronous processing"
            }
        
        # For synchronous processing, create the resource here
        # This is a simplified implementation
        
        # Generate a unique ID for the resource
        resource_id = f"{resource_type}-{region_id}-{datetime.utcnow().timestamp()}"
        
        # Create resource name
        resource_name = f"{location_name} {resource_type.capitalize()}"
        
        # Determine products based on resource type
        products = self._get_resource_products(db, resource_type)
        
        # Calculate max yield based on abundance
        max_yield = abundance * 100.0  # Simple calculation
        
        # Create the resource
        new_resource = DBResource(
            id=resource_id,
            name=resource_name,
            description=f"A {resource_type} discovered in {location_name}",
            location_id=location.id,
            resource_type=resource_type,
            depletion_level=0.0,  # New resource, not depleted
            max_yield=max_yield,
            regeneration_rate=0.01,  # 1% regeneration per day
            extraction_difficulty=max(0.1, 1.0 - abundance),  # Inverse of abundance
            products=products,
            custom_data={"discovery_date": datetime.utcnow().isoformat()}
        )
        
        db.add(new_resource)
        
        # Calculate economic impacts
        discovery_impacts = {
            "prosperity_modifier": 1.0 + (abundance * 0.2),  # Resource discoveries boost prosperity
            "price_modifiers": {},
            "supply_modifiers": {}
        }
        
        # Affect prices of items produced from this resource
        affected_categories = set()
        for item_id, yield_rate in products.items():
            item = db.query(DBItem).filter(DBItem.id == item_id).first()
            if item:
                affected_categories.add(item.category)
                
                # Resource discovery lowers prices and increases supply
                discovery_impacts["price_modifiers"][item_id] = max(0.5, 1.0 - (abundance * 0.3))
                discovery_impacts["supply_modifiers"][item_id] = 1.0 + (abundance * 0.5)
        
        # Apply category-level impacts
        for category in affected_categories:
            discovery_impacts["price_modifiers"][category] = max(0.7, 1.0 - (abundance * 0.2))
            discovery_impacts["supply_modifiers"][category] = 1.0 + (abundance * 0.3)
        
        # Apply impacts to the region
        self._apply_event_impacts(db, region_id, discovery_impacts)
        
        # Store the discovery in the region's history
        custom_data = region.custom_data or {}
        discoveries = custom_data.get("resource_discoveries", [])
        
        new_discovery = {
            "resource_id": resource_id,
            "resource_name": resource_name,
            "resource_type": resource_type,
            "location_id": location.id,
            "location_name": location_name,
            "abundance": abundance,
            "discovery_date": datetime.utcnow().isoformat(),
            "products": products
        }
        
        discoveries.append(new_discovery)
        custom_data["resource_discoveries"] = discoveries
        region.custom_data = custom_data
        
        # Commit changes
        db.commit()
        
        # Publish event
        self.event_bus.publish(Event(
            event_type="resource_discovery",
            data={
                "region_id": region_id,
                "region_name": region.name,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "resource_type": resource_type,
                "location_id": location.id,
                "location_name": location_name,
                "abundance": abundance,
                "economic_impacts": discovery_impacts,
                "timestamp": datetime.utcnow().isoformat()
            },
            source="world_event_service"
        ))
        
        return {
            "action": "discover_resource",
            "status": "success",
            "region_id": region_id,
            "region_name": region.name,
            "resource_id": resource_id,
            "resource_name": resource_name,
            "resource_type": resource_type,
            "location_id": location.id,
            "location_name": location_name,
            "abundance": abundance,
            "max_yield": max_yield,
            "products": products,
            "economic_impacts": {
                "prosperity_change": f"+{(discovery_impacts['prosperity_modifier'] - 1.0) * 100:.1f}%",
                "price_changes": {k: f"{(v - 1.0) * 100:.1f}%" for k, v in discovery_impacts["price_modifiers"].items() if isinstance(k, str)},
                "supply_changes": {k: f"+{(v - 1.0) * 100:.1f}%" for k, v in discovery_impacts["supply_modifiers"].items() if isinstance(k, str)}
            }
        }
    
    def _weighted_random_event_type(self) -> str:
        """
        Select a random event type based on weighted probabilities.
        
        Returns:
            Event type
        """
        # Normalize probabilities
        total = sum(self.event_types.values())
        normalized = {k: v / total for k, v in self.event_types.items()}
        
        # Cumulative distribution
        cumulative = 0
        r = random.random()
        for event_type, probability in normalized.items():
            cumulative += probability
            if r <= cumulative:
                return event_type
        
        # Fallback
        return list(self.event_types.keys())[0]
    
    def _generate_event_details(self, db: Session, region_id: str, event_type: str) -> Dict[str, Any]:
        """
        Generate details for a specific event type.
        
        Args:
            db: Database session
            region_id: Region identifier
            event_type: Type of event
            
        Returns:
            Event details
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        
        # Generate details based on event type
        if event_type == "natural_disaster":
            disasters = ["earthquake", "flood", "drought", "fire", "blizzard", "hurricane"]
            disaster_type = random.choice(disasters)
            severity = random.uniform(0.3, 0.9)
            
            return {
                "disaster_type": disaster_type,
                "severity": severity,
                "description": f"A {disaster_type} has struck {region.name} with {severity:.1f} severity!",
                "duration_days": int(severity * 30)  # Higher severity means longer recovery
            }
            
        elif event_type == "trade_boom":
            duration_days = random.randint(7, 30)
            prosperity_boost = random.uniform(0.1, 0.3)
            
            return {
                "prosperity_boost": prosperity_boost,
                "description": f"A trade boom has begun in {region.name}, increasing prosperity!",
                "duration_days": duration_days
            }
            
        elif event_type == "resource_discovery":
            resource_types = ["gold_vein", "iron_deposit", "gemstone_deposit", "forest", "fertile_land", "magical_spring"]
            resource_type = random.choice(resource_types)
            abundance = random.uniform(0.4, 0.9)
            
            return {
                "resource_type": resource_type,
                "abundance": abundance,
                "description": f"A new {resource_type.replace('_', ' ')} has been discovered in {region.name}!",
                "duration_days": 0  # Permanent effect
            }
            
        elif event_type == "bandit_activity":
            severity = random.uniform(0.2, 0.8)
            duration_days = random.randint(3, 21)
            
            return {
                "severity": severity,
                "description": f"Bandits have increased their activity in {region.name}, disrupting trade!",
                "duration_days": duration_days
            }
            
        elif event_type == "festival":
            festivals = ["harvest_festival", "founding_day", "spring_celebration", "midsummer_feast", "winter_solstice"]
            festival_type = random.choice(festivals)
            duration_days = random.randint(3, 14)
            
            return {
                "festival_type": festival_type,
                "description": f"A {festival_type.replace('_', ' ')} has begun in {region.name}!",
                "duration_days": duration_days
            }
            
        elif event_type == "disease_outbreak":
            severity = random.uniform(0.3, 0.8)
            duration_days = int(severity * 60)  # More severe diseases last longer
            
            return {
                "severity": severity,
                "description": f"A disease outbreak has begun in {region.name}!",
                "duration_days": duration_days
            }
            
        elif event_type == "technological_breakthrough":
            categories = ["weapon", "armor", "tool", "magical"]
            affected_category = random.choice(categories)
            magnitude = random.uniform(0.2, 0.5)
            
            return {
                "affected_category": affected_category,
                "magnitude": magnitude,
                "description": f"A technological breakthrough in {affected_category}s has occurred in {region.name}!",
                "duration_days": 0  # Permanent effect
            }
            
        else:
            return {
                "description": f"An unknown event has occurred in {region.name}!",
                "duration_days": 7
            }
    
    def _calculate_event_economic_impacts(self, event_type: str, event_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate economic impacts for an event.
        
        Args:
            event_type: Type of event
            event_details: Event details
            
        Returns:
            Economic impacts
        """
        impacts = {
            "prosperity_modifier": 1.0,
            "price_modifiers": {},
            "supply_modifiers": {}
        }
        
        # Calculate impacts based on event type
        if event_type == "natural_disaster":
            severity = event_details.get("severity", 0.5)
            disaster_type = event_details.get("disaster_type", "earthquake")
            
            # Disasters reduce prosperity
            impacts["prosperity_modifier"] = max(0.5, 1.0 - (severity * 0.4))
            
            # Different disaster types affect different resources
            if disaster_type in ["earthquake", "fire"]:
                # Buildings destroyed, affects manufacturing
                impacts["price_modifiers"]["weapon"] = 1.2
                impacts["price_modifiers"]["armor"] = 1.2
                impacts["price_modifiers"]["tool"] = 1.3
                impacts["supply_modifiers"]["weapon"] = 0.8
                impacts["supply_modifiers"]["armor"] = 0.8
                impacts["supply_modifiers"]["tool"] = 0.7
                
            elif disaster_type in ["flood", "hurricane"]:
                # Crops destroyed, affects food
                impacts["price_modifiers"]["food"] = 1.5
                impacts["supply_modifiers"]["food"] = 0.6
                
            elif disaster_type == "drought":
                # Water shortage, affects food and potions
                impacts["price_modifiers"]["food"] = 1.4
                impacts["price_modifiers"]["potion"] = 1.3
                impacts["supply_modifiers"]["food"] = 0.7
                impacts["supply_modifiers"]["potion"] = 0.8
                
            elif disaster_type == "blizzard":
                # Travel difficult, affects all trade
                impacts["price_modifiers"]["food"] = 1.3
                impacts["price_modifiers"]["material"] = 1.2
                impacts["supply_modifiers"]["food"] = 0.8
                impacts["supply_modifiers"]["material"] = 0.9
        
        elif event_type == "trade_boom":
            prosperity_boost = event_details.get("prosperity_boost", 0.2)
            
            # Booms increase prosperity
            impacts["prosperity_modifier"] = 1.0 + prosperity_boost
            
            # General trade improvements
            categories = ["weapon", "armor", "food", "material", "tool", "magical", "potion"]
            for category in categories:
                impacts["supply_modifiers"][category] = 1.2
                impacts["price_modifiers"][category] = 0.9  # More supply means lower prices
        
        elif event_type == "resource_discovery":
            resource_type = event_details.get("resource_type", "iron_deposit")
            abundance = event_details.get("abundance", 0.5)
            
            # Discoveries increase prosperity
            impacts["prosperity_modifier"] = 1.0 + (abundance * 0.1)
            
            # Different resources affect different categories
            if "gold" in resource_type or "gem" in resource_type:
                # Luxury resources
                impacts["supply_modifiers"]["treasure"] = 1.0 + abundance
                impacts["price_modifiers"]["treasure"] = 1.0 - (abundance * 0.3)
                
            elif "iron" in resource_type or "metal" in resource_type:
                # Metal resources for weapons, armor, tools
                impacts["supply_modifiers"]["weapon"] = 1.0 + (abundance * 0.7)
                impacts["supply_modifiers"]["armor"] = 1.0 + (abundance * 0.7)
                impacts["supply_modifiers"]["tool"] = 1.0 + (abundance * 0.8)
                impacts["price_modifiers"]["weapon"] = 1.0 - (abundance * 0.2)
                impacts["price_modifiers"]["armor"] = 1.0 - (abundance * 0.2)
                impacts["price_modifiers"]["tool"] = 1.0 - (abundance * 0.25)
                
            elif "forest" in resource_type:
                # Wood resources
                impacts["supply_modifiers"]["material"] = 1.0 + (abundance * 0.9)
                impacts["price_modifiers"]["material"] = 1.0 - (abundance * 0.25)
                
            elif "fertile" in resource_type:
                # Food resources
                impacts["supply_modifiers"]["food"] = 1.0 + (abundance * 0.9)
                impacts["price_modifiers"]["food"] = 1.0 - (abundance * 0.3)
                
            elif "magical" in resource_type:
                # Magical resources
                impacts["supply_modifiers"]["magical"] = 1.0 + (abundance * 0.8)
                impacts["supply_modifiers"]["potion"] = 1.0 + (abundance * 0.6)
                impacts["price_modifiers"]["magical"] = 1.0 - (abundance * 0.2)
                impacts["price_modifiers"]["potion"] = 1.0 - (abundance * 0.15)
        
        elif event_type == "bandit_activity":
            severity = event_details.get("severity", 0.5)
            
            # Bandits reduce prosperity
            impacts["prosperity_modifier"] = max(0.7, 1.0 - (severity * 0.2))
            
            # Bandits affect all trade by reducing supply and increasing prices
            categories = ["weapon", "armor", "food", "material", "tool", "magical", "potion", "treasure"]
            for category in categories:
                impacts["supply_modifiers"][category] = max(0.6, 1.0 - (severity * 0.3))
                impacts["price_modifiers"][category] = 1.0 + (severity * 0.2)
        
        elif event_type == "festival":
            # Festivals increase prosperity
            impacts["prosperity_modifier"] = 1.2
            
            # Festivals increase demand for certain goods
            impacts["supply_modifiers"]["food"] = 1.5
            impacts["supply_modifiers"]["luxury"] = 1.4
            impacts["supply_modifiers"]["clothing"] = 1.3
            impacts["price_modifiers"]["food"] = 1.1  # Slight price increase despite more supply
            impacts["price_modifiers"]["luxury"] = 1.2
            impacts["price_modifiers"]["clothing"] = 1.15
        
        elif event_type == "disease_outbreak":
            severity = event_details.get("severity", 0.5)
            
            # Diseases reduce prosperity
            impacts["prosperity_modifier"] = max(0.5, 1.0 - (severity * 0.4))
            
            # Diseases affect population-dependent production and increase demand for medicine
            impacts["supply_modifiers"]["food"] = max(0.7, 1.0 - (severity * 0.2))
            impacts["supply_modifiers"]["material"] = max(0.8, 1.0 - (severity * 0.15))
            impacts["supply_modifiers"]["tool"] = max(0.9, 1.0 - (severity * 0.1))
            impacts["supply_modifiers"]["potion"] = 1.5  # Increased production of medicine
            impacts["price_modifiers"]["food"] = 1.0 + (severity * 0.1)
            impacts["price_modifiers"]["potion"] = 1.0 + (severity * 0.4)  # Medicine prices spike
        
        elif event_type == "technological_breakthrough":
            affected_category = event_details.get("affected_category", "weapon")
            magnitude = event_details.get("magnitude", 0.3)
            
            # Breakthroughs increase prosperity
            impacts["prosperity_modifier"] = 1.0 + (magnitude * 0.15)
            
            # Breakthroughs increase supply and quality but may not lower prices immediately
            impacts["supply_modifiers"][affected_category] = 1.0 + (magnitude * 0.5)
            impacts["price_modifiers"][affected_category] = 1.0 + (magnitude * 0.1)  # Slight price increase for better quality
        
        return impacts
    
    def _apply_event_impacts(self, db: Session, region_id: str, impacts: Dict[str, Any]) -> None:
        """
        Apply economic impacts to a region.
        
        Args:
            db: Database session
            region_id: Region identifier
            impacts: Economic impacts to apply
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return
        
        # Apply prosperity modifier
        prosperity_modifier = impacts.get("prosperity_modifier", 1.0)
        region.prosperity_level = max(0.1, min(1.0, region.prosperity_level * prosperity_modifier))
        
        # Apply price modifiers
        price_modifiers = impacts.get("price_modifiers", {})
        category_price_modifiers = region.category_price_modifiers or {}
        
        for category, modifier in price_modifiers.items():
            current_modifier = category_price_modifiers.get(category, 1.0)
            category_price_modifiers[category] = current_modifier * modifier
        
        region.category_price_modifiers = category_price_modifiers
        
        # Apply supply/demand modifiers
        supply_modifiers = impacts.get("supply_modifiers", {})
        supply_demand_signals = region.supply_demand_signals or {}
        
        for category, modifier in supply_modifiers.items():
            # Convert supply modifier to supply/demand signal
            # Higher supply = lower demand = negative signal
            supply_change = modifier - 1.0
            signal_change = -supply_change  # Inverse relationship
            
            current_signal = supply_demand_signals.get(category, 0.0)
            new_signal = max(-1.0, min(1.0, current_signal + signal_change))
            supply_demand_signals[category] = new_signal
        
        region.supply_demand_signals = supply_demand_signals
    
    def _record_event_in_region_history(self, 
                                      db: Session, 
                                      region_id: str, 
                                      event_type: str, 
                                      event_details: Dict[str, Any],
                                      economic_impacts: Dict[str, Any]) -> None:
        """
        Record an event in the region's history.
        
        Args:
            db: Database session
            region_id: Region identifier
            event_type: Type of event
            event_details: Event details
            economic_impacts: Economic impacts
        """
        # Get the region
        region = db.query(DBMarketRegionInfo).filter(DBMarketRegionInfo.region_id == region_id).first()
        if not region:
            return
        
        # Get custom data
        custom_data = region.custom_data or {}
        events_history = custom_data.get("events_history", [])
        
        # Add new event
        new_event = {
            "event_type": event_type,
            "date": datetime.utcnow().isoformat(),
            "details": event_details,
            "economic_impacts": {
                "prosperity_modifier": economic_impacts.get("prosperity_modifier", 1.0),
                "affected_categories": list(set(
                    list(economic_impacts.get("price_modifiers", {}).keys()) + 
                    list(economic_impacts.get("supply_modifiers", {}).keys())
                ))
            }
        }
        
        events_history.append(new_event)
        custom_data["events_history"] = events_history
        region.custom_data = custom_data
    
    def _get_disaster_impact_factors(self, disaster_type: str) -> Dict[str, Any]:
        """
        Get impact factors for a specific disaster type.
        
        Args:
            disaster_type: Type of disaster
            
        Returns:
            Impact factors
        """
        impact_factors = {
            "prosperity": 0.3,  # Default prosperity impact
            "resource_depletion": 0.3,  # Default resource depletion
            "categories": {}  # Category-specific impacts
        }
        
        if disaster_type == "earthquake":
            impact_factors["prosperity"] = 0.4
            impact_factors["resource_depletion"] = 0.5
            impact_factors["categories"] = {
                "weapon": {"price": 0.3, "supply": 0.4},
                "armor": {"price": 0.3, "supply": 0.4},
                "tool": {"price": 0.4, "supply": 0.5},
                "material": {"price": 0.5, "supply": 0.6}
            }
            
        elif disaster_type == "flood":
            impact_factors["prosperity"] = 0.3
            impact_factors["resource_depletion"] = 0.2
            impact_factors["categories"] = {
                "food": {"price": 0.5, "supply": 0.6},
                "material": {"price": 0.3, "supply": 0.4}
            }
            
        elif disaster_type == "drought":
            impact_factors["prosperity"] = 0.4
            impact_factors["resource_depletion"] = 0.6
            impact_factors["categories"] = {
                "food": {"price": 0.6, "supply": 0.7},
                "potion": {"price": 0.4, "supply": 0.5}
            }
            
        elif disaster_type == "fire":
            impact_factors["prosperity"] = 0.3
            impact_factors["resource_depletion"] = 0.4
            impact_factors["categories"] = {
                "material": {"price": 0.5, "supply": 0.6},
                "food": {"price": 0.3, "supply": 0.4},
                "clothing": {"price": 0.4, "supply": 0.5}
            }
            
        elif disaster_type == "blizzard":
            impact_factors["prosperity"] = 0.2
            impact_factors["resource_depletion"] = 0.1
            impact_factors["categories"] = {
                "food": {"price": 0.4, "supply": 0.5},
                "clothing": {"price": 0.2, "supply": 0.3}
            }
            
        elif disaster_type == "hurricane":
            impact_factors["prosperity"] = 0.4
            impact_factors["resource_depletion"] = 0.3
            impact_factors["categories"] = {
                "food": {"price": 0.5, "supply": 0.6},
                "material": {"price": 0.4, "supply": 0.5},
                "tool": {"price": 0.3, "supply": 0.4}
            }
            
        else:
            # Default impacts for unknown disaster types
            impact_factors["categories"] = {
                "food": {"price": 0.3, "supply": 0.4},
                "material": {"price": 0.3, "supply": 0.4}
            }
        
        return impact_factors
    
    def _get_resource_products(self, db: Session, resource_type: str) -> Dict[str, float]:
        """
        Get products that can be harvested from a resource type.
        
        Args:
            db: Database session
            resource_type: Type of resource
            
        Returns:
            Dictionary mapping item IDs to yield rates
        """
        products = {}
        
        # Get items by category based on resource type
        categories = []
        
        if "gold" in resource_type or "gem" in resource_type:
            categories = ["treasure"]
        elif "iron" in resource_type or "metal" in resource_type:
            categories = ["material"]
        elif "forest" in resource_type:
            categories = ["material"]
        elif "fertile" in resource_type:
            categories = ["food"]
        elif "magical" in resource_type:
            categories = ["magical", "material"]
        else:
            categories = ["material"]
        
        # Get items in these categories
        for category in categories:
            items = db.query(DBItem).filter(DBItem.category == category).all()
            for item in items:
                # Randomly select some items as products
                if random.random() < 0.7:  # 70% chance to be a product
                    yield_rate = random.uniform(0.5, 5.0)
                    products[item.id] = yield_rate
        
        # If no items found, add a generic fallback
        if not products:
            products["generic_material"] = 1.0
        
        return products
    
    def _handle_world_event(self, event: Event) -> None:
        """
        Handle a world event being triggered.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling world event: {event.data}")
        
        # In a real implementation, this would trigger additional
        # systems to react to the event
    
    def _handle_festival_start(self, event: Event) -> None:
        """
        Handle a festival starting.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling festival start: {event.data}")
        
        # In a real implementation, this might trigger NPCs to attend,
        # special quests to become available, etc.
    
    def _handle_war_declaration(self, event: Event) -> None:
        """
        Handle a war being declared.
        
        Args:
            event: Event data
        """
        self.logger.info(f"Handling war declaration: {event.data}")
        
        # In a real implementation, this would trigger military movements,
        # changes in faction relationships, etc.