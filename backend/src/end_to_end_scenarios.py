"""
End-to-End Scenario Flow Module

This module implements a comprehensive end-to-end gameplay flow
that demonstrates how player actions propagate through the entire system.
"""

import uuid
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

# Import core systems
from backend.src.game_engine.magic_system import (
    MagicSystem, MagicUser, Spell, Domain, DamageType, EffectType, MagicTier
)
from backend.src.text_parser.text_parser import TextParser
from backend.src.ai_gm.ai_gm_brain_integrated import AIGMBrain


class EndToEndScenarioRunner:
    """
    Runs end-to-end gameplay scenarios that integrate all game systems.
    """
    def __init__(self, debug: bool = False):
        self.debug = debug
        
        # Initialize core systems
        self.magic_system = MagicSystem()
        self.text_parser = TextParser()
        self.ai_gm = AIGMBrain()
        
        # Game state storage
        self.player_states = {}
        self.world_state = {}
        self.quest_states = {}
        self.npc_states = {}
        self.combat_states = {}
        
        # Initialize logging
        self.action_log = []
        self.system_log = []
    
    def log_action(self, action: str, details: Dict[str, Any] = None) -> None:
        """Log a player or system action."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details or {}
        }
        self.action_log.append(log_entry)
        
        if self.debug:
            print(f"ACTION: {action}")
            if details:
                print(f"DETAILS: {json.dumps(details, indent=2)}")
    
    def log_system(self, system: str, event: str, details: Dict[str, Any] = None) -> None:
        """Log a system event."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "system": system,
            "event": event,
            "details": details or {}
        }
        self.system_log.append(log_entry)
        
        if self.debug:
            print(f"SYSTEM: {system} - {event}")
            if details:
                print(f"DETAILS: {json.dumps(details, indent=2)}")
    
    def initialize_player(self, player_id: str, name: str) -> Dict[str, Any]:
        """Initialize a new player with starting state."""
        # Create basic player state
        player_state = {
            "id": player_id,
            "name": name,
            "level": 1,
            "experience": 0,
            "gold": 100,
            "health": {
                "current": 100,
                "max": 100
            },
            "location": {
                "region": "Emerald Vale",
                "area": "Crossroads",
                "coordinates": [0, 0]
            },
            "inventory": {
                "items": {
                    "basic_sword": {
                        "id": "basic_sword",
                        "name": "Iron Sword",
                        "type": "weapon",
                        "damage": 5,
                        "value": 10,
                        "equipped": True
                    },
                    "basic_armor": {
                        "id": "basic_armor",
                        "name": "Leather Armor",
                        "type": "armor",
                        "defense": 3,
                        "value": 15,
                        "equipped": True
                    },
                    "health_potion": {
                        "id": "health_potion",
                        "name": "Minor Health Potion",
                        "type": "consumable",
                        "effect": {"health": 20},
                        "value": 5,
                        "quantity": 3
                    }
                },
                "materials": {
                    "wood": 5,
                    "leather": 3,
                    "iron_ore": 2
                },
                "currency": 100
            },
            "skills": {
                "combat": {
                    "melee": 5,
                    "ranged": 3,
                    "defense": 4
                },
                "crafting": {
                    "blacksmithing": 2,
                    "alchemy": 1,
                    "enchanting": 0
                },
                "social": {
                    "persuasion": 3,
                    "intimidation": 2,
                    "bargaining": 2
                }
            },
            "quests": {
                "active": ["village_troubles"],
                "completed": []
            },
            "relationships": {
                "village_elder": 10,  # Neutral
                "blacksmith": 15      # Slightly positive
            }
        }
        
        # Create magic profile for the player
        magic_user = MagicUser(
            id=player_id,
            name=name,
            level=1,
            mana_max=50,
            mana_current=50,
            mana_regen_rate=1.0,  # 1 mana per minute
            primary_domains=[Domain.ARCANE],
            secondary_domains=[],
            known_spells={"arcane_bolt"},
            magic_skills={
                "spellcasting": 2,
                "concentration": 1,
                "magical_knowledge": 1,
                "mana_control": 1
            }
        )
        
        # Register with magic system
        self.magic_system.register_magic_user(magic_user)
        
        # Create starting spell
        arcane_bolt = Spell(
            id="arcane_bolt",
            name="Arcane Bolt",
            description="A simple bolt of arcane energy.",
            domains=[Domain.ARCANE],
            damage_types=[DamageType.ARCANE],
            effect_types=[EffectType.DAMAGE],
            mana_cost=5,
            casting_time=1.0,
            cooldown=2.0,
            base_power=3.0,
            level_req=1,
            tier=MagicTier.LESSER,
            targeting_type="single",
            range_max=20.0,
            duration=0.0,
            components=["verbal", "somatic"],
            tags=["arcane", "damage"]
        )
        
        # Register spell with magic system
        self.magic_system.register_spell(arcane_bolt)
        
        # Add magic profile to player state
        player_state["magic"] = {
            "profile_id": magic_user.id,
            "mana_current": magic_user.mana_current,
            "mana_max": magic_user.mana_max,
            "known_spells": list(magic_user.known_spells)
        }
        
        # Store player state
        self.player_states[player_id] = player_state
        
        # Log player creation
        self.log_system("PLAYER_SYSTEM", "PLAYER_CREATED", {
            "player_id": player_id,
            "name": name
        })
        
        return player_state
    
    def initialize_world(self) -> Dict[str, Any]:
        """Initialize the game world with regions, areas, and NPCs."""
        # Create world regions
        world_state = {
            "regions": {
                "emerald_vale": {
                    "id": "emerald_vale",
                    "name": "Emerald Vale",
                    "description": "A verdant valley with rolling hills and small settlements.",
                    "danger_level": 1,
                    "areas": {
                        "crossroads": {
                            "id": "crossroads",
                            "name": "Crossroads",
                            "description": "A small trading post where several roads meet.",
                            "npcs": ["village_elder", "traveling_merchant"],
                            "connected_areas": ["forest_path", "village_square"],
                            "points_of_interest": ["old_well", "notice_board"],
                            "encounters": ["wolf_pack", "bandit_ambush"],
                            "resources": ["wood", "herbs"]
                        },
                        "forest_path": {
                            "id": "forest_path",
                            "name": "Forest Path",
                            "description": "A winding path through the dense forest.",
                            "npcs": [],
                            "connected_areas": ["crossroads", "old_ruins"],
                            "points_of_interest": ["large_oak", "small_shrine"],
                            "encounters": ["wolf_pack", "forest_spirit"],
                            "resources": ["wood", "herbs", "mushrooms"]
                        },
                        "village_square": {
                            "id": "village_square",
                            "name": "Village Square",
                            "description": "The central gathering place in the village.",
                            "npcs": ["blacksmith", "innkeeper", "general_store_owner"],
                            "connected_areas": ["crossroads", "north_gate"],
                            "points_of_interest": ["village_fountain", "marketplace"],
                            "encounters": [],
                            "resources": []
                        },
                        "old_ruins": {
                            "id": "old_ruins",
                            "name": "Old Ruins",
                            "description": "The crumbling remains of an ancient structure.",
                            "npcs": [],
                            "connected_areas": ["forest_path"],
                            "points_of_interest": ["broken_statue", "sealed_door"],
                            "encounters": ["skeleton_patrol", "ancient_guardian"],
                            "resources": ["stone", "arcane_residue"]
                        }
                    }
                }
            },
            "current_time": {
                "hour": 12,
                "day": 1,
                "month": 1,
                "year": 1,
                "season": "spring"
            },
            "weather": {
                "current": "clear",
                "temperature": "mild"
            }
        }
        
        # Create NPCs
        npcs = {
            "village_elder": {
                "id": "village_elder",
                "name": "Elder Thaddeus",
                "description": "An elderly man with a long white beard and wise eyes.",
                "location": {
                    "region": "emerald_vale",
                    "area": "crossroads"
                },
                "dialogue": {
                    "greeting": "Welcome, traveler. What brings you to our humble crossroads?",
                    "quest_offer": "We've been having trouble with wolves attacking travelers. Could you help us?",
                    "quest_active": "Have you dealt with those wolves yet?",
                    "quest_complete": "Thank you for your help. The road is safer now."
                },
                "quests": ["village_troubles"],
                "inventory": {
                    "items": {},
                    "currency": 50
                },
                "schedule": {
                    "morning": "crossroads",
                    "afternoon": "crossroads",
                    "evening": "village_square",
                    "night": "village_square"
                }
            },
            "blacksmith": {
                "id": "blacksmith",
                "name": "Goran the Smith",
                "description": "A burly man with muscular arms and a soot-stained apron.",
                "location": {
                    "region": "emerald_vale",
                    "area": "village_square"
                },
                "dialogue": {
                    "greeting": "Need something forged? I'm your man.",
                    "shop": "Take a look at my wares. Quality guaranteed.",
                    "quest_offer": "I could use some iron ore if you're heading to the mines."
                },
                "inventory": {
                    "items": {
                        "steel_sword": {
                            "id": "steel_sword",
                            "name": "Steel Sword",
                            "type": "weapon",
                            "damage": 8,
                            "value": 30,
                            "for_sale": True
                        },
                        "iron_shield": {
                            "id": "iron_shield",
                            "name": "Iron Shield",
                            "type": "shield",
                            "defense": 5,
                            "value": 25,
                            "for_sale": True
                        }
                    },
                    "currency": 200
                },
                "crafting": {
                    "specialization": "blacksmithing",
                    "recipes": ["iron_dagger", "steel_sword", "iron_shield"]
                },
                "schedule": {
                    "morning": "village_square",
                    "afternoon": "village_square",
                    "evening": "village_square",
                    "night": "village_square"
                }
            }
        }
        
        # Create quests
        quests = {
            "village_troubles": {
                "id": "village_troubles",
                "name": "Village Troubles",
                "description": "Deal with the wolves that have been attacking travelers near the crossroads.",
                "giver": "village_elder",
                "stages": [
                    {
                        "id": "talk_to_elder",
                        "description": "Talk to Elder Thaddeus about the wolf problem.",
                        "completed": False
                    },
                    {
                        "id": "kill_wolves",
                        "description": "Hunt down and kill the wolves (0/3).",
                        "target": {
                            "type": "monster",
                            "id": "wolf",
                            "count": 3,
                            "current": 0
                        },
                        "completed": False
                    },
                    {
                        "id": "return_to_elder",
                        "description": "Return to Elder Thaddeus to report your success.",
                        "completed": False
                    }
                ],
                "rewards": {
                    "experience": 100,
                    "gold": 50,
                    "items": ["leather_boots"],
                    "reputation": {
                        "village_elder": 15
                    }
                },
                "status": "available",
                "location": {
                    "region": "emerald_vale",
                    "area": "crossroads"
                }
            }
        }
        
        # Create monsters
        monsters = {
            "wolf": {
                "id": "wolf",
                "name": "Forest Wolf",
                "description": "A gray wolf with sharp teeth and keen eyes.",
                "level": 2,
                "health": {
                    "current": 30,
                    "max": 30
                },
                "attacks": [
                    {
                        "name": "Bite",
                        "damage": [3, 6],
                        "type": "physical"
                    },
                    {
                        "name": "Howl",
                        "effect": "intimidate",
                        "type": "status"
                    }
                ],
                "loot": {
                    "wolf_pelt": 0.8,  # 80% chance
                    "wolf_fang": 0.4,  # 40% chance
                    "meat": 1.0        # 100% chance
                },
                "spawn_areas": ["forest_path", "old_ruins"],
                "aggression": "territorial"
            },
            "skeleton": {
                "id": "skeleton",
                "name": "Ancient Skeleton",
                "description": "The animated bones of a long-dead warrior.",
                "level": 3,
                "health": {
                    "current": 25,
                    "max": 25
                },
                "attacks": [
                    {
                        "name": "Bone Slash",
                        "damage": [4, 7],
                        "type": "physical"
                    }
                ],
                "resistances": {
                    "piercing": 0.5,
                    "fire": -0.5
                },
                "loot": {
                    "bone": 1.0,      # 100% chance
                    "rusty_sword": 0.3 # 30% chance
                },
                "spawn_areas": ["old_ruins"],
                "aggression": "hostile"
            }
        }
        
        # Store world state components
        self.world_state = world_state
        self.npc_states = npcs
        self.quest_states = quests
        self.monster_states = monsters
        
        # Log world initialization
        self.log_system("WORLD_SYSTEM", "WORLD_INITIALIZED", {
            "regions": list(world_state["regions"].keys())
        })
        
        return world_state
    
    def process_player_command(self, player_id: str, command_text: str) -> Dict[str, Any]:
        """
        Process a player command through all relevant systems.
        
        This is the main entry point for the end-to-end scenario,
        simulating how a player's text command flows through the system.
        """
        # Get player state
        player_state = self.player_states.get(player_id)
        if not player_state:
            return {"error": "Player not found"}
        
        # Log the player command
        self.log_action("PLAYER_COMMAND", {
            "player_id": player_id,
            "command": command_text
        })
        
        # 1. Text parsing stage - Convert natural language to game actions
        self.log_system("TEXT_PARSER", "PARSING_COMMAND", {"command": command_text})
        parsed_command = self.text_parser.parse_command(command_text)
        self.log_system("TEXT_PARSER", "COMMAND_PARSED", {"parsed_command": parsed_command})
        
        # 2. Action dispatch - Route to appropriate system
        action_type = parsed_command.get("action_type")
        
        # 3. Execute the action through the appropriate system
        result = {}
        
        if action_type == "movement":
            result = self._handle_movement(player_id, parsed_command)
        elif action_type == "dialogue":
            result = self._handle_dialogue(player_id, parsed_command)
        elif action_type == "combat":
            result = self._handle_combat(player_id, parsed_command)
        elif action_type == "inventory":
            result = self._handle_inventory(player_id, parsed_command)
        elif action_type == "magic":
            result = self._handle_magic(player_id, parsed_command)
        elif action_type == "crafting":
            result = self._handle_crafting(player_id, parsed_command)
        elif action_type == "quest":
            result = self._handle_quest(player_id, parsed_command)
        elif action_type == "examine":
            result = self._handle_examine(player_id, parsed_command)
        else:
            # Default to AI GM handling for complex or unrecognized commands
            result = self._handle_with_ai_gm(player_id, parsed_command)
        
        # 4. Update game state based on action results
        self._update_game_state(player_id, action_type, result)
        
        # 5. Generate response for player
        response = self._generate_player_response(player_id, action_type, result)
        
        # Log the response
        self.log_system("RESPONSE_GENERATOR", "RESPONSE_GENERATED", {
            "player_id": player_id,
            "response": response
        })
        
        return response
    
    def _handle_movement(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player movement between areas."""
        player = self.player_states[player_id]
        current_region = player["location"]["region"]
        current_area = player["location"]["area"]
        
        # Get destination from command
        destination = parsed_command.get("target")
        if not destination:
            return {"success": False, "message": "No destination specified"}
        
        # Check if destination is a connected area
        current_region_data = self.world_state["regions"].get(current_region, {})
        current_area_data = current_region_data.get("areas", {}).get(current_area, {})
        connected_areas = current_area_data.get("connected_areas", [])
        
        # Try to find the area by name matching
        destination_area = None
        for area_id in connected_areas:
            area_data = current_region_data.get("areas", {}).get(area_id, {})
            area_name = area_data.get("name", "").lower()
            if destination.lower() in area_name or area_id.lower() == destination.lower():
                destination_area = area_id
                break
        
        if not destination_area:
            return {"success": False, "message": f"Cannot travel to {destination} from here"}
        
        # Move player to new area
        old_area = player["location"]["area"]
        player["location"]["area"] = destination_area
        
        # Check for random encounters
        encounter = self._check_for_encounter(player_id, destination_area)
        
        # Trigger area discovery events if this is the player's first visit
        visited_areas = player.get("visited_areas", [])
        is_first_visit = destination_area not in visited_areas
        
        if is_first_visit:
            player.setdefault("visited_areas", []).append(destination_area)
            self.log_system("ACHIEVEMENT_SYSTEM", "AREA_DISCOVERED", {
                "player_id": player_id,
                "area": destination_area
            })
        
        # Return result of movement
        result = {
            "success": True,
            "message": f"You travel from {old_area} to {destination_area}",
            "old_area": old_area,
            "new_area": destination_area,
            "first_visit": is_first_visit,
            "encounter": encounter
        }
        
        # Log the movement
        self.log_system("MOVEMENT_SYSTEM", "PLAYER_MOVED", {
            "player_id": player_id,
            "from_area": old_area,
            "to_area": destination_area
        })
        
        return result
    
    def _check_for_encounter(self, player_id: str, area_id: str) -> Optional[Dict[str, Any]]:
        """Check if player triggers a random encounter when entering an area."""
        player = self.player_states[player_id]
        region_id = player["location"]["region"]
        
        # Get area data
        area_data = self.world_state["regions"].get(region_id, {}).get("areas", {}).get(area_id, {})
        possible_encounters = area_data.get("encounters", [])
        
        if not possible_encounters:
            return None
        
        # 30% chance of encounter when entering an area with possible encounters
        if random.random() < 0.3:
            # Select a random encounter
            encounter_id = random.choice(possible_encounters)
            
            # Check if it's a monster encounter
            if encounter_id == "wolf_pack" and area_id == "forest_path":
                # Create a wolf pack encounter
                encounter = {
                    "type": "combat",
                    "id": f"encounter_{uuid.uuid4().hex[:8]}",
                    "name": "Wolf Pack",
                    "description": "A pack of wolves blocks your path, growling menacingly.",
                    "monsters": [
                        {"id": "wolf", "name": "Forest Wolf", "count": 3}
                    ],
                    "loot": {
                        "wolf_pelt": 2,
                        "wolf_fang": 1,
                        "meat": 3
                    },
                    "quest_related": "village_troubles" if "village_troubles" in player["quests"]["active"] else None
                }
                
                # Log the encounter
                self.log_system("ENCOUNTER_SYSTEM", "ENCOUNTER_TRIGGERED", {
                    "player_id": player_id,
                    "encounter": encounter["name"],
                    "area": area_id
                })
                
                return encounter
            
            elif encounter_id == "skeleton_patrol" and area_id == "old_ruins":
                # Create a skeleton patrol encounter
                encounter = {
                    "type": "combat",
                    "id": f"encounter_{uuid.uuid4().hex[:8]}",
                    "name": "Skeleton Patrol",
                    "description": "A group of skeletons patrols among the ancient stones.",
                    "monsters": [
                        {"id": "skeleton", "name": "Ancient Skeleton", "count": 2}
                    ],
                    "loot": {
                        "bone": 4,
                        "rusty_sword": 1,
                        "ancient_coin": 5
                    }
                }
                
                # Log the encounter
                self.log_system("ENCOUNTER_SYSTEM", "ENCOUNTER_TRIGGERED", {
                    "player_id": player_id,
                    "encounter": encounter["name"],
                    "area": area_id
                })
                
                return encounter
        
        return None
    
    def _handle_dialogue(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player dialogue with NPCs."""
        player = self.player_states[player_id]
        current_region = player["location"]["region"]
        current_area = player["location"]["area"]
        
        # Get target NPC from command
        npc_target = parsed_command.get("target")
        if not npc_target:
            return {"success": False, "message": "No NPC specified for dialogue"}
        
        # Check if NPC is in the current area
        area_data = self.world_state["regions"].get(current_region, {}).get("areas", {}).get(current_area, {})
        area_npcs = area_data.get("npcs", [])
        
        # Find the NPC by name or ID
        npc_id = None
        for possible_npc_id in area_npcs:
            npc_data = self.npc_states.get(possible_npc_id, {})
            npc_name = npc_data.get("name", "").lower()
            if npc_target.lower() in npc_name or possible_npc_id.lower() == npc_target.lower():
                npc_id = possible_npc_id
                break
        
        if not npc_id:
            return {"success": False, "message": f"{npc_target} is not here"}
        
        # Get NPC data
        npc = self.npc_states[npc_id]
        
        # Determine dialogue topic
        topic = parsed_command.get("topic", "greeting")
        
        # Get dialogue for topic
        dialogue_response = npc["dialogue"].get(topic, npc["dialogue"].get("greeting"))
        
        # Handle special dialogue topics
        if topic == "quest" and "quest_offer" in npc["dialogue"]:
            # Check if NPC has quests to offer
            available_quests = []
            for quest_id in npc.get("quests", []):
                quest = self.quest_states.get(quest_id)
                if quest and quest["status"] == "available":
                    available_quests.append(quest)
            
            if available_quests:
                # Offer first available quest
                quest = available_quests[0]
                dialogue_response = npc["dialogue"]["quest_offer"]
                
                # Update quest status to offered
                quest["status"] = "offered"
                
                # Log quest offered
                self.log_system("QUEST_SYSTEM", "QUEST_OFFERED", {
                    "player_id": player_id,
                    "npc_id": npc_id,
                    "quest_id": quest["id"]
                })
        
        elif topic == "shop" and "shop" in npc["dialogue"]:
            # Show shop inventory
            shop_items = []
            for item_id, item in npc.get("inventory", {}).get("items", {}).items():
                if item.get("for_sale"):
                    shop_items.append(item)
            
            return {
                "success": True,
                "message": npc["dialogue"]["shop"],
                "npc_id": npc_id,
                "npc_name": npc["name"],
                "dialogue_type": "shop",
                "shop_items": shop_items
            }
        
        # Check if dialogue completes a quest stage
        self._check_quest_stage_completion(player_id, "dialogue", npc_id)
        
        # Return dialogue result
        result = {
            "success": True,
            "message": dialogue_response,
            "npc_id": npc_id,
            "npc_name": npc["name"],
            "dialogue_type": topic
        }
        
        # Log the dialogue
        self.log_system("DIALOGUE_SYSTEM", "PLAYER_DIALOGUE", {
            "player_id": player_id,
            "npc_id": npc_id,
            "topic": topic
        })
        
        return result
    
    def _handle_combat(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player combat actions."""
        player = self.player_states[player_id]
        
        # Check if player is in combat
        if "active_combat" not in player:
            # Player is initiating combat
            target = parsed_command.get("target")
            if not target:
                return {"success": False, "message": "No target specified for combat"}
            
            # Check for monster in the area
            current_region = player["location"]["region"]
            current_area = player["location"]["area"]
            
            # Generate a combat encounter based on the area
            area_data = self.world_state["regions"].get(current_region, {}).get("areas", {}).get(current_area, {})
            area_encounters = area_data.get("encounters", [])
            
            combat_encounter = None
            for encounter_id in area_encounters:
                if "wolf" in encounter_id and "wolf" in target.lower():
                    # Create wolf encounter
                    combat_encounter = {
                        "id": f"combat_{uuid.uuid4().hex[:8]}",
                        "type": "combat",
                        "status": "active",
                        "enemies": [
                            {
                                "id": f"wolf_{uuid.uuid4().hex[:8]}",
                                "type": "wolf",
                                "name": "Forest Wolf",
                                "health": {"current": 30, "max": 30},
                                "level": 2
                            }
                        ],
                        "loot": {
                            "wolf_pelt": 1,
                            "wolf_fang": 1 if random.random() < 0.4 else 0,
                            "meat": 1
                        },
                        "quest_related": "village_troubles" if "village_troubles" in player["quests"]["active"] else None,
                        "round": 1,
                        "player_turn": True
                    }
                    break
                elif "skeleton" in encounter_id and "skeleton" in target.lower():
                    # Create skeleton encounter
                    combat_encounter = {
                        "id": f"combat_{uuid.uuid4().hex[:8]}",
                        "type": "combat",
                        "status": "active",
                        "enemies": [
                            {
                                "id": f"skeleton_{uuid.uuid4().hex[:8]}",
                                "type": "skeleton",
                                "name": "Ancient Skeleton",
                                "health": {"current": 25, "max": 25},
                                "level": 3
                            }
                        ],
                        "loot": {
                            "bone": 2,
                            "rusty_sword": 1 if random.random() < 0.3 else 0
                        },
                        "round": 1,
                        "player_turn": True
                    }
                    break
            
            if not combat_encounter:
                return {"success": False, "message": f"No {target} found to attack"}
            
            # Start combat
            player["active_combat"] = combat_encounter
            
            # Log combat start
            self.log_system("COMBAT_SYSTEM", "COMBAT_STARTED", {
                "player_id": player_id,
                "combat_id": combat_encounter["id"],
                "enemies": [e["name"] for e in combat_encounter["enemies"]]
            })
            
            return {
                "success": True,
                "message": f"You engage in combat with {combat_encounter['enemies'][0]['name']}!",
                "combat_started": True,
                "combat_id": combat_encounter["id"],
                "enemies": combat_encounter["enemies"]
            }
        else:
            # Player is already in combat
            combat = player["active_combat"]
            
            # Check if it's player's turn
            if not combat["player_turn"]:
                return {"success": False, "message": "It's not your turn yet"}
            
            # Get action and target
            action = parsed_command.get("action", "attack")
            target_id = parsed_command.get("target")
            
            # Find target enemy
            target_enemy = None
            for enemy in combat["enemies"]:
                if target_id:
                    if enemy["id"] == target_id or target_id.lower() in enemy["name"].lower():
                        target_enemy = enemy
                        break
                else:
                    # Default to first enemy if no target specified
                    target_enemy = enemy
                    break
            
            if not target_enemy:
                return {"success": False, "message": "Target not found"}
            
            # Process attack
            if action == "attack":
                # Calculate damage
                player_weapon = next((item for item in player["inventory"]["items"].values() 
                                     if item.get("type") == "weapon" and item.get("equipped")), None)
                
                base_damage = player_weapon["damage"] if player_weapon else 2
                skill_bonus = player["skills"]["combat"]["melee"] * 0.5
                damage_roll = random.randint(1, 6)
                total_damage = int(base_damage + skill_bonus + damage_roll)
                
                # Apply damage to enemy
                target_enemy["health"]["current"] -= total_damage
                
                # Check if enemy is defeated
                enemy_defeated = target_enemy["health"]["current"] <= 0
                if enemy_defeated:
                    target_enemy["health"]["current"] = 0
                    combat["enemies"] = [e for e in combat["enemies"] if e["id"] != target_enemy["id"]]
                
                # Check if combat is over
                combat_over = len(combat["enemies"]) == 0
                if combat_over:
                    # End combat
                    combat["status"] = "completed"
                    
                    # Award loot
                    for item, quantity in combat["loot"].items():
                        if quantity > 0:
                            if item in player["inventory"]["materials"]:
                                player["inventory"]["materials"][item] += quantity
                            else:
                                player["inventory"]["materials"][item] = quantity
                    
                    # Check if this completes a quest objective
                    if combat.get("quest_related") == "village_troubles" and target_enemy["type"] == "wolf":
                        for quest_id in player["quests"]["active"]:
                            if quest_id == "village_troubles":
                                quest = self.quest_states[quest_id]
                                for stage in quest["stages"]:
                                    if stage["id"] == "kill_wolves" and not stage["completed"]:
                                        stage["target"]["current"] += 1
                                        
                                        # Check if all wolves are killed
                                        if stage["target"]["current"] >= stage["target"]["count"]:
                                            stage["completed"] = True
                                            
                                            # Log quest stage completion
                                            self.log_system("QUEST_SYSTEM", "QUEST_STAGE_COMPLETED", {
                                                "player_id": player_id,
                                                "quest_id": quest_id,
                                                "stage_id": stage["id"]
                                            })
                    
                    # Remove active combat
                    del player["active_combat"]
                    
                    # Log combat end
                    self.log_system("COMBAT_SYSTEM", "COMBAT_COMPLETED", {
                        "player_id": player_id,
                        "combat_id": combat["id"],
                        "outcome": "victory"
                    })
                    
                    return {
                        "success": True,
                        "message": f"You defeated {target_enemy['name']}!",
                        "damage_dealt": total_damage,
                        "enemy_defeated": True,
                        "combat_completed": True,
                        "loot_gained": combat["loot"]
                    }
                
                # End player turn
                combat["player_turn"] = False
                
                # Process enemy turn
                enemy_damage = 0
                damage_type = "physical"
                enemy_action = "attacks"
                
                if len(combat["enemies"]) > 0:
                    # Get first active enemy
                    active_enemy = combat["enemies"][0]
                    
                    # Select random attack
                    enemy_type = active_enemy["type"]
                    monster_data = self.monster_states.get(enemy_type, {})
                    attacks = monster_data.get("attacks", [])
                    
                    if attacks:
                        attack = random.choice(attacks)
                        enemy_action = attack["name"]
                        damage_type = attack["type"]
                        
                        if "damage" in attack:
                            min_dmg, max_dmg = attack["damage"]
                            enemy_damage = random.randint(min_dmg, max_dmg)
                            
                            # Apply damage to player
                            player["health"]["current"] -= enemy_damage
                            
                            # Ensure health doesn't go below 0
                            player["health"]["current"] = max(0, player["health"]["current"])
                    
                    # Check if player is defeated
                    player_defeated = player["health"]["current"] <= 0
                    if player_defeated:
                        # End combat
                        combat["status"] = "completed"
                        
                        # Remove active combat
                        del player["active_combat"]
                        
                        # Log combat end
                        self.log_system("COMBAT_SYSTEM", "COMBAT_COMPLETED", {
                            "player_id": player_id,
                            "combat_id": combat["id"],
                            "outcome": "defeat"
                        })
                        
                        return {
                            "success": True,
                            "message": f"You were defeated by {active_enemy['name']}!",
                            "damage_dealt": total_damage,
                            "enemy_action": enemy_action,
                            "damage_taken": enemy_damage,
                            "player_defeated": True,
                            "combat_completed": True
                        }
                
                # Start new round, player's turn again
                combat["round"] += 1
                combat["player_turn"] = True
                
                return {
                    "success": True,
                    "message": f"You hit {target_enemy['name']} for {total_damage} damage!",
                    "damage_dealt": total_damage,
                    "enemy_defeated": enemy_defeated,
                    "enemy_action": enemy_action,
                    "damage_taken": enemy_damage,
                    "combat_continues": True,
                    "round": combat["round"]
                }
            
            elif action == "cast":
                # Handle spell casting in combat via the magic system
                spell_id = parsed_command.get("spell")
                if not spell_id:
                    return {"success": False, "message": "No spell specified"}
                
                # Forward to magic handling
                magic_result = self._handle_magic(player_id, {
                    "action_type": "magic",
                    "action": "cast",
                    "spell": spell_id,
                    "target": target_enemy["id"]
                })
                
                if magic_result["success"]:
                    # Check if enemy is defeated
                    enemy_defeated = target_enemy["health"]["current"] <= 0
                    if enemy_defeated:
                        target_enemy["health"]["current"] = 0
                        combat["enemies"] = [e for e in combat["enemies"] if e["id"] != target_enemy["id"]]
                    
                    # Check if combat is over
                    combat_over = len(combat["enemies"]) == 0
                    if combat_over:
                        # End combat
                        combat["status"] = "completed"
                        
                        # Award loot
                        for item, quantity in combat["loot"].items():
                            if quantity > 0:
                                if item in player["inventory"]["materials"]:
                                    player["inventory"]["materials"][item] += quantity
                                else:
                                    player["inventory"]["materials"][item] = quantity
                        
                        # Remove active combat
                        del player["active_combat"]
                        
                        # Log combat end
                        self.log_system("COMBAT_SYSTEM", "COMBAT_COMPLETED", {
                            "player_id": player_id,
                            "combat_id": combat["id"],
                            "outcome": "victory"
                        })
                        
                        return {
                            "success": True,
                            "message": f"You defeated {target_enemy['name']} with {magic_result.get('spell_name', 'a spell')}!",
                            "spell_cast": True,
                            "spell_result": magic_result,
                            "enemy_defeated": True,
                            "combat_completed": True,
                            "loot_gained": combat["loot"]
                        }
                    
                    # End player turn
                    combat["player_turn"] = False
                    
                    # Process enemy turn (similar to attack action)
                    # ... (enemy turn logic)
                    
                    # Start new round, player's turn again
                    combat["round"] += 1
                    combat["player_turn"] = True
                    
                    return {
                        "success": True,
                        "message": magic_result.get("message", "You cast a spell!"),
                        "spell_cast": True,
                        "spell_result": magic_result,
                        "enemy_defeated": enemy_defeated,
                        "combat_continues": True,
                        "round": combat["round"]
                    }
                else:
                    return magic_result
            
            elif action == "flee":
                # Attempt to flee combat
                flee_chance = 0.4 + (player["skills"]["combat"]["defense"] * 0.05)
                flee_success = random.random() < flee_chance
                
                if flee_success:
                    # End combat
                    combat["status"] = "fled"
                    
                    # Remove active combat
                    del player["active_combat"]
                    
                    # Log combat end
                    self.log_system("COMBAT_SYSTEM", "COMBAT_FLED", {
                        "player_id": player_id,
                        "combat_id": combat["id"]
                    })
                    
                    return {
                        "success": True,
                        "message": "You successfully flee from combat!",
                        "fled": True,
                        "combat_completed": True
                    }
                else:
                    # Failed to flee, enemy gets an attack
                    combat["player_turn"] = False
                    
                    # Process enemy turn
                    # ... (enemy turn logic)
                    
                    # Start new round, player's turn again
                    combat["round"] += 1
                    combat["player_turn"] = True
                    
                    return {
                        "success": False,
                        "message": "You failed to flee from combat!",
                        "fled": False,
                        "combat_continues": True,
                        "round": combat["round"]
                    }
            
            else:
                return {"success": False, "message": f"Unknown combat action: {action}"}
    
    def _handle_magic(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player magic actions."""
        player = self.player_states[player_id]
        magic_profile_id = player.get("magic", {}).get("profile_id")
        
        if not magic_profile_id:
            return {"success": False, "message": "You don't have magical abilities"}
        
        # Get magic user from magic system
        magic_user = self.magic_system.magic_users.get(magic_profile_id)
        if not magic_user:
            return {"success": False, "message": "Magic profile not found"}
        
        # Get action and spell
        action = parsed_command.get("action", "cast")
        spell_id = parsed_command.get("spell")
        
        # Handle spell casting
        if action == "cast":
            if not spell_id:
                return {"success": False, "message": "No spell specified"}
            
            # Check if spell is known
            if spell_id not in magic_user.known_spells:
                return {"success": False, "message": f"You don't know the spell {spell_id}"}
            
            # Get spell from magic system
            spell = self.magic_system.spells.get(spell_id)
            if not spell:
                return {"success": False, "message": f"Unknown spell: {spell_id}"}
            
            # Check if player has enough mana
            if magic_user.mana_current < spell.mana_cost:
                return {
                    "success": False, 
                    "message": f"Not enough mana. Required: {spell.mana_cost}, Current: {magic_user.mana_current}"
                }
            
            # Get target if specified
            target_id = parsed_command.get("target")
            location_id = f"{player['location']['region']}_{player['location']['area']}"
            
            # Handle target selection based on context
            if "active_combat" in player and target_id:
                # In combat, target should be an enemy
                combat = player["active_combat"]
                target_enemy = None
                
                for enemy in combat["enemies"]:
                    if enemy["id"] == target_id or target_id.lower() in enemy["name"].lower():
                        target_enemy = enemy
                        break
                
                if target_enemy:
                    # Cast spell in combat
                    game_time = 0.0  # For simplicity
                    
                    # Call magic system to cast spell
                    cast_result = self.magic_system.cast_spell(
                        caster_id=magic_user.id,
                        spell_id=spell_id,
                        target_id=target_enemy["id"],
                        location_id=location_id,
                        current_time=game_time
                    )
                    
                    if cast_result["success"]:
                        # Apply spell effects to target
                        if any(effect.get("effect_type") == "DAMAGE" for effect in cast_result.get("effects", [])):
                            # Calculate total damage from effects
                            total_damage = 0
                            for effect in cast_result.get("effects", []):
                                if effect.get("effect_type") == "DAMAGE":
                                    total_damage += effect.get("potency", 0)
                            
                            # Apply damage to enemy
                            target_enemy["health"]["current"] -= int(total_damage)
                            
                            # Update mana in player state
                            player["magic"]["mana_current"] = magic_user.mana_current
                            
                            return {
                                "success": True,
                                "message": f"You cast {spell.name} at {target_enemy['name']} for {int(total_damage)} damage!",
                                "spell_name": spell.name,
                                "spell_id": spell_id,
                                "target": target_enemy["name"],
                                "damage_dealt": int(total_damage),
                                "mana_spent": spell.mana_cost,
                                "mana_remaining": magic_user.mana_current
                            }
                        else:
                            # Non-damage spell effects
                            # Update mana in player state
                            player["magic"]["mana_current"] = magic_user.mana_current
                            
                            return {
                                "success": True,
                                "message": f"You cast {spell.name} at {target_enemy['name']}!",
                                "spell_name": spell.name,
                                "spell_id": spell_id,
                                "target": target_enemy["name"],
                                "mana_spent": spell.mana_cost,
                                "mana_remaining": magic_user.mana_current
                            }
                    else:
                        return cast_result
                else:
                    return {"success": False, "message": f"Target {target_id} not found in combat"}
            else:
                # Not in combat, general spell casting
                game_time = 0.0  # For simplicity
                
                # Call magic system to cast spell
                cast_result = self.magic_system.cast_spell(
                    caster_id=magic_user.id,
                    spell_id=spell_id,
                    target_id=target_id,
                    location_id=location_id,
                    current_time=game_time
                )
                
                if cast_result["success"]:
                    # Update mana in player state
                    player["magic"]["mana_current"] = magic_user.mana_current
                    
                    return {
                        "success": True,
                        "message": f"You cast {spell.name}!",
                        "spell_name": spell.name,
                        "spell_id": spell_id,
                        "mana_spent": spell.mana_cost,
                        "mana_remaining": magic_user.mana_current
                    }
                else:
                    return cast_result
        
        elif action == "learn":
            # Learning a new spell would go here
            return {"success": False, "message": "Spell learning not implemented yet"}
        
        else:
            return {"success": False, "message": f"Unknown magic action: {action}"}
    
    def _handle_inventory(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player inventory actions."""
        player = self.player_states[player_id]
        action = parsed_command.get("action", "view")
        
        if action == "view":
            # Return player inventory
            return {
                "success": True,
                "message": "Your inventory:",
                "inventory": player["inventory"]
            }
        
        elif action == "use":
            item_id = parsed_command.get("item")
            if not item_id:
                return {"success": False, "message": "No item specified"}
            
            # Find item in inventory
            item = None
            for inv_item_id, inv_item in player["inventory"]["items"].items():
                if inv_item_id == item_id or item_id.lower() in inv_item.get("name", "").lower():
                    item = inv_item
                    item_id = inv_item_id
                    break
            
            if not item:
                return {"success": False, "message": f"Item {item_id} not found in inventory"}
            
            # Handle different item types
            if item.get("type") == "consumable":
                # Apply item effects
                if "effect" in item:
                    for effect_type, value in item["effect"].items():
                        if effect_type == "health":
                            # Heal player
                            old_health = player["health"]["current"]
                            player["health"]["current"] = min(player["health"]["max"], old_health + value)
                            
                            # Remove one from quantity or remove item if last one
                            item["quantity"] -= 1
                            if item["quantity"] <= 0:
                                del player["inventory"]["items"][item_id]
                            
                            return {
                                "success": True,
                                "message": f"You use {item['name']} and heal for {player['health']['current'] - old_health} health.",
                                "item_used": item["name"],
                                "health_restored": player["health"]["current"] - old_health
                            }
                        
                        # Other effect types would be handled here
                
                return {"success": False, "message": f"Cannot use {item['name']}"}
            
            elif item.get("type") in ["weapon", "armor", "shield"]:
                # Toggle equipped status
                currently_equipped = item.get("equipped", False)
                
                if currently_equipped:
                    item["equipped"] = False
                    return {
                        "success": True,
                        "message": f"You unequip {item['name']}.",
                        "item_unequipped": item["name"]
                    }
                else:
                    # Unequip any other items of the same type
                    for other_id, other_item in player["inventory"]["items"].items():
                        if other_item.get("type") == item["type"] and other_item.get("equipped", False):
                            other_item["equipped"] = False
                    
                    # Equip this item
                    item["equipped"] = True
                    
                    return {
                        "success": True,
                        "message": f"You equip {item['name']}.",
                        "item_equipped": item["name"]
                    }
            
            else:
                return {"success": False, "message": f"Cannot use {item['name']}"}
        
        elif action == "drop":
            item_id = parsed_command.get("item")
            if not item_id:
                return {"success": False, "message": "No item specified"}
            
            # Find item in inventory
            item = None
            for inv_item_id, inv_item in player["inventory"]["items"].items():
                if inv_item_id == item_id or item_id.lower() in inv_item.get("name", "").lower():
                    item = inv_item
                    item_id = inv_item_id
                    break
            
            if not item:
                return {"success": False, "message": f"Item {item_id} not found in inventory"}
            
            # Remove item from inventory
            del player["inventory"]["items"][item_id]
            
            return {
                "success": True,
                "message": f"You drop {item['name']}.",
                "item_dropped": item["name"]
            }
        
        else:
            return {"success": False, "message": f"Unknown inventory action: {action}"}
    
    def _handle_crafting(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player crafting actions."""
        player = self.player_states[player_id]
        action = parsed_command.get("action", "craft")
        
        # Check if player is at a crafting location
        current_region = player["location"]["region"]
        current_area = player["location"]["area"]
        
        # For this example, assume crafting is available in the village_square (blacksmith)
        if current_area != "village_square" and action != "recipes":
            return {
                "success": False, 
                "message": "You need to be at a crafting location. Try visiting the village square."
            }
        
        if action == "recipes":
            # List available recipes based on player skills
            available_recipes = []
            
            # Check blacksmithing skill
            if player["skills"]["crafting"]["blacksmithing"] > 0:
                available_recipes.append({
                    "id": "iron_dagger",
                    "name": "Iron Dagger",
                    "type": "weapon",
                    "damage": 4,
                    "materials": {"iron_ore": 1, "wood": 1},
                    "skill_required": "blacksmithing",
                    "skill_level": 1
                })
            
            if player["skills"]["crafting"]["blacksmithing"] >= 2:
                available_recipes.append({
                    "id": "iron_sword",
                    "name": "Iron Sword",
                    "type": "weapon",
                    "damage": 6,
                    "materials": {"iron_ore": 2, "wood": 1},
                    "skill_required": "blacksmithing",
                    "skill_level": 2
                })
            
            # Check alchemy skill
            if player["skills"]["crafting"]["alchemy"] > 0:
                available_recipes.append({
                    "id": "minor_health_potion",
                    "name": "Minor Health Potion",
                    "type": "consumable",
                    "effect": {"health": 20},
                    "materials": {"herbs": 2},
                    "skill_required": "alchemy",
                    "skill_level": 1
                })
            
            return {
                "success": True,
                "message": "Available crafting recipes:",
                "recipes": available_recipes
            }
        
        elif action == "craft":
            recipe_id = parsed_command.get("recipe")
            if not recipe_id:
                return {"success": False, "message": "No recipe specified"}
            
            # Find recipe
            recipe = None
            if recipe_id == "iron_dagger" and player["skills"]["crafting"]["blacksmithing"] >= 1:
                recipe = {
                    "id": "iron_dagger",
                    "name": "Iron Dagger",
                    "type": "weapon",
                    "damage": 4,
                    "materials": {"iron_ore": 1, "wood": 1},
                    "skill_required": "blacksmithing",
                    "skill_level": 1
                }
            elif recipe_id == "iron_sword" and player["skills"]["crafting"]["blacksmithing"] >= 2:
                recipe = {
                    "id": "iron_sword",
                    "name": "Iron Sword",
                    "type": "weapon",
                    "damage": 6,
                    "materials": {"iron_ore": 2, "wood": 1},
                    "skill_required": "blacksmithing",
                    "skill_level": 2
                }
            elif recipe_id == "minor_health_potion" and player["skills"]["crafting"]["alchemy"] >= 1:
                recipe = {
                    "id": "minor_health_potion",
                    "name": "Minor Health Potion",
                    "type": "consumable",
                    "effect": {"health": 20},
                    "materials": {"herbs": 2},
                    "skill_required": "alchemy",
                    "skill_level": 1
                }
            
            if not recipe:
                return {"success": False, "message": f"Recipe {recipe_id} not found or skill too low"}
            
            # Check if player has required materials
            for material, amount in recipe["materials"].items():
                if player["inventory"]["materials"].get(material, 0) < amount:
                    return {
                        "success": False, 
                        "message": f"Not enough {material}. Need {amount}, have {player['inventory']['materials'].get(material, 0)}"
                    }
            
            # Consume materials
            for material, amount in recipe["materials"].items():
                player["inventory"]["materials"][material] -= amount
            
            # Create crafted item
            item_id = f"{recipe_id}_{uuid.uuid4().hex[:8]}"
            crafted_item = {
                "id": item_id,
                "name": recipe["name"],
                "type": recipe["type"]
            }
            
            if recipe["type"] == "weapon":
                crafted_item["damage"] = recipe["damage"]
                crafted_item["value"] = recipe["damage"] * 5
                crafted_item["equipped"] = False
            elif recipe["type"] == "consumable":
                crafted_item["effect"] = recipe["effect"]
                crafted_item["value"] = 10
                crafted_item["quantity"] = 1
            
            # Add to inventory
            player["inventory"]["items"][item_id] = crafted_item
            
            # Award experience for crafting
            skill_type = recipe["skill_required"]
            skill_exp_gain = recipe["skill_level"] * 10
            player["skills"]["crafting"][skill_type] += 0.1  # Small skill increase
            
            # Log crafting
            self.log_system("CRAFTING_SYSTEM", "ITEM_CRAFTED", {
                "player_id": player_id,
                "item_name": crafted_item["name"],
                "recipe_id": recipe["id"]
            })
            
            return {
                "success": True,
                "message": f"You craft {crafted_item['name']}.",
                "item_crafted": crafted_item,
                "materials_used": recipe["materials"],
                "skill_gain": {skill_type: 0.1}
            }
        
        else:
            return {"success": False, "message": f"Unknown crafting action: {action}"}
    
    def _handle_quest(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player quest actions."""
        player = self.player_states[player_id]
        action = parsed_command.get("action", "view")
        
        if action == "view":
            # Get active quests with details
            active_quests = []
            for quest_id in player["quests"]["active"]:
                quest = self.quest_states.get(quest_id)
                if quest:
                    active_quests.append(quest)
            
            # Get completed quests
            completed_quests = []
            for quest_id in player["quests"]["completed"]:
                quest = self.quest_states.get(quest_id)
                if quest:
                    completed_quests.append(quest)
            
            return {
                "success": True,
                "message": "Your quests:",
                "active_quests": active_quests,
                "completed_quests": completed_quests
            }
        
        elif action == "accept":
            quest_id = parsed_command.get("quest")
            if not quest_id:
                return {"success": False, "message": "No quest specified"}
            
            # Check if quest exists and is offered
            quest = self.quest_states.get(quest_id)
            if not quest:
                return {"success": False, "message": f"Quest {quest_id} not found"}
            
            if quest["status"] != "offered":
                return {"success": False, "message": f"Quest {quest['name']} is not currently offered to you"}
            
            # Accept the quest
            quest["status"] = "active"
            
            # Add to player's active quests if not already there
            if quest_id not in player["quests"]["active"]:
                player["quests"]["active"].append(quest_id)
            
            # Mark the first stage as active
            if quest["stages"] and not quest["stages"][0]["completed"]:
                quest["stages"][0]["active"] = True
            
            # Log quest acceptance
            self.log_system("QUEST_SYSTEM", "QUEST_ACCEPTED", {
                "player_id": player_id,
                "quest_id": quest_id
            })
            
            return {
                "success": True,
                "message": f"You accept the quest: {quest['name']}",
                "quest_accepted": quest["name"]
            }
        
        elif action == "complete":
            quest_id = parsed_command.get("quest")
            if not quest_id:
                return {"success": False, "message": "No quest specified"}
            
            # Check if quest exists and is active
            quest = self.quest_states.get(quest_id)
            if not quest:
                return {"success": False, "message": f"Quest {quest_id} not found"}
            
            if quest_id not in player["quests"]["active"]:
                return {"success": False, "message": f"Quest {quest['name']} is not in your active quests"}
            
            # Check if all stages are completed
            all_stages_completed = all(stage["completed"] for stage in quest["stages"])
            
            if not all_stages_completed:
                # Find the first incomplete stage
                for stage in quest["stages"]:
                    if not stage["completed"]:
                        return {
                            "success": False,
                            "message": f"Quest stage not completed: {stage['description']}",
                            "incomplete_stage": stage
                        }
            
            # Complete the quest
            quest["status"] = "completed"
            
            # Move from active to completed quests
            player["quests"]["active"].remove(quest_id)
            player["quests"]["completed"].append(quest_id)
            
            # Award quest rewards
            if "rewards" in quest:
                # Experience
                if "experience" in quest["rewards"]:
                    player["experience"] += quest["rewards"]["experience"]
                    
                    # Check for level up
                    exp_needed_for_level = player["level"] * 100
                    if player["experience"] >= exp_needed_for_level:
                        player["level"] += 1
                        player["health"]["max"] += 10
                        player["health"]["current"] = player["health"]["max"]
                        
                        # Log level up
                        self.log_system("PLAYER_SYSTEM", "PLAYER_LEVEL_UP", {
                            "player_id": player_id,
                            "new_level": player["level"]
                        })
                
                # Gold
                if "gold" in quest["rewards"]:
                    player["gold"] += quest["rewards"]["gold"]
                    player["inventory"]["currency"] += quest["rewards"]["gold"]
                
                # Items
                if "items" in quest["rewards"]:
                    for item_id in quest["rewards"]["items"]:
                        # In a real game, would look up item templates
                        if item_id == "leather_boots":
                            player["inventory"]["items"][item_id] = {
                                "id": item_id,
                                "name": "Leather Boots",
                                "type": "armor",
                                "defense": 2,
                                "value": 15,
                                "equipped": False
                            }
                
                # Reputation
                if "reputation" in quest["rewards"]:
                    for npc_id, rep_gain in quest["rewards"]["reputation"].items():
                        player["relationships"][npc_id] = player.get("relationships", {}).get(npc_id, 0) + rep_gain
            
            # Log quest completion
            self.log_system("QUEST_SYSTEM", "QUEST_COMPLETED", {
                "player_id": player_id,
                "quest_id": quest_id,
                "rewards": quest.get("rewards", {})
            })
            
            return {
                "success": True,
                "message": f"You complete the quest: {quest['name']}",
                "quest_completed": quest["name"],
                "rewards": quest.get("rewards", {})
            }
        
        else:
            return {"success": False, "message": f"Unknown quest action: {action}"}
    
    def _handle_examine(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle player examining objects, NPCs, or the environment."""
        player = self.player_states[player_id]
        target = parsed_command.get("target")
        
        if not target:
            return {"success": False, "message": "No target specified to examine"}
        
        current_region = player["location"]["region"]
        current_area = player["location"]["area"]
        
        # Check if examining an NPC
        area_data = self.world_state["regions"].get(current_region, {}).get("areas", {}).get(current_area, {})
        area_npcs = area_data.get("npcs", [])
        
        for npc_id in area_npcs:
            npc = self.npc_states.get(npc_id, {})
            npc_name = npc.get("name", "").lower()
            
            if target.lower() in npc_name or npc_id.lower() == target.lower():
                return {
                    "success": True,
                    "message": npc.get("description", f"You see {npc['name']}."),
                    "target_type": "npc",
                    "target_id": npc_id,
                    "target_name": npc["name"]
                }
        
        # Check if examining a point of interest
        area_pois = area_data.get("points_of_interest", [])
        
        for poi_id in area_pois:
            # In a real game, would have full POI data
            poi_name = poi_id.replace("_", " ").title()
            
            if target.lower() in poi_name.lower() or poi_id.lower() == target.lower():
                poi_descriptions = {
                    "old_well": "An old stone well. Villagers come here to draw water.",
                    "notice_board": "A wooden board with notices and wanted posters.",
                    "large_oak": "An enormous oak tree that must be hundreds of years old.",
                    "small_shrine": "A small shrine dedicated to a local nature deity.",
                    "village_fountain": "A stone fountain in the center of the square.",
                    "marketplace": "Stalls set up for trading goods.",
                    "broken_statue": "A crumbling statue of a forgotten hero.",
                    "sealed_door": "A mysterious door sealed with ancient runes."
                }
                
                poi_description = poi_descriptions.get(poi_id, f"You see a {poi_name}.")
                
                return {
                    "success": True,
                    "message": poi_description,
                    "target_type": "poi",
                    "target_id": poi_id,
                    "target_name": poi_name
                }
        
        # Check if examining the area itself
        if target.lower() in current_area.lower() or target.lower() == "area" or target.lower() == "around":
            return {
                "success": True,
                "message": area_data.get("description", f"You look around {current_area}."),
                "target_type": "area",
                "target_id": current_area,
                "target_name": area_data.get("name", current_area)
            }
        
        # No valid target found
        return {
            "success": False,
            "message": f"You don't see anything called {target} here."
        }
    
    def _handle_with_ai_gm(self, player_id: str, parsed_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle complex or ambiguous commands through the AI GM.
        This is a fallback for commands that don't fit cleanly into other categories.
        """
        player = self.player_states[player_id]
        command_text = parsed_command.get("original_text", "")
        
        # Log that we're using the AI GM
        self.log_system("AI_GM", "PROCESSING_COMMAND", {
            "player_id": player_id,
            "command": command_text
        })
        
        # Prepare context for AI GM
        context = {
            "player": player,
            "location": {
                "region": self.world_state["regions"].get(player["location"]["region"], {}),
                "area": self.world_state["regions"].get(player["location"]["region"], {})
                        .get("areas", {}).get(player["location"]["area"], {})
            },
            "npcs": [
                self.npc_states.get(npc_id) for npc_id in 
                self.world_state["regions"].get(player["location"]["region"], {})
                .get("areas", {}).get(player["location"]["area"], {}).get("npcs", [])
            ],
            "time": self.world_state["current_time"],
            "weather": self.world_state["weather"]
        }
        
        # Ask AI GM to process the command
        ai_gm_response = self.ai_gm.process_player_input(command_text, context)
        
        # Log AI GM response
        self.log_system("AI_GM", "RESPONSE_GENERATED", {
            "player_id": player_id,
            "response": ai_gm_response
        })
        
        # In a real implementation, we would also process any game state updates
        # returned by the AI GM. For now, we'll just return the response.
        return {
            "success": True,
            "message": ai_gm_response.get("response", "The AI GM doesn't know how to respond to that."),
            "handled_by_ai_gm": True
        }
    
    def _check_quest_stage_completion(self, player_id: str, action_type: str, target_id: str) -> None:
        """Check if an action completes a quest stage."""
        player = self.player_states[player_id]
        
        # Loop through active quests
        for quest_id in player["quests"]["active"]:
            quest = self.quest_states.get(quest_id)
            if not quest:
                continue
            
            # Check each quest stage
            for stage in quest["stages"]:
                if stage["completed"]:
                    continue
                
                # Check for talk_to_elder stage
                if stage["id"] == "talk_to_elder" and action_type == "dialogue" and target_id == "village_elder":
                    stage["completed"] = True
                    
                    # Activate next stage
                    next_stage_index = quest["stages"].index(stage) + 1
                    if next_stage_index < len(quest["stages"]):
                        quest["stages"][next_stage_index]["active"] = True
                    
                    # Log quest stage completion
                    self.log_system("QUEST_SYSTEM", "QUEST_STAGE_COMPLETED", {
                        "player_id": player_id,
                        "quest_id": quest_id,
                        "stage_id": stage["id"]
                    })
                
                # Check for return_to_elder stage
                elif stage["id"] == "return_to_elder" and action_type == "dialogue" and target_id == "village_elder":
                    # Check if previous stages are complete
                    prev_stages_complete = True
                    for prev_stage in quest["stages"]:
                        if prev_stage["id"] == stage["id"]:
                            break
                        if not prev_stage["completed"]:
                            prev_stages_complete = False
                            break
                    
                    if prev_stages_complete:
                        stage["completed"] = True
                        
                        # Log quest stage completion
                        self.log_system("QUEST_SYSTEM", "QUEST_STAGE_COMPLETED", {
                            "player_id": player_id,
                            "quest_id": quest_id,
                            "stage_id": stage["id"]
                        })
    
    def _update_game_state(self, player_id: str, action_type: str, action_result: Dict[str, Any]) -> None:
        """Update global game state based on player actions and results."""
        # This would implement more complex state updates and world changes
        # For now, we'll just log the update
        self.log_system("GAME_STATE", "STATE_UPDATED", {
            "player_id": player_id,
            "action_type": action_type,
            "result_summary": {k: v for k, v in action_result.items() if k != "message" and not isinstance(v, dict)}
        })
    
    def _generate_player_response(self, player_id: str, action_type: str, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a response to send back to the player."""
        # Create a basic response with the result message
        response = {
            "message": action_result.get("message", "Something happened."),
            "success": action_result.get("success", False)
        }
        
        # Add relevant game state info depending on action type
        player = self.player_states[player_id]
        
        # Add player status to all responses
        response["player_status"] = {
            "health": player["health"],
            "level": player["level"],
            "experience": player["experience"],
            "location": player["location"]
        }
        
        # Add magic status if player has magic
        if "magic" in player:
            magic_user = self.magic_system.magic_users.get(player["magic"]["profile_id"])
            if magic_user:
                response["player_status"]["magic"] = {
                    "mana_current": magic_user.mana_current,
                    "mana_max": magic_user.mana_max
                }
        
        # Add action-specific data
        if action_type == "movement":
            # Add description of new area
            area_id = player["location"]["area"]
            region_id = player["location"]["region"]
            area_data = self.world_state["regions"].get(region_id, {}).get("areas", {}).get(area_id, {})
            
            response["location"] = {
                "name": area_data.get("name", area_id),
                "description": area_data.get("description", ""),
                "npcs_present": [
                    self.npc_states[npc_id]["name"] 
                    for npc_id in area_data.get("npcs", []) 
                    if npc_id in self.npc_states
                ],
                "exits": area_data.get("connected_areas", [])
            }
            
            # Add encounter data if one was triggered
            if action_result.get("encounter"):
                response["encounter"] = action_result["encounter"]
        
        elif action_type == "combat":
            # Add combat status if in combat
            if "active_combat" in player:
                response["combat_status"] = {
                    "in_combat": True,
                    "enemies": [
                        {
                            "name": enemy["name"],
                            "health_current": enemy["health"]["current"],
                            "health_max": enemy["health"]["max"]
                        }
                        for enemy in player["active_combat"]["enemies"]
                    ],
                    "round": player["active_combat"]["round"],
                    "player_turn": player["active_combat"]["player_turn"]
                }
            else:
                response["combat_status"] = {
                    "in_combat": False
                }
                
                # Add loot if combat was just completed
                if action_result.get("combat_completed") and action_result.get("loot_gained"):
                    response["loot_gained"] = action_result["loot_gained"]
        
        elif action_type == "quest":
            # Add quest status for view action
            if "active_quests" in action_result:
                response["quests"] = {
                    "active": action_result["active_quests"],
                    "completed": action_result["completed_quests"]
                }
            
            # Add rewards for complete action
            if "rewards" in action_result:
                response["rewards"] = action_result["rewards"]
        
        return response
    
    def run_end_to_end_scenario(self) -> Dict[str, Any]:
        """
        Run a complete end-to-end scenario to demonstrate system integration.
        
        This function simulates a series of player commands that exercise
        multiple game systems working together.
        """
        print("=== Running End-to-End Scenario ===")
        
        # 1. Initialize the world and a player
        self.initialize_world()
        player_id = "test_player"
        player = self.initialize_player(player_id, "Aventus")
        
        print(f"Initialized world and player: {player['name']}")
        
        # 2. Examine the starting area
        response = self.process_player_command(player_id, "look around")
        print(f"\nPlayer looks around: {response['message']}")
        
        # 3. Talk to the village elder
        response = self.process_player_command(player_id, "talk to elder")
        print(f"\nPlayer talks to elder: {response['message']}")
        
        # 4. Ask about quests
        response = self.process_player_command(player_id, "ask elder about quest")
        print(f"\nPlayer asks about quests: {response['message']}")
        
        # 5. Accept the quest
        response = self.process_player_command(player_id, "accept quest village_troubles")
        print(f"\nPlayer accepts quest: {response['message']}")
        
        # 6. Check quest log
        response = self.process_player_command(player_id, "view quests")
        print(f"\nPlayer checks quest log: {response['message']}")
        print(f"Active quests: {len(response.get('quests', {}).get('active', []))}")
        
        # 7. Move to the forest path
        response = self.process_player_command(player_id, "go to forest path")
        print(f"\nPlayer moves to forest path: {response['message']}")
        
        # 8. Encounter wolves (part of the quest)
        if "encounter" in response and response["encounter"]["name"] == "Wolf Pack":
            print(f"Encountered: {response['encounter']['description']}")
        else:
            # Manually trigger wolf encounter for demonstration
            print("\nTriggering wolf encounter...")
            encounter = self._check_for_encounter(player_id, "forest_path")
            if encounter and encounter["name"] == "Wolf Pack":
                print(f"Encountered: {encounter['description']}")
        
        # 9. Fight the wolves
        response = self.process_player_command(player_id, "attack wolf")
        print(f"\nPlayer attacks wolf: {response['message']}")
        
        # 10. Continue combat until wolves are defeated
        while response.get("combat_status", {}).get("in_combat", False):
            if response.get("combat_status", {}).get("player_turn", True):
                # Use magic in combat
                response = self.process_player_command(player_id, "cast arcane bolt at wolf")
                print(f"\nPlayer casts spell: {response['message']}")
            else:
                # Let enemy take turn and then continue attacking
                response = self.process_player_command(player_id, "attack wolf")
                print(f"\nPlayer attacks wolf: {response['message']}")
        
        # 11. Check inventory after combat
        response = self.process_player_command(player_id, "check inventory")
        print(f"\nPlayer checks inventory: {response['message']}")
        
        # 12. Return to the elder to complete the quest
        response = self.process_player_command(player_id, "go to crossroads")
        print(f"\nPlayer returns to crossroads: {response['message']}")
        
        response = self.process_player_command(player_id, "talk to elder")
        print(f"\nPlayer talks to elder: {response['message']}")
        
        # 13. Complete the quest
        response = self.process_player_command(player_id, "complete quest village_troubles")
        
        # If the quest isn't ready to complete, the wolves stage might not be updated
        if not response["success"]:
            print(f"\nCannot complete quest yet: {response['message']}")
            
            # Manually update quest stage for demonstration
            quest = self.quest_states["village_troubles"]
            for stage in quest["stages"]:
                if stage["id"] == "kill_wolves":
                    stage["target"]["current"] = stage["target"]["count"]
                    stage["completed"] = True
                elif stage["id"] == "return_to_elder":
                    stage["active"] = True
            
            # Try completing again
            response = self.process_player_command(player_id, "complete quest village_troubles")
        
        print(f"\nPlayer completes quest: {response['message']}")
        if "rewards" in response:
            print(f"Quest rewards: {response['rewards']}")
        
        # 14. Go to the village to try crafting
        response = self.process_player_command(player_id, "go to village square")
        print(f"\nPlayer goes to village square: {response['message']}")
        
        # 15. Talk to the blacksmith
        response = self.process_player_command(player_id, "talk to blacksmith")
        print(f"\nPlayer talks to blacksmith: {response['message']}")
        
        # 16. Check available recipes
        response = self.process_player_command(player_id, "check crafting recipes")
        print(f"\nPlayer checks crafting recipes: {response['message']}")
        
        # 17. Craft an item if possible
        if response.get("recipes"):
            recipe = response["recipes"][0]
            response = self.process_player_command(player_id, f"craft {recipe['id']}")
            print(f"\nPlayer tries to craft {recipe['name']}: {response['message']}")
        
        # 18. Check final player state
        player = self.player_states[player_id]
        print("\nFinal player state:")
        print(f"  Level: {player['level']}")
        print(f"  Health: {player['health']['current']}/{player['health']['max']}")
        print(f"  Gold: {player['gold']}")
        print(f"  Location: {player['location']['area']} in {player['location']['region']}")
        print(f"  Active quests: {player['quests']['active']}")
        print(f"  Completed quests: {player['quests']['completed']}")
        
        print("\n=== End-to-End Scenario Complete ===")
        
        # Return the logs for analysis
        return {
            "action_log": self.action_log,
            "system_log": self.system_log,
            "final_player_state": player
        }


def run_scenario():
    """Run the end-to-end scenario and display results."""
    # Create scenario runner
    runner = EndToEndScenarioRunner(debug=True)
    
    # Run the scenario
    scenario_results = runner.run_end_to_end_scenario()
    
    # Return the results
    return scenario_results


if __name__ == "__main__":
    run_scenario()