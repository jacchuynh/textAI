"""
World Reaction Integration with AI GM Brain

This module integrates the world reaction system with the AIGMBrain
to provide dynamic storytelling capabilities.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from backend.src.ai_gm.ai_gm_brain import AIGMBrain
from backend.src.ai_gm.world_reaction.enhanced_context_manager import EnhancedContextManager
from backend.src.ai_gm.world_reaction.reaction_assessor import WorldReactionAssessor
from backend.src.ai_gm.world_reaction.reputation_manager import ActionSignificance


def extend_ai_gm_brain_with_world_reaction(ai_gm_brain: AIGMBrain) -> None:
    """
    Extend the AI GM Brain with world reaction capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
    """
    # Create components
    enhanced_context_manager = EnhancedContextManager(db_service=getattr(ai_gm_brain, 'db_service', None))
    
    # Get or create LLM manager
    if hasattr(ai_gm_brain, 'llm_manager'):
        llm_manager = ai_gm_brain.llm_manager
    else:
        from backend.src.ai_gm.ai_gm_llm_manager import LLMManager
        llm_manager = LLMManager(api_key=None)  # This would normally take an API key
    
    reaction_assessor = WorldReactionAssessor(
        llm_manager=llm_manager, 
        db_service=getattr(ai_gm_brain, 'db_service', None)
    )
    
    # Store components in AI GM Brain
    ai_gm_brain.enhanced_context_manager = enhanced_context_manager
    ai_gm_brain.reaction_assessor = reaction_assessor
    
    # Add new methods to AI GM Brain
    ai_gm_brain.assess_world_reaction = lambda player_input, context, target_entity=None: _assess_world_reaction(
        ai_gm_brain, player_input, context, target_entity
    )
    
    ai_gm_brain.record_significant_action = lambda action_description, significance, location, affected_entities=None, reputation_changes=None: _record_significant_action(
        ai_gm_brain, action_description, significance, location, affected_entities, reputation_changes
    )
    
    # Override the process_player_input method to incorporate world reaction
    original_process_player_input = ai_gm_brain.process_player_input
    
    def enhanced_process_player_input(player_input: str) -> Dict[str, Any]:
        """Enhanced player input processing with world reaction."""
        # First, get the basic response using the original method
        basic_response = original_process_player_input(player_input)
        
        # Check if this is a case where world reaction should be assessed
        if _should_assess_world_reaction(basic_response, player_input):
            world_reaction = _incorporate_world_reaction(ai_gm_brain, player_input, basic_response)
            
            if world_reaction and world_reaction.get('success'):
                # Enhance the response with world reaction data
                basic_response['response_text'] = world_reaction['reaction_data']['suggested_reactive_dialogue_or_narration']
                basic_response['metadata']['world_reaction'] = {
                    'perception_summary': world_reaction['reaction_data']['perception_summary'],
                    'attitude_shift': world_reaction['reaction_data']['subtle_attitude_shift_description'],
                    'target_entity': world_reaction['target_entity']
                }
                basic_response['metadata']['processing']['world_reaction_applied'] = True
        
        return basic_response
    
    # Replace the original method with the enhanced version
    ai_gm_brain.process_player_input = enhanced_process_player_input
    
    # Add method to get world reaction statistics
    ai_gm_brain.get_world_reaction_statistics = lambda: _get_world_reaction_statistics(ai_gm_brain)
    
    # Log the extension
    logging.getLogger("AIGMBrain").info("AI GM Brain extended with world reaction capabilities")


async def _assess_world_reaction(
    ai_gm_brain: AIGMBrain, 
    player_input: str, 
    context: Optional[Dict[str, Any]] = None, 
    target_entity: Optional[str] = None
) -> Dict[str, Any]:
    """
    Assess world reaction to player input.
    
    Args:
        ai_gm_brain: AI GM Brain instance
        player_input: Player's input text
        context: Optional context dictionary (will be prepared if not provided)
        target_entity: Optional specific entity to assess reaction from
        
    Returns:
        World reaction assessment results
    """
    if not hasattr(ai_gm_brain, 'reaction_assessor'):
        return {
            'success': False,
            'error': 'World reaction assessor not initialized'
        }
    
    # Prepare context if not provided
    if not context:
        event = {'event_type': 'PLAYER_INPUT', 'input': player_input}
        context = ai_gm_brain.enhanced_context_manager.prepare_event_context(
            event, ai_gm_brain.player_id
        )
    
    # Assess world reaction
    return await ai_gm_brain.reaction_assessor.assess_world_reaction(
        player_input, context, target_entity
    )


def _record_significant_action(
    ai_gm_brain: AIGMBrain,
    action_description: str,
    significance: ActionSignificance,
    location: str,
    affected_entities: Optional[List[str]] = None,
    reputation_changes: Optional[Dict[str, int]] = None
) -> str:
    """
    Record a significant player action.
    
    Args:
        ai_gm_brain: AI GM Brain instance
        action_description: Description of the action
        significance: Action significance level
        location: Where the action occurred
        affected_entities: Optional list of affected entities
        reputation_changes: Optional reputation changes
        
    Returns:
        Action ID
    """
    if not hasattr(ai_gm_brain, 'enhanced_context_manager'):
        logging.getLogger("AIGMBrain").error("Cannot record action: enhanced context manager not initialized")
        return ""
    
    return ai_gm_brain.enhanced_context_manager.record_significant_action(
        ai_gm_brain.player_id,
        action_description,
        significance,
        location,
        affected_entities,
        reputation_changes
    )


def _should_assess_world_reaction(response: Dict[str, Any], player_input: str) -> bool:
    """
    Determine whether world reaction should be assessed for this input/response.
    
    Args:
        response: Response data from basic processing
        player_input: Original player input
        
    Returns:
        True if world reaction should be assessed
    """
    # Check if this is a social interaction or has failed parsing
    metadata = response.get('metadata', {})
    
    # Case 1: Failed to parse as a command but looks like social input
    if metadata.get('command_parser', {}).get('success') is False:
        if _is_social_input(player_input):
            return True
    
    # Case 2: Is a successful interaction with an NPC
    if "npc" in metadata.get('target_entity', '').lower():
        return True
        
    # Case 3: Is an ambiguous input that might benefit from world context
    if metadata.get('decision_tree', {}).get('response_basis') == 'GENERAL_LLM_INTERPRETATION':
        return True
    
    return False


def _is_social_input(player_input: str) -> bool:
    """
    Determine if input appears to be social interaction.
    
    Args:
        player_input: Player input text
        
    Returns:
        True if input appears to be social
    """
    social_indicators = [
        '?', 'hello', 'hi', 'hey', 'greet', 'talk', 'ask', 'tell', 'say',
        'who are you', 'what do you', 'your name', 'about you'
    ]
    
    player_input_lower = player_input.lower()
    return any(indicator in player_input_lower for indicator in social_indicators)


async def _incorporate_world_reaction(
    ai_gm_brain: AIGMBrain, 
    player_input: str, 
    basic_response: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Incorporate world reaction into response.
    
    Args:
        ai_gm_brain: AI GM Brain instance
        player_input: Player input text
        basic_response: Basic response data
        
    Returns:
        World reaction data or None if unsuccessful
    """
    try:
        # Prepare context from basic response and game state
        metadata = basic_response.get('metadata', {})
        
        # Extract target entity if available
        target_entity = metadata.get('target_entity')
        
        # Use event context manager to prepare full context
        event = {
            'event_type': 'PLAYER_INPUT',
            'input': player_input,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        context = ai_gm_brain.enhanced_context_manager.prepare_event_context(
            event, ai_gm_brain.player_id
        )
        
        # Add any additional context from the basic response
        if 'world_state' in metadata:
            context['world_state'] = metadata['world_state']
        
        # Assess world reaction
        world_reaction = await ai_gm_brain.assess_world_reaction(player_input, context, target_entity)
        return world_reaction
        
    except Exception as e:
        logging.getLogger("AIGMBrain").error(f"Error incorporating world reaction: {e}")
        return None


def _get_world_reaction_statistics(ai_gm_brain: AIGMBrain) -> Dict[str, Any]:
    """
    Get statistics about world reaction system.
    
    Args:
        ai_gm_brain: AI GM Brain instance
        
    Returns:
        Dictionary of statistics
    """
    stats = {}
    
    if hasattr(ai_gm_brain, 'reaction_assessor'):
        stats['reaction_assessments'] = ai_gm_brain.reaction_assessor.get_assessment_statistics()
    
    # Add any other relevant statistics
    
    return stats