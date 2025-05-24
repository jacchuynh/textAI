# Assuming event_bus.py is in the parent directory or accessible
# from ..event_bus import EventType, GameEvent # If you need to type hint or use EventType directly

class NarrativeBranchChoiceHandler:
    def __init__(self, director, event_bus):
        """
        Manages narrative opportunities available to characters, for an AI GM to leverage.

        Args:
            director: An instance of DomainNarrativeDirector.
            event_bus: The game's event bus.
        """
        self.director = director
        self.event_bus = event_bus

        # Stores the full context of NARRATIVE_BRANCH_AVAILABLE events.
        # Key: opportunity_id (e.g., the ID of the NARRATIVE_BRANCH_AVAILABLE event itself)
        # Value: dict (context of the event, including branch_name, char_id, etc.)
        self.available_opportunities: dict[str, dict] = {}

        # Tracks which opportunities are currently considered "active" or "hinted" for a character.
        # Key: char_id
        # Value: list[opportunity_id]
        self.pending_opportunities_for_character: dict[str, list[str]] = {}

    def handle_narrative_branch_available(self, event): # event is a GameEvent
        """
        Called when a NARRATIVE_BRANCH_AVAILABLE event occurs.
        Stores the details of this potential narrative path.
        """
        char_id = event.actor
        branch_name = event.context.get("branch_name")
        opportunity_id = event.id  # Use the unique ID of the event itself

        if not branch_name:
            print(f"NBCH_Warning: NARRATIVE_BRANCH_AVAILABLE event (ID: {opportunity_id}) for actor {char_id} is missing 'branch_name' in context.")
            return

        # Store the full context, ensuring we know which character it was for.
        self.available_opportunities[opportunity_id] = event.context.copy()
        self.available_opportunities[opportunity_id]['_source_event_id_'] = opportunity_id
        self.available_opportunities[opportunity_id]['_character_id_'] = char_id
        self.available_opportunities[opportunity_id]['_timestamp_offered_'] = event.timestamp

        if char_id not in self.pending_opportunities_for_character:
            self.pending_opportunities_for_character[char_id] = []
        
        if opportunity_id not in self.pending_opportunities_for_character[char_id]:
            self.pending_opportunities_for_character[char_id].append(opportunity_id)
            # print(f"NBCH_Info: Opportunity '{branch_name}' (ID: {opportunity_id}) now pending for character {char_id}.")
        # else:
            # print(f"NBCH_Info: Opportunity '{branch_name}' (ID: {opportunity_id}) was already pending for character {char_id}.")


    def get_pending_opportunities_for_gm(self, char_id: str) -> list[dict]:
        """
        Provides a list of currently pending narrative opportunities for a character.
        This information is intended to be used by the AI GM to understand available plot hooks.

        Each item in the list is a dictionary containing the context of the
        NARRATIVE_BRANCH_AVAILABLE event (including 'branch_name', 'description', 
        '_source_event_id_' as opportunity_id, etc.).
        """
        opportunities_info = []
        if char_id in self.pending_opportunities_for_character:
            for opportunity_id in self.pending_opportunities_for_character[char_id]:
                if opportunity_id in self.available_opportunities:
                    # Return a copy of the opportunity context
                    info = self.available_opportunities[opportunity_id].copy()
                    opportunities_info.append(info)
        return opportunities_info

    def attempt_to_initiate_branch_via_gm(self, opportunity_id: str, char_id: str, game_id: str | None = None) -> tuple[bool, str, str | None]:
        """
        Called by the AI GM (or its controlling system) when it determines, based on player
        interaction, that the player intends to pursue a specific narrative opportunity.

        Args:
            opportunity_id: The unique ID of the NARRATIVE_BRANCH_AVAILABLE event that represents
                            the opportunity being pursued.
            char_id: The ID of the character pursuing the branch.
            game_id: The ID of the current game session.

        Returns:
            A tuple: (success_flag, message_for_gm, new_runtime_branch_id_or_None)
                     The message_for_gm should inform the AI GM's narration.
        """
        opportunity_context = self.available_opportunities.get(opportunity_id)

        if not opportunity_context:
            return False, f"GM_ATTEMPT_FAIL: Opportunity ID '{opportunity_id}' not found or is no longer available.", None

        # Validate that this opportunity was indeed for the given character and is still pending
        if opportunity_context.get('_character_id_') != char_id:
            return False, f"GM_ATTEMPT_FAIL: Opportunity ID '{opportunity_id}' was not for character '{char_id}'.", None
        
        if char_id not in self.pending_opportunities_for_character or \
           opportunity_id not in self.pending_opportunities_for_character[char_id]:
            # This could happen if it was already pursued or timed out.
            return False, f"GM_ATTEMPT_FAIL: Opportunity ID '{opportunity_id}' is not currently pending for character '{char_id}'.", None

        branch_name = opportunity_context.get("branch_name")
        if not branch_name:
            self._clear_opportunity(char_id, opportunity_id, "invalid_data")
            return False, f"GM_ATTEMPT_FAIL: Critical error - Branch name missing in context for opportunity '{opportunity_id}'.", None

        # Retrieve the full, current branch template from the director's definitions
        branch_template = self.director.branch_definitions.get(branch_name)
        if not branch_template:
            # Compatibility for director possibly having themes separately
            if hasattr(self.director, '_find_branch_template_in_themes') and callable(getattr(self.director, '_find_branch_template_in_themes')):
                 branch_template = self.director._find_branch_template_in_themes(branch_name)
            if not branch_template:
                self._clear_opportunity(char_id, opportunity_id, "template_not_found")
                return False, f"GM_ATTEMPT_FAIL: Branch template for '{branch_name}' (Opportunity ID: {opportunity_id}) not found in director's definitions.", None
        
        # Call the director to attempt to create/start the narrative branch.
        # The director is responsible for final checks (WorldState, character conditions, exclusivity).
        new_runtime_branch_id = self.director.create_narrative_branch(branch_template, char_id, game_id)

        if new_runtime_branch_id:
            # Success! The branch was created by the director.
            self._clear_opportunity(char_id, opportunity_id, "pursued_and_started")
            # The AI GM will use this success to narrate the player's actions leading into the branch.
            return True, f"GM_ATTEMPT_SUCCESS: Branch '{branch_name}' (Opportunity ID: {opportunity_id}) was successfully initiated.", new_runtime_branch_id
        else:
            # Failure: The director did not create the branch.
            # Reasons could include: WorldState changed, character no longer meets requirements, exclusivity conflict.
            # The director's `create_narrative_branch` should ideally log specific reasons if possible.
            self._clear_opportunity(char_id, opportunity_id, "rejected_by_director")
            return False, f"GM_ATTEMPT_FAIL: Branch '{branch_name}' (Opportunity ID: {opportunity_id}) could not be initiated. Conditions may have changed, or it's no longer valid as per director.", None

    def _clear_opportunity(self, char_id: str, opportunity_id: str, status: str):
        """
        Internal helper to remove an opportunity from pending lists and the main store,
        marking its final status.
        """
        if char_id in self.pending_opportunities_for_character and \
           opportunity_id in self.pending_opportunities_for_character[char_id]:
            self.pending_opportunities_for_character[char_id].remove(opportunity_id)
            if not self.pending_opportunities_for_character[char_id]:
                del self.pending_opportunities_for_character[char_id]
        
        # Remove from the main available_opportunities store once processed.
        # You might choose to move it to an archive or just mark status if you need history.
        if opportunity_id in self.available_opportunities:
            # self.available_opportunities[opportunity_id]['_final_status_'] = status
            # self.available_opportunities[opportunity_id]['_status_update_time_'] = datetime.utcnow().isoformat()
            del self.available_opportunities[opportunity_id] # Simpler: just delete
            # print(f"NBCH_Info: Opportunity ID '{opportunity_id}' for char '{char_id}' cleared with status: {status}.")


    def mark_opportunity_as_ignored_or_declined(self, opportunity_id: str, char_id: str):
        """
        Called by the AI GM if it determines the player is not interested in or has
        implicitly declined a previously hinted opportunity. This prevents the GM
        from repeatedly offering the same stale hook.
        """
        if char_id in self.pending_opportunities_for_character and \
           opportunity_id in self.pending_opportunities_for_character[char_id]:
            self._clear_opportunity(char_id, opportunity_id, "player_declined_or_ignored")
            # print(f"NBCH_Info: Opportunity ID '{opportunity_id}' for char '{char_id}' marked as declined/ignored by player.")
            return True
        return False

    def cleanup_stale_opportunities(self, char_id: str, current_valid_opportunity_ids: set[str]):
        """
        (Optional utility)
        If the director re-evaluates all available branches for a character and provides a
        set of currently valid opportunity_ids, this method can remove any pending ones
        that are no longer in that valid set (e.g., due to major WorldState changes
        that invalidated them wholesale before player interaction).
        """
        if char_id in self.pending_opportunities_for_character:
            stale_ids = [opp_id for opp_id in self.pending_opportunities_for_character[char_id] if opp_id not in current_valid_opportunity_ids]
            for stale_id in stale_ids:
                self._clear_opportunity(char_id, stale_id, "invalidated_by_system_refresh")
                # print(f"NBCH_Info: Stale opportunity ID '{stale_id}' for char '{char_id}' cleaned up.")
