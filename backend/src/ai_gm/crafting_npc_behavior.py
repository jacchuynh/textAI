"""
Crafting NPC Behavior Module

This module provides specialized behaviors for crafting NPCs within the AI GM Brain system.
It allows NPCs to craft items, trade materials, and operate businesses using the material
and recipe system.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple

from backend.src.ai_gm.ai_gm_brain_integrated import AIGMBrain
from backend.src.crafting.services.crafting_integration_service import create_crafting_integration_service

logger = logging.getLogger(__name__)

class CraftingNPCBehavior:
    """Specialized behaviors for crafting NPCs within the AI GM Brain system."""
    
    def __init__(self, ai_gm_brain: AIGMBrain):
        """
        Initialize the crafting NPC behavior module.
        
        Args:
            ai_gm_brain: The AI GM Brain instance to integrate with
        """
        self.ai_gm_brain = ai_gm_brain
        self.crafting_service = create_crafting_integration_service()
        
        # Initialize crafting-related properties in AI GM Brain knowledge base
        if "crafting" not in self.ai_gm_brain.knowledge_base:
            self.ai_gm_brain.knowledge_base["crafting"] = {
                "materials": {},
                "recipes": {},
                "npc_professions": {},
                "region_materials": {}
            }
        
        # Integrate crafting system with AI GM Brain
        self.crafting_service.integrate_with_ai_gm_brain(self.ai_gm_brain)
    
    def close(self):
        """Close the crafting service."""
        if self.crafting_service:
            self.crafting_service.close()
    
    def register_npc_profession(self, npc_id: str, profession: str, 
                               specialization: Optional[str] = None, 
                               skill_levels: Optional[Dict[str, int]] = None, 
                               wealth_level: int = 3) -> Dict[str, Any]:
        """
        Register an NPC as having a specific crafting profession.
        
        Args:
            npc_id: The NPC ID to register
            profession: The profession name (e.g., "Blacksmith", "Alchemist")
            specialization: Optional specialization within the profession
            skill_levels: Optional dictionary of skill levels for this NPC
            wealth_level: The wealth level of the NPC (1-5)
            
        Returns:
            A dictionary with the NPC's profession information
        """
        try:
            # Generate inventory based on profession
            inventory = self.crafting_service.generate_npc_inventory_for_profession(
                profession, wealth_level, specialization
            )
            
            # Set default skill levels if none provided
            if not skill_levels:
                skill_levels = {}
                
                # Set skills based on profession
                profession_skills = {
                    "Blacksmith": ["Blacksmithing", "Weaponsmithing", "Armorsmithing"],
                    "Weaponsmith": ["Blacksmithing", "Weaponsmithing"],
                    "Armorsmith": ["Blacksmithing", "Armorsmithing"],
                    "Alchemist": ["Alchemy", "Herbalism", "Poison Craft"],
                    "Herbalist": ["Herbalism", "Alchemy"],
                    "Woodworker": ["Woodworking", "Carpentry"],
                    "Carpenter": ["Carpentry", "Woodworking", "Furniture Making"],
                    "Tailor": ["Tailoring", "Weaving"],
                    "Leatherworker": ["Leatherworking", "Tanning"],
                    "Jeweler": ["Jewelcrafting", "Gemcutting", "Silversmithing"],
                    "Gemcutter": ["Gemcutting", "Jewelcrafting"],
                    "Relicsmith": ["Relicsmithing", "Containment Artifice"]
                }
                
                # Set skill levels based on profession
                base_skills = profession_skills.get(profession, [profession])
                for skill in base_skills:
                    skill_levels[skill] = random.randint(1, 3) + wealth_level
                    
                # Specialization gets higher skill
                if specialization:
                    skill_key = next((s for s in skill_levels.keys() if specialization.lower() in s.lower()), None)
                    if skill_key:
                        skill_levels[skill_key] = min(skill_levels[skill_key] + 2, 10)
            
            # Create profession information
            profession_info = {
                "profession": profession,
                "specialization": specialization,
                "skill_levels": skill_levels,
                "wealth_level": wealth_level,
                "inventory": inventory,
                "can_craft": True,
                "crafting_stations": self._get_crafting_stations_for_profession(profession, specialization)
            }
            
            # Store in AI GM Brain knowledge base
            if "npc_professions" not in self.ai_gm_brain.knowledge_base["crafting"]:
                self.ai_gm_brain.knowledge_base["crafting"]["npc_professions"] = {}
                
            self.ai_gm_brain.knowledge_base["crafting"]["npc_professions"][npc_id] = profession_info
            
            logger.info(f"Registered NPC {npc_id} as {profession} with specialization {specialization}")
            return profession_info
        except Exception as e:
            logger.error(f"Error registering NPC profession: {e}")
            return {"error": str(e)}
    
    def register_region_materials(self, region_id: str) -> Dict[str, Any]:
        """
        Register materials available in a specific region.
        
        Args:
            region_id: The region ID to register materials for
            
        Returns:
            A dictionary with the region's material availability information
        """
        try:
            # Generate material availability for the region
            availability = self.crafting_service.generate_region_material_availability(region_id)
            
            # Store in AI GM Brain knowledge base
            if "region_materials" not in self.ai_gm_brain.knowledge_base["crafting"]:
                self.ai_gm_brain.knowledge_base["crafting"]["region_materials"] = {}
                
            self.ai_gm_brain.knowledge_base["crafting"]["region_materials"][region_id] = availability
            
            logger.info(f"Registered materials for region {region_id}")
            return availability
        except Exception as e:
            logger.error(f"Error registering region materials: {e}")
            return {"error": str(e)}
    
    def get_npc_crafting_response(self, npc_id: str, 
                                 player_request: str, 
                                 player_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a response for a player interacting with a crafting NPC.
        
        Args:
            npc_id: The NPC ID to generate a response for
            player_request: The player's request to the NPC
            player_id: Optional player ID for contextual information
            
        Returns:
            A dictionary with the NPC's response information
        """
        try:
            # Get NPC profession information
            npc_profession = self.ai_gm_brain.knowledge_base["crafting"]["npc_professions"].get(npc_id)
            if not npc_profession:
                logger.warning(f"NPC {npc_id} is not registered as a crafting NPC")
                return {
                    "response": f"I'm not a craftsperson. I cannot help you with crafting.",
                    "can_help": False
                }
            
            # Categorize the player request
            request_category = self._categorize_player_request(player_request, npc_profession)
            
            # Generate response based on request category
            response = {}
            
            if request_category == "craft_item":
                # Extract item name from player request
                item_name = self._extract_item_name_from_request(player_request)
                response = self._handle_craft_item_request(npc_profession, item_name, player_id)
                
            elif request_category == "buy_material":
                # Extract material name from player request
                material_name = self._extract_material_name_from_request(player_request)
                response = self._handle_buy_material_request(npc_profession, material_name, player_id)
                
            elif request_category == "sell_material":
                # Extract material name from player request
                material_name = self._extract_material_name_from_request(player_request)
                response = self._handle_sell_material_request(npc_profession, material_name, player_id)
                
            elif request_category == "ask_profession":
                response = self._handle_ask_profession_request(npc_profession)
                
            elif request_category == "ask_available_items":
                response = self._handle_ask_available_items_request(npc_profession)
                
            else:  # general_conversation
                response = self._handle_general_conversation(npc_profession, player_request)
            
            return response
        except Exception as e:
            logger.error(f"Error generating NPC crafting response: {e}")
            return {
                "response": "I apologize, but I'm having trouble understanding your request. Could you try again?",
                "error": str(e)
            }
    
    def simulate_npc_crafting_activity(self, npc_id: str, region_id: str) -> Dict[str, Any]:
        """
        Simulate an NPC's crafting activity for ambient world detail.
        
        Args:
            npc_id: The NPC ID to simulate activity for
            region_id: The region ID where the NPC is located
            
        Returns:
            A dictionary with information about the NPC's crafting activity
        """
        try:
            # Get NPC profession information
            npc_profession = self.ai_gm_brain.knowledge_base["crafting"]["npc_professions"].get(npc_id)
            if not npc_profession:
                logger.warning(f"NPC {npc_id} is not registered as a crafting NPC")
                return {
                    "activity": "non_crafting",
                    "description": "The NPC is not engaged in any crafting activity."
                }
            
            # Determine crafting activity
            profession = npc_profession["profession"]
            specialization = npc_profession["specialization"]
            
            # Get craftable items for this NPC
            craftable_items = self.crafting_service.get_craftable_items_by_profession(
                profession if "-" not in profession else profession.split(" - ")[0]
            )
            
            if not craftable_items:
                return {
                    "activity": "idle",
                    "description": f"The {profession} is currently not working on anything specific."
                }
            
            # Select a random item to craft
            item = random.choice(craftable_items)
            
            # Generate activity description
            activities = {
                "Blacksmith": [
                    f"is hammering away at a hot piece of metal, crafting {item['recipe_name']}.",
                    f"is carefully shaping {item['recipe_name']} at the anvil, sweat dripping from their brow.",
                    f"is stoking the forge before beginning work on {item['recipe_name']}."
                ],
                "Weaponsmith": [
                    f"is honing the edge of {item['recipe_name']}, testing its sharpness periodically.",
                    f"is carefully attaching a handle to {item['recipe_name']}, ensuring it's secure.",
                    f"is examining the balance of {item['recipe_name']}, making minute adjustments."
                ],
                "Alchemist": [
                    f"is carefully measuring ingredients for {item['recipe_name']}.",
                    f"is grinding herbs in a mortar for {item['recipe_name']}, the aroma filling the air.",
                    f"is heating a bubbling concoction of {item['recipe_name']} over a small flame."
                ],
                "Woodworker": [
                    f"is carving intricate details into {item['recipe_name']}.",
                    f"is sanding {item['recipe_name']} to a smooth finish.",
                    f"is measuring and marking wood for {item['recipe_name']}."
                ],
                "Tailor": [
                    f"is stitching together pieces of fabric for {item['recipe_name']}.",
                    f"is cutting patterns for {item['recipe_name']} from a bolt of cloth.",
                    f"is fitting {item['recipe_name']} on a mannequin, adjusting it with pins."
                ],
                "Leatherworker": [
                    f"is stretching and cutting leather for {item['recipe_name']}.",
                    f"is punching holes into leather pieces for {item['recipe_name']}.",
                    f"is applying oil to finished {item['recipe_name']}, making it supple."
                ],
                "Jeweler": [
                    f"is setting a gemstone into {item['recipe_name']} with tiny tools.",
                    f"is polishing {item['recipe_name']} to a brilliant shine.",
                    f"is melting precious metal for {item['recipe_name']} in a small crucible."
                ],
                "Relicsmith": [
                    f"is inscribing arcane symbols onto {item['recipe_name']}.",
                    f"is carefully binding magical components into {item['recipe_name']}.",
                    f"is testing the resonance of {item['recipe_name']} with specialized tools."
                ]
            }
            
            profession_key = next((p for p in activities.keys() if p.lower() in profession.lower()), "Craftsperson")
            description = random.choice(activities.get(profession_key, [
                f"is working diligently on crafting {item['recipe_name']}.",
                f"is focused on creating {item['recipe_name']} with careful attention to detail.",
                f"is making progress on {item['recipe_name']}, occasionally stepping back to examine their work."
            ]))
            
            return {
                "activity": "crafting",
                "item_being_crafted": item['recipe_name'],
                "item_description": item['recipe_description'],
                "description": f"The {profession}{' specializing in ' + specialization if specialization else ''} {description}",
                "difficulty_level": item['difficulty_level'],
                "crafting_time_remaining": random.randint(1, item['crafting_time_seconds'])
            }
        except Exception as e:
            logger.error(f"Error simulating NPC crafting activity: {e}")
            return {
                "activity": "unknown",
                "description": "The craftsperson is busy with their work.",
                "error": str(e)
            }
    
    def _categorize_player_request(self, player_request: str, npc_profession: Dict[str, Any]) -> str:
        """
        Categorize the player's request to determine how to respond.
        
        Args:
            player_request: The player's request text
            npc_profession: The NPC's profession information
            
        Returns:
            The category of the player's request
        """
        player_request = player_request.lower()
        
        # Craft item request
        craft_keywords = ["craft", "make", "create", "forge", "smith", "brew", "sew", "tailor", "build"]
        if any(keyword in player_request for keyword in craft_keywords):
            return "craft_item"
        
        # Buy material request
        buy_keywords = ["buy", "purchase", "acquire", "get", "need", "looking for", "sell me", "have any"]
        if any(keyword in player_request for keyword in buy_keywords):
            return "buy_material"
        
        # Sell material request
        sell_keywords = ["sell", "trade", "offer", "exchange", "interested in"]
        if any(keyword in player_request for keyword in sell_keywords):
            return "sell_material"
        
        # Ask about profession
        profession_keywords = ["what do you do", "your profession", "your craft", "your trade", 
                             "what can you make", "what do you craft", "are you a"]
        if any(keyword in player_request for keyword in profession_keywords):
            return "ask_profession"
        
        # Ask about available items
        available_keywords = ["what do you have", "what's available", "show me", "inventory", 
                            "what can i buy", "what items", "wares", "goods", "merchandise"]
        if any(keyword in player_request for keyword in available_keywords):
            return "ask_available_items"
        
        # Default to general conversation
        return "general_conversation"
    
    def _extract_item_name_from_request(self, player_request: str) -> str:
        """
        Extract an item name from the player's request.
        
        Args:
            player_request: The player's request text
            
        Returns:
            The extracted item name or empty string if not found
        """
        # TODO: Implement more sophisticated NLP extraction if needed
        # For now, just extract words after craft-related keywords
        
        player_request = player_request.lower()
        
        craft_keywords = ["craft", "make", "create", "forge", "smith", "brew", "sew", "tailor", "build"]
        
        for keyword in craft_keywords:
            if keyword in player_request:
                # Extract text after the keyword
                after_keyword = player_request.split(keyword, 1)[1].strip()
                
                # Remove common articles and prepositions
                for word in ["a", "an", "the", "some", "me", "for me"]:
                    after_keyword = after_keyword.replace(f"{word} ", " ")
                
                return after_keyword.strip()
        
        return ""
    
    def _extract_material_name_from_request(self, player_request: str) -> str:
        """
        Extract a material name from the player's request.
        
        Args:
            player_request: The player's request text
            
        Returns:
            The extracted material name or empty string if not found
        """
        # TODO: Implement more sophisticated NLP extraction if needed
        # For now, just extract words after buy/sell-related keywords
        
        player_request = player_request.lower()
        
        buy_keywords = ["buy", "purchase", "acquire", "get", "need", "looking for", "sell me"]
        sell_keywords = ["sell", "trade", "offer", "exchange", "interested in"]
        
        all_keywords = buy_keywords + sell_keywords
        
        for keyword in all_keywords:
            if keyword in player_request:
                # Extract text after the keyword
                after_keyword = player_request.split(keyword, 1)[1].strip()
                
                # Remove common articles and prepositions
                for word in ["a", "an", "the", "some", "me", "to you", "from you"]:
                    after_keyword = after_keyword.replace(f"{word} ", " ")
                
                return after_keyword.strip()
        
        return ""
    
    def _handle_craft_item_request(self, npc_profession: Dict[str, Any], 
                                  item_name: str, 
                                  player_id: Optional[str]) -> Dict[str, Any]:
        """
        Handle a player's request to craft an item.
        
        Args:
            npc_profession: The NPC's profession information
            item_name: The name of the item to craft
            player_id: The player's ID
            
        Returns:
            A dictionary with the response information
        """
        profession = npc_profession["profession"]
        
        # Get craftable items for this NPC's profession
        craftable_items = self.crafting_service.get_craftable_items_by_profession(
            profession if "-" not in profession else profession.split(" - ")[0]
        )
        
        # Find the requested item
        matching_items = []
        for item in craftable_items:
            if item_name.lower() in item['recipe_name'].lower() or item_name.lower() in item['output_item']['name'].lower():
                matching_items.append(item)
        
        if not matching_items:
            return {
                "response": f"I'm sorry, but I don't know how to craft {item_name}. Perhaps you're looking for a different craftsperson?",
                "can_craft": False,
                "requested_item": item_name
            }
        
        # Get the best matching item
        best_match = matching_items[0]
        
        # Check if NPC has the skills to craft this item
        required_skills = best_match.get('required_skills', [])
        can_craft = True
        missing_skills = []
        
        for skill in required_skills:
            skill_level = npc_profession['skill_levels'].get(skill['skill_name'], 0)
            if skill_level < skill['level']:
                can_craft = False
                missing_skills.append(f"{skill['skill_name']} (needs level {skill['level']}, has {skill_level})")
        
        # Check if NPC has the required station
        has_station = best_match['required_station_type'] in npc_profession['crafting_stations']
        
        if not can_craft:
            return {
                "response": f"I'm afraid I don't have the skills to craft {best_match['recipe_name']}. I would need more experience in {', '.join(missing_skills)}.",
                "can_craft": False,
                "requested_item": best_match['recipe_name'],
                "missing_skills": missing_skills
            }
        
        if not has_station:
            return {
                "response": f"I know how to craft {best_match['recipe_name']}, but I don't have the necessary {best_match['required_station_type']}. Perhaps another craftsperson in town has one?",
                "can_craft": False,
                "requested_item": best_match['recipe_name'],
                "missing_station": best_match['required_station_type']
            }
        
        # Calculate price based on material values, difficulty, and NPC's markup
        base_price = best_match['output_item']['base_value']
        difficulty_modifier = 1.0 + (best_match['difficulty_level'] * 0.1)  # +10% per difficulty level
        markup = 1.0 + (0.1 * (6 - npc_profession['wealth_level']))  # Lower wealth = higher markup
        
        price = base_price * difficulty_modifier * markup
        
        # Round to appropriate value
        price = round(price * 100) / 100
        
        # Calculate crafting time
        crafting_time_hours = best_match['crafting_time_seconds'] / 3600
        crafting_time_formatted = f"{int(crafting_time_hours)} hours" if crafting_time_hours >= 1 else f"{int(best_match['crafting_time_seconds'] / 60)} minutes"
        
        return {
            "response": f"I can craft {best_match['recipe_name']} for you. It would cost {price} gold and take about {crafting_time_formatted} to complete. Would you like me to make it for you?",
            "can_craft": True,
            "requested_item": best_match['recipe_name'],
            "item_description": best_match['recipe_description'],
            "difficulty_level": best_match['difficulty_level'],
            "price": price,
            "crafting_time_seconds": best_match['crafting_time_seconds'],
            "crafting_time_formatted": crafting_time_formatted
        }
    
    def _handle_buy_material_request(self, npc_profession: Dict[str, Any], 
                                    material_name: str, 
                                    player_id: Optional[str]) -> Dict[str, Any]:
        """
        Handle a player's request to buy a material.
        
        Args:
            npc_profession: The NPC's profession information
            material_name: The name of the material to buy
            player_id: The player's ID
            
        Returns:
            A dictionary with the response information
        """
        # Check NPC's inventory for the requested material
        inventory = npc_profession.get('inventory', [])
        
        matching_items = []
        for item in inventory:
            if material_name.lower() in item['name'].lower():
                matching_items.append(item)
        
        if not matching_items:
            return {
                "response": f"I'm sorry, but I don't have any {material_name} available for sale at the moment. Perhaps check back later?",
                "has_material": False,
                "requested_material": material_name
            }
        
        # Get the best matching item
        best_match = matching_items[0]
        
        # Calculate price with slight markup
        markup = 1.2  # 20% markup
        price_per_unit = best_match['unit_value'] * markup
        
        # Round to appropriate value
        price_per_unit = round(price_per_unit * 100) / 100
        
        available_quantity = best_match['quantity']
        
        return {
            "response": f"Yes, I have {best_match['name']} available. I can sell it for {price_per_unit} gold per unit. I currently have {available_quantity} units in stock. How many would you like to purchase?",
            "has_material": True,
            "requested_material": best_match['name'],
            "material_description": best_match['description'],
            "available_quantity": available_quantity,
            "price_per_unit": price_per_unit,
            "total_value": best_match['total_value'],
            "material_type": best_match['material_type'],
            "rarity": best_match['rarity'],
            "is_raw_material": best_match['is_raw_material']
        }
    
    def _handle_sell_material_request(self, npc_profession: Dict[str, Any], 
                                     material_name: str, 
                                     player_id: Optional[str]) -> Dict[str, Any]:
        """
        Handle a player's request to sell a material to the NPC.
        
        Args:
            npc_profession: The NPC's profession information
            material_name: The name of the material to sell
            player_id: The player's ID
            
        Returns:
            A dictionary with the response information
        """
        profession = npc_profession["profession"]
        
        # Determine if this is a material the NPC would be interested in
        profession_material_types = {
            "Blacksmith": ["ORE", "METAL", "METAL_PRECIOUS"],
            "Weaponsmith": ["METAL", "WOOD_PROCESSED", "LEATHER"],
            "Armorsmith": ["METAL", "LEATHER", "CLOTH"],
            "Alchemist": ["HERB", "MINERAL", "ANIMAL_PART", "MAGICAL"],
            "Herbalist": ["HERB", "PLANT_FIBER"],
            "Woodworker": ["WOOD_RAW", "WOOD_PROCESSED", "WOOD_MAGICAL"],
            "Carpenter": ["WOOD_PROCESSED", "WOOD_RAW", "FASTENER_METAL", "FASTENER_WOOD"],
            "Tailor": ["CLOTH", "THREAD", "PLANT_FIBER", "LEATHER"],
            "Leatherworker": ["LEATHER", "HIDE", "EXOTIC_HIDE", "EXOTIC_LEATHER"],
            "Jeweler": ["GEM_RAW", "GEM", "METAL_PRECIOUS"],
            "Gemcutter": ["GEM_RAW", "GEM", "GEM_PROCESSED", "GEM_MAGICAL"],
            "Relicsmith": ["MAGICAL", "METAL", "GEM_MAGICAL"]
        }
        
        # Get profession key
        profession_key = next((p for p in profession_material_types.keys() if p.lower() in profession.lower()), None)
        
        if not profession_key:
            interested = random.choice([True, False])  # Random interest if profession not in list
        else:
            # Try to find the material in the database
            materials = []
            
            try:
                # Query materials that match the name
                db = self.crafting_service.db
                materials = db.query(self.crafting_service.models.DBMaterial).filter(
                    self.crafting_service.models.DBMaterial.name.ilike(f"%{material_name}%")
                ).all()
            except:
                pass
            
            interested = False
            if materials:
                # Check if any material type matches the profession's interests
                for material in materials:
                    if material.material_type in profession_material_types.get(profession_key, []):
                        interested = True
                        break
            else:
                # If material not found, guess based on name
                interested = any(t.lower() in material_name.lower() for t in ["ore", "metal", "gem", "leather", "cloth", "wood", "herb"])
        
        if not interested:
            return {
                "response": f"I'm sorry, but I'm not interested in purchasing {material_name}. Perhaps another merchant might be interested?",
                "interested": False,
                "requested_material": material_name
            }
        
        # Determine a reasonable buying price (lower than selling price)
        base_price = random.uniform(1.0, 10.0)  # Random price if not found in database
        if materials:
            base_price = materials[0].base_value
        
        # Calculate discount (NPC buys for less than they sell)
        discount = 0.7  # 30% discount when buying from players
        price_per_unit = base_price * discount
        
        # Round to appropriate value
        price_per_unit = round(price_per_unit * 100) / 100
        
        return {
            "response": f"I would be interested in purchasing {material_name}. I can offer you {price_per_unit} gold per unit. How many would you like to sell to me?",
            "interested": True,
            "requested_material": material_name,
            "price_per_unit": price_per_unit,
            "material_base_value": base_price,
            "needed_for_profession": True
        }
    
    def _handle_ask_profession_request(self, npc_profession: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a player asking about the NPC's profession.
        
        Args:
            npc_profession: The NPC's profession information
            
        Returns:
            A dictionary with the response information
        """
        profession = npc_profession["profession"]
        specialization = npc_profession["specialization"]
        
        # Craft station descriptions
        stations = ", ".join(npc_profession["crafting_stations"])
        
        # Get skill descriptions
        skills = []
        for skill_name, level in npc_profession["skill_levels"].items():
            # Convert numerical level to descriptive text
            level_text = {
                1: "a novice in",
                2: "beginning to learn",
                3: "familiar with",
                4: "skilled in",
                5: "very skilled in",
                6: "highly proficient in",
                7: "an expert in",
                8: "a master of",
                9: "a renowned master of",
                10: "legendary in"
            }.get(level, "skilled in")
            
            skills.append(f"{level_text} {skill_name}")
        
        skill_description = ", ".join(skills[:2])  # Just show top 2 skills
        
        # Craft description of what they can make
        profession_craft_descriptions = {
            "Blacksmith": "forge metal items like tools, weapons, and armor",
            "Weaponsmith": "craft finely balanced weapons of various types",
            "Armorsmith": "create protective armor for all manner of warriors",
            "Alchemist": "brew potions, elixirs, and magical concoctions",
            "Herbalist": "prepare herbal remedies and natural medicines",
            "Woodworker": "craft items from various types of wood",
            "Carpenter": "build furniture and wooden structures",
            "Tailor": "sew clothing and fabric goods of all kinds",
            "Leatherworker": "create leather goods from hides and skins",
            "Jeweler": "craft beautiful jewelry and precious adornments",
            "Gemcutter": "cut and polish gemstones to bring out their beauty",
            "Relicsmith": "forge magical artifacts and enchanted items"
        }
        
        craft_description = profession_craft_descriptions.get(
            profession, 
            f"craft various items as a {profession}"
        )
        
        response = f"I am a {profession}"
        if specialization:
            response += f" specializing in {specialization}"
        
        response += f". I {craft_description}. I'm {skill_description}."
        
        if stations:
            response += f" In my workshop, I have {stations} for my crafting work."
        
        return {
            "response": response,
            "profession": profession,
            "specialization": specialization,
            "crafting_stations": npc_profession["crafting_stations"],
            "top_skills": list(npc_profession["skill_levels"].items())[:3]
        }
    
    def _handle_ask_available_items_request(self, npc_profession: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a player asking about what items the NPC has available.
        
        Args:
            npc_profession: The NPC's profession information
            
        Returns:
            A dictionary with the response information
        """
        inventory = npc_profession.get('inventory', [])
        
        if not inventory:
            return {
                "response": "I'm afraid I don't have any items available at the moment. Perhaps check back later?",
                "has_inventory": False
            }
        
        # Group inventory by material type
        grouped_inventory = {}
        for item in inventory:
            material_type = item.get('material_type', 'Other')
            if material_type not in grouped_inventory:
                grouped_inventory[material_type] = []
            
            grouped_inventory[material_type].append(item)
        
        # Prepare readable inventory description
        inventory_descriptions = []
        for material_type, items in grouped_inventory.items():
            readable_type = material_type.replace('_', ' ').title()
            item_count = len(items)
            
            # List a few items from each category
            item_examples = [item['name'] for item in items[:3]]
            example_text = ", ".join(item_examples)
            
            if item_count > 3:
                example_text += f", and {item_count - 3} more"
            
            inventory_descriptions.append(f"{readable_type}: {example_text}")
        
        # Create full response
        response = "Here's what I currently have available:\n\n"
        response += "\n".join(inventory_descriptions)
        
        return {
            "response": response,
            "has_inventory": True,
            "grouped_inventory": grouped_inventory,
            "inventory_descriptions": inventory_descriptions
        }
    
    def _handle_general_conversation(self, npc_profession: Dict[str, Any], 
                                    player_request: str) -> Dict[str, Any]:
        """
        Handle general conversation with the NPC.
        
        Args:
            npc_profession: The NPC's profession information
            player_request: The player's request text
            
        Returns:
            A dictionary with the response information
        """
        profession = npc_profession["profession"]
        
        # Simple response templates
        responses = {
            "greeting": [
                f"Greetings! I'm a {profession}. How can I help you today?",
                f"Welcome to my workshop. I'm a {profession} by trade.",
                f"Hello there! Looking for a {profession}'s services?"
            ],
            "business": [
                f"Business has been steady. Always more work for a {profession} in these parts.",
                f"I've been keeping busy with my craft. A {profession}'s work is never done!",
                f"I can't complain about business. People always need a skilled {profession}."
            ],
            "farewell": [
                "Safe travels, friend. Return if you need my services.",
                "Farewell! Come back anytime.",
                "Until next time. May your path be clear."
            ],
            "default": [
                f"As a {profession}, I mainly focus on my craft. Was there something specific you wanted to know?",
                f"I'm afraid I don't have much to say about that. I'm just a simple {profession}.",
                f"Hmm, that's an interesting question. I'm not sure I can help with that as a {profession}."
            ]
        }
        
        # Determine response category
        category = "default"
        player_request_lower = player_request.lower()
        
        if any(word in player_request_lower for word in ["hello", "hi", "greetings", "good day"]):
            category = "greeting"
        elif any(word in player_request_lower for word in ["business", "trade", "how's work", "busy"]):
            category = "business"
        elif any(word in player_request_lower for word in ["goodbye", "farewell", "bye", "see you"]):
            category = "farewell"
        
        return {
            "response": random.choice(responses[category]),
            "category": category,
            "is_greeting": category == "greeting",
            "is_farewell": category == "farewell"
        }
    
    def _get_crafting_stations_for_profession(self, profession: str, 
                                             specialization: Optional[str] = None) -> List[str]:
        """
        Get the crafting stations typically associated with a profession.
        
        Args:
            profession: The profession name
            specialization: Optional specialization within the profession
            
        Returns:
            A list of crafting station types
        """
        profession_stations = {
            "Blacksmith": ["Forge", "Anvil", "Quenching Trough"],
            "Weaponsmith": ["Forge", "Anvil", "Grindstone", "Quenching Trough"],
            "Armorsmith": ["Forge", "Anvil", "Armorer's Bench"],
            "Alchemist": ["Alchemy Lab", "Distillery", "Herbalist's Table"],
            "Herbalist": ["Herbalist's Table", "Drying Rack", "Mortar and Pestle"],
            "Woodworker": ["Carpenter's Workbench", "Sawmill", "Lathe"],
            "Carpenter": ["Carpenter's Workbench", "Sawmill"],
            "Tailor": ["Tailor's Workbench", "Loom", "Spinning Wheel"],
            "Leatherworker": ["Leatherworking Table", "Tanning Rack", "Curing Station"],
            "Jeweler": ["Jeweler's Workbench", "Forge", "Polishing Wheel"],
            "Gemcutter": ["Jeweler's Workbench", "Gem Cutting Table", "Polishing Wheel"],
            "Relicsmith": ["Artificer's Workbench", "Runic Inscriber", "Forge"]
        }
        
        # Get base stations for profession
        stations = profession_stations.get(profession, ["Craftsperson's Workbench"])
        
        # Add specialization-specific stations if applicable
        if specialization:
            if "weapon" in specialization.lower():
                stations.extend(["Weapon Rack", "Testing Dummy"])
            elif "armor" in specialization.lower():
                stations.extend(["Armor Stand", "Fitting Form"])
            elif "gem" in specialization.lower():
                stations.extend(["Magnifying Apparatus", "Precision Cutting Tools"])
            elif "potion" in specialization.lower():
                stations.extend(["Cauldron", "Ingredient Storage"])
            elif "furniture" in specialization.lower():
                stations.extend(["Assembly Table", "Varnishing Station"])
        
        return list(set(stations))  # Remove duplicates