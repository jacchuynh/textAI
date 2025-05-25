"""
Economic Command Handler - Process and execute economic commands

This module acts as the central orchestrator for processing economic commands
and directing them to the appropriate game services. It translates player text
input into structured commands and then executes them.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple, Union
import json

from .economic_actions import EconomicAction
from .economic_grammars import match_economic_command, ParsedEconomicCommand, GameContext
from .economic_object_resolver import (
    economic_object_resolver, 
    ResolvedItemData,
    ResolvedRecipeData,
    ResolvedShopData,
    ResolvedBusinessData,
    ResolvedBuildingData,
    ResolvedNPCData,
    ResolvedLocationData,
    ResolvedMaterialData,
    ResolvedBuildingTemplateData,
    ResolvedPlotData
)


logger = logging.getLogger("text_parser.economic_handler")


class CommandResult:
    """Result of processing an economic command."""
    
    def __init__(
        self, 
        success: bool, 
        message: str, 
        data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        command_type: Optional[str] = None
    ):
        self.success = success
        self.message = message
        self.data = data or {}
        self.error = error
        self.command_type = command_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "command_type": self.command_type
        }


class EconomicCommandHandler:
    """
    Handle economic commands by parsing player input and directing it to appropriate services.
    Acts as the bridge between the text parser and the game's economic systems.
    """
    
    def __init__(self):
        """Initialize the economic command handler."""
        self.logger = logging.getLogger("text_parser.economic_handler")
        
        # These service interfaces will be set during application initialization
        self.item_service = None
        self.transaction_service = None
        self.recipe_service = None
        self.shop_service = None
        self.business_service = None
        self.building_service = None
        self.npc_service = None
        self.player_service = None
        self.economy_service = None
        self.black_market_service = None
    
    def set_services(self, services: Dict[str, Any]) -> None:
        """
        Set the service interfaces for the handler to use.
        
        Args:
            services: Dictionary of service interfaces
        """
        for service_name, service in services.items():
            if hasattr(self, f"{service_name}_service"):
                setattr(self, f"{service_name}_service", service)
        
        # Also update the object resolver with the same services
        economic_object_resolver.set_services(services)
    
    def process_command(self, input_text: str, context: GameContext) -> CommandResult:
        """
        Process an economic command from player input.
        
        Args:
            input_text: Raw text input from player
            context: Current game context
            
        Returns:
            CommandResult with the result of processing the command
        """
        # Attempt to parse the command
        parsed_command = match_economic_command(input_text, context)
        
        if not parsed_command:
            return CommandResult(
                success=False,
                message="I couldn't understand your economic command. Please try again with different wording.",
                error="No matching economic command pattern",
                command_type="unknown"
            )
        
        # Process the command based on its action type
        try:
            self.logger.info(f"Processing economic command: {parsed_command.action.name} - '{input_text}'")
            
            # Shopping actions
            if parsed_command.action in [
                EconomicAction.BUY_ITEM, 
                EconomicAction.SELL_ITEM, 
                EconomicAction.LIST_SHOP_ITEMS,
                EconomicAction.VIEW_ITEM_DETAILS,
                EconomicAction.GET_ITEM_PRICE,
                EconomicAction.INITIATE_BARTER
            ]:
                return self._handle_shopping_command(parsed_command, context)
            
            # Crafting actions
            elif parsed_command.action in [
                EconomicAction.CRAFT_ITEM,
                EconomicAction.LIST_KNOWN_RECIPES,
                EconomicAction.LIST_CRAFTABLE_RECIPES,
                EconomicAction.VIEW_RECIPE_DETAILS,
                EconomicAction.ATTEMPT_RECIPE_DISCOVERY,
                EconomicAction.CHECK_CRAFTING_MATERIALS
            ]:
                return self._handle_crafting_command(parsed_command, context)
            
            # Business management actions
            elif parsed_command.action in [
                EconomicAction.VIEW_BUSINESS_STATUS,
                EconomicAction.SET_PRODUCT_PRICE,
                EconomicAction.MANAGE_BUSINESS_INVENTORY,
                EconomicAction.HIRE_STAFF,
                EconomicAction.ASSIGN_STAFF_TASK,
                EconomicAction.UPGRADE_BUSINESS,
                EconomicAction.VIEW_BUSINESS_LEDGER,
                EconomicAction.PAY_BUSINESS_TAXES,
                EconomicAction.COLLECT_BUSINESS_PROFITS
            ]:
                return self._handle_business_command(parsed_command, context)
            
            # Building actions
            elif parsed_command.action in [
                EconomicAction.CONSTRUCT_BUILDING,
                EconomicAction.UPGRADE_BUILDING,
                EconomicAction.LIST_AVAILABLE_BUILDINGS,
                EconomicAction.VIEW_BUILDING_DETAILS,
                EconomicAction.REPAIR_BUILDING,
                EconomicAction.BUY_PROPERTY,
                EconomicAction.SELL_PROPERTY
            ]:
                return self._handle_building_command(parsed_command, context)
            
            # Inventory and currency actions
            elif parsed_command.action in [
                EconomicAction.CHECK_INVENTORY,
                EconomicAction.CHECK_CURRENCY,
                EconomicAction.LOCATE_MATERIAL_SOURCE
            ]:
                return self._handle_inventory_command(parsed_command, context)
            
            # Market actions
            elif parsed_command.action in [
                EconomicAction.GET_MARKET_PRICE_INFO,
                EconomicAction.ACCESS_BLACK_MARKET,
                EconomicAction.LIST_BLACK_MARKET_GOODS
            ]:
                return self._handle_market_command(parsed_command, context)
            
            # Illicit actions
            elif parsed_command.action in [
                EconomicAction.START_ILLICIT_OPERATION,
                EconomicAction.LAUNDER_MONEY,
                EconomicAction.BRIBE_AUTHORITY,
                EconomicAction.CHECK_HEAT_LEVEL,
                EconomicAction.FENCE_STOLEN_GOODS
            ]:
                return self._handle_illicit_command(parsed_command, context)
            
            else:
                return CommandResult(
                    success=False,
                    message=f"The action {parsed_command.action.name} is recognized but not yet implemented.",
                    error="Action not implemented",
                    command_type=parsed_command.action.name
                )
        
        except Exception as e:
            self.logger.error(f"Error processing economic command: {e}", exc_info=True)
            return CommandResult(
                success=False,
                message="There was an error processing your command. Please try again.",
                error=str(e),
                command_type=parsed_command.action.name if parsed_command else "unknown"
            )
    
    def _handle_shopping_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle shopping-related commands."""
        if not self.transaction_service or not self.item_service or not self.shop_service:
            return CommandResult(
                success=False,
                message="Shopping services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        # Buy item
        if command.action == EconomicAction.BUY_ITEM:
            # Resolve the item to buy
            item = None
            shop = None
            
            # Resolve shop first if provided
            if command.secondary_target:
                shop = economic_object_resolver.resolve_shop_by_name_or_context(
                    command.secondary_target, context
                )
                
                if not shop:
                    return CommandResult(
                        success=False,
                        message=f"I couldn't find the shop or vendor '{command.secondary_target}'.",
                        error="Shop not found",
                        command_type=command.action.name
                    )
                
                # Update context with the resolved shop
                context.current_shop_id = shop.shop_id
            
            # Resolve the item to buy
            item = economic_object_resolver.resolve_item_for_purchase(
                command.primary_target, context, shop.shop_id if shop else None
            )
            
            if not item:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find the item '{command.primary_target}' for sale.",
                    error="Item not found",
                    command_type=command.action.name
                )
            
            # If shop is still not resolved, try to get it from the item's shop_id
            if not shop and item.additional_data.get("shop_id"):
                shop = economic_object_resolver.resolve_shop_by_name_or_context(
                    None, context._replace(current_shop_id=item.additional_data["shop_id"])
                )
            
            # Determine quantity and price
            quantity = command.quantity or 1
            price = command.price
            
            if not price:
                # Use item's price if command didn't specify one
                price = item.value * quantity if item.value else None
            
            # Execute the purchase
            try:
                result = self.transaction_service.player_buy_item(
                    player_id=context.player_id,
                    item_id=item.item_id,
                    shop_id=shop.shop_id if shop else context.current_shop_id,
                    quantity=quantity,
                    price=price
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You purchased {quantity} {item.name} for {result.get('total_cost')} {command.currency_type or 'gold'}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to buy {item.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error processing your purchase: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Sell item
        elif command.action == EconomicAction.SELL_ITEM:
            # Resolve the item to sell
            item = None
            shop = None
            
            # Resolve the item from inventory
            item = economic_object_resolver.resolve_item_in_inventory(
                command.primary_target, context, context.player_id
            )
            
            if not item:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find '{command.primary_target}' in your inventory.",
                    error="Item not found in inventory",
                    command_type=command.action.name
                )
            
            # Resolve shop if provided
            if command.secondary_target:
                shop = economic_object_resolver.resolve_shop_by_name_or_context(
                    command.secondary_target, context
                )
                
                if not shop:
                    return CommandResult(
                        success=False,
                        message=f"I couldn't find the shop or vendor '{command.secondary_target}'.",
                        error="Shop not found",
                        command_type=command.action.name
                    )
            else:
                # Try to use current shop context
                shop = economic_object_resolver.resolve_shop_by_name_or_context(None, context)
            
            # Determine quantity and price
            quantity = command.quantity or 1
            price = command.price
            
            # Ensure we have enough of the item
            available_quantity = item.additional_data.get("quantity", 0)
            if quantity > available_quantity:
                return CommandResult(
                    success=False,
                    message=f"You only have {available_quantity} {item.name} in your inventory.",
                    error="Insufficient quantity",
                    command_type=command.action.name
                )
            
            # Execute the sale
            try:
                result = self.transaction_service.player_sell_item(
                    player_id=context.player_id,
                    item_id=item.item_id,
                    shop_id=shop.shop_id if shop else context.current_shop_id,
                    quantity=quantity,
                    price=price
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You sold {quantity} {item.name} for {result.get('total_amount')} {command.currency_type or 'gold'}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to sell {item.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error processing your sale: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # List shop items
        elif command.action == EconomicAction.LIST_SHOP_ITEMS:
            shop = None
            
            # Resolve shop if provided
            if command.secondary_target:
                shop = economic_object_resolver.resolve_shop_by_name_or_context(
                    command.secondary_target, context
                )
                
                if not shop:
                    return CommandResult(
                        success=False,
                        message=f"I couldn't find the shop or vendor '{command.secondary_target}'.",
                        error="Shop not found",
                        command_type=command.action.name
                    )
            else:
                # Try to use current shop context
                shop = economic_object_resolver.resolve_shop_by_name_or_context(None, context)
                
                if not shop:
                    return CommandResult(
                        success=False,
                        message="I'm not sure which shop you want to browse. Please specify a shop.",
                        error="No shop specified or in context",
                        command_type=command.action.name
                    )
            
            # Get shop inventory
            try:
                items = self.shop_service.get_shop_inventory(shop.shop_id)
                
                if not items:
                    return CommandResult(
                        success=True,
                        message=f"{shop.name} doesn't have any items for sale at the moment.",
                        data={"items": [], "shop": shop.to_dict()},
                        command_type=command.action.name
                    )
                
                # Format response
                grouped_items = {}
                for item in items:
                    category = item.get("category", "Miscellaneous")
                    if category not in grouped_items:
                        grouped_items[category] = []
                    grouped_items[category].append(item)
                
                return CommandResult(
                    success=True,
                    message=f"Here are the items available at {shop.name}:",
                    data={"items": items, "grouped_items": grouped_items, "shop": shop.to_dict()},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting the shop inventory: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # View item details
        elif command.action == EconomicAction.VIEW_ITEM_DETAILS:
            # Try to find item in inventory first
            item = economic_object_resolver.resolve_item_in_inventory(
                command.primary_target, context, context.player_id
            )
            
            # If not found in inventory, try to find in shop
            if not item:
                item = economic_object_resolver.resolve_item_for_purchase(
                    command.primary_target, context
                )
            
            # If still not found, try to find as a material
            if not item:
                material = economic_object_resolver.resolve_material_for_crafting(
                    command.primary_target, context
                )
                
                if material:
                    # Convert material to item format
                    return CommandResult(
                        success=True,
                        message=f"Material information for {material.name}:",
                        data={
                            "item": material.to_dict(),
                            "is_material": True
                        },
                        command_type=command.action.name
                    )
            
            if not item:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find any information about '{command.primary_target}'.",
                    error="Item not found",
                    command_type=command.action.name
                )
            
            # Get detailed item information
            try:
                details = self.item_service.get_item_details(item.item_id)
                
                return CommandResult(
                    success=True,
                    message=f"Item information for {item.name}:",
                    data={"item": details or item.to_dict()},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting item details: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Get item price
        elif command.action == EconomicAction.GET_ITEM_PRICE:
            # Try to find as a shop item
            item = economic_object_resolver.resolve_item_for_purchase(
                command.primary_target, context
            )
            
            # If not found in shop, try to find in inventory
            if not item:
                item = economic_object_resolver.resolve_item_in_inventory(
                    command.primary_target, context, context.player_id
                )
            
            if not item:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find any price information for '{command.primary_target}'.",
                    error="Item not found",
                    command_type=command.action.name
                )
            
            # Get market price information
            try:
                price_info = self.economy_service.get_item_price_info(item.item_id)
                
                if price_info:
                    return CommandResult(
                        success=True,
                        message=f"Price information for {item.name}:",
                        data={"item": item.to_dict(), "price_info": price_info},
                        command_type=command.action.name
                    )
                else:
                    # Just return the base value if no market info
                    return CommandResult(
                        success=True,
                        message=f"{item.name} costs {item.value} gold.",
                        data={"item": item.to_dict(), "price": item.value},
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting price information: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Initiate bartering
        elif command.action == EconomicAction.INITIATE_BARTER:
            # TODO: Implement bartering system
            return CommandResult(
                success=False,
                message="The bartering system is not yet implemented.",
                error="Feature not implemented",
                command_type=command.action.name
            )
        
        # Default case
        return CommandResult(
            success=False,
            message="This shopping action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )
    
    def _handle_crafting_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle crafting-related commands."""
        if not self.recipe_service:
            return CommandResult(
                success=False,
                message="Crafting services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        # Craft item
        if command.action == EconomicAction.CRAFT_ITEM:
            # Resolve the recipe
            recipe = economic_object_resolver.resolve_recipe_for_crafting(
                command.primary_target, context
            )
            
            if not recipe:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a recipe for '{command.primary_target}'.",
                    error="Recipe not found",
                    command_type=command.action.name
                )
            
            # Determine quantity
            quantity = command.quantity or 1
            
            # Check if we can craft this recipe
            if not recipe.additional_data.get("can_craft", True):
                # Check what's missing
                if not recipe.additional_data.get("has_required_station", True):
                    return CommandResult(
                        success=False,
                        message=f"You need a {recipe.additional_data.get('required_station_type')} to craft {recipe.name}.",
                        error="Missing crafting station",
                        command_type=command.action.name,
                        data={"recipe": recipe.to_dict()}
                    )
                
                # Check if any ingredients are missing
                missing_ingredients = []
                for ingredient in recipe.ingredients:
                    if not ingredient.get("in_inventory", False) or ingredient.get("available_quantity", 0) < ingredient.get("quantity", 1) * quantity:
                        missing_ingredients.append(ingredient)
                
                if missing_ingredients:
                    message = f"You don't have enough materials to craft {recipe.name}. You need:"
                    for ingredient in missing_ingredients:
                        needed = ingredient.get("quantity", 1) * quantity
                        have = ingredient.get("available_quantity", 0)
                        message += f"\n- {ingredient.get('name')}: {have}/{needed}"
                    
                    return CommandResult(
                        success=False,
                        message=message,
                        error="Missing ingredients",
                        command_type=command.action.name,
                        data={"recipe": recipe.to_dict(), "missing_ingredients": missing_ingredients}
                    )
                
                # If no specific reason is given
                return CommandResult(
                    success=False,
                    message=f"You can't craft {recipe.name} at the moment.",
                    error="Cannot craft recipe",
                    command_type=command.action.name,
                    data={"recipe": recipe.to_dict()}
                )
            
            # Execute the crafting
            try:
                result = self.recipe_service.craft_item(
                    player_id=context.player_id,
                    recipe_id=recipe.recipe_id,
                    quantity=quantity
                )
                
                if result.get("success"):
                    # Get the output item name
                    output_name = "item"
                    for output in recipe.outputs:
                        if output.get("is_primary", False):
                            output_name = output.get("name", "item")
                            break
                    
                    return CommandResult(
                        success=True,
                        message=f"You successfully crafted {quantity} {output_name}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to craft {recipe.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error while crafting: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # List known recipes
        elif command.action == EconomicAction.LIST_KNOWN_RECIPES:
            try:
                recipes = self.recipe_service.get_known_recipes(
                    player_id=context.player_id
                )
                
                if not recipes:
                    return CommandResult(
                        success=True,
                        message="You don't know any recipes yet.",
                        data={"recipes": []},
                        command_type=command.action.name
                    )
                
                # Group recipes by category
                grouped_recipes = {}
                for recipe in recipes:
                    category = recipe.get("recipe_category", "Miscellaneous")
                    if category not in grouped_recipes:
                        grouped_recipes[category] = []
                    grouped_recipes[category].append(recipe)
                
                return CommandResult(
                    success=True,
                    message=f"You know {len(recipes)} recipes:",
                    data={"recipes": recipes, "grouped_recipes": grouped_recipes},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting your recipes: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # List craftable recipes
        elif command.action == EconomicAction.LIST_CRAFTABLE_RECIPES:
            try:
                recipes = self.recipe_service.get_craftable_recipes(
                    player_id=context.player_id
                )
                
                if not recipes:
                    return CommandResult(
                        success=True,
                        message="You can't craft any recipes at the moment.",
                        data={"recipes": []},
                        command_type=command.action.name
                    )
                
                # Group recipes by category
                grouped_recipes = {}
                for recipe in recipes:
                    category = recipe.get("recipe_category", "Miscellaneous")
                    if category not in grouped_recipes:
                        grouped_recipes[category] = []
                    grouped_recipes[category].append(recipe)
                
                return CommandResult(
                    success=True,
                    message=f"You can craft {len(recipes)} recipes:",
                    data={"recipes": recipes, "grouped_recipes": grouped_recipes},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting craftable recipes: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # View recipe details
        elif command.action == EconomicAction.VIEW_RECIPE_DETAILS:
            # Resolve the recipe
            recipe = economic_object_resolver.resolve_recipe_for_crafting(
                command.primary_target, context
            )
            
            if not recipe:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a recipe for '{command.primary_target}'.",
                    error="Recipe not found",
                    command_type=command.action.name
                )
            
            # Get detailed recipe information
            try:
                details = self.recipe_service.get_recipe_details(recipe.recipe_id)
                
                if details:
                    # If we got extended details, use those
                    return CommandResult(
                        success=True,
                        message=f"Recipe information for {recipe.name}:",
                        data={"recipe": details},
                        command_type=command.action.name
                    )
                else:
                    # Otherwise use what we have from the resolver
                    return CommandResult(
                        success=True,
                        message=f"Recipe information for {recipe.name}:",
                        data={"recipe": recipe.to_dict()},
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting recipe details: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Attempt recipe discovery
        elif command.action == EconomicAction.ATTEMPT_RECIPE_DISCOVERY:
            # This is for discovering a new recipe through experimentation
            target = command.primary_target
            
            try:
                result = self.recipe_service.attempt_recipe_discovery(
                    player_id=context.player_id,
                    target_name=target
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=result.get("message", f"You've made progress in discovering a recipe for {target}."),
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"You were unable to discover a recipe for {target}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error during recipe discovery: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Check crafting materials
        elif command.action == EconomicAction.CHECK_CRAFTING_MATERIALS:
            try:
                materials = self.recipe_service.get_player_crafting_materials(
                    player_id=context.player_id
                )
                
                if not materials:
                    return CommandResult(
                        success=True,
                        message="You don't have any crafting materials.",
                        data={"materials": []},
                        command_type=command.action.name
                    )
                
                # Group materials by type
                grouped_materials = {}
                for material in materials:
                    material_type = material.get("material_type", "Miscellaneous")
                    if material_type not in grouped_materials:
                        grouped_materials[material_type] = []
                    grouped_materials[material_type].append(material)
                
                return CommandResult(
                    success=True,
                    message=f"You have {len(materials)} different crafting materials:",
                    data={"materials": materials, "grouped_materials": grouped_materials},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error checking your crafting materials: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Default case
        return CommandResult(
            success=False,
            message="This crafting action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )
    
    def _handle_business_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle business management commands."""
        if not self.business_service:
            return CommandResult(
                success=False,
                message="Business management services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        # Resolve the business if not explicitly specified
        business = None
        if command.action != EconomicAction.HIRE_STAFF:  # For hiring, we handle it separately
            business = economic_object_resolver.resolve_player_owned_business(
                None, context  # Use context to get default business
            )
            
            if not business:
                return CommandResult(
                    success=False,
                    message="You don't own a business.",
                    error="No business found",
                    command_type=command.action.name
                )
        
        # View business status
        if command.action == EconomicAction.VIEW_BUSINESS_STATUS:
            try:
                status = self.business_service.get_business_status(business.business_id)
                
                if status:
                    return CommandResult(
                        success=True,
                        message=f"Status of {business.name}:",
                        data={"business": status},
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=True,
                        message=f"Status of {business.name}:",
                        data={"business": business.to_dict()},
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error getting business status: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Set product price
        elif command.action == EconomicAction.SET_PRODUCT_PRICE:
            if not command.primary_target or not command.price:
                return CommandResult(
                    success=False,
                    message="Please specify both the item and the new price.",
                    error="Missing item or price",
                    command_type=command.action.name
                )
            
            # Resolve the item
            item = economic_object_resolver.resolve_item_in_inventory(
                command.primary_target, context, business.owner_id
            )
            
            if not item:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find '{command.primary_target}' in your business inventory.",
                    error="Item not found in business inventory",
                    command_type=command.action.name
                )
            
            try:
                result = self.business_service.set_product_price(
                    business_id=business.business_id,
                    item_id=item.item_id,
                    price=command.price
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You set the price of {item.name} to {command.price} {command.currency_type or 'gold'}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to set price for {item.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error setting the product price: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Manage business inventory
        elif command.action == EconomicAction.MANAGE_BUSINESS_INVENTORY:
            try:
                inventory = self.business_service.get_business_inventory(business.business_id)
                
                if not inventory:
                    return CommandResult(
                        success=True,
                        message=f"{business.name} doesn't have any items in inventory.",
                        data={"inventory": []},
                        command_type=command.action.name
                    )
                
                # Group items by category
                grouped_inventory = {}
                for item in inventory:
                    category = item.get("category", "Miscellaneous")
                    if category not in grouped_inventory:
                        grouped_inventory[category] = []
                    grouped_inventory[category].append(item)
                
                return CommandResult(
                    success=True,
                    message=f"Inventory of {business.name}:",
                    data={"inventory": inventory, "grouped_inventory": grouped_inventory},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error retrieving the business inventory: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Hire staff
        elif command.action == EconomicAction.HIRE_STAFF:
            # First, make sure we have a business
            if not business:
                # Try to resolve by name if provided in the command
                if command.secondary_target:
                    business = economic_object_resolver.resolve_player_owned_business(
                        command.secondary_target, context
                    )
                
                # If still no business, try to get the default
                if not business:
                    business = economic_object_resolver.resolve_player_owned_business(
                        None, context
                    )
                
                if not business:
                    return CommandResult(
                        success=False,
                        message="You don't own a business to hire staff for.",
                        error="No business found",
                        command_type=command.action.name
                    )
            
            # Get the staff type from the command
            staff_type = command.primary_target
            if not staff_type:
                return CommandResult(
                    success=False,
                    message="Please specify what type of staff you want to hire.",
                    error="Missing staff type",
                    command_type=command.action.name
                )
            
            try:
                result = self.business_service.hire_staff(
                    business_id=business.business_id,
                    staff_type=staff_type
                )
                
                if result.get("success"):
                    staff_name = result.get("staff", {}).get("name", "new employee")
                    return CommandResult(
                        success=True,
                        message=f"You hired {staff_name} as a {staff_type} for {business.name}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to hire {staff_type}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error hiring staff: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Assign staff task
        elif command.action == EconomicAction.ASSIGN_STAFF_TASK:
            staff_name = command.primary_target
            task = command.modifiers.get("task")
            
            if not staff_name or not task:
                return CommandResult(
                    success=False,
                    message="Please specify both the staff member and the task to assign.",
                    error="Missing staff or task",
                    command_type=command.action.name
                )
            
            try:
                result = self.business_service.assign_staff_task(
                    business_id=business.business_id,
                    staff_name=staff_name,
                    task=task
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You assigned {staff_name} to {task}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to assign {staff_name} to {task}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error assigning the task: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Upgrade business
        elif command.action == EconomicAction.UPGRADE_BUSINESS:
            try:
                result = self.business_service.upgrade_business(business.business_id)
                
                if result.get("success"):
                    new_level = result.get("new_level", business.level + 1)
                    return CommandResult(
                        success=True,
                        message=f"You upgraded {business.name} to level {new_level}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to upgrade {business.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error upgrading the business: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # View business ledger
        elif command.action == EconomicAction.VIEW_BUSINESS_LEDGER:
            try:
                ledger = self.business_service.get_business_ledger(business.business_id)
                
                if not ledger or not ledger.get("transactions"):
                    return CommandResult(
                        success=True,
                        message=f"{business.name} has no financial transactions recorded.",
                        data={"ledger": {"transactions": []}},
                        command_type=command.action.name
                    )
                
                return CommandResult(
                    success=True,
                    message=f"Financial ledger for {business.name}:",
                    data={"ledger": ledger},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error retrieving the business ledger: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Pay business taxes
        elif command.action == EconomicAction.PAY_BUSINESS_TAXES:
            try:
                result = self.business_service.pay_business_taxes(business.business_id)
                
                if result.get("success"):
                    amount_paid = result.get("amount_paid", 0)
                    return CommandResult(
                        success=True,
                        message=f"You paid {amount_paid} gold in taxes for {business.name}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to pay taxes for {business.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error paying business taxes: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Collect business profits
        elif command.action == EconomicAction.COLLECT_BUSINESS_PROFITS:
            try:
                result = self.business_service.collect_business_profits(business.business_id)
                
                if result.get("success"):
                    amount_collected = result.get("amount_collected", 0)
                    return CommandResult(
                        success=True,
                        message=f"You collected {amount_collected} gold in profits from {business.name}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to collect profits from {business.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error collecting business profits: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Default case
        return CommandResult(
            success=False,
            message="This business management action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )
    
    def _handle_building_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle building-related commands."""
        if not self.building_service:
            return CommandResult(
                success=False,
                message="Building services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        # Construct building
        if command.action == EconomicAction.CONSTRUCT_BUILDING:
            # Resolve the building template
            template = economic_object_resolver.resolve_building_template_for_construction(
                command.primary_target, context
            )
            
            if not template:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a building template for '{command.primary_target}'.",
                    error="Building template not found",
                    command_type=command.action.name
                )
            
            # Resolve the plot if provided
            plot = None
            if command.secondary_target:
                plot = economic_object_resolver.resolve_land_plot_for_building(
                    command.secondary_target, context
                )
                
                if not plot:
                    return CommandResult(
                        success=False,
                        message=f"I couldn't find a plot at '{command.secondary_target}'.",
                        error="Plot not found",
                        command_type=command.action.name
                    )
            
            try:
                result = self.building_service.construct_building(
                    player_id=context.player_id,
                    template_id=template.template_id,
                    plot_id=plot.plot_id if plot else None,
                    location_id=context.location_id if not plot else None
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You've started construction of a {template.name}. It will be completed in {template.construction_time // 3600} hours.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to start construction of {template.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error starting construction: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Upgrade building
        elif command.action == EconomicAction.UPGRADE_BUILDING:
            # Resolve the building
            building = economic_object_resolver.resolve_building_by_name(
                command.primary_target, context
            )
            
            if not building:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a building named '{command.primary_target}'.",
                    error="Building not found",
                    command_type=command.action.name
                )
            
            try:
                result = self.building_service.upgrade_building(building.building_id)
                
                if result.get("success"):
                    new_level = result.get("new_level", building.level + 1)
                    return CommandResult(
                        success=True,
                        message=f"You've started upgrading {building.name} to level {new_level}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to upgrade {building.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error upgrading the building: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # List available buildings
        elif command.action == EconomicAction.LIST_AVAILABLE_BUILDINGS:
            try:
                templates = self.building_service.get_available_building_templates(
                    player_id=context.player_id,
                    location_id=context.location_id
                )
                
                if not templates:
                    return CommandResult(
                        success=True,
                        message="There are no building templates available to you.",
                        data={"templates": []},
                        command_type=command.action.name
                    )
                
                # Group templates by type
                grouped_templates = {}
                for template in templates:
                    building_type = template.get("building_type", "Miscellaneous")
                    if building_type not in grouped_templates:
                        grouped_templates[building_type] = []
                    grouped_templates[building_type].append(template)
                
                return CommandResult(
                    success=True,
                    message=f"Available building templates:",
                    data={"templates": templates, "grouped_templates": grouped_templates},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error retrieving building templates: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # View building details
        elif command.action == EconomicAction.VIEW_BUILDING_DETAILS:
            # Try to resolve as an existing building first
            building = economic_object_resolver.resolve_building_by_name(
                command.primary_target, context
            )
            
            if building:
                try:
                    details = self.building_service.get_building_details(building.building_id)
                    
                    if details:
                        return CommandResult(
                            success=True,
                            message=f"Building information for {building.name}:",
                            data={"building": details},
                            command_type=command.action.name
                        )
                    else:
                        return CommandResult(
                            success=True,
                            message=f"Building information for {building.name}:",
                            data={"building": building.to_dict()},
                            command_type=command.action.name
                        )
                
                except Exception as e:
                    return CommandResult(
                        success=False,
                        message=f"There was an error retrieving building details: {str(e)}",
                        error=str(e),
                        command_type=command.action.name
                    )
            
            # If not an existing building, try to resolve as a template
            template = economic_object_resolver.resolve_building_template_for_construction(
                command.primary_target, context
            )
            
            if template:
                return CommandResult(
                    success=True,
                    message=f"Building template information for {template.name}:",
                    data={"template": template.to_dict()},
                    command_type=command.action.name
                )
            
            return CommandResult(
                success=False,
                message=f"I couldn't find a building or template named '{command.primary_target}'.",
                error="Building or template not found",
                command_type=command.action.name
            )
        
        # Repair building
        elif command.action == EconomicAction.REPAIR_BUILDING:
            # Resolve the building
            building = economic_object_resolver.resolve_building_by_name(
                command.primary_target, context
            )
            
            if not building:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a building named '{command.primary_target}'.",
                    error="Building not found",
                    command_type=command.action.name
                )
            
            try:
                result = self.building_service.repair_building(building.building_id)
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You've repaired {building.name}.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to repair {building.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error repairing the building: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Buy property
        elif command.action == EconomicAction.BUY_PROPERTY:
            # Resolve the plot
            plot = economic_object_resolver.resolve_land_plot_for_building(
                command.primary_target, context
            )
            
            if not plot:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a plot at '{command.primary_target}'.",
                    error="Plot not found",
                    command_type=command.action.name
                )
            
            try:
                result = self.building_service.buy_property(
                    player_id=context.player_id,
                    plot_id=plot.plot_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You've purchased {plot.name} for {result.get('price', plot.price)} gold.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to purchase {plot.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error purchasing the property: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Sell property
        elif command.action == EconomicAction.SELL_PROPERTY:
            # Resolve the plot
            plot = economic_object_resolver.resolve_land_plot_for_building(
                command.primary_target, context
            )
            
            if not plot:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find a plot at '{command.primary_target}'.",
                    error="Plot not found",
                    command_type=command.action.name
                )
            
            try:
                result = self.building_service.sell_property(
                    player_id=context.player_id,
                    plot_id=plot.plot_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=f"You've sold {plot.name} for {result.get('price', 0)} gold.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to sell {plot.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error selling the property: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Default case
        return CommandResult(
            success=False,
            message="This building action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )
    
    def _handle_inventory_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle inventory and resource related commands."""
        if not self.item_service or not self.player_service:
            return CommandResult(
                success=False,
                message="Inventory services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        # Check inventory
        if command.action == EconomicAction.CHECK_INVENTORY:
            try:
                # If a specific item was mentioned, get details on that
                if command.primary_target:
                    item = economic_object_resolver.resolve_item_in_inventory(
                        command.primary_target, context, context.player_id
                    )
                    
                    if not item:
                        return CommandResult(
                            success=False,
                            message=f"I couldn't find '{command.primary_target}' in your inventory.",
                            error="Item not found in inventory",
                            command_type=command.action.name
                        )
                    
                    return CommandResult(
                        success=True,
                        message=f"You have {item.additional_data.get('quantity', 1)} {item.name} in your inventory.",
                        data={"item": item.to_dict()},
                        command_type=command.action.name
                    )
                
                # Otherwise, get the full inventory
                inventory = self.item_service.get_player_inventory(context.player_id)
                
                if not inventory:
                    return CommandResult(
                        success=True,
                        message="Your inventory is empty.",
                        data={"inventory": []},
                        command_type=command.action.name
                    )
                
                # Group items by category
                grouped_inventory = {}
                for item in inventory:
                    category = item.get("category", "Miscellaneous")
                    if category not in grouped_inventory:
                        grouped_inventory[category] = []
                    grouped_inventory[category].append(item)
                
                return CommandResult(
                    success=True,
                    message=f"Your inventory contains {len(inventory)} items:",
                    data={"inventory": inventory, "grouped_inventory": grouped_inventory},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error checking your inventory: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Check currency
        elif command.action == EconomicAction.CHECK_CURRENCY:
            try:
                balance = self.player_service.get_player_currency(context.player_id)
                
                if isinstance(balance, dict):
                    # Multiple currency types
                    message = "Your current balance:"
                    for currency, amount in balance.items():
                        message += f"\n- {currency}: {amount}"
                    
                    return CommandResult(
                        success=True,
                        message=message,
                        data={"balance": balance},
                        command_type=command.action.name
                    )
                else:
                    # Single default currency
                    return CommandResult(
                        success=True,
                        message=f"You have {balance} gold.",
                        data={"balance": {"gold": balance}},
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error checking your currency: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Locate material source
        elif command.action == EconomicAction.LOCATE_MATERIAL_SOURCE:
            # Resolve the material
            material = economic_object_resolver.resolve_material_for_crafting(
                command.primary_target, context
            )
            
            if not material:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find information about '{command.primary_target}'.",
                    error="Material not found",
                    command_type=command.action.name
                )
            
            try:
                sources = self.economy_service.get_material_sources(
                    material_id=material.material_id,
                    region_id=context.location_id if hasattr(context, "location_id") else None
                )
                
                if not sources:
                    return CommandResult(
                        success=True,
                        message=f"I couldn't find any sources for {material.name} in this region.",
                        data={"material": material.to_dict(), "sources": []},
                        command_type=command.action.name
                    )
                
                return CommandResult(
                    success=True,
                    message=f"Sources for {material.name}:",
                    data={"material": material.to_dict(), "sources": sources},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error locating material sources: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Default case
        return CommandResult(
            success=False,
            message="This inventory action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )
    
    def _handle_market_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle market-related commands."""
        if not self.economy_service and command.action != EconomicAction.ACCESS_BLACK_MARKET:
            return CommandResult(
                success=False,
                message="Market services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        if command.action == EconomicAction.ACCESS_BLACK_MARKET:
            if not self.black_market_service:
                return CommandResult(
                    success=False,
                    message="Black market services are not available at this time.",
                    error="Required services not available",
                    command_type=command.action.name
                )
            
            try:
                result = self.black_market_service.access_black_market(
                    player_id=context.player_id,
                    location_id=context.location_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=result.get("message", "You've accessed the black market."),
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", "Failed to access the black market."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error accessing the black market: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        elif command.action == EconomicAction.LIST_BLACK_MARKET_GOODS:
            if not self.black_market_service:
                return CommandResult(
                    success=False,
                    message="Black market services are not available at this time.",
                    error="Required services not available",
                    command_type=command.action.name
                )
            
            try:
                goods = self.black_market_service.get_black_market_goods(
                    player_id=context.player_id,
                    location_id=context.location_id
                )
                
                if not goods:
                    return CommandResult(
                        success=True,
                        message="There are no black market goods available here.",
                        data={"goods": []},
                        command_type=command.action.name
                    )
                
                # Group goods by category
                grouped_goods = {}
                for item in goods:
                    category = item.get("category", "Miscellaneous")
                    if category not in grouped_goods:
                        grouped_goods[category] = []
                    grouped_goods[category].append(item)
                
                return CommandResult(
                    success=True,
                    message=f"Black market goods available:",
                    data={"goods": goods, "grouped_goods": grouped_goods},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error retrieving black market goods: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        elif command.action == EconomicAction.GET_MARKET_PRICE_INFO:
            try:
                # If a specific item was mentioned, get market price for that
                if command.primary_target:
                    # Try to resolve as an item
                    item = economic_object_resolver.resolve_item_for_purchase(
                        command.primary_target, context
                    )
                    
                    if not item:
                        # Try to resolve as a material
                        material = economic_object_resolver.resolve_material_for_crafting(
                            command.primary_target, context
                        )
                        
                        if material:
                            price_info = self.economy_service.get_material_price_info(
                                material_id=material.material_id,
                                region_id=context.location_id
                            )
                            
                            return CommandResult(
                                success=True,
                                message=f"Market price information for {material.name}:",
                                data={"material": material.to_dict(), "price_info": price_info},
                                command_type=command.action.name
                            )
                    
                    if not item:
                        return CommandResult(
                            success=False,
                            message=f"I couldn't find market information for '{command.primary_target}'.",
                            error="Item not found",
                            command_type=command.action.name
                        )
                    
                    price_info = self.economy_service.get_item_price_info(
                        item_id=item.item_id,
                        region_id=context.location_id
                    )
                    
                    return CommandResult(
                        success=True,
                        message=f"Market price information for {item.name}:",
                        data={"item": item.to_dict(), "price_info": price_info},
                        command_type=command.action.name
                    )
                
                # Otherwise, get general market prices
                market_prices = self.economy_service.get_market_prices(
                    region_id=context.location_id
                )
                
                if not market_prices:
                    return CommandResult(
                        success=True,
                        message="There is no market price information available for this region.",
                        data={"market_prices": []},
                        command_type=command.action.name
                    )
                
                return CommandResult(
                    success=True,
                    message=f"Market prices in this region:",
                    data={"market_prices": market_prices},
                    command_type=command.action.name
                )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error retrieving market price information: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Default case
        return CommandResult(
            success=False,
            message="This market action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )
    
    def _handle_illicit_command(self, command: ParsedEconomicCommand, context: GameContext) -> CommandResult:
        """Handle illicit operations commands."""
        if not self.black_market_service:
            return CommandResult(
                success=False,
                message="Black market services are not available at this time.",
                error="Required services not available",
                command_type=command.action.name
            )
        
        # Start illicit operation
        if command.action == EconomicAction.START_ILLICIT_OPERATION:
            operation_type = command.primary_target
            
            if not operation_type:
                return CommandResult(
                    success=False,
                    message="Please specify what type of illicit operation you want to start.",
                    error="Missing operation type",
                    command_type=command.action.name
                )
            
            try:
                result = self.black_market_service.start_illicit_operation(
                    player_id=context.player_id,
                    operation_type=operation_type,
                    location_id=context.location_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=result.get("message", f"You've started a {operation_type} operation."),
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to start {operation_type} operation."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error starting the illicit operation: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Launder money
        elif command.action == EconomicAction.LAUNDER_MONEY:
            try:
                result = self.black_market_service.launder_money(
                    player_id=context.player_id,
                    location_id=context.location_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=result.get("message", "You've laundered your money."),
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", "Failed to launder money."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error laundering money: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Bribe authority
        elif command.action == EconomicAction.BRIBE_AUTHORITY:
            authority = command.primary_target
            
            if not authority:
                return CommandResult(
                    success=False,
                    message="Please specify who you want to bribe.",
                    error="Missing authority target",
                    command_type=command.action.name
                )
            
            try:
                result = self.black_market_service.bribe_authority(
                    player_id=context.player_id,
                    authority_name=authority,
                    location_id=context.location_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=result.get("message", f"You've bribed {authority}."),
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to bribe {authority}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error bribing the authority: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Check heat level
        elif command.action == EconomicAction.CHECK_HEAT_LEVEL:
            try:
                result = self.black_market_service.get_heat_level(
                    player_id=context.player_id,
                    location_id=context.location_id
                )
                
                if result:
                    heat_level = result.get("heat_level", 0)
                    authority_presence = result.get("authority_presence", 0)
                    
                    # Describe the heat level
                    heat_description = "nonexistent"
                    if heat_level >= 0.8:
                        heat_description = "extreme"
                    elif heat_level >= 0.6:
                        heat_description = "high"
                    elif heat_level >= 0.4:
                        heat_description = "moderate"
                    elif heat_level >= 0.2:
                        heat_description = "low"
                    elif heat_level > 0:
                        heat_description = "minimal"
                    
                    # Describe the authority presence
                    authority_description = "nonexistent"
                    if authority_presence >= 4:
                        authority_description = "overwhelming"
                    elif authority_presence == 3:
                        authority_description = "heavy"
                    elif authority_presence == 2:
                        authority_description = "moderate"
                    elif authority_presence == 1:
                        authority_description = "light"
                    
                    return CommandResult(
                        success=True,
                        message=f"Current heat level is {heat_description} with {authority_description} authority presence.",
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=True,
                        message="No heat level information available for this location.",
                        data={"heat_level": 0, "authority_presence": 0},
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error checking the heat level: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Fence stolen goods
        elif command.action == EconomicAction.FENCE_STOLEN_GOODS:
            item_name = command.primary_target
            
            if not item_name:
                return CommandResult(
                    success=False,
                    message="Please specify what item you want to fence.",
                    error="Missing item name",
                    command_type=command.action.name
                )
            
            # Resolve the item from inventory
            item = economic_object_resolver.resolve_item_in_inventory(
                item_name, context, context.player_id
            )
            
            if not item:
                return CommandResult(
                    success=False,
                    message=f"I couldn't find '{item_name}' in your inventory.",
                    error="Item not found in inventory",
                    command_type=command.action.name
                )
            
            try:
                result = self.black_market_service.fence_stolen_goods(
                    player_id=context.player_id,
                    item_id=item.item_id,
                    quantity=command.quantity or 1,
                    location_id=context.location_id
                )
                
                if result.get("success"):
                    return CommandResult(
                        success=True,
                        message=result.get("message", f"You've fenced {item.name}."),
                        data=result,
                        command_type=command.action.name
                    )
                else:
                    return CommandResult(
                        success=False,
                        message=result.get("message", f"Failed to fence {item.name}."),
                        error=result.get("error"),
                        command_type=command.action.name
                    )
            
            except Exception as e:
                return CommandResult(
                    success=False,
                    message=f"There was an error fencing the item: {str(e)}",
                    error=str(e),
                    command_type=command.action.name
                )
        
        # Default case
        return CommandResult(
            success=False,
            message="This illicit action is not yet implemented.",
            error="Action not implemented",
            command_type=command.action.name
        )


# Create a global instance of the economic command handler
economic_command_handler = EconomicCommandHandler()