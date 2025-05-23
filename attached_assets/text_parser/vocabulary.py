"""
Vocabulary management for the parser engine with monster name support.

This module handles the vocabulary used by the parser, including
verbs, nouns, adjectives, prepositions, and monster names/aliases.
"""
from typing import Dict, List, Set, Optional, Any, Tuple
import json
import os
import re


class VocabularyManager:
    """
    Manages vocabulary for the parser engine.
    
    This class handles loading, accessing, and managing the vocabulary,
    including synonym mapping and word type identification.
    """
    
    def __init__(self, vocab_dir: str = "data/vocabulary"):
        """
        Initialize the vocabulary manager.
        
        Args:
            vocab_dir: Directory containing vocabulary files
        """
        self.vocab_dir = vocab_dir
        self.verbs: Dict[str, str] = {}  # word -> canonical form
        self.nouns: Set[str] = set()
        self.compound_nouns: Dict[str, str] = {}  # "vine weasel" -> "vine weasel" - for multi-word entities
        self.noun_aliases: Dict[str, str] = {}  # "blade" -> "sword" - maps alias to canonical noun
        self.adjectives: Set[str] = set()
        self.prepositions: Set[str] = set()
        self.articles: Set[str] = set()
        self.directions: Set[str] = set()  # Special case for navigation
        
        # Monster data
        self.monster_names: Set[str] = set()  # Set of all monster names (canonical)
        self._monster_vocab_loaded = False
        
        # Load vocabulary
        self._load_vocabulary()
    
    def _load_vocabulary(self) -> None:
        """Load vocabulary from files."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(self.vocab_dir, exist_ok=True)
            
            # Load verbs and their synonyms
            verb_path = os.path.join(self.vocab_dir, "verbs.json")
            if os.path.exists(verb_path):
                with open(verb_path, 'r') as f:
                    verb_data = json.load(f)
                for canonical, synonyms in verb_data.items():
                    # Add canonical form to itself
                    self.verbs[canonical] = canonical
                    # Add all synonyms mapping to canonical form
                    for syn in synonyms:
                        self.verbs[syn] = canonical
            else:
                # Create a default verbs file if it doesn't exist
                self._create_default_verbs_file(verb_path)
            
            # Load nouns
            noun_path = os.path.join(self.vocab_dir, "nouns.txt")
            if os.path.exists(noun_path):
                with open(noun_path, 'r') as f:
                    self.nouns = set(line.strip().lower() for line in f if line.strip())
            else:
                # Create a default nouns file if it doesn't exist
                self._create_default_nouns_file(noun_path)
            
            # Load noun aliases (if exists)
            noun_alias_path = os.path.join(self.vocab_dir, "noun_aliases.json")
            if os.path.exists(noun_alias_path):
                with open(noun_alias_path, 'r') as f:
                    self.noun_aliases = json.load(f)
            
            # Load compound nouns (if exists)
            compound_path = os.path.join(self.vocab_dir, "compound_nouns.json")
            if os.path.exists(compound_path):
                with open(compound_path, 'r') as f:
                    self.compound_nouns = json.load(f)
            
            # Load adjectives
            adj_path = os.path.join(self.vocab_dir, "adjectives.txt")
            if os.path.exists(adj_path):
                with open(adj_path, 'r') as f:
                    self.adjectives = set(line.strip().lower() for line in f if line.strip())
            else:
                # Create a default adjectives file if it doesn't exist
                self._create_default_adjectives_file(adj_path)
            
            # Load prepositions
            prep_path = os.path.join(self.vocab_dir, "prepositions.txt")
            if os.path.exists(prep_path):
                with open(prep_path, 'r') as f:
                    self.prepositions = set(line.strip().lower() for line in f if line.strip())
            else:
                # Create a default prepositions file if it doesn't exist
                self._create_default_prepositions_file(prep_path)
            
            # Load directions
            dir_path = os.path.join(self.vocab_dir, "directions.txt")
            if os.path.exists(dir_path):
                with open(dir_path, 'r') as f:
                    self.directions = set(line.strip().lower() for line in f if line.strip())
            else:
                # Create a default directions file
                self._create_default_directions_file(dir_path)
            
            # Load articles
            self.articles = {"a", "an", "the", "some", "any"}
            
        except Exception as e:
            print(f"Error loading vocabulary: {e}")
            # Create default vocabulary
            self._create_default_vocabulary()
    
    def _create_default_vocabulary(self) -> None:
        """Create default vocabulary if files don't exist."""
        # Default verbs (with synonyms)
        self.verbs = {
            # Movement verbs
            "go": "go", "move": "go", "walk": "go", "run": "go", "travel": "go",
            # Interaction verbs
            "take": "take", "grab": "take", "pick": "take", "get": "take",
            "drop": "drop", "discard": "drop", "put": "put", "place": "put",
            "use": "use", "activate": "use", "operate": "use",
            "examine": "examine", "look": "examine", "inspect": "examine", "check": "examine",
            "open": "open", "unlock": "open",
            "close": "close", "shut": "close", "lock": "close",
            # Combat verbs
            "attack": "attack", "hit": "attack", "strike": "attack", "fight": "attack",
            "defend": "defend", "block": "defend", "parry": "defend",
            # Inventory verbs
            "inventory": "inventory", "i": "inventory", "items": "inventory",
            # Communication verbs
            "talk": "talk", "speak": "talk", "say": "talk", "ask": "talk"
        }
        
        # Default nouns
        self.nouns = {
            "door", "key", "sword", "shield", "potion", "book",
            "chest", "box", "table", "chair", "bed", "window",
            "goblin", "troll", "dragon", "merchant", "guard", "villager",
            "room", "hall", "cave", "forest", "mountain", "river"
        }
        
        # Default compound nouns
        self.compound_nouns = {}
        
        # Default noun aliases
        self.noun_aliases = {
            "blade": "sword",
            "container": "box",
            "crate": "box"
        }
        
        # Default directions
        self.directions = {
            "north", "east", "south", "west", 
            "northeast", "northwest", "southeast", "southwest",
            "up", "down", "in", "out", "forward", "back"
        }
        
        # Default adjectives
        self.adjectives = {
            "rusty", "shiny", "old", "new", "large", "small",
            "heavy", "light", "sharp", "dull", "broken", "intact",
            "magic", "mundane", "valuable", "worthless", "red", "blue",
            "green", "black", "white", "wooden", "metal", "leather"
        }
        
        # Default prepositions
        self.prepositions = {
            "in", "on", "at", "to", "with", "from", "by",
            "under", "over", "through", "between", "behind",
            "above", "below", "beside", "near", "against"
        }
        
        # Default articles
        self.articles = {"a", "an", "the", "some", "any"}
    
    def _create_default_verbs_file(self, file_path: str) -> None:
        """Create a default verbs file."""
        default_verbs = {
            "go": ["move", "walk", "run", "travel"],
            "take": ["grab", "pick", "get"],
            "drop": ["discard"],
            "put": ["place"],
            "use": ["activate", "operate"],
            "examine": ["look", "inspect", "check"],
            "open": ["unlock"],
            "close": ["shut", "lock"],
            "attack": ["hit", "strike", "fight"],
            "defend": ["block", "parry"],
            "inventory": ["i", "items"],
            "talk": ["speak", "say", "ask"]
        }
        
        with open(file_path, 'w') as f:
            json.dump(default_verbs, f, indent=4)
    
    def _create_default_nouns_file(self, file_path: str) -> None:
        """Create a default nouns file."""
        default_nouns = [
            "door", "key", "sword", "shield", "potion", "book",
            "chest", "box", "table", "chair", "bed", "window",
            "goblin", "troll", "dragon", "merchant", "guard", "villager",
            "room", "hall", "cave", "forest", "mountain", "river"
        ]
        
        with open(file_path, 'w') as f:
            f.write("\n".join(default_nouns))
    
    def _create_default_adjectives_file(self, file_path: str) -> None:
        """Create a default adjectives file."""
        default_adjectives = [
            "rusty", "shiny", "old", "new", "large", "small",
            "heavy", "light", "sharp", "dull", "broken", "intact",
            "magic", "mundane", "valuable", "worthless", "red", "blue",
            "green", "black", "white", "wooden", "metal", "leather"
        ]
        
        with open(file_path, 'w') as f:
            f.write("\n".join(default_adjectives))
    
    def _create_default_prepositions_file(self, file_path: str) -> None:
        """Create a default prepositions file."""
        default_prepositions = [
            "in", "on", "at", "to", "with", "from", "by",
            "under", "over", "through", "between", "behind",
            "above", "below", "beside", "near", "against"
        ]
        
        with open(file_path, 'w') as f:
            f.write("\n".join(default_prepositions))
    
    def _create_default_directions_file(self, file_path: str) -> None:
        """Create a default directions file."""
        default_directions = [
            "north", "east", "south", "west", 
            "northeast", "northwest", "southeast", "southwest",
            "up", "down", "in", "out", "forward", "back"
        ]
        
        with open(file_path, 'w') as f:
            f.write("\n".join(default_directions))
    
    def load_monster_vocab(self, monster_list: List[Dict]) -> None:
        """
        Dynamically load monster names and aliases as nouns.
        
        Args:
            monster_list: List of monster dictionaries with names and optional aliases
        """
        for m in monster_list:
            name = m.get('name', '')
            if not name:
                continue
                
            # Normalize name
            name_lower = name.lower()
            
            # Add to monster names set
            self.monster_names.add(name_lower)
            
            # Add to nouns set
            self.nouns.add(name_lower)
            
            # Check if multi-word name
            if ' ' in name_lower:
                # Add as compound noun
                self.compound_nouns[name_lower] = name_lower
                
                # Also add individual words as possible nouns for partial matching
                words = name_lower.split()
                for word in words:
                    if not (self.is_article(word) or self.is_adjective(word) or self.is_preposition(word)):
                        self.nouns.add(word)
                        # Also set up noun alias from last word to full name
                        # e.g., "weasel" -> "vine weasel"
                        if word == words[-1] and word != name_lower:
                            self.noun_aliases[word] = name_lower
            
            # Add category and threat tier as nouns if not already
            category = m.get('category', '').lower()
            threat_tier = m.get('threat_tier', '').lower()
            if category:
                self.nouns.add(category)
            if threat_tier:
                self.nouns.add(threat_tier)
            
            # Add aliases if available
            aliases = m.get('aliases', [])
            for alias in aliases:
                alias_lower = alias.lower()
                self.nouns.add(alias_lower)
                self.noun_aliases[alias_lower] = name_lower
                
                if ' ' in alias_lower:
                    # Compound alias
                    self.compound_nouns[alias_lower] = name_lower
        
        self._monster_vocab_loaded = True
    
    def is_verb(self, word: str) -> bool:
        """
        Check if a word is a verb.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is a verb, False otherwise
        """
        return word.lower() in self.verbs
    
    def is_direction(self, word: str) -> bool:
        """
        Check if a word is a direction.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is a direction, False otherwise
        """
        return word.lower() in self.directions
    
    def is_noun(self, word: str) -> bool:
        """
        Check if a word is a noun.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is a noun, False otherwise
        """
        word = word.lower()
        return (word in self.nouns or 
                word in self.noun_aliases or
                word in self.monster_names)
    
    def is_compound_noun(self, phrase: str) -> bool:
        """
        Check if a phrase is a compound noun.
        
        Args:
            phrase: The phrase to check
            
        Returns:
            True if the phrase is a compound noun, False otherwise
        """
        return phrase.lower() in self.compound_nouns
    
    def get_compounds_starting_with(self, word: str) -> List[str]:
        """
        Get compound nouns starting with the given word.
        
        Args:
            word: The starting word
            
        Returns:
            List of compound nouns starting with the word
        """
        word_lower = word.lower()
        return [compound for compound in self.compound_nouns 
                if compound.startswith(word_lower + ' ')]
    
    def is_adjective(self, word: str) -> bool:
        """
        Check if a word is an adjective.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is an adjective, False otherwise
        """
        return word.lower() in self.adjectives
    
    def is_preposition(self, word: str) -> bool:
        """
        Check if a word is a preposition.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is a preposition, False otherwise
        """
        return word.lower() in self.prepositions
    
    def is_article(self, word: str) -> bool:
        """
        Check if a word is an article.
        
        Args:
            word: The word to check
            
        Returns:
            True if the word is an article, False otherwise
        """
        return word.lower() in self.articles
    
    def get_canonical_verb(self, verb: str) -> str:
        """
        Get the canonical form of a verb.
        
        Args:
            verb: The verb to get the canonical form for
            
        Returns:
            The canonical form of the verb, or the verb itself if not found
        """
        return self.verbs.get(verb.lower(), verb.lower())
    
    def get_canonical_noun(self, noun: str) -> str:
        """
        Get the canonical form of a noun.
        
        Args:
            noun: The noun to get the canonical form for
            
        Returns:
            The canonical form of the noun, or the noun itself if not found
        """
        noun_lower = noun.lower()
        
        # First check noun aliases
        if noun_lower in self.noun_aliases:
            return self.noun_aliases[noun_lower]
        
        # Then check compound nouns
        if noun_lower in self.compound_nouns:
            return self.compound_nouns[noun_lower]
        
        # Then check if it's a recognized noun
        if noun_lower in self.nouns:
            return noun_lower
        
        # Not found
        return noun_lower
    
    def add_verb(self, verb: str, synonyms: List[str] = None) -> None:
        """
        Add a verb and its synonyms to the vocabulary.
        
        Args:
            verb: The canonical form of the verb
            synonyms: Optional list of synonyms
        """
        verb = verb.lower()
        self.verbs[verb] = verb
        
        if synonyms:
            for syn in synonyms:
                self.verbs[syn.lower()] = verb
    
    def add_noun(self, noun: str) -> None:
        """
        Add a noun to the vocabulary.
        
        Args:
            noun: The noun to add
        """
        self.nouns.add(noun.lower())
    
    def add_adjective(self, adjective: str) -> None:
        """
        Add an adjective to the vocabulary.
        
        Args:
            adjective: The adjective to add
        """
        self.adjectives.add(adjective.lower())
    
    def add_preposition(self, preposition: str) -> None:
        """
        Add a preposition to the vocabulary.
        
        Args:
            preposition: The preposition to add
        """
        self.prepositions.add(preposition.lower())
    
    def save_vocabulary(self) -> None:
        """Save vocabulary to files."""
        try:
            # Ensure directory exists
            os.makedirs(self.vocab_dir, exist_ok=True)
            
            # Save verbs
            verb_canonical = {}
            for word, canonical in self.verbs.items():
                if canonical == word:  # This is a canonical form
                    verb_canonical[word] = [syn for syn, can in self.verbs.items() 
                                          if can == word and syn != word]
            
            with open(os.path.join(self.vocab_dir, "verbs.json"), 'w') as f:
                json.dump(verb_canonical, f, indent=4)
            
            # Save nouns
            with open(os.path.join(self.vocab_dir, "nouns.txt"), 'w') as f:
                f.write("\n".join(sorted(self.nouns)))
            
            # Save compound nouns
            with open(os.path.join(self.vocab_dir, "compound_nouns.json"), 'w') as f:
                json.dump(self.compound_nouns, f, indent=4)
            
            # Save noun aliases
            with open(os.path.join(self.vocab_dir, "noun_aliases.json"), 'w') as f:
                json.dump(self.noun_aliases, f, indent=4)
            
            # Save adjectives
            with open(os.path.join(self.vocab_dir, "adjectives.txt"), 'w') as f:
                f.write("\n".join(sorted(self.adjectives)))
            
            # Save prepositions
            with open(os.path.join(self.vocab_dir, "prepositions.txt"), 'w') as f:
                f.write("\n".join(sorted(self.prepositions)))
            
            # Save directions
            with open(os.path.join(self.vocab_dir, "directions.txt"), 'w') as f:
                f.write("\n".join(sorted(self.directions)))
                
        except Exception as e:
            print(f"Error saving vocabulary: {e}")

    def find_possible_compound_nouns(self, tokens: List[str]) -> List[Tuple[str, int]]:
        """
        Find possible compound nouns in a list of tokens.
        
        Args:
            tokens: List of token words
            
        Returns:
            List of tuples (compound_noun, num_tokens_used)
        """
        results = []
        tokens_lower = [t.lower() for t in tokens]
        
        # Check multi-word phrases for compound nouns
        for start_idx in range(len(tokens)):
            for end_idx in range(start_idx + 1, min(start_idx + 5, len(tokens) + 1)):
                phrase = " ".join(tokens_lower[start_idx:end_idx])
                if self.is_compound_noun(phrase):
                    results.append((phrase, end_idx - start_idx))
        
        # Sort by length (number of tokens) descending
        results.sort(key=lambda x: x[1], reverse=True)
        return results