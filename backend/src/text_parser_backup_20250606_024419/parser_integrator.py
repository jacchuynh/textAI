"""
Text Parser Integrator Module

This module serves as the main interface between the text parser and the game's economic systems.
It processes parsed commands related to crafting, trading, and economic activities,
then routes them to the appropriate economic subsystems.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Union
import json

# Import economic subsystems
from backend.src.crafting.services.crafting_integration_service import create_crafting_integration_service
from backend.src.crafting.services.material_service import MaterialService
from backend.src.crafting.services.recipe_service import RecipeService
from backend.src.crafting.services.crafting_service import CraftingService
from backend.src.economy.services.economy_service import EconomyService
from backend.src.business.api.business_api import BusinessAPI
from backend.src.business.api.black_market_api import BlackMarketAPI

# Import AI GM integration
from backend.src.ai_gm.crafting_npc_behavior import CraftingNPCBehavior

logger = logging.getLogger(__name__)

class ParserIntegrator:
    """
    Main interface between the text parser and the game's economic systems.
    
    This class receives parsed commands related to economic activities and routes them
    to the appropriate subsystems (crafting, trading, business operations, etc.).
    """
    
    def __init__(self):
        """Initialize the parser integrator with connections to all economic subsystems."""
        self.crafting_integration = create_crafting_integration_service()
        self.material_service = MaterialService()
        self.recipe_service = RecipeService()
        self.crafting_service = CraftingService()
        self.economy_service = EconomyService()
        self.business_api = BusinessAPI()
        self.black_market_api = BlackMarketAPI()
        
        # Command patterns for different economic activities
        self.command_patterns = self._initialize_command_patterns()
        
        logger.info("Parser Integrator initialized with connections to all economic subsystems")
    
    def close(self):
        """Close all service connections."""
        if hasattr(self, 'crafting_integration') and self.crafting_integration:
            self.crafting_integration.close()
        if hasattr(self, 'material_service') and self.material_service:
            self.material_service.close()
        if hasattr(self, 'recipe_service') and self.recipe_service:
            self.recipe_service.close()
        if hasattr(self, 'crafting_service') and self.crafting_service:
            self.crafting_service.close()
        if hasattr(self, 'economy_service') and self.economy_service:
            self.economy_service.close()
    
    def _initialize_command_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Initialize patterns for recognizing economic commands in player text.
        
        Returns:
            A dictionary mapping command categories to lists of pattern dictionaries
        """
        return {
            "crafting": [
                {
                    "pattern": r"(?i)craft\s+(?P<item_name>.+?)(?:\s+using\s+(?P<materials>.+))?$",
                    "action": "craft_item",
                    "description": "Craft an item, optionally specifying materials to use"
                },
                {
                    "pattern": r"(?i)learn\s+recipe(?:\s+for\s+)?(?P<recipe_name>.+)$",
                    "action": "learn_recipe",
                    "description": "Learn a new crafting recipe"
                },
                {
                    "pattern": r"(?i)(?:what\s+can\s+I\s+craft|show\s+(?:my\s+)?recipes)(?:\s+for\s+(?P<profession>.+))?$",
                    "action": "list_recipes",
                    "description": "List recipes the player knows, optionally filtering by profession"
                }
            ],
            "material_gathering": [
                {
                    "pattern": r"(?i)(?:gather|collect|mine|harvest)\s+(?P<material_name>.+?)(?:\s+from\s+(?P<source>.+))?$",
                    "action": "gather_material",
                    "description": "Gather materials from the environment"
                },
                {
                    "pattern": r"(?i)(?:search|look)\s+for\s+(?P<material_name>.+?)(?:\s+in\s+(?P<location>.+))?$",
                    "action": "search_for_material",
                    "description": "Search for specific materials in the current area"
                }
            ],
            "trading": [
                {
                    "pattern": r"(?i)(?:sell|trade)\s+(?P<quantity>\d+)?\s*(?P<item_name>.+?)(?:\s+to\s+(?P<npc_name>.+?))?(?:\s+for\s+(?P<price>\d+))?$",
                    "action": "sell_item",
                    "description": "Sell items to an NPC or the market"
                },
                {
                    "pattern": r"(?i)(?:buy|purchase)\s+(?P<quantity>\d+)?\s*(?P<item_name>.+?)(?:\s+from\s+(?P<npc_name>.+?))?$",
                    "action": "buy_item",
                    "description": "Buy items from an NPC or the market"
                },
                {
                    "pattern": r"(?i)check\s+(?:price|value)(?:\s+of\s+)?(?P<item_name>.+?)$",
                    "action": "check_price",
                    "description": "Check the market price of an item"
                }
            ],
            "business": [
                {
                    "pattern": r"(?i)(?:open|start|establish)\s+(?:a\s+)?(?P<business_type>.+?)(?:\s+(?:business|shop|store))?(?:\s+in\s+(?P<location>.+))?$",
                    "action": "start_business",
                    "description": "Start a new business"
                },
                {
                    "pattern": r"(?i)(?:manage|run|check)\s+(?:my\s+)?(?P<business_type>.+?)(?:\s+(?:business|shop|store))?$",
                    "action": "manage_business",
                    "description": "Manage an existing business"
                },
                {
                    "pattern": r"(?i)hire\s+(?P<npc_type>.+?)(?:\s+for\s+(?:my\s+)?(?P<business_type>.+?))?$",
                    "action": "hire_employee",
                    "description": "Hire an employee for a business"
                }
            ],
            "black_market": [
                {
                    "pattern": r"(?i)(?:find|contact|locate)(?:\s+the\s+)?(?:black\s+market|underground\s+market|smuggler)(?:\s+in\s+(?P<location>.+))?$",
                    "action": "find_black_market",
                    "description": "Find black market vendors"
                },
                {
                    "pattern": r"(?i)smuggle\s+(?P<item_name>.+?)(?:\s+to\s+(?P<destination>.+))?$",
                    "action": "smuggle_items",
                    "description": "Smuggle illicit goods to a destination"
                }
            ],
            "economy_information": [
                {
                    "pattern": r"(?i)check\s+(?:the\s+)?(?:economy|market|prices)(?:\s+in\s+(?P<location>.+))?$",
                    "action": "check_economy",
                    "description": "Get information about the local economy"
                },
                {
                    "pattern": r"(?i)(?:what|which)\s+(?:materials|resources)(?:\s+are\s+)?(?:available|found)(?:\s+in\s+(?P<location>.+))?$",
                    "action": "list_regional_materials",
                    "description": "List materials available in a region"
                }
            ]
        }
    
    def process_text_command(self, player_id: str, command_text: str, 
                            context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a text command related to economic activities.
        
        Args:
            player_id: The ID of the player issuing the command
            command_text: The text command to process
            context: Optional context information (location, NPCs present, etc.)
            
        Returns:
            A dictionary with the processing results
        """
        logger.info(f"Processing economic command from player {player_id}: '{command_text}'")
        
        if not context:
            context = {}
        
        # Default response
        response = {
            "success": False,
            "message": "I don't understand that command related to crafting or trading.",
            "command": command_text,
            "matched_action": None
        }
        
        # Try to match the command against known patterns
        matched_pattern, match_groups = self._match_command_pattern(command_text)
        
        if matched_pattern:
            action = matched_pattern.get("action")
            response["matched_action"] = action
            
            try:
                # Route to appropriate handler based on action
                if action.startswith("craft_"):
                    response = self._handle_crafting_command(player_id, action, match_groups, context)
                elif action.startswith("gather_") or action.startswith("search_"):
                    response = self._handle_gathering_command(player_id, action, match_groups, context)
                elif action.startswith("sell_") or action.startswith("buy_") or action.startswith("check_price"):
                    response = self._handle_trading_command(player_id, action, match_groups, context)
                elif action.startswith("start_") or action.startswith("manage_") or action.startswith("hire_"):
                    response = self._handle_business_command(player_id, action, match_groups, context)
                elif action.startswith("find_") or action.startswith("smuggle_"):
                    response = self._handle_black_market_command(player_id, action, match_groups, context)
                elif action.startswith("check_") or action.startswith("list_"):
                    response = self._handle_information_command(player_id, action, match_groups, context)
                else:
                    logger.warning(f"Matched action {action} has no handler")
                    response["message"] = f"I recognized your command about {action.replace('_', ' ')}, but I don't know how to process it yet."
            except Exception as e:
                logger.error(f"Error processing command {action}: {e}", exc_info=True)
                response["message"] = f"There was an error processing your request: {str(e)}"
        
        return response
    
    def _match_command_pattern(self, command_text: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, str]]]:
        """
        Match a command text against known patterns.
        
        Args:
            command_text: The text command to match
            
        Returns:
            A tuple of (matched pattern dict, match groups dict) or (None, None) if no match
        """
        for category, patterns in self.command_patterns.items():
            for pattern_dict in patterns:
                match = re.match(pattern_dict["pattern"], command_text)
                if match:
                    return pattern_dict, match.groupdict()
        
        return None, None
    
    def _handle_crafting_command(self, player_id: str, action: str, 
                               match_groups: Dict[str, str], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle crafting-related commands.
        
        Args:
            player_id: The ID of the player issuing the command
            action: The matched action type
            match_groups: Dictionary of matched pattern groups
            context: Context information
            
        Returns:
            A dictionary with the processing results
        """
        if action == "craft_item":
            item_name = match_groups.get("item_name", "").strip()
            materials_str = match_groups.get("materials", "").strip()
            
            # Convert materials string to a list of materials if provided
            specified_materials = []
            if materials_str:
                # Simple parsing: split by commas or "and"
                materials_str = materials_str.replace(" and ", ", ")
                materials_list = [m.strip() for m in materials_str.split(",") if m.strip()]
                
                # Process each material to extract quantity and name
                for material in materials_list:
                    # Try to extract quantity
                    quantity_match = re.match(r"(?P<quantity>\d+)\s+(?P<name>.+)", material)
                    if quantity_match:
                        material_dict = {
                            "name": quantity_match.group("name"),
                            "quantity": int(quantity_match.group("quantity"))
                        }
                    else:
                        material_dict = {
                            "name": material,
                            "quantity": 1
                        }
                    specified_materials.append(material_dict)
            
            # Look up the recipe
            recipe_result = self.recipe_service.find_recipe_by_name(item_name)
            
            if not recipe_result.get("success", False):
                return {
                    "success": False,
                    "message": f"I couldn't find a recipe for {item_name}. Are you sure you know how to craft this item?",
                    "action": action,
                    "item_name": item_name
                }
            
            recipe = recipe_result.get("recipe")
            
            # Check if player knows the recipe
            knows_recipe = self.recipe_service.player_knows_recipe(player_id, recipe.id)
            
            if not knows_recipe:
                return {
                    "success": False,
                    "message": f"You don't know how to craft {item_name}. You need to learn this recipe first.",
                    "action": action,
                    "item_name": item_name,
                    "recipe_exists": True
                }
            
            # Check if player has required skills
            skill_check = self._check_player_crafting_skills(player_id, recipe.required_skills)
            
            if not skill_check["has_skills"]:
                missing_skills = skill_check["missing_skills"]
                missing_skills_str = ", ".join([f"{skill['skill_name']} (level {skill['level']} required)" for skill in missing_skills])
                
                return {
                    "success": False,
                    "message": f"You lack the skills to craft {item_name}. You need: {missing_skills_str}",
                    "action": action,
                    "item_name": item_name,
                    "missing_skills": missing_skills
                }
            
            # Check if player has required materials
            required_materials = []
            for ingredient in recipe.ingredients:
                material = self.material_service.get_material_by_id(ingredient.item_id)
                if material.get("success", False):
                    required_materials.append({
                        "id": ingredient.item_id,
                        "name": material["material"].name,
                        "quantity": ingredient.quantity,
                        "consumed": ingredient.consumed_in_crafting
                    })
            
            # Check if player has the materials
            has_materials, missing_materials = self._check_player_has_materials(player_id, required_materials)
            
            if not has_materials:
                missing_str = ", ".join([f"{item['name']} (need {item['quantity']}, have {item['have']})" for item in missing_materials])
                
                return {
                    "success": False,
                    "message": f"You don't have all the required materials to craft {item_name}. You need: {missing_str}",
                    "action": action,
                    "item_name": item_name,
                    "missing_materials": missing_materials
                }
            
            # Check if in appropriate location with required crafting station
            required_station = recipe.required_station_type
            has_station = self._check_player_has_crafting_station(player_id, required_station, context)
            
            if not has_station:
                return {
                    "success": False,
                    "message": f"You need access to a {required_station} to craft {item_name}. Find an appropriate crafting location.",
                    "action": action,
                    "item_name": item_name,
                    "required_station": required_station
                }
            
            # All checks passed, attempt crafting
            craft_result = self.crafting_service.craft_item(
                player_id=player_id,
                recipe_id=recipe.id,
                quality_modifier=0.0,  # Base quality
                specified_materials=specified_materials if specified_materials else None
            )
            
            if craft_result.success:
                # Format output message
                outputs_str = []
                for output in craft_result.outputs:
                    if output.get("quantity", 0) > 0:
                        quality_str = ""
                        if output.get("quality") > 0:
                            quality_str = f" (Quality: {output['quality']})"
                        outputs_str.append(f"{output['quantity']} {output['name']}{quality_str}")
                
                outputs_message = ", ".join(outputs_str)
                
                # Format experience message
                exp_str = []
                for exp in craft_result.experience_gained:
                    exp_str.append(f"{exp['amount']} {exp['skill_name']} experience")
                
                exp_message = ""
                if exp_str:
                    exp_message = f" You gained {', '.join(exp_str)}."
                
                return {
                    "success": True,
                    "message": f"You successfully crafted {outputs_message}.{exp_message}",
                    "action": action,
                    "item_name": item_name,
                    "crafting_result": {
                        "outputs": craft_result.outputs,
                        "consumed_ingredients": craft_result.consumed_ingredients,
                        "experience_gained": craft_result.experience_gained,
                        "quality_achieved": craft_result.quality_achieved
                    }
                }
            else:
                return {
                    "success": False,
                    "message": craft_result.message,
                    "action": action,
                    "item_name": item_name
                }
        
        elif action == "learn_recipe":
            recipe_name = match_groups.get("recipe_name", "").strip()
            
            # Look up the recipe
            recipe_result = self.recipe_service.find_recipe_by_name(recipe_name)
            
            if not recipe_result.get("success", False):
                return {
                    "success": False,
                    "message": f"I couldn't find a recipe for {recipe_name}.",
                    "action": action,
                    "recipe_name": recipe_name
                }
            
            recipe = recipe_result.get("recipe")
            
            # Check if player already knows the recipe
            knows_recipe = self.recipe_service.player_knows_recipe(player_id, recipe.id)
            
            if knows_recipe:
                return {
                    "success": False,
                    "message": f"You already know how to craft {recipe_name}.",
                    "action": action,
                    "recipe_name": recipe_name
                }
            
            # Check if recipe is discoverable
            if not recipe.is_discoverable:
                # Check context for a teacher NPC or recipe book
                has_teacher = context.get("has_recipe_teacher", False)
                has_recipe_book = context.get("has_recipe_book", False)
                
                if not (has_teacher or has_recipe_book):
                    return {
                        "success": False,
                        "message": f"You need someone to teach you this recipe or a recipe book to learn it.",
                        "action": action,
                        "recipe_name": recipe_name
                    }
            
            # Check if player meets skill requirements
            if recipe.auto_learn_at_skill_level:
                skill_name = recipe.auto_learn_at_skill_level.skill_name
                required_level = recipe.auto_learn_at_skill_level.level
                
                player_skill_level = self._get_player_skill_level(player_id, skill_name)
                
                if player_skill_level < required_level:
                    return {
                        "success": False,
                        "message": f"You need {skill_name} level {required_level} to learn this recipe. Your current level is {player_skill_level}.",
                        "action": action,
                        "recipe_name": recipe_name,
                        "required_skill": {
                            "name": skill_name,
                            "level": required_level,
                            "current_level": player_skill_level
                        }
                    }
            
            # All checks passed, learn the recipe
            learn_result = self.recipe_service.add_recipe_to_player(player_id, recipe.id)
            
            if learn_result:
                return {
                    "success": True,
                    "message": f"You've learned how to craft {recipe_name}!",
                    "action": action,
                    "recipe_name": recipe_name,
                    "recipe_data": {
                        "id": recipe.id,
                        "name": recipe.name,
                        "description": recipe.description,
                        "difficulty": recipe.difficulty_level,
                        "category": recipe.recipe_category
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"There was an error learning the recipe for {recipe_name}.",
                    "action": action,
                    "recipe_name": recipe_name
                }
        
        elif action == "list_recipes":
            profession = match_groups.get("profession", "").strip()
            
            # Get recipes the player knows
            known_recipes = self.recipe_service.get_player_known_recipes(player_id)
            
            if not known_recipes:
                return {
                    "success": False,
                    "message": "You don't know any crafting recipes yet.",
                    "action": action,
                    "recipes": []
                }
            
            # Filter by profession if specified
            if profession:
                filtered_recipes = []
                for recipe in known_recipes:
                    if profession.lower() in recipe.recipe_category.lower():
                        filtered_recipes.append(recipe)
                
                if not filtered_recipes:
                    return {
                        "success": False,
                        "message": f"You don't know any {profession} recipes yet.",
                        "action": action,
                        "profession": profession,
                        "recipes": []
                    }
                
                # Group recipes by category
                recipes_by_category = {}
                for recipe in filtered_recipes:
                    category = recipe.recipe_category
                    if category not in recipes_by_category:
                        recipes_by_category[category] = []
                    recipes_by_category[category].append(recipe)
                
                # Format the response
                message = f"Your known {profession} recipes:\n\n"
                for category, recipes in recipes_by_category.items():
                    message += f"--- {category} ---\n"
                    for recipe in recipes:
                        message += f"• {recipe.name} (Difficulty: {recipe.difficulty_level})\n"
                    message += "\n"
                
                return {
                    "success": True,
                    "message": message.strip(),
                    "action": action,
                    "profession": profession,
                    "recipes": [self._recipe_to_dict(r) for r in filtered_recipes],
                    "recipes_by_category": {k: [self._recipe_to_dict(r) for r in v] for k, v in recipes_by_category.items()}
                }
            else:
                # Group recipes by category
                recipes_by_category = {}
                for recipe in known_recipes:
                    category = recipe.recipe_category
                    if category not in recipes_by_category:
                        recipes_by_category[category] = []
                    recipes_by_category[category].append(recipe)
                
                # Format the response
                message = "Your known recipes:\n\n"
                for category, recipes in recipes_by_category.items():
                    message += f"--- {category} ---\n"
                    for recipe in recipes:
                        message += f"• {recipe.name} (Difficulty: {recipe.difficulty_level})\n"
                    message += "\n"
                
                return {
                    "success": True,
                    "message": message.strip(),
                    "action": action,
                    "recipes": [self._recipe_to_dict(r) for r in known_recipes],
                    "recipes_by_category": {k: [self._recipe_to_dict(r) for r in v] for k, v in recipes_by_category.items()}
                }
        
        # Default response for unhandled crafting actions
        return {
            "success": False,
            "message": f"The crafting action '{action}' is recognized but not implemented yet.",
            "action": action
        }
    
    def _handle_gathering_command(self, player_id: str, action: str, 
                                match_groups: Dict[str, str], 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle material gathering commands.
        
        Args:
            player_id: The ID of the player issuing the command
            action: The matched action type
            match_groups: Dictionary of matched pattern groups
            context: Context information
            
        Returns:
            A dictionary with the processing results
        """
        if action == "gather_material":
            material_name = match_groups.get("material_name", "").strip()
            source = match_groups.get("source", "").strip()
            
            # Get current region from context
            current_region = context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure where you are. Please specify a location.",
                    "action": action,
                    "material_name": material_name
                }
            
            # Check if the material is available in this region
            available_materials = self.crafting_integration.get_region_available_materials(current_region)
            
            # Find materials that match the name
            matching_materials = []
            for material in available_materials:
                if material_name.lower() in material["name"].lower():
                    matching_materials.append(material)
            
            if not matching_materials:
                return {
                    "success": False,
                    "message": f"You can't find any {material_name} in this area.",
                    "action": action,
                    "material_name": material_name,
                    "region": current_region
                }
            
            # Check if the source is appropriate for the material
            if source:
                valid_source = False
                for material in matching_materials:
                    for tag in material.get("source_tags", []):
                        if source.lower() in tag.lower():
                            valid_source = True
                            break
                    if valid_source:
                        break
                
                if not valid_source:
                    return {
                        "success": False,
                        "message": f"You can't gather {material_name} from {source} in this area.",
                        "action": action,
                        "material_name": material_name,
                        "source": source,
                        "region": current_region
                    }
            
            # Determine best matching material
            best_match = matching_materials[0]
            
            # Simulate gathering success/failure
            # In a real implementation, this would check player skills, tools, etc.
            success_chance = 0.7  # 70% base chance
            
            # Adjust for material rarity
            rarity_modifiers = {
                "COMMON": 0.2,
                "UNCOMMON": 0.0,
                "RARE": -0.2,
                "EPIC": -0.4,
                "LEGENDARY": -0.6
            }
            
            success_chance += rarity_modifiers.get(best_match["rarity"], 0.0)
            
            # Random success check
            import random
            success = random.random() < success_chance
            
            if success:
                # Determine quantity gathered
                base_quantity = 1
                if best_match["rarity"] == "COMMON":
                    base_quantity = random.randint(1, 3)
                
                # Add to player inventory
                # In a real implementation, this would use the inventory system
                
                return {
                    "success": True,
                    "message": f"You successfully gathered {base_quantity} {best_match['name']}.",
                    "action": action,
                    "material_name": best_match["name"],
                    "quantity": base_quantity,
                    "material_data": best_match
                }
            else:
                return {
                    "success": False,
                    "message": f"You search for {material_name} but fail to find any. Perhaps try a different location or approach.",
                    "action": action,
                    "material_name": material_name
                }
        
        elif action == "search_for_material":
            material_name = match_groups.get("material_name", "").strip()
            location = match_groups.get("location", "").strip()
            
            # Get current region from context or use specified location
            current_region = location if location else context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure where you are. Please specify a location.",
                    "action": action,
                    "material_name": material_name
                }
            
            # Get materials available in this region
            region_materials = self.crafting_integration.generate_region_material_availability(current_region)
            
            # Flatten the materials list
            all_materials = []
            for rarity, materials in region_materials.items():
                if rarity != "illicit":  # Don't show illicit materials in normal search
                    all_materials.extend(materials)
            
            # Find materials that match the name
            matching_materials = []
            for material in all_materials:
                if material_name.lower() in material["name"].lower():
                    matching_materials.append(material)
            
            if not matching_materials:
                return {
                    "success": False,
                    "message": f"You don't find any {material_name} in this area.",
                    "action": action,
                    "material_name": material_name,
                    "region": current_region
                }
            
            # Format the response
            if len(matching_materials) == 1:
                material = matching_materials[0]
                return {
                    "success": True,
                    "message": f"You find that {material['name']} can be found in this area. You might be able to gather some.",
                    "action": action,
                    "material_name": material_name,
                    "matching_materials": matching_materials
                }
            else:
                message = f"You find several types of {material_name} in this area:\n\n"
                for material in matching_materials:
                    message += f"• {material['name']}\n"
                
                return {
                    "success": True,
                    "message": message,
                    "action": action,
                    "material_name": material_name,
                    "matching_materials": matching_materials
                }
        
        # Default response for unhandled gathering actions
        return {
            "success": False,
            "message": f"The gathering action '{action}' is recognized but not implemented yet.",
            "action": action
        }
    
    def _handle_trading_command(self, player_id: str, action: str, 
                              match_groups: Dict[str, str], 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle trading-related commands.
        
        Args:
            player_id: The ID of the player issuing the command
            action: The matched action type
            match_groups: Dictionary of matched pattern groups
            context: Context information
            
        Returns:
            A dictionary with the processing results
        """
        if action == "sell_item":
            item_name = match_groups.get("item_name", "").strip()
            quantity_str = match_groups.get("quantity", "1").strip()
            npc_name = match_groups.get("npc_name", "").strip()
            price_str = match_groups.get("price", "").strip()
            
            # Parse quantity
            try:
                quantity = int(quantity_str) if quantity_str else 1
            except ValueError:
                quantity = 1
            
            # Parse price if specified
            price = None
            if price_str:
                try:
                    price = float(price_str)
                except ValueError:
                    pass
            
            # Check if trading with specific NPC or general market
            if npc_name:
                # Get NPC ID from context
                npc_id = None
                for npc in context.get("npcs_present", []):
                    if npc_name.lower() in npc.get("name", "").lower():
                        npc_id = npc.get("id")
                        break
                
                if not npc_id:
                    return {
                        "success": False,
                        "message": f"There's no one named {npc_name} here to trade with.",
                        "action": action,
                        "item_name": item_name,
                        "npc_name": npc_name
                    }
                
                # Check if NPC is interested in the item
                if "ai_gm_brain" in context and npc_id:
                    # Use AI GM to determine NPC response
                    ai_gm = context["ai_gm_brain"]
                    crafting_behavior = CraftingNPCBehavior(ai_gm)
                    
                    npc_response = crafting_behavior.get_npc_crafting_response(
                        npc_id=npc_id,
                        player_request=f"I want to sell you {quantity} {item_name}",
                        player_id=player_id
                    )
                    
                    if npc_response.get("interested", False):
                        # NPC wants to buy
                        price_per_unit = npc_response.get("price_per_unit", 0)
                        total_price = price_per_unit * quantity
                        
                        # Complete the transaction
                        # In a real implementation, this would involve the inventory and currency systems
                        
                        return {
                            "success": True,
                            "message": f"You sell {quantity} {item_name} to {npc_name} for {total_price} gold.",
                            "action": action,
                            "item_name": item_name,
                            "quantity": quantity,
                            "npc_name": npc_name,
                            "total_price": total_price,
                            "price_per_unit": price_per_unit
                        }
                    else:
                        # NPC not interested
                        return {
                            "success": False,
                            "message": npc_response.get("response", f"{npc_name} is not interested in buying {item_name}."),
                            "action": action,
                            "item_name": item_name,
                            "npc_name": npc_name,
                            "npc_response": npc_response
                        }
                else:
                    # No AI GM available, use simple logic
                    # Check if player has the item
                    has_item = self._check_player_has_item(player_id, item_name, quantity)
                    
                    if not has_item:
                        return {
                            "success": False,
                            "message": f"You don't have {quantity} {item_name} to sell.",
                            "action": action,
                            "item_name": item_name,
                            "quantity": quantity
                        }
                    
                    # Simple price calculation
                    price_per_unit = 10  # Default price
                    total_price = price_per_unit * quantity
                    
                    # Complete the transaction
                    # In a real implementation, this would involve the inventory and currency systems
                    
                    return {
                        "success": True,
                        "message": f"You sell {quantity} {item_name} to {npc_name} for {total_price} gold.",
                        "action": action,
                        "item_name": item_name,
                        "quantity": quantity,
                        "npc_name": npc_name,
                        "total_price": total_price,
                        "price_per_unit": price_per_unit
                    }
            else:
                # Selling to general market
                # Check if in a market location
                is_market = context.get("is_market", False)
                
                if not is_market:
                    return {
                        "success": False,
                        "message": "You need to be at a market or shop to sell items.",
                        "action": action,
                        "item_name": item_name
                    }
                
                # Check if player has the item
                has_item = self._check_player_has_item(player_id, item_name, quantity)
                
                if not has_item:
                    return {
                        "success": False,
                        "message": f"You don't have {quantity} {item_name} to sell.",
                        "action": action,
                        "item_name": item_name,
                        "quantity": quantity
                    }
                
                # Get market price for the item
                market_price = self.economy_service.get_item_market_price(item_name, context.get("current_region", ""))
                
                if not market_price:
                    return {
                        "success": False,
                        "message": f"There doesn't seem to be a market for {item_name} here.",
                        "action": action,
                        "item_name": item_name
                    }
                
                total_price = market_price * quantity
                
                # Complete the transaction
                # In a real implementation, this would involve the inventory and currency systems
                
                return {
                    "success": True,
                    "message": f"You sell {quantity} {item_name} at the market for {total_price} gold.",
                    "action": action,
                    "item_name": item_name,
                    "quantity": quantity,
                    "total_price": total_price,
                    "price_per_unit": market_price
                }
        
        elif action == "buy_item":
            item_name = match_groups.get("item_name", "").strip()
            quantity_str = match_groups.get("quantity", "1").strip()
            npc_name = match_groups.get("npc_name", "").strip()
            
            # Parse quantity
            try:
                quantity = int(quantity_str) if quantity_str else 1
            except ValueError:
                quantity = 1
            
            # Check if buying from specific NPC or general market
            if npc_name:
                # Similar logic to sell_item but for buying
                # Get NPC ID from context
                npc_id = None
                for npc in context.get("npcs_present", []):
                    if npc_name.lower() in npc.get("name", "").lower():
                        npc_id = npc.get("id")
                        break
                
                if not npc_id:
                    return {
                        "success": False,
                        "message": f"There's no one named {npc_name} here to buy from.",
                        "action": action,
                        "item_name": item_name,
                        "npc_name": npc_name
                    }
                
                # Check if NPC has the item
                if "ai_gm_brain" in context and npc_id:
                    # Use AI GM to determine NPC response
                    ai_gm = context["ai_gm_brain"]
                    crafting_behavior = CraftingNPCBehavior(ai_gm)
                    
                    npc_response = crafting_behavior.get_npc_crafting_response(
                        npc_id=npc_id,
                        player_request=f"Do you have {item_name} for sale?",
                        player_id=player_id
                    )
                    
                    if npc_response.get("has_material", False):
                        # NPC has the item
                        price_per_unit = npc_response.get("price_per_unit", 0)
                        available_quantity = npc_response.get("available_quantity", 0)
                        
                        if available_quantity < quantity:
                            return {
                                "success": False,
                                "message": f"{npc_name} only has {available_quantity} {item_name} available.",
                                "action": action,
                                "item_name": item_name,
                                "quantity": quantity,
                                "available_quantity": available_quantity,
                                "npc_name": npc_name
                            }
                        
                        total_price = price_per_unit * quantity
                        
                        # Check if player has enough money
                        player_money = self._get_player_money(player_id)
                        
                        if player_money < total_price:
                            return {
                                "success": False,
                                "message": f"You don't have enough money to buy {quantity} {item_name}. It costs {total_price} gold but you only have {player_money} gold.",
                                "action": action,
                                "item_name": item_name,
                                "quantity": quantity,
                                "total_price": total_price,
                                "player_money": player_money
                            }
                        
                        # Complete the transaction
                        # In a real implementation, this would involve the inventory and currency systems
                        
                        return {
                            "success": True,
                            "message": f"You buy {quantity} {item_name} from {npc_name} for {total_price} gold.",
                            "action": action,
                            "item_name": item_name,
                            "quantity": quantity,
                            "npc_name": npc_name,
                            "total_price": total_price,
                            "price_per_unit": price_per_unit
                        }
                    else:
                        # NPC doesn't have the item
                        return {
                            "success": False,
                            "message": npc_response.get("response", f"{npc_name} doesn't have {item_name} for sale."),
                            "action": action,
                            "item_name": item_name,
                            "npc_name": npc_name,
                            "npc_response": npc_response
                        }
                else:
                    # No AI GM available, use simple logic
                    return {
                        "success": False,
                        "message": f"Unable to determine if {npc_name} has {item_name} for sale.",
                        "action": action,
                        "item_name": item_name,
                        "npc_name": npc_name
                    }
            else:
                # Buying from general market
                # Similar logic to selling to general market
                is_market = context.get("is_market", False)
                
                if not is_market:
                    return {
                        "success": False,
                        "message": "You need to be at a market or shop to buy items.",
                        "action": action,
                        "item_name": item_name
                    }
                
                # Get market price for the item
                market_price = self.economy_service.get_item_market_price(item_name, context.get("current_region", ""))
                
                if not market_price:
                    return {
                        "success": False,
                        "message": f"There doesn't seem to be {item_name} available in this market.",
                        "action": action,
                        "item_name": item_name
                    }
                
                total_price = market_price * quantity
                
                # Check if player has enough money
                player_money = self._get_player_money(player_id)
                
                if player_money < total_price:
                    return {
                        "success": False,
                        "message": f"You don't have enough money to buy {quantity} {item_name}. It costs {total_price} gold but you only have {player_money} gold.",
                        "action": action,
                        "item_name": item_name,
                        "quantity": quantity,
                        "total_price": total_price,
                        "player_money": player_money
                    }
                
                # Complete the transaction
                # In a real implementation, this would involve the inventory and currency systems
                
                return {
                    "success": True,
                    "message": f"You buy {quantity} {item_name} at the market for {total_price} gold.",
                    "action": action,
                    "item_name": item_name,
                    "quantity": quantity,
                    "total_price": total_price,
                    "price_per_unit": market_price
                }
        
        elif action == "check_price":
            item_name = match_groups.get("item_name", "").strip()
            
            # Get current region from context
            current_region = context.get("current_region", "")
            
            # Get market price for the item
            market_price = self.economy_service.get_item_market_price(item_name, current_region)
            
            if not market_price:
                return {
                    "success": False,
                    "message": f"You couldn't find any price information for {item_name} in this area.",
                    "action": action,
                    "item_name": item_name
                }
            
            return {
                "success": True,
                "message": f"The current market price for {item_name} is {market_price} gold per unit.",
                "action": action,
                "item_name": item_name,
                "price": market_price,
                "region": current_region
            }
        
        # Default response for unhandled trading actions
        return {
            "success": False,
            "message": f"The trading action '{action}' is recognized but not implemented yet.",
            "action": action
        }
    
    def _handle_business_command(self, player_id: str, action: str, 
                               match_groups: Dict[str, str], 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle business-related commands.
        
        Args:
            player_id: The ID of the player issuing the command
            action: The matched action type
            match_groups: Dictionary of matched pattern groups
            context: Context information
            
        Returns:
            A dictionary with the processing results
        """
        if action == "start_business":
            business_type = match_groups.get("business_type", "").strip()
            location = match_groups.get("location", "").strip()
            
            # Get current region from context or use specified location
            current_region = location if location else context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure where you want to start your business. Please specify a location.",
                    "action": action,
                    "business_type": business_type
                }
            
            # Check if player already has a business of this type
            player_businesses = self.business_api.get_player_businesses(player_id)
            
            for business in player_businesses:
                if business_type.lower() in business.get("type", "").lower():
                    return {
                        "success": False,
                        "message": f"You already own a {business['type']} business in {business['location']}.",
                        "action": action,
                        "business_type": business_type,
                        "existing_business": business
                    }
            
            # Check if player has enough money to start a business
            startup_cost = self.business_api.get_business_startup_cost(business_type, current_region)
            player_money = self._get_player_money(player_id)
            
            if player_money < startup_cost:
                return {
                    "success": False,
                    "message": f"You don't have enough money to start a {business_type} business. It costs {startup_cost} gold but you only have {player_money} gold.",
                    "action": action,
                    "business_type": business_type,
                    "startup_cost": startup_cost,
                    "player_money": player_money
                }
            
            # Check if player has necessary skills
            required_skills = self.business_api.get_business_required_skills(business_type)
            missing_skills = []
            
            for skill in required_skills:
                player_skill_level = self._get_player_skill_level(player_id, skill["name"])
                if player_skill_level < skill["level"]:
                    missing_skills.append({
                        "name": skill["name"],
                        "required_level": skill["level"],
                        "current_level": player_skill_level
                    })
            
            if missing_skills:
                missing_str = ", ".join([f"{skill['name']} (level {skill['required_level']} required, you have {skill['current_level']})" for skill in missing_skills])
                
                return {
                    "success": False,
                    "message": f"You lack the skills to run a {business_type} business. You need: {missing_str}",
                    "action": action,
                    "business_type": business_type,
                    "missing_skills": missing_skills
                }
            
            # All checks passed, start the business
            business_result = self.business_api.start_player_business(
                player_id=player_id,
                business_type=business_type,
                location=current_region,
                initial_investment=startup_cost
            )
            
            if business_result.get("success", False):
                business = business_result.get("business", {})
                
                return {
                    "success": True,
                    "message": f"Congratulations! You've started a {business_type} business in {current_region}. Your initial investment was {startup_cost} gold.",
                    "action": action,
                    "business_type": business_type,
                    "location": current_region,
                    "business_id": business.get("id"),
                    "business_data": business
                }
            else:
                return {
                    "success": False,
                    "message": business_result.get("message", f"There was an error starting your {business_type} business."),
                    "action": action,
                    "business_type": business_type,
                    "error": business_result.get("error")
                }
        
        elif action == "manage_business":
            business_type = match_groups.get("business_type", "").strip()
            
            # Get player's businesses
            player_businesses = self.business_api.get_player_businesses(player_id)
            
            if not player_businesses:
                return {
                    "success": False,
                    "message": "You don't own any businesses to manage.",
                    "action": action,
                    "business_type": business_type
                }
            
            # Find matching business
            matching_businesses = []
            for business in player_businesses:
                if business_type.lower() in business.get("type", "").lower():
                    matching_businesses.append(business)
            
            if not matching_businesses:
                business_list = ", ".join([b.get("type", "Unknown") for b in player_businesses])
                return {
                    "success": False,
                    "message": f"You don't own a {business_type} business. Your businesses: {business_list}",
                    "action": action,
                    "business_type": business_type,
                    "player_businesses": player_businesses
                }
            
            # If multiple matching businesses, use the most recent one
            business = matching_businesses[0]
            
            # Get business details
            business_details = self.business_api.get_business_details(business.get("id"))
            
            if not business_details.get("success", False):
                return {
                    "success": False,
                    "message": business_details.get("message", f"There was an error retrieving details for your {business_type} business."),
                    "action": action,
                    "business_type": business_type,
                    "error": business_details.get("error")
                }
            
            # Format business details for display
            details = business_details.get("details", {})
            
            message = f"--- {details.get('name', business_type.title())} Business in {details.get('location')} ---\n\n"
            message += f"Status: {details.get('status', 'Active')}\n"
            message += f"Reputation: {details.get('reputation', 0)}/100\n"
            message += f"Current Capital: {details.get('current_capital', 0)} gold\n\n"
            
            message += "Recent Transactions:\n"
            for transaction in details.get("recent_transactions", [])[:5]:
                message += f"• {transaction.get('description')}: {transaction.get('amount')} gold\n"
            
            message += "\nInventory:\n"
            for item in details.get("inventory", [])[:5]:
                message += f"• {item.get('quantity')} {item.get('name')}\n"
            
            if len(details.get("inventory", [])) > 5:
                message += f"• ... and {len(details.get('inventory', [])) - 5} more items\n"
            
            message += "\nEmployees:\n"
            for employee in details.get("employees", []):
                message += f"• {employee.get('name')} - {employee.get('role')} (Salary: {employee.get('salary')} gold/day)\n"
            
            if not details.get("employees"):
                message += "• No employees yet\n"
            
            message += "\nWhat would you like to do with your business?"
            
            return {
                "success": True,
                "message": message,
                "action": action,
                "business_type": business_type,
                "business_id": business.get("id"),
                "business_details": details
            }
        
        elif action == "hire_employee":
            npc_type = match_groups.get("npc_type", "").strip()
            business_type = match_groups.get("business_type", "").strip()
            
            # If business type not specified, get player's businesses
            if not business_type:
                player_businesses = self.business_api.get_player_businesses(player_id)
                
                if not player_businesses:
                    return {
                        "success": False,
                        "message": "You don't own any businesses to hire employees for.",
                        "action": action,
                        "npc_type": npc_type
                    }
                
                # Use the first business
                business = player_businesses[0]
                business_type = business.get("type", "business")
                business_id = business.get("id")
            else:
                # Get player's businesses of the specified type
                player_businesses = self.business_api.get_player_businesses(player_id)
                
                matching_businesses = []
                for business in player_businesses:
                    if business_type.lower() in business.get("type", "").lower():
                        matching_businesses.append(business)
                
                if not matching_businesses:
                    business_list = ", ".join([b.get("type", "Unknown") for b in player_businesses])
                    return {
                        "success": False,
                        "message": f"You don't own a {business_type} business. Your businesses: {business_list}",
                        "action": action,
                        "npc_type": npc_type,
                        "business_type": business_type
                    }
                
                # Use the first matching business
                business = matching_businesses[0]
                business_id = business.get("id")
            
            # Check if there are suitable NPCs present
            suitable_npcs = []
            for npc in context.get("npcs_present", []):
                if npc_type.lower() in npc.get("profession", "").lower() or npc_type.lower() in npc.get("type", "").lower():
                    suitable_npcs.append(npc)
            
            if not suitable_npcs:
                return {
                    "success": False,
                    "message": f"There are no {npc_type}s here that you could hire.",
                    "action": action,
                    "npc_type": npc_type,
                    "business_type": business_type
                }
            
            # Get the first suitable NPC
            npc = suitable_npcs[0]
            npc_id = npc.get("id")
            npc_name = npc.get("name")
            
            # Check if NPC is already employed
            business_employees = self.business_api.get_business_employees(business_id)
            
            for employee in business_employees:
                if employee.get("npc_id") == npc_id:
                    return {
                        "success": False,
                        "message": f"{npc_name} is already employed at your {business_type} business.",
                        "action": action,
                        "npc_type": npc_type,
                        "business_type": business_type,
                        "npc_id": npc_id,
                        "npc_name": npc_name
                    }
            
            # Determine salary
            salary = 10  # Default daily salary
            
            # Ask NPC if they're interested (if AI GM is available)
            if "ai_gm_brain" in context and npc_id:
                # Use AI GM to determine NPC response
                ai_gm = context["ai_gm_brain"]
                
                # Logic for NPC response would go here
                # For now, assume NPCs are always interested
                interested = True
                negotiated_salary = salary
            else:
                # No AI GM available, assume NPC is interested
                interested = True
                negotiated_salary = salary
            
            if not interested:
                return {
                    "success": False,
                    "message": f"{npc_name} is not interested in working at your {business_type} business.",
                    "action": action,
                    "npc_type": npc_type,
                    "business_type": business_type,
                    "npc_id": npc_id,
                    "npc_name": npc_name
                }
            
            # Check if business has enough capital for the salary
            business_details = self.business_api.get_business_details(business_id)
            current_capital = business_details.get("details", {}).get("current_capital", 0)
            
            if current_capital < negotiated_salary * 7:  # One week's salary
                return {
                    "success": False,
                    "message": f"Your business doesn't have enough capital to pay {npc_name}'s salary. You need at least {negotiated_salary * 7} gold (one week's salary), but you only have {current_capital} gold.",
                    "action": action,
                    "npc_type": npc_type,
                    "business_type": business_type,
                    "npc_id": npc_id,
                    "npc_name": npc_name,
                    "negotiated_salary": negotiated_salary,
                    "current_capital": current_capital
                }
            
            # Hire the NPC
            hire_result = self.business_api.hire_business_employee(
                business_id=business_id,
                npc_id=npc_id,
                role=npc_type,
                salary=negotiated_salary
            )
            
            if hire_result.get("success", False):
                return {
                    "success": True,
                    "message": f"You've hired {npc_name} as a {npc_type} at your {business_type} business for {negotiated_salary} gold per day.",
                    "action": action,
                    "npc_type": npc_type,
                    "business_type": business_type,
                    "npc_id": npc_id,
                    "npc_name": npc_name,
                    "salary": negotiated_salary,
                    "employee_data": hire_result.get("employee", {})
                }
            else:
                return {
                    "success": False,
                    "message": hire_result.get("message", f"There was an error hiring {npc_name} for your {business_type} business."),
                    "action": action,
                    "npc_type": npc_type,
                    "business_type": business_type,
                    "error": hire_result.get("error")
                }
        
        # Default response for unhandled business actions
        return {
            "success": False,
            "message": f"The business action '{action}' is recognized but not implemented yet.",
            "action": action
        }
    
    def _handle_black_market_command(self, player_id: str, action: str, 
                                   match_groups: Dict[str, str], 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle black market-related commands.
        
        Args:
            player_id: The ID of the player issuing the command
            action: The matched action type
            match_groups: Dictionary of matched pattern groups
            context: Context information
            
        Returns:
            A dictionary with the processing results
        """
        if action == "find_black_market":
            location = match_groups.get("location", "").strip()
            
            # Get current region from context or use specified location
            current_region = location if location else context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure where you are. Please specify a location.",
                    "action": action
                }
            
            # Check if black market exists in this region
            black_market_exists = self.black_market_api.check_black_market_exists(current_region)
            
            if not black_market_exists:
                return {
                    "success": False,
                    "message": f"You search for signs of a black market in {current_region}, but find nothing suspicious.",
                    "action": action,
                    "region": current_region
                }
            
            # Check player's criminal reputation
            criminal_rep = self._get_player_criminal_reputation(player_id)
            
            # Check heat level in the region
            heat_level = self.black_market_api.get_region_heat_level(current_region)
            
            # Determine success chance based on reputation and heat
            # Higher rep = easier to find, higher heat = harder to find
            base_chance = 0.5
            rep_modifier = min(0.4, criminal_rep * 0.04)  # Up to +0.4 for rep 10
            heat_modifier = -min(0.4, heat_level * 0.1)  # Up to -0.4 for heat 4
            
            success_chance = base_chance + rep_modifier + heat_modifier
            
            # Random check
            import random
            success = random.random() < success_chance
            
            if success:
                # Get black market vendor info
                vendor_info = self.black_market_api.get_black_market_vendor(current_region)
                
                # Get available illicit goods
                illicit_goods = self.crafting_integration.get_illicit_materials_for_region(current_region)
                
                return {
                    "success": True,
                    "message": f"After asking around discreetly, you find a contact who can connect you with {vendor_info.get('name')}, a black market dealer in {current_region}.",
                    "action": action,
                    "region": current_region,
                    "vendor": vendor_info,
                    "illicit_goods": illicit_goods
                }
            else:
                # Failed to find black market
                # Check if player was detected by authorities
                detection_chance = min(0.5, heat_level * 0.15)  # Up to 0.5 for heat 3+
                detected = random.random() < detection_chance
                
                if detected:
                    # Increase heat level
                    self.black_market_api.increase_heat_level(current_region, 0.2)
                    
                    return {
                        "success": False,
                        "message": f"Your inquiries about illegal goods have attracted unwanted attention. A guard eyes you suspiciously as you walk away empty-handed.",
                        "action": action,
                        "region": current_region,
                        "detected": True,
                        "heat_increased": True
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Despite your efforts, you can't seem to find any black market contacts in {current_region}. Perhaps try a different approach or location.",
                        "action": action,
                        "region": current_region,
                        "detected": False
                    }
        
        elif action == "smuggle_items":
            item_name = match_groups.get("item_name", "").strip()
            destination = match_groups.get("destination", "").strip()
            
            # Get current region from context
            current_region = context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure where you are. Please specify your current location.",
                    "action": action,
                    "item_name": item_name
                }
            
            # If destination not specified, ask for it
            if not destination:
                return {
                    "success": False,
                    "message": f"Where do you want to smuggle {item_name} to? Please specify a destination.",
                    "action": action,
                    "item_name": item_name,
                    "current_region": current_region
                }
            
            # Check if item is actually illicit in the destination
            illicit_check = self.black_market_api.check_item_illicit(item_name, destination)
            
            if not illicit_check:
                return {
                    "success": False,
                    "message": f"{item_name} is not considered illicit in {destination}. You can transport it legally.",
                    "action": action,
                    "item_name": item_name,
                    "destination": destination
                }
            
            # Check if player has the item
            has_item = self._check_player_has_item(player_id, item_name, 1)
            
            if not has_item:
                return {
                    "success": False,
                    "message": f"You don't have any {item_name} to smuggle.",
                    "action": action,
                    "item_name": item_name
                }
            
            # Start a smuggling operation
            smuggling_result = self.black_market_api.start_smuggling_operation(
                player_id=player_id,
                item_name=item_name,
                quantity=1,
                origin=current_region,
                destination=destination
            )
            
            if smuggling_result.get("success", False):
                operation = smuggling_result.get("operation", {})
                
                return {
                    "success": True,
                    "message": f"You've arranged to smuggle {item_name} from {current_region} to {destination}. The operation will take {operation.get('estimated_time_hours', 24)} hours and has a {operation.get('success_chance', 50)}% chance of success.",
                    "action": action,
                    "item_name": item_name,
                    "destination": destination,
                    "operation_id": operation.get("id"),
                    "operation_data": operation
                }
            else:
                return {
                    "success": False,
                    "message": smuggling_result.get("message", f"There was an error starting a smuggling operation for {item_name}."),
                    "action": action,
                    "item_name": item_name,
                    "error": smuggling_result.get("error")
                }
        
        # Default response for unhandled black market actions
        return {
            "success": False,
            "message": f"The black market action '{action}' is recognized but not implemented yet.",
            "action": action
        }
    
    def _handle_information_command(self, player_id: str, action: str, 
                                  match_groups: Dict[str, str], 
                                  context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle information-related commands.
        
        Args:
            player_id: The ID of the player issuing the command
            action: The matched action type
            match_groups: Dictionary of matched pattern groups
            context: Context information
            
        Returns:
            A dictionary with the processing results
        """
        if action == "check_economy":
            location = match_groups.get("location", "").strip()
            
            # Get current region from context or use specified location
            current_region = location if location else context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure which economy you want to check. Please specify a location.",
                    "action": action
                }
            
            # Get economic information for the region
            economy_info = self.economy_service.get_region_economy_info(current_region)
            
            if not economy_info:
                return {
                    "success": False,
                    "message": f"I couldn't find economic information for {current_region}.",
                    "action": action,
                    "region": current_region
                }
            
            # Format the response
            message = f"--- Economic Conditions in {current_region} ---\n\n"
            message += f"Economy Strength: {economy_info.get('strength', 5)}/10\n"
            message += f"Primary Resources: {', '.join(economy_info.get('primary_resources', ['Unknown']))}\n"
            message += f"Currency Value: {economy_info.get('currency_value', 1.0)} (relative to standard)\n\n"
            
            message += "Current Market Trends:\n"
            for trend in economy_info.get("market_trends", []):
                message += f"• {trend.get('description')}\n"
            
            message += "\nHigh-Demand Items:\n"
            for item in economy_info.get("high_demand_items", [])[:5]:
                message += f"• {item.get('name')} (Price multiplier: {item.get('price_multiplier', 1.0)})\n"
            
            message += "\nLow-Value Items:\n"
            for item in economy_info.get("low_value_items", [])[:5]:
                message += f"• {item.get('name')} (Price multiplier: {item.get('price_multiplier', 1.0)})\n"
            
            return {
                "success": True,
                "message": message,
                "action": action,
                "region": current_region,
                "economy_info": economy_info
            }
        
        elif action == "list_regional_materials":
            location = match_groups.get("location", "").strip()
            
            # Get current region from context or use specified location
            current_region = location if location else context.get("current_region", "")
            
            if not current_region:
                return {
                    "success": False,
                    "message": "I'm not sure which region's materials you want to check. Please specify a location.",
                    "action": action
                }
            
            # Get materials available in this region
            materials = self.crafting_integration.generate_region_material_availability(current_region)
            
            if not materials:
                return {
                    "success": False,
                    "message": f"I couldn't find information about materials in {current_region}.",
                    "action": action,
                    "region": current_region
                }
            
            # Format the response
            message = f"--- Materials Found in {current_region} ---\n\n"
            
            for rarity, materials_list in materials.items():
                if rarity != "illicit" and materials_list:
                    message += f"{rarity.capitalize()} Materials:\n"
                    for material in materials_list[:5]:
                        message += f"• {material.get('name')}\n"
                    
                    if len(materials_list) > 5:
                        message += f"• ... and {len(materials_list) - 5} more\n"
                    
                    message += "\n"
            
            # Only show illicit materials if player has criminal reputation
            criminal_rep = self._get_player_criminal_reputation(player_id)
            
            if criminal_rep > 3 and materials.get("illicit"):
                message += "Restricted Materials (known to those with underworld connections):\n"
                for material in materials.get("illicit", [])[:3]:
                    message += f"• {material.get('name')}\n"
                
                if len(materials.get("illicit", [])) > 3:
                    message += f"• ... and {len(materials.get('illicit', [])) - 3} more\n"
            
            return {
                "success": True,
                "message": message,
                "action": action,
                "region": current_region,
                "materials": materials
            }
        
        # Default response for unhandled information actions
        return {
            "success": False,
            "message": f"The information action '{action}' is recognized but not implemented yet.",
            "action": action
        }
    
    # Helper methods
    def _check_player_crafting_skills(self, player_id: str, required_skills: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Check if a player has the required skills for crafting.
        
        Args:
            player_id: The player's ID
            required_skills: List of skill requirements
            
        Returns:
            Dictionary with skill check results
        """
        has_skills = True
        missing_skills = []
        
        for skill_req in required_skills:
            skill_name = skill_req.get("skill_name", "")
            required_level = skill_req.get("level", 1)
            
            player_level = self._get_player_skill_level(player_id, skill_name)
            
            if player_level < required_level:
                has_skills = False
                missing_skills.append({
                    "skill_name": skill_name,
                    "level": required_level,
                    "player_level": player_level
                })
        
        return {
            "has_skills": has_skills,
            "missing_skills": missing_skills
        }
    
    def _check_player_has_materials(self, player_id: str, required_materials: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Check if a player has the required materials.
        
        Args:
            player_id: The player's ID
            required_materials: List of required materials
            
        Returns:
            Tuple of (has_all_materials, list_of_missing_materials)
        """
        has_all = True
        missing_materials = []
        
        # In a real implementation, this would check the player's inventory
        # For now, just assume the player has all materials
        
        return has_all, missing_materials
    
    def _check_player_has_crafting_station(self, player_id: str, required_station: str, context: Dict[str, Any]) -> bool:
        """
        Check if a player has access to the required crafting station.
        
        Args:
            player_id: The player's ID
            required_station: The required crafting station type
            context: Context information
            
        Returns:
            True if the player has access to the station, False otherwise
        """
        # Check if location has the station
        location_stations = context.get("available_crafting_stations", [])
        
        if required_station in location_stations:
            return True
        
        # Check if player owns a portable version of the station
        # In a real implementation, this would check the player's inventory
        
        # For now, assume player doesn't have portable stations
        return False
    
    def _check_player_has_item(self, player_id: str, item_name: str, quantity: int) -> bool:
        """
        Check if a player has a specific item in the required quantity.
        
        Args:
            player_id: The player's ID
            item_name: The name of the item
            quantity: The required quantity
            
        Returns:
            True if the player has the item, False otherwise
        """
        # In a real implementation, this would check the player's inventory
        # For now, just assume the player has the item
        return True
    
    def _get_player_skill_level(self, player_id: str, skill_name: str) -> int:
        """
        Get a player's skill level for a specific skill.
        
        Args:
            player_id: The player's ID
            skill_name: The name of the skill
            
        Returns:
            The player's skill level
        """
        # In a real implementation, this would query the player's skills
        # For now, just return a default level of 1
        return 1
    
    def _get_player_money(self, player_id: str) -> float:
        """
        Get a player's current money.
        
        Args:
            player_id: The player's ID
            
        Returns:
            The player's current money
        """
        # In a real implementation, this would query the player's currency
        # For now, just return a default amount of 100
        return 100.0
    
    def _get_player_criminal_reputation(self, player_id: str) -> int:
        """
        Get a player's criminal reputation.
        
        Args:
            player_id: The player's ID
            
        Returns:
            The player's criminal reputation (0-10)
        """
        # In a real implementation, this would query the player's reputation
        # For now, just return a default value of 0
        return 0
    
    def _recipe_to_dict(self, recipe: Any) -> Dict[str, Any]:
        """
        Convert a recipe object to a dictionary.
        
        Args:
            recipe: The recipe object
            
        Returns:
            Dictionary representation of the recipe
        """
        return {
            "id": getattr(recipe, "id", None),
            "name": getattr(recipe, "name", "Unknown"),
            "description": getattr(recipe, "description", ""),
            "recipe_category": getattr(recipe, "recipe_category", ""),
            "difficulty_level": getattr(recipe, "difficulty_level", 1),
            "required_station_type": getattr(recipe, "required_station_type", None)
        }

# Factory function to create a ParserIntegrator
def create_parser_integrator() -> ParserIntegrator:
    """Create and return a new ParserIntegrator instance."""
    return ParserIntegrator()