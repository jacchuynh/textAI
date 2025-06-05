"""
World/NPC Reaction Assessment using LLM for dynamic storytelling
"""

from typing import Dict, Any, List, Optional
import logging
import json
from datetime import datetime

# Import LLM manager from your existing setup
# This is a placeholder - update with your actual LLM manager import
from ..ai_gm_llm_manager import LLMInteractionManager


class WorldReactionAssessor:
    """
    Assesses world and NPC reactions to player actions using LLM
    """
    
    def __init__(self, llm_manager: LLMInteractionManager, db_service=None):
        """
        Initialize world reaction assessor.
        
        Args:
            llm_manager: LLM manager for making API calls
            db_service: Database service for logging
        """
        self.llm_manager = llm_manager
        self.db_service = db_service
        self.logger = logging.getLogger("WorldReactionAssessor")
        
        # Track reaction assessment statistics
        self.assessment_stats = {
            'total_assessments': 0,
            'successful_assessments': 0,
            'social_context_assessments': 0,
            'environmental_assessments': 0,
            'attitude_shifts_detected': 0
        }
    
    async def assess_world_reaction(self, 
                                  player_input: str,
                                  context: Dict[str, Any],
                                  target_entity: str = None) -> Dict[str, Any]:
        """
        Assess how the world/NPCs react to player input or presence.
        
        Args:
            player_input: What the player said/did
            context: Enhanced context with reputation and world state
            target_entity: Specific NPC/faction being interacted with
            
        Returns:
            Assessment results including reaction details
        """
        self.assessment_stats['total_assessments'] += 1
        start_time = datetime.utcnow()
        
        try:
            # Determine target for reaction assessment
            if not target_entity:
                target_entity = self._determine_primary_target(context)
            
            # Build LLM prompt for world reaction assessment
            prompt = self._build_world_reaction_prompt(player_input, context, target_entity)
            
            # Call LLM for reaction assessment
            llm_result = await self.llm_manager.generate_response(
                input_text=player_input,
                context={
                    **context,
                    'target_entity': target_entity,
                    'assessment_prompt': prompt
                },
                response_type="world_reaction_assessment",
                max_tokens=250
            )
            
            if llm_result['success']:
                # Parse JSON response
                reaction_data = self._parse_reaction_response(llm_result['content'])
                
                if reaction_data:
                    self.assessment_stats['successful_assessments'] += 1
                    
                    # Track specific types of assessments
                    if 'npc' in target_entity.lower() or 'character' in target_entity.lower():
                        self.assessment_stats['social_context_assessments'] += 1
                    else:
                        self.assessment_stats['environmental_assessments'] += 1
                    
                    if reaction_data.get('subtle_attitude_shift_description'):
                        self.assessment_stats['attitude_shifts_detected'] += 1
                    
                    # Log successful assessment
                    if self.db_service:
                        await self._log_reaction_assessment(
                            player_input, target_entity, reaction_data, context
                        )
                    
                    return {
                        'success': True,
                        'target_entity': target_entity,
                        'reaction_data': reaction_data,
                        'assessment_time': (datetime.utcnow() - start_time).total_seconds(),
                        'model_used': llm_result.get('model', 'default'),
                        'llm_metadata': {
                            'tokens_used': llm_result.get('tokens_used', 0),
                            'cost_estimate': llm_result.get('cost_estimate', 0)
                        }
                    }
                else:
                    return self._create_fallback_assessment(target_entity, "Failed to parse LLM response")
            else:
                return self._create_fallback_assessment(target_entity, llm_result.get('error_message', 'LLM call failed'))
                
        except Exception as e:
            self.logger.error(f"Error in world reaction assessment: {e}")
            return self._create_fallback_assessment(target_entity, str(e))
    
    def _build_world_reaction_prompt(self, 
                                   player_input: str, 
                                   context: Dict[str, Any], 
                                   target_entity: str) -> str:
        """Build LLM prompt for world reaction assessment"""
        
        # Extract context information
        player_name = context.get('player_name', 'the adventurer')
        reputation_summary = context.get('player_reputation_summary', 'No notable reputation')
        recent_actions = context.get('recent_significant_actions', [])
        
        # Format recent actions
        if recent_actions:
            actions_text = '\n'.join([f"- {action}" for action in recent_actions])
        else:
            actions_text = "- No recent significant actions"
        
        # Get target-specific information
        target_info = self._get_target_info(target_entity, context)
        
        # Get world state context
        world_reaction_data = context.get('world_reaction_data', {})
        world_state_summary = world_reaction_data.get('world_state_summary', 'Political: stable, Economic: stable')
        
        # Build the prompt using the specified template
        prompt = f"""You are an AI Game Master assistant simulating world reactions.

Player Input: "{player_input}"

Player Profile:
- Name: {player_name}
- Reputation with {target_info['name']}: {target_info['reputation_status']}
- Recent Significant Actions by Player:
{actions_text}

Current Context:
- Interacting with: {target_info['name']} (Disposition towards player: {target_info['disposition']})
- Location: {context.get('current_location', 'unknown location')}
- World State: {world_state_summary}
- Social Atmosphere: {world_reaction_data.get('social_atmosphere', 'normal')}

Based on all this:
1. How does {target_info['name']} likely perceive the player's input/presence in this specific situation?
2. What is a plausible, brief, in-character dialogue snippet or narrative observation reflecting this reaction?
3. Are there any subtle (non-mechanical) shifts in attitude or immediate environmental responses?

Provide your response in JSON format like this:
{{
 "perception_summary": "How the target likely perceives the player's action/presence.",
 "suggested_reactive_dialogue_or_narration": "Brief dialogue or narrative snippet.",
 "subtle_attitude_shift_description": "e.g., NPC seems more wary, crowd grows quiet, etc. or null"
}}"""
        
        return prompt
    
    def _determine_primary_target(self, context: Dict[str, Any]) -> str:
        """Determine the primary target for reaction assessment"""
        
        # Check for active NPCs first
        active_npcs = context.get('active_npcs', [])
        if active_npcs:
            return f"npc_{active_npcs[0]}"
        
        # Check for present NPCs
        present_npcs = context.get('present_npcs', [])
        if present_npcs:
            return f"npc_{present_npcs[0]}"
        
        # Check for active factions
        active_factions = context.get('active_factions', [])
        if active_factions:
            return f"faction_{active_factions[0]}"
        
        # Default to location environment
        current_location = context.get('current_location', 'the area')
        return f"environment_{current_location}"
    
    def _get_target_info(self, target_entity: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Get information about the target entity"""
        
        world_reaction_data = context.get('world_reaction_data', {})
        npc_dispositions = world_reaction_data.get('npc_dispositions', {})
        
        if target_entity.startswith('npc_'):
            npc_id = target_entity[4:]  # Remove 'npc_' prefix
            
            # Try to get NPC name from context
            npcs_data = context.get('npcs', {})
            npc_name = npcs_data.get(npc_id, {}).get('name', npc_id.replace('_', ' ').title())
            
            # Get disposition
            disposition_info = npc_dispositions.get(npc_id, {})
            disposition = disposition_info.get('disposition', 'neutral')
            reputation_status = disposition_info.get('reputation_level', 'neutral')
            
            return {
                'name': npc_name,
                'disposition': disposition,
                'reputation_status': reputation_status
            }
        
        elif target_entity.startswith('faction_'):
            faction_id = target_entity[8:]  # Remove 'faction_' prefix
            faction_name = faction_id.replace('_', ' ').title()
            
            # Get faction reputation from context
            reputation_details = context.get('reputation_details', [])
            faction_rep = next(
                (rep for rep in reputation_details if faction_id in rep['entity'].lower()),
                {'level': 'neutral'}
            )
            
            return {
                'name': f"the {faction_name}",
                'disposition': self._reputation_to_disposition(faction_rep['level']),
                'reputation_status': faction_rep['level']
            }
        
        elif target_entity.startswith('environment_'):
            location = target_entity[12:]  # Remove 'environment_' prefix
            location_name = location.replace('_', ' ').title()
            
            return {
                'name': f"the environment of {location_name}",
                'disposition': 'neutral environmental response',
                'reputation_status': 'neutral'
            }
        
        else:
            return {
                'name': target_entity.replace('_', ' ').title(),
                'disposition': 'unknown',
                'reputation_status': 'unknown'
            }
    
    def _reputation_to_disposition(self, reputation_level: str) -> str:
        """Convert reputation level to disposition description"""
        disposition_map = {
            'revered': 'deeply respectful and eager to help',
            'respected': 'respectful and helpful',
            'liked': 'friendly and welcoming',
            'neutral': 'neutral and professional',
            'disliked': 'suspicious and unwelcoming',
            'despised': 'hostile and dismissive',
            'hated': 'openly antagonistic'
        }
        return disposition_map.get(reputation_level, 'uncertain')
    
    def _parse_reaction_response(self, response_content: str) -> Optional[Dict[str, Any]]:
        """Parse LLM response to extract reaction data"""
        try:
            # Extract JSON from response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                reaction_data = json.loads(json_str)
                
                # Validate required fields
                required_fields = [
                    'perception_summary',
                    'suggested_reactive_dialogue_or_narration'
                ]
                
                if all(field in reaction_data for field in required_fields):
                    # Clean up null values
                    if reaction_data.get('subtle_attitude_shift_description') == 'null':
                        reaction_data['subtle_attitude_shift_description'] = None
                    
                    return reaction_data
                else:
                    self.logger.warning(f"Missing required fields in reaction response: {reaction_data}")
                    return None
            else:
                self.logger.warning(f"No valid JSON found in response: {response_content}")
                return None
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse reaction response JSON: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing reaction response: {e}")
            return None
    
    def _create_fallback_assessment(self, target_entity: str, error_message: str) -> Dict[str, Any]:
        """Create fallback assessment when LLM fails"""
        target_name = target_entity.replace('_', ' ').title() if target_entity else "The environment"
        
        return {
            'success': False,
            'target_entity': target_entity,
            'reaction_data': {
                'perception_summary': f"{target_name} notices your presence but shows no particular reaction.",
                'suggested_reactive_dialogue_or_narration': f"{target_name} regards you with a neutral expression.",
                'subtle_attitude_shift_description': None
            },
            'error': error_message,
            'fallback_used': True
        }
    
    async def _log_reaction_assessment(self, 
                                     player_input: str, 
                                     target_entity: str, 
                                     reaction_data: Dict[str, Any], 
                                     context: Dict[str, Any]):
        """Log reaction assessment to database"""
        if self.db_service:
            await self.db_service.save_event({
                'session_id': context.get('session_id'),
                'event_type': 'WORLD_REACTION_ASSESSED',
                'actor': context.get('player_id'),
                'context': {
                    'player_input': player_input,
                    'target_entity': target_entity,
                    'perception_summary': reaction_data.get('perception_summary'),
                    'attitude_shift': reaction_data.get('subtle_attitude_shift_description'),
                    'current_location': context.get('current_location')
                }
            })
    
    def get_assessment_statistics(self) -> Dict[str, Any]:
        """Get reaction assessment statistics"""
        total = self.assessment_stats['total_assessments']
        return {
            'total_assessments': total,
            'successful_assessments': self.assessment_stats['successful_assessments'],
            'success_rate': (
                self.assessment_stats['successful_assessments'] / max(1, total)
            ),
            'social_context_assessments': self.assessment_stats['social_context_assessments'],
            'environmental_assessments': self.assessment_stats['environmental_assessments'],
            'attitude_shifts_detected': self.assessment_stats['attitude_shifts_detected'],
            'attitude_shift_rate': (
                self.assessment_stats['attitude_shifts_detected'] / max(1, total)
            )
        }