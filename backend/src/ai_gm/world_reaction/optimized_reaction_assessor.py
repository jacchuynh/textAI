"""
Optimized World Reaction Assessor - High-performance version with async optimizations

This module provides an optimized version of the world reaction assessor that leverages
concurrent processing, intelligent caching, and batching for maximum performance.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import the base assessor and optimization components
from .reaction_assessor import WorldReactionAssessor
from ..optimizations.performance_optimizer import (
    PerformanceOptimizer, 
    monitor_performance,
    ConcurrentProcessingManager
)


class OptimizedWorldReactionAssessor(WorldReactionAssessor):
    """
    High-performance world reaction assessor with async optimizations
    """
    
    def __init__(self, llm_manager, db_service=None, optimization_config: Optional[Dict[str, Any]] = None):
        """
        Initialize optimized world reaction assessor.
        
        Args:
            llm_manager: LLM manager for making API calls
            db_service: Database service for logging
            optimization_config: Configuration for performance optimizations
        """
        super().__init__(llm_manager, db_service)
        
        # Initialize performance optimizer
        self.optimizer = PerformanceOptimizer(optimization_config)
        self.concurrent_manager = ConcurrentProcessingManager(
            max_concurrent=optimization_config.get('max_concurrent_reactions', 8) if optimization_config else 8,
            timeout=optimization_config.get('reaction_timeout', 4.0) if optimization_config else 4.0
        )
        
        self.logger = logging.getLogger("OptimizedWorldReactionAssessor")
        
        # Performance tracking
        self.optimization_stats = {
            'batch_assessments': 0,
            'concurrent_assessments': 0,
            'cache_optimizations': 0,
            'fallback_generations': 0,
            'total_time_saved': 0.0
        }
    
    async def assess_multiple_world_reactions(self,
                                            player_input: str,
                                            context: Dict[str, Any],
                                            target_entities: List[str] = None,
                                            priority_order: bool = True) -> Dict[str, Any]:
        """
        Assess reactions from multiple world entities concurrently with optimizations.
        
        Args:
            player_input: What the player said/did
            context: Enhanced context with reputation and world state
            target_entities: Specific entities to assess (if None, auto-determine)
            priority_order: Whether to prioritize certain entities over others
            
        Returns:
            Comprehensive reaction assessment from multiple entities
        """
        start_time = time.time()
        self.optimization_stats['concurrent_assessments'] += 1
        
        # Use the performance optimizer for intelligent processing
        async def process_single_reaction(request_data):
            return await self._process_single_optimized_reaction(request_data)
        
        # Get optimized results using the performance optimizer
        results = await self.optimizer.optimized_world_reaction_assessment(
            player_input=player_input,
            context=context,
            target_entities=target_entities,
            processor_func=process_single_reaction
        )
        
        # Post-process and prioritize results
        processed_results = self._post_process_multiple_results(
            results, player_input, context, priority_order
        )
        
        # Calculate time saved through optimizations
        processing_time = time.time() - start_time
        estimated_sequential_time = len(results) * 0.8  # Estimate 800ms per sequential call
        time_saved = max(0, estimated_sequential_time - processing_time)
        self.optimization_stats['total_time_saved'] += time_saved
        
        self.logger.info(
            f"Assessed {len(results)} entities in {processing_time:.3f}s "
            f"(estimated sequential time: {estimated_sequential_time:.3f}s, "
            f"time saved: {time_saved:.3f}s)"
        )
        
        return {
            'success': True,
            'total_entities_assessed': len(results),
            'successful_assessments': len([r for r in results if r.get('success', False)]),
            'reaction_results': processed_results,
            'processing_time': processing_time,
            'optimization_stats': {
                'time_saved_seconds': time_saved,
                'cache_hits': sum(1 for r in results if r.get('from_cache', False)),
                'concurrent_processed': len(results)
            },
            'performance_summary': self._generate_performance_summary()
        }
    
    async def _process_single_optimized_reaction(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single reaction request with optimizations applied.
        """
        try:
            # Extract request parameters
            player_input = request_data['player_input']
            context = request_data['context']
            target_entity = request_data['target_entity']
            
            # Use the parent class method with timing and error handling
            result = await self.assess_world_reaction(player_input, context, target_entity)
            
            # Add optimization metadata
            result['from_cache'] = False  # This would be set by the cache system
            result['optimization_applied'] = True
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in optimized reaction processing: {e}")
            return self._create_fallback_assessment(
                request_data.get('target_entity', 'unknown'),
                f"Optimization error: {str(e)}"
            )
    
    def _post_process_multiple_results(self,
                                     results: List[Dict[str, Any]],
                                     player_input: str,
                                     context: Dict[str, Any],
                                     priority_order: bool) -> List[Dict[str, Any]]:
        """
        Post-process multiple reaction results with prioritization and filtering.
        """
        if not priority_order:
            return results
        
        # Define priority order for different entity types
        priority_map = {
            'npc_': 1,      # NPCs get highest priority
            'faction_': 2,  # Factions get medium priority
            'environment_': 3  # Environment gets lowest priority
        }
        
        # Sort results by priority and success status
        def sort_key(result):
            target_entity = result.get('target_entity', 'unknown')
            entity_type = next(
                (prefix for prefix in priority_map.keys() if target_entity.startswith(prefix)),
                'unknown_'
            )
            priority = priority_map.get(entity_type, 999)
            success = result.get('success', False)
            
            # Successful results get higher priority
            return (priority, not success)
        
        sorted_results = sorted(results, key=sort_key)
        
        # Add priority metadata
        for i, result in enumerate(sorted_results):
            result['priority_rank'] = i + 1
            result['total_results'] = len(sorted_results)
        
        return sorted_results
    
    async def assess_world_reaction_with_fallback(self,
                                                player_input: str,
                                                context: Dict[str, Any],
                                                target_entity: str = None,
                                                fallback_timeout: float = 2.0) -> Dict[str, Any]:
        """
        Assess world reaction with intelligent fallback strategies.
        
        This method provides multiple fallback layers for maximum reliability:
        1. Primary LLM assessment
        2. Fast fallback generation if timeout occurs
        3. Rule-based fallback if all else fails
        """
        try:
            # Attempt primary assessment with timeout
            result = await asyncio.wait_for(
                self.assess_world_reaction(player_input, context, target_entity),
                timeout=fallback_timeout
            )
            
            if result.get('success', False):
                return result
            else:
                # Primary assessment failed, try fallback
                return await self._generate_intelligent_fallback(
                    player_input, context, target_entity, "primary_assessment_failed"
                )
                
        except asyncio.TimeoutError:
            self.logger.warning(f"Assessment timeout for {target_entity}, generating fallback")
            self.optimization_stats['fallback_generations'] += 1
            
            return await self._generate_intelligent_fallback(
                player_input, context, target_entity, "timeout"
            )
            
        except Exception as e:
            self.logger.error(f"Assessment error: {e}")
            return await self._generate_intelligent_fallback(
                player_input, context, target_entity, f"error: {str(e)}"
            )
    
    async def _generate_intelligent_fallback(self,
                                           player_input: str,
                                           context: Dict[str, Any],
                                           target_entity: str,
                                           reason: str) -> Dict[str, Any]:
        """
        Generate an intelligent fallback response using rule-based logic.
        """
        self.optimization_stats['fallback_generations'] += 1
        
        # Analyze input for emotional content and intent
        input_analysis = self._analyze_player_input(player_input)
        target_info = self._get_target_info(target_entity, context)
        
        # Generate contextually appropriate fallback
        fallback_reaction = self._generate_contextual_fallback(
            input_analysis, target_info, context
        )
        
        return {
            'success': True,  # Fallback is considered successful
            'target_entity': target_entity,
            'reaction_data': fallback_reaction,
            'fallback_reason': reason,
            'assessment_time': 0.05,  # Very fast fallback
            'is_fallback': True,
            'fallback_quality': 'intelligent_rule_based'
        }
    
    def _analyze_player_input(self, player_input: str) -> Dict[str, Any]:
        """
        Analyze player input for emotional content and intent using rule-based logic.
        """
        input_lower = player_input.lower()
        
        # Detect emotional markers
        aggressive_words = ['attack', 'fight', 'kill', 'destroy', 'hate', 'angry']
        friendly_words = ['hello', 'greet', 'friend', 'help', 'thank', 'please']
        questioning_words = ['what', 'where', 'why', 'how', 'who', 'when']
        
        emotion_score = {
            'aggressive': sum(1 for word in aggressive_words if word in input_lower),
            'friendly': sum(1 for word in friendly_words if word in input_lower),
            'questioning': sum(1 for word in questioning_words if word in input_lower)
        }
        
        # Determine dominant emotion
        dominant_emotion = max(emotion_score.keys(), key=lambda k: emotion_score[k])
        
        return {
            'dominant_emotion': dominant_emotion if emotion_score[dominant_emotion] > 0 else 'neutral',
            'emotion_intensity': max(emotion_score.values()),
            'input_length': len(player_input.split()),
            'contains_question': '?' in player_input
        }
    
    def _generate_contextual_fallback(self,
                                    input_analysis: Dict[str, Any],
                                    target_info: Dict[str, str],
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate contextually appropriate fallback reaction based on analysis.
        """
        emotion = input_analysis['dominant_emotion']
        target_name = target_info['name']
        disposition = target_info['disposition']
        
        # Base reactions by emotion type
        emotion_reactions = {
            'aggressive': {
                'perception_summary': f"{target_name} perceives the aggressive tone and reacts accordingly.",
                'suggested_reactive_dialogue_or_narration': 
                    f"{target_name} tenses up, sensing the hostile intent." if 'hostile' in disposition 
                    else f"{target_name} steps back cautiously, unsure of the aggressive approach.",
                'subtle_attitude_shift_description': 
                    "The atmosphere grows tense and wary." if input_analysis['emotion_intensity'] > 1 else None
            },
            'friendly': {
                'perception_summary': f"{target_name} notices the friendly approach and responds appropriately.",
                'suggested_reactive_dialogue_or_narration':
                    f"{target_name} smiles warmly in response." if 'friendly' in disposition
                    else f"{target_name} nods politely, acknowledging the greeting.",
                'subtle_attitude_shift_description':
                    "The mood lightens slightly." if input_analysis['emotion_intensity'] > 1 else None
            },
            'questioning': {
                'perception_summary': f"{target_name} recognizes a question or inquiry being posed.",
                'suggested_reactive_dialogue_or_narration':
                    f"{target_name} considers the question thoughtfully." if 'helpful' in disposition
                    else f"{target_name} looks uncertain about how to respond.",
                'subtle_attitude_shift_description': None
            },
            'neutral': {
                'perception_summary': f"{target_name} observes the neutral interaction without strong reaction.",
                'suggested_reactive_dialogue_or_narration':
                    f"{target_name} maintains their current demeanor.",
                'subtle_attitude_shift_description': None
            }
        }
        
        return emotion_reactions.get(emotion, emotion_reactions['neutral'])
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of current performance optimizations.
        """
        total_assessments = self.optimization_stats['concurrent_assessments']
        total_time_saved = self.optimization_stats['total_time_saved']
        
        return {
            'total_optimized_assessments': total_assessments,
            'total_time_saved_seconds': total_time_saved,
            'average_time_saved_per_assessment': 
                total_time_saved / total_assessments if total_assessments > 0 else 0,
            'optimization_efficiency_percent': 
                (total_time_saved / (total_assessments * 0.8) * 100) if total_assessments > 0 else 0,
            'fallback_usage_rate': 
                (self.optimization_stats['fallback_generations'] / total_assessments * 100) 
                if total_assessments > 0 else 0,
            'performance_optimizer_stats': self.optimizer.get_performance_report()
        }
    
    async def assess_priority_reactions(self,
                                      player_input: str,
                                      context: Dict[str, Any],
                                      max_entities: int = 3) -> Dict[str, Any]:
        """
        Assess reactions from the most important entities only, optimized for speed.
        
        This method is designed for time-critical situations where only the most
        relevant reactions are needed quickly.
        """
        # Determine priority entities
        priority_entities = self._determine_priority_entities(context, max_entities)
        
        if not priority_entities:
            return {
                'success': False,
                'message': 'No priority entities found for assessment'
            }
        
        # Process with high-priority optimizations
        start_time = time.time()
        
        # Use shorter timeouts for priority assessments
        original_timeout = self.concurrent_manager.timeout
        self.concurrent_manager.timeout = 1.5  # Faster timeout for priority
        
        try:
            result = await self.assess_multiple_world_reactions(
                player_input=player_input,
                context=context,
                target_entities=priority_entities,
                priority_order=True
            )
            
            result['is_priority_assessment'] = True
            result['priority_processing_time'] = time.time() - start_time
            
            return result
            
        finally:
            # Restore original timeout
            self.concurrent_manager.timeout = original_timeout
    
    def _determine_priority_entities(self, context: Dict[str, Any], max_entities: int) -> List[str]:
        """
        Determine the highest priority entities for reaction assessment.
        """
        entities = []
        
        # Priority 1: Active dialogue NPCs
        active_npcs = context.get('active_npcs', [])
        entities.extend([f"npc_{npc}" for npc in active_npcs[:2]])
        
        # Priority 2: Combat-relevant entities
        if context.get('in_combat', False):
            combat_npcs = context.get('combat_npcs', [])
            entities.extend([f"npc_{npc}" for npc in combat_npcs[:1]])
        
        # Priority 3: Location-specific important NPCs
        location_npcs = context.get('location_important_npcs', [])
        entities.extend([f"npc_{npc}" for npc in location_npcs[:1]])
        
        # Priority 4: Environment (always included)
        current_location = context.get('current_location')
        if current_location:
            entities.append(f"environment_{current_location}")
        
        # Remove duplicates and limit to max_entities
        unique_entities = list(dict.fromkeys(entities))  # Preserves order
        return unique_entities[:max_entities]
    
    async def get_optimization_report(self) -> Dict[str, Any]:
        """
        Get comprehensive optimization performance report.
        """
        base_stats = self.assessment_stats.copy()
        optimization_stats = self.optimization_stats.copy()
        performance_report = self.optimizer.get_performance_report()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'base_assessment_stats': base_stats,
            'optimization_stats': optimization_stats,
            'performance_optimizer_report': performance_report,
            'efficiency_metrics': {
                'total_time_saved': optimization_stats['total_time_saved'],
                'average_entities_per_assessment': 
                    base_stats['total_assessments'] / optimization_stats['concurrent_assessments']
                    if optimization_stats['concurrent_assessments'] > 0 else 0,
                'optimization_success_rate': 
                    ((optimization_stats['concurrent_assessments'] - optimization_stats['fallback_generations']) / 
                     optimization_stats['concurrent_assessments'] * 100)
                    if optimization_stats['concurrent_assessments'] > 0 else 0
            },
            'recommendations': self._get_optimization_recommendations()
        }
    
    def _get_optimization_recommendations(self) -> List[str]:
        """
        Generate optimization recommendations based on current performance.
        """
        recommendations = []
        
        # Analyze fallback usage
        if self.optimization_stats['concurrent_assessments'] > 0:
            fallback_rate = (self.optimization_stats['fallback_generations'] / 
                           self.optimization_stats['concurrent_assessments'])
            
            if fallback_rate > 0.3:
                recommendations.append(
                    "High fallback usage detected. Consider increasing timeouts or improving LLM reliability."
                )
            elif fallback_rate < 0.1:
                recommendations.append(
                    "Low fallback usage indicates good system reliability. Consider reducing timeouts for faster response."
                )
        
        # Analyze time savings
        avg_time_saved = (self.optimization_stats['total_time_saved'] / 
                         self.optimization_stats['concurrent_assessments']
                         if self.optimization_stats['concurrent_assessments'] > 0 else 0)
        
        if avg_time_saved > 1.0:
            recommendations.append(
                "Excellent time savings from optimizations. System is performing well."
            )
        elif avg_time_saved < 0.3:
            recommendations.append(
                "Limited time savings detected. Consider increasing concurrent processing limits."
            )
        
        # Add general performance optimizer recommendations
        recommendations.extend(self.optimizer._get_optimization_recommendations())
        
        return recommendations
