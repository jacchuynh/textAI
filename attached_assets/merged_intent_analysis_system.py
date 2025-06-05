"""
Advanced Intent Analysis System for AI-Driven RPG
Combines structured knowledge with layered analysis for deep player understanding
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Union
from enum import Enum
import numpy as np
import json
import logging
from datetime import datetime

# Import necessary libraries
import spacy
from spacy.matcher import Matcher
from langchain.chains.router import RouterChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import BaseLLM
from sentence_transformers import SentenceTransformer

# Core Intent Models
class IntentType(Enum):
    GOAL = "goal"  # What player wants to achieve
    APPROACH = "approach"  # How they want to do it
    VALUE = "value"  # What principles guide them
    CONSTRAINT = "constraint"  # What they won't do
    RELATIONSHIP = "relationship"  # Social priorities
    TIMELINE = "timeline"  # When they want results
    EMOTIONAL_STATE = "emotional_state"  # How they feel
    HESITATION = "hesitation"  # Uncertainty
    CONTRADICTION = "contradiction"  # Conflicts with past statements
    SUBCONSCIOUS = "subconscious"  # Implied but not stated

@dataclass
class Intent:
    """Comprehensive player intention model"""
    # Core properties
    category: str  # Main intent category
    subcategory: str  # Specific intent type
    confidence: float  # 0.0-1.0
    text_span: str  # Original text that generated this intent
    
    # Extended properties
    domains_involved: List[str] = field(default_factory=list)  # Which domains this affects
    timeline: str = "immediate"  # "immediate", "short_term", "long_term"
    priority: int = 3  # 1-5 (5 = highest)
    emotional_weight: float = 0.5  # Emotional intensity
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    context_tags: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    world_evaluation: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntentConflict:
    """Represents conflicting intentions"""
    intent_a: Intent
    intent_b: Intent
    conflict_type: str  # "direct_opposition", "resource_competition", "value_conflict"
    severity: float  # 0.0-1.0
    resolution_suggestions: List[str]

@dataclass
class IntentAnalysisResult:
    """Complete analysis of player input"""
    primary_intents: List[Intent]
    secondary_intents: List[Intent]
    conflicts: List[IntentConflict]
    overall_confidence: float
    analysis_confidence: float
    paralysis_detected: bool = False
    paralysis_severity: str = "none"  # "none", "mild", "moderate", "severe"
    context_coherence: float = 1.0
    recommended_clarifications: List[str] = field(default_factory=list)
    dominant_intent: Optional[Intent] = None
    arbitration_result: Dict[str, Any] = field(default_factory=dict)

# Layer 1: NLP Intent Extraction
class NLPIntentExtractor:
    """Advanced NLP extraction using spaCy with custom patterns"""
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")
        self.setup_nlp_pipeline()
        
    def setup_nlp_pipeline(self):
        """Initialize spaCy with custom rules for RPG intent detection"""
        # Custom entity ruler for RPG-specific terms
        ruler = self.nlp.add_pipe("entity_ruler", before="ner")
        
        # RPG-specific patterns
        patterns = [
            # Goals
            {"label": "COMBAT_GOAL", "pattern": [{"LOWER": {"IN": ["master", "become", "learn"]}}, 
             {"LOWER": {"IN": ["sword", "combat", "fighting", "warrior", "battle"]}}]},
            {"label": "SOCIAL_GOAL", "pattern": [{"LOWER": {"IN": ["diplomat", "negotiator", "leader", "influence"]}}]},
            {"label": "MAGIC_GOAL", "pattern": [{"LOWER": {"IN": ["mage", "wizard", "magic", "arcane", "spells"]}}]},
            
            # Approaches  
            {"label": "HONORABLE_APPROACH", "pattern": [{"LOWER": {"IN": ["honor", "honorable", "noble", "righteous"]}}]},
            {"label": "PRAGMATIC_APPROACH", "pattern": [{"LOWER": {"IN": ["practical", "efficient", "whatever", "works"]}}]},
            {"label": "SNEAKY_APPROACH", "pattern": [{"LOWER": {"IN": ["stealth", "sneaky", "shadows", "quiet"]}}]},
            
            # Values
            {"label": "PROTECTION_VALUE", "pattern": [{"LOWER": {"IN": ["protect", "defend", "save", "help"]}}]},
            {"label": "POWER_VALUE", "pattern": [{"LOWER": {"IN": ["power", "strength", "dominate", "control"]}}]},
            {"label": "KNOWLEDGE_VALUE", "pattern": [{"LOWER": {"IN": ["learn", "understand", "discover", "study"]}}]},
            
            # Constraints
            {"label": "MORAL_CONSTRAINT", "pattern": [{"LOWER": {"IN": ["never", "won't", "refuse"]}}, 
                                                     {"LOWER": {"IN": ["kill", "harm", "innocent"]}}]},
            {"label": "INDEPENDENCE_CONSTRAINT", "pattern": [{"LOWER": {"IN": ["independent", "alone", "solo"]}}]},
            
            # Emotional States
            {"label": "CONFLICTED_EMOTION", "pattern": [{"LOWER": {"IN": ["torn", "conflicted", "unsure", "confused"]}}]},
            {"label": "CONFIDENT_EMOTION", "pattern": [{"LOWER": {"IN": ["certain", "sure", "confident", "resolved"]}}]},
            
            # Hesitations
            {"label": "HESITATION", "pattern": [{"LOWER": {"IN": ["maybe", "perhaps", "might", "unsure", "confused"]}}]}
        ]
        
        ruler.add_patterns(patterns)
        
        # Matcher for complex patterns
        self.matcher = Matcher(self.nlp.vocab)
        
        # Intent patterns
        goal_patterns = [
            [{"LEMMA": {"IN": ["want", "desire", "hope", "plan", "intend"]}},
             {"POS": "PART", "OP": "?"},  # "to" 
             {"POS": "VERB"}],
            [{"TEXT": {"IN": ["I'll", "I", "My"]}},
             {"LEMMA": {"IN": ["become", "learn", "master", "build", "create"]}}]
        ]
        self.matcher.add("GOAL", goal_patterns)
        
        # Hesitation Patterns
        hesitation_patterns = [
            [{"LEMMA": {"IN": ["unsure", "uncertain", "confused", "torn"]}}],
            [{"TEXT": {"IN": ["maybe", "perhaps", "might", "could"]}},
             {"POS": "PRON", "OP": "?"},
             {"POS": "VERB"}],
            [{"TEXT": {"IN": ["I", "i"]}},
             {"LEMMA": {"IN": ["don't", "can't", "won't"]}},
             {"LEMMA": "know"}]
        ]
        self.matcher.add("HESITATION", hesitation_patterns)
        
        # Value Statement Patterns
        value_patterns = [
            [{"TEXT": {"IN": ["I", "i"]}},
             {"LEMMA": {"IN": ["believe", "think", "feel"]}},
             {"LEMMA": {"IN": ["in", "that"]}, "OP": "?"}],
            [{"LEMMA": {"IN": ["important", "valuable", "sacred", "wrong", "right"]}}]
        ]
        self.matcher.add("VALUE", value_patterns)
        
        # Intent conflict patterns
        conflict_patterns = [
            # Direct oppositions
            ("HONOR_VS_EFFICIENCY", [
                [{"LOWER": "honor"}, {"IS_ALPHA": True, "OP": "*"}, {"LOWER": {"IN": ["efficient", "practical", "quick"]}}]
            ]),
            ("HELP_VS_POWER", [
                [{"LOWER": {"IN": ["help", "protect"]}}, {"IS_ALPHA": True, "OP": "*"}, {"LOWER": {"IN": ["power", "dominate"]}}]
            ])
        ]
        
        for name, patterns in conflict_patterns:
            self.matcher.add(name, patterns)
            
    def analyze(self, text: str, context: Dict) -> List[Intent]:
        """Extract intents using spaCy NLP and pattern matching"""
        doc = self.nlp(text)
        intents = []
        
        # Extract from named entities
        for ent in doc.ents:
            if ent.label_ in ["COMBAT_GOAL", "SOCIAL_GOAL", "MAGIC_GOAL"]:
                intents.append(Intent(
                    category="GOAL",
                    subcategory=ent.label_.lower(),
                    confidence=0.8,
                    text_span=ent.text,
                    domains_involved=self._map_to_domains(ent.label_),
                    timeline="long_term",
                    priority=3,
                    emotional_weight=self._assess_emotional_weight(doc)
                ))
            elif ent.label_ in ["HONORABLE_APPROACH", "PRAGMATIC_APPROACH", "SNEAKY_APPROACH"]:
                intents.append(Intent(
                    category="APPROACH",
                    subcategory=ent.label_.lower(),
                    confidence=0.75,
                    text_span=ent.text,
                    domains_involved=self._map_to_domains(ent.label_),
                    timeline="immediate",
                    priority=4
                ))
            elif ent.label_ in ["PROTECTION_VALUE", "POWER_VALUE", "KNOWLEDGE_VALUE"]:
                intents.append(Intent(
                    category="VALUE",
                    subcategory=ent.label_.lower(),
                    confidence=0.85,
                    text_span=ent.text,
                    domains_involved=self._map_to_domains(ent.label_),
                    timeline="long_term",
                    priority=2
                ))
            elif ent.label_ in ["CONFLICTED_EMOTION", "CONFIDENT_EMOTION"]:
                intents.append(Intent(
                    category="EMOTIONAL_STATE",
                    subcategory=ent.label_.lower(),
                    confidence=0.9,
                    text_span=ent.text,
                    domains_involved=["MIND", "SPIRIT"],
                    timeline="immediate",
                    priority=5,
                    emotional_weight=0.8
                ))
        
        # Extract from matcher patterns
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            label = self.nlp.vocab.strings[match_id]
            span = doc[start:end]
            
            if label in ["GOAL", "VALUE", "HESITATION"]:
                intents.append(Intent(
                    category=label,
                    subcategory=self._infer_subcategory(label, span.text),
                    confidence=self._calculate_confidence(span.text),
                    text_span=span.text,
                    domains_involved=self._extract_domains(span.text),
                    emotional_weight=self._assess_emotional_weight(doc),
                    context_tags=self._extract_context_tags(span.text)
                ))
            elif "VS" in label:  # Conflict patterns
                intents.append(Intent(
                    category="CONTRADICTION",
                    subcategory=label.lower(),
                    confidence=0.85,
                    text_span=span.text,
                    domains_involved=[],
                    timeline="immediate",
                    priority=5  # Conflicts are high priority
                ))
                
        return intents
    
    def _map_to_domains(self, entity_label: str) -> List[str]:
        """Map NLP entities to game domains"""
        mapping = {
            "COMBAT_GOAL": ["BODY", "AWARENESS"],
            "SOCIAL_GOAL": ["SOCIAL", "AUTHORITY"],
            "MAGIC_GOAL": ["MIND", "SPIRIT"],
            "HONORABLE_APPROACH": ["SPIRIT", "SOCIAL"],
            "PRAGMATIC_APPROACH": ["MIND", "CRAFT"],
            "SNEAKY_APPROACH": ["AWARENESS", "BODY"],
            "PROTECTION_VALUE": ["SPIRIT", "BODY"],
            "POWER_VALUE": ["AUTHORITY", "MIND"],
            "KNOWLEDGE_VALUE": ["MIND", "SPIRIT"]
        }
        return mapping.get(entity_label, [])
    
    def _infer_subcategory(self, category: str, text: str) -> str:
        """Infer subcategory from text content"""
        text_lower = text.lower()
        
        if category == "GOAL":
            if any(word in text_lower for word in ["combat", "fight", "sword", "warrior"]):
                return "combat_mastery"
            elif any(word in text_lower for word in ["talk", "negotiate", "diplomat", "leader"]):
                return "diplomatic_influence"
            elif any(word in text_lower for word in ["magic", "spell", "arcane", "wizard"]):
                return "magical_mastery"
            return "general_goal"
            
        elif category == "VALUE":
            if any(word in text_lower for word in ["protect", "save", "help"]):
                return "protection"
            elif any(word in text_lower for word in ["power", "strength", "control"]):
                return "power"
            elif any(word in text_lower for word in ["knowledge", "learn", "understand"]):
                return "knowledge"
            return "general_value"
            
        elif category == "HESITATION":
            if any(word in text_lower for word in ["conflicted", "torn"]):
                return "value_conflict"
            elif any(word in text_lower for word in ["unsure", "confused"]):
                return "uncertainty"
            return "general_hesitation"
            
        return "general"
    
    def _calculate_confidence(self, text: str) -> float:
        """Analyze linguistic markers for confidence"""
        confidence_modifiers = {
            'definitely': 0.9, 'absolutely': 0.9, 'certainly': 0.9,
            'probably': 0.7, 'likely': 0.7,
            'maybe': 0.5, 'perhaps': 0.5, 'might': 0.5,
            'unsure': 0.3, 'confused': 0.3, 'torn': 0.3,
            'paralyzed': 0.1, 'lost': 0.1, 'overwhelmed': 0.1
        }
        
        base_confidence = 0.6
        text_lower = text.lower()
        
        for word, value in confidence_modifiers.items():
            if word in text_lower:
                base_confidence = value
                break
                
        return base_confidence
    
    def _extract_domains(self, text: str) -> List[str]:
        """Map text to relevant domains"""
        domain_keywords = {
            'BODY': ['fight', 'train', 'physical', 'strength', 'health', 'combat'],
            'MIND': ['learn', 'study', 'think', 'analyze', 'knowledge', 'magic'],
            'SPIRIT': ['believe', 'faith', 'courage', 'willpower', 'divine'],
            'SOCIAL': ['persuade', 'negotiate', 'friends', 'reputation', 'influence'],
            'CRAFT': ['make', 'build', 'create', 'forge', 'craft', 'art'],
            'AUTHORITY': ['lead', 'command', 'rule', 'authority', 'control'],
            'AWARENESS': ['notice', 'perceive', 'observe', 'alert', 'timing']
        }
        
        involved_domains = []
        text_lower = text.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                involved_domains.append(domain)
                
        return involved_domains or ['GENERAL']
    
    def _assess_emotional_weight(self, doc) -> float:
        """Determine emotional intensity of the intent"""
        emotion_markers = {
            'passionate': 0.9, 'desperate': 0.9, 'furious': 0.9,
            'eager': 0.7, 'excited': 0.7, 'angry': 0.7,
            'interested': 0.5, 'curious': 0.5,
            'reluctant': 0.3, 'hesitant': 0.3,
            'indifferent': 0.1, 'bored': 0.1
        }
        
        for token in doc:
            if token.lemma_.lower() in emotion_markers:
                return emotion_markers[token.lemma_.lower()]
                
        return 0.4  # Default moderate emotional weight
    
    def _extract_context_tags(self, text: str) -> List[str]:
        """Extract contextual tags from the text"""
        text_lower = text.lower()
        tags = []
        
        # Time-based tags
        time_words = ['now', 'later', 'soon', 'eventually', 'never', 'always']
        for word in time_words:
            if word in text_lower:
                tags.append(f"temporal_{word}")
                
        # Conditional tags  
        conditional_words = ['if', 'when', 'unless', 'provided', 'assuming']
        for word in conditional_words:
            if word in text_lower:
                tags.append("conditional")
                
        return tags

# Layer 2: Semantic Vector Analysis
class SemanticVectorAnalyzer:
    """Advanced semantic analysis using embeddings"""
    
    def __init__(self, embedding_model=None):
        # Support both OpenAI embeddings or SentenceTransformers
        if isinstance(embedding_model, str):
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_type = "sentence_transformer"
        else:
            self.embedding_model = embedding_model or OpenAIEmbeddings()
            self.embedding_type = "openai"
            
        self.intent_vectorstore = None
        self.setup_intent_knowledge_base()
    
    def setup_intent_knowledge_base(self):
        """Create vector store of known intent patterns"""
        intent_examples = [
            # Combat intentions
            "I want to become a master swordsman through honorable duels",
            "I need to learn fighting quickly, whatever it takes", 
            "I want to protect people using martial skills",
            
            # Social intentions  
            "I want to become a respected diplomat",
            "I need to build a network of informants",
            "I want to lead people through inspiration",
            
            # Magic intentions
            "I want to master elemental magic through study",
            "I need magical power to defeat my enemies",
            "I want to use magic to help others",
            
            # Conflicting intentions
            "I want to be honorable but also effective",
            "I need power but don't want to hurt innocents",
            "I want to help everyone while staying independent"
        ]
        
        # Create metadata
        metadatas = []
        for ex in intent_examples:
            category = self._categorize_example(ex)
            metadatas.append({"category": category})
        
        # Build vector store for semantic similarity
        if self.embedding_type == "openai":
            self.intent_vectorstore = FAISS.from_texts(
                intent_examples, 
                self.embedding_model,
                metadatas=metadatas
            )
        else:
            # For sentence transformers, would need to implement direct FAISS integration
            # Placeholder for implementation
            pass
    
    def _categorize_example(self, example: str) -> str:
        """Categorize intent examples for metadata"""
        example_lower = example.lower()
        if any(word in example_lower for word in ["sword", "combat", "fight"]):
            return "combat"
        elif any(word in example_lower for word in ["diplomat", "social", "leader"]):
            return "social"  
        elif any(word in example_lower for word in ["magic", "spell", "arcane"]):
            return "magic"
        else:
            return "general"
    
    def analyze(self, text: str, context: Dict) -> List[Intent]:
        """Use embeddings to find semantically similar intent patterns"""
        if not self.intent_vectorstore:
            return []
            
        # Find most similar examples in knowledge base
        similar_docs = self.intent_vectorstore.similarity_search_with_score(
            text, k=5
        )
        
        intents = []
        for doc, score in similar_docs:
            # Converting FAISS distance to confidence (lower distance = higher confidence)
            similarity_confidence = max(0.1, min(0.9, 1.0 - score))
            
            if similarity_confidence > 0.5:  # Only high similarity matches
                intents.append(Intent(
                    category="GOAL",  # Inferred from similarity
                    subcategory=doc.metadata.get("category", "unknown"),
                    confidence=similarity_confidence,
                    text_span=text,  # Full input for semantic matches
                    domains_involved=self._infer_domains_from_similarity(doc.page_content),
                    timeline="medium_term",
                    priority=2
                ))
        
        return intents
    
    def _infer_domains_from_similarity(self, similar_text: str) -> List[str]:
        """Infer domains from similar intent examples"""
        domains = []
        similar_lower = similar_text.lower()
        
        domain_keywords = {
            'BODY': ['combat', 'sword', 'fight', 'physical'],
            'MIND': ['magic', 'study', 'learn'],
            'SOCIAL': ['diplomat', 'leader', 'network', 'informants'],
            'SPIRIT': ['honor', 'protect', 'help']
        }
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in similar_lower for keyword in keywords):
                domains.append(domain)
                
        return domains or ["GENERAL"]

# Layer 3: Memory & Contradiction Analysis
class MemoryAnalyzer:
    """Memory-based contradiction detection using RAG"""
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.conflict_indicators = [
            ('want', 'refuse'), ('love', 'hate'), ('trust', 'distrust'),
            ('help', 'harm'), ('protect', 'attack'), ('friend', 'enemy'),
            ('honor', 'pragmatic'), ('stay', 'leave')
        ]
    
    def analyze(self, text: str, intents: List[Intent], context: Dict) -> List[Intent]:
        """Find contradictions with past statements"""
        if not self.vector_db or not text:
            return []
            
        # Get related memories
        memories = self.vector_db.similarity_search(
            text, k=10, threshold=0.7
        )
        
        contradiction_intents = []
        
        for memory in memories:
            conflict_score = self._detect_conflict(text, memory.page_content)
            
            if conflict_score > 0.5:  # Significant conflict detected
                contradiction_intents.append(Intent(
                    category="CONTRADICTION",
                    subcategory="memory_conflict",
                    confidence=conflict_score,
                    text_span=f"Conflicts with past statement: '{memory.page_content}'",
                    domains_involved=self._extract_domains_from_memory(memory),
                    timeline="immediate",
                    priority=5,
                    emotional_weight=0.8,
                    context_tags=['memory_conflict'],
                    conflicts_with=[str(memory.metadata.get('id', 'unknown'))]
                ))
                
        return contradiction_intents
    
    def _detect_conflict(self, current_text: str, past_text: str) -> float:
        """Detect semantic conflicts between statements"""
        current_lower = current_text.lower()
        past_lower = past_text.lower()
        
        # Check for opposite pairs
        for pos, neg in self.conflict_indicators:
            if ((pos in current_lower and neg in past_lower) or 
                (neg in current_lower and pos in past_lower)):
                return 0.8
                
        return 0.0
    
    def _extract_domains_from_memory(self, memory) -> List[str]:
        """Extract domains from memory metadata"""
        if hasattr(memory, 'metadata') and 'domains' in memory.metadata:
            return memory.metadata['domains']
        return ["MIND"]  # Default domain for memory conflicts
        
    def store_intent_in_memory(self, text: str, intents: List[Intent], context: Dict):
        """Store current intent in memory for future reference"""
        if not self.vector_db:
            return
            
        # Prepare metadata
        domains = []
        for intent in intents:
            domains.extend(intent.domains_involved)
        
        metadata = {
            'timestamp': datetime.now().timestamp(),
            'domains': list(set(domains)),
            'context': context.get('situation', 'unknown'),
            'id': context.get('memory_id', str(hash(text)))
        }
        
        # Add to vector DB
        self.vector_db.add_texts([text], metadatas=[metadata])

# Layer 4: Intent Taxonomy & Knowledge Base
class IntentKnowledgeBase:
    """Structured knowledge about intents and their relationships"""
    
    def __init__(self):
        self.intent_taxonomy = {
            "GOALS": {
                "combat_mastery": {
                    "domains": ["BODY", "AWARENESS"],
                    "conflicting_goals": ["pacifist_path", "scholarly_focus"],
                    "supporting_approaches": ["training_intensive", "challenge_seeking"]
                },
                "diplomatic_influence": {
                    "domains": ["SOCIAL", "MIND"],
                    "conflicting_goals": ["intimidation_path", "hermit_lifestyle"],
                    "supporting_approaches": ["relationship_building", "knowledge_gathering"]
                },
                "magical_mastery": {
                    "domains": ["MIND", "SPIRIT"],
                    "conflicting_goals": ["anti_magic_stance", "pure_physical_focus"],
                    "supporting_approaches": ["scholarly_study", "experimental_practice"]
                }
            },
            "APPROACHES": {
                "honorable": {
                    "supports": ["protection_goals", "leadership_goals"],
                    "conflicts_with": ["efficiency_at_any_cost", "stealth_focus"],
                    "domain_modifiers": {"SPIRIT": 1.2, "AUTHORITY": 1.1}
                },
                "pragmatic": {
                    "supports": ["power_goals", "survival_goals"],
                    "conflicts_with": ["honor_bound", "idealistic"],
                    "domain_modifiers": {"MIND": 1.2, "CRAFT": 1.1}
                }
            },
            "VALUES": {
                "protection": {
                    "reinforces": ["combat_for_defense", "healing_arts"],
                    "conflicts_with": ["selfish_power", "destructive_magic"]
                },
                "independence": {
                    "reinforces": ["self_reliant_skills", "solo_capabilities"],
                    "conflicts_with": ["team_leadership", "dependency_relationships"]
                }
            }
        }
        
        self.conflict_patterns = {
            "direct_opposition": [
                (["honor", "noble", "righteous"], ["efficient", "practical", "expedient"]),
                (["help", "protect", "save"], ["power", "dominate", "control"]),
                (["peaceful", "diplomatic"], ["violent", "aggressive", "force"])
            ],
            "resource_competition": [
                (["master", "focus"], ["also", "and", "plus"]),  # Trying to master too many things
                (["intensive", "dedicated"], ["broad", "diverse", "various"])  # Deep vs broad
            ],
            "timeline_conflict": [
                (["immediately", "now", "quickly"], ["careful", "slowly", "eventually"]),
                (["long-term", "eventually"], ["urgent", "pressing", "immediate"])
            ]
        }
    
    def check_taxonomy_conflict(self, intent_a: Intent, intent_b: Intent) -> float:
        """Check if two intents conflict based on taxonomy"""
        # If same category, check for subcategory conflicts
        if intent_a.category == intent_b.category == "GOAL":
            taxonomy_a = self.intent_taxonomy["GOALS"].get(intent_a.subcategory, {})
            taxonomy_b = self.intent_taxonomy["GOALS"].get(intent_b.subcategory, {})
            
            # Direct conflict listed in taxonomy
            if intent_b.subcategory in taxonomy_a.get("conflicting_goals", []):
                return 0.9
            if intent_a.subcategory in taxonomy_b.get("conflicting_goals", []):
                return 0.9
                
        # Approach vs Value conflicts
        if intent_a.category == "APPROACH" and intent_b.category == "VALUE":
            approach_data = self.intent_taxonomy["APPROACHES"].get(intent_a.subcategory, {})
            if intent_b.subcategory in approach_data.get("conflicts_with", []):
                return 0.8
                
        return 0.0
    
    def check_resource_competition(self, intent_a: Intent, intent_b: Intent) -> bool:
        """Check if intents compete for limited resources (time, focus, etc)"""
        # Two different mastery goals might compete for time/focus
        if (intent_a.category == intent_b.category == "GOAL" and 
            intent_a.subcategory != intent_b.subcategory and
            "mastery" in intent_a.subcategory and "mastery" in intent_b.subcategory):
            return True
            
        return False
    
    def generate_resolution_suggestions(self, intent_a: Intent, intent_b: Intent) -> List[str]:
        """Generate suggestions for resolving conflicts"""
        suggestions = []
        
        if intent_a.category == intent_b.category == "GOAL":
            suggestions.append("Consider which goal aligns better with your character's values.")
            suggestions.append("You might be able to pursue one goal now and the other later.")
            suggestions.append("Is there a middle path that honors aspects of both goals?")
            
        elif "APPROACH" in [intent_a.category, intent_b.category] and "VALUE" in [intent_a.category, intent_b.category]:
            suggestions.append("What matters more to your character: the approach or upholding values?")
            suggestions.append("Could you modify your approach while preserving core values?")
            
        return suggestions

# Layer 5: Conflict Detection
class ConflictDetector:
    """Detects conflicts between intents"""
    
    def __init__(self, knowledge_base: IntentKnowledgeBase):
        self.knowledge_base = knowledge_base
    
    def detect_conflicts(self, intents: List[Intent]) -> List[IntentConflict]:
        """Find conflicts between all intents"""
        conflicts = []
        
        # Check each pair of intents
        for i, intent_a in enumerate(intents):
            for j, intent_b in enumerate(intents[i+1:], start=i+1):
                conflict = self._check_pair_conflict(intent_a, intent_b)
                if conflict:
                    conflicts.append(conflict)
                    
        return conflicts
    
    def _check_pair_conflict(self, intent_a: Intent, intent_b: Intent) -> Optional[IntentConflict]:
        """Check if pair of intents conflict"""
        # Check taxonomy conflicts
        taxonomy_conflict = self.knowledge_base.check_taxonomy_conflict(intent_a, intent_b)
        if taxonomy_conflict > 0:
            return IntentConflict(
                intent_a=intent_a,
                intent_b=intent_b,
                conflict_type="direct_opposition",
                severity=taxonomy_conflict,
                resolution_suggestions=self.knowledge_base.generate_resolution_suggestions(intent_a, intent_b)
            )
        
        # Check resource competition
        if self.knowledge_base.check_resource_competition(intent_a, intent_b):
            return IntentConflict(
                intent_a=intent_a,
                intent_b=intent_b,
                conflict_type="resource_competition", 
                severity=0.6,
                resolution_suggestions=[
                    "Focus on one goal first, then pursue the other",
                    "Find ways to train both skills simultaneously",
                    "Consider which is more important for your immediate situation"
                ]
            )
            
        # Check for explicit contradictions
        if "CONTRADICTION" in [intent_a.category, intent_b.category]:
            return IntentConflict(
                intent_a=intent_a,
                intent_b=intent_b,
                conflict_type="explicit_contradiction",
                severity=0.9,
                resolution_suggestions=[
                    "Reflect on what's changed since your previous statement",
                    "Consider which perspective feels more authentic now",
                    "How might your character reconcile these opposing views?"
                ]
            )
            
        # Check for hesitation vs confident statements
        if "HESITATION" in [intent_a.category, intent_b.category]:
            other = intent_b if intent_a.category == "HESITATION" else intent_a
            if other.confidence > 0.7:  # Confident statement vs hesitation
                return IntentConflict(
                    intent_a=intent_a,
                    intent_b=intent_b,
                    conflict_type="confidence_conflict",
                    severity=0.5,
                    resolution_suggestions=[
                        "What's causing your hesitation about this course of action?",
                        "What would help you feel more confident in your decision?"
                    ]
                )
                
        return None

# Layer 6: World State Evaluation
class WorldStateEvaluator:
    """Evaluates intent feasibility against world state"""
    
    def __init__(self, world_state_manager=None):
        self.world_state = world_state_manager
    
    def evaluate_intent_feasibility(self, intent: Intent, context: Dict) -> Dict[str, Any]:
        """Check if intent conflicts with current world state"""
        if not self.world_state:
            return {"feasible": True}  # Default if no world state manager
            
        evaluation = {
            'feasible': True,
            'obstacles': [],
            'hidden_consequences': [],
            'required_resources': [],
            'social_implications': []
        }
        
        # Example evaluations based on context
        if context.get('player_wealth', 100) < 50:
            evaluation['obstacles'].append('Limited funds may restrict options')
            
        if 'combat' in intent.subcategory and context.get('player_injured', False):
            evaluation['feasible'] = False
            evaluation['obstacles'].append('Current injuries limit combat effectiveness')
            
        if 'diplomatic' in intent.subcategory:
            reputation = context.get('reputation', {}).get('diplomatic', 0)
            if reputation < 0:
                evaluation['obstacles'].append('Poor diplomatic reputation will make this challenging')
                
        # Check for social implications
        if intent.category == "GOAL":
            evaluation['social_implications'] = self._predict_reputation_impact(intent, context)
            
        return evaluation
    
    def _predict_reputation_impact(self, intent: Intent, context: Dict) -> List[str]:
        """Predict reputation effects"""
        implications = []
        
        if 'SOCIAL' in intent.domains_involved:
            implications.append('Will affect social standing')
            
        if 'AUTHORITY' in intent.domains_involved:
            implications.append('May impact leadership perception')
            
        # Faction-specific implications
        factions = context.get('active_factions', [])
        for faction in factions:
            if faction.get('values', []) and any(value in intent.text_span.lower() for value in faction['values']):
                implications.append(f"Will strengthen relationship with {faction['name']}")
            if faction.get('dislikes', []) and any(dislike in intent.text_span.lower() for dislike in faction['dislikes']):
                implications.append(f"Will damage relationship with {faction['name']}")
                
        return implications

# Layer 7: Paralysis Detection
class IntentParalysisHandler:
    """Detects and handles player intent paralysis"""
    
    def detect_paralysis(self, intents: List[Intent], conflicts: List[IntentConflict]) -> Tuple[bool, str]:
        """Detect if player is experiencing intent paralysis"""
        # Count hesitations
        hesitation_count = len([i for i in intents if i.category == "HESITATION"])
        
        # Count contradictions
        contradiction_count = len([i for i in intents if i.category == "CONTRADICTION"])
        
        # Count high-severity conflicts
        high_severity_conflicts = len([c for c in conflicts if c.severity > 0.7])
        
        # Calculate confidence
        if not intents:
            avg_confidence = 0
        else:
            avg_confidence = sum(i.confidence for i in intents) / len(intents)
        
        # Decision tree for paralysis detection
        if hesitation_count > 1 and high_severity_conflicts > 0:
            return True, "severe"
        elif contradiction_count > 0 and avg_confidence < 0.4:
            return True, "moderate"
        elif avg_confidence < 0.5 or hesitation_count > 0:
            return True, "mild"
        else:
            return False, "none"
    
    def generate_responses(self, severity: str, intents: List[Intent], conflicts: List[IntentConflict]) -> Dict[str, Any]:
        """Generate appropriate responses based on paralysis severity"""
        if severity == "mild":
            return {
                'response_type': 'clarifying_questions',
                'questions': [
                    "What feels most important to your character right now?",
                    "What would align best with your character's values?",
                    "What approach feels most natural given your character's personality?"
                ]
            }
        elif severity == "moderate":
            return {
                'response_type': 'internal_monologue',
                'monologue': f"Your character feels torn between competing desires... The weight of {len(conflicts)} different impulses creates a moment of internal conflict.",
                'emotional_state': 'conflicted',
                'growth_opportunity': 'wisdom_through_reflection'
            }
        elif severity == "severe":
            interventions = [
                'environmental_pressure',  # External event forces decision
                'time_pressure',          # Deadline approaches
                'ally_intervention',      # Friend offers guidance
                'enemy_action',          # Enemy makes choice for you
                'random_event'           # Fate intervenes
            ]
            
            import random
            chosen_intervention = random.choice(interventions)
            
            return {
                'response_type': 'dramatic_intervention',
                'intervention_type': chosen_intervention,
                'narrative_hook': f"Just as indecision paralyzes you, {chosen_intervention} occurs..."
            }
        else:
            return {'response_type': 'continue_normally'}

# Layer 8: LLM Intent Arbitration
class LLMIntentArbitrator:
    """Uses LLM to handle complex intent scenarios"""
    
    def __init__(self, llm_client=None):
        self.llm = llm_client
    
    def arbitrate(self, intents: List[Intent], conflicts: List[IntentConflict], context: Dict) -> Dict[str, Any]:
        """Use LLM to resolve complex intent conflicts"""
        if not self.llm:
            return self._fallback_arbitration(intents, conflicts)
            
        # Only use LLM for complex cases to save tokens
        if len(conflicts) <= 1 or len(intents) <= 2:
            return self._fallback_arbitration(intents, conflicts)
            
        # Build prompt
        prompt = self._build_arbitration_prompt(intents, conflicts, context)
        
        try:
            # Call LLM
            response = self.llm(prompt)
            return self._parse_arbitration_response(response)
        except Exception as e:
            logging.error(f"LLM arbitration failed: {e}")
            return self._fallback_arbitration(intents, conflicts)
    
    def _build_arbitration_prompt(self, intents: List[Intent], conflicts: List[IntentConflict], context: Dict) -> str:
        """Build prompt for LLM arbitration"""
        prompt = f"""
        Character Context: {context.get('character_summary', 'Unknown character')}
        Current Situation: {context.get('current_situation', 'General situation')}
        
        The character has expressed multiple intents that may conflict:
        
        PRIMARY INTENTS:
        """
        
        for i, intent in enumerate(intents[:3]):  # Limit to top 3
            prompt += f"{i+1}. {intent.text_span} (Confidence: {intent.confidence}, Type: {intent.category})\n"
            
        prompt += "\nCONFLICTS DETECTED:\n"
        for i, conflict in enumerate(conflicts[:3]):  # Limit to top 3
            prompt += f"- Conflict {i+1}: {conflict.intent_a.text_span} vs {conflict.intent_b.text_span}\n"
            
        prompt += """
        
        Please analyze this situation and suggest:
        1. The dominant intent (most aligned with character)
        2. How to resolve the conflict (internal dialogue, compromise, etc.)
        3. Emotional state this creates (confident, torn, paralyzed, etc.)
        4. Suggested player agency options (3-4 choices)
        
        Format your response as JSON with keys: dominant_intent, resolution_method, emotional_state, player_options
        """
        
        return prompt
    
    def _parse_arbitration_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            return json.loads(response)
        except:
            # Fallback parsing if JSON parsing fails
            return {
                'resolution': 'llm_guidance',
                'guidance': response,
                'emotional_state': 'conflicted'
            }
    
    def _fallback_arbitration(self, intents: List[Intent], conflicts: List[IntentConflict]) -> Dict[str, Any]:
        """Simple heuristic-based arbitration as fallback"""
        if not intents:
            return {
                'resolution': 'no_intent_detected',
                'dominant_intent': None,
                'emotional_state': 'neutral',
                'player_options': ["Clarify your intentions"]
            }
            
        # Sort by confidence and priority
        sorted_intents = sorted(intents, key=lambda x: (x.priority, x.confidence), reverse=True)
        dominant = sorted_intents[0]
        
        # Generate basic options
        options = []
        for intent in sorted_intents[:3]:
            if intent.category == "GOAL":
                options.append(f"Focus on {intent.subcategory}")
                
        if not options:
            options = ["Continue with current course", "Reconsider options", "Seek more information"]
            
        return {
            'resolution': 'heuristic',
            'dominant_intent': dominant,
            'emotional_state': 'determined' if dominant.confidence > 0.7 else 'uncertain',
            'player_options': options
        }

# Main Analyzer Class
class AdvancedIntentAnalyzer:
    """Complete intent analysis system combining all layers"""
    
    def __init__(self, config: Dict[str, Any] = None):
        config = config or {}
        
        # Initialize all layers
        self.nlp_extractor = NLPIntentExtractor()
        self.semantic_analyzer = SemanticVectorAnalyzer(config.get('embedding_model'))
        self.memory_analyzer = MemoryAnalyzer(config.get('vector_db'))
        self.knowledge_base = IntentKnowledgeBase()
        self.conflict_detector = ConflictDetector(self.knowledge_base)
        self.world_evaluator = WorldStateEvaluator(config.get('world_state_manager'))
        self.paralysis_handler = IntentParalysisHandler()
        self.llm_arbitrator = LLMIntentArbitrator(config.get('llm_client'))
        
        self.player_profile_manager = PlayerProfileManager()
        
    def analyze_intent(self, player_input: str, context: Dict = None) -> IntentAnalysisResult:
        """Complete analysis pipeline for player input"""
        context = context or {}
        
        # Layer 1: Extract basic intents with NLP
        nlp_intents = self.nlp_extractor.analyze(player_input, context)
        
        # Layer 2: Semantic vector analysis
        semantic_intents = self.semantic_analyzer.analyze(player_input, context)
        
        # Layer 3: Memory-based contradiction analysis
        memory_intents = self.memory_analyzer.analyze(player_input, nlp_intents + semantic_intents, context)
        
        # Combine all detected intents
        all_intents = nlp_intents + semantic_intents + memory_intents
        
        # Layer 4-5: Detect conflicts using knowledge base
        conflicts = self.conflict_detector.detect_conflicts(all_intents)
        
        # Layer 6: Evaluate against world state
        for intent in all_intents:
            intent.world_evaluation = self.world_evaluator.evaluate_intent_feasibility(intent, context)
        
        # Layer 7: Check for paralysis
        paralysis_detected, paralysis_severity = self.paralysis_handler.detect_paralysis(all_intents, conflicts)
        paralysis_response = None
        if paralysis_detected:
            paralysis_response = self.paralysis_handler.generate_responses(
                paralysis_severity, all_intents, conflicts
            )
        
        # Layer 8: Use LLM for complex arbitration
        arbitration_result = None
        dominant_intent = None
        if len(conflicts) > 1 or (all_intents and all_intents[0].confidence < 0.6):
            arbitration_result = self.llm_arbitrator.arbitrate(all_intents, conflicts, context)
            if arbitration_result and 'dominant_intent' in arbitration_result:
                dominant_intent = arbitration_result['dominant_intent']
        elif all_intents:
            # Simple case: select highest confidence intent
            sorted_intents = sorted(all_intents, key=lambda x: (x.priority, x.confidence), reverse=True)
            dominant_intent = sorted_intents[0]
            
        # Calculate confidence metrics
        overall_confidence = self._calculate_confidence(all_intents, conflicts)
        analysis_confidence = self._calculate_analysis_confidence(all_intents, conflicts)
            
        # Store in memory for future reference
        self.memory_analyzer.store_intent_in_memory(player_input, all_intents, context)
        
        # Update player profile with new insights
        self.player_profile_manager.update_profile(all_intents, dominant_intent, conflicts, context)
        
        # Prepare final result
        primary_intents, secondary_intents = self._prioritize_intents(all_intents)
        
        return IntentAnalysisResult(
            primary_intents=primary_intents,
            secondary_intents=secondary_intents,
            conflicts=conflicts,
            overall_confidence=overall_confidence,
            analysis_confidence=analysis_confidence,
            paralysis_detected=paralysis_detected,
            paralysis_severity=paralysis_severity,
            context_coherence=self._assess_context_coherence(player_input, context),
            recommended_clarifications=self._generate_clarifications(conflicts, paralysis_detected, paralysis_response),
            dominant_intent=dominant_intent,
            arbitration_result=arbitration_result or {}
        )
        
    def _prioritize_intents(self, intents: List[Intent]) -> Tuple[List[Intent], List[Intent]]:
        """Split intents into primary and secondary based on priority and confidence"""
        sorted_intents = sorted(intents, key=lambda x: (x.priority, x.confidence), reverse=True)
        
        if len(sorted_intents) <= 3:
            return sorted_intents, []
        
        return sorted_intents[:3], sorted_intents[3:]
        
    def _calculate_confidence(self, intents: List[Intent], conflicts: List[IntentConflict]) -> float:
        """Calculate overall confidence in intent analysis"""
        if not intents:
            return 0.1
        
        # Average confidence of detected intents
        avg_confidence = sum(i.confidence for i in intents) / len(intents)
        
        # Reduce confidence for high conflicts
        conflict_penalty = min(0.4, len(conflicts) * 0.1)
        
        return max(0.1, avg_confidence - conflict_penalty)
        
    def _calculate_analysis_confidence(self, intents: List[Intent], conflicts: List[IntentConflict]) -> float:
        """Calculate confidence in the analysis itself (meta-confidence)"""
        # Base confidence
        base = 0.7
        
        # Adjust based on conflict clarity
        if conflicts and all(c.severity > 0.8 for c in conflicts):
            base += 0.2  # Very clear conflicts
        elif conflicts and any(c.severity < 0.5 for c in conflicts):
            base -= 0.2  # Some ambiguous conflicts
            
        # Adjust based on intent diversity
        categories = set(i.category for i in intents)
        if len(categories) >= 3:
            base += 0.1  # Diverse intent types detected
        
        return max(0.3, min(base, 0.95))
        
    def _assess_context_coherence(self, player_input: str, context: Dict) -> float:
        """Assess how well the input aligns with current context"""
        if not context:
            return 1.0
            
        # This would be more sophisticated in a real system
        return 0.8
        
    def _generate_clarifications(self, conflicts: List[IntentConflict], paralysis_detected: bool, 
                               paralysis_response: Dict[str, Any]) -> List[str]:
        """Generate clarification questions"""
        if paralysis_detected and paralysis_response and 'questions' in paralysis_response:
            return paralysis_response['questions']
            
        clarifications = []
        for conflict in conflicts:
            if conflict.severity > 0.6 and conflict.resolution_suggestions:
                clarifications.extend(conflict.resolution_suggestions[:2])  # Limit to 2 per conflict
                
        return clarifications[:3]  # Limit total to avoid overwhelming

# Player Profile Tracking
class PlayerProfileManager:
    """Tracks player intent patterns over time"""
    
    def __init__(self):
        self.profile = {}
        self.intent_history = []
        
    def update_profile(self, intents: List[Intent], dominant_intent: Optional[Intent], 
                      conflicts: List[IntentConflict], context: Dict):
        """Update player profile with new intent data"""
        # Track declared goals over time
        for intent in intents:
            if intent.category == "GOAL":
                if intent.subcategory not in self.profile:
                    self.profile[intent.subcategory] = {"strength": 0, "consistency": 0}
                self.profile[intent.subcategory]["strength"] += intent.confidence
                
                # Detect consistency
                if self.intent_history:
                    last_intents = self.intent_history[-1]
                    similar_previous = [i for i in last_intents 
                                      if i.category == "GOAL" and i.subcategory == intent.subcategory]
                    if similar_previous:
                        self.profile[intent.subcategory]["consistency"] += 0.1
        
        # Store history for pattern analysis
        self.intent_history.append(intents)
        if len(self.intent_history) > 20:  # Keep recent history
            self.intent_history.pop(0)
            
    def get_consistent_traits(self) -> Dict[str, float]:
        """Get traits that player has consistently demonstrated"""
        return {k: v["consistency"] for k, v in self.profile.items() 
               if v["consistency"] > 0.5}
               
    def calculate_growth_modifiers(self, analysis_result: IntentAnalysisResult) -> Dict[str, float]:
        """Calculate growth point modifiers based on intent alignment"""
        modifiers = {}
        
        for intent in analysis_result.primary_intents:
            for domain in intent.domains_involved:
                current_modifier = modifiers.get(domain, 1.0)
                intent_bonus = intent.confidence * 0.5  # Up to 50% bonus
                modifiers[domain] = current_modifier + intent_bonus
        
        return modifiers
        
    def suggest_opportunities(self, analysis_result: IntentAnalysisResult) -> List[Dict[str, Any]]:
        """Suggest gameplay opportunities based on revealed intentions"""
        opportunities = []
        
        consistent_traits = self.get_consistent_traits()
        
        for trait, strength in consistent_traits.items():
            if "combat" in trait:
                opportunities.append({
                    "type": "quest_suggestion",
                    "description": "A combat trial that tests your growing skills",
                    "relevance": strength
                })
            elif "diplomatic" in trait:
                opportunities.append({
                    "type": "npc_interaction",
                    "description": "A complex negotiation that could boost your reputation",
                    "relevance": strength
                })
                
        # Add opportunities based on current conflicts
        for conflict in analysis_result.conflicts:
            opportunities.append({
                "type": "character_development",
                "description": f"An opportunity to resolve your conflict between {conflict.intent_a.subcategory} and {conflict.intent_b.subcategory}",
                "relevance": conflict.severity
            })
                
        return sorted(opportunities, key=lambda x: x["relevance"], reverse=True)[:3]

# Game Integration Layer
class RPGIntentSystem:
    """Integration layer for RPG game engine"""
    
    def __init__(self, config: Dict = None):
        config = config or {}
        self.analyzer = AdvancedIntentAnalyzer(config)
        self.player_profile = {}
        self.intent_history = []
    
    def process_player_input(self, player_input: str, game_context: Dict = None) -> Dict:
        """Process player input and return actionable analysis"""
        game_context = game_context or {}
        
        # Analyze the input
        analysis = self.analyzer.analyze_intent(player_input, game_context)
        
        # Update player profile
        self._update_player_profile(analysis)
        
        # Generate game response
        response = self._generate_game_response(analysis, game_context)
        
        return {
            "analysis": analysis,
            "response": response,
            "growth_modifiers": self._calculate_growth_modifiers(analysis),
            "opportunity_suggestions": self._suggest_opportunities(analysis)
        }
    
    def _update_player_profile(self, analysis: IntentAnalysisResult):
        """Track player profile over time"""
        # Store history for pattern analysis
        self.intent_history.append(analysis)
        if len(self.intent_history) > 50:  # Keep recent history
            self.intent_history.pop(0)
        
        # Track declared goals
        for intent in analysis.primary_intents:
            if intent.category == "GOAL":
                if intent.subcategory not in self.player_profile:
                    self.player_profile[intent.subcategory] = {"strength": 0, "consistency": 0}
                self.player_profile[intent.subcategory]["strength"] += intent.confidence
    
    def _generate_game_response(self, analysis: IntentAnalysisResult, context: Dict) -> str:
        """Generate appropriate game response based on analysis"""
        if analysis.paralysis_detected:
            return self._handle_intent_paralysis(analysis)
        elif analysis.conflicts:
            return self._acknowledge_conflicts(analysis)
        else:
            return self._confirm_understanding(analysis)
    
    def _handle_intent_paralysis(self, analysis: IntentAnalysisResult) -> str:
        """Handle cases where player has conflicting intentions"""
        clarifications = analysis.recommended_clarifications
        
        response = "I can see you're weighing several important considerations. "
        response += clarifications[0] if clarifications else "What feels most important to you right now?"
        
        return response
    
    def _acknowledge_conflicts(self, analysis: IntentAnalysisResult) -> str:
        """Acknowledge player's conflicting intentions"""
        if analysis.dominant_intent:
            return f"I understand your primary goal is to {analysis.dominant_intent.text_span}, though I sense some conflict in your approach."
        else:
            return "I notice you have some conflicting goals. Which one feels most important right now?"
    
    def _confirm_understanding(self, analysis: IntentAnalysisResult) -> str:
        """Confirm understanding of clear player intent"""
        if not analysis.primary_intents:
            return "I'm not sure I understand your intentions. Could you clarify?"
            
        primary = analysis.primary_intents[0]
        return f"I understand that you want to {primary.text_span}. I'll help you work toward that."
    
    def _calculate_growth_modifiers(self, analysis: IntentAnalysisResult) -> Dict:
        """Calculate growth point modifiers based on intent alignment"""
        modifiers = {}
        
        for intent in analysis.primary_intents:
            for domain in intent.domains_involved:
                current_modifier = modifiers.get(domain, 1.0)
                intent_bonus = intent.confidence * 0.5  # Up to 50% bonus
                modifiers[domain] = current_modifier + intent_bonus
        
        return modifiers
    
    def _suggest_opportunities(self, analysis: IntentAnalysisResult) -> List[Dict]:
        """Suggest gameplay opportunities based on detected intents"""
        opportunities = []
        
        for intent in analysis.primary_intents:
            if intent.category == "GOAL" and intent.subcategory == "combat_mastery":
                opportunities.append({
                    "type": "combat_challenge",
                    "description": "There's a fighting tournament in the nearby town",
                    "alignment": 0.9
                })
            elif intent.category == "GOAL" and intent.subcategory == "diplomatic_influence":
                opportunities.append({
                    "type": "social_opportunity",
                    "description": "A noble is hosting a gathering where you could make connections",
                    "alignment": 0.9
                })
            elif intent.category == "GOAL" and intent.subcategory == "magical_mastery":
                opportunities.append({
                    "type": "magical_discovery",
                    "description": "There are rumors of an ancient arcane library in the mountains",
                    "alignment": 0.9
                })
        
        if analysis.conflicts:
            # Suggest opportunities that could help resolve conflicts
            opportunities.append({
                "type": "conflict_resolution",
                "description": "An old sage who helps adventurers find their true path",
                "alignment": 0.8
            })
        
        return opportunities

# Example usage
if __name__ == "__main__":
    # Configuration for the system
    CONFIG = {
        "embedding_model": "all-MiniLM-L6-v2",  # SentenceTransformer model
        "confidence_threshold": 0.4,
        "paralysis_threshold": 0.7,
        "max_clarifications": 3
    }
    
    # Initialize the system
    intent_system = RPGIntentSystem(CONFIG)
    
    # Example player inputs
    test_inputs = [
        "I want to become a master swordsman but I also don't want to hurt innocent people",
        "I need to learn magic quickly to defeat my enemies",
        "I want to be diplomatic but sometimes force is necessary",
        "I'm trying to build a network of contacts while staying independent"
    ]
    
    for input_text in test_inputs:
        print(f"\nPlayer: {input_text}")
        result = intent_system.process_player_input(input_text)
        print(f"Analysis: {result['response']}")
        if result['analysis'].conflicts:
            print(f"Conflicts detected: {len(result['analysis'].conflicts)}")
        print(f"Growth modifiers: {result['growth_modifiers']}")