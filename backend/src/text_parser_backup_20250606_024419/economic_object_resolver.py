"""
Economic Object Resolver - Resolves economic entities from text references

This module provides specialized resolution for economic entities like items, 
recipes, businesses, and buildings from text references. It acts as a bridge
between the text parser and the actual game systems.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass
from pydantic import BaseModel

from .economic_grammars import GameContext


logger = logging.getLogger("text_parser.economic_resolver")


class ResolvedItemData(BaseModel):
    """Data for a successfully resolved item."""
    item_id: str
    name: str
    description: Optional[str] = None
    value: Optional[float] = None
    item_type: Optional[str] = None
    rarity: Optional[str] = None
    is_craftable: bool = False
    is_equippable: bool = False
    is_consumable: bool = False
    is_material: bool = False
    additional_data: Dict[str, Any] = {}


class ResolvedRecipeData(BaseModel):
    """Data for a successfully resolved crafting recipe."""
    recipe_id: str
    name: str
    description: Optional[str] = None
    difficulty: Optional[int] = None
    required_profession: Optional[str] = None
    required_skill_level: Optional[int] = None
    crafting_time: Optional[int] = None  # in seconds
    ingredients: List[Dict[str, Any]] = []
    outputs: List[Dict[str, Any]] = []
    additional_data: Dict[str, Any] = {}


class ResolvedShopData(BaseModel):
    """Data for a successfully resolved shop."""
    shop_id: str
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    location_id: Optional[str] = None
    shop_type: Optional[str] = None
    reputation: Optional[float] = None
    additional_data: Dict[str, Any] = {}


class ResolvedBusinessData(BaseModel):
    """Data for a successfully resolved player-owned business."""
    business_id: str
    name: str
    description: Optional[str] = None
    owner_id: str
    business_type: Optional[str] = None
    location_id: Optional[str] = None
    level: Optional[int] = None
    staff: List[Dict[str, Any]] = []
    finances: Dict[str, Any] = {}
    additional_data: Dict[str, Any] = {}


class ResolvedBuildingData(BaseModel):
    """Data for a successfully resolved building."""
    building_id: str
    name: str
    description: Optional[str] = None
    owner_id: Optional[str] = None
    building_type: Optional[str] = None
    location_id: Optional[str] = None
    condition: Optional[float] = None  # 0.0 to 1.0
    level: Optional[int] = None
    modules: List[Dict[str, Any]] = []
    additional_data: Dict[str, Any] = {}


class ResolvedNPCData(BaseModel):
    """Data for a successfully resolved NPC."""
    npc_id: str
    name: str
    description: Optional[str] = None
    profession: Optional[str] = None
    location_id: Optional[str] = None
    reputation: Optional[float] = None  # -1.0 to 1.0
    disposition: Optional[str] = None  # friendly, neutral, hostile
    trades: bool = False
    crafts: bool = False
    additional_data: Dict[str, Any] = {}


class ResolvedLocationData(BaseModel):
    """Data for a successfully resolved location."""
    location_id: str
    name: str
    description: Optional[str] = None
    region_id: Optional[str] = None
    location_type: Optional[str] = None
    has_market: bool = False
    has_black_market: bool = False
    additional_data: Dict[str, Any] = {}


class ResolvedMaterialData(BaseModel):
    """Data for a successfully resolved crafting material."""
    material_id: str
    name: str
    description: Optional[str] = None
    material_type: Optional[str] = None
    rarity: Optional[str] = None
    base_value: Optional[float] = None
    sources: List[str] = []
    is_craftable: bool = False
    illicit_in_regions: List[str] = []
    additional_data: Dict[str, Any] = {}


class ResolvedBuildingTemplateData(BaseModel):
    """Data for a successfully resolved building template."""
    template_id: str
    name: str
    description: Optional[str] = None
    building_type: Optional[str] = None
    required_materials: List[Dict[str, Any]] = []
    construction_time: Optional[int] = None  # in seconds
    base_cost: Optional[float] = None
    upgradable: bool = False
    size: Optional[str] = None  # small, medium, large
    additional_data: Dict[str, Any] = {}


class ResolvedPlotData(BaseModel):
    """Data for a successfully resolved land plot."""
    plot_id: str
    name: str
    description: Optional[str] = None
    location_id: Optional[str] = None
    size: Optional[str] = None  # small, medium, large
    price: Optional[float] = None
    owner_id: Optional[str] = None
    is_for_sale: bool = False
    allowed_building_types: List[str] = []
    additional_data: Dict[str, Any] = {}


class EconomicObjectResolver:
    """
    Resolves economic entities from text references by connecting to game services.
    This class bridges the text parser and the game's economic systems.
    """
    
    def __init__(self):
        """Initialize the economic object resolver."""
        self.logger = logging.getLogger("text_parser.economic_resolver")
        
        # These service interfaces will be set during application initialization
        self.item_service = None
        self.recipe_service = None
        self.shop_service = None
        self.business_service = None
        self.building_service = None
        self.npc_service = None
        self.location_service = None
        self.economy_service = None
        self.black_market_service = None
        
    def set_services(self, services: Dict[str, Any]) -> None:
        """
        Set the service interfaces for the resolver to use.
        
        Args:
            services: Dictionary of service interfaces
        """
        for service_name, service in services.items():
            if hasattr(self, f"{service_name}_service"):
                setattr(self, f"{service_name}_service", service)
    
    def resolve_item_for_purchase(
        self, name_str: str, context: GameContext, shop_id: Optional[str] = None
    ) -> Optional[ResolvedItemData]:
        """
        Resolve an item that the player wants to purchase.
        
        Args:
            name_str: Text describing the item
            context: Current game context
            shop_id: Optional shop ID to limit the search
            
        Returns:
            ResolvedItemData if found, None otherwise
        """
        if not self.item_service:
            self.logger.warning("Item service not available for resolving item for purchase")
            return None
        
        # If no shop_id provided but there's one in context, use that
        if not shop_id and context.current_shop_id:
            shop_id = context.current_shop_id
        
        try:
            # Call the item service to find items for sale that match the name
            items = self.item_service.find_items_by_name_fuzzy(
                name_str, 
                shop_id=shop_id, 
                location_id=context.location_id
            )
            
            if not items:
                return None
                
            # Take the best match (first item)
            item = items[0]
            
            return ResolvedItemData(
                item_id=item["id"],
                name=item["name"],
                description=item.get("description"),
                value=item.get("price") or item.get("value"),
                item_type=item.get("type"),
                rarity=item.get("rarity"),
                is_craftable=item.get("is_craftable", False),
                is_equippable=item.get("is_equippable", False),
                is_consumable=item.get("is_consumable", False),
                is_material=item.get("is_material", False),
                additional_data={
                    "available_quantity": item.get("available_quantity", 0),
                    "shop_id": shop_id,
                    "for_sale": True
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving item for purchase: {e}")
            return None
    
    def resolve_item_in_inventory(
        self, name_str: str, context: GameContext, inventory_owner_id: Optional[str] = None
    ) -> Optional[ResolvedItemData]:
        """
        Resolve an item in a character's inventory.
        
        Args:
            name_str: Text describing the item
            context: Current game context
            inventory_owner_id: ID of the inventory owner (defaults to player)
            
        Returns:
            ResolvedItemData if found, None otherwise
        """
        if not self.item_service:
            self.logger.warning("Item service not available for resolving inventory item")
            return None
        
        # If no inventory_owner_id provided, use the player ID from context
        if not inventory_owner_id:
            inventory_owner_id = context.player_id
        
        try:
            # Call the item service to find items in the inventory that match the name
            items = self.item_service.find_items_in_inventory_by_name(
                name_str, 
                owner_id=inventory_owner_id
            )
            
            if not items:
                return None
                
            # Take the best match (first item)
            item = items[0]
            
            return ResolvedItemData(
                item_id=item["id"],
                name=item["name"],
                description=item.get("description"),
                value=item.get("value"),
                item_type=item.get("type"),
                rarity=item.get("rarity"),
                is_craftable=item.get("is_craftable", False),
                is_equippable=item.get("is_equippable", False),
                is_consumable=item.get("is_consumable", False),
                is_material=item.get("is_material", False),
                additional_data={
                    "quantity": item.get("quantity", 1),
                    "equipped": item.get("equipped", False),
                    "owner_id": inventory_owner_id
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving inventory item: {e}")
            return None
    
    def resolve_recipe_for_crafting(
        self, name_str: str, context: GameContext, character_id: Optional[str] = None
    ) -> Optional[ResolvedRecipeData]:
        """
        Resolve a crafting recipe that the player wants to use.
        
        Args:
            name_str: Text describing the recipe or output item
            context: Current game context
            character_id: ID of the character doing the crafting (defaults to player)
            
        Returns:
            ResolvedRecipeData if found, None otherwise
        """
        if not self.recipe_service:
            self.logger.warning("Recipe service not available for resolving recipe")
            return None
        
        # If no character_id provided, use the player ID from context
        if not character_id:
            character_id = context.player_id
        
        try:
            # First try to find by recipe name
            recipes = self.recipe_service.find_recipes_by_name(
                name_str, 
                character_id=character_id
            )
            
            # If no results, try finding by output item name
            if not recipes:
                recipes = self.recipe_service.find_recipes_by_output_item_name(
                    name_str, 
                    character_id=character_id
                )
            
            if not recipes:
                return None
                
            # Take the best match (first recipe)
            recipe = recipes[0]
            
            # Format ingredients and outputs
            ingredients = []
            for ingredient in recipe.get("ingredients", []):
                ingredients.append({
                    "id": ingredient.get("id"),
                    "name": ingredient.get("name"),
                    "quantity": ingredient.get("quantity", 1),
                    "in_inventory": ingredient.get("in_inventory", False),
                    "available_quantity": ingredient.get("available_quantity", 0)
                })
            
            outputs = []
            for output in recipe.get("outputs", []):
                outputs.append({
                    "id": output.get("id"),
                    "name": output.get("name"),
                    "quantity": output.get("quantity", 1),
                    "is_primary": output.get("is_primary", True)
                })
            
            return ResolvedRecipeData(
                recipe_id=recipe["id"],
                name=recipe["name"],
                description=recipe.get("description"),
                difficulty=recipe.get("difficulty_level"),
                required_profession=recipe.get("required_profession"),
                required_skill_level=recipe.get("required_skill_level"),
                crafting_time=recipe.get("crafting_time_seconds"),
                ingredients=ingredients,
                outputs=outputs,
                additional_data={
                    "can_craft": recipe.get("can_craft", False),
                    "has_required_station": recipe.get("has_required_station", False),
                    "required_station_type": recipe.get("required_station_type"),
                    "category": recipe.get("recipe_category")
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving recipe for crafting: {e}")
            return None
    
    def resolve_shop_by_name_or_context(
        self, name_str: Optional[str], context: GameContext
    ) -> Optional[ResolvedShopData]:
        """
        Resolve a shop by name or from current context.
        
        Args:
            name_str: Optional text describing the shop
            context: Current game context
            
        Returns:
            ResolvedShopData if found, None otherwise
        """
        if not self.shop_service:
            self.logger.warning("Shop service not available for resolving shop")
            return None
        
        try:
            shop = None
            
            # If name provided, try to find by name
            if name_str:
                shops = self.shop_service.find_shops_by_name(
                    name_str, 
                    location_id=context.location_id
                )
                if shops:
                    shop = shops[0]
            
            # If no shop found and we have a current shop in context, use that
            if not shop and context.current_shop_id:
                shop = self.shop_service.get_shop_by_id(context.current_shop_id)
            
            # If still no shop, try finding shops at current location
            if not shop and context.location_id:
                shops = self.shop_service.get_shops_at_location(context.location_id)
                if shops:
                    shop = shops[0]  # Take the first one
            
            if not shop:
                return None
                
            return ResolvedShopData(
                shop_id=shop["id"],
                name=shop["name"],
                description=shop.get("description"),
                owner_id=shop.get("owner_id"),
                owner_name=shop.get("owner_name"),
                location_id=shop.get("location_id"),
                shop_type=shop.get("shop_type"),
                reputation=shop.get("reputation"),
                additional_data={
                    "open_hours": shop.get("open_hours"),
                    "specializes_in": shop.get("specializes_in", []),
                    "price_modifier": shop.get("price_modifier", 1.0)
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving shop: {e}")
            return None
    
    def resolve_npc_for_interaction(
        self, name_str: str, context: GameContext
    ) -> Optional[ResolvedNPCData]:
        """
        Resolve an NPC that the player wants to interact with.
        
        Args:
            name_str: Text describing the NPC
            context: Current game context
            
        Returns:
            ResolvedNPCData if found, None otherwise
        """
        if not self.npc_service:
            self.logger.warning("NPC service not available for resolving NPC")
            return None
        
        try:
            npc = None
            
            # If we have a current NPC in context, check if the name matches
            if context.current_npc_id:
                current_npc = self.npc_service.get_npc_by_id(context.current_npc_id)
                if current_npc and self._is_name_match(name_str, current_npc["name"]):
                    npc = current_npc
            
            # If no match with current NPC, search by name
            if not npc:
                npcs = self.npc_service.find_npcs_by_name(
                    name_str, 
                    location_id=context.location_id
                )
                if npcs:
                    npc = npcs[0]
            
            if not npc:
                return None
                
            return ResolvedNPCData(
                npc_id=npc["id"],
                name=npc["name"],
                description=npc.get("description"),
                profession=npc.get("profession"),
                location_id=npc.get("location_id"),
                reputation=npc.get("reputation"),
                disposition=npc.get("disposition"),
                trades=npc.get("trades", False),
                crafts=npc.get("crafts", False),
                additional_data={
                    "faction": npc.get("faction"),
                    "level": npc.get("level"),
                    "shop_id": npc.get("shop_id")
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving NPC: {e}")
            return None
    
    def resolve_player_owned_business(
        self, name_str: Optional[str], context: GameContext
    ) -> Optional[ResolvedBusinessData]:
        """
        Resolve a player-owned business by name or from context.
        
        Args:
            name_str: Optional text describing the business
            context: Current game context
            
        Returns:
            ResolvedBusinessData if found, None otherwise
        """
        if not self.business_service:
            self.logger.warning("Business service not available for resolving business")
            return None
        
        try:
            business = None
            
            # If name provided, try to find by name
            if name_str:
                businesses = self.business_service.find_player_businesses_by_name(
                    name_str, 
                    player_id=context.player_id
                )
                if businesses:
                    business = businesses[0]
            
            # If no business found and we have a current business in context, use that
            if not business and context.current_business_id:
                business = self.business_service.get_business_by_id(context.current_business_id)
            
            # If still no business, get the player's default business if they have one
            if not business:
                businesses = self.business_service.get_player_businesses(context.player_id)
                if businesses:
                    business = businesses[0]  # Take the first one
            
            if not business:
                return None
                
            # Format staff data
            staff = []
            for staff_member in business.get("staff", []):
                staff.append({
                    "id": staff_member.get("id"),
                    "name": staff_member.get("name"),
                    "role": staff_member.get("role"),
                    "skill_level": staff_member.get("skill_level"),
                    "salary": staff_member.get("salary"),
                    "current_task": staff_member.get("current_task")
                })
            
            return ResolvedBusinessData(
                business_id=business["id"],
                name=business["name"],
                description=business.get("description"),
                owner_id=business["owner_id"],
                business_type=business.get("business_type"),
                location_id=business.get("location_id"),
                level=business.get("level"),
                staff=staff,
                finances={
                    "current_capital": business.get("current_capital", 0),
                    "daily_revenue": business.get("daily_revenue", 0),
                    "daily_expenses": business.get("daily_expenses", 0),
                    "tax_rate": business.get("tax_rate", 0),
                    "last_tax_payment": business.get("last_tax_payment")
                },
                additional_data={
                    "reputation": business.get("reputation", 0),
                    "inventory_capacity": business.get("inventory_capacity", 0),
                    "is_illicit": business.get("is_illicit", False)
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving player business: {e}")
            return None
    
    def resolve_building_template_for_construction(
        self, name_str: str, context: GameContext
    ) -> Optional[ResolvedBuildingTemplateData]:
        """
        Resolve a building template for construction.
        
        Args:
            name_str: Text describing the building template
            context: Current game context
            
        Returns:
            ResolvedBuildingTemplateData if found, None otherwise
        """
        if not self.building_service:
            self.logger.warning("Building service not available for resolving building template")
            return None
        
        try:
            # Find building templates that match the name
            templates = self.building_service.find_building_templates_by_name(name_str)
            
            if not templates:
                return None
                
            # Take the best match (first template)
            template = templates[0]
            
            # Format required materials
            required_materials = []
            for material in template.get("required_materials", []):
                required_materials.append({
                    "id": material.get("id"),
                    "name": material.get("name"),
                    "quantity": material.get("quantity", 1),
                    "in_inventory": material.get("in_inventory", False),
                    "available_quantity": material.get("available_quantity", 0)
                })
            
            return ResolvedBuildingTemplateData(
                template_id=template["id"],
                name=template["name"],
                description=template.get("description"),
                building_type=template.get("building_type"),
                required_materials=required_materials,
                construction_time=template.get("construction_time_seconds"),
                base_cost=template.get("base_cost"),
                upgradable=template.get("upgradable", False),
                size=template.get("size"),
                additional_data={
                    "category": template.get("category"),
                    "max_level": template.get("max_level", 1),
                    "requires_permission": template.get("requires_permission", False),
                    "requires_skill": template.get("requires_skill"),
                    "requires_skill_level": template.get("requires_skill_level")
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving building template: {e}")
            return None
    
    def resolve_land_plot_for_building(
        self, identifier_str: str, context: GameContext
    ) -> Optional[ResolvedPlotData]:
        """
        Resolve a land plot for building construction.
        
        Args:
            identifier_str: Text identifying the plot
            context: Current game context
            
        Returns:
            ResolvedPlotData if found, None otherwise
        """
        if not self.building_service:
            self.logger.warning("Building service not available for resolving land plot")
            return None
        
        try:
            plot = None
            
            # Check if identifier is a plot ID or name
            if identifier_str.isdigit() or (len(identifier_str) > 8 and "-" in identifier_str):
                # Looks like an ID (number or UUID)
                plot = self.building_service.get_plot_by_id(identifier_str)
            else:
                # Try to find by name at current location
                plots = self.building_service.find_plots_by_name(
                    identifier_str, 
                    location_id=context.location_id
                )
                if plots:
                    plot = plots[0]
            
            # If not found, try getting plots owned by the player
            if not plot:
                plots = self.building_service.get_plots_owned_by_player(context.player_id)
                for p in plots:
                    if self._is_name_match(identifier_str, p["name"]):
                        plot = p
                        break
            
            if not plot:
                return None
                
            return ResolvedPlotData(
                plot_id=plot["id"],
                name=plot["name"],
                description=plot.get("description"),
                location_id=plot.get("location_id"),
                size=plot.get("size"),
                price=plot.get("price"),
                owner_id=plot.get("owner_id"),
                is_for_sale=plot.get("is_for_sale", False),
                allowed_building_types=plot.get("allowed_building_types", []),
                additional_data={
                    "coordinates": plot.get("coordinates"),
                    "terrain_type": plot.get("terrain_type"),
                    "has_building": plot.get("has_building", False),
                    "building_id": plot.get("building_id")
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving land plot: {e}")
            return None
    
    def resolve_material_for_crafting(
        self, name_str: str, context: GameContext
    ) -> Optional[ResolvedMaterialData]:
        """
        Resolve a crafting material.
        
        Args:
            name_str: Text describing the material
            context: Current game context
            
        Returns:
            ResolvedMaterialData if found, None otherwise
        """
        if not self.recipe_service:
            self.logger.warning("Recipe service not available for resolving material")
            return None
        
        try:
            # Find materials that match the name
            materials = self.recipe_service.find_materials_by_name(name_str)
            
            if not materials:
                return None
                
            # Take the best match (first material)
            material = materials[0]
            
            return ResolvedMaterialData(
                material_id=material["id"],
                name=material["name"],
                description=material.get("description"),
                material_type=material.get("material_type"),
                rarity=material.get("rarity"),
                base_value=material.get("base_value"),
                sources=material.get("source_tags", []),
                is_craftable=material.get("is_craftable", False),
                illicit_in_regions=material.get("illicit_in_regions", []),
                additional_data={
                    "properties": material.get("properties", {}),
                    "in_inventory": material.get("in_inventory", False),
                    "inventory_quantity": material.get("inventory_quantity", 0)
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving crafting material: {e}")
            return None
    
    def resolve_building_by_name(
        self, name_str: str, context: GameContext
    ) -> Optional[ResolvedBuildingData]:
        """
        Resolve a building by name.
        
        Args:
            name_str: Text describing the building
            context: Current game context
            
        Returns:
            ResolvedBuildingData if found, None otherwise
        """
        if not self.building_service:
            self.logger.warning("Building service not available for resolving building")
            return None
        
        try:
            # Find player-owned buildings that match the name
            buildings = self.building_service.find_player_buildings_by_name(
                name_str, 
                player_id=context.player_id
            )
            
            if not buildings:
                # Try finding buildings at current location
                buildings = self.building_service.find_buildings_by_name(
                    name_str, 
                    location_id=context.location_id
                )
            
            if not buildings:
                return None
                
            # Take the best match (first building)
            building = buildings[0]
            
            # Format modules
            modules = []
            for module in building.get("modules", []):
                modules.append({
                    "id": module.get("id"),
                    "name": module.get("name"),
                    "level": module.get("level"),
                    "type": module.get("type"),
                    "condition": module.get("condition", 1.0),
                    "functionality": module.get("functionality", 1.0)
                })
            
            return ResolvedBuildingData(
                building_id=building["id"],
                name=building["name"],
                description=building.get("description"),
                owner_id=building.get("owner_id"),
                building_type=building.get("building_type"),
                location_id=building.get("location_id"),
                condition=building.get("condition", 1.0),
                level=building.get("level"),
                modules=modules,
                additional_data={
                    "construction_date": building.get("construction_date"),
                    "last_repair_date": building.get("last_repair_date"),
                    "last_upgrade_date": building.get("last_upgrade_date"),
                    "max_level": building.get("max_level"),
                    "plot_id": building.get("plot_id"),
                    "business_id": building.get("business_id")
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving building: {e}")
            return None
    
    def resolve_black_market_vendor(
        self, name_str: Optional[str], context: GameContext
    ) -> Optional[ResolvedNPCData]:
        """
        Resolve a black market vendor.
        
        Args:
            name_str: Optional text describing the vendor
            context: Current game context
            
        Returns:
            ResolvedNPCData if found, None otherwise
        """
        if not self.black_market_service:
            self.logger.warning("Black market service not available for resolving vendor")
            return None
        
        try:
            vendor = None
            
            # If name provided, try to find by name
            if name_str:
                vendors = self.black_market_service.find_vendors_by_name(
                    name_str, 
                    location_id=context.location_id
                )
                if vendors:
                    vendor = vendors[0]
            
            # If no vendor found, try finding vendors at current location
            if not vendor and context.location_id:
                vendors = self.black_market_service.get_vendors_at_location(
                    context.location_id,
                    player_notoriety=self._get_player_notoriety(context.player_id)
                )
                if vendors:
                    vendor = vendors[0]  # Take the first one
            
            if not vendor:
                return None
                
            return ResolvedNPCData(
                npc_id=vendor["id"],
                name=vendor["name"],
                description=vendor.get("description"),
                profession="Black Market Vendor",
                location_id=vendor.get("location_id"),
                reputation=vendor.get("reputation"),
                disposition=vendor.get("disposition"),
                trades=True,
                crafts=False,
                additional_data={
                    "faction": vendor.get("faction"),
                    "specializes_in": vendor.get("specializes_in", []),
                    "security_level": vendor.get("security_level", 1),
                    "requires_introduction": vendor.get("requires_introduction", False),
                    "minimum_notoriety": vendor.get("minimum_notoriety", 0)
                }
            )
        
        except Exception as e:
            self.logger.error(f"Error resolving black market vendor: {e}")
            return None
    
    def _is_name_match(self, input_name: str, actual_name: str) -> bool:
        """
        Check if input name matches the actual name.
        
        Args:
            input_name: User-provided name
            actual_name: Actual name to compare against
            
        Returns:
            True if names match, False otherwise
        """
        input_name = input_name.lower().strip()
        actual_name = actual_name.lower().strip()
        
        # Exact match
        if input_name == actual_name:
            return True
        
        # Partial match (input is part of actual)
        if input_name in actual_name:
            return True
        
        # Check for fuzzy match using simplified tokenization
        input_tokens = set(input_name.split())
        actual_tokens = set(actual_name.split())
        
        # If more than half of input tokens match
        common_tokens = input_tokens.intersection(actual_tokens)
        if len(common_tokens) >= len(input_tokens) * 0.5:
            return True
        
        return False
    
    def _get_player_notoriety(self, player_id: str) -> float:
        """
        Get player's notoriety in the criminal underworld.
        
        Args:
            player_id: Player ID
            
        Returns:
            Notoriety value (0.0 to 1.0)
        """
        if not self.black_market_service:
            return 0.0
        
        try:
            player_data = self.black_market_service.get_player_criminal_profile(player_id)
            return player_data.get("notoriety", 0.0)
        except Exception:
            return 0.0


# Create a global instance of the economic object resolver
economic_object_resolver = EconomicObjectResolver()