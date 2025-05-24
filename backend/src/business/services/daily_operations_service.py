"""
Player Business Daily Operations Service

This module provides services for day-to-day operations of a player-owned business,
including customer order processing, crafting, staff management, inventory management,
shop front operations, and financial oversight.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime, timedelta, date
from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from backend.src.business.models.pydantic_models import (
    PlayerBusinessProfile, CustomOrderRequest, CustomOrderStatus, 
    CustomOrderResponse, StaffMemberContract, StaffRole, StaffJobListing,
    LedgerEntry, DailyOperationSummary, LedgerSummary, BusinessType
)
from backend.src.business.models.db_models import (
    DBPlayerBusinessProfile, DBCustomOrderRequest, DBStaffMemberContract,
    DBLedgerEntry, DBDailyOperationSummary, DBStaffJobListing,
    DBPropertyDeed, DBLeaseAgreement
)

# Assuming there are item, character, and economy services
# from backend.src.item.services.item_service import ItemService
# from backend.src.character.services.character_service import CharacterService
# from backend.src.economy.services.economy_service import EconomyService
# from backend.src.npc.services.npc_service import NpcService
# from backend.src.crafting.services.crafting_service import CraftingService

logger = logging.getLogger(__name__)

class PlayerBusinessDailyOperationsService:
    """
    Service for day-to-day operations of a player-owned business, including customer order
    processing, crafting, staff management, inventory management, shop front operations,
    and financial oversight.
    """
    
    def __init__(self):
        """Initialize the Player Business Daily Operations Service."""
        self.logger = logging.getLogger("PlayerBusinessDailyOperationsService")
        
        # Initialize related services
        # self.item_service = ItemService()
        # self.character_service = CharacterService()
        # self.economy_service = EconomyService()
        # self.npc_service = NpcService()
        # self.crafting_service = CraftingService()
        
        self.logger.info("Player Business Daily Operations Service initialized")
    
    # ===================== Customer Order Workflow =====================
    
    def review_incoming_custom_order_requests(self, 
                                           db: Session, 
                                           business_id: str) -> List[DBCustomOrderRequest]:
        """
        Review incoming custom order requests for a business.
        
        Args:
            db: Database session
            business_id: Business ID
            
        Returns:
            List of custom order requests
        """
        self.logger.info(f"Reviewing incoming custom order requests for business {business_id}")
        
        try:
            # Get all pending custom order requests
            orders = db.query(DBCustomOrderRequest).filter(
                DBCustomOrderRequest.target_player_business_profile_id == business_id,
                DBCustomOrderRequest.status == CustomOrderStatus.AWAITING_PLAYER_REVIEW
            ).all()
            
            self.logger.info(f"Found {len(orders)} pending custom order requests")
            return orders
        except Exception as e:
            self.logger.error(f"Error reviewing custom order requests: {e}")
            return []
    
    def accept_or_decline_custom_order(self, 
                                    db: Session, 
                                    player_id: str, 
                                    order_id: str, 
                                    response: CustomOrderResponse) -> Optional[DBCustomOrderRequest]:
        """
        Accept or decline a custom order request.
        
        Args:
            db: Database session
            player_id: Player character ID
            order_id: Order ID
            response: Response to the order request
            
        Returns:
            Updated custom order request, or None if update failed
        """
        self.logger.info(f"Processing response to custom order {order_id} by player {player_id}")
        
        try:
            # Get the order
            order = db.query(DBCustomOrderRequest).filter(
                DBCustomOrderRequest.id == order_id,
                DBCustomOrderRequest.status == CustomOrderStatus.AWAITING_PLAYER_REVIEW
            ).first()
            
            if not order:
                self.logger.warning(f"Order {order_id} not found or not in AWAITING_PLAYER_REVIEW status")
                return None
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == order.target_player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return None
            
            # Update the order based on the response
            if response.accept:
                # Accept the order
                order.status = CustomOrderStatus.PLAYER_ACCEPTED
                order.negotiated_price_final = response.counter_offer_price or order.offered_price_initial
                order.acceptance_date = datetime.utcnow()
                
                # Calculate deadline
                days_to_complete = response.estimated_completion_days or order.deadline_preference_days
                order.actual_deadline_date = datetime.utcnow() + timedelta(days=days_to_complete)
                
                # Update materials required
                if response.required_materials_from_customer:
                    order.materials_provided_by_npc = response.required_materials_from_customer
                
                # Create a ledger entry for a deposit if applicable
                if order.negotiated_price_final > 0:
                    deposit_amount = order.negotiated_price_final * 0.25  # 25% deposit
                    
                    # Create ledger entry
                    ledger_entry = DBLedgerEntry(
                        id=f"ledger-entry-{uuid4().hex}",
                        business_id=business.id,
                        date=datetime.utcnow(),
                        entry_type="order_deposit",
                        amount=deposit_amount,
                        description=f"Deposit for custom order: {order.item_description_by_npc}",
                        related_entity_id=order.id,
                        related_entity_type="custom_order",
                        tags=["income", "deposit", "custom_order"]
                    )
                    
                    db.add(ledger_entry)
                    
                    # Update business bank balance
                    business.bank_balance += deposit_amount
                
                self.logger.info(f"Custom order {order_id} accepted by player {player_id}")
            else:
                # Decline the order
                order.status = CustomOrderStatus.PLAYER_REJECTED
                order.player_notes_on_order = response.message_to_customer or "Order declined by business owner."
                
                self.logger.info(f"Custom order {order_id} declined by player {player_id}")
            
            db.commit()
            db.refresh(order)
            
            # Notify the NPC about the decision
            # In a real implementation, this would update the NPC's knowledge and potentially affect reputation
            # self.npc_service.notify_custom_order_decision(
            #     db, order.requesting_npc_id, order.id, response.accept, response.message_to_customer
            # )
            
            return order
        except Exception as e:
            self.logger.error(f"Error processing custom order response: {e}")
            db.rollback()
            return None
    
    def plan_material_sourcing_for_order(self, 
                                      db: Session, 
                                      player_id: str, 
                                      order_id: str) -> Dict[str, Any]:
        """
        Plan material sourcing for a custom order.
        
        Args:
            db: Database session
            player_id: Player character ID
            order_id: Order ID
            
        Returns:
            Material sourcing plan
        """
        self.logger.info(f"Planning material sourcing for order {order_id} by player {player_id}")
        
        try:
            # Get the order
            order = db.query(DBCustomOrderRequest).filter(
                DBCustomOrderRequest.id == order_id,
                DBCustomOrderRequest.status == CustomOrderStatus.PLAYER_ACCEPTED
            ).first()
            
            if not order:
                self.logger.warning(f"Order {order_id} not found or not in PLAYER_ACCEPTED status")
                return {"success": False, "reason": "Order not found or not in accepted status"}
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == order.target_player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Determine required materials
            # In a real implementation, this would be based on the item category and description
            # required_materials = self.crafting_service.determine_materials_for_item(
            #     db, order.item_category_hint, order.item_description_by_npc, order.desired_materials_hint
            # )
            
            # For this example, we'll simulate required materials
            required_materials = {
                f"material-{random.randint(1, 100)}": random.randint(1, 5) for _ in range(random.randint(2, 5))
            }
            
            # Check which materials are already in stock
            # In a real implementation, this would check the business inventory
            # current_stock = self.item_service.get_business_inventory(db, business.id)
            
            # For this example, we'll simulate current stock
            current_stock = {
                material_id: random.randint(0, 3) for material_id in required_materials.keys()
            }
            
            # Determine what needs to be purchased
            to_purchase = {}
            for material_id, required_qty in required_materials.items():
                in_stock = current_stock.get(material_id, 0)
                if in_stock < required_qty:
                    to_purchase[material_id] = required_qty - in_stock
            
            # Find potential suppliers
            # In a real implementation, this would query the economy system for suppliers
            # suppliers = self.economy_service.find_suppliers_for_materials(db, list(to_purchase.keys()), business.location_id)
            
            # For this example, we'll simulate suppliers
            suppliers = []
            for material_id in to_purchase.keys():
                suppliers.append({
                    "material_id": material_id,
                    "supplier_id": f"npc-{random.randint(1, 100)}",
                    "supplier_name": f"Supplier {random.randint(1, 100)}",
                    "price_per_unit": random.uniform(1.0, 10.0),
                    "available_quantity": random.randint(5, 20),
                    "quality": random.choice(["low", "medium", "high"]),
                    "distance": random.uniform(0.1, 5.0)  # distance in km or similar unit
                })
            
            # Update order with required materials
            order.materials_required = required_materials
            order.status = CustomOrderStatus.MATERIALS_GATHERING
            
            db.commit()
            
            return {
                "success": True,
                "order_id": order.id,
                "required_materials": required_materials,
                "current_stock": current_stock,
                "to_purchase": to_purchase,
                "potential_suppliers": suppliers
            }
        except Exception as e:
            self.logger.error(f"Error planning material sourcing: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    def update_order_progress(self, 
                           db: Session, 
                           player_id: str, 
                           order_id: str, 
                           new_status: CustomOrderStatus, 
                           progress_notes: Optional[str] = None) -> Optional[DBCustomOrderRequest]:
        """
        Update the progress of a custom order.
        
        Args:
            db: Database session
            player_id: Player character ID
            order_id: Order ID
            new_status: New status for the order
            progress_notes: Optional notes on progress
            
        Returns:
            Updated custom order request, or None if update failed
        """
        self.logger.info(f"Updating order {order_id} to status {new_status} by player {player_id}")
        
        try:
            # Get the order
            order = db.query(DBCustomOrderRequest).filter(
                DBCustomOrderRequest.id == order_id
            ).first()
            
            if not order:
                self.logger.warning(f"Order {order_id} not found")
                return None
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == order.target_player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return None
            
            # Validate status transition
            valid_transitions = {
                CustomOrderStatus.PLAYER_ACCEPTED: [CustomOrderStatus.MATERIALS_GATHERING, CustomOrderStatus.CANCELLED_BY_PLAYER],
                CustomOrderStatus.MATERIALS_GATHERING: [CustomOrderStatus.CRAFTING_IN_PROGRESS, CustomOrderStatus.CANCELLED_BY_PLAYER],
                CustomOrderStatus.CRAFTING_IN_PROGRESS: [CustomOrderStatus.AWAITING_PICKUP, CustomOrderStatus.CANCELLED_BY_PLAYER],
                CustomOrderStatus.AWAITING_PICKUP: [CustomOrderStatus.COMPLETED_DELIVERED, CustomOrderStatus.PAYMENT_PENDING],
                CustomOrderStatus.PAYMENT_PENDING: [CustomOrderStatus.PAYMENT_RECEIVED]
            }
            
            if order.status not in valid_transitions or new_status not in valid_transitions.get(order.status, []):
                self.logger.warning(f"Invalid status transition from {order.status} to {new_status}")
                return None
            
            # Update order status
            order.status = new_status
            
            # Add progress notes if provided
            if progress_notes:
                # In a real implementation, we would append to existing notes
                order.player_notes_on_order = (order.player_notes_on_order or "") + f"\n[{datetime.utcnow().isoformat()}] {progress_notes}"
            
            # Handle specific status transitions
            if new_status == CustomOrderStatus.CRAFTING_IN_PROGRESS:
                # In a real implementation, this would consume materials from inventory
                # self.item_service.consume_materials_for_order(db, business.id, order.id, order.materials_required)
                pass
            elif new_status == CustomOrderStatus.AWAITING_PICKUP:
                # In a real implementation, this would create the crafted item in inventory
                # self.item_service.add_crafted_item_to_inventory(db, business.id, order.id, order.item_description_by_npc)
                pass
            elif new_status == CustomOrderStatus.PAYMENT_PENDING:
                # Calculate remaining payment (full price minus deposit)
                deposit_amount = order.negotiated_price_final * 0.25  # 25% deposit
                remaining_payment = order.negotiated_price_final - deposit_amount
                
                # In a real implementation, this would update the business's pending payments
                order.custom_data = order.custom_data or {}
                order.custom_data["remaining_payment"] = remaining_payment
                
                # Notify the NPC that payment is due
                # self.npc_service.notify_order_ready_for_pickup(db, order.requesting_npc_id, order.id, remaining_payment)
            elif new_status == CustomOrderStatus.PAYMENT_RECEIVED:
                # Process the final payment
                remaining_payment = order.custom_data.get("remaining_payment", 0) if order.custom_data else 0
                
                # Create ledger entry for final payment
                ledger_entry = DBLedgerEntry(
                    id=f"ledger-entry-{uuid4().hex}",
                    business_id=business.id,
                    date=datetime.utcnow(),
                    entry_type="order_final_payment",
                    amount=remaining_payment,
                    description=f"Final payment for custom order: {order.item_description_by_npc}",
                    related_entity_id=order.id,
                    related_entity_type="custom_order",
                    tags=["income", "payment", "custom_order"]
                )
                
                db.add(ledger_entry)
                
                # Update business bank balance
                business.bank_balance += remaining_payment
                
                # Mark order as completed
                order.status = CustomOrderStatus.COMPLETED_DELIVERED
                order.completion_date = datetime.utcnow()
                
                # Generate NPC satisfaction and feedback
                # In a real implementation, this would be based on various factors
                satisfaction_rating = random.randint(3, 5)  # 3-5 stars (assuming generally good service)
                feedback_options = [
                    "Excellent work, exactly what I wanted!",
                    "Very satisfied with the quality, will order again.",
                    "Good craftsmanship, though it took a bit longer than expected.",
                    "The item meets my needs, thank you for your service.",
                    "I'm pleased with the result, though the price was a bit steep."
                ]
                
                order.npc_satisfaction_rating = satisfaction_rating
                order.npc_feedback_text = random.choice(feedback_options)
                
                # Update business reputation based on satisfaction
                reputation_change = (satisfaction_rating - 3) * 2  # -2 to +4 range
                metrics = business.metrics
                metrics["reputation"] = min(100, max(0, metrics["reputation"] + reputation_change))
                metrics["customer_satisfaction"] = min(100, max(0, metrics["customer_satisfaction"] + reputation_change))
                business.metrics = metrics
                
                # Award experience to the business
                business.experience_points += 10 + (satisfaction_rating * 5)  # 25-35 XP per completed order
                
                # Check if mastery level should increase
                self._check_and_update_mastery_level(db, business)
            
            db.commit()
            db.refresh(order)
            
            self.logger.info(f"Order {order_id} updated to status {new_status}")
            return order
        except Exception as e:
            self.logger.error(f"Error updating order progress: {e}")
            db.rollback()
            return None
    
    # ===================== Staff Management & Delegation =====================
    
    def post_job_listing_for_staff(self, 
                                db: Session, 
                                player_id: str, 
                                listing: StaffJobListing) -> Optional[DBStaffJobListing]:
        """
        Post a job listing for staff.
        
        Args:
            db: Database session
            player_id: Player character ID
            listing: Staff job listing details
            
        Returns:
            Created job listing, or None if creation failed
        """
        self.logger.info(f"Posting job listing for business {listing.player_business_profile_id} by player {player_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == listing.player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return None
            
            # Create job listing
            job_listing = DBStaffJobListing(
                id=f"job-listing-{uuid4().hex}",
                player_business_profile_id=business.id,
                role_title=listing.role_title,
                staff_role_category=listing.staff_role_category,
                wage_range_min=listing.wage_range_min,
                wage_range_max=listing.wage_range_max,
                working_hours_description=listing.working_hours_description,
                listing_duration_days=listing.listing_duration_days,
                creation_date=datetime.utcnow(),
                expiry_date=datetime.utcnow() + timedelta(days=listing.listing_duration_days),
                is_active=True,
                responsibilities=listing.responsibilities,
                required_skills=listing.required_skills,
                preferred_skills=listing.preferred_skills,
                benefits=listing.benefits,
                applicant_npc_ids=[]
            )
            
            db.add(job_listing)
            
            # Create ledger entry for job listing cost
            # In a real implementation, there might be a cost to post a job listing
            listing_cost = 10.0  # Example cost
            
            ledger_entry = DBLedgerEntry(
                id=f"ledger-entry-{uuid4().hex}",
                business_id=business.id,
                date=datetime.utcnow(),
                entry_type="job_listing_cost",
                amount=-listing_cost,
                description=f"Cost for posting job listing: {listing.role_title}",
                related_entity_id=job_listing.id,
                related_entity_type="job_listing",
                tags=["expense", "hiring", "administrative"]
            )
            
            db.add(ledger_entry)
            
            # Update business bank balance
            business.bank_balance -= listing_cost
            
            db.commit()
            db.refresh(job_listing)
            
            # In a real implementation, this would notify NPCs about the job listing
            # self.npc_service.broadcast_job_listing(db, job_listing.id)
            
            self.logger.info(f"Job listing {job_listing.id} posted for business {business.id}")
            return job_listing
        except Exception as e:
            self.logger.error(f"Error posting job listing: {e}")
            db.rollback()
            return None
    
    def get_applicants_for_job_listing(self, 
                                    db: Session, 
                                    player_id: str, 
                                    job_listing_id: str) -> List[Dict[str, Any]]:
        """
        Get applicants for a job listing.
        
        Args:
            db: Database session
            player_id: Player character ID
            job_listing_id: Job listing ID
            
        Returns:
            List of applicants with details
        """
        self.logger.info(f"Getting applicants for job listing {job_listing_id}")
        
        try:
            # Get the job listing
            job_listing = db.query(DBStaffJobListing).filter(
                DBStaffJobListing.id == job_listing_id
            ).first()
            
            if not job_listing:
                self.logger.warning(f"Job listing {job_listing_id} not found")
                return []
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == job_listing.player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return []
            
            # In a real implementation, this would query the NPC service for details about applicants
            # applicants = self.npc_service.get_job_applicants(db, job_listing_id)
            
            # For this example, we'll simulate some applicants
            applicants = []
            for i in range(random.randint(1, 5)):
                npc_id = f"npc-{random.randint(1, 100)}"
                
                # Simulate NPC details
                npc_details = {
                    "id": npc_id,
                    "name": f"Applicant {i+1}",
                    "background": random.choice([
                        "Former apprentice looking for new opportunities",
                        "Experienced journeyman seeking a change of pace",
                        "Novice eager to learn the trade",
                        "Skilled craftsperson fallen on hard times",
                        "Ambitious worker with a passion for the craft"
                    ]),
                    "experience_years": random.randint(0, 10),
                    "personality_traits": random.sample([
                        "diligent", "creative", "punctual", "friendly", "detail-oriented",
                        "ambitious", "patient", "adaptable", "reliable", "resourceful"
                    ], k=random.randint(2, 4)),
                    "skills": {
                        skill: random.randint(20, 80) for skill in random.sample([
                            "crafting", "customer_service", "organization", "management",
                            "negotiation", "creativity", "attention_to_detail", "physical_labor"
                        ], k=random.randint(3, 6))
                    },
                    "wage_expectation": random.uniform(
                        job_listing.wage_range_min * 0.9,
                        job_listing.wage_range_max * 1.1
                    ),
                    "references": random.choice([
                        "Former employer speaks highly of work ethic",
                        "Apprenticed under a well-known master",
                        "No formal references but has samples of work",
                        "Comes recommended by a local guild member",
                        "Self-taught but has impressive portfolio"
                    ]),
                    "availability": random.choice([
                        "Can start immediately",
                        "Available starting next week",
                        "Needs to give notice to current employer",
                        "Available for part-time work only",
                        "Flexible schedule"
                    ])
                }
                
                applicants.append(npc_details)
                
                # Add to job listing's applicants if not already there
                if npc_id not in job_listing.applicant_npc_ids:
                    job_listing.applicant_npc_ids.append(npc_id)
            
            db.commit()
            
            self.logger.info(f"Found {len(applicants)} applicants for job listing {job_listing_id}")
            return applicants
        except Exception as e:
            self.logger.error(f"Error getting job applicants: {e}")
            return []
    
    def interview_npc_applicant(self, 
                             db: Session, 
                             player_id: str, 
                             job_listing_id: str, 
                             npc_id: str) -> Dict[str, Any]:
        """
        Interview an NPC applicant for a job.
        
        Args:
            db: Database session
            player_id: Player character ID
            job_listing_id: Job listing ID
            npc_id: NPC ID of the applicant
            
        Returns:
            Interview results and dialogue options
        """
        self.logger.info(f"Interviewing NPC {npc_id} for job listing {job_listing_id} by player {player_id}")
        
        try:
            # Get the job listing
            job_listing = db.query(DBStaffJobListing).filter(
                DBStaffJobListing.id == job_listing_id
            ).first()
            
            if not job_listing:
                self.logger.warning(f"Job listing {job_listing_id} not found")
                return {"success": False, "reason": "Job listing not found"}
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == job_listing.player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Check if NPC is an applicant
            if npc_id not in job_listing.applicant_npc_ids:
                self.logger.warning(f"NPC {npc_id} is not an applicant for job listing {job_listing_id}")
                return {"success": False, "reason": "NPC is not an applicant for this job"}
            
            # In a real implementation, this would query the NPC service for details about the applicant
            # and potentially simulate a dialogue-based interview
            # interview_session = self.npc_service.initiate_job_interview(db, npc_id, job_listing_id, business.id)
            
            # For this example, we'll simulate an interview session
            # This would be much more complex in a real implementation, with actual dialogue and skill checks
            interview_questions = [
                "Tell me about your previous experience in this field.",
                "How would you handle a difficult customer?",
                "What do you believe are your greatest strengths?",
                "How do you prioritize tasks when you have multiple responsibilities?",
                "Why do you want to work for our establishment specifically?"
            ]
            
            # Simulate applicant's answers and performance
            interview_answers = {}
            for question in interview_questions:
                # In a real implementation, these would be based on the NPC's personality and skills
                quality = random.uniform(0.3, 0.9)  # 0.0 to 1.0, with 1.0 being perfect
                
                # Generate a response based on quality
                if quality < 0.5:
                    response_quality = "poor"
                    confidence = "nervous"
                elif quality < 0.7:
                    response_quality = "adequate"
                    confidence = "somewhat confident"
                else:
                    response_quality = "excellent"
                    confidence = "very confident"
                
                answer_templates = {
                    "poor": [
                        "Umm... I'm not really sure. I haven't thought about that much.",
                        "I... well... that's a difficult question. I don't know exactly.",
                        "I don't have much experience with that, to be honest."
                    ],
                    "adequate": [
                        "I've dealt with similar situations before and managed reasonably well.",
                        "I believe I can handle that based on my previous experience.",
                        "I'm fairly competent in that area, though I'm still learning."
                    ],
                    "excellent": [
                        "I have extensive experience in this area and have developed effective strategies.",
                        "That's actually my specialty. I've consistently excelled in that aspect.",
                        "I've studied and practiced this extensively, and I'm confident in my abilities."
                    ]
                }
                
                interview_answers[question] = {
                    "answer": random.choice(answer_templates[response_quality]),
                    "quality": response_quality,
                    "confidence": confidence,
                    "score": int(quality * 10)
                }
            
            # Overall impression
            total_score = sum(answer["score"] for answer in interview_answers.values())
            average_score = total_score / len(interview_questions)
            
            if average_score < 5:
                overall_impression = "poor"
                hiring_recommendation = "not recommended"
            elif average_score < 7:
                overall_impression = "decent"
                hiring_recommendation = "acceptable"
            else:
                overall_impression = "excellent"
                hiring_recommendation = "highly recommended"
            
            # Wage negotiation
            expected_wage = random.uniform(job_listing.wage_range_min, job_listing.wage_range_max)
            negotiation_flexibility = random.uniform(0.1, 0.3)  # 10-30% flexibility
            min_acceptable_wage = expected_wage * (1 - negotiation_flexibility)
            
            # Record that the interview took place
            if "interviewed_applicants" not in job_listing.custom_data:
                job_listing.custom_data = job_listing.custom_data or {}
                job_listing.custom_data["interviewed_applicants"] = {}
            
            job_listing.custom_data["interviewed_applicants"][npc_id] = {
                "date": datetime.utcnow().isoformat(),
                "overall_impression": overall_impression,
                "average_score": average_score,
                "hiring_recommendation": hiring_recommendation,
                "expected_wage": expected_wage,
                "min_acceptable_wage": min_acceptable_wage
            }
            
            db.commit()
            
            self.logger.info(f"Interview with NPC {npc_id} completed with impression: {overall_impression}")
            
            # Return interview results
            return {
                "success": True,
                "npc_id": npc_id,
                "job_listing_id": job_listing_id,
                "questions_and_answers": interview_answers,
                "overall_impression": overall_impression,
                "hiring_recommendation": hiring_recommendation,
                "expected_wage": expected_wage,
                "min_acceptable_wage": min_acceptable_wage,
                "negotiation_options": [
                    {"action": "offer_expected_wage", "amount": expected_wage, "likelihood_of_acceptance": "very high"},
                    {"action": "offer_slightly_below", "amount": expected_wage * 0.9, "likelihood_of_acceptance": "moderate"},
                    {"action": "offer_minimum", "amount": min_acceptable_wage, "likelihood_of_acceptance": "low"},
                    {"action": "offer_above_expected", "amount": expected_wage * 1.1, "likelihood_of_acceptance": "guaranteed"}
                ]
            }
        except Exception as e:
            self.logger.error(f"Error interviewing NPC applicant: {e}")
            return {"success": False, "reason": str(e)}
    
    def hire_staff_member(self, 
                       db: Session, 
                       player_id: str, 
                       job_listing_id: str, 
                       npc_id: str, 
                       offered_wage: float, 
                       contract_details: Dict[str, Any]) -> Optional[DBStaffMemberContract]:
        """
        Hire a staff member based on a job listing.
        
        Args:
            db: Database session
            player_id: Player character ID
            job_listing_id: Job listing ID
            npc_id: NPC ID of the applicant
            offered_wage: Wage offered to the applicant
            contract_details: Additional contract details
            
        Returns:
            Created staff contract, or None if hiring failed
        """
        self.logger.info(f"Hiring NPC {npc_id} for job listing {job_listing_id} by player {player_id}")
        
        try:
            # Get the job listing
            job_listing = db.query(DBStaffJobListing).filter(
                DBStaffJobListing.id == job_listing_id
            ).first()
            
            if not job_listing:
                self.logger.warning(f"Job listing {job_listing_id} not found")
                return None
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == job_listing.player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return None
            
            # Check if NPC is an applicant
            if npc_id not in job_listing.applicant_npc_ids:
                self.logger.warning(f"NPC {npc_id} is not an applicant for job listing {job_listing_id}")
                return None
            
            # In a real implementation, check if the NPC accepts the offer
            # acceptance = self.npc_service.offer_job(db, npc_id, job_listing_id, offered_wage, contract_details)
            
            # For this example, we'll simulate acceptance based on wage
            interview_data = job_listing.custom_data.get("interviewed_applicants", {}).get(npc_id, {})
            min_acceptable_wage = interview_data.get("min_acceptable_wage", job_listing.wage_range_min * 0.8)
            expected_wage = interview_data.get("expected_wage", job_listing.wage_range_min)
            
            if offered_wage < min_acceptable_wage:
                self.logger.info(f"NPC {npc_id} rejected job offer - wage too low")
                return None
            
            # Calculate initial morale based on offered wage vs. expected wage
            initial_morale = 70.0  # Base morale
            if offered_wage >= expected_wage * 1.1:
                initial_morale = 90.0  # Very happy with offer
            elif offered_wage >= expected_wage:
                initial_morale = 80.0  # Satisfied with offer
            elif offered_wage >= min_acceptable_wage:
                initial_morale = 60.0  # Accepted but not thrilled
            
            # Create staff contract
            staff_contract = DBStaffMemberContract(
                id=f"staff-contract-{uuid4().hex}",
                player_business_profile_id=business.id,
                npc_id=npc_id,
                role_title=job_listing.role_title,
                staff_role_category=job_listing.staff_role_category,
                agreed_wage_per_period=offered_wage,
                wage_payment_schedule=contract_details.get("wage_payment_schedule", "weekly"),
                assigned_tasks_description=contract_details.get("assigned_tasks", "General duties as assigned"),
                working_hours_description=job_listing.working_hours_description,
                current_morale_level=initial_morale,
                contract_start_date=datetime.utcnow(),
                contract_end_date=contract_details.get("contract_end_date"),
                days_worked=0,
                skills=contract_details.get("initial_skills", {
                    "primary_skill": random.randint(40, 70),
                    "secondary_skill": random.randint(30, 60)
                }),
                training_progress={}
            )
            
            db.add(staff_contract)
            
            # Update job listing to inactive if specified
            if contract_details.get("close_listing_after_hire", True):
                job_listing.is_active = False
            
            # Add staff member to business
            if business.current_staff_ids is None:
                business.current_staff_ids = []
            business.current_staff_ids.append(staff_contract.id)
            
            db.commit()
            db.refresh(staff_contract)
            
            self.logger.info(f"Staff member {npc_id} hired with contract {staff_contract.id}")
            return staff_contract
        except Exception as e:
            self.logger.error(f"Error hiring staff member: {e}")
            db.rollback()
            return None
    
    def assign_daily_tasks_to_staff(self, 
                                 db: Session, 
                                 player_id: str, 
                                 staff_contract_id: str, 
                                 task_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Assign daily or weekly tasks to staff.
        
        Args:
            db: Database session
            player_id: Player character ID
            staff_contract_id: Staff contract ID
            task_list: List of tasks to assign
            
        Returns:
            Task assignment results
        """
        self.logger.info(f"Assigning tasks to staff {staff_contract_id} by player {player_id}")
        
        try:
            # Get the staff contract
            staff_contract = db.query(DBStaffMemberContract).filter(
                DBStaffMemberContract.id == staff_contract_id
            ).first()
            
            if not staff_contract:
                self.logger.warning(f"Staff contract {staff_contract_id} not found")
                return {"success": False, "reason": "Staff contract not found"}
            
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == staff_contract.player_business_profile_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Validate tasks
            if not task_list:
                self.logger.warning(f"No tasks provided for staff {staff_contract_id}")
                return {"success": False, "reason": "No tasks provided"}
            
            # Ensure the custom_data field is initialized
            staff_contract.custom_data = staff_contract.custom_data or {}
            
            # Record the task assignment
            staff_contract.custom_data["current_tasks"] = task_list
            staff_contract.custom_data["task_assignment_date"] = datetime.utcnow().isoformat()
            staff_contract.assigned_tasks_description = "\n".join([task["description"] for task in task_list])
            
            # In a real implementation, this would update the NPC's behavior and activities
            # self.npc_service.update_staff_tasks(db, staff_contract.npc_id, task_list)
            
            # Simulate morale impact based on task suitability
            morale_impact = 0.0
            task_suitability = []
            
            for task in task_list:
                # In a real implementation, this would be based on the NPC's skills and preferences
                skill_match = random.random()  # 0.0 to 1.0, with 1.0 being perfect match
                
                if skill_match > 0.7:
                    suitability = "excellent"
                    task_morale_impact = random.uniform(0.5, 2.0)
                elif skill_match > 0.4:
                    suitability = "good"
                    task_morale_impact = random.uniform(-0.5, 1.0)
                else:
                    suitability = "poor"
                    task_morale_impact = random.uniform(-2.0, -0.5)
                
                morale_impact += task_morale_impact
                task_suitability.append({
                    "task": task["description"],
                    "suitability": suitability,
                    "morale_impact": task_morale_impact
                })
            
            # Update staff morale
            staff_contract.current_morale_level = max(0, min(100, staff_contract.current_morale_level + morale_impact))
            
            db.commit()
            db.refresh(staff_contract)
            
            self.logger.info(f"Tasks assigned to staff {staff_contract_id} with morale impact: {morale_impact}")
            
            return {
                "success": True,
                "staff_contract_id": staff_contract_id,
                "tasks_assigned": len(task_list),
                "morale_impact": morale_impact,
                "current_morale": staff_contract.current_morale_level,
                "task_suitability": task_suitability
            }
        except Exception as e:
            self.logger.error(f"Error assigning tasks to staff: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    def pay_staff_wages(self, 
                     db: Session, 
                     player_id: str, 
                     business_id: str) -> Dict[str, Any]:
        """
        Pay wages to all staff members.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            
        Returns:
            Wage payment results
        """
        self.logger.info(f"Paying staff wages for business {business_id} by player {player_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Get all staff contracts for the business
            staff_contracts = db.query(DBStaffMemberContract).filter(
                DBStaffMemberContract.player_business_profile_id == business_id
            ).all()
            
            if not staff_contracts:
                self.logger.info(f"No staff contracts found for business {business_id}")
                return {"success": True, "total_paid": 0.0, "staff_paid": 0}
            
            # Pay each staff member
            total_wages = 0.0
            staff_paid = []
            staff_not_paid = []
            
            for contract in staff_contracts:
                # Check if wage payment is due
                # In a real implementation, this would be based on the payment schedule
                # and the last payment date
                
                # For this example, we'll assume all wages are due
                wage = contract.agreed_wage_per_period
                total_wages += wage
                
                # Record the payment
                contract.last_wage_payment_date = datetime.utcnow()
                contract.days_worked += 7  # Assuming weekly payment
                
                # Create ledger entry
                ledger_entry = DBLedgerEntry(
                    id=f"ledger-entry-{uuid4().hex}",
                    business_id=business.id,
                    date=datetime.utcnow(),
                    entry_type="staff_wages",
                    amount=-wage,
                    description=f"Wages for {contract.role_title} ({contract.npc_id})",
                    related_entity_id=contract.id,
                    related_entity_type="staff_contract",
                    tags=["expense", "wages", "staff"]
                )
                
                db.add(ledger_entry)
                
                # Update morale based on timely payment
                contract.current_morale_level = min(100, contract.current_morale_level + 5)
                
                staff_paid.append({
                    "staff_id": contract.id,
                    "npc_id": contract.npc_id,
                    "role": contract.role_title,
                    "wage_paid": wage,
                    "new_morale": contract.current_morale_level
                })
            
            # Deduct total wages from business bank balance
            if business.bank_balance >= total_wages:
                business.bank_balance -= total_wages
                payment_status = "full_payment"
            else:
                # Not enough funds to pay all wages
                self.logger.warning(f"Insufficient funds to pay all wages for business {business_id}")
                payment_status = "insufficient_funds"
                
                # In a real implementation, this would have significant consequences
                # for staff morale and potentially lead to staff quitting
                for contract in staff_contracts:
                    contract.current_morale_level = max(0, contract.current_morale_level - 20)
                    
                # Record the attempted payment
                ledger_entry = DBLedgerEntry(
                    id=f"ledger-entry-{uuid4().hex}",
                    business_id=business.id,
                    date=datetime.utcnow(),
                    entry_type="failed_wage_payment",
                    amount=0,
                    description=f"Failed to pay staff wages due to insufficient funds",
                    tags=["expense", "wages", "staff", "failed"]
                )
                
                db.add(ledger_entry)
                
                return {"success": False, "reason": "Insufficient funds", "total_owed": total_wages, "bank_balance": business.bank_balance}
            
            db.commit()
            
            self.logger.info(f"Paid {total_wages} in wages to {len(staff_paid)} staff members")
            
            return {
                "success": True,
                "total_paid": total_wages,
                "staff_paid": len(staff_paid),
                "payment_details": staff_paid,
                "new_bank_balance": business.bank_balance
            }
        except Exception as e:
            self.logger.error(f"Error paying staff wages: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    # ===================== Inventory & Resource Management =====================
    
    def check_material_stock_levels(self, 
                                 db: Session, 
                                 player_id: str, 
                                 business_id: str) -> Dict[str, Any]:
        """
        Check material stock levels for a business.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            
        Returns:
            Current stock levels and recommendations
        """
        self.logger.info(f"Checking material stock levels for business {business_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # In a real implementation, this would query the inventory system
            # current_stock = self.item_service.get_business_inventory(db, business.id)
            
            # For this example, we'll simulate inventory
            # Get common materials based on business type
            common_materials = self._get_common_materials_for_business_type(business.business_type)
            
            # Simulate current stock levels
            current_stock = {}
            for material_id, material_name in common_materials.items():
                current_stock[material_id] = {
                    "id": material_id,
                    "name": material_name,
                    "quantity": random.randint(0, 20),
                    "unit_value": random.uniform(0.5, 10.0),
                    "quality": random.choice(["low", "medium", "high"]),
                    "perishable": random.random() < 0.2,  # 20% chance of being perishable
                    "expiry_date": (datetime.utcnow() + timedelta(days=random.randint(10, 60))).isoformat() if random.random() < 0.2 else None
                }
            
            # Determine recommended stock levels
            recommended_stock = {}
            low_stock_items = {}
            expiring_soon_items = {}
            
            for material_id, material_info in current_stock.items():
                # Recommended level depends on business type and material importance
                recommended_level = random.randint(5, 15)  # This would be based on actual business needs
                recommended_stock[material_id] = recommended_level
                
                # Check if stock is low
                if material_info["quantity"] < recommended_level * 0.5:
                    low_stock_items[material_id] = {
                        "name": material_info["name"],
                        "current_quantity": material_info["quantity"],
                        "recommended_quantity": recommended_level,
                        "deficit": recommended_level - material_info["quantity"],
                        "priority": "high" if material_info["quantity"] == 0 else "medium"
                    }
                
                # Check if perishable items are expiring soon
                if material_info.get("perishable") and material_info.get("expiry_date"):
                    expiry_date = datetime.fromisoformat(material_info["expiry_date"])
                    days_until_expiry = (expiry_date - datetime.utcnow()).days
                    
                    if days_until_expiry <= 7:
                        expiring_soon_items[material_id] = {
                            "name": material_info["name"],
                            "quantity": material_info["quantity"],
                            "expiry_date": material_info["expiry_date"],
                            "days_until_expiry": days_until_expiry,
                            "priority": "high" if days_until_expiry <= 3 else "medium"
                        }
            
            # Calculate total inventory value
            total_inventory_value = sum(item["quantity"] * item["unit_value"] for item in current_stock.values())
            
            # Get potential suppliers for low stock items
            # In a real implementation, this would query the economy system
            # suppliers = self.economy_service.find_suppliers_for_materials(
            #     db, list(low_stock_items.keys()), business.location_id
            # )
            
            # For this example, we'll simulate suppliers
            suppliers = []
            for material_id in low_stock_items.keys():
                material_name = current_stock[material_id]["name"]
                
                for i in range(random.randint(1, 3)):
                    suppliers.append({
                        "supplier_id": f"npc-supplier-{random.randint(1, 100)}",
                        "supplier_name": f"Supplier {random.randint(1, 100)}",
                        "material_id": material_id,
                        "material_name": material_name,
                        "price_per_unit": current_stock[material_id]["unit_value"] * random.uniform(0.8, 1.2),
                        "available_quantity": random.randint(5, 30),
                        "quality": random.choice(["low", "medium", "high"]),
                        "delivery_time_days": random.randint(1, 5),
                        "reputation": random.randint(1, 5)  # 1-5 stars
                    })
            
            self.logger.info(f"Inventory check complete. Total value: {total_inventory_value:.2f}")
            
            return {
                "success": True,
                "current_stock": current_stock,
                "recommended_stock": recommended_stock,
                "low_stock_items": low_stock_items,
                "expiring_soon_items": expiring_soon_items,
                "total_inventory_value": total_inventory_value,
                "potential_suppliers": suppliers
            }
        except Exception as e:
            self.logger.error(f"Error checking material stock levels: {e}")
            return {"success": False, "reason": str(e)}
    
    def order_materials_from_supplier(self, 
                                   db: Session, 
                                   player_id: str, 
                                   business_id: str, 
                                   order_details: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Order materials from a supplier.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            order_details: Details of the order
            
        Returns:
            Order results
        """
        self.logger.info(f"Ordering materials for business {business_id} by player {player_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Validate order details
            if not order_details:
                self.logger.warning(f"No order details provided")
                return {"success": False, "reason": "No order details provided"}
            
            # Calculate total cost
            total_cost = sum(item["quantity"] * item["price_per_unit"] for item in order_details)
            
            # Check if business can afford the order
            if business.bank_balance < total_cost:
                self.logger.warning(f"Insufficient funds to place order. Required: {total_cost}, Available: {business.bank_balance}")
                return {"success": False, "reason": "Insufficient funds", "required": total_cost, "available": business.bank_balance}
            
            # Process the order
            order_items = []
            for item in order_details:
                # In a real implementation, this would create purchase orders and track their status
                order_items.append({
                    "item_id": item["material_id"],
                    "item_name": item.get("material_name", f"Material {item['material_id']}"),
                    "quantity": item["quantity"],
                    "price_per_unit": item["price_per_unit"],
                    "total_price": item["quantity"] * item["price_per_unit"],
                    "supplier_id": item["supplier_id"],
                    "supplier_name": item.get("supplier_name", f"Supplier {item['supplier_id']}"),
                    "expected_delivery_days": item.get("delivery_time_days", random.randint(1, 5)),
                    "quality": item.get("quality", "medium")
                })
            
            # Create ledger entry for the purchase
            ledger_entry = DBLedgerEntry(
                id=f"ledger-entry-{uuid4().hex}",
                business_id=business.id,
                date=datetime.utcnow(),
                entry_type="material_purchase",
                amount=-total_cost,
                description=f"Purchase of materials from suppliers",
                tags=["expense", "inventory", "materials"]
            )
            
            db.add(ledger_entry)
            
            # Deduct cost from business bank balance
            business.bank_balance -= total_cost
            
            # Store the order in custom data for tracking
            business.custom_data = business.custom_data or {}
            if "pending_material_orders" not in business.custom_data:
                business.custom_data["pending_material_orders"] = []
            
            order_id = f"order-{uuid4().hex}"
            
            business.custom_data["pending_material_orders"].append({
                "order_id": order_id,
                "order_date": datetime.utcnow().isoformat(),
                "items": order_items,
                "total_cost": total_cost,
                "status": "processing"
            })
            
            db.commit()
            
            # In a real implementation, this would schedule the delivery of materials
            # self.economy_service.schedule_material_delivery(db, business_id, order_id, order_items)
            
            self.logger.info(f"Order placed for materials. Total cost: {total_cost:.2f}")
            
            return {
                "success": True,
                "order_id": order_id,
                "items_ordered": len(order_items),
                "total_cost": total_cost,
                "new_bank_balance": business.bank_balance,
                "estimated_delivery": max(item["expected_delivery_days"] for item in order_items)
            }
        except Exception as e:
            self.logger.error(f"Error ordering materials: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    def manage_spoilage_or_degradation(self, 
                                    db: Session, 
                                    player_id: str, 
                                    business_id: str) -> Dict[str, Any]:
        """
        Manage spoilage or degradation of materials.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            
        Returns:
            Spoilage management results
        """
        self.logger.info(f"Managing spoilage/degradation for business {business_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # In a real implementation, this would query the inventory system for perishable items
            # inventory = self.item_service.get_business_inventory(db, business.id)
            
            # For this example, we'll simulate inventory
            # Get common materials based on business type with some perishable items
            common_materials = self._get_common_materials_for_business_type(business.business_type)
            
            # Simulate current inventory with some perishable items
            inventory = {}
            for material_id, material_name in common_materials.items():
                is_perishable = random.random() < 0.3  # 30% chance of being perishable
                
                inventory[material_id] = {
                    "id": material_id,
                    "name": material_name,
                    "quantity": random.randint(1, 20),
                    "unit_value": random.uniform(0.5, 10.0),
                    "quality": random.choice(["low", "medium", "high"]),
                    "perishable": is_perishable,
                    "expiry_date": (datetime.utcnow() + timedelta(days=random.randint(-5, 30))).isoformat() if is_perishable else None,
                    "condition_percentage": random.randint(50, 100) if is_perishable else 100
                }
            
            # Check for expired or spoiled items
            expired_items = {}
            degraded_items = {}
            total_loss_value = 0.0
            
            for material_id, item in inventory.items():
                if item.get("perishable") and item.get("expiry_date"):
                    expiry_date = datetime.fromisoformat(item["expiry_date"])
                    
                    if expiry_date < datetime.utcnow():
                        # Item has expired
                        expired_quantity = item["quantity"]
                        loss_value = expired_quantity * item["unit_value"]
                        total_loss_value += loss_value
                        
                        expired_items[material_id] = {
                            "name": item["name"],
                            "quantity": expired_quantity,
                            "unit_value": item["unit_value"],
                            "total_value": loss_value,
                            "expiry_date": item["expiry_date"]
                        }
                    elif item.get("condition_percentage", 100) < 70:
                        # Item is degrading but not expired
                        degraded_quantity = item["quantity"]
                        condition_loss = (100 - item["condition_percentage"]) / 100.0
                        loss_value = degraded_quantity * item["unit_value"] * condition_loss
                        total_loss_value += loss_value
                        
                        degraded_items[material_id] = {
                            "name": item["name"],
                            "quantity": degraded_quantity,
                            "condition": item["condition_percentage"],
                            "unit_value": item["unit_value"],
                            "estimated_loss_value": loss_value,
                            "expiry_date": item["expiry_date"],
                            "days_until_expiry": (expiry_date - datetime.utcnow()).days
                        }
            
            # Options for dealing with expired/degraded items
            expired_options = {
                "discard": "Discard expired items (total loss)",
                "sell_at_discount": "Sell expired items at steep discount (recover some value)",
                "repurpose": "Repurpose for different use (if applicable)"
            }
            
            degraded_options = {
                "use_quickly": "Use degraded items quickly before they expire",
                "sell_at_discount": "Sell degraded items at discount",
                "preservation": "Apply preservation techniques (additional cost)"
            }
            
            # Create ledger entry for spoilage loss if any
            if total_loss_value > 0:
                ledger_entry = DBLedgerEntry(
                    id=f"ledger-entry-{uuid4().hex}",
                    business_id=business.id,
                    date=datetime.utcnow(),
                    entry_type="inventory_spoilage",
                    amount=-total_loss_value,
                    description=f"Loss due to expired or degraded materials",
                    tags=["expense", "inventory", "spoilage"]
                )
                
                db.add(ledger_entry)
                
                # In a real implementation, this would update the inventory
                # self.item_service.remove_expired_items(db, business.id, list(expired_items.keys()))
                
                db.commit()
            
            self.logger.info(f"Spoilage management complete. Total loss value: {total_loss_value:.2f}")
            
            return {
                "success": True,
                "expired_items": expired_items,
                "degraded_items": degraded_items,
                "total_loss_value": total_loss_value,
                "expired_options": expired_options,
                "degraded_options": degraded_options
            }
        except Exception as e:
            self.logger.error(f"Error managing spoilage: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    # ===================== Shop Front Operations =====================
    
    def set_daily_prices_for_stock_items(self, 
                                      db: Session, 
                                      player_id: str, 
                                      business_id: str, 
                                      price_adjustments: Dict[str, float]) -> Dict[str, Any]:
        """
        Set daily prices for stock items.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            price_adjustments: Map of item IDs to new prices
            
        Returns:
            Price adjustment results
        """
        self.logger.info(f"Setting daily prices for business {business_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Validate price adjustments
            if not price_adjustments:
                self.logger.warning(f"No price adjustments provided")
                return {"success": False, "reason": "No price adjustments provided"}
            
            # In a real implementation, this would validate that the items exist in inventory
            # and update their prices
            # updated_items = self.item_service.update_item_prices(db, business.id, price_adjustments)
            
            # For this example, we'll simulate the update
            # Store the price adjustments in custom data
            business.custom_data = business.custom_data or {}
            if "item_prices" not in business.custom_data:
                business.custom_data["item_prices"] = {}
            
            for item_id, price in price_adjustments.items():
                business.custom_data["item_prices"][item_id] = price
            
            # Get market information for comparison
            # In a real implementation, this would query the economy system
            # market_prices = self.economy_service.get_market_prices(db, list(price_adjustments.keys()), business.location_id)
            
            # For this example, we'll simulate market prices
            market_prices = {}
            price_comparisons = {}
            
            for item_id, price in price_adjustments.items():
                # Simulate market average price
                market_avg = price * random.uniform(0.8, 1.2)
                market_prices[item_id] = market_avg
                
                # Compare with market
                if price < market_avg * 0.9:
                    comparison = "significantly_below_market"
                    potential_effect = "high_volume_low_margin"
                elif price < market_avg * 0.95:
                    comparison = "below_market"
                    potential_effect = "higher_volume"
                elif price > market_avg * 1.1:
                    comparison = "significantly_above_market"
                    potential_effect = "low_volume_high_margin"
                elif price > market_avg * 1.05:
                    comparison = "above_market"
                    potential_effect = "lower_volume"
                else:
                    comparison = "at_market"
                    potential_effect = "average_volume_average_margin"
                
                price_comparisons[item_id] = {
                    "your_price": price,
                    "market_average": market_avg,
                    "comparison": comparison,
                    "potential_effect": potential_effect
                }
            
            db.commit()
            
            self.logger.info(f"Updated prices for {len(price_adjustments)} items")
            
            return {
                "success": True,
                "updated_items": len(price_adjustments),
                "price_comparisons": price_comparisons,
                "market_insight": "Your overall pricing strategy is " + (
                    "competitive" if sum(1 for c in price_comparisons.values() if c["comparison"] in ["below_market", "significantly_below_market"]) > len(price_comparisons) / 2
                    else "premium" if sum(1 for c in price_comparisons.values() if c["comparison"] in ["above_market", "significantly_above_market"]) > len(price_comparisons) / 2
                    else "aligned with market averages"
                )
            }
        except Exception as e:
            self.logger.error(f"Error setting daily prices: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    def process_direct_sale_to_npc(self, 
                                db: Session, 
                                player_id: str, 
                                business_id: str, 
                                customer_npc_id: str, 
                                items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a direct sale to an NPC customer.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            customer_npc_id: NPC customer ID
            items: Items being sold
            
        Returns:
            Sale results
        """
        self.logger.info(f"Processing sale to NPC {customer_npc_id} for business {business_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Validate items
            if not items:
                self.logger.warning(f"No items provided for sale")
                return {"success": False, "reason": "No items provided for sale"}
            
            # In a real implementation, this would check if the items are in stock
            # and if the quantities are available
            # inventory_check = self.item_service.check_inventory_availability(db, business.id, items)
            
            # For this example, we'll assume all items are available
            
            # Calculate total sale amount
            total_sale_amount = sum(item["quantity"] * item["price"] for item in items)
            
            # In a real implementation, this would get information about the NPC
            # npc_info = self.npc_service.get_npc_details(db, customer_npc_id)
            
            # For this example, we'll simulate NPC customer
            # Simulate haggling or negotiation if applicable
            negotiation_result = None
            final_sale_amount = total_sale_amount
            
            # 30% chance of negotiation
            if random.random() < 0.3:
                negotiation_skill = random.uniform(0.1, 0.9)  # 0.0 to 1.0, with 1.0 being perfect
                discount_requested = total_sale_amount * (0.05 + (negotiation_skill * 0.15))  # 5-20% discount
                
                negotiation_result = {
                    "original_amount": total_sale_amount,
                    "discount_requested": discount_requested,
                    "discount_percentage": (discount_requested / total_sale_amount) * 100,
                    "haggling_dialogue": random.choice([
                        "This seems a bit steep. Could you offer a better price?",
                        "I was hoping to pay a bit less. Any chance of a discount?",
                        "The quality is good, but the price is high. Can we negotiate?",
                        "I'm a regular customer, surely you can do better on the price?"
                    ])
                }
                
                # Options for player response
                negotiation_result["options"] = [
                    {"action": "accept_full_discount", "final_amount": total_sale_amount - discount_requested, "customer_satisfaction": "very_high"},
                    {"action": "partial_discount", "final_amount": total_sale_amount - (discount_requested / 2), "customer_satisfaction": "high"},
                    {"action": "small_courtesy_discount", "final_amount": total_sale_amount - (discount_requested / 4), "customer_satisfaction": "moderate"},
                    {"action": "hold_firm", "final_amount": total_sale_amount, "customer_satisfaction": "low"}
                ]
                
                # For this example, we'll simulate accepting a partial discount
                final_sale_amount = total_sale_amount - (discount_requested / 2)
                negotiation_result["player_response"] = "partial_discount"
                negotiation_result["final_amount"] = final_sale_amount
            
            # Process the sale
            # In a real implementation, this would update inventory, record the transaction, etc.
            # self.item_service.remove_items_from_inventory(db, business.id, items)
            
            # Create ledger entry for the sale
            ledger_entry = DBLedgerEntry(
                id=f"ledger-entry-{uuid4().hex}",
                business_id=business.id,
                date=datetime.utcnow(),
                entry_type="sale",
                amount=final_sale_amount,
                description=f"Sale to customer {customer_npc_id}",
                related_entity_id=customer_npc_id,
                related_entity_type="npc_customer",
                tags=["income", "sale"]
            )
            
            db.add(ledger_entry)
            
            # Update business bank balance
            business.bank_balance += final_sale_amount
            
            # Update business metrics
            metrics = business.metrics
            
            # Small boost to reputation for each sale
            metrics["reputation"] = min(100, metrics["reputation"] + 0.2)
            
            # Simulate customer satisfaction (affected by negotiation)
            customer_satisfaction = 0.0
            if negotiation_result:
                if negotiation_result["player_response"] == "accept_full_discount":
                    customer_satisfaction = 2.0
                elif negotiation_result["player_response"] == "partial_discount":
                    customer_satisfaction = 1.0
                elif negotiation_result["player_response"] == "small_courtesy_discount":
                    customer_satisfaction = 0.5
                else:  # hold_firm
                    customer_satisfaction = -0.5
            else:
                # No negotiation, standard satisfaction
                customer_satisfaction = 0.8
            
            metrics["customer_satisfaction"] = min(100, max(0, metrics["customer_satisfaction"] + customer_satisfaction))
            
            business.metrics = metrics
            
            # Track customer interaction
            business.custom_data = business.custom_data or {}
            if "customer_interactions" not in business.custom_data:
                business.custom_data["customer_interactions"] = []
            
            business.custom_data["customer_interactions"].append({
                "customer_id": customer_npc_id,
                "date": datetime.utcnow().isoformat(),
                "transaction_amount": final_sale_amount,
                "items_purchased": len(items),
                "negotiated": negotiation_result is not None,
                "satisfaction_change": customer_satisfaction
            })
            
            # Update daily operation summary
            today = datetime.utcnow().date().isoformat()
            if "daily_operations" not in business.custom_data:
                business.custom_data["daily_operations"] = {}
            
            if today not in business.custom_data["daily_operations"]:
                business.custom_data["daily_operations"][today] = {
                    "sales_count": 0,
                    "sales_revenue": 0.0,
                    "customer_count": 0,
                    "items_sold": 0
                }
            
            business.custom_data["daily_operations"][today]["sales_count"] += 1
            business.custom_data["daily_operations"][today]["sales_revenue"] += final_sale_amount
            business.custom_data["daily_operations"][today]["customer_count"] += 1
            business.custom_data["daily_operations"][today]["items_sold"] += sum(item["quantity"] for item in items)
            
            db.commit()
            
            # Award experience to the business
            business.experience_points += 5 + int(final_sale_amount / 10)
            self._check_and_update_mastery_level(db, business)
            
            db.commit()
            
            self.logger.info(f"Processed sale to NPC {customer_npc_id}. Amount: {final_sale_amount:.2f}")
            
            return {
                "success": True,
                "sale_id": ledger_entry.id,
                "customer_npc_id": customer_npc_id,
                "original_amount": total_sale_amount,
                "final_amount": final_sale_amount,
                "items_sold": len(items),
                "total_quantity": sum(item["quantity"] for item in items),
                "negotiation": negotiation_result,
                "new_bank_balance": business.bank_balance,
                "experience_gained": 5 + int(final_sale_amount / 10)
            }
        except Exception as e:
            self.logger.error(f"Error processing sale: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    # ===================== Financial Oversight =====================
    
    def review_ledger(self, 
                   db: Session, 
                   player_id: str, 
                   business_id: str, 
                   start_date: date, 
                   end_date: date) -> LedgerSummary:
        """
        Review the business ledger for a specific period.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            start_date: Start date for the period
            end_date: End date for the period
            
        Returns:
            Ledger summary for the period
        """
        self.logger.info(f"Reviewing ledger for business {business_id} from {start_date} to {end_date}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return None
            
            # Convert dates to datetime for filtering
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            # Get ledger entries for the period
            ledger_entries = db.query(DBLedgerEntry).filter(
                DBLedgerEntry.business_id == business_id,
                DBLedgerEntry.date >= start_datetime,
                DBLedgerEntry.date <= end_datetime
            ).order_by(DBLedgerEntry.date).all()
            
            if not ledger_entries:
                self.logger.info(f"No ledger entries found for the period")
                
                # Return empty summary
                return LedgerSummary(
                    business_id=business_id,
                    start_date=start_date,
                    end_date=end_date,
                    starting_balance=business.bank_balance,  # Use current balance as approximation
                    ending_balance=business.bank_balance,
                    total_income=0.0,
                    total_expenses=0.0,
                    profit_or_loss=0.0,
                    income_by_category={},
                    expenses_by_category={},
                    top_income_sources=[],
                    top_expenses=[],
                    pending_payments=[],
                    tax_liability=0.0
                )
            
            # Calculate starting and ending balances
            # In a real implementation, this would calculate the actual balances at the start and end dates
            # For this example, we'll calculate based on the entries
            total_income = sum(entry.amount for entry in ledger_entries if entry.amount > 0)
            total_expenses = sum(abs(entry.amount) for entry in ledger_entries if entry.amount < 0)
            net_change = total_income - total_expenses
            
            # Group by categories
            income_by_category = {}
            expenses_by_category = {}
            
            for entry in ledger_entries:
                if entry.amount > 0:
                    # Income
                    category = entry.entry_type
                    income_by_category[category] = income_by_category.get(category, 0.0) + entry.amount
                else:
                    # Expense
                    category = entry.entry_type
                    expenses_by_category[category] = expenses_by_category.get(category, 0.0) + abs(entry.amount)
            
            # Find top income sources
            income_entries = [entry for entry in ledger_entries if entry.amount > 0]
            income_entries.sort(key=lambda x: x.amount, reverse=True)
            top_income_sources = [
                {
                    "date": entry.date.isoformat(),
                    "amount": entry.amount,
                    "description": entry.description,
                    "type": entry.entry_type
                }
                for entry in income_entries[:5]  # Top 5
            ]
            
            # Find top expenses
            expense_entries = [entry for entry in ledger_entries if entry.amount < 0]
            expense_entries.sort(key=lambda x: abs(x.amount), reverse=True)
            top_expenses = [
                {
                    "date": entry.date.isoformat(),
                    "amount": abs(entry.amount),
                    "description": entry.description,
                    "type": entry.entry_type
                }
                for entry in expense_entries[:5]  # Top 5
            ]
            
            # Pending payments (from custom orders, etc.)
            pending_payments = []
            
            # Get pending custom orders
            pending_orders = db.query(DBCustomOrderRequest).filter(
                DBCustomOrderRequest.target_player_business_profile_id == business_id,
                DBCustomOrderRequest.status == CustomOrderStatus.PAYMENT_PENDING
            ).all()
            
            for order in pending_orders:
                remaining_payment = order.custom_data.get("remaining_payment", 0) if order.custom_data else 0
                
                if remaining_payment > 0:
                    pending_payments.append({
                        "id": order.id,
                        "type": "custom_order",
                        "amount": remaining_payment,
                        "due_date": (datetime.utcnow() + timedelta(days=3)).isoformat(),  # Example due date
                        "description": f"Payment for custom order: {order.item_description_by_npc}"
                    })
            
            # Calculate tax liability
            # In a real implementation, this would be based on tax rules, income, etc.
            # For this example, we'll use a simple percentage of income
            tax_liability = total_income * 0.15  # Example: 15% tax rate
            
            # Create ledger summary
            ledger_summary = LedgerSummary(
                business_id=business_id,
                start_date=start_date,
                end_date=end_date,
                starting_balance=business.bank_balance - net_change,  # Approximate
                ending_balance=business.bank_balance,
                total_income=total_income,
                total_expenses=total_expenses,
                profit_or_loss=net_change,
                income_by_category=income_by_category,
                expenses_by_category=expenses_by_category,
                top_income_sources=top_income_sources,
                top_expenses=top_expenses,
                pending_payments=pending_payments,
                tax_liability=tax_liability
            )
            
            self.logger.info(f"Ledger review complete. Income: {total_income:.2f}, Expenses: {total_expenses:.2f}, Profit/Loss: {net_change:.2f}")
            
            return ledger_summary
        except Exception as e:
            self.logger.error(f"Error reviewing ledger: {e}")
            return None
    
    def pay_taxes_or_rent(self, 
                       db: Session, 
                       player_id: str, 
                       business_id: str, 
                       payment_type: str, 
                       amount: float) -> Dict[str, Any]:
        """
        Pay taxes or rent for the business.
        
        Args:
            db: Database session
            player_id: Player character ID
            business_id: Business ID
            payment_type: Type of payment ('tax' or 'rent')
            amount: Amount to pay
            
        Returns:
            Payment results
        """
        self.logger.info(f"Processing {payment_type} payment for business {business_id}")
        
        try:
            # Get the business
            business = db.query(DBPlayerBusinessProfile).filter(
                DBPlayerBusinessProfile.id == business_id,
                DBPlayerBusinessProfile.player_character_id == player_id
            ).first()
            
            if not business:
                self.logger.warning(f"Business not found or not owned by player {player_id}")
                return {"success": False, "reason": "Business not found or not owned by player"}
            
            # Check if business can afford the payment
            if business.bank_balance < amount:
                self.logger.warning(f"Insufficient funds to make {payment_type} payment. Required: {amount}, Available: {business.bank_balance}")
                return {"success": False, "reason": "Insufficient funds", "required": amount, "available": business.bank_balance}
            
            # Process the payment
            if payment_type == "tax":
                # Get property deed if it exists
                property_deed = None
                if business.property_id:
                    property_deed = db.query(DBPropertyDeed).filter(
                        DBPropertyDeed.id == business.property_id
                    ).first()
                
                if property_deed:
                    property_deed.last_tax_payment_date = datetime.utcnow()
                
                entry_type = "property_tax"
                description = f"Property tax payment for business location"
                recipient = "local_government"
            elif payment_type == "rent":
                # Get lease agreement if it exists
                lease_agreement = None
                if business.property_id:
                    lease_agreement = db.query(DBLeaseAgreement).filter(
                        DBLeaseAgreement.id == business.property_id
                    ).first()
                
                if lease_agreement:
                    lease_agreement.last_rent_payment_date = datetime.utcnow()
                
                entry_type = "rent"
                description = f"Rent payment for business location"
                recipient = lease_agreement.lessor_npc_id if lease_agreement else "landlord"
            else:
                self.logger.warning(f"Invalid payment type: {payment_type}")
                return {"success": False, "reason": f"Invalid payment type: {payment_type}"}
            
            # Create ledger entry
            ledger_entry = DBLedgerEntry(
                id=f"ledger-entry-{uuid4().hex}",
                business_id=business.id,
                date=datetime.utcnow(),
                entry_type=entry_type,
                amount=-amount,
                description=description,
                tags=["expense", payment_type, "property"]
            )
            
            db.add(ledger_entry)
            
            # Deduct payment from business bank balance
            business.bank_balance -= amount
            
            db.commit()
            
            self.logger.info(f"Processed {payment_type} payment of {amount:.2f}")
            
            return {
                "success": True,
                "payment_type": payment_type,
                "amount_paid": amount,
                "payment_date": datetime.utcnow().isoformat(),
                "recipient": recipient,
                "new_bank_balance": business.bank_balance
            }
        except Exception as e:
            self.logger.error(f"Error paying {payment_type}: {e}")
            db.rollback()
            return {"success": False, "reason": str(e)}
    
    # ===================== Utility Methods =====================
    
    def _get_common_materials_for_business_type(self, business_type: BusinessType) -> Dict[str, str]:
        """
        Get common materials used by a specific business type.
        
        Args:
            business_type: Business type
            
        Returns:
            Dictionary mapping material IDs to names
        """
        # Define common materials by business type
        if business_type == BusinessType.BLACKSMITH:
            return {
                f"material-{i}": name for i, name in enumerate([
                    "Iron Ingot", "Steel Bar", "Coal", "Copper Ingot", "Tin", "Silver Bar",
                    "Gold Nugget", "Leather Strip", "Wood Handle", "Gemstone", "Whetstone"
                ])
            }
        elif business_type == BusinessType.APOTHECARY:
            return {
                f"material-{i}": name for i, name in enumerate([
                    "Healing Herb", "Mushroom", "Spider Silk", "Snake Venom", "Flower Petal",
                    "Tree Bark", "River Clay", "Crystal Shard", "Butterfly Wing", "Bat Wing",
                    "Glass Vial", "Mortar and Pestle", "Distilled Water"
                ])
            }
        elif business_type == BusinessType.BAKERY:
            return {
                f"material-{i}": name for i, name in enumerate([
                    "Flour", "Sugar", "Salt", "Butter", "Eggs", "Milk", "Honey",
                    "Yeast", "Nuts", "Dried Fruit", "Spices", "Chocolate"
                ])
            }
        elif business_type == BusinessType.TAVERN:
            return {
                f"material-{i}": name for i, name in enumerate([
                    "Ale Keg", "Wine Bottle", "Spirit Cask", "Bread", "Cheese", "Meat",
                    "Vegetables", "Spices", "Fruit", "Honey", "Salt", "Glassware", "Plates"
                ])
            }
        else:
            # Generic materials for other business types
            return {
                f"material-{i}": f"Generic Material {i+1}" for i in range(10)
            }
    
    def _check_and_update_mastery_level(self, db: Session, business: DBPlayerBusinessProfile) -> bool:
        """
        Check if the business's mastery level should increase and update if necessary.
        
        Args:
            db: Database session
            business: Business profile
            
        Returns:
            True if mastery level was increased, False otherwise
        """
        # Define experience thresholds for each level
        level_thresholds = {
            1: 0,     # Starting level
            2: 100,   # XP needed for level 2
            3: 300,
            4: 600,
            5: 1000,
            6: 1500,
            7: 2500,
            8: 4000,
            9: 6000,
            10: 10000  # Max level
        }
        
        # Check if current XP exceeds threshold for next level
        current_level = business.mastery_level
        next_level = current_level + 1
        
        if next_level > 10:
            # Already at max level
            return False
        
        if business.experience_points >= level_thresholds[next_level]:
            # Level up!
            business.mastery_level = next_level
            
            # Record the event
            business.custom_data = business.custom_data or {}
            if "mastery_progression" not in business.custom_data:
                business.custom_data["mastery_progression"] = []
            
            business.custom_data["mastery_progression"].append({
                "date": datetime.utcnow().isoformat(),
                "from_level": current_level,
                "to_level": next_level,
                "experience_points": business.experience_points
            })
            
            db.commit()
            return True
        
        return False