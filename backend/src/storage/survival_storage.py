from typing import Dict, List, Optional
import json
import os
from datetime import datetime

from ..shared.survival_models import SurvivalState, CampaignSurvivalConfig


class SurvivalStorage:
    """Storage service for survival system data"""
    
    def __init__(self, data_dir: str = None):
        """Initialize the storage service
        
        Args:
            data_dir: Directory to store data files
        """
        # Default data directory
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "../data/survival")
            
        self.data_dir = data_dir
        self.survival_states_dir = os.path.join(data_dir, "states")
        self.campaign_configs_dir = os.path.join(data_dir, "campaigns")
        
        # Ensure directories exist
        os.makedirs(self.survival_states_dir, exist_ok=True)
        os.makedirs(self.campaign_configs_dir, exist_ok=True)
    
    def save_survival_state(self, state: SurvivalState) -> bool:
        """Save a survival state to storage
        
        Args:
            state: Survival state to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to dict for serialization
            data = state.model_dump()
            
            # Set updated timestamp
            data["updated_at"] = datetime.now().isoformat()
            
            # Save to file
            file_path = os.path.join(self.survival_states_dir, f"{state.character_id}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving survival state: {e}")
            return False
    
    def load_survival_state(self, character_id: str) -> Optional[SurvivalState]:
        """Load a survival state from storage
        
        Args:
            character_id: ID of the character
            
        Returns:
            Loaded survival state or None if not found
        """
        try:
            file_path = os.path.join(self.survival_states_dir, f"{character_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return None
                
            # Load from file
            with open(file_path, "r") as f:
                data = json.load(f)
                
            # Convert timestamp strings back to datetime
            if "updated_at" in data and isinstance(data["updated_at"], str):
                data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                
            # Parse state history timestamps
            if "state_history" in data and isinstance(data["state_history"], list):
                for entry in data["state_history"]:
                    if "timestamp" in entry and isinstance(entry["timestamp"], str):
                        entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
            
            # Create SurvivalState object
            return SurvivalState(**data)
        except Exception as e:
            print(f"Error loading survival state: {e}")
            return None
    
    def save_campaign_config(self, config: CampaignSurvivalConfig) -> bool:
        """Save a campaign survival configuration to storage
        
        Args:
            config: Campaign configuration to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert to dict for serialization
            data = config.model_dump()
            
            # Save to file
            file_path = os.path.join(self.campaign_configs_dir, f"{config.campaign_id}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
                
            return True
        except Exception as e:
            print(f"Error saving campaign config: {e}")
            return False
    
    def load_campaign_config(self, campaign_id: str) -> Optional[CampaignSurvivalConfig]:
        """Load a campaign survival configuration from storage
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            Loaded campaign configuration or None if not found
        """
        try:
            file_path = os.path.join(self.campaign_configs_dir, f"{campaign_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return None
                
            # Load from file
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Create CampaignSurvivalConfig object
            return CampaignSurvivalConfig(**data)
        except Exception as e:
            print(f"Error loading campaign config: {e}")
            return None
    
    def delete_survival_state(self, character_id: str) -> bool:
        """Delete a survival state from storage
        
        Args:
            character_id: ID of the character
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.survival_states_dir, f"{character_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return False
                
            # Delete file
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting survival state: {e}")
            return False
    
    def delete_campaign_config(self, campaign_id: str) -> bool:
        """Delete a campaign survival configuration from storage
        
        Args:
            campaign_id: ID of the campaign
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.campaign_configs_dir, f"{campaign_id}.json")
            
            # Check if file exists
            if not os.path.exists(file_path):
                return False
                
            # Delete file
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting campaign config: {e}")
            return False
    
    def list_survival_states(self) -> List[str]:
        """List all character IDs with saved survival states
        
        Returns:
            List of character IDs
        """
        try:
            # Get all JSON files in the states directory
            files = [f for f in os.listdir(self.survival_states_dir) if f.endswith(".json")]
            
            # Extract character IDs from filenames
            character_ids = [os.path.splitext(f)[0] for f in files]
            
            return character_ids
        except Exception as e:
            print(f"Error listing survival states: {e}")
            return []
    
    def list_campaign_configs(self) -> List[str]:
        """List all campaign IDs with saved configurations
        
        Returns:
            List of campaign IDs
        """
        try:
            # Get all JSON files in the campaigns directory
            files = [f for f in os.listdir(self.campaign_configs_dir) if f.endswith(".json")]
            
            # Extract campaign IDs from filenames
            campaign_ids = [os.path.splitext(f)[0] for f in files]
            
            return campaign_ids
        except Exception as e:
            print(f"Error listing campaign configs: {e}")
            return []
