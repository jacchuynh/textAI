"""
Authority and Consequence Service

This module provides functionality for managing authority actions, investigations,
and consequences for illicit activities in the game world.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.src.business.models.illicit_models import (
    InvestigationStatus, CrimeType, ConsequenceType,
    AuthorityInvestigation, RegionalHeatLevel
)
from backend.src.business.models.illicit_db_models import (
    DBAuthorityInvestigation, DBRegionalHeatLevel,
    DBPlayerCriminalRecord, DBBlackMarketTransaction
)
from backend.src.business.services.black_market_operations_service import BlackMarketOperationsService
from backend.src.business.crud import (
    get_business, update_business
)

logger = logging.getLogger(__name__)

class AuthorityConsequenceService:
    """Service for authority actions and consequences."""
    
    def __init__(self):
        """Initialize the authority and consequence service."""
        self.logger = logging.getLogger("AuthorityConsequenceService")
        self.black_market_service = BlackMarketOperationsService()
    
    def calculate_detection_risk(
        self,
        db: Session,
        player_id: str,
        location_id: str,
        action_details: Dict[str, Any]
    ) -> float:
        """
        Calculate the risk of detection for an illicit action.
        
        Args:
            db: Database session
            player_id: ID of the player
            location_id: ID of the location
            action_details: Details of the action
            
        Returns:
            Detection risk as a float (0.0-1.0)
        """
        # Get player criminal record
        criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
        
        # Get regional heat level
        heat_level = self.black_market_service._get_or_create_heat_level(db, location_id)
        
        # Base risk based on action type
        action_type = action_details.get("action_type", "unknown")
        
        base_risk_by_type = {
            "buy_illicit_item": 0.1,
            "sell_illicit_item": 0.15,
            "craft_illicit_item": 0.15,
            "smuggle_goods": 0.2,
            "fence_stolen_goods": 0.15,
            "offer_illicit_service": 0.2,
            "money_laundering": 0.25,
            "bribe_official": 0.2,
            "infiltrate_location": 0.3,
            "black_market_transaction": 0.15
        }
        
        base_risk = base_risk_by_type.get(action_type, 0.2)
        
        # Risk modifiers
        risk_modifiers = 0.0
        
        # Regional heat significantly affects risk
        risk_modifiers += heat_level.current_heat / 20  # Up to +0.5 for maximum heat
        
        # Authority presence affects risk
        risk_modifiers += heat_level.authority_presence / 25  # Up to +0.4
        
        # Player notoriety affects risk in complex ways
        if criminal_record.notoriety > 7.0:
            # Very notorious criminals attract more attention
            risk_modifiers += 0.15
        elif criminal_record.notoriety > 4.0:
            # Moderately notorious criminals know how to operate
            risk_modifiers -= 0.05
        elif criminal_record.notoriety > 2.0:
            # Some criminal experience helps
            risk_modifiers -= 0.1
        else:
            # Novices make more mistakes
            risk_modifiers += 0.1
            
        # Player being suspected in the region increases risk
        if location_id in criminal_record.suspected_by_regions:
            risk_modifiers += 0.2
            
        # Active investigations in the region increase risk
        active_investigations = heat_level.active_investigations
        if active_investigations > 3:
            risk_modifiers += 0.2
        elif active_investigations > 0:
            risk_modifiers += 0.1
            
        # Specific action parameters affect risk
        value = action_details.get("value", 0)
        if isinstance(value, (int, float)) and value > 0:
            if value > 500:
                risk_modifiers += 0.15
            elif value > 200:
                risk_modifiers += 0.07
            elif value > 50:
                risk_modifiers += 0.03
                
        quantity = action_details.get("quantity", 0)
        if isinstance(quantity, (int, float)) and quantity > 0:
            if quantity > 10:
                risk_modifiers += 0.15
            elif quantity > 5:
                risk_modifiers += 0.07
            elif quantity > 1:
                risk_modifiers += 0.02
                
        # Time of day affects risk (if provided)
        time_of_day = action_details.get("time_of_day", "")
        if time_of_day == "day":
            risk_modifiers += 0.1
        elif time_of_day == "night":
            risk_modifiers -= 0.1
            
        # Disguise reduces risk
        if criminal_record.current_disguise_effectiveness > 0:
            risk_modifiers -= criminal_record.current_disguise_effectiveness / 2  # Up to -0.5
            
        # Security measures (if any)
        security_level = action_details.get("security_level", 0)
        if security_level > 0:
            risk_modifiers -= security_level / 40  # Up to -0.25
            
        # Calculate final risk with all modifiers
        final_risk = max(0.01, min(0.99, base_risk + risk_modifiers))
        
        return final_risk
    
    def trigger_investigation(
        self,
        db: Session,
        location_id: str,
        target_id: str,
        target_type: str,
        suspicion_cause: str,
        initial_evidence_level: float = 0.1
    ) -> Dict[str, Any]:
        """
        Trigger a new authority investigation.
        
        Args:
            db: Database session
            location_id: ID of the location
            target_id: ID of the target (player, business, or location)
            target_type: Type of the target ("player", "business", "location")
            suspicion_cause: Cause of suspicion
            initial_evidence_level: Initial evidence level (0.0-1.0)
            
        Returns:
            Dictionary with investigation details
        """
        # Validate target type
        if target_type not in ["player", "business", "location"]:
            raise ValueError(f"Invalid target type: {target_type}")
            
        # Get regional heat level
        heat_level = self.black_market_service._get_or_create_heat_level(db, location_id)
        
        # Check if there's already an active investigation for this target
        existing_investigation = db.query(DBAuthorityInvestigation).filter(
            DBAuthorityInvestigation.target_id == target_id,
            DBAuthorityInvestigation.target_type == target_type,
            DBAuthorityInvestigation.status.in_([
                InvestigationStatus.INITIAL.value,
                InvestigationStatus.ONGOING.value,
                InvestigationStatus.GATHERING_EVIDENCE.value,
                InvestigationStatus.PREPARING_RAID.value
            ])
        ).first()
        
        if existing_investigation:
            # Update existing investigation with new evidence
            existing_investigation.evidence_level = min(
                1.0, 
                existing_investigation.evidence_level + (initial_evidence_level / 2)
            )
            
            # Add progress note
            progress_notes = existing_investigation.progress_notes.copy()
            progress_notes.append({
                "date": datetime.utcnow().isoformat(),
                "note": f"Additional suspicion: {suspicion_cause}",
                "evidence_added": initial_evidence_level / 2
            })
            existing_investigation.progress_notes = progress_notes
            
            db.commit()
            
            return {
                "success": True,
                "message": "Added evidence to existing investigation",
                "investigation_id": existing_investigation.id,
                "target_id": target_id,
                "target_type": target_type,
                "current_evidence_level": existing_investigation.evidence_level,
                "status": existing_investigation.status
            }
        
        # Create new investigation
        
        # Generate investigator NPC (would use NPC system in a real implementation)
        investigator_id = f"investigator_{str(uuid4())[:8]}"
        
        # Determine initial status
        initial_status = InvestigationStatus.INITIAL.value
        if initial_evidence_level > 0.3:
            # If there's significant initial evidence, start more aggressively
            initial_status = InvestigationStatus.ONGOING.value
            
        # Estimate completion date based on complexity
        complexity_factor = 1.0
        if target_type == "player":
            complexity_factor = 1.5  # Players are harder to investigate
        elif target_type == "business":
            complexity_factor = 1.2  # Businesses are moderately complex
            
        # Authority presence speeds up investigations
        speed_factor = heat_level.authority_presence / 5  # 1-2 range
        
        # Calculate expected duration in days
        base_days = random.randint(3, 7)
        expected_days = base_days * complexity_factor / speed_factor
        
        expected_completion = datetime.utcnow() + timedelta(days=expected_days)
        
        # Create investigation
        investigation = DBAuthorityInvestigation(
            id=str(uuid4()),
            target_id=target_id,
            target_type=target_type,
            investigator_npc_id=investigator_id,
            region_id=location_id,
            start_date=datetime.utcnow(),
            status=initial_status,
            evidence_level=initial_evidence_level,
            suspicion_cause=suspicion_cause,
            progress_notes=[{
                "date": datetime.utcnow().isoformat(),
                "note": f"Investigation started due to: {suspicion_cause}",
                "initial_evidence": initial_evidence_level
            }],
            expected_completion_date=expected_completion
        )
        
        db.add(investigation)
        
        # Update regional heat level
        self.black_market_service._update_heat_level(
            db,
            location_id,
            {
                "active_investigations": heat_level.active_investigations + 1,
                "current_heat": min(10.0, heat_level.current_heat + 0.3)  # Investigations raise heat
            }
        )
        
        # If the target is a player, update their criminal record
        if target_type == "player":
            criminal_record = self.black_market_service._get_or_create_criminal_record(db, target_id)
            if location_id not in criminal_record.suspected_by_regions:
                suspected_regions = criminal_record.suspected_by_regions.copy()
                suspected_regions.append(location_id)
                
                self.black_market_service._update_criminal_record(
                    db,
                    target_id,
                    {"suspected_by_regions": suspected_regions}
                )
        
        db.commit()
        
        return {
            "success": True,
            "message": "New investigation started",
            "investigation_id": investigation.id,
            "target_id": target_id,
            "target_type": target_type,
            "investigator_id": investigator_id,
            "evidence_level": initial_evidence_level,
            "status": initial_status,
            "expected_completion_date": expected_completion.isoformat()
        }
    
    def update_investigation(
        self,
        db: Session,
        investigation_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing investigation.
        
        Args:
            db: Database session
            investigation_id: ID of the investigation
            updates: Updates to apply
            
        Returns:
            Dictionary with updated investigation details
        """
        # Get the investigation
        investigation = db.query(DBAuthorityInvestigation).filter(
            DBAuthorityInvestigation.id == investigation_id
        ).first()
        
        if not investigation:
            raise ValueError(f"Investigation {investigation_id} not found")
            
        # Apply updates
        if "status" in updates and updates["status"] in [status.value for status in InvestigationStatus]:
            investigation.status = updates["status"]
            
        if "evidence_level" in updates and isinstance(updates["evidence_level"], float):
            investigation.evidence_level = max(0.0, min(1.0, updates["evidence_level"]))
            
        if "expected_completion_date" in updates and isinstance(updates["expected_completion_date"], (str, datetime)):
            if isinstance(updates["expected_completion_date"], str):
                try:
                    investigation.expected_completion_date = datetime.fromisoformat(updates["expected_completion_date"])
                except ValueError:
                    pass  # Invalid date format, ignore
            else:
                investigation.expected_completion_date = updates["expected_completion_date"]
                
        if "progress_note" in updates and isinstance(updates["progress_note"], str):
            progress_notes = investigation.progress_notes.copy()
            progress_notes.append({
                "date": datetime.utcnow().isoformat(),
                "note": updates["progress_note"]
            })
            investigation.progress_notes = progress_notes
            
        # Special case for concluding investigation
        if "conclude" in updates and updates["conclude"]:
            investigation.status = InvestigationStatus.CONCLUDED.value
            
            # Update regional heat level
            heat_level = self.black_market_service._get_or_create_heat_level(db, investigation.region_id)
            self.black_market_service._update_heat_level(
                db,
                investigation.region_id,
                {"active_investigations": max(0, heat_level.active_investigations - 1)}
            )
            
        db.commit()
        
        return {
            "success": True,
            "investigation_id": investigation.id,
            "target_id": investigation.target_id,
            "target_type": investigation.target_type,
            "current_status": investigation.status,
            "current_evidence_level": investigation.evidence_level,
            "expected_completion_date": investigation.expected_completion_date.isoformat() if investigation.expected_completion_date else None,
            "progress_notes_count": len(investigation.progress_notes)
        }
    
    def simulate_patrol_encounter(
        self,
        db: Session,
        player_id: str,
        location_id: str,
        encounter_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simulate an encounter with a patrol in a location.
        
        Args:
            db: Database session
            player_id: ID of the player
            location_id: ID of the location
            encounter_context: Optional context for the encounter
            
        Returns:
            Dictionary with encounter results
        """
        # Get player criminal record
        criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
        
        # Get regional heat level
        heat_level = self.black_market_service._get_or_create_heat_level(db, location_id)
        
        # Determine if patrol is present
        patrol_chance = 0.1  # Base chance
        
        # Heat and authority presence affect patrol chance
        patrol_chance += heat_level.current_heat / 20  # Up to +0.5
        patrol_chance += heat_level.authority_presence / 20  # Up to +0.5
        
        # Cap patrol chance
        patrol_chance = max(0.05, min(0.9, patrol_chance))
        
        # Roll for patrol presence
        patrol_present = random.random() <= patrol_chance
        
        if not patrol_present:
            return {
                "patrol_present": False,
                "message": "No patrols encountered in the area."
            }
            
        # Patrol is present - determine suspicion level
        suspicion_base = 0.1  # Base suspicion
        
        # Player notoriety affects suspicion
        if criminal_record.notoriety > 7.0:
            suspicion_base += 0.3  # Well-known criminal
        elif criminal_record.notoriety > 4.0:
            suspicion_base += 0.15  # Known criminal
        elif criminal_record.notoriety > 2.0:
            suspicion_base += 0.05  # Minor criminal reputation
            
        # Being suspected in this region greatly increases suspicion
        if location_id in criminal_record.suspected_by_regions:
            suspicion_base += 0.3
            
        # Disguise reduces suspicion
        if criminal_record.current_disguise_effectiveness > 0:
            suspicion_base -= criminal_record.current_disguise_effectiveness / 2
            
        # Context factors
        if encounter_context:
            # Carrying illicit items
            if encounter_context.get("carrying_illicit_items", False):
                suspicion_base += 0.2
                
            # Suspicious behavior
            if encounter_context.get("suspicious_behavior", False):
                suspicion_base += 0.15
                
            # Time of day
            if encounter_context.get("time_of_day", "") == "night":
                suspicion_base += 0.1
                
            # Near black market location
            if encounter_context.get("near_black_market", False):
                suspicion_base += 0.2
                
            # With known criminals
            if encounter_context.get("with_criminals", False):
                suspicion_base += 0.25
                
        # Final suspicion level
        suspicion_level = max(0.0, min(1.0, suspicion_base))
        
        # Determine patrol reaction based on suspicion
        if suspicion_level < 0.3:
            # Low suspicion - patrol ignores player
            return {
                "patrol_present": True,
                "suspicion_level": suspicion_level,
                "reaction": "ignore",
                "message": "A patrol passes by but pays you no attention."
            }
            
        elif suspicion_level < 0.6:
            # Moderate suspicion - patrol questions player
            # Update last patrol time
            self.black_market_service._update_heat_level(
                db,
                location_id,
                {"last_patrol_time": datetime.utcnow()}
            )
            
            return {
                "patrol_present": True,
                "suspicion_level": suspicion_level,
                "reaction": "question",
                "message": "A patrol stops you for questioning. They seem somewhat suspicious."
            }
            
        else:
            # High suspicion - patrol searches player
            # Update last patrol time
            self.black_market_service._update_heat_level(
                db,
                location_id,
                {"last_patrol_time": datetime.utcnow()}
            )
            
            # Determine if player is caught with contraband
            caught = False
            contraband_items = []
            
            if encounter_context and encounter_context.get("carrying_illicit_items", False):
                items = encounter_context.get("illicit_items", [])
                
                # Calculate chance of discovery for each item
                for item in items:
                    # More suspicious patrols search more thoroughly
                    discovery_chance = suspicion_level * 0.8
                    
                    # Hidden items are harder to find
                    if item.get("hidden", False):
                        discovery_chance *= 0.5
                        
                    if random.random() <= discovery_chance:
                        caught = True
                        contraband_items.append(item)
            
            if caught:
                # Player caught with contraband
                # Update criminal record
                known_crimes = criminal_record.known_crimes.copy()
                known_crimes.append({
                    "date": datetime.utcnow().isoformat(),
                    "type": "possession_of_contraband",
                    "location_id": location_id,
                    "details": {
                        "items": contraband_items,
                        "patrol_encounter": True
                    }
                })
                
                self.black_market_service._update_criminal_record(
                    db,
                    player_id,
                    {
                        "notoriety": criminal_record.notoriety + 0.5,
                        "times_caught": criminal_record.times_caught + 1,
                        "known_crimes": known_crimes,
                        "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [location_id]))
                    }
                )
                
                # Increase regional heat
                self.black_market_service._update_heat_level(
                    db,
                    location_id,
                    {
                        "current_heat": min(10.0, heat_level.current_heat + 0.5),
                        "recent_incidents": heat_level.recent_incidents + 1
                    }
                )
                
                # Determine consequences
                consequence = self._determine_contraband_consequence(contraband_items)
                
                # Start investigation if serious contraband
                if consequence["severity"] == "moderate" or consequence["severity"] == "severe":
                    self.trigger_investigation(
                        db,
                        location_id,
                        player_id,
                        "player",
                        f"Caught with {len(contraband_items)} contraband items",
                        0.3
                    )
                
                return {
                    "patrol_present": True,
                    "suspicion_level": suspicion_level,
                    "reaction": "search",
                    "caught": True,
                    "contraband_items": contraband_items,
                    "consequence": consequence,
                    "message": f"A patrol searches you and discovers contraband! {consequence['details']}"
                }
            else:
                # Nothing found, but player now suspected
                if location_id not in criminal_record.suspected_by_regions:
                    suspected_regions = criminal_record.suspected_by_regions.copy()
                    suspected_regions.append(location_id)
                    
                    self.black_market_service._update_criminal_record(
                        db,
                        player_id,
                        {"suspected_by_regions": suspected_regions}
                    )
                    
                return {
                    "patrol_present": True,
                    "suspicion_level": suspicion_level,
                    "reaction": "search",
                    "caught": False,
                    "message": "A patrol searches you thoroughly but finds nothing incriminating. They remain suspicious."
                }
    
    def apply_penalty_for_crime(
        self,
        db: Session,
        player_id: str,
        crime_details: Dict[str, Any],
        severity_level: str
    ) -> Dict[str, Any]:
        """
        Apply a penalty for a committed crime.
        
        Args:
            db: Database session
            player_id: ID of the player
            crime_details: Details of the crime
            severity_level: Severity level ("minor", "moderate", "severe")
            
        Returns:
            Dictionary with penalty application results
        """
        # Get player criminal record
        criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
        
        # Validate severity level
        if severity_level not in ["minor", "moderate", "severe"]:
            raise ValueError(f"Invalid severity level: {severity_level}")
            
        # Extract crime details
        crime_type = crime_details.get("type", "unknown")
        location_id = crime_details.get("location_id", "unknown")
        business_id = crime_details.get("business_id")
        value = crime_details.get("value", 0.0)
        
        # Determine penalty based on severity and crime type
        penalties = []
        
        # Fine is almost always applied
        fine_amount = 0.0
        
        if severity_level == "minor":
            # Minor penalties
            if crime_type in ["possession_of_contraband", "selling_illegal_goods"]:
                fine_amount = max(20.0, value * 0.5)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Fine of {fine_amount} gold for minor {crime_type}"
                })
            elif crime_type in ["smuggling", "illicit_crafting"]:
                fine_amount = max(50.0, value * 0.7)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Fine of {fine_amount} gold for minor {crime_type}"
                })
            else:
                # Generic minor penalty
                fine_amount = max(25.0, value * 0.6)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Fine of {fine_amount} gold for minor offense"
                })
                
            # Always confiscate illegal items
            if crime_details.get("items", []):
                penalties.append({
                    "type": ConsequenceType.CONFISCATION.value,
                    "items": crime_details["items"],
                    "details": f"Confiscation of {len(crime_details['items'])} illegal items"
                })
                
        elif severity_level == "moderate":
            # Moderate penalties
            if crime_type in ["possession_of_contraband", "selling_illegal_goods"]:
                fine_amount = max(100.0, value * 1.2)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Fine of {fine_amount} gold for {crime_type}"
                })
                
                # Confiscation of items
                if crime_details.get("items", []):
                    penalties.append({
                        "type": ConsequenceType.CONFISCATION.value,
                        "items": crime_details["items"],
                        "details": f"Confiscation of {len(crime_details['items'])} illegal items"
                    })
                    
                # Business restrictions if applicable
                if business_id:
                    penalties.append({
                        "type": ConsequenceType.LICENSE_REVOCATION.value,
                        "duration_days": 7,
                        "details": "Business license temporarily suspended for 7 days"
                    })
                    
            elif crime_type in ["smuggling", "money_laundering", "illicit_crafting"]:
                fine_amount = max(200.0, value * 1.5)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Fine of {fine_amount} gold for {crime_type}"
                })
                
                # Confiscation
                if crime_details.get("items", []) or crime_details.get("goods", {}):
                    items = crime_details.get("items", [])
                    goods = crime_details.get("goods", {})
                    
                    penalties.append({
                        "type": ConsequenceType.CONFISCATION.value,
                        "items": items,
                        "goods": goods,
                        "details": "Confiscation of all illegal goods"
                    })
                    
                # Possible short imprisonment
                if random.random() < 0.3:  # 30% chance
                    imprisonment_days = random.randint(1, 3)
                    penalties.append({
                        "type": ConsequenceType.IMPRISONMENT.value,
                        "duration_days": imprisonment_days,
                        "details": f"Imprisonment for {imprisonment_days} days"
                    })
                    
            else:
                # Generic moderate penalty
                fine_amount = max(150.0, value * 1.3)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Fine of {fine_amount} gold for moderate offense"
                })
                
        else:  # severe
            # Severe penalties
            if crime_type in ["possession_of_contraband", "selling_illegal_goods"]:
                fine_amount = max(300.0, value * 2.0)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Heavy fine of {fine_amount} gold for {crime_type}"
                })
                
                # Confiscation
                if crime_details.get("items", []):
                    penalties.append({
                        "type": ConsequenceType.CONFISCATION.value,
                        "items": crime_details["items"],
                        "details": f"Confiscation of {len(crime_details['items'])} illegal items"
                    })
                    
                # Business consequences
                if business_id:
                    penalties.append({
                        "type": ConsequenceType.BUSINESS_SHUTDOWN.value,
                        "duration_days": random.randint(14, 30),
                        "details": "Business shut down by authorities"
                    })
                    
                # Imprisonment
                imprisonment_days = random.randint(5, 15)
                penalties.append({
                    "type": ConsequenceType.IMPRISONMENT.value,
                    "duration_days": imprisonment_days,
                    "details": f"Imprisonment for {imprisonment_days} days"
                })
                
            elif crime_type in ["smuggling", "money_laundering"]:
                fine_amount = max(500.0, value * 2.5)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Heavy fine of {fine_amount} gold for {crime_type}"
                })
                
                # Asset seizure
                seizure_amount = max(200.0, value * 1.0)
                penalties.append({
                    "type": ConsequenceType.ASSET_SEIZURE.value,
                    "amount": seizure_amount,
                    "details": f"Seizure of assets worth {seizure_amount} gold"
                })
                
                # Imprisonment
                imprisonment_days = random.randint(10, 30)
                penalties.append({
                    "type": ConsequenceType.IMPRISONMENT.value,
                    "duration_days": imprisonment_days,
                    "details": f"Imprisonment for {imprisonment_days} days"
                })
                
                # Reputation damage
                penalties.append({
                    "type": ConsequenceType.REPUTATION_DAMAGE.value,
                    "factions": ["town_guard", "merchants_guild"],
                    "amount": -3.0,
                    "details": "Severe reputation damage with lawful factions"
                })
                
                # Bounty
                bounty_amount = max(100.0, value * 0.5)
                penalties.append({
                    "type": ConsequenceType.BOUNTY.value,
                    "amount": bounty_amount,
                    "details": f"Bounty of {bounty_amount} gold placed on your head"
                })
                
            else:
                # Generic severe penalty
                fine_amount = max(400.0, value * 2.0)
                penalties.append({
                    "type": ConsequenceType.FINE.value,
                    "amount": fine_amount,
                    "details": f"Heavy fine of {fine_amount} gold for severe offense"
                })
                
                # Imprisonment
                imprisonment_days = random.randint(7, 20)
                penalties.append({
                    "type": ConsequenceType.IMPRISONMENT.value,
                    "duration_days": imprisonment_days,
                    "details": f"Imprisonment for {imprisonment_days} days"
                })
        
        # Apply penalties
        for penalty in penalties:
            self._apply_single_penalty(db, player_id, penalty, crime_details)
            
        # Update criminal record with notoriety increase
        notoriety_increase = {
            "minor": 0.3,
            "moderate": 0.7,
            "severe": 1.5
        }
        
        self.black_market_service._update_criminal_record(
            db,
            player_id,
            {"notoriety": criminal_record.notoriety + notoriety_increase.get(severity_level, 0.5)}
        )
        
        # Increase regional heat
        heat_increase = {
            "minor": 0.2,
            "moderate": 0.5,
            "severe": 1.0
        }
        
        if location_id and location_id != "unknown":
            heat_level = self.black_market_service._get_or_create_heat_level(db, location_id)
            self.black_market_service._update_heat_level(
                db,
                location_id,
                {
                    "current_heat": min(10.0, heat_level.current_heat + heat_increase.get(severity_level, 0.5)),
                    "recent_incidents": heat_level.recent_incidents + 1
                }
            )
        
        return {
            "success": True,
            "player_id": player_id,
            "crime_type": crime_type,
            "severity_level": severity_level,
            "penalties_applied": penalties,
            "notoriety_increase": notoriety_increase.get(severity_level, 0.5),
            "total_fine_amount": fine_amount,
            "message": f"Penalties applied for {crime_type}: {', '.join(p['details'] for p in penalties)}"
        }
    
    def schedule_patrol(
        self,
        db: Session,
        location_id: str,
        patrol_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Schedule a patrol in a location.
        
        Args:
            db: Database session
            location_id: ID of the location
            patrol_details: Optional patrol details
            
        Returns:
            Dictionary with patrol scheduling results
        """
        # Get regional heat level
        heat_level = self.black_market_service._get_or_create_heat_level(db, location_id)
        
        # Determine patrol frequency based on heat and authority presence
        base_frequency = 24  # Hours between patrols
        
        # Higher heat means more frequent patrols
        if heat_level.current_heat > 8.0:
            base_frequency = 4
        elif heat_level.current_heat > 6.0:
            base_frequency = 8
        elif heat_level.current_heat > 4.0:
            base_frequency = 12
        elif heat_level.current_heat > 2.0:
            base_frequency = 18
            
        # Authority presence affects frequency
        frequency_modifier = 1.0
        if heat_level.authority_presence > 8:
            frequency_modifier = 0.5  # Twice as frequent
        elif heat_level.authority_presence > 6:
            frequency_modifier = 0.7
        elif heat_level.authority_presence < 4:
            frequency_modifier = 1.5  # Less frequent
        elif heat_level.authority_presence < 2:
            frequency_modifier = 2.0  # Half as frequent
            
        # Calculate final frequency
        patrol_frequency_hours = max(1, base_frequency * frequency_modifier)
        
        # Determine next patrol time
        last_patrol = heat_level.last_patrol_time
        
        if last_patrol:
            # Schedule after the last patrol plus frequency
            next_patrol = last_patrol + timedelta(hours=patrol_frequency_hours)
            
            # If that's in the past, schedule for now + small random delay
            if next_patrol < datetime.utcnow():
                next_patrol = datetime.utcnow() + timedelta(hours=random.uniform(0.5, 2.0))
        else:
            # No previous patrol, schedule randomly within the next frequency period
            next_patrol = datetime.utcnow() + timedelta(hours=random.uniform(1.0, patrol_frequency_hours))
            
        # Determine patrol size and composition based on heat and authority presence
        patrol_size = 2  # Default size
        
        if heat_level.current_heat > 7.0 or heat_level.authority_presence > 7:
            patrol_size = 4
        elif heat_level.current_heat > 4.0 or heat_level.authority_presence > 4:
            patrol_size = 3
            
        # Determine if specialized units are included
        has_inspector = heat_level.current_heat > 6.0 or random.random() < 0.2
        has_mage = (heat_level.current_heat > 8.0 and heat_level.authority_presence > 6) or random.random() < 0.1
        
        # Create patrol data
        patrol_data = {
            "location_id": location_id,
            "scheduled_time": next_patrol.isoformat(),
            "size": patrol_size,
            "has_inspector": has_inspector,
            "has_mage": has_mage,
            "thoroughness": min(10, max(1, int((heat_level.current_heat + heat_level.authority_presence) / 2))),
            "active_investigations": heat_level.active_investigations,
            "custom_data": patrol_details or {}
        }
        
        # Store in regional heat level custom data
        custom_data = heat_level.special_conditions.copy()
        custom_data["next_patrol"] = patrol_data
        
        self.black_market_service._update_heat_level(
            db,
            location_id,
            {"special_conditions": custom_data}
        )
        
        return {
            "success": True,
            "location_id": location_id,
            "next_patrol": patrol_data,
            "frequency_hours": patrol_frequency_hours
        }
    
    # === HELPER METHODS ===
    
    def _determine_contraband_consequence(
        self,
        contraband_items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Determine consequence for being caught with contraband."""
        if not contraband_items:
            return {
                "type": "warning",
                "severity": "minor",
                "details": "You receive a warning for suspicious behavior."
            }
            
        # Calculate total value and severity
        total_value = sum(item.get("value", 10.0) for item in contraband_items)
        
        # Determine severity based on item categories
        severity_score = 0
        
        for item in contraband_items:
            category = item.get("category", "")
            
            if category == IllicitItemCategory.FORBIDDEN_ARTIFACT.value:
                severity_score += 3
            elif category == IllicitItemCategory.ILLEGAL_SUBSTANCE.value:
                severity_score += 2
            elif category == IllicitItemCategory.COUNTERFEIT.value:
                severity_score += 2
            elif category == IllicitItemCategory.STOLEN.value:
                severity_score += 1
            else:
                severity_score += 1
                
        # Adjust by quantity
        total_quantity = sum(item.get("quantity", 1) for item in contraband_items)
        if total_quantity > 10:
            severity_score *= 1.5
        elif total_quantity > 5:
            severity_score *= 1.2
            
        # Determine consequence
        if severity_score < 3:
            # Minor consequence
            fine_amount = max(20.0, total_value * 0.5)
            
            return {
                "type": "fine",
                "severity": "minor",
                "fine_amount": fine_amount,
                "details": f"The patrol confiscates your contraband and issues a fine of {fine_amount} gold."
            }
            
        elif severity_score < 7:
            # Moderate consequence
            fine_amount = max(50.0, total_value * 1.0)
            
            return {
                "type": "fine_and_detainment",
                "severity": "moderate",
                "fine_amount": fine_amount,
                "detainment_hours": random.randint(4, 12),
                "details": f"The patrol confiscates your contraband, issues a fine of {fine_amount} gold, and detains you for questioning."
            }
            
        else:
            # Severe consequence
            fine_amount = max(100.0, total_value * 1.5)
            imprisonment_days = random.randint(1, 5)
            
            return {
                "type": "arrest",
                "severity": "severe",
                "fine_amount": fine_amount,
                "imprisonment_days": imprisonment_days,
                "details": f"The patrol arrests you for possession of serious contraband. You face a {fine_amount} gold fine and {imprisonment_days} days imprisonment."
            }
    
    def _apply_single_penalty(
        self,
        db: Session,
        player_id: str,
        penalty: Dict[str, Any],
        crime_details: Dict[str, Any]
    ) -> None:
        """Apply a single penalty to a player."""
        penalty_type = penalty.get("type", "")
        
        if penalty_type == ConsequenceType.FINE.value:
            # Fine - would deduct from player currency
            amount = penalty.get("amount", 0.0)
            # In a real implementation, deduct from player gold
            
        elif penalty_type == ConsequenceType.IMPRISONMENT.value:
            # Imprisonment - would restrict player actions
            duration_days = penalty.get("duration_days", 1)
            # In a real implementation, apply imprisonment status to player
            
        elif penalty_type == ConsequenceType.BUSINESS_SHUTDOWN.value:
            # Business shutdown
            business_id = crime_details.get("business_id")
            duration_days = penalty.get("duration_days", 7)
            
            if business_id:
                business = get_business(db, business_id)
                if business:
                    # Apply closure to business
                    update_business(db, business_id, {
                        "custom_data": {
                            **(business.custom_data or {}),
                            "closure": {
                                "closed_until": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                                "reason": "Authority shutdown due to illegal activities"
                            }
                        }
                    })
                    
        elif penalty_type == ConsequenceType.LICENSE_REVOCATION.value:
            # License revocation
            business_id = crime_details.get("business_id")
            duration_days = penalty.get("duration_days", 7)
            
            if business_id:
                business = get_business(db, business_id)
                if business:
                    # Apply license restriction to business
                    update_business(db, business_id, {
                        "custom_data": {
                            **(business.custom_data or {}),
                            "license_restriction": {
                                "until": (datetime.utcnow() + timedelta(days=duration_days)).isoformat(),
                                "details": "License restricted due to violations"
                            }
                        }
                    })
                    
        elif penalty_type == ConsequenceType.ASSET_SEIZURE.value:
            # Asset seizure - would take assets from player
            amount = penalty.get("amount", 0.0)
            # In a real implementation, remove assets or gold
            
        elif penalty_type == ConsequenceType.BOUNTY.value:
            # Apply bounty
            amount = penalty.get("amount", 0.0)
            criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
            
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"current_bounty": criminal_record.current_bounty + amount}
            )
            
        elif penalty_type == ConsequenceType.REPUTATION_DAMAGE.value:
            # Reputation damage with factions
            # In a real implementation, reduce faction reputation
            pass