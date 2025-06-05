"""
Character creation service for TextRealms.
"""
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import uuid

from ..shared.character_creation_models import (
    CharacterCreationPreset,
    CharacterCreationSession,
    DefaultPresets
)
from ..shared.models import Character, DomainType, GrowthTier
from ..shared.survival_models import SurvivalState, SurvivalStateUpdate
from .survival_integration import SurvivalIntegration
from .survival_system import SurvivalSystem


class CharacterCreationService:
    """Service for handling character creation logic"""
    
    def __init__(
        self, 
        storage=None, 
        survival_system: Optional[SurvivalSystem] = None,
        survival_integration: Optional[SurvivalIntegration] = None
    ):
        """Initialize the character creation service
        
        Args:
            storage: Storage service for persistence
            survival_system: Survival system for creating survival states
            survival_integration: Survival integration for linking characters to survival
        """
        self.storage = storage
        self.survival_system = survival_system
        self.survival_integration = survival_integration
        
        # In-memory cache
        self.presets: Dict[str, CharacterCreationPreset] = {}
        self.sessions: Dict[str, CharacterCreationSession] = {}
        
        # Initialize with default presets
        self._load_default_presets()
    
    def _load_default_presets(self):
        """Load the default character creation presets"""
        for preset in DefaultPresets.all_presets():
            self.presets[preset.id] = preset
            
            # Persist if storage is available
            if self.storage:
                self.storage.save_character_creation_preset(preset)
    
    def get_presets(self) -> List[CharacterCreationPreset]:
        """Get all available character creation presets
        
        Returns:
            List of character creation presets
        """
        presets = list(self.presets.values())
        
        # If we have storage, load any additional presets
        if self.storage:
            stored_presets = self.storage.load_all_character_creation_presets()
            
            # Add any presets not in memory
            for preset in stored_presets:
                if preset.id not in self.presets:
                    self.presets[preset.id] = preset
                    presets.append(preset)
        
        return presets
    
    def get_preset(self, preset_id: str) -> Optional[CharacterCreationPreset]:
        """Get a specific character creation preset
        
        Args:
            preset_id: ID of the preset to get
            
        Returns:
            The character creation preset or None if not found
        """
        if preset_id in self.presets:
            return self.presets[preset_id]
        
        # Try to load from storage
        if self.storage:
            preset = self.storage.load_character_creation_preset(preset_id)
            if preset:
                self.presets[preset_id] = preset
                return preset
        
        return None
    
    def create_preset(self, preset: CharacterCreationPreset) -> CharacterCreationPreset:
        """Create a new character creation preset
        
        Args:
            preset: Preset to create
            
        Returns:
            The created preset
        """
        self.presets[preset.id] = preset
        
        # Persist if storage is available
        if self.storage:
            self.storage.save_character_creation_preset(preset)
        
        return preset
    
    def create_session(self, preset_id: str, user_id: Optional[str] = None) -> CharacterCreationSession:
        """Create a new character creation session
        
        Args:
            preset_id: ID of the preset to use
            user_id: Optional user ID to associate with the session
            
        Returns:
            The created session
        """
        # Get the preset
        preset = self.get_preset(preset_id)
        if not preset:
            raise ValueError(f"Preset with ID {preset_id} not found")
        
        # Create the session
        session = CharacterCreationSession(
            preset_id=preset_id,
            preset=preset,
            user_id=user_id
        )
        
        # Initialize domain allocations with minimum values
        for domain in DomainType:
            session.domain_allocations[domain] = preset.min_per_domain
        
        # Calculate initial derived stats
        session.calculate_derived_stats(preset)
        
        # Store the session
        self.sessions[session.id] = session
        
        # Persist if storage is available
        if self.storage:
            self.storage.save_character_creation_session(session)
        
        return session
    
    def get_session(self, session_id: str) -> Optional[CharacterCreationSession]:
        """Get a character creation session
        
        Args:
            session_id: ID of the session to get
            
        Returns:
            The character creation session or None if not found
        """
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Try to load from storage
        if self.storage:
            session = self.storage.load_character_creation_session(session_id)
            if session:
                # Make sure we have the preset
                if not session.preset and session.preset_id:
                    session.preset = self.get_preset(session.preset_id)
                
                self.sessions[session_id] = session
                return session
        
        return None
    
    def update_domain_allocations(
        self, 
        session_id: str, 
        allocations: Dict[DomainType, int]
    ) -> CharacterCreationSession:
        """Update domain allocations for a character creation session
        
        Args:
            session_id: ID of the session to update
            allocations: New domain allocations
            
        Returns:
            The updated session
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        
        preset = session.preset or self.get_preset(session.preset_id)
        if not preset:
            raise ValueError(f"Preset for session {session_id} not found")
        
        # Update allocations
        session.domain_allocations.update(allocations)
        
        # Recalculate derived stats
        session.calculate_derived_stats(preset)
        
        # Update timestamp
        session.updated_at = datetime.now()
        
        # Persist changes
        if self.storage:
            self.storage.save_character_creation_session(session)
        
        return session
    
    def update_tag_allocations(
        self, 
        session_id: str, 
        allocations: Dict[str, int]
    ) -> CharacterCreationSession:
        """Update tag allocations for a character creation session
        
        Args:
            session_id: ID of the session to update
            allocations: New tag allocations
            
        Returns:
            The updated session
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        
        # Update allocations
        session.tag_allocations.update(allocations)
        
        # Update timestamp
        session.updated_at = datetime.now()
        
        # Persist changes
        if self.storage:
            self.storage.save_character_creation_session(session)
        
        return session
    
    def update_character_details(
        self,
        session_id: str,
        name: Optional[str] = None,
        background: Optional[str] = None,
        character_class: Optional[str] = None,
        traits: Optional[List[str]] = None
    ) -> CharacterCreationSession:
        """Update character details for a character creation session
        
        Args:
            session_id: ID of the session to update
            name: Optional character name
            background: Optional character background
            character_class: Optional character class
            traits: Optional list of character traits
            
        Returns:
            The updated session
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        
        # Update fields if provided
        if name is not None:
            session.character_name = name
        
        if background is not None:
            session.character_background = background
        
        if character_class is not None:
            session.character_class = character_class
        
        if traits is not None:
            session.chosen_traits = traits
        
        # Update timestamp
        session.updated_at = datetime.now()
        
        # Persist changes
        if self.storage:
            self.storage.save_character_creation_session(session)
        
        return session
    
    def validate_session(self, session_id: str) -> List[str]:
        """Validate a character creation session
        
        Args:
            session_id: ID of the session to validate
            
        Returns:
            List of validation errors, empty if valid
        """
        session = self.get_session(session_id)
        if not session:
            return ["Session not found"]
        
        preset = session.preset or self.get_preset(session.preset_id)
        if not preset:
            return ["Preset not found"]
        
        # Validate the session
        session.validate(preset)
        
        return session.validation_errors
    
    def finalize_character(self, session_id: str) -> Dict[str, Any]:
        """Finalize character creation and create the character
        
        Args:
            session_id: ID of the session to finalize
            
        Returns:
            Dictionary with created character and associated data
        """
        session = self.get_session(session_id)
        if not session:
            raise ValueError(f"Session with ID {session_id} not found")
        
        preset = session.preset or self.get_preset(session.preset_id)
        if not preset:
            raise ValueError(f"Preset for session {session_id} not found")
        
        # Validate the session
        errors = self.validate_session(session_id)
        if errors:
            raise ValueError(f"Character creation session is not valid: {', '.join(errors)}")
        
        # Create the character
        character_id = str(uuid.uuid4())
        
        # 1. Create basic character data
        character = Character(
            id=character_id,
            name=session.character_name,
            domains=session.domain_allocations,
            tags=session.tag_allocations,
            traits=session.chosen_traits + preset.bonus_traits,
            background=session.character_background,
            character_class=session.character_class,
            creation_preset=preset.name,
            growth_tier=preset.starting_tier,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 2. Create survival state with custom base health
        survival_state = None
        if self.survival_integration:
            # Use integration for full initialization
            survival_state = self.survival_integration.initialize_character_survival(
                character_id=character_id,
                base_health=preset.base_health
            )
        elif self.survival_system:
            # Use survival system directly
            body_value = session.domain_allocations.get(DomainType.BODY, 0)
            survival_state = self.survival_system.create_survival_state(
                character_id=character_id,
                base_health=preset.base_health,
                body_value=body_value
            )
        
        # 3. Add inventory items based on preset
        inventory = preset.starting_items.copy()
        
        # 4. Add currency
        currency = preset.starting_currency
        
        # 5. Persist all data
        if self.storage:
            self.storage.save_character(character)
        
        # Return the created data
        result = {
            "character": character,
            "survival_state": survival_state.model_dump() if survival_state else None,
            "inventory": inventory,
            "currency": currency,
            "preset_used": preset.model_dump()
        }
        
        return result
