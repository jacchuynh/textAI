"""
Enhanced World Reaction Integration with Performance Optimizations

This module provides an optimized integration of the world reaction system
with comprehensive async performance optimizations, caching, and intelligent fallbacks.
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..ai_gm_brain import AIGMBrain
from .enhanced_context_manager import EnhancedContextManager
from .optimized_reaction_assessor import OptimizedWorldReactionAssessor
from .reputation_manager import ActionSignificance
from ..optimizations.performance_optimizer import PerformanceOptimizer


class OptimizedWorldReactionIntegration:
    """
    High-performance world reaction integration with advanced optimizations
    """
    
    def __init__(self, 
                 ai_gm_brain: AIGMBrain,
                 optimization_config: Optional[Dict[str, Any]] = None):
        """
        Initialize optimized world reaction integration.
        
        Args:
            ai_gm_brain: AI GM Brain instance to extend
            optimization_config: Performance optimization configuration
        """
        self.ai_gm_brain = ai_gm_brain
        self.logger = logging.getLogger("OptimizedWorldReactionIntegration")
        
        # Default optimization configuration
        self.optimization_config = optimization_config or {
            'max_concurrent_reactions': 8,
            'reaction_timeout': 4.0,
            'cache_max_size': 1000,
            'cache_default_ttl': 300,
            'batch_size': 5,
            'batch_timeout': 1.0,
            'enable_intelligent_fallbacks': True,
            'enable_priority_processing': True,
            'enable_background_updates': True
        }
        
        # Initialize components
        self._initialize_components()
        
        # Integration statistics
        self.integration_stats = {
            'total_integrations': 0,
            'successful_optimizations': 0,
            'fallback_usage': 0,
            'background_updates': 0,
            'cache_optimizations': 0
        }
    
    def _initialize_components(self):
        """Initialize all integration components"""
        try:
            # Enhanced context manager
            self.enhanced_context_manager = EnhancedContextManager(
                db_service=getattr(self.ai_gm_brain, 'db_service', None)
            )
            
            # Get or create LLM manager
            if hasattr(self.ai_gm_brain, 'llm_manager'):
                llm_manager = self.ai_gm_brain.llm_manager
            else:
                from ..ai_gm_llm_manager import LLMInteractionManager
                llm_manager = LLMInteractionManager(self.ai_gm_brain)
                self.ai_gm_brain.llm_manager = llm_manager
            
            # Optimized reaction assessor
            self.reaction_assessor = OptimizedWorldReactionAssessor(
                llm_manager=llm_manager,
                db_service=getattr(self.ai_gm_brain, 'db_service', None),
                optimization_config=self.optimization_config
            )
            
            # Performance optimizer
            self.performance_optimizer = PerformanceOptimizer(self.optimization_config)
            
            self.logger.info("All optimization components initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing optimization components: {e}")
            raise
    
    def integrate(self):
        """
        Integrate optimized world reaction capabilities into AI GM Brain
        """
        try:
            # Store components in AI GM Brain
            self.ai_gm_brain.enhanced_context_manager = self.enhanced_context_manager
            self.ai_gm_brain.reaction_assessor = self.reaction_assessor
            self.ai_gm_brain.world_reaction_optimizer = self.performance_optimizer
            
            # Add optimized async methods
            self._add_optimized_methods()
            
            # Override core processing with optimizations
            self._enhance_core_processing()
            
            # Add performance monitoring methods
            self._add_monitoring_methods()
            
            # Start background optimization tasks if enabled
            if self.optimization_config.get('enable_background_updates', True):
                self._start_background_tasks()
            
            self.logger.info("Optimized world reaction integration completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during optimized integration: {e}")
            raise
    
    def _add_optimized_methods(self):
        """Add optimized world reaction methods to AI GM Brain"""
        
        # High-performance async world reaction assessment
        async def assess_world_reaction_optimized(player_input: str, 
                                                context: Optional[Dict[str, Any]] = None,
                                                target_entities: Optional[List[str]] = None,
                                                priority_mode: bool = False) -> Dict[str, Any]:
            """
            Optimized world reaction assessment with multiple entities and caching
            """
            self.integration_stats['total_integrations'] += 1
            
            # Enhance context with current game state
            enhanced_context = await self._enhance_context(context or {})
            
            try:
                if priority_mode:
                    # Use priority assessment for time-critical situations
                    result = await self.reaction_assessor.assess_priority_reactions(
                        player_input,
                        enhanced_context,
                        max_entities=3
                    )
                else:
                    # Full multi-entity assessment
                    result = await self.reaction_assessor.assess_multiple_world_reactions(
                        player_input,
                        enhanced_context,
                        target_entities,
                        priority_order=True
                    )
                
                if result.get('success', False):
                    self.integration_stats['successful_optimizations'] += 1
                    
                    # Schedule background context updates if enabled
                    if self.optimization_config.get('enable_background_updates', True):
                        asyncio.create_task(self._update_context_background(
                            player_input, result, enhanced_context
                        ))
                
                return result
                
            except Exception as e:
                self.logger.error(f"Error in optimized world reaction assessment: {e}")
                return self._create_integration_fallback(player_input, enhanced_context, str(e))
        
        # Synchronous wrapper with async execution
        def assess_world_reaction_sync(player_input: str,
                                     context: Optional[Dict[str, Any]] = None,
                                     target_entity: Optional[str] = None) -> Dict[str, Any]:
            """
            Synchronous wrapper for optimized world reaction assessment
            """
            try:
                # Create new event loop if none exists
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_closed():
                        raise RuntimeError("Event loop is closed")
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Convert single target_entity to list if provided
                target_entities = [target_entity] if target_entity else None
                
                # Run the async assessment
                if loop.is_running():
                    # If loop is already running, return a sync fallback to avoid blocking
                    # In production, this would queue the task for later processing
                    self.logger.debug("Event loop already running, using sync fallback")
                    return self._create_sync_fallback(player_input, context or {})
                else:
                    # Run in the event loop
                    return loop.run_until_complete(assess_world_reaction_optimized(
                        player_input, context, target_entities, priority_mode=True
                    ))
                    
            except Exception as e:
                self.logger.error(f"Error in sync world reaction wrapper: {e}")
                return self._create_sync_fallback(player_input, context or {}, str(e))
        
        # Batch processing method for multiple inputs
        async def assess_batch_world_reactions(inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
            """
            Process multiple world reaction assessments in batch for efficiency
            """
            if not inputs:
                return []
            
            self.logger.info(f"Processing batch of {len(inputs)} world reaction assessments")
            
            # Process all inputs concurrently
            tasks = [
                assess_world_reaction_optimized(
                    item.get('player_input', ''),
                    item.get('context', {}),
                    item.get('target_entities'),
                    priority_mode=item.get('priority_mode', False)
                )
                for item in inputs
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append(
                        self._create_integration_fallback(
                            inputs[i].get('player_input', ''),
                            inputs[i].get('context', {}),
                            str(result)
                        )
                    )
                else:
                    processed_results.append(result)
            
            return processed_results
        
        # Add methods to AI GM Brain
        self.ai_gm_brain.assess_world_reaction_optimized = assess_world_reaction_optimized
        self.ai_gm_brain.assess_world_reaction = assess_world_reaction_sync
        self.ai_gm_brain.assess_world_reaction_async = assess_world_reaction_optimized
        self.ai_gm_brain.assess_batch_world_reactions = assess_batch_world_reactions
        
        # Legacy compatibility
        self.ai_gm_brain.record_significant_action = self._record_significant_action
    
    def _enhance_core_processing(self):
        """Enhance core AI GM processing with optimized world reactions"""
        
        # Store original method
        if hasattr(self.ai_gm_brain, '_original_process_player_input'):
            original_process_player_input = self.ai_gm_brain._original_process_player_input
        else:
            original_process_player_input = self.ai_gm_brain.process_player_input
            self.ai_gm_brain._original_process_player_input = original_process_player_input
        
        async def enhanced_process_player_input_async(player_input: str) -> Dict[str, Any]:
            """
            Enhanced async player input processing with optimized world reactions
            """
            start_time = datetime.utcnow()
            
            # Get basic response
            if asyncio.iscoroutinefunction(original_process_player_input):
                basic_response = await original_process_player_input(player_input)
            else:
                basic_response = original_process_player_input(player_input)
            
            # Check if world reaction should be assessed
            if self._should_assess_world_reaction(basic_response, player_input):
                # Perform optimized world reaction assessment
                world_reaction_result = await self.ai_gm_brain.assess_world_reaction_async(
                    player_input,
                    context=basic_response.get('metadata', {}).get('context', {}),
                    priority_mode=True  # Use priority mode for real-time responses
                )
                
                if world_reaction_result.get('success', False):
                    # Integrate world reaction into response
                    basic_response = self._integrate_world_reaction_result(
                        basic_response, world_reaction_result
                    )
                    
                    # Add optimization metadata
                    if 'metadata' not in basic_response:
                        basic_response['metadata'] = {}
                    
                    basic_response['metadata']['world_reaction_optimization'] = {
                        'enabled': True,
                        'processing_time': world_reaction_result.get('processing_time', 0),
                        'entities_assessed': world_reaction_result.get('total_entities_assessed', 0),
                        'cache_hits': world_reaction_result.get('optimization_stats', {}).get('cache_hits', 0),
                        'fallbacks_used': len([r for r in world_reaction_result.get('reaction_results', []) 
                                             if r.get('is_fallback', False)])
                    }
            
            # Add overall processing time
            total_processing_time = (datetime.utcnow() - start_time).total_seconds()
            if 'metadata' not in basic_response:
                basic_response['metadata'] = {}
            basic_response['metadata']['total_processing_time'] = total_processing_time
            
            return basic_response
        
        def enhanced_process_player_input_sync(player_input: str) -> Dict[str, Any]:
            """
            Enhanced sync player input processing with optimized world reactions
            """
            try:
                # Try to run async version if possible
                try:
                    loop = asyncio.get_event_loop()
                    if not loop.is_running():
                        return loop.run_until_complete(
                            enhanced_process_player_input_async(player_input)
                        )
                except RuntimeError:
                    # No event loop available, use sync fallback
                    self.logger.debug("No event loop available, using sync fallback processing")
                    return self._create_sync_fallback_with_basic_processing(player_input, original_process_player_input)
                
                # Fallback to sync processing
                basic_response = original_process_player_input(player_input)
                
                # Add sync world reaction if enabled
                if self._should_assess_world_reaction(basic_response, player_input):
                    sync_world_reaction = self.ai_gm_brain.assess_world_reaction(
                        player_input=player_input,
                        context=basic_response.get('metadata', {}).get('context', {})
                    )
                    
                    if sync_world_reaction.get('success', False):
                        basic_response = self._integrate_world_reaction_result(
                            basic_response, sync_world_reaction
                        )
                
                return basic_response
                
            except Exception as e:
                self.logger.error(f"Error in enhanced sync processing: {e}")
                return original_process_player_input(player_input)
        
        # Replace methods
        self.ai_gm_brain.process_player_input_async = enhanced_process_player_input_async
        self.ai_gm_brain.process_player_input = enhanced_process_player_input_sync
    
    def _add_monitoring_methods(self):
        """Add performance monitoring and reporting methods"""
        
        async def get_optimization_performance_report() -> Dict[str, Any]:
            """Get comprehensive optimization performance report"""
            reaction_report = await self.reaction_assessor.get_optimization_report()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'integration_stats': self.integration_stats.copy(),
                'reaction_assessor_report': reaction_report,
                'performance_optimizer_report': self.performance_optimizer.get_performance_report(),
                'system_recommendations': self._generate_system_recommendations()
            }
        
        def get_optimization_status() -> Dict[str, Any]:
            """Get current optimization status"""
            return {
                'optimization_enabled': True,
                'components_active': {
                    'enhanced_context_manager': hasattr(self.ai_gm_brain, 'enhanced_context_manager'),
                    'optimized_reaction_assessor': hasattr(self.ai_gm_brain, 'reaction_assessor'),
                    'performance_optimizer': hasattr(self.ai_gm_brain, 'world_reaction_optimizer'),
                    'background_tasks': self.optimization_config.get('enable_background_updates', False)
                },
                'integration_stats': self.integration_stats.copy(),
                'last_optimization_check': datetime.utcnow().isoformat()
            }
        
        # Add monitoring methods to AI GM Brain
        self.ai_gm_brain.get_optimization_performance_report = get_optimization_performance_report
        self.ai_gm_brain.get_optimization_status = get_optimization_status
    
    async def _enhance_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance context with current game state information"""
        enhanced_context = context.copy()
        
        # Add AI GM Brain specific context
        enhanced_context.update({
            'game_id': getattr(self.ai_gm_brain, 'game_id', 'unknown'),
            'player_id': getattr(self.ai_gm_brain, 'player_id', 'unknown'),
            'processing_mode': getattr(self.ai_gm_brain, 'current_mode', 'default'),
            'optimization_enabled': True
        })
        
        # Use enhanced context manager if available
        if hasattr(self.enhanced_context_manager, 'enhance_context_for_assessment'):
            try:
                enhanced_context = await self.enhanced_context_manager.enhance_context_for_assessment(
                    enhanced_context
                )
            except Exception as e:
                self.logger.warning(f"Error enhancing context: {e}")
        
        return enhanced_context
    
    def _should_assess_world_reaction(self, response: Dict[str, Any], player_input: str) -> bool:
        """Determine if world reaction should be assessed"""
        # Skip for certain response types
        skip_types = ['system_message', 'error', 'ooc_command']
        response_type = response.get('response_type', 'narrative')
        
        if response_type in skip_types:
            return False
        
        # Skip for very short inputs
        if len(player_input.strip()) < 3:
            return False
        
        # Skip if explicitly disabled
        if response.get('metadata', {}).get('skip_world_reaction', False):
            return False
        
        return True
    
    def _integrate_world_reaction_result(self, 
                                       basic_response: Dict[str, Any], 
                                       world_reaction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate world reaction results into the basic response"""
        if not world_reaction_result.get('success', False):
            return basic_response
        
        reaction_results = world_reaction_result.get('reaction_results', [])
        if not reaction_results:
            return basic_response
        
        # Get the highest priority reaction
        primary_reaction = reaction_results[0]
        reaction_data = primary_reaction.get('reaction_data', {})
        
        # Enhance response text with world reaction
        suggested_narration = reaction_data.get('suggested_reactive_dialogue_or_narration', '')
        if suggested_narration:
            # Append or replace response text based on quality
            if primary_reaction.get('is_fallback', False):
                # For fallbacks, append to existing response
                if basic_response.get('response_text'):
                    basic_response['response_text'] += f" {suggested_narration}"
                else:
                    basic_response['response_text'] = suggested_narration
            else:
                # For high-quality reactions, use as primary response
                basic_response['response_text'] = suggested_narration
        
        # Add world reaction metadata
        if 'metadata' not in basic_response:
            basic_response['metadata'] = {}
        
        basic_response['metadata']['world_reaction'] = {
            'primary_target': primary_reaction.get('target_entity', 'unknown'),
            'perception_summary': reaction_data.get('perception_summary', ''),
            'attitude_shift': reaction_data.get('subtle_attitude_shift_description'),
            'total_entities_assessed': len(reaction_results),
            'processing_time': world_reaction_result.get('processing_time', 0),
            'optimization_applied': True
        }
        
        return basic_response
    
    def _create_integration_fallback(self, 
                                   player_input: str, 
                                   context: Dict[str, Any], 
                                   error: str) -> Dict[str, Any]:
        """Create fallback response for integration errors"""
        self.integration_stats['fallback_usage'] += 1
        
        return {
            'success': False,
            'total_entities_assessed': 0,
            'reaction_results': [],
            'processing_time': 0.0,
            'fallback_reason': f'integration_error: {error}',
            'optimization_stats': {
                'time_saved_seconds': 0,
                'cache_hits': 0,
                'concurrent_processed': 0
            }
        }
    
    def _create_sync_fallback(self, 
                            player_input: str, 
                            context: Dict[str, Any], 
                            error: str = None) -> Dict[str, Any]:
        """Create fallback response for sync processing"""
        return {
            'success': True,
            'target_entity': 'environment_current',
            'reaction_data': {
                'perception_summary': 'The environment responds naturally to the action.',
                'suggested_reactive_dialogue_or_narration': 'The area remains quiet as the action unfolds.',
                'subtle_attitude_shift_description': None
            },
            'fallback_reason': f'sync_processing{": " + error if error else ""}',
            'assessment_time': 0.05,
            'is_fallback': True
        }
    
    def _create_sync_fallback_with_basic_processing(self, 
                                                  player_input: str, 
                                                  original_process_player_input) -> Dict[str, Any]:
        """Create fallback response using basic processing when async fails"""
        try:
            # Get basic response using original processing
            basic_response = original_process_player_input(player_input)
            
            # Add sync world reaction if enabled and appropriate
            if self._should_assess_world_reaction(basic_response, player_input):
                sync_world_reaction = self.ai_gm_brain.assess_world_reaction(
                    player_input=player_input,
                    context=basic_response.get('metadata', {}).get('context', {})
                )
                
                if sync_world_reaction.get('success', False):
                    basic_response = self._integrate_world_reaction_result(
                        basic_response, sync_world_reaction
                    )
            
            return basic_response
            
        except Exception as e:
            self.logger.error(f"Error in sync fallback processing: {e}")
            return original_process_player_input(player_input)
    
    async def _update_context_background(self, 
                                       player_input: str, 
                                       world_reaction_result: Dict[str, Any], 
                                       context: Dict[str, Any]):
        """Update context information in the background"""
        try:
            self.integration_stats['background_updates'] += 1
            
            # Update reputation based on reactions
            # Update world state based on attitude shifts
            # Log significant interactions
            
            # This would integrate with the enhanced context manager
            # For now, we'll just log the update
            self.logger.debug(f"Background context update completed for input: {player_input[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Error in background context update: {e}")
    
    def _record_significant_action(self, 
                                 action_description: str, 
                                 significance: ActionSignificance, 
                                 location: str, 
                                 affected_entities: Optional[List[str]] = None, 
                                 reputation_changes: Optional[Dict[str, int]] = None) -> bool:
        """Record significant action for world reaction tracking"""
        try:
            # This would integrate with the enhanced context manager and reputation system
            self.logger.info(f"Recorded significant action: {action_description}")
            return True
        except Exception as e:
            self.logger.error(f"Error recording significant action: {e}")
            return False
    
    def _start_background_tasks(self):
        """Start background optimization tasks"""
        async def cleanup_task():
            """Periodic cleanup of caches and optimization data"""
            while True:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    
                    # Clean up caches
                    if hasattr(self.reaction_assessor, 'optimizer'):
                        self.reaction_assessor.optimizer.cache._clean_expired()
                    
                    self.logger.debug("Background cleanup completed")
                    
                except Exception as e:
                    self.logger.error(f"Error in background cleanup: {e}")
        
        # Start the cleanup task only if there's an event loop
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(cleanup_task())
                self.logger.info("Background optimization tasks started")
            else:
                self.logger.info("No running event loop, background tasks deferred")
        except RuntimeError:
            # No event loop available
            self.logger.info("No event loop available, background tasks disabled")
    
    def _generate_system_recommendations(self) -> List[str]:
        """Generate system optimization recommendations"""
        recommendations = []
        
        # Analyze integration performance
        total_integrations = self.integration_stats['total_integrations']
        if total_integrations > 0:
            success_rate = (self.integration_stats['successful_optimizations'] / total_integrations) * 100
            fallback_rate = (self.integration_stats['fallback_usage'] / total_integrations) * 100
            
            if success_rate > 90:
                recommendations.append("System optimization is performing excellently")
            elif success_rate < 70:
                recommendations.append("Consider increasing timeout values or improving error handling")
            
            if fallback_rate > 20:
                recommendations.append("High fallback usage detected - check LLM connectivity and performance")
        
        # Check configuration optimization
        if self.optimization_config.get('max_concurrent_reactions', 0) < 5:
            recommendations.append("Consider increasing max_concurrent_reactions for better performance")
        
        if not self.optimization_config.get('enable_background_updates', True):
            recommendations.append("Enable background updates for better context tracking")
        
        return recommendations


def extend_ai_gm_brain_with_optimized_world_reaction(
    ai_gm_brain: AIGMBrain, 
    optimization_config: Optional[Dict[str, Any]] = None
) -> OptimizedWorldReactionIntegration:
    """
    Extend AI GM Brain with optimized world reaction capabilities.
    
    Args:
        ai_gm_brain: AI GM Brain instance to extend
        optimization_config: Performance optimization configuration
        
    Returns:
        OptimizedWorldReactionIntegration instance for monitoring and control
    """
    integration = OptimizedWorldReactionIntegration(ai_gm_brain, optimization_config)
    integration.integrate()
    
    # Log the enhancement
    logging.getLogger("AIGMBrain").info(
        "AI GM Brain extended with optimized world reaction capabilities"
    )
    
    return integration


# Legacy compatibility function
def extend_ai_gm_brain_with_world_reaction(ai_gm_brain: AIGMBrain) -> None:
    """
    Legacy compatibility function - now uses optimized version
    """
    extend_ai_gm_brain_with_optimized_world_reaction(ai_gm_brain)
