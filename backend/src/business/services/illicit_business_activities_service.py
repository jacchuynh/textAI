"""
Illicit Business Activities Service

This module provides functionality for managing illicit operations within player-owned businesses,
including hidden inventory, crafting illicit items, and money laundering.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.src.business.models.illicit_models import (
    IllicitItemCategory, IllicitServiceType, SecurityMeasure,
    IllicitBusinessOperation, IllicitInventoryItem, IllicitService,
    IllicitCustomOrderRequest
)
from backend.src.business.models.illicit_db_models import (
    DBIllicitBusinessOperation, DBIllicitInventoryItem, 
    DBIllicitService, DBIllicitCustomOrderRequest
)
from backend.src.business.services.black_market_operations_service import BlackMarketOperationsService
from backend.src.business.services.player_business_daily_operations_service import PlayerBusinessDailyOperationsService
from backend.src.business.crud import (
    get_business, update_business, record_financial_transaction
)

logger = logging.getLogger(__name__)

class IllicitBusinessActivitiesService:
    """Service for managing illicit business activities."""
    
    def __init__(self):
        """Initialize the illicit business activities service."""
        self.logger = logging.getLogger("IllicitBusinessActivitiesService")
        self.black_market_service = BlackMarketOperationsService()
        self.daily_operations_service = PlayerBusinessDailyOperationsService()
    
    def toggle_illicit_operation_mode(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        is_active: bool
    ) -> Dict[str, Any]:
        """
        Toggle a business's illicit operation mode.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            is_active: Whether illicit operations should be active
            
        Returns:
            Dictionary with toggle results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get or create illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Update active status
        illicit_op.is_active = is_active
        db.commit()
        
        # Update business notoriety if activating
        if is_active and not illicit_op.is_active:
            # Increase business notoriety
            update_business(db, business_id, {
                "criminal_notoriety_score": business.criminal_notoriety_score + 0.5 if hasattr(business, "criminal_notoriety_score") else 0.5
            })
            
            # Update player's criminal record
            self.black_market_service._get_or_create_criminal_record(db, player_id)
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.5}
            )
            
        return {
            "business_id": business_id,
            "illicit_operations_active": is_active,
            "security_level": illicit_op.security_level,
            "hidden_capacity": illicit_op.hidden_capacity,
            "message": f"Illicit operations {'activated' if is_active else 'deactivated'} for {business.business_name_player_chosen}."
        }
    
    def add_security_measure(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        security_measure: str,
        cost: float
    ) -> Dict[str, Any]:
        """
        Add a security measure to a business's illicit operations.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            security_measure: Security measure to add
            cost: Cost of the security measure
            
        Returns:
            Dictionary with security measure addition results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Validate security measure
        try:
            security_measure_enum = SecurityMeasure(security_measure)
        except ValueError:
            raise ValueError(f"Invalid security measure: {security_measure}")
            
        # Check business funds
        if business.current_capital < cost:
            raise ValueError(f"Insufficient funds. Need {cost} gold, have {business.current_capital} gold.")
            
        # Get or create illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Check if security measure already exists
        if security_measure in illicit_op.security_measures:
            raise ValueError(f"Security measure {security_measure} already installed")
            
        # Add security measure
        security_measures = illicit_op.security_measures.copy()
        security_measures.append(security_measure)
        illicit_op.security_measures = security_measures
        
        # Increase security level
        security_level_increase = {
            SecurityMeasure.HIDDEN_COMPARTMENT.value: 1,
            SecurityMeasure.LOOKOUT_POST.value: 2,
            SecurityMeasure.ESCAPE_TUNNEL.value: 3,
            SecurityMeasure.BRIBED_GUARDS.value: 2,
            SecurityMeasure.SOUNDPROOFING.value: 1,
            SecurityMeasure.CODE_PHRASES.value: 1,
            SecurityMeasure.DISGUISED_MERCHANDISE.value: 1,
            SecurityMeasure.FALSE_PAPERWORK.value: 2,
            SecurityMeasure.MAGICAL_WARDS.value: 3,
            SecurityMeasure.SECRET_ENTRANCE.value: 2
        }
        
        illicit_op.security_level += security_level_increase.get(security_measure, 1)
        
        # Reduce business capital
        update_business(db, business_id, {
            "current_capital": business.current_capital - cost
        })
        
        # Record transaction
        record_financial_transaction(
            db,
            {
                "business_id": business_id,
                "transaction_type": "expense",
                "amount": cost,
                "description": f"Security upgrade: {security_measure.replace('_', ' ').title()}",
                "timestamp": datetime.utcnow().isoformat(),
                "custom_data": {
                    "type": "security_measure",
                    "measure_added": security_measure
                }
            }
        )
        
        db.commit()
        
        # Security effects
        security_effects = {
            SecurityMeasure.HIDDEN_COMPARTMENT.value: "Provides a hidden storage area for illicit goods",
            SecurityMeasure.LOOKOUT_POST.value: "Gives early warning of authority patrols or inspections",
            SecurityMeasure.ESCAPE_TUNNEL.value: "Offers an escape route during raids",
            SecurityMeasure.BRIBED_GUARDS.value: "Reduces the frequency of official inspections",
            SecurityMeasure.SOUNDPROOFING.value: "Prevents suspicious noises from being heard outside",
            SecurityMeasure.CODE_PHRASES.value: "Allows secure communication about illicit activities",
            SecurityMeasure.DISGUISED_MERCHANDISE.value: "Makes illicit goods harder to identify during inspections",
            SecurityMeasure.FALSE_PAPERWORK.value: "Provides cover for illicit goods and operations",
            SecurityMeasure.MAGICAL_WARDS.value: "Magical protection against detection and intrusion",
            SecurityMeasure.SECRET_ENTRANCE.value: "Allows discreet access for illicit contacts"
        }
        
        # Capacity increases
        capacity_increases = {
            SecurityMeasure.HIDDEN_COMPARTMENT.value: 10,
            SecurityMeasure.SECRET_ENTRANCE.value: 5
        }
        
        if security_measure in capacity_increases:
            illicit_op.hidden_capacity += capacity_increases[security_measure]
            
        return {
            "business_id": business_id,
            "security_measure_added": security_measure,
            "new_security_level": illicit_op.security_level,
            "cost": cost,
            "effect": security_effects.get(security_measure, "Improves security for illicit operations"),
            "capacity_increase": capacity_increases.get(security_measure, 0),
            "new_hidden_capacity": illicit_op.hidden_capacity,
            "message": f"Added {security_measure.replace('_', ' ').title()} security measure to {business.business_name_player_chosen}."
        }
    
    def craft_illicit_item(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        item_recipe_id: str,
        quantity: int = 1
    ) -> Dict[str, Any]:
        """
        Craft an illicit item in a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            item_recipe_id: ID of the item recipe
            quantity: Quantity to craft
            
        Returns:
            Dictionary with crafting results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Get recipe details (in a real implementation, this would come from a recipe database)
        # For now, use some example recipes
        recipes = {
            "poison_recipe": {
                "name": "Deadly Nightshade Poison",
                "category": IllicitItemCategory.ILLEGAL_SUBSTANCE.value,
                "description": "A potent poison that causes paralysis and death.",
                "materials": {
                    "nightshade": 2,
                    "venomous_spider_fangs": 1,
                    "alchemical_base": 1
                },
                "production_time_hours": 3,
                "base_price": 50.0,
                "risk_level": 8,
                "skill_required": "alchemy"
            },
            "lockpick_recipe": {
                "name": "Master Lockpicks",
                "category": IllicitItemCategory.CONTRABAND.value,
                "description": "High-quality lockpicks that can open almost any lock.",
                "materials": {
                    "fine_steel": 2,
                    "precision_tools": 1
                },
                "production_time_hours": 2,
                "base_price": 30.0,
                "risk_level": 5,
                "skill_required": "smithing"
            },
            "counterfeit_recipe": {
                "name": "Counterfeit Gold Coins",
                "category": IllicitItemCategory.COUNTERFEIT.value,
                "description": "Fake gold coins that look just like the real thing.",
                "materials": {
                    "base_metal": 2,
                    "gold_leaf": 1,
                    "engraving_tools": 1
                },
                "production_time_hours": 4,
                "base_price": 100.0,
                "risk_level": 9,
                "skill_required": "forgery"
            }
        }
        
        # Check if recipe exists
        if item_recipe_id not in recipes:
            raise ValueError(f"Recipe {item_recipe_id} not found")
            
        recipe = recipes[item_recipe_id]
        
        # Check business inventory for materials
        regular_inventory = business.inventory or {}
        
        # Verify all materials are available
        missing_materials = []
        for material, required_quantity in recipe["materials"].items():
            total_required = required_quantity * quantity
            
            if material not in regular_inventory or regular_inventory[material]["quantity"] < total_required:
                missing_materials.append({
                    "material": material,
                    "required": total_required,
                    "available": regular_inventory.get(material, {}).get("quantity", 0)
                })
                
        if missing_materials:
            return {
                "success": False,
                "message": "Missing required materials for crafting.",
                "missing_materials": missing_materials
            }
            
        # Calculate detection risk
        base_risk = 0.1  # 10% base risk
        
        # Higher risk items have higher detection chance
        base_risk += recipe["risk_level"] / 50  # Up to +0.2 for highest risk
        
        # Larger quantities are riskier
        if quantity > 5:
            base_risk += 0.2
        elif quantity > 2:
            base_risk += 0.1
            
        # Security measures reduce risk
        security_reduction = illicit_op.security_level / 50  # Up to -0.2
        
        # Final risk
        detection_risk = max(0.01, min(0.9, base_risk - security_reduction))
        
        # Roll for detection
        is_detected = random.random() <= detection_risk
        
        if is_detected:
            # Crafting was detected - handle consequences
            
            # Update heat level for business location
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {
                    "current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 1.0,
                    "recent_incidents": self.black_market_service._get_or_create_heat_level(db, business.location_id).recent_incidents + 1
                }
            )
            
            # Update player criminal record
            criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
            
            known_crimes = criminal_record.known_crimes.copy()
            known_crimes.append({
                "date": datetime.utcnow().isoformat(),
                "type": "illicit_crafting",
                "location_id": business.location_id,
                "business_id": business_id,
                "item": recipe["name"],
                "quantity": quantity
            })
            
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {
                    "notoriety": criminal_record.notoriety + 0.5,
                    "known_crimes": known_crimes,
                    "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [business.location_id]))
                }
            )
            
            # Consume materials (they're lost in the raid)
            for material, required_quantity in recipe["materials"].items():
                total_required = required_quantity * quantity
                regular_inventory[material]["quantity"] -= total_required
                
            # Update inventory
            update_business(db, business_id, {
                "inventory": regular_inventory
            })
            
            # Determine consequences
            consequence_roll = random.random()
            
            if consequence_roll < 0.3:
                # Minor consequences - fine
                fine_amount = recipe["base_price"] * quantity
                
                consequence = {
                    "type": "fine",
                    "severity": "minor",
                    "fine_amount": fine_amount,
                    "details": f"Authorities issued a fine of {fine_amount} gold for illegal crafting."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
            elif consequence_roll < 0.7:
                # Moderate consequences - fine and confiscation
                fine_amount = recipe["base_price"] * quantity * 1.5
                
                consequence = {
                    "type": "fine_and_confiscation",
                    "severity": "moderate",
                    "fine_amount": fine_amount,
                    "details": f"Authorities confiscated materials and issued a fine of {fine_amount} gold."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
            else:
                # Severe consequences - temporary business closure
                fine_amount = recipe["base_price"] * quantity * 2
                closure_days = random.randint(1, 5)
                
                consequence = {
                    "type": "business_closure",
                    "severity": "severe",
                    "fine_amount": fine_amount,
                    "closure_days": closure_days,
                    "details": f"Authorities temporarily closed the business for {closure_days} days and issued a fine of {fine_amount} gold."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount),
                    "custom_data": {
                        **(business.custom_data or {}),
                        "closure": {
                            "closed_until": (datetime.utcnow() + timedelta(days=closure_days)).isoformat(),
                            "reason": "Illicit crafting"
                        }
                    }
                })
            
            return {
                "success": False,
                "detected": True,
                "materials_lost": True,
                "message": f"Your illicit crafting operation was discovered by authorities!",
                "consequence": consequence
            }
            
        else:
            # Successful crafting
            
            # Consume materials
            for material, required_quantity in recipe["materials"].items():
                total_required = required_quantity * quantity
                regular_inventory[material]["quantity"] -= total_required
                
            # Update inventory
            update_business(db, business_id, {
                "inventory": regular_inventory
            })
            
            # Add item to illicit inventory
            item_id = f"illicit_{item_recipe_id}_{str(uuid4())[:8]}"
            
            # Check if there's already this type of item in illicit inventory
            existing_item = db.query(DBIllicitInventoryItem).filter(
                DBIllicitInventoryItem.business_operation_id == illicit_op.id,
                DBIllicitInventoryItem.name == recipe["name"]
            ).first()
            
            if existing_item:
                # Update existing item
                existing_item.quantity += quantity
                db.commit()
                
                item_result = {
                    "item_id": existing_item.item_id,
                    "name": existing_item.name,
                    "quantity": existing_item.quantity,
                    "category": existing_item.category,
                    "crafted_quantity": quantity
                }
            else:
                # Create new item
                # Calculate value - illicit items are more valuable
                purchase_price = 0  # Crafted, not purchased
                selling_price = recipe["base_price"] * 1.5  # 50% markup
                
                new_item = DBIllicitInventoryItem(
                    id=str(uuid4()),
                    business_operation_id=illicit_op.id,
                    item_id=item_id,
                    name=recipe["name"],
                    quantity=quantity,
                    purchase_price_per_unit=purchase_price,
                    selling_price_per_unit=selling_price,
                    category=recipe["category"],
                    is_stolen=False,
                    acquisition_date=datetime.utcnow(),
                    description=recipe["description"],
                    custom_data={
                        "crafted": True,
                        "recipe_id": item_recipe_id,
                        "production_time_hours": recipe["production_time_hours"]
                    }
                )
                
                db.add(new_item)
                db.commit()
                
                item_result = {
                    "item_id": new_item.item_id,
                    "name": new_item.name,
                    "quantity": new_item.quantity,
                    "category": new_item.category,
                    "selling_price": new_item.selling_price_per_unit,
                    "crafted_quantity": quantity
                }
                
            # Slightly increase regional heat
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {"current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.1}
            )
            
            # Slightly increase notoriety
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.2}
            )
            
            return {
                "success": True,
                "message": f"Successfully crafted {quantity} {recipe['name']}.",
                "item": item_result,
                "risk_taken": detection_risk
            }
    
    def launder_money(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        amount_to_launder: float
    ) -> Dict[str, Any]:
        """
        Launder illicit money through a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            amount_to_launder: Amount of money to launder
            
        Returns:
            Dictionary with laundering results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Calculate maximum laundering capacity based on business type and size
        # In a real implementation, this would be based on business data
        base_capacity = 1000.0  # Base capacity per day
        
        # Business size modifier
        size_modifier = 1.0  # Default
        if hasattr(business, "size") and business.size:
            size_mapper = {
                "small": 0.5,
                "medium": 1.0,
                "large": 2.0
            }
            size_modifier = size_mapper.get(business.size, 1.0)
            
        # Business type modifier
        type_modifier = 1.0  # Default
        if business.business_type:
            type_mapper = {
                "tavern": 1.5,  # Cash-heavy businesses are better for laundering
                "inn": 1.3,
                "trading_post": 1.2,
                "blacksmith": 0.8,
                "alchemist": 0.7
            }
            type_modifier = type_mapper.get(business.business_type, 1.0)
            
        # Calculate maximum daily capacity
        max_capacity = base_capacity * size_modifier * type_modifier
        
        # Check if amount exceeds capacity
        if amount_to_launder > max_capacity:
            return {
                "success": False,
                "message": f"Cannot launder more than {max_capacity} gold per day through this business.",
                "max_capacity": max_capacity
            }
            
        # Calculate detection risk
        base_risk = 0.1  # 10% base risk
        
        # Larger amounts are riskier
        amount_factor = amount_to_launder / max_capacity
        base_risk += amount_factor * 0.4  # Up to +0.4 for maximum amount
        
        # Security measures reduce risk
        security_reduction = illicit_op.security_level / 40  # Up to -0.25
        
        # Laundering efficiency affects success
        efficiency_bonus = -0.1 if illicit_op.laundering_efficiency >= 0.9 else 0.0
        
        # Final risk
        detection_risk = max(0.01, min(0.9, base_risk - security_reduction + efficiency_bonus))
        
        # Roll for detection
        is_detected = random.random() <= detection_risk
        
        if is_detected:
            # Laundering was detected - handle consequences
            
            # Update heat level for business location
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {
                    "current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 1.0,
                    "recent_incidents": self.black_market_service._get_or_create_heat_level(db, business.location_id).recent_incidents + 1
                }
            )
            
            # Update player criminal record
            criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
            
            known_crimes = criminal_record.known_crimes.copy()
            known_crimes.append({
                "date": datetime.utcnow().isoformat(),
                "type": "money_laundering",
                "location_id": business.location_id,
                "business_id": business_id,
                "amount": amount_to_launder
            })
            
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {
                    "notoriety": criminal_record.notoriety + 0.8,  # Significant notoriety increase
                    "known_crimes": known_crimes,
                    "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [business.location_id]))
                }
            )
            
            # Determine consequences
            consequence_roll = random.random()
            
            if consequence_roll < 0.2:
                # Minor consequences - fine
                fine_amount = amount_to_launder * 0.5
                
                consequence = {
                    "type": "fine",
                    "severity": "minor",
                    "fine_amount": fine_amount,
                    "details": f"Authorities issued a fine of {fine_amount} gold for suspicious financial activity."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
            elif consequence_roll < 0.6:
                # Moderate consequences - fine and investigation
                fine_amount = amount_to_launder * 1.0
                
                consequence = {
                    "type": "fine_and_investigation",
                    "severity": "moderate",
                    "fine_amount": fine_amount,
                    "details": f"Authorities fined you {fine_amount} gold and opened an investigation into your business."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
                # TODO: Start an investigation (would be handled by the authority system)
                
            else:
                # Severe consequences - asset seizure
                fine_amount = amount_to_launder * 2.0
                
                consequence = {
                    "type": "asset_seizure",
                    "severity": "severe",
                    "fine_amount": fine_amount,
                    "details": f"Authorities seized {fine_amount} gold from your business and are investigating your activities."
                }
                
                # Apply fine/seizure
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
                # TODO: Start a serious investigation (would be handled by the authority system)
            
            return {
                "success": False,
                "detected": True,
                "message": "Your money laundering operation was discovered by authorities!",
                "consequence": consequence,
                "money_lost": amount_to_launder
            }
            
        else:
            # Successful laundering
            
            # Calculate laundering fee
            laundering_fee = amount_to_launder * (1.0 - illicit_op.laundering_efficiency)
            clean_amount = amount_to_launder - laundering_fee
            
            # Add clean money to business
            update_business(db, business_id, {
                "current_capital": business.current_capital + clean_amount
            })
            
            # Record laundering in transaction history
            record_financial_transaction(
                db,
                {
                    "business_id": business_id,
                    "transaction_type": "income",
                    "amount": clean_amount,
                    "description": "Income from various services",
                    "timestamp": datetime.utcnow().isoformat(),
                    "custom_data": {
                        "actual_source": "laundered_money",
                        "original_amount": amount_to_launder,
                        "fee": laundering_fee
                    }
                }
            )
            
            # Slightly increase regional heat
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {"current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.2}
            )
            
            # Increase notoriety
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.3}
            )
            
            return {
                "success": True,
                "message": f"Successfully laundered {amount_to_launder} gold. {clean_amount} gold added to business funds.",
                "original_amount": amount_to_launder,
                "laundering_fee": laundering_fee,
                "clean_amount": clean_amount,
                "risk_taken": detection_risk
            }
    
    def add_illicit_item_to_inventory(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        item_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add an illicit item to a business's hidden inventory.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            item_data: Data for the illicit item
            
        Returns:
            Dictionary with item addition results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Validate required item fields
        required_fields = ["name", "quantity", "category"]
        for field in required_fields:
            if field not in item_data:
                raise ValueError(f"Missing required field: {field}")
                
        # Validate category
        try:
            category = IllicitItemCategory(item_data["category"])
        except ValueError:
            raise ValueError(f"Invalid item category: {item_data['category']}")
            
        # Check if item will fit in hidden capacity
        existing_items = db.query(DBIllicitInventoryItem).filter(
            DBIllicitInventoryItem.business_operation_id == illicit_op.id
        ).all()
        
        current_capacity_used = sum(item.quantity for item in existing_items)
        new_quantity = item_data["quantity"]
        
        if current_capacity_used + new_quantity > illicit_op.hidden_capacity:
            return {
                "success": False,
                "message": f"Not enough hidden capacity. Have {illicit_op.hidden_capacity - current_capacity_used}, need {new_quantity}.",
                "current_capacity": illicit_op.hidden_capacity,
                "used_capacity": current_capacity_used,
                "available_capacity": illicit_op.hidden_capacity - current_capacity_used
            }
            
        # Check if similar item already exists
        existing_item = None
        if "item_id" in item_data:
            existing_item = db.query(DBIllicitInventoryItem).filter(
                DBIllicitInventoryItem.business_operation_id == illicit_op.id,
                DBIllicitInventoryItem.item_id == item_data["item_id"]
            ).first()
        
        if not existing_item and "name" in item_data:
            existing_item = db.query(DBIllicitInventoryItem).filter(
                DBIllicitInventoryItem.business_operation_id == illicit_op.id,
                DBIllicitInventoryItem.name == item_data["name"]
            ).first()
            
        # Set default values if not provided
        purchase_price = item_data.get("purchase_price_per_unit", 0.0)
        selling_price = item_data.get("selling_price_per_unit", purchase_price * 1.5)
        
        if existing_item:
            # Update existing item
            existing_item.quantity += new_quantity
            
            # Update prices if provided
            if "purchase_price_per_unit" in item_data:
                existing_item.purchase_price_per_unit = purchase_price
            if "selling_price_per_unit" in item_data:
                existing_item.selling_price_per_unit = selling_price
                
            db.commit()
            
            item_result = {
                "item_id": existing_item.item_id,
                "name": existing_item.name,
                "quantity": existing_item.quantity,
                "category": existing_item.category,
                "added_quantity": new_quantity
            }
        else:
            # Create new item
            item_id = item_data.get("item_id", f"illicit_{str(uuid4())[:8]}")
            
            new_item = DBIllicitInventoryItem(
                id=str(uuid4()),
                business_operation_id=illicit_op.id,
                item_id=item_id,
                name=item_data["name"],
                quantity=new_quantity,
                purchase_price_per_unit=purchase_price,
                selling_price_per_unit=selling_price,
                category=category.value,
                is_stolen=item_data.get("is_stolen", False),
                origin_region_id=item_data.get("origin_region_id"),
                acquisition_date=datetime.utcnow(),
                description=item_data.get("description", ""),
                custom_data=item_data.get("custom_data", {})
            )
            
            db.add(new_item)
            db.commit()
            
            item_result = {
                "item_id": new_item.item_id,
                "name": new_item.name,
                "quantity": new_item.quantity,
                "category": new_item.category,
                "added_quantity": new_quantity
            }
            
        # Slightly increase notoriety if item is stolen
        if item_data.get("is_stolen", False):
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.1}
            )
            
        return {
            "success": True,
            "message": f"Added {new_quantity} {item_data['name']} to hidden inventory.",
            "item": item_result,
            "current_capacity": illicit_op.hidden_capacity,
            "used_capacity": current_capacity_used + new_quantity,
            "available_capacity": illicit_op.hidden_capacity - (current_capacity_used + new_quantity)
        }
    
    def get_illicit_inventory(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        category_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a business's illicit inventory.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            category_filter: Optional category to filter items
            
        Returns:
            Dictionary with illicit inventory
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Get illicit inventory
        query = db.query(DBIllicitInventoryItem).filter(
            DBIllicitInventoryItem.business_operation_id == illicit_op.id
        )
        
        if category_filter:
            try:
                category = IllicitItemCategory(category_filter)
                query = query.filter(DBIllicitInventoryItem.category == category.value)
            except ValueError:
                pass  # Invalid category, ignore filter
                
        items = query.all()
        
        # Convert to dictionary format
        inventory_items = []
        for item in items:
            inventory_items.append({
                "item_id": item.item_id,
                "name": item.name,
                "quantity": item.quantity,
                "category": item.category,
                "purchase_price_per_unit": item.purchase_price_per_unit,
                "selling_price_per_unit": item.selling_price_per_unit,
                "is_stolen": item.is_stolen,
                "origin_region_id": item.origin_region_id,
                "acquisition_date": item.acquisition_date.isoformat(),
                "description": item.description,
                "custom_data": item.custom_data
            })
            
        # Calculate capacity usage
        total_quantity = sum(item.quantity for item in items)
        
        return {
            "business_id": business_id,
            "items": inventory_items,
            "total_items": len(inventory_items),
            "total_quantity": total_quantity,
            "capacity": {
                "total": illicit_op.hidden_capacity,
                "used": total_quantity,
                "available": illicit_op.hidden_capacity - total_quantity
            },
            "security_level": illicit_op.security_level
        }
    
    def sell_illicit_item(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        item_id: str,
        quantity: int,
        buyer_id: Optional[str] = None,
        custom_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Sell an illicit item from a business's hidden inventory.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            item_id: ID of the item to sell
            quantity: Quantity to sell
            buyer_id: Optional ID of the buyer (NPC or player)
            custom_price: Optional custom price
            
        Returns:
            Dictionary with sale results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Get item
        item = db.query(DBIllicitInventoryItem).filter(
            DBIllicitInventoryItem.business_operation_id == illicit_op.id,
            DBIllicitInventoryItem.item_id == item_id
        ).first()
        
        if not item:
            raise ValueError(f"Item {item_id} not found in illicit inventory")
            
        # Check quantity
        if item.quantity < quantity:
            raise ValueError(f"Not enough items. Have {item.quantity}, trying to sell {quantity}.")
            
        # Determine price
        unit_price = custom_price or item.selling_price_per_unit
        total_price = unit_price * quantity
        
        # Calculate detection risk
        base_risk = 0.1  # 10% base risk
        
        # Certain categories are riskier to sell
        category_risk = {
            IllicitItemCategory.STOLEN.value: 0.1,
            IllicitItemCategory.CONTRABAND.value: 0.05,
            IllicitItemCategory.FORBIDDEN_ARTIFACT.value: 0.2,
            IllicitItemCategory.ILLEGAL_SUBSTANCE.value: 0.15,
            IllicitItemCategory.COUNTERFEIT.value: 0.1,
            IllicitItemCategory.SMUGGLED.value: 0.05
        }
        
        base_risk += category_risk.get(item.category, 0.0)
        
        # Larger quantities are riskier
        if quantity > 5:
            base_risk += 0.1
            
        # Higher value transactions are riskier
        if total_price > 500:
            base_risk += 0.1
        elif total_price > 200:
            base_risk += 0.05
            
        # Security measures reduce risk
        security_reduction = illicit_op.security_level / 50  # Up to -0.2
        
        # Known buyer reduces risk
        if buyer_id:
            base_risk -= 0.05
            
        # Final risk
        detection_risk = max(0.01, min(0.9, base_risk - security_reduction))
        
        # Roll for detection
        is_detected = random.random() <= detection_risk
        
        if is_detected:
            # Sale was detected - handle consequences
            
            # Update heat level for business location
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {
                    "current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.8,
                    "recent_incidents": self.black_market_service._get_or_create_heat_level(db, business.location_id).recent_incidents + 1
                }
            )
            
            # Update player criminal record
            criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
            
            known_crimes = criminal_record.known_crimes.copy()
            known_crimes.append({
                "date": datetime.utcnow().isoformat(),
                "type": "selling_illegal_goods",
                "location_id": business.location_id,
                "business_id": business_id,
                "item": item.name,
                "quantity": quantity,
                "value": total_price
            })
            
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {
                    "notoriety": criminal_record.notoriety + 0.5,
                    "known_crimes": known_crimes,
                    "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [business.location_id]))
                }
            )
            
            # Determine consequences
            consequence_roll = random.random()
            
            if consequence_roll < 0.3:
                # Minor consequences - item confiscation
                consequence = {
                    "type": "confiscation",
                    "severity": "minor",
                    "details": f"Authorities confiscated the {item.name}."
                }
                
                # Remove item from inventory
                item.quantity -= quantity
                if item.quantity <= 0:
                    db.delete(item)
                db.commit()
                
            elif consequence_roll < 0.7:
                # Moderate consequences - confiscation and fine
                fine_amount = total_price * 1.5
                
                consequence = {
                    "type": "confiscation_and_fine",
                    "severity": "moderate",
                    "fine_amount": fine_amount,
                    "details": f"Authorities confiscated the {item.name} and issued a fine of {fine_amount} gold."
                }
                
                # Remove item from inventory
                item.quantity -= quantity
                if item.quantity <= 0:
                    db.delete(item)
                    
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
                db.commit()
                
            else:
                # Severe consequences - confiscation, fine, and potential arrest
                fine_amount = total_price * 2.5
                
                consequence = {
                    "type": "arrest_attempt",
                    "severity": "severe",
                    "fine_amount": fine_amount,
                    "details": f"Authorities confiscated the {item.name}, issued a fine of {fine_amount} gold, and are attempting to arrest you."
                }
                
                # Remove item from inventory
                item.quantity -= quantity
                if item.quantity <= 0:
                    db.delete(item)
                    
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
                db.commit()
                
                # TODO: Handle arrest (would be handled by the authority system)
            
            return {
                "success": False,
                "detected": True,
                "message": "Your illicit sale was discovered by authorities!",
                "consequence": consequence,
                "item_id": item_id,
                "item_name": item.name,
                "quantity": quantity
            }
            
        else:
            # Successful sale
            
            # Update inventory
            item.quantity -= quantity
            if item.quantity <= 0:
                db.delete(item)
                
            # Add revenue to business
            update_business(db, business_id, {
                "current_capital": business.current_capital + total_price
            })
            
            # Record transaction
            record_financial_transaction(
                db,
                {
                    "business_id": business_id,
                    "transaction_type": "income",
                    "amount": total_price,
                    "description": f"Sale of special goods",
                    "timestamp": datetime.utcnow().isoformat(),
                    "related_entity_id": buyer_id,
                    "custom_data": {
                        "illicit_sale": True,
                        "item_id": item_id,
                        "item_name": item.name,
                        "quantity": quantity,
                        "unit_price": unit_price
                    }
                }
            )
            
            # Record black market transaction
            black_market_tx = DBBlackMarketTransaction(
                id=str(uuid4()),
                business_id=business_id,
                player_id=player_id,
                contact_npc_id=buyer_id if buyer_id and buyer_id.startswith("npc_") else None,
                transaction_type="sell",
                item_id=item_id,
                quantity=quantity,
                total_price=total_price,
                location_id=business.location_id,
                risk_taken=detection_risk,
                was_detected=False,
                custom_data={
                    "item_name": item.name,
                    "item_category": item.category,
                    "unit_price": unit_price,
                    "through_business": True
                }
            )
            db.add(black_market_tx)
            
            # Slightly increase regional heat
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {"current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.1}
            )
            
            # Slightly increase notoriety
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.2}
            )
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Successfully sold {quantity} {item.name} for {total_price} gold.",
                "item_id": item_id,
                "item_name": item.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "total_price": total_price,
                "risk_taken": detection_risk,
                "transaction_id": black_market_tx.id
            }
    
    def offer_illicit_service(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        service_type: str,
        service_details: Dict[str, Any],
        customer_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Offer an illicit service through a business.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            service_type: Type of service
            service_details: Details of the service
            customer_id: Optional ID of the customer
            
        Returns:
            Dictionary with service results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Validate service type
        try:
            service_type_enum = IllicitServiceType(service_type)
        except ValueError:
            raise ValueError(f"Invalid service type: {service_type}")
            
        # Get service from business services or create new one
        service = db.query(DBIllicitService).filter(
            DBIllicitService.business_operation_id == illicit_op.id,
            DBIllicitService.service_type == service_type_enum.value
        ).first()
        
        if not service:
            # Create new service
            service_name = service_details.get("name", service_type_enum.value.replace("_", " ").title())
            
            service = DBIllicitService(
                id=str(uuid4()),
                business_operation_id=illicit_op.id,
                service_type=service_type_enum.value,
                name=service_name,
                description=service_details.get("description", ""),
                base_price=service_details.get("base_price", 100.0),
                skill_requirement=service_details.get("skill_requirement", 5),
                risk_level=service_details.get("risk_level", 5),
                is_available=True,
                required_resources=service_details.get("required_resources", {}),
                custom_data=service_details.get("custom_data", {})
            )
            
            db.add(service)
            db.commit()
            
        # Check if service is available
        if not service.is_available:
            raise ValueError(f"Service {service.name} is not currently available")
            
        # Check required resources
        for resource, required_quantity in service.required_resources.items():
            # Check business inventory
            regular_inventory = business.inventory or {}
            
            if resource not in regular_inventory or regular_inventory[resource]["quantity"] < required_quantity:
                return {
                    "success": False,
                    "message": f"Missing required resource: {resource}. Need {required_quantity}.",
                    "missing_resources": [{
                        "resource": resource,
                        "required": required_quantity,
                        "available": regular_inventory.get(resource, {}).get("quantity", 0)
                    }]
                }
                
        # Calculate service price
        base_price = service.base_price
        
        # Adjust price based on service details
        price_modifiers = service_details.get("price_modifiers", {})
        final_price = base_price
        
        for modifier, value in price_modifiers.items():
            if modifier == "complexity":
                final_price *= (1.0 + (value / 10))
            elif modifier == "urgency":
                final_price *= (1.0 + (value / 5))
            elif modifier == "discretion":
                final_price *= (1.0 + (value / 8))
                
        # Calculate detection risk
        base_risk = 0.1  # 10% base risk
        
        # Service risk level affects detection
        base_risk += service.risk_level / 50  # Up to +0.2
        
        # Certain services are inherently riskier
        service_risk_modifier = {
            IllicitServiceType.FENCE.value: 0.05,
            IllicitServiceType.SMUGGLING.value: 0.1,
            IllicitServiceType.FORGERY.value: 0.1,
            IllicitServiceType.UNLICENSED_MAGIC.value: 0.15,
            IllicitServiceType.INFORMATION_BROKER.value: 0.05,
            IllicitServiceType.MONEY_LAUNDERING.value: 0.2,
            IllicitServiceType.ASSASSINATION.value: 0.3
        }
        base_risk += service_risk_modifier.get(service.service_type, 0.0)
        
        # Price can affect risk (higher value = higher risk)
        if final_price > 500:
            base_risk += 0.1
        elif final_price > 200:
            base_risk += 0.05
            
        # Security measures reduce risk
        security_reduction = illicit_op.security_level / 40  # Up to -0.25
        
        # Known customer reduces risk
        if customer_id:
            base_risk -= 0.05
            
        # Service details can affect risk
        for modifier, value in service_details.get("risk_modifiers", {}).items():
            if modifier == "public_location":
                base_risk += value / 10
            elif modifier == "daylight":
                base_risk += value / 8
                
        # Final risk
        detection_risk = max(0.01, min(0.9, base_risk - security_reduction))
        
        # Roll for detection
        is_detected = random.random() <= detection_risk
        
        if is_detected:
            # Service was detected - handle consequences
            
            # Update heat level for business location
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {
                    "current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 1.0,
                    "recent_incidents": self.black_market_service._get_or_create_heat_level(db, business.location_id).recent_incidents + 1
                }
            )
            
            # Update player criminal record
            criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
            
            known_crimes = criminal_record.known_crimes.copy()
            known_crimes.append({
                "date": datetime.utcnow().isoformat(),
                "type": "illicit_service",
                "service_type": service.service_type,
                "location_id": business.location_id,
                "business_id": business_id,
                "value": final_price
            })
            
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {
                    "notoriety": criminal_record.notoriety + 0.7,
                    "known_crimes": known_crimes,
                    "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [business.location_id]))
                }
            )
            
            # Consume resources
            regular_inventory = business.inventory or {}
            for resource, required_quantity in service.required_resources.items():
                regular_inventory[resource]["quantity"] -= required_quantity
                
            # Update inventory
            update_business(db, business_id, {
                "inventory": regular_inventory
            })
            
            # Determine consequences (more severe for certain services)
            service_severity_modifier = 1.0
            if service.service_type == IllicitServiceType.ASSASSINATION.value:
                service_severity_modifier = 2.0
            elif service.service_type in [IllicitServiceType.UNLICENSED_MAGIC.value, IllicitServiceType.MONEY_LAUNDERING.value]:
                service_severity_modifier = 1.5
                
            consequence_roll = random.random() * service_severity_modifier
            
            if consequence_roll < 0.3:
                # Minor consequences - fine
                fine_amount = final_price * 1.0
                
                consequence = {
                    "type": "fine",
                    "severity": "minor",
                    "fine_amount": fine_amount,
                    "details": f"Authorities issued a fine of {fine_amount} gold for offering illegal services."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount)
                })
                
            elif consequence_roll < 0.7:
                # Moderate consequences - fine and business restrictions
                fine_amount = final_price * 2.0
                
                consequence = {
                    "type": "fine_and_restrictions",
                    "severity": "moderate",
                    "fine_amount": fine_amount,
                    "details": f"Authorities issued a fine of {fine_amount} gold and placed restrictions on your business."
                }
                
                # Apply fine
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount),
                    "custom_data": {
                        **(business.custom_data or {}),
                        "restrictions": {
                            "until": (datetime.utcnow() + timedelta(days=7)).isoformat(),
                            "type": "increased_inspections",
                            "description": "Increased authority inspections"
                        }
                    }
                })
                
            else:
                # Severe consequences - business closure
                fine_amount = final_price * 3.0
                closure_days = random.randint(3, 14)
                
                consequence = {
                    "type": "business_closure",
                    "severity": "severe",
                    "fine_amount": fine_amount,
                    "closure_days": closure_days,
                    "details": f"Authorities closed your business for {closure_days} days and issued a fine of {fine_amount} gold."
                }
                
                # Apply fine and closure
                update_business(db, business_id, {
                    "current_capital": max(0, business.current_capital - fine_amount),
                    "custom_data": {
                        **(business.custom_data or {}),
                        "closure": {
                            "closed_until": (datetime.utcnow() + timedelta(days=closure_days)).isoformat(),
                            "reason": f"Illegal {service.service_type} services"
                        }
                    }
                })
                
                # Disable the service
                service.is_available = False
            
            db.commit()
            
            return {
                "success": False,
                "detected": True,
                "message": f"Your {service.name} service was discovered by authorities!",
                "consequence": consequence,
                "service_type": service.service_type
            }
            
        else:
            # Successful service
            
            # Consume resources
            regular_inventory = business.inventory or {}
            for resource, required_quantity in service.required_resources.items():
                regular_inventory[resource]["quantity"] -= required_quantity
                
            # Update inventory
            update_business(db, business_id, {
                "inventory": regular_inventory
            })
            
            # Add revenue to business
            update_business(db, business_id, {
                "current_capital": business.current_capital + final_price
            })
            
            # Record transaction
            record_financial_transaction(
                db,
                {
                    "business_id": business_id,
                    "transaction_type": "income",
                    "amount": final_price,
                    "description": "Specialized service fees",
                    "timestamp": datetime.utcnow().isoformat(),
                    "related_entity_id": customer_id,
                    "custom_data": {
                        "illicit_service": True,
                        "service_type": service.service_type,
                        "service_name": service.name
                    }
                }
            )
            
            # Record black market transaction
            black_market_tx = DBBlackMarketTransaction(
                id=str(uuid4()),
                business_id=business_id,
                player_id=player_id,
                contact_npc_id=customer_id if customer_id and customer_id.startswith("npc_") else None,
                transaction_type="service",
                service_id=service.id,
                total_price=final_price,
                location_id=business.location_id,
                risk_taken=detection_risk,
                was_detected=False,
                custom_data={
                    "service_name": service.name,
                    "service_type": service.service_type,
                    "service_details": service_details,
                    "through_business": True
                }
            )
            db.add(black_market_tx)
            
            # Slightly increase regional heat
            self.black_market_service._update_heat_level(
                db,
                business.location_id,
                {"current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.15}
            )
            
            # Increase notoriety based on service type
            notoriety_increase = {
                IllicitServiceType.FENCE.value: 0.1,
                IllicitServiceType.SMUGGLING.value: 0.2,
                IllicitServiceType.FORGERY.value: 0.2,
                IllicitServiceType.UNLICENSED_MAGIC.value: 0.3,
                IllicitServiceType.INFORMATION_BROKER.value: 0.1,
                IllicitServiceType.MONEY_LAUNDERING.value: 0.3,
                IllicitServiceType.ASSASSINATION.value: 0.5
            }
            
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + notoriety_increase.get(service.service_type, 0.2)}
            )
            
            db.commit()
            
            # Generate service outcome
            service_outcome = {}
            
            if service.service_type == IllicitServiceType.FENCE.value:
                service_outcome = {
                    "items_fenced": service_details.get("items", []),
                    "fence_fee": final_price * 0.2
                }
            elif service.service_type == IllicitServiceType.FORGERY.value:
                service_outcome = {
                    "document_type": service_details.get("document_type", "document"),
                    "quality": min(10, max(1, illicit_op.security_level)),
                    "detection_difficulty": min(10, max(1, illicit_op.security_level))
                }
            elif service.service_type == IllicitServiceType.INFORMATION_BROKER.value:
                service_outcome = {
                    "information_type": service_details.get("information_type", "secret"),
                    "target": service_details.get("target", "unknown"),
                    "reliability": min(10, max(1, service.skill_requirement)) / 10
                }
            
            return {
                "success": True,
                "message": f"Successfully provided {service.name} service for {final_price} gold.",
                "service_type": service.service_type,
                "service_name": service.name,
                "price": final_price,
                "risk_taken": detection_risk,
                "transaction_id": black_market_tx.id,
                "outcome": service_outcome
            }
    
    def handle_illicit_custom_order(
        self,
        db: Session,
        player_id: str,
        business_id: str,
        order_id: str,
        action: str,
        action_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Handle an illicit custom order.
        
        Args:
            db: Database session
            player_id: ID of the player
            business_id: ID of the business
            order_id: ID of the order
            action: Action to take (accept, reject, complete, etc.)
            action_details: Optional action details
            
        Returns:
            Dictionary with action results
        """
        # Validate business ownership
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
        if business.player_character_id != player_id:
            raise ValueError("You don't own this business")
            
        # Get illicit operation
        illicit_op = self._get_or_create_illicit_operation(db, business_id)
        
        # Verify illicit operations are active
        if not illicit_op.is_active:
            raise ValueError("Illicit operations are not active for this business")
            
        # Get the order
        order = db.query(DBIllicitCustomOrderRequest).filter(
            DBIllicitCustomOrderRequest.id == order_id,
            DBIllicitCustomOrderRequest.target_player_business_profile_id == business_id
        ).first()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
            
        # Process action
        if action == "accept":
            if order.status != "awaiting_review":
                raise ValueError(f"Cannot accept order in status {order.status}")
                
            # Update order status
            order.status = "accepted"
            order.custom_data = {
                **(order.custom_data or {}),
                "accepted_date": datetime.utcnow().isoformat(),
                "accepted_details": action_details
            }
            
            db.commit()
            
            # Slightly increase notoriety
            self.black_market_service._update_criminal_record(
                db,
                player_id,
                {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.1}
            )
            
            return {
                "success": True,
                "message": f"Accepted illicit custom order for {order.item_description_by_npc}",
                "order_id": order_id,
                "new_status": "accepted",
                "deadline_date": order.deadline_date.isoformat()
            }
            
        elif action == "reject":
            if order.status != "awaiting_review":
                raise ValueError(f"Cannot reject order in status {order.status}")
                
            # Update order status
            order.status = "declined"
            order.custom_data = {
                **(order.custom_data or {}),
                "declined_date": datetime.utcnow().isoformat(),
                "declined_reason": action_details.get("reason", "No reason provided")
            }
            
            db.commit()
            
            return {
                "success": True,
                "message": f"Rejected illicit custom order",
                "order_id": order_id,
                "new_status": "declined"
            }
            
        elif action == "complete":
            if order.status != "accepted":
                raise ValueError(f"Cannot complete order in status {order.status}")
                
            # Check if order is past deadline
            if datetime.utcnow() > order.deadline_date:
                return {
                    "success": False,
                    "message": f"Order deadline has passed",
                    "order_id": order_id,
                    "deadline_date": order.deadline_date.isoformat()
                }
                
            # Calculate detection risk
            base_risk = 0.1  # 10% base risk
            
            # Item category affects risk
            category_risk = {
                IllicitItemCategory.STOLEN.value: 0.1,
                IllicitItemCategory.CONTRABAND.value: 0.05,
                IllicitItemCategory.FORBIDDEN_ARTIFACT.value: 0.2,
                IllicitItemCategory.ILLEGAL_SUBSTANCE.value: 0.15,
                IllicitItemCategory.COUNTERFEIT.value: 0.1,
                IllicitItemCategory.SMUGGLED.value: 0.05
            }
            
            base_risk += category_risk.get(order.item_category_hint, 0.0)
            
            # Order risk level affects detection
            base_risk += order.risk_level / 10  # Up to +0.1
            
            # Security measures reduce risk
            security_reduction = illicit_op.security_level / 50  # Up to -0.2
            
            # Final risk
            detection_risk = max(0.01, min(0.9, base_risk - security_reduction))
            
            # Roll for detection
            is_detected = random.random() <= detection_risk
            
            if is_detected:
                # Order completion was detected
                
                # Update heat level
                self.black_market_service._update_heat_level(
                    db,
                    business.location_id,
                    {
                        "current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.7,
                        "recent_incidents": self.black_market_service._get_or_create_heat_level(db, business.location_id).recent_incidents + 1
                    }
                )
                
                # Update player criminal record
                criminal_record = self.black_market_service._get_or_create_criminal_record(db, player_id)
                
                known_crimes = criminal_record.known_crimes.copy()
                known_crimes.append({
                    "date": datetime.utcnow().isoformat(),
                    "type": "illicit_custom_order",
                    "location_id": business.location_id,
                    "business_id": business_id,
                    "item_category": order.item_category_hint,
                    "value": order.offered_price_initial
                })
                
                self.black_market_service._update_criminal_record(
                    db,
                    player_id,
                    {
                        "notoriety": criminal_record.notoriety + 0.4,
                        "known_crimes": known_crimes,
                        "suspected_by_regions": list(set(criminal_record.suspected_by_regions + [business.location_id]))
                    }
                )
                
                # Determine consequences
                consequence_roll = random.random()
                
                if consequence_roll < 0.3:
                    # Minor consequences - order confiscation
                    consequence = {
                        "type": "confiscation",
                        "severity": "minor",
                        "details": "Authorities confiscated the illicit order."
                    }
                    
                elif consequence_roll < 0.7:
                    # Moderate consequences - confiscation and fine
                    fine_amount = order.offered_price_initial * 0.5
                    
                    consequence = {
                        "type": "confiscation_and_fine",
                        "severity": "moderate",
                        "fine_amount": fine_amount,
                        "details": f"Authorities confiscated the order and issued a fine of {fine_amount} gold."
                    }
                    
                    # Apply fine
                    update_business(db, business_id, {
                        "current_capital": max(0, business.current_capital - fine_amount)
                    })
                    
                else:
                    # Severe consequences - confiscation, fine, and customer investigation
                    fine_amount = order.offered_price_initial * 1.0
                    
                    consequence = {
                        "type": "confiscation_fine_and_investigation",
                        "severity": "severe",
                        "fine_amount": fine_amount,
                        "details": f"Authorities confiscated the order, issued a fine of {fine_amount} gold, and are investigating your customer."
                    }
                    
                    # Apply fine
                    update_business(db, business_id, {
                        "current_capital": max(0, business.current_capital - fine_amount)
                    })
                
                # Update order status
                order.status = "failed"
                order.custom_data = {
                    **(order.custom_data or {}),
                    "failed_date": datetime.utcnow().isoformat(),
                    "failed_reason": "Detected by authorities",
                    "consequence": consequence
                }
                
                db.commit()
                
                return {
                    "success": False,
                    "detected": True,
                    "message": "Your illicit custom order completion was discovered by authorities!",
                    "order_id": order_id,
                    "new_status": "failed",
                    "consequence": consequence
                }
                
            else:
                # Successful completion
                
                # Update order status
                order.status = "completed"
                order.custom_data = {
                    **(order.custom_data or {}),
                    "completed_date": datetime.utcnow().isoformat(),
                    "completion_details": action_details
                }
                
                # Add payment to business
                update_business(db, business_id, {
                    "current_capital": business.current_capital + order.offered_price_initial
                })
                
                # Record transaction
                record_financial_transaction(
                    db,
                    {
                        "business_id": business_id,
                        "transaction_type": "income",
                        "amount": order.offered_price_initial,
                        "description": "Custom order payment",
                        "timestamp": datetime.utcnow().isoformat(),
                        "related_entity_id": order.requesting_npc_id,
                        "custom_data": {
                            "illicit_order": True,
                            "order_id": order_id,
                            "item_category": order.item_category_hint
                        }
                    }
                )
                
                # Record black market transaction
                black_market_tx = DBBlackMarketTransaction(
                    id=str(uuid4()),
                    business_id=business_id,
                    player_id=player_id,
                    contact_npc_id=order.requesting_npc_id,
                    transaction_type="custom_order",
                    total_price=order.offered_price_initial,
                    location_id=business.location_id,
                    risk_taken=detection_risk,
                    was_detected=False,
                    custom_data={
                        "order_id": order_id,
                        "item_category": order.item_category_hint,
                        "item_description": order.item_description_by_npc,
                        "through_business": True
                    }
                )
                db.add(black_market_tx)
                
                # Slightly increase regional heat
                self.black_market_service._update_heat_level(
                    db,
                    business.location_id,
                    {"current_heat": self.black_market_service._get_or_create_heat_level(db, business.location_id).current_heat + 0.1}
                )
                
                # Increase notoriety
                self.black_market_service._update_criminal_record(
                    db,
                    player_id,
                    {"notoriety": self.black_market_service._get_or_create_criminal_record(db, player_id).notoriety + 0.3}
                )
                
                db.commit()
                
                return {
                    "success": True,
                    "message": f"Successfully completed illicit custom order for {order.offered_price_initial} gold.",
                    "order_id": order_id,
                    "new_status": "completed",
                    "payment": order.offered_price_initial,
                    "risk_taken": detection_risk,
                    "transaction_id": black_market_tx.id
                }
                
        else:
            raise ValueError(f"Unknown action: {action}")
    
    # === HELPER METHODS ===
    
    def _get_or_create_illicit_operation(
        self,
        db: Session,
        business_id: str
    ) -> DBIllicitBusinessOperation:
        """Get or create illicit operation for a business."""
        illicit_op = db.query(DBIllicitBusinessOperation).filter(
            DBIllicitBusinessOperation.business_id == business_id
        ).first()
        
        if not illicit_op:
            # Create new illicit operation
            illicit_op = DBIllicitBusinessOperation(
                id=str(uuid4()),
                business_id=business_id,
                is_active=False,
                hidden_capacity=10,
                security_level=1,
                security_measures=[],
                laundering_efficiency=0.85,
                known_black_market_contacts=[],
                bribed_officials=[],
                custom_data={}
            )
            db.add(illicit_op)
            db.commit()
            
        return illicit_op