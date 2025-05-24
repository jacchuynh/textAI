from enum import Enum, auto
from datetime import datetime
from typing import Dict, List, Any, Optional

# Assuming world_state.py is in the same directory (narrative_engine_0_1_2b)
from .world_state import world_state_manager, PoliticalStability, EconomicStatus 
# Assuming event_bus.py is in the parent directory relative to narrative_engine_0_1_2b
from ..event_bus import event_bus, GameEvent, EventType
# Assuming branch_definitions.py is in the same directory
from .branch_definitions import detailed_branches as default_branch_definitions


class NarrativeBranchType(Enum):
    """Types of narrative branches available in the system."""
    DOMAIN_OPPORTUNITY = auto()  # Special opportunities based on domain expertise
    DOMAIN_CHALLENGE = auto()    # Challenges that target specific domains
    DOMAIN_GROWTH = auto()       # Growth opportunities for underdeveloped domains
    CHARACTER_ARC = auto()       # Character development branches
    RELATIONSHIP = auto()        # Relationship development branches
    WORLD_IMPACT = auto()        # World-changing branches
    WORLD_STATE_RESPONSE = auto() # NEW: Branches specifically responding to world state


class DomainNarrativeDirector:
    """
    Director that guides narrative based on character domains, progression, and world state.
    """
    
    def __init__(self, branch_definitions: Optional[Dict] = None):
        """
        Initialize the domain narrative director.
        
        Args:
            branch_definitions: Optional pre-loaded branch definitions. Uses default if None.
        """
        self.event_bus = event_bus # Use the global instance
        self.active_branches: Dict[str, Dict[str, Any]] = {}
        # Use provided definitions or the default from branch_definitions.py
        self.branch_definitions: Dict[str, Dict[str, Any]] = branch_definitions if branch_definitions is not None else default_branch_definitions
        self.domain_themes: Dict[tuple, Dict[str, Any]] = self._initialize_domain_themes()
        
        self._register_event_handlers()
    
    def _initialize_domain_themes(self) -> Dict:
        # (Your existing _initialize_domain_themes code can remain largely the same)
        # Consider if domain_themes themselves could have world_state_conditions
        return {
            ("STRENGTH", "ENDURANCE"): { # Assuming DomainType enum/str are used consistently
                "name": "Physical Dominance",
                "description": "A narrative focused on physical challenges and triumphs.",
                "recommended_tones": ["HEROIC", "GRIM"],
                "branch_opportunities": [ # These are templates for branches
                    {
                        "name": "Trial of Might", # This name should match a key in self.branch_definitions
                        "type": NarrativeBranchType.DOMAIN_CHALLENGE,
                        "description": "A physical challenge that tests the limits of strength and endurance.",
                        "min_domain_value": 3 # Min value for *both* domains in the pair to trigger generally
                    },
                ]
            },
            ("INTELLECT", "PERCEPTION"): {
                "name": "Keen Observer",
                "description": "A narrative focused on mysteries, clues, and discoveries.",
                "recommended_tones": ["MYSTERIOUS", "NEUTRAL"],
                "branch_opportunities": [
                    {
                        "name": "Hidden Truths", # Example, should be in branch_definitions
                        "type": NarrativeBranchType.DOMAIN_OPPORTUNITY,
                        "description": "Discover secrets that others have missed.",
                        "min_domain_value": 2
                    }
                ]
            },
        }
    
    def _register_event_handlers(self):
        self.event_bus.subscribe(EventType.DOMAIN_INCREASED, self._handle_domain_increase)
        # self.event_bus.subscribe(EventType.CHARACTER_CREATED, self._handle_character_created) # Placeholder
        self.event_bus.subscribe(EventType.DOMAIN_CHECK, self._handle_domain_check)
        # NEW: Potentially subscribe to WORLD_STATE_CHANGED to proactively check for new opportunities
        self.event_bus.subscribe(EventType.WORLD_STATE_CHANGED, self._handle_world_state_change)


    def _check_world_state_conditions(self, branch_template: Dict[str, Any]) -> bool:
        """Checks if the world state conditions for a branch are met."""
        conditions = branch_template.get("world_state_conditions")
        if not conditions:
            return True # No conditions, so it's always met

        current_world_snapshot = world_state_manager.get_current_state_summary()

        for key, value_or_list in conditions.items():
            if key == "political_stability":
                if current_world_snapshot["political_stability"] not in value_or_list: return False
            elif key == "economic_status":
                if current_world_snapshot["economic_status"] not in value_or_list: return False
            elif key == "current_season":
                if current_world_snapshot["current_season"] not in value_or_list: return False
            elif key == "active_global_threats": # Check if any listed threat is active
                if any(threat in current_world_snapshot["active_global_threats"] for threat in value_or_list): return False
            elif key == "not_active_global_threats": # Check if any listed threat should NOT be active
                if any(threat in current_world_snapshot["active_global_threats"] for threat in value_or_list): return False
            # Add more conditions as needed (e.g., specific world_properties)
            elif key in current_world_snapshot["world_properties"]:
                 if current_world_snapshot["world_properties"][key] not in value_or_list: return False
            elif key.startswith("min_") and key.split("_",1)[1] in current_world_snapshot["world_properties"]:
                prop_name = key.split("_",1)[1]
                if current_world_snapshot["world_properties"][prop_name] < value_or_list : return False
            elif key.startswith("max_") and key.split("_",1)[1] in current_world_snapshot["world_properties"]:
                prop_name = key.split("_",1)[1]
                if current_world_snapshot["world_properties"][prop_name] > value_or_list : return False

        return True

    def _handle_world_state_change(self, event: GameEvent):
        """
        When world state changes, re-evaluate if new narrative branches might become available
        for relevant characters (e.g., the player or key NPCs).
        This is a simplified example; you'd need a way to get current player/character IDs.
        """
        # This is a placeholder for identifying characters to check for.
        # In a real game, you'd iterate over players or key NPCs.
        character_id_to_check = "player_character_id" # Example
        
        # We need character's current domains to check effectively
        # This part remains a challenge without direct character data access
        character_domains = self._get_character_domains_for_event(character_id_to_check, event.game_id)
        if not character_domains:
            return

        potential_branches = []
        # Check all defined branches
        for branch_name, branch_template in self.branch_definitions.items():
            domain_name = branch_template.get("domain") # Primary domain for the branch
            min_value = branch_template.get("min_domain_value", 0)
            
            # Check domain requirement (if any specified for the branch directly)
            domain_ok = True
            if domain_name and domain_name in character_domains:
                if character_domains[domain_name] < min_value:
                    domain_ok = False
            elif domain_name: # Domain specified but character doesn't have it or it's not in our mock data
                domain_ok = False 

            if domain_ok and self._check_world_state_conditions(branch_template):
                # Avoid re-notifying if branch is already active or recently offered
                # This logic would need more robust tracking of offered branches
                is_new_opportunity = True # Simplified
                if is_new_opportunity:
                    potential_branches.append(branch_template)
        
        for branch in potential_branches:
            self._publish_branch_available_event(character_id_to_check, branch, event.game_id, "world_state_change")

    def _publish_branch_available_event(self, character_id: str, branch_template: Dict, game_id: Optional[str], trigger_reason: str):
        """Helper to publish NARRATIVE_BRANCH_AVAILABLE event."""
        branch_type_enum = branch_template.get("type", NarrativeBranchType.DOMAIN_OPPORTUNITY)
        branch_type_name = branch_type_enum.name if hasattr(branch_type_enum, "name") else str(branch_type_enum)

        event_context = {
            "branch_name": branch_template["name"],
            "branch_type": branch_type_name,
            "description": branch_template["description"],
            "trigger_reason": trigger_reason, # e.g., "domain_increase", "world_state_change"
        }
        if branch_template.get("domain"):
            event_context["domain_name"] = branch_template["domain"]

        branch_event = self._create_event(
            type=EventType.NARRATIVE_BRANCH_AVAILABLE, # Ensure this EventType exists
            actor=character_id,
            context=event_context,
            tags=["narrative", "opportunity", trigger_reason] + ([branch_template["domain"].lower()] if branch_template.get("domain") else []),
            game_id=game_id
        )
        self.event_bus.publish(branch_event)


    def _handle_domain_increase(self, event: GameEvent):
        character_id = event.actor
        domain_name = event.context.get("domain") # Assuming this is str, like "STRENGTH"
        new_value = event.context.get("new_value", 0)
        
        potential_branches = self._find_potential_branches(character_id, domain_name, new_value, event.game_id)
        
        for branch in potential_branches:
            self._publish_branch_available_event(character_id, branch, event.game_id, "domain_increase")
            
    def _get_character_domains_for_event(self, character_id: str, game_id: Optional[str]) -> Optional[Dict[str, int]]:
        """
        Placeholder/Simplified: Get character domains.
        In a real system, this would query a character management service or database.
        For now, it uses the existing placeholder logic but should be improved.
        """
        # This is a conceptual placeholder. The original _get_character_domains
        # simulates an event request. A real implementation is needed.
        # For testing, you could return a mock dictionary:
        # print(f"DomainNarrativeDirector: Requesting domains for {character_id} (Game: {game_id}) - NEEDS PROPER IMPLEMENTATION")
        if character_id == "player_character_id": # Example
            return {"STRENGTH": 3, "ENDURANCE": 2, "INTELLECT": 4, "PERCEPTION": 3, "AWARENESS": 2} 
        return None


    def _find_potential_branches(self, character_id: str, domain_name_changed: str, domain_value_new: int, game_id: Optional[str]) -> List[Dict[str, Any]]:
        """
        Find potential narrative branches for a character based on domain and world state.
        """
        character_domains = self._get_character_domains_for_event(character_id, game_id)
        if not character_domains:
            return []
            
        potential_branches_templates: List[Dict[str, Any]] = []
        
        # 1. Check single-domain branches from main branch_definitions
        for branch_name, branch_template in self.branch_definitions.items():
            # Check primary domain requirement
            if branch_template.get("domain") == domain_name_changed and domain_value_new >= branch_template.get("min_domain_value", 0):
                if self._check_world_state_conditions(branch_template):
                    potential_branches_templates.append(branch_template)
            # Check if this branch could be unlocked by any domain increase if it has no specific primary domain
            elif not branch_template.get("domain") and domain_value_new >= branch_template.get("min_domain_value", 0):
                 if self._check_world_state_conditions(branch_template):
                    potential_branches_templates.append(branch_template)


        # 2. Check domain_themes (multi-domain thematic opportunities)
        for domain_pair, theme in self.domain_themes.items():
            if domain_name_changed in domain_pair:
                # This theme is relevant to the changed domain
                other_domain_in_pair = domain_pair[0] if domain_pair[1] == domain_name_changed else domain_pair[1]
                
                if other_domain_in_pair in character_domains:
                    other_value = character_domains[other_domain_in_pair]
                    
                    for themed_branch_opportunity_template in theme["branch_opportunities"]:
                        # Themed opportunities might refer to full branch defs by name
                        full_branch_template = self.branch_definitions.get(themed_branch_opportunity_template["name"])
                        if not full_branch_template:
                            # Or it could be a self-contained mini-template
                            full_branch_template = themed_branch_opportunity_template 

                        min_val_for_theme = themed_branch_opportunity_template.get("min_domain_value", 0) # Min value for *each* domain in pair

                        # Check if both domains in the pair meet the general threshold for this theme opportunity
                        # AND if the specific branch (if different) meets its own domain reqs
                        primary_domain_of_branch = full_branch_template.get("domain")
                        min_val_of_branch = full_branch_template.get("min_domain_value", 0)

                        domain_match_for_branch = False
                        if primary_domain_of_branch:
                            if primary_domain_of_branch == domain_name_changed and domain_value_new >= min_val_of_branch:
                                domain_match_for_branch = True
                            elif primary_domain_of_branch == other_domain_in_pair and other_value >= min_val_of_branch:
                                 domain_match_for_branch = True
                            elif primary_domain_of_branch in character_domains and character_domains[primary_domain_of_branch] >= min_val_of_branch:
                                domain_match_for_branch = True
                        else: # Branch has no specific primary domain, theme pairing is enough
                            domain_match_for_branch = True


                        if (domain_value_new >= min_val_for_theme and 
                            other_value >= min_val_for_theme and
                            domain_match_for_branch and
                            self._check_world_state_conditions(full_branch_template)):
                            if full_branch_template not in potential_branches_templates: # Avoid duplicates
                                potential_branches_templates.append(full_branch_template)
        
        return potential_branches_templates

    def _create_event(self, type: EventType, actor: str, context: Optional[Dict[str, Any]] = None, 
                      tags: Optional[List[str]] = None, effects: Optional[List[Dict[str, Any]]] = None, 
                      game_id: Optional[str] = None) -> GameEvent:
        """
        Create a GameEvent object.
        """
        # Ensure EventType.NARRATIVE_BRANCH_AVAILABLE and others are defined in event_bus.py
        # For custom string types, handle them as per GameEvent constructor
        actual_event_type = type
        if isinstance(type, str): # If a string is passed, try to convert to EventType
            try:
                actual_event_type = EventType.from_string(type)
            except ValueError:
                 # Keep as string if not a standard EventType, GameEvent handles this
                 pass

        return GameEvent(
            type=actual_event_type,
            actor=actor,
            context=context or {},
            metadata={}, # Add if needed
            tags=tags or [],
            effects=effects or [],
            game_id=game_id
        )

    # --- Other methods like _handle_character_created, _handle_domain_check,
    # --- create_narrative_branch, _update_branch_progress, etc., remain largely the same
    # --- but ensure they use the _create_event method for consistency.

    def _handle_character_created(self, event: GameEvent):
        # Placeholder: could pre-evaluate initial branches based on starting domains and world state
        pass
    
    def _handle_domain_check(self, event: GameEvent):
        character_id = event.actor
        # Ensure domain_name is correctly extracted if it's an enum or string
        domain_name_from_event = event.context.get("domain")
        if isinstance(domain_name_from_event, Enum): # If domain is an Enum in context
            domain_name = domain_name_from_event.value 
        else: # Assume it's a string
            domain_name = domain_name_from_event

        success = event.context.get("success", False)
        
        related_branches = [
            branch_id for branch_id, branch_data in self.active_branches.items()
            if branch_data.get("character_id") == character_id and
               branch_data.get("required_domain") == domain_name and # Ensure this matches format
               not branch_data.get("completed", False)
        ]
        
        for branch_id in related_branches:
            self._update_branch_progress(branch_id, success)

    def create_narrative_branch(self, branch_template: Dict[str, Any], character_id: str, game_id: Optional[str] = None) -> Optional[str]:
        branch_name_to_check = branch_template.get("name")
        if not branch_name_to_check:
            print(f"Error: Branch template missing name: {branch_template}")
            return None
        
        # Ensure the chosen branch template is still valid under current world conditions
        # (Could have changed since being offered)
        full_template_def = self.branch_definitions.get(branch_name_to_check, branch_template) # Get full def if available
        if not self._check_world_state_conditions(full_template_def):
            print(f"World state conditions for branch '{branch_name_to_check}' no longer met.")
            # Optionally publish an event "NARRATIVE_BRANCH_UNAVAILABLE"
            return None

        import uuid
        branch_id = str(uuid.uuid4())
        
        branch_type_enum = full_template_def.get("type", NarrativeBranchType.DOMAIN_OPPORTUNITY)
        
        branch = {
            "id": branch_id,
            "name": full_template_def["name"],
            "type": branch_type_enum, # Store the enum member itself
            "description": full_template_def["description"],
            "character_id": character_id,
            "required_domain": full_template_def.get("domain"), # Primary domain
            "progress": 0,
            "completed": False,
            "failed": False,
            "created_at": datetime.utcnow().isoformat(),
            "implementation": full_template_def.get("implementation", {}),
            "stages": full_template_def.get("stages", []),
            "current_stage_index": 0, # Use index for stages list
            "duration": full_template_def.get("duration"),
            "game_id": game_id
        }
        
        self.active_branches[branch_id] = branch
        
        event = self._create_event(
            type=EventType.NARRATIVE_BRANCH_CREATED, # Ensure EventType exists
            actor=character_id,
            context={
                "branch_id": branch_id,
                "branch_name": branch["name"],
                "branch_type": branch["type"].name, # Use enum name for context string
                "description": branch["description"]
            },
            tags=["narrative", "branch", "created"],
            effects=[{"type": "narrative_branch_started", "branch_id": branch_id}],
            game_id=game_id
        )
        self.event_bus.publish(event)
        return branch_id

    def _update_branch_progress(self, branch_id: str, success: bool):
        if branch_id not in self.active_branches:
            return None
            
        branch = self.active_branches[branch_id]
        if branch["completed"] or branch["failed"]:
            return branch["completed"] # True if completed, False if failed

        branch["progress"] += 20 if success else -10
        branch["progress"] = max(0, min(100, branch["progress"]))
        
        # Update stage
        stages = branch.get("stages", [])
        if stages:
            new_stage_index = branch["current_stage_index"]
            for i, stage_def in enumerate(stages):
                if branch["progress"] >= stage_def.get("progress", 0):
                    new_stage_index = i
            if new_stage_index != branch["current_stage_index"]:
                branch["current_stage_index"] = new_stage_index
                # Publish stage change event if needed
                # print(f"Branch {branch_id} advanced to stage {new_stage_index}: {stages[new_stage_index]['description']}")

        if branch["progress"] >= 100:
            branch["completed"] = True
            self._handle_branch_completion(branch_id)
            return True
        
        # Simplified failure condition for now
        if branch["progress"] <= 0 : # Could add max failed attempts
            # For now, one severe setback (progress <=0) can lead to failure if not recovered
            # More complex logic for 'failed_attempts' could be added here
            # branch["failed"] = True
            # self._handle_branch_failure(branch_id)
            # return False
            pass # Let it linger at 0 progress, might need specific actions to fail it.

        return None # Still in progress

    def _handle_branch_completion(self, branch_id: str):
        branch = self.active_branches[branch_id]
        character_id = branch.get("character_id")
        game_id = branch.get("game_id")
        
        event = self._create_event(
            type=EventType.NARRATIVE_BRANCH_COMPLETED, # Ensure EventType exists
            actor=character_id,
            context={
                "branch_id": branch_id,
                "branch_name": branch["name"],
                "branch_type": branch["type"].name,
                "description": branch["description"]
            },
            tags=["narrative", "completion"],
            effects=[{"type": "narrative_completion", "branch_id": branch_id, "branch_name": branch["name"]}],
            game_id=game_id
        )
        self.event_bus.publish(event)
        
        # Handle unlocks
        # Find the original template for this branch to check for "unlocks"
        original_template = self.branch_definitions.get(branch["name"]) or self._find_branch_template_in_themes(branch["name"])

        if original_template and "unlocks" in original_template:
            for unlock_name in original_template["unlocks"]:
                unlocked_template = self.branch_definitions.get(unlock_name) or self._find_branch_template_in_themes(unlock_name)
                if unlocked_template and self._check_world_state_conditions(unlocked_template):
                     # Check if character meets domain requirements for the unlocked branch
                    char_domains = self._get_character_domains_for_event(character_id, game_id)
                    domain_ok = True
                    if unlocked_template.get("domain") and char_domains:
                        if char_domains.get(unlocked_template["domain"], 0) < unlocked_template.get("min_domain_value",0):
                            domain_ok = False
                    elif unlocked_template.get("domain"): # domain required but char_domains not available
                        domain_ok = False 
                    
                    if domain_ok:
                        self._publish_branch_available_event(character_id, unlocked_template, game_id, f"unlocked_by_{branch['name']}")


    def _find_branch_template_in_themes(self, branch_name: str) -> Optional[Dict[str, Any]]:
        """Helper to find a branch template referenced within domain_themes."""
        for theme_data in self.domain_themes.values():
            for opp_template in theme_data.get("branch_opportunities", []):
                if opp_template.get("name") == branch_name:
                    # This might be a mini-template or a reference to a full definition
                    return self.branch_definitions.get(branch_name, opp_template)
        return None

    # ... (other methods like _handle_branch_failure, get_active_branches_for_character, etc.)
    # Ensure EventTypes like NARRATIVE_BRANCH_FAILED, NARRATIVE_BRANCH_AVAILABLE are defined in event_bus.py

    def get_branch_stage_description(self, branch_id: str) -> Optional[str]:
        """Gets the description of the current stage of a branch."""
        branch = self.active_branches.get(branch_id)
        if not branch:
            return None
        
        stages = branch.get("stages", [])
        current_stage_idx = branch.get("current_stage_index", 0)
        
        if stages and 0 <= current_stage_idx < len(stages):
            return stages[current_stage_idx].get("description")
        return branch.get("description") # Fallback to main description