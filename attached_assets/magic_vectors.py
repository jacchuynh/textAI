"""
Magic System Vector Database Integration
Spell similarity, recommendations, and magic intelligence
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
import redis
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
import faiss
import pickle
from datetime import datetime, timedelta

from app.db.magic_models import SpellTemplate, PlayerMagicState, MagicEvent
from app.db.database import SessionLocal

class MagicVectorDatabase:
    """
    Vector database for magic system intelligence
    Handles spell similarity, recommendations, and pattern matching
    """
    
    def __init__(self, redis_client=None, dimension=128):
        self.redis_client = redis_client or redis.Redis(host='localhost', port=6379, db=1)
        self.dimension = dimension
        self.scaler = StandardScaler()
        
        # FAISS index for fast similarity search
        self.spell_index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.player_preference_index = faiss.IndexFlatIP(dimension)
        
        # Cache for frequently accessed vectors
        self.vector_cache = {}
        
    def generate_spell_vector(self, spell_data: Dict[str, Any]) -> np.ndarray:
        """
        Generate a feature vector for a spell
        Captures spell characteristics for similarity matching
        """
        features = []
        
        # Basic spell properties (normalized)
        features.extend([
            spell_data.get('mana_cost', 0) / 100.0,  # Normalized mana cost
            spell_data.get('cast_time', 1) / 10.0,   # Normalized cast time
            spell_data.get('tier', 1) / 3.0,         # Spell tier
            len(spell_data.get('components', [])) / 10.0,  # Component complexity
        ])
        
        # Magic type one-hot encoding
        magic_types = ['arcane', 'mana', 'spiritual', 'elemental', 'divine']
        magic_type = spell_data.get('magic_type', 'arcane')
        magic_type_vector = [1.0 if mt == magic_type else 0.0 for mt in magic_types]
        features.extend(magic_type_vector)
        
        # Effect categories (presence/absence)
        effect_categories = ['damage', 'heal', 'buff', 'debuff', 'utility', 'movement', 'shield']
        effects = spell_data.get('effects', {})
        effect_vector = [1.0 if cat in effects else 0.0 for cat in effect_categories]
        features.extend(effect_vector)
        
        # Component type encoding
        component_types = ['verbal', 'somatic', 'material', 'focus', 'divine_focus']
        components = spell_data.get('components', [])
        component_vector = [1.0 if comp in components else 0.0 for comp in component_types]
        features.extend(component_vector)
        
        # Range and duration categories
        range_categories = ['self', 'touch', 'close', 'medium', 'long', 'unlimited']
        spell_range = spell_data.get('range', 'medium')
        range_vector = [1.0 if r == spell_range else 0.0 for r in range_categories]
        features.extend(range_vector)
        
        # Duration categories
        duration_categories = ['instant', 'rounds', 'minutes', 'hours', 'permanent']
        duration = spell_data.get('duration', 'instant')
        duration_vector = [1.0 if d == duration else 0.0 for d in duration_categories]
        features.extend(duration_vector)
        
        # School/domain associations
        schools = ['evocation', 'illusion', 'transmutation', 'conjuration', 'enchantment', 'abjuration', 'divination', 'necromancy']
        school = spell_data.get('school', 'evocation')
        school_vector = [1.0 if s == school else 0.0 for s in schools]
        features.extend(school_vector)
        
        # Corruption risk and difficulty
        features.extend([
            spell_data.get('corruption_risk', 0) / 10.0,
            spell_data.get('difficulty', 1) / 10.0,
            spell_data.get('ritual_time', 0) / 60.0,  # Ritual time in minutes
        ])
        
        # Environmental preferences
        environments = ['indoor', 'outdoor', 'underground', 'water', 'air', 'leyline']
        preferred_env = spell_data.get('preferred_environment', 'indoor')
        env_vector = [1.0 if env == preferred_env else 0.0 for env in environments]
        features.extend(env_vector)
        
        # Pad or truncate to fixed dimension
        if len(features) < self.dimension:
            features.extend([0.0] * (self.dimension - len(features)))
        else:
            features = features[:self.dimension]
        
        return np.array(features, dtype=np.float32)
    
    def generate_player_preference_vector(self, player_id: str) -> np.ndarray:
        """
        Generate a preference vector for a player based on their magic usage history
        """
        cache_key = f"player_pref_vector:{player_id}"
        
        # Check cache first
        cached_vector = self.redis_client.get(cache_key)
        if cached_vector:
            return np.frombuffer(cached_vector, dtype=np.float32)
        
        session = SessionLocal()
        
        try:
            # Get player's spell usage history
            magic_events = session.query(MagicEvent).filter(
                MagicEvent.player_id == player_id,
                MagicEvent.event_type == 'spell_cast',
                MagicEvent.created_at > datetime.utcnow() - timedelta(days=30)  # Last 30 days
            ).all()
            
            if not magic_events:
                # Return neutral preference vector for new players
                return np.zeros(self.dimension, dtype=np.float32)
            
            # Aggregate spell vectors weighted by usage frequency and success
            spell_vectors = []
            weights = []
            
            for event in magic_events:
                if event.spell_id:
                    spell_template = session.query(SpellTemplate).filter_by(id=event.spell_id).first()
                    if spell_template and spell_template.feature_vector:
                        spell_vector = np.array(spell_template.feature_vector)
                        spell_vectors.append(spell_vector)
                        
                        # Weight by success rate and recency
                        success_weight = event.success_rate or 0.5
                        recency_weight = 1.0 / (1 + (datetime.utcnow() - event.created_at).days)
                        weights.append(success_weight * recency_weight)
            
            if not spell_vectors:
                return np.zeros(self.dimension, dtype=np.float32)
            
            # Calculate weighted average
            spell_vectors = np.array(spell_vectors)
            weights = np.array(weights)
            weights = weights / weights.sum()  # Normalize
            
            preference_vector = np.average(spell_vectors, axis=0, weights=weights)
            preference_vector = preference_vector.astype(np.float32)
            
            # Cache the result for 1 hour
            self.redis_client.setex(cache_key, 3600, preference_vector.tobytes())
            
            return preference_vector
            
        finally:
            session.close()
    
    def add_spell_to_index(self, spell_id: str, spell_data: Dict[str, Any]):
        """Add a spell to the vector index"""
        
        vector = self.generate_spell_vector(spell_data)
        
        # Store in database
        session = SessionLocal()
        try:
            spell_template = session.query(SpellTemplate).filter_by(id=spell_id).first()
            if spell_template:
                spell_template.feature_vector = vector.tolist()
                session.commit()
        finally:
            session.close()
        
        # Add to FAISS index
        self.spell_index.add(vector.reshape(1, -1))
        
        # Cache the vector
        self.vector_cache[spell_id] = vector
    
    def find_similar_spells(self, spell_id: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Find spells similar to the given spell
        Returns list of (spell_id, similarity_score) tuples
        """
        
        # Get the query spell vector
        if spell_id in self.vector_cache:
            query_vector = self.vector_cache[spell_id]
        else:
            session = SessionLocal()
            try:
                spell_template = session.query(SpellTemplate).filter_by(id=spell_id).first()
                if not spell_template or not spell_template.feature_vector:
                    return []
                query_vector = np.array(spell_template.feature_vector, dtype=np.float32)
            finally:
                session.close()
        
        # Search in FAISS index
        similarities, indices = self.spell_index.search(query_vector.reshape(1, -1), top_k + 1)
        
        # Get spell IDs for the results (excluding the query spell itself)
        session = SessionLocal()
        try:
            all_spells = session.query(SpellTemplate).filter(
                SpellTemplate.feature_vector.isnot(None)
            ).all()
            
            results = []
            for i, similarity in zip(indices[0], similarities[0]):
                if i < len(all_spells) and all_spells[i].id != spell_id:
                    results.append((all_spells[i].id, float(similarity)))
            
            return results[:top_k]
            
        finally:
            session.close()
    
    def recommend_spells_for_player(self, player_id: str, top_k: int = 10, 
                                   filter_known: bool = True) -> List[Tuple[str, float]]:
        """
        Recommend spells for a player based on their preferences and mastery
        """
        
        player_vector = self.generate_player_preference_vector(player_id)
        
        session = SessionLocal()
        try:
            # Get player state for filtering
            player_state = session.query(PlayerMagicState).filter_by(player_id=player_id).first()
            if not player_state:
                return []
            
            # Get all available spells
            spells_query = session.query(SpellTemplate).filter(
                SpellTemplate.feature_vector.isnot(None)
            )
            
            # Filter by mastery level if needed
            if filter_known:
                # Get spells the player has used recently
                recent_spells = session.query(MagicEvent.spell_id).filter(
                    MagicEvent.player_id == player_id,
                    MagicEvent.event_type == 'spell_cast',
                    MagicEvent.created_at > datetime.utcnow() - timedelta(days=7)
                ).distinct().subquery()
                
                spells_query = spells_query.filter(
                    ~SpellTemplate.id.in_(recent_spells)
                )
            
            spells = spells_query.all()
            
            # Calculate similarities
            recommendations = []
            for spell in spells:
                spell_vector = np.array(spell.feature_vector, dtype=np.float32)
                similarity = cosine_similarity([player_vector], [spell_vector])[0][0]
                
                # Adjust similarity based on player's mastery and spell requirements
                mastery_adjustment = self._calculate_mastery_adjustment(spell, player_state)
                adjusted_similarity = similarity * mastery_adjustment
                
                recommendations.append((spell.id, float(adjusted_similarity)))
            
            # Sort by similarity and return top k
            recommendations.sort(key=lambda x: x[1], reverse=True)
            return recommendations[:top_k]
            
        finally:
            session.close()
    
    def _calculate_mastery_adjustment(self, spell: SpellTemplate, player_state: PlayerMagicState) -> float:
        """Calculate mastery-based adjustment for spell recommendations"""
        
        # Get player's relevant mastery level
        if spell.magic_type == 'arcane':
            mastery_level = player_state.arcane_mastery
        elif spell.magic_type == 'mana':
            mastery_level = player_state.mana_infusion
        else:
            mastery_level = player_state.spiritual_utility
        
        # Penalty for spells too advanced
        if spell.min_mastery_level > mastery_level:
            return 0.1  # Heavy penalty for inaccessible spells
        
        # Slight penalty for spells too simple
        if spell.min_mastery_level < mastery_level - 5:
            return 0.7
        
        # Bonus for spells at appropriate level
        return 1.0
    
    def find_optimal_spell_combinations(self, available_spells: List[str], 
                                      goal_effects: List[str], max_combo_size: int = 3) -> List[Dict]:
        """
        Find optimal spell combinations for achieving specific effects
        """
        
        session = SessionLocal()
        
        try:
            spell_templates = session.query(SpellTemplate).filter(
                SpellTemplate.id.in_(available_spells)
            ).all()
            
            # Convert to vectors
            spell_vectors = {}
            for spell in spell_templates:
                if spell.feature_vector:
                    spell_vectors[spell.id] = np.array(spell.feature_vector)
            
            # Create goal vector based on desired effects
            goal_vector = self._create_goal_vector(goal_effects)
            
            # Find best combinations
            best_combinations = []
            
            # Single spells
            for spell_id, vector in spell_vectors.items():
                similarity = cosine_similarity([goal_vector], [vector])[0][0]
                best_combinations.append({
                    'spells': [spell_id],
                    'similarity': float(similarity),
                    'estimated_mana_cost': self._estimate_combo_mana_cost([spell_id], spell_templates)
                })
            
            # Spell pairs
            if max_combo_size >= 2:
                spell_ids = list(spell_vectors.keys())
                for i in range(len(spell_ids)):
                    for j in range(i + 1, len(spell_ids)):
                        combo_vector = (spell_vectors[spell_ids[i]] + spell_vectors[spell_ids[j]]) / 2
                        similarity = cosine_similarity([goal_vector], [combo_vector])[0][0]
                        best_combinations.append({
                            'spells': [spell_ids[i], spell_ids[j]],
                            'similarity': float(similarity),
                            'estimated_mana_cost': self._estimate_combo_mana_cost([spell_ids[i], spell_ids[j]], spell_templates)
                        })
            
            # Sort by similarity and return top combinations
            best_combinations.sort(key=lambda x: x['similarity'], reverse=True)
            return best_combinations[:10]
            
        finally:
            session.close()
    
    def _create_goal_vector(self, goal_effects: List[str]) -> np.ndarray:
        """Create a vector representing desired magical effects"""
        
        # This is a simplified version - you'd want to expand this based on your effect system
        effect_mapping = {
            'damage': [1, 0, 0, 0, 0],
            'heal': [0, 1, 0, 0, 0],
            'buff': [0, 0, 1, 0, 0],
            'debuff': [0, 0, 0, 1, 0],
            'utility': [0, 0, 0, 0, 1]
        }
        
        goal_vector = np.zeros(self.dimension, dtype=np.float32)
        
        # Set effect preferences
        for i, effect in enumerate(goal_effects):
            if effect in effect_mapping and i < len(effect_mapping):
                effect_vector = effect_mapping[effect]
                goal_vector[i*5:(i+1)*5] = effect_vector
        
        return goal_vector
    
    def _estimate_combo_mana_cost(self, spell_ids: List[str], spell_templates: List) -> float:
        """Estimate total mana cost for a spell combination"""
        
        total_cost = 0.0
        spell_dict = {spell.id: spell for spell in spell_templates}
        
        for spell_id in spell_ids:
            if spell_id in spell_dict:
                total_cost += spell_dict[spell_id].mana_cost
        
        # Add combination penalty (spells are less efficient when combined)
        if len(spell_ids) > 1:
            total_cost *= 1.2
        
        return total_cost
    
    def update_spell_vectors_from_usage(self):
        """
        Update spell vectors based on actual usage patterns and success rates
        Machine learning approach to improve recommendations over time
        """
        
        session = SessionLocal()
        
        try:
            # Get all spells with usage data
            spells_with_usage = session.query(SpellTemplate).filter(
                SpellTemplate.usage_count > 10  # Only spells with sufficient data
            ).all()
            
            for spell in spells_with_usage:
                # Get recent usage statistics
                recent_events = session.query(MagicEvent).filter(
                    MagicEvent.spell_id == spell.id,
                    MagicEvent.created_at > datetime.utcnow() - timedelta(days=30)
                ).all()
                
                if recent_events:
                    # Calculate performance metrics
                    avg_success = np.mean([event.success_rate or 0.5 for event in recent_events])
                    avg_mana_efficiency = np.mean([
                        (event.success_rate or 0.5) / (event.mana_cost or 1)
                        for event in recent_events
                    ])
                    
                    # Adjust spell vector based on performance
                    if spell.feature_vector:
                        current_vector = np.array(spell.feature_vector)
                        
                        # Boost or penalize based on performance
                        performance_factor = (avg_success * avg_mana_efficiency) / 0.5  # Normalize around 0.5
                        adjusted_vector = current_vector * performance_factor
                        
                        # Update in database
                        spell.feature_vector = adjusted_vector.tolist()
            
            session.commit()
            
        finally:
            session.close()
    
    def rebuild_indices(self):
        """Rebuild FAISS indices from database"""
        
        session = SessionLocal()
        
        try:
            # Clear current indices
            self.spell_index.reset()
            self.vector_cache.clear()
            
            # Load all spell vectors
            spells = session.query(SpellTemplate).filter(
                SpellTemplate.feature_vector.isnot(None)
            ).all()
            
            if spells:
                vectors = np.array([spell.feature_vector for spell in spells], dtype=np.float32)
                self.spell_index.add(vectors)
                
                # Update cache
                for spell in spells:
                    self.vector_cache[spell.id] = np.array(spell.feature_vector, dtype=np.float32)
            
            print(f"Rebuilt indices with {len(spells)} spells")
            
        finally:
            session.close()

# Integration functions for your existing magic system
def initialize_spell_vectors():
    """Initialize vectors for all existing spells"""
    
    vector_db = MagicVectorDatabase()
    session = SessionLocal()
    
    try:
        spells = session.query(SpellTemplate).all()
        
        for spell in spells:
            spell_data = {
                'mana_cost': spell.mana_cost,
                'tier': spell.tier,
                'magic_type': spell.magic_type,
                'effects': spell.effects or {},
                'components': spell.components or [],
                # Add more fields as needed
            }
            
            vector_db.add_spell_to_index(spell.id, spell_data)
        
        print(f"Initialized vectors for {len(spells)} spells")
        
    finally:
        session.close()

def get_spell_recommendations(player_id: str, context: Dict[str, Any] = None) -> List[Dict]:
    """Get spell recommendations for a player with context"""
    
    vector_db = MagicVectorDatabase()
    recommendations = vector_db.recommend_spells_for_player(player_id, top_k=10)
    
    # Enrich with spell details
    session = SessionLocal()
    try:
        enriched_recommendations = []
        for spell_id, similarity in recommendations:
            spell = session.query(SpellTemplate).filter_by(id=spell_id).first()
            if spell:
                enriched_recommendations.append({
                    'spell_id': spell_id,
                    'name': spell.name,
                    'similarity_score': similarity,
                    'mana_cost': spell.mana_cost,
                    'tier': spell.tier,
                    'magic_type': spell.magic_type,
                    'success_rate': spell.avg_success_rate
                })
        
        return enriched_recommendations
        
    finally:
        session.close()

def find_similar_spells_for_learning(spell_id: str, player_mastery: Dict[str, int]) -> List[Dict]:
    """Find similar spells that a player could learn next"""
    
    vector_db = MagicVectorDatabase()
    similar_spells = vector_db.find_similar_spells(spell_id, top_k=5)
    
    # Filter by player's mastery level
    session = SessionLocal()
    try:
        learning_candidates = []
        for similar_spell_id, similarity in similar_spells:
            spell = session.query(SpellTemplate).filter_by(id=similar_spell_id).first()
            if spell:
                required_mastery = player_mastery.get(spell.magic_type, 0)
                if spell.min_mastery_level <= required_mastery + 2:  # Slightly above current level
                    learning_candidates.append({
                        'spell_id': similar_spell_id,
                        'name': spell.name,
                        'similarity': similarity,
                        'mastery_requirement': spell.min_mastery_level,
                        'current_mastery': required_mastery
                    })
        
        return learning_candidates
        
    finally:
        session.close()
