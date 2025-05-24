"""
Business Development Service

This module provides services for business development activities such as
research, upgrades, expansion, and reputation building.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4

from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, ResearchProject, BusinessFixtureOrUpgrade,
    BusinessExpansionProposal, BusinessReputation, ShopAmbiance,
    TransactionType
)
from backend.src.business.crud import (
    get_business, update_business, get_research_project, 
    get_research_projects_by_business, update_research_project,
    get_business_fixture, get_business_fixtures_by_business,
    record_financial_transaction
)

logger = logging.getLogger(__name__)

class BusinessDevelopmentService:
    """Service for business development, research, upgrades, and expansion."""
    
    def __init__(self):
        self.logger = logging.getLogger("BusinessDevelopmentService")
    
    # === RESEARCH METHODS ===
    
    def initiate_research_project(
        self,
        db: Session,
        business_id: str,
        research_subject: str,
        description: str,
        time_investment_hours: int,
        required_materials: Optional[Dict[str, int]] = None,
        required_skills: Optional[Dict[str, int]] = None,
        cost_currency: float = 0.0,
        player_skill_level: int = 1
    ) -> ResearchProject:
        """
        Initiate a research project for new recipes, techniques, or products.
        
        Args:
            db: Database session
            business_id: Business profile ID
            research_subject: Subject of research
            description: Detailed description
            time_investment_hours: Expected hours to complete
            required_materials: Optional required materials and quantities
            required_skills: Optional required skills and levels
            cost_currency: Optional currency cost
            player_skill_level: Player's relevant skill level (1-10)
            
        Returns:
            Created research project
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Validate required materials if provided
        if required_materials:
            inventory = business.inventory or {}
            for item_id, quantity in required_materials.items():
                if item_id not in inventory or inventory[item_id]["quantity"] < quantity:
                    raise ValueError(f"Not enough of material {item_id} in inventory")
        
        # Validate skills if provided
        if required_skills:
            # This would normally check against player character skills
            # For now, we'll just validate against the player_skill_level
            max_required_skill = max(required_skills.values()) if required_skills else 0
            if max_required_skill > player_skill_level:
                self.logger.warning(f"Player skill level {player_skill_level} may be too low for required skill level {max_required_skill}")
        
        # Adjust time based on player skill
        skill_modifier = 1.0 - (player_skill_level - 1) * 0.05  # 5% reduction per skill level
        adjusted_time = max(1, int(time_investment_hours * skill_modifier))
        
        # Create research project
        research_data = {
            "id": f"research-{uuid4().hex}",
            "player_business_profile_id": business_id,
            "research_subject": research_subject,
            "description": description,
            "required_materials": required_materials or {},
            "required_skills": required_skills or {},
            "time_investment_hours": adjusted_time,
            "start_date": datetime.utcnow(),
            "completion_date": None,
            "current_progress_percentage": 0.0,
            "results_description": None,
            "unlocked_recipe_ids": [],
            "unlocked_technique_ids": [],
            "is_completed": False,
            "cost_currency": cost_currency,
            "custom_data": {
                "initiation_date": datetime.utcnow().isoformat(),
                "adjusted_time_factor": skill_modifier,
                "estimated_completion_date": (datetime.utcnow() + timedelta(hours=adjusted_time)).isoformat()
            }
        }
        
        # Record the cost transaction if applicable
        if cost_currency > 0:
            record_financial_transaction(
                db=db,
                business_id=business_id,
                transaction_type=TransactionType.OTHER,
                amount=cost_currency,
                description=f"Research investment: {research_subject}",
                is_income=False,
                category="research_investment"
            )
            
            # Update business balance
            update_business(db, business_id, {
                "current_balance": business.current_balance - cost_currency,
                "total_expenses": business.total_expenses + cost_currency
            })
        
        # Consume materials if required
        if required_materials:
            inventory = business.inventory.copy()
            for item_id, quantity in required_materials.items():
                inventory[item_id]["quantity"] -= quantity
            
            # Update business inventory
            update_business(db, business_id, {"inventory": inventory})
        
        # Add to business research projects
        active_research_projects = business.active_research_projects or []
        active_research_projects.append(research_data["id"])
        update_business(db, business_id, {"active_research_projects": active_research_projects})
        
        # In a real implementation, this would create the research project in the database
        # and potentially set up a timer or events for progress updates
        
        self.logger.info(f"Initiated research project {research_data['id']} for business {business_id}: {research_subject}")
        
        # Return as ResearchProject model
        return ResearchProject(**research_data)
    
    def progress_research_project(
        self,
        db: Session,
        research_id: str,
        hours_invested: float,
        materials_used: Optional[Dict[str, int]] = None,
        player_skill_level: int = 1,
        progress_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the progress of a research project.
        
        Args:
            db: Database session
            research_id: Research project ID
            hours_invested: Hours invested in this progress update
            materials_used: Optional additional materials used
            player_skill_level: Player's relevant skill level (1-10)
            progress_notes: Optional notes on the progress
            
        Returns:
            Dictionary with progress update results
        """
        # Get the research project
        research = get_research_project(db, research_id)
        if not research:
            raise ValueError(f"Research project {research_id} not found")
            
        # Check if already completed
        if research.is_completed:
            raise ValueError(f"Research project {research_id} is already completed")
            
        # Get the business
        business = get_business(db, research.player_business_profile_id)
        if not business:
            raise ValueError(f"Business {research.player_business_profile_id} not found")
            
        # Consume additional materials if used
        if materials_used:
            inventory = business.inventory.copy()
            for item_id, quantity in materials_used.items():
                if item_id not in inventory or inventory[item_id]["quantity"] < quantity:
                    raise ValueError(f"Not enough of material {item_id} in inventory")
                    
                inventory[item_id]["quantity"] -= quantity
            
            # Update business inventory
            update_business(db, research.player_business_profile_id, {"inventory": inventory})
        
        # Calculate progress increase
        base_progress_percentage = (hours_invested / research.time_investment_hours) * 100
        
        # Adjust based on skill level
        skill_modifier = 1.0 + (player_skill_level - 1) * 0.05  # 5% bonus per skill level
        progress_percentage_increase = base_progress_percentage * skill_modifier
        
        # Calculate new progress
        current_progress = research.current_progress_percentage
        new_progress = min(100.0, current_progress + progress_percentage_increase)
        
        # Check if research is now complete
        is_completed = new_progress >= 100.0
        completion_date = datetime.utcnow() if is_completed else None
        
        # Generate results if completed
        results_description = None
        unlocked_recipe_ids = []
        unlocked_technique_ids = []
        
        if is_completed:
            # Generate appropriate research results based on subject and business type
            results, recipes, techniques = self._generate_research_results(
                research.research_subject, 
                business.business_type,
                player_skill_level
            )
            
            results_description = results
            unlocked_recipe_ids = recipes
            unlocked_technique_ids = techniques
        
        # Update research project
        update_data = {
            "current_progress_percentage": new_progress,
            "is_completed": is_completed
        }
        
        if completion_date:
            update_data["completion_date"] = completion_date
            
        if results_description:
            update_data["results_description"] = results_description
            
        if unlocked_recipe_ids:
            update_data["unlocked_recipe_ids"] = unlocked_recipe_ids
            
        if unlocked_technique_ids:
            update_data["unlocked_technique_ids"] = unlocked_technique_ids
            
        # Update custom data with progress log
        custom_data = research.custom_data or {}
        progress_log = custom_data.get("progress_log", [])
        
        progress_entry = {
            "date": datetime.utcnow().isoformat(),
            "hours_invested": hours_invested,
            "materials_used": materials_used,
            "progress_increase": progress_percentage_increase,
            "new_progress": new_progress,
            "notes": progress_notes
        }
        
        progress_log.append(progress_entry)
        custom_data["progress_log"] = progress_log
        
        if is_completed:
            custom_data["completion_summary"] = {
                "total_hours": sum(entry["hours_invested"] for entry in progress_log),
                "completion_date": completion_date.isoformat(),
                "unlocked_recipes_count": len(unlocked_recipe_ids),
                "unlocked_techniques_count": len(unlocked_technique_ids)
            }
        
        update_data["custom_data"] = custom_data
        
        # In a real implementation, this would update the research project in the database
        # For now, just return the update results
        
        # Create progress update result
        progress_result = {
            "research_id": research_id,
            "previous_progress": current_progress,
            "new_progress": new_progress,
            "progress_increase": progress_percentage_increase,
            "hours_invested": hours_invested,
            "materials_used": materials_used,
            "is_completed": is_completed
        }
        
        if is_completed:
            progress_result["completion_date"] = completion_date.isoformat()
            progress_result["results_description"] = results_description
            progress_result["unlocked_recipe_ids"] = unlocked_recipe_ids
            progress_result["unlocked_technique_ids"] = unlocked_technique_ids
        
        self.logger.info(f"Updated research project {research_id} progress: {new_progress:.1f}%, " +
                        f"completed: {is_completed}")
        
        return progress_result
    
    def _generate_research_results(
        self, 
        research_subject: str, 
        business_type: str,
        player_skill_level: int
    ) -> Tuple[str, List[str], List[str]]:
        """
        Generate research results based on subject and business type.
        
        Args:
            research_subject: Subject of research
            business_type: Type of business
            player_skill_level: Player's skill level
            
        Returns:
            Tuple of (results description, unlocked recipe IDs, unlocked technique IDs)
        """
        # This would be much more sophisticated in a real implementation
        # For now, generate some basic results
        
        # Number of recipes/techniques based on skill level
        num_recipes = max(1, player_skill_level // 3)
        num_techniques = max(1, player_skill_level // 4)
        
        # Generate recipe IDs
        recipe_ids = [f"recipe-{research_subject.lower().replace(' ', '-')}-{i+1}" for i in range(num_recipes)]
        
        # Generate technique IDs
        technique_ids = [f"technique-{research_subject.lower().replace(' ', '-')}-{i+1}" for i in range(num_techniques)]
        
        # Generate results description
        results = f"Your research into {research_subject} has yielded valuable insights. "
        
        if recipe_ids:
            if len(recipe_ids) == 1:
                results += f"You've discovered a new recipe that you can now craft. "
            else:
                results += f"You've discovered {len(recipe_ids)} new recipes that you can now craft. "
                
        if technique_ids:
            if len(technique_ids) == 1:
                results += f"You've also developed a new technique that improves your crafting efficiency. "
            else:
                results += f"You've also developed {len(technique_ids)} new techniques that improve your crafting efficiency. "
                
        # Add business-specific flavor
        if business_type == "blacksmith":
            results += "The forge will be much more productive with these innovations."
        elif business_type == "apothecary":
            results += "Your understanding of alchemical principles has deepened considerably."
        elif business_type == "tailor":
            results += "Your designs will stand out with these new techniques."
        else:
            results += "These discoveries will help set your business apart from competitors."
            
        return results, recipe_ids, technique_ids
    
    def get_research_summary(
        self,
        db: Session,
        business_id: str,
        include_completed: bool = True
    ) -> Dict[str, Any]:
        """
        Get a summary of all research projects for a business.
        
        Args:
            db: Database session
            business_id: Business profile ID
            include_completed: Whether to include completed projects
            
        Returns:
            Dictionary with research summary
        """
        # Get research projects
        research_projects = get_research_projects_by_business(db, business_id, include_completed)
        
        # Create summary
        summary = {
            "business_id": business_id,
            "active_projects": [],
            "completed_projects": [],
            "total_active": 0,
            "total_completed": 0,
            "total_recipes_unlocked": 0,
            "total_techniques_unlocked": 0,
            "total_investment": 0.0,
            "recommended_research": self._get_recommended_research(db, business_id)
        }
        
        # Process each project
        for project in research_projects:
            project_summary = {
                "id": project.id,
                "subject": project.research_subject,
                "progress": project.current_progress_percentage,
                "time_invested": project.time_investment_hours,
                "start_date": project.start_date.isoformat() if project.start_date else None,
                "cost": project.cost_currency
            }
            
            summary["total_investment"] += project.cost_currency
            
            if project.is_completed:
                project_summary["completion_date"] = project.completion_date.isoformat() if project.completion_date else None
                project_summary["results"] = project.results_description
                project_summary["unlocked_recipes"] = project.unlocked_recipe_ids
                project_summary["unlocked_techniques"] = project.unlocked_technique_ids
                
                summary["completed_projects"].append(project_summary)
                summary["total_completed"] += 1
                summary["total_recipes_unlocked"] += len(project.unlocked_recipe_ids)
                summary["total_techniques_unlocked"] += len(project.unlocked_technique_ids)
            else:
                project_summary["estimated_completion"] = project.custom_data.get("estimated_completion_date") if project.custom_data else None
                summary["active_projects"].append(project_summary)
                summary["total_active"] += 1
        
        # Sort projects by date
        summary["active_projects"].sort(key=lambda p: p["start_date"], reverse=True)
        summary["completed_projects"].sort(key=lambda p: p["completion_date"], reverse=True)
        
        self.logger.info(f"Generated research summary for business {business_id}")
        
        return summary
    
    def _get_recommended_research(
        self,
        db: Session,
        business_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get recommended research topics based on business type and current state.
        
        Args:
            db: Database session
            business_id: Business profile ID
            
        Returns:
            List of recommended research topics
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            return []
            
        # Get current research projects
        current_projects = get_research_projects_by_business(db, business_id, include_completed=True)
        
        # Extract current research subjects to avoid duplicates
        current_subjects = [p.research_subject.lower() for p in current_projects]
        
        # Generate recommendations based on business type
        recommendations = []
        
        if business.business_type == "blacksmith":
            possible_research = [
                {"subject": "Advanced Forging Techniques", "description": "Research more efficient ways to forge metal items.", "difficulty": 4},
                {"subject": "Steel Alloy Improvements", "description": "Develop better steel alloys for stronger weapons and tools.", "difficulty": 6},
                {"subject": "Decorative Metalwork", "description": "Learn how to create more ornate and valuable decorated items.", "difficulty": 5},
                {"subject": "Tool Durability Enhancement", "description": "Find ways to make tools last longer and maintain their edge.", "difficulty": 4},
                {"subject": "Armor Weight Reduction", "description": "Research methods to create lighter but equally protective armor.", "difficulty": 7}
            ]
        elif business.business_type == "apothecary":
            possible_research = [
                {"subject": "Healing Potion Potency", "description": "Improve the effectiveness of healing potions.", "difficulty": 5},
                {"subject": "Rare Herb Substitutions", "description": "Find ways to substitute common herbs for rare ones in recipes.", "difficulty": 4},
                {"subject": "Extended Shelf Life", "description": "Develop preservation techniques for perishable ingredients.", "difficulty": 3},
                {"subject": "Poison Neutralization", "description": "Research antidotes for common and exotic poisons.", "difficulty": 6},
                {"subject": "Alchemical Distillation", "description": "Improve distillation process for creating purer substances.", "difficulty": 7}
            ]
        elif business.business_type == "tailor":
            possible_research = [
                {"subject": "Waterproof Treatments", "description": "Develop treatments to make fabric water resistant.", "difficulty": 4},
                {"subject": "Reinforced Stitching", "description": "Create stronger seams for hardier clothing.", "difficulty": 3},
                {"subject": "Luxury Fabric Blends", "description": "Research blending techniques for creating premium fabrics.", "difficulty": 5},
                {"subject": "Dye Fastness Improvement", "description": "Find ways to make dyes more colorfast and vibrant.", "difficulty": 4},
                {"subject": "Heat-Resistant Materials", "description": "Develop fabrics that provide protection from heat.", "difficulty": 6}
            ]
        else:
            # Generic research options for other business types
            possible_research = [
                {"subject": "Production Efficiency", "description": "Research ways to produce goods more efficiently.", "difficulty": 4},
                {"subject": "Material Conservation", "description": "Find methods to reduce material waste in production.", "difficulty": 3},
                {"subject": "Quality Improvement Processes", "description": "Develop techniques to improve product quality.", "difficulty": 5},
                {"subject": "Market Trend Analysis", "description": "Study current market trends to better target products.", "difficulty": 4},
                {"subject": "Customer Experience Enhancement", "description": "Research ways to improve the customer shopping experience.", "difficulty": 3}
            ]
        
        # Filter out existing research subjects
        filtered_research = [r for r in possible_research if r["subject"].lower() not in current_subjects]
        
        # Sort by difficulty (lowest first) and take up to 3
        filtered_research.sort(key=lambda r: r["difficulty"])
        recommendations = filtered_research[:3]
        
        # Add estimated time and materials
        for recommendation in recommendations:
            # Base time on difficulty
            base_time = recommendation["difficulty"] * 5  # 5 hours per difficulty level
            
            # Generate some required materials based on the subject
            # This would be more sophisticated in a real implementation
            required_materials = {}
            if "metal" in recommendation["subject"].lower() or business.business_type == "blacksmith":
                required_materials["item-metal-ingot"] = recommendation["difficulty"]
                required_materials["item-coal"] = recommendation["difficulty"] * 2
            elif "herb" in recommendation["subject"].lower() or business.business_type == "apothecary":
                required_materials["item-herbs-common"] = recommendation["difficulty"]
                required_materials["item-glass-vial"] = max(1, recommendation["difficulty"] // 2)
            elif "fabric" in recommendation["subject"].lower() or business.business_type == "tailor":
                required_materials["item-fabric"] = recommendation["difficulty"]
                required_materials["item-thread"] = recommendation["difficulty"] * 2
            else:
                required_materials["item-paper"] = recommendation["difficulty"]
                required_materials["item-ink"] = max(1, recommendation["difficulty"] // 2)
            
            # Add to recommendation
            recommendation["estimated_time_hours"] = base_time
            recommendation["required_materials"] = required_materials
            recommendation["estimated_cost"] = recommendation["difficulty"] * 10.0  # 10 gold per difficulty level
        
        return recommendations
    
    # === FIXTURE/UPGRADE METHODS ===
    
    def purchase_business_fixture(
        self,
        db: Session,
        business_id: str,
        fixture_type_name: str,
        description: str,
        cost_currency: float,
        installation_time_hours: int,
        benefits_description: str,
        functional_bonus: Dict[str, float],
        aesthetic_bonus: Optional[float] = None,
        prerequisites_text: Optional[str] = None,
        cost_materials: Optional[Dict[str, int]] = None
    ) -> BusinessFixtureOrUpgrade:
        """
        Purchase a fixture or upgrade for the business.
        
        Args:
            db: Database session
            business_id: Business profile ID
            fixture_type_name: Type of fixture/upgrade
            description: Description of the fixture
            cost_currency: Currency cost
            installation_time_hours: Hours needed for installation
            benefits_description: Description of benefits
            functional_bonus: Dictionary mapping bonus types to values
            aesthetic_bonus: Optional aesthetic improvement value (0.0-1.0)
            prerequisites_text: Optional text describing prerequisites
            cost_materials: Optional materials required for installation
            
        Returns:
            Created fixture/upgrade
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Check if business has enough funds
        if business.current_balance < cost_currency:
            raise ValueError(f"Not enough funds. Needed: {cost_currency}, Available: {business.current_balance}")
            
        # Check for materials if required
        if cost_materials:
            inventory = business.inventory or {}
            for item_id, quantity in cost_materials.items():
                if item_id not in inventory or inventory[item_id]["quantity"] < quantity:
                    raise ValueError(f"Not enough of material {item_id} in inventory")
        
        # Create fixture
        fixture_data = {
            "id": f"fixture-{uuid4().hex}",
            "player_business_profile_id": business_id,
            "fixture_type_name": fixture_type_name,
            "description": description,
            "cost_materials": cost_materials or {},
            "cost_currency": cost_currency,
            "installation_time_hours": installation_time_hours,
            "prerequisites_text": prerequisites_text,
            "benefits_description": benefits_description,
            "is_installed_and_active": False,
            "condition_percentage": 100.0,
            "purchase_date": datetime.utcnow(),
            "installation_date": None,
            "last_maintenance_date": None,
            "functional_bonus": functional_bonus,
            "aesthetic_bonus": aesthetic_bonus,
            "custom_data": {
                "purchase_date": datetime.utcnow().isoformat(),
                "estimated_installation_completion": (datetime.utcnow() + timedelta(hours=installation_time_hours)).isoformat()
            }
        }
        
        # Record the purchase transaction
        record_financial_transaction(
            db=db,
            business_id=business_id,
            transaction_type=TransactionType.UPGRADE,
            amount=cost_currency,
            description=f"Purchase of {fixture_type_name}",
            is_income=False,
            category="upgrades"
        )
        
        # Update business balance
        update_business(db, business_id, {
            "current_balance": business.current_balance - cost_currency,
            "total_expenses": business.total_expenses + cost_currency
        })
        
        # Consume materials if required
        if cost_materials:
            inventory = business.inventory.copy()
            for item_id, quantity in cost_materials.items():
                inventory[item_id]["quantity"] -= quantity
            
            # Update business inventory
            update_business(db, business_id, {"inventory": inventory})
        
        # Add to business fixtures
        installed_fixtures = business.installed_fixtures or []
        installed_fixtures.append(fixture_data["id"])
        update_business(db, business_id, {"installed_fixtures": installed_fixtures})
        
        # In a real implementation, this would create the fixture in the database
        
        self.logger.info(f"Purchased fixture {fixture_data['id']} for business {business_id}: {fixture_type_name}")
        
        # Return as BusinessFixtureOrUpgrade model
        return BusinessFixtureOrUpgrade(**fixture_data)
    
    def install_business_fixture(
        self,
        db: Session,
        fixture_id: str,
        hours_spent: float,
        installation_notes: Optional[str] = None,
        skill_level: int = 1
    ) -> Dict[str, Any]:
        """
        Install a purchased fixture or upgrade.
        
        Args:
            db: Database session
            fixture_id: Fixture ID
            hours_spent: Hours spent on installation
            installation_notes: Optional notes on installation
            skill_level: Relevant skill level for installation (1-10)
            
        Returns:
            Dictionary with installation results
        """
        # Get the fixture
        fixture = get_business_fixture(db, fixture_id)
        if not fixture:
            raise ValueError(f"Fixture {fixture_id} not found")
            
        # Check if already installed
        if fixture.is_installed_and_active:
            raise ValueError(f"Fixture {fixture_id} is already installed")
            
        # Get the business
        business = get_business(db, fixture.player_business_profile_id)
        if not business:
            raise ValueError(f"Business {fixture.player_business_profile_id} not found")
            
        # Calculate progress percentage
        total_hours_needed = fixture.installation_time_hours
        
        # Adjust based on skill level
        skill_modifier = 1.0 + (skill_level - 1) * 0.05  # 5% bonus per skill level
        effective_hours = hours_spent * skill_modifier
        
        # Get current progress from custom data
        custom_data = fixture.custom_data or {}
        installation_log = custom_data.get("installation_log", [])
        hours_already_spent = sum(entry["hours_spent"] for entry in installation_log) if installation_log else 0
        
        # Add new entry to installation log
        installation_entry = {
            "date": datetime.utcnow().isoformat(),
            "hours_spent": hours_spent,
            "effective_hours": effective_hours,
            "notes": installation_notes
        }
        
        installation_log.append(installation_entry)
        custom_data["installation_log"] = installation_log
        
        # Calculate total progress
        total_hours_spent = hours_already_spent + effective_hours
        progress_percentage = min(100.0, (total_hours_spent / total_hours_needed) * 100)
        
        # Check if installation is complete
        is_completed = progress_percentage >= 100.0
        installation_date = datetime.utcnow() if is_completed else None
        
        # Update fixture
        update_data = {
            "custom_data": custom_data
        }
        
        if is_completed:
            update_data["is_installed_and_active"] = True
            update_data["installation_date"] = installation_date
            
            # Apply benefits to business
            self._apply_fixture_benefits(db, business, fixture)
        
        # In a real implementation, this would update the fixture in the database
        
        # Create installation result
        installation_result = {
            "fixture_id": fixture_id,
            "hours_spent": hours_spent,
            "effective_hours": effective_hours,
            "total_hours_spent": total_hours_spent,
            "progress_percentage": progress_percentage,
            "is_completed": is_completed
        }
        
        if is_completed:
            installation_result["installation_date"] = installation_date.isoformat()
            installation_result["benefits_applied"] = fixture.functional_bonus
            
            if fixture.aesthetic_bonus:
                installation_result["aesthetic_improvement"] = fixture.aesthetic_bonus
        
        self.logger.info(f"Updated fixture {fixture_id} installation progress: {progress_percentage:.1f}%, " +
                        f"completed: {is_completed}")
        
        return installation_result
    
    def _apply_fixture_benefits(
        self,
        db: Session,
        business: PlayerBusinessProfile,
        fixture: BusinessFixtureOrUpgrade
    ) -> None:
        """
        Apply the benefits of a fixture to the business.
        
        Args:
            db: Database session
            business: Business profile
            fixture: Installed fixture
        """
        # Apply functional bonuses
        # In a real implementation, these would affect various business operations
        
        # Apply aesthetic bonus if applicable
        if fixture.aesthetic_bonus:
            # Update shop ambiance
            ambiance = business.ambiance or {}
            
            # Increase relevant ambiance factors
            if "forge" in fixture.fixture_type_name.lower() or "anvil" in fixture.fixture_type_name.lower():
                ambiance["organization"] = min(10, ambiance.get("organization", 5) + 1)
            elif "counter" in fixture.fixture_type_name.lower() or "display" in fixture.fixture_type_name.lower():
                ambiance["customer_comfort"] = min(10, ambiance.get("customer_comfort", 5) + 1)
            elif "decor" in fixture.fixture_type_name.lower():
                ambiance["decor_quality"] = min(10, ambiance.get("decor_quality", 5) + 1)
            elif "light" in fixture.fixture_type_name.lower():
                ambiance["lighting"] = min(10, ambiance.get("lighting", 5) + 1)
            
            # Add to unique features if appropriate
            if "unique" in fixture.fixture_type_name.lower() or "rare" in fixture.fixture_type_name.lower():
                unique_features = ambiance.get("unique_features", [])
                unique_features.append(fixture.fixture_type_name)
                ambiance["unique_features"] = unique_features
            
            # Recalculate overall ambiance rating
            factors = ["cleanliness", "decor_quality", "lighting", "organization", "customer_comfort"]
            total = sum(ambiance.get(factor, 5) for factor in factors)
            ambiance["overall_ambiance_rating"] = min(10, max(1, total // len(factors)))
            
            # Update last updated date
            ambiance["last_updated"] = datetime.utcnow().isoformat()
            
            # Update business ambiance
            update_business(db, business.id, {"ambiance": ambiance})
    
    def perform_fixture_maintenance(
        self,
        db: Session,
        fixture_id: str,
        maintenance_cost: float,
        hours_spent: float,
        materials_used: Optional[Dict[str, int]] = None,
        maintenance_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform maintenance on a business fixture.
        
        Args:
            db: Database session
            fixture_id: Fixture ID
            maintenance_cost: Currency cost of maintenance
            hours_spent: Hours spent on maintenance
            materials_used: Optional materials used for maintenance
            maintenance_notes: Optional notes on maintenance
            
        Returns:
            Dictionary with maintenance results
        """
        # Get the fixture
        fixture = get_business_fixture(db, fixture_id)
        if not fixture:
            raise ValueError(f"Fixture {fixture_id} not found")
            
        # Check if installed
        if not fixture.is_installed_and_active:
            raise ValueError(f"Fixture {fixture_id} is not installed")
            
        # Get the business
        business = get_business(db, fixture.player_business_profile_id)
        if not business:
            raise ValueError(f"Business {fixture.player_business_profile_id} not found")
            
        # Check if business has enough funds
        if business.current_balance < maintenance_cost:
            raise ValueError(f"Not enough funds. Needed: {maintenance_cost}, Available: {business.current_balance}")
            
        # Check for materials if required
        if materials_used:
            inventory = business.inventory or {}
            for item_id, quantity in materials_used.items():
                if item_id not in inventory or inventory[item_id]["quantity"] < quantity:
                    raise ValueError(f"Not enough of material {item_id} in inventory")
        
        # Record the maintenance transaction
        record_financial_transaction(
            db=db,
            business_id=business.id,
            transaction_type=TransactionType.MAINTENANCE,
            amount=maintenance_cost,
            description=f"Maintenance for {fixture.fixture_type_name}",
            is_income=False,
            category="maintenance"
        )
        
        # Update business balance
        update_business(db, business.id, {
            "current_balance": business.current_balance - maintenance_cost,
            "total_expenses": business.total_expenses + maintenance_cost
        })
        
        # Consume materials if used
        if materials_used:
            inventory = business.inventory.copy()
            for item_id, quantity in materials_used.items():
                inventory[item_id]["quantity"] -= quantity
            
            # Update business inventory
            update_business(db, business.id, {"inventory": inventory})
        
        # Calculate condition improvement
        old_condition = fixture.condition_percentage
        
        # Basic condition improvement based on hours spent and materials
        condition_improvement = min(100 - old_condition, hours_spent * 5)
        
        if materials_used:
            # More materials = better improvement
            condition_improvement += min(100 - old_condition - condition_improvement, 
                                       sum(materials_used.values()) * 2)
        
        # Cap at 100%
        new_condition = min(100, old_condition + condition_improvement)
        
        # Update fixture
        custom_data = fixture.custom_data or {}
        maintenance_log = custom_data.get("maintenance_log", [])
        
        maintenance_entry = {
            "date": datetime.utcnow().isoformat(),
            "cost": maintenance_cost,
            "hours_spent": hours_spent,
            "materials_used": materials_used,
            "condition_before": old_condition,
            "condition_after": new_condition,
            "notes": maintenance_notes
        }
        
        maintenance_log.append(maintenance_entry)
        custom_data["maintenance_log"] = maintenance_log
        
        update_data = {
            "condition_percentage": new_condition,
            "last_maintenance_date": datetime.utcnow(),
            "custom_data": custom_data
        }
        
        # In a real implementation, this would update the fixture in the database
        
        # Create maintenance result
        maintenance_result = {
            "fixture_id": fixture_id,
            "fixture_name": fixture.fixture_type_name,
            "maintenance_date": datetime.utcnow().isoformat(),
            "cost": maintenance_cost,
            "hours_spent": hours_spent,
            "materials_used": materials_used,
            "condition_before": old_condition,
            "condition_after": new_condition,
            "condition_improvement": condition_improvement
        }
        
        self.logger.info(f"Performed maintenance on fixture {fixture_id}, condition improved from " +
                        f"{old_condition:.1f}% to {new_condition:.1f}%")
        
        return maintenance_result
    
    def get_fixtures_summary(
        self,
        db: Session,
        business_id: str
    ) -> Dict[str, Any]:
        """
        Get a summary of all fixtures for a business.
        
        Args:
            db: Database session
            business_id: Business profile ID
            
        Returns:
            Dictionary with fixtures summary
        """
        # Get fixtures
        fixtures = get_business_fixtures_by_business(db, business_id)
        
        # Create summary
        summary = {
            "business_id": business_id,
            "total_fixtures": len(fixtures),
            "installed_fixtures": [],
            "pending_installation": [],
            "fixtures_needing_maintenance": [],
            "total_investment": 0.0,
            "functional_bonuses": {},
            "aesthetic_improvement": 0.0
        }
        
        # Process each fixture
        for fixture in fixtures:
            fixture_summary = {
                "id": fixture.id,
                "type_name": fixture.fixture_type_name,
                "description": fixture.description,
                "cost": fixture.cost_currency,
                "condition": fixture.condition_percentage
            }
            
            summary["total_investment"] += fixture.cost_currency
            
            # Track functional bonuses
            for bonus_type, bonus_value in fixture.functional_bonus.items():
                if bonus_type not in summary["functional_bonuses"]:
                    summary["functional_bonuses"][bonus_type] = 0.0
                    
                # Only count if installed and active
                if fixture.is_installed_and_active:
                    summary["functional_bonuses"][bonus_type] += bonus_value
            
            # Track aesthetic improvement
            if fixture.aesthetic_bonus and fixture.is_installed_and_active:
                summary["aesthetic_improvement"] += fixture.aesthetic_bonus
            
            if fixture.is_installed_and_active:
                fixture_summary["installation_date"] = fixture.installation_date.isoformat() if fixture.installation_date else None
                fixture_summary["last_maintenance_date"] = fixture.last_maintenance_date.isoformat() if fixture.last_maintenance_date else None
                
                summary["installed_fixtures"].append(fixture_summary)
                
                # Check if needs maintenance
                if fixture.condition_percentage < 70:
                    summary["fixtures_needing_maintenance"].append(fixture_summary)
            else:
                # Not installed yet
                if "installation_log" in fixture.custom_data:
                    # Installation in progress
                    installation_log = fixture.custom_data["installation_log"]
                    hours_spent = sum(entry["hours_spent"] for entry in installation_log)
                    progress = min(100, (hours_spent / fixture.installation_time_hours) * 100)
                    
                    fixture_summary["installation_progress"] = progress
                    fixture_summary["hours_spent"] = hours_spent
                    fixture_summary["hours_remaining"] = max(0, fixture.installation_time_hours - hours_spent)
                
                summary["pending_installation"].append(fixture_summary)
        
        # Sort by condition (ascending) and installation date (descending)
        summary["installed_fixtures"].sort(key=lambda f: (f["condition"], 
                                                        f.get("installation_date", ""), 
                                                        f["type_name"]))
        
        summary["fixtures_needing_maintenance"].sort(key=lambda f: f["condition"])
        
        # Sort pending by progress (descending)
        summary["pending_installation"].sort(key=lambda f: f.get("installation_progress", 0), reverse=True)
        
        self.logger.info(f"Generated fixtures summary for business {business_id}")
        
        return summary
    
    # === EXPANSION AND REPUTATION METHODS ===
    
    def propose_business_expansion(
        self,
        db: Session,
        business_id: str,
        expansion_type: str,
        description: str,
        estimated_cost: float,
        estimated_construction_time_days: int,
        benefits_description: str,
        required_permits: Optional[List[str]] = None
    ) -> BusinessExpansionProposal:
        """
        Propose an expansion for the business.
        
        Args:
            db: Database session
            business_id: Business profile ID
            expansion_type: Type of expansion
            description: Detailed description
            estimated_cost: Estimated cost
            estimated_construction_time_days: Estimated construction time
            benefits_description: Description of benefits
            required_permits: Optional list of required permits
            
        Returns:
            Created expansion proposal
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Create proposal
        proposal_data = {
            "id": f"expansion-{uuid4().hex}",
            "player_business_profile_id": business_id,
            "expansion_type": expansion_type,
            "description": description,
            "estimated_cost": estimated_cost,
            "required_permits": required_permits or [],
            "estimated_construction_time_days": estimated_construction_time_days,
            "benefits_description": benefits_description,
            "proposal_date": datetime.utcnow(),
            "approval_status": "pending",
            "approval_authority_npc_id": None,
            "construction_project_id": None,
            "custom_data": {
                "proposal_date": datetime.utcnow().isoformat(),
                "proposing_player_id": business.player_character_id
            }
        }
        
        # In a real implementation, this would create the proposal in the database
        # and potentially trigger approval process
        
        self.logger.info(f"Created expansion proposal {proposal_data['id']} for business {business_id}: {expansion_type}")
        
        # Return as BusinessExpansionProposal model
        return BusinessExpansionProposal(**proposal_data)
    
    def build_business_reputation(
        self,
        db: Session,
        business_id: str,
        action_type: str,
        description: str,
        cost: Optional[float] = None,
        target_audience: Optional[str] = None,
        hours_invested: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Take actions to build business reputation in the community.
        
        Args:
            db: Database session
            business_id: Business profile ID
            action_type: Type of reputation-building action
            description: Description of the action
            cost: Optional currency cost
            target_audience: Optional target audience (e.g., "nobles", "commoners", "guild")
            hours_invested: Optional hours invested
            
        Returns:
            Dictionary with reputation impact results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Check if business has enough funds if cost provided
        if cost and business.current_balance < cost:
            raise ValueError(f"Not enough funds. Needed: {cost}, Available: {business.current_balance}")
        
        # Process the payment if there is a cost
        if cost and cost > 0:
            # Record the transaction
            record_financial_transaction(
                db=db,
                business_id=business_id,
                transaction_type=TransactionType.DONATION if action_type == "charity" else TransactionType.OTHER,
                amount=cost,
                description=f"Reputation building: {description}",
                is_income=False,
                category="reputation_building"
            )
            
            # Update business balance
            update_business(db, business_id, {
                "current_balance": business.current_balance - cost,
                "total_expenses": business.total_expenses + cost
            })
        
        # Calculate reputation impacts
        reputation_impacts = self._calculate_reputation_impacts(
            action_type, cost, target_audience, hours_invested
        )
        
        # Update business reputation
        reputation = business.reputation or {}
        
        # Apply impacts
        for impact_type, impact_value in reputation_impacts.items():
            if impact_type in reputation:
                reputation[impact_type] = min(10, max(1, reputation[impact_type] + impact_value))
            
        # Add to notable achievements if significant
        if any(value >= 1.0 for value in reputation_impacts.values()):
            notable_achievements = reputation.get("notable_achievements", [])
            notable_achievements.append({
                "date": datetime.utcnow().isoformat(),
                "description": description,
                "action_type": action_type
            })
            reputation["notable_achievements"] = notable_achievements
        
        # Add to activity log
        reputation_activities = reputation.get("reputation_activities", [])
        activity = {
            "date": datetime.utcnow().isoformat(),
            "action_type": action_type,
            "description": description,
            "cost": cost,
            "target_audience": target_audience,
            "hours_invested": hours_invested,
            "impacts": reputation_impacts
        }
        reputation_activities.append(activity)
        reputation["reputation_activities"] = reputation_activities
        
        # Update business reputation
        update_business(db, business_id, {"reputation": reputation})
        
        # Create result
        result = {
            "business_id": business_id,
            "action_type": action_type,
            "description": description,
            "cost": cost,
            "target_audience": target_audience,
            "hours_invested": hours_invested,
            "reputation_impacts": reputation_impacts,
            "new_reputation_values": {
                key: value for key, value in reputation.items() 
                if key in ["overall_reputation", "quality_reputation", "service_reputation", 
                          "price_reputation", "reliability_reputation", "community_standing", 
                          "guild_standing"]
            }
        }
        
        self.logger.info(f"Built reputation for business {business_id} with action: {action_type}")
        
        return result
    
    def _calculate_reputation_impacts(
        self,
        action_type: str,
        cost: Optional[float],
        target_audience: Optional[str],
        hours_invested: Optional[float]
    ) -> Dict[str, float]:
        """
        Calculate reputation impacts from a reputation-building action.
        
        Args:
            action_type: Type of action
            cost: Optional cost
            target_audience: Optional target audience
            hours_invested: Optional hours invested
            
        Returns:
            Dictionary mapping reputation types to impact values
        """
        impacts = {
            "overall_reputation": 0.0,
            "community_standing": 0.0
        }
        
        # Base impact from hours invested
        if hours_invested:
            base_impact = min(1.0, hours_invested / 10)  # Cap at 1.0 for 10+ hours
        else:
            base_impact = 0.1  # Minimal impact if no time invested
        
        # Modify based on cost
        if cost:
            cost_factor = min(2.0, cost / 100)  # Cap at 2.0 for 200+ gold
            base_impact *= (1.0 + cost_factor)
        
        # Apply based on action type
        if action_type == "charity":
            impacts["community_standing"] = base_impact * 1.5
            impacts["overall_reputation"] = base_impact
            
            if target_audience == "nobles":
                impacts["community_standing"] = base_impact * 2.0
                
        elif action_type == "sponsorship":
            impacts["community_standing"] = base_impact * 1.2
            impacts["overall_reputation"] = base_impact
            
            if target_audience == "guild":
                impacts["guild_standing"] = base_impact * 1.5
                
        elif action_type == "quality_showcase":
            impacts["quality_reputation"] = base_impact * 1.5
            impacts["overall_reputation"] = base_impact
            
        elif action_type == "customer_service":
            impacts["service_reputation"] = base_impact * 1.5
            impacts["overall_reputation"] = base_impact
            
        elif action_type == "fair_pricing":
            impacts["price_reputation"] = base_impact * 1.5
            impacts["overall_reputation"] = base_impact
            
        elif action_type == "reliability_demonstration":
            impacts["reliability_reputation"] = base_impact * 1.5
            impacts["overall_reputation"] = base_impact
            
        elif action_type == "community_event":
            impacts["community_standing"] = base_impact * 1.3
            impacts["service_reputation"] = base_impact * 0.5
            impacts["overall_reputation"] = base_impact
            
        else:
            # Generic impact for unknown action types
            impacts["overall_reputation"] = base_impact
        
        # Round to 2 decimal places
        for key in impacts:
            impacts[key] = round(impacts[key], 2)
        
        return impacts
    
    def improve_shop_ambiance(
        self,
        db: Session,
        business_id: str,
        improvement_type: str,
        description: str,
        cost: float,
        hours_invested: float,
        materials_used: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Improve the ambiance of the shop.
        
        Args:
            db: Database session
            business_id: Business profile ID
            improvement_type: Type of ambiance improvement
            description: Description of the improvement
            cost: Currency cost
            hours_invested: Hours invested
            materials_used: Optional materials used
            
        Returns:
            Dictionary with ambiance improvement results
        """
        # Get the business
        business = get_business(db, business_id)
        if not business:
            raise ValueError(f"Business {business_id} not found")
            
        # Check if business has enough funds
        if business.current_balance < cost:
            raise ValueError(f"Not enough funds. Needed: {cost}, Available: {business.current_balance}")
            
        # Check for materials if required
        if materials_used:
            inventory = business.inventory or {}
            for item_id, quantity in materials_used.items():
                if item_id not in inventory or inventory[item_id]["quantity"] < quantity:
                    raise ValueError(f"Not enough of material {item_id} in inventory")
        
        # Record the transaction
        record_financial_transaction(
            db=db,
            business_id=business_id,
            transaction_type=TransactionType.UPGRADE,
            amount=cost,
            description=f"Shop ambiance improvement: {improvement_type}",
            is_income=False,
            category="ambiance_improvements"
        )
        
        # Update business balance
        update_business(db, business_id, {
            "current_balance": business.current_balance - cost,
            "total_expenses": business.total_expenses + cost
        })
        
        # Consume materials if used
        if materials_used:
            inventory = business.inventory.copy()
            for item_id, quantity in materials_used.items():
                inventory[item_id]["quantity"] -= quantity
            
            # Update business inventory
            update_business(db, business_id, {"inventory": inventory})
        
        # Calculate ambiance improvements
        ambiance = business.ambiance or {}
        old_values = {}
        new_values = {}
        
        # Apply improvements based on type
        if improvement_type == "cleaning":
            old_values["cleanliness"] = ambiance.get("cleanliness", 5)
            ambiance["cleanliness"] = min(10, old_values["cleanliness"] + min(3, hours_invested / 2))
            new_values["cleanliness"] = ambiance["cleanliness"]
            ambiance["last_cleaned_date"] = datetime.utcnow().isoformat()
            
        elif improvement_type == "decor":
            old_values["decor_quality"] = ambiance.get("decor_quality", 5)
            # More expensive decor = bigger improvement
            decor_improvement = min(3, cost / 100)
            ambiance["decor_quality"] = min(10, old_values["decor_quality"] + decor_improvement)
            new_values["decor_quality"] = ambiance["decor_quality"]
            
            # Potentially add unique feature
            if cost >= 200:  # Expensive decor becomes a unique feature
                unique_features = ambiance.get("unique_features", [])
                unique_features.append(description)
                ambiance["unique_features"] = unique_features
                
        elif improvement_type == "lighting":
            old_values["lighting"] = ambiance.get("lighting", 5)
            ambiance["lighting"] = min(10, old_values["lighting"] + min(2, cost / 50))
            new_values["lighting"] = ambiance["lighting"]
            
        elif improvement_type == "organization":
            old_values["organization"] = ambiance.get("organization", 5)
            ambiance["organization"] = min(10, old_values["organization"] + min(3, hours_invested / 3))
            new_values["organization"] = ambiance["organization"]
            
        elif improvement_type == "customer_comfort":
            old_values["customer_comfort"] = ambiance.get("customer_comfort", 5)
            ambiance["customer_comfort"] = min(10, old_values["customer_comfort"] + min(2, cost / 75))
            new_values["customer_comfort"] = ambiance["customer_comfort"]
            
        else:
            # Generic improvement
            # Improve the lowest factor
            factors = ["cleanliness", "decor_quality", "lighting", "organization", "customer_comfort"]
            values = [ambiance.get(factor, 5) for factor in factors]
            lowest_factor = factors[values.index(min(values))]
            
            old_values[lowest_factor] = ambiance.get(lowest_factor, 5)
            ambiance[lowest_factor] = min(10, old_values[lowest_factor] + 1)
            new_values[lowest_factor] = ambiance[lowest_factor]
        
        # Recalculate overall ambiance rating
        factors = ["cleanliness", "decor_quality", "lighting", "organization", "customer_comfort"]
        old_values["overall_ambiance_rating"] = ambiance.get("overall_ambiance_rating", 5)
        
        total = sum(ambiance.get(factor, 5) for factor in factors)
        ambiance["overall_ambiance_rating"] = min(10, max(1, total // len(factors)))
        new_values["overall_ambiance_rating"] = ambiance["overall_ambiance_rating"]
        
        # Add ambiance description if significant improvement
        if ambiance["overall_ambiance_rating"] >= 8 and not ambiance.get("ambiance_description"):
            ambiance["ambiance_description"] = self._generate_ambiance_description(business.business_type, ambiance)
        
        # Track improvement history
        improvement_history = ambiance.get("improvement_history", [])
        improvement = {
            "date": datetime.utcnow().isoformat(),
            "improvement_type": improvement_type,
            "description": description,
            "cost": cost,
            "hours_invested": hours_invested,
            "materials_used": materials_used,
            "before": old_values,
            "after": new_values
        }
        improvement_history.append(improvement)
        ambiance["improvement_history"] = improvement_history
        
        # Update business ambiance
        update_business(db, business_id, {"ambiance": ambiance})
        
        # Create result
        result = {
            "business_id": business_id,
            "improvement_type": improvement_type,
            "description": description,
            "cost": cost,
            "hours_invested": hours_invested,
            "before": old_values,
            "after": new_values,
            "overall_rating": ambiance["overall_ambiance_rating"]
        }
        
        self.logger.info(f"Improved shop ambiance for business {business_id}: {improvement_type}")
        
        return result
    
    def _generate_ambiance_description(self, business_type: str, ambiance: Dict[str, Any]) -> str:
        """
        Generate a description of the shop ambiance.
        
        Args:
            business_type: Type of business
            ambiance: Ambiance data
            
        Returns:
            Description of the ambiance
        """
        # This would be more sophisticated in a real implementation
        # For now, generate a simple description based on ratings
        
        cleanliness = ambiance.get("cleanliness", 5)
        decor = ambiance.get("decor_quality", 5)
        lighting = ambiance.get("lighting", 5)
        organization = ambiance.get("organization", 5)
        comfort = ambiance.get("customer_comfort", 5)
        
        # Business-specific descriptions
        if business_type == "blacksmith":
            if cleanliness >= 8:
                clean_desc = "surprisingly clean for a smithy"
            elif cleanliness >= 5:
                clean_desc = "reasonably tidy despite the nature of metalworking"
            else:
                clean_desc = "somewhat sooty and grimy as expected"
                
            if lighting >= 8:
                light_desc = "well-lit by a combination of the forge and strategically placed lanterns"
            elif lighting >= 5:
                light_desc = "adequately lit by the forge's glow"
            else:
                light_desc = "dimly lit except for the red glow of the forge"
                
            return f"The blacksmith shop is {clean_desc} and {light_desc}. " + \
                   f"The workspace is {'highly organized' if organization >= 8 else 'functionally arranged'} " + \
                   f"with {'finely crafted' if decor >= 8 else 'practical'} tools displayed prominently. " + \
                   f"Customers find the waiting area {'remarkably comfortable' if comfort >= 8 else 'adequate for short waits'}."
                   
        elif business_type == "apothecary":
            if cleanliness >= 8:
                clean_desc = "immaculately clean"
            elif cleanliness >= 5:
                clean_desc = "tidy and orderly"
            else:
                clean_desc = "somewhat cluttered but functional"
                
            if lighting >= 8:
                light_desc = "brightly lit to facilitate precise work"
            elif lighting >= 5:
                light_desc = "well-lit by windows and lamps"
            else:
                light_desc = "dimly lit with a somewhat mysterious atmosphere"
                
            return f"The apothecary shop is {clean_desc} and {light_desc}. " + \
                   f"Herbs and ingredients are {'meticulously organized' if organization >= 8 else 'systematically arranged'} " + \
                   f"in {'beautifully crafted' if decor >= 8 else 'functional'} jars and containers. " + \
                   f"The atmosphere is {'inviting and soothing' if comfort >= 8 else 'practical but not uncomfortable'}."
        
        # Generic description for other business types
        cleanliness_desc = "spotless" if cleanliness >= 8 else "clean" if cleanliness >= 5 else "somewhat untidy"
        light_desc = "brilliantly lit" if lighting >= 8 else "well-lit" if lighting >= 5 else "somewhat dim"
        organization_desc = "perfectly organized" if organization >= 8 else "neatly arranged" if organization >= 5 else "functionally arranged"
        decor_desc = "beautifully decorated" if decor >= 8 else "pleasantly adorned" if decor >= 5 else "simply decorated"
        comfort_desc = "extremely comfortable" if comfort >= 8 else "comfortable" if comfort >= 5 else "basic but functional"
        
        return f"The shop is {cleanliness_desc} and {light_desc}, with merchandise {organization_desc}. " + \
               f"The interior is {decor_desc}, creating a {comfort_desc} atmosphere for customers."