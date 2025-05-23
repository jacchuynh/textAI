"""
Core parser engine for processing player text input.

This module handles tokenization, parsing, and mapping player text commands
to executable game actions.
"""
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
import re
import string
from enum import Enum

from event_bus import event_bus, GameEvent
from game_context import game_context # Assuming game_context is globally accessible
from .vocabulary import VocabularyManager
from .object_resolver import ObjectResolver


class TokenType(Enum):
    """Types of tokens in player input."""
    VERB = "verb"
    NOUN = "noun"
    ADJECTIVE = "adjective"
    PREPOSITION = "preposition"
    ARTICLE = "article"
    DIRECTION = "direction"
    PRONOUN = "pronoun"
    UNKNOWN = "unknown"


class CommandPattern(Enum):
    """Common command patterns."""
    VERB_ONLY = "verb_only"  # look, inventory
    VERB_DIRECTION = "verb_direction"  # go north
    VERB_OBJECT = "verb_object"  # take sword
    VERB_OBJECT_PREP_OBJECT = "verb_object_prep_object"  # put key in lock
    IMPLICIT_VERB_DIRECTION = "implicit_verb_direction" # north (implies "go north")
    IMPLICIT_VERB_OBJECT = "implicit_verb_object" # sword (implies "examine sword")
    UNKNOWN = "unknown"


class Token:
    """Represents a token in the player's command."""
    
    def __init__(self, word: str, token_type: TokenType):
        """
        Initialize a token.
        
        Args:
            word: The original word
            token_type: The type of token
        """
        self.word = word.lower()
        self.type = token_type
        
    def __repr__(self):
        return f"Token({self.word}, {self.type.value})"


class NounPhrase:
    """Represents a noun phrase in the player's command."""
    
    def __init__(self, noun: str, adjectives: List[str] = None, determiner: str = None, original_text: str = None):
        """
        Initialize a noun phrase.
        
        Args:
            noun: The main noun (can be compound)
            adjectives: Optional list of adjectives
            determiner: Optional determiner (e.g., "the", "a")
            original_text: The original text that formed this noun phrase
        """
        self.noun = noun.lower() # This will be the (potentially compound) noun
        self.adjectives = [adj.lower() for adj in adjectives] if adjectives else []
        self.determiner = determiner.lower() if determiner else None
        self.game_object_id: Optional[str] = None # To be filled by object resolution
        self.original_text: str = original_text if original_text else noun

    def __repr__(self):
        adj_str = " ".join(self.adjectives)
        det_str = f"{self.determiner} " if self.determiner else ""
        return f"NounPhrase({det_str}{adj_str} {self.noun})"

class ParsedCommand:
    """Represents a parsed player command."""
    
    def __init__(self, 
                 action: Optional[str] = None, 
                 direct_object_phrase: Optional[NounPhrase] = None,
                 preposition: Optional[str] = None,
                 indirect_object_phrase: Optional[NounPhrase] = None,
                 raw_input: Optional[str] = None,
                 error_message: Optional[str] = None,
                 disambiguation_target: Optional[str] = None, # "direct" or "indirect"
                 disambiguation_candidates: Optional[List[Dict[str, Any]]] = None):
        self.action = action
        self.direct_object_phrase = direct_object_phrase
        self.preposition = preposition
        self.indirect_object_phrase = indirect_object_phrase
        self.raw_input = raw_input
        self.error_message = error_message
        self.disambiguation_target = disambiguation_target
        self.disambiguation_candidates = disambiguation_candidates
        self.pattern = self._determine_pattern()
        
    def _determine_pattern(self) -> CommandPattern:
        if not self.action:
            return CommandPattern.UNKNOWN
            
        if self.action and not self.direct_object_phrase and not self.indirect_object_phrase:
            # Could be VERB_ONLY or IMPLICIT_VERB_DIRECTION/OBJECT if action was inferred
            if self.raw_input and " " not in self.raw_input: # Single word input
                if self.action == "go" and self.raw_input.lower() in vocabulary_manager.directions:
                     return CommandPattern.IMPLICIT_VERB_DIRECTION
                # Further checks for implicit object examine could be added here
                # For now, assume VERB_ONLY if action is explicit
            return CommandPattern.VERB_ONLY
            
        if self.action == "go" and self.direct_object_phrase and \
           self.direct_object_phrase.noun in vocabulary_manager.directions and \
           not self.indirect_object_phrase:
            return CommandPattern.VERB_DIRECTION
            
        if self.action and self.direct_object_phrase and not self.indirect_object_phrase:
            return CommandPattern.VERB_OBJECT
            
        if self.action and self.direct_object_phrase and self.preposition and self.indirect_object_phrase:
            return CommandPattern.VERB_OBJECT_PREP_OBJECT
            
        return CommandPattern.UNKNOWN
            
    def to_command_dict(self) -> Dict[str, Any]:
        """Convert to a structured command dictionary."""
        cmd = {
            'action': f"ACTION_{self.action.upper()}" if self.action else None,
            'direct_object_id': self.direct_object_phrase.game_object_id if self.direct_object_phrase else None,
            'direct_object_noun': self.direct_object_phrase.noun if self.direct_object_phrase else None,
            'preposition': self.preposition,
            'indirect_object_id': self.indirect_object_phrase.game_object_id if self.indirect_object_phrase else None,
            'indirect_object_noun': self.indirect_object_phrase.noun if self.indirect_object_phrase else None,
            'raw_input': self.raw_input,
            'pattern': self.pattern.value if self.pattern else None,
            'error_message': self.error_message,
            'requires_disambiguation': bool(self.disambiguation_candidates),
            'disambiguation_target': self.disambiguation_target
        }
        return cmd
    
    def needs_disambiguation(self) -> bool:
        return bool(self.disambiguation_candidates)
    
    def has_error(self) -> bool:
        return bool(self.error_message)
    
    def update_after_disambiguation(self, selected_object_id: str) -> bool:
        if not self.disambiguation_candidates or not self.disambiguation_target:
            return False
            
        target_phrase = None
        if self.disambiguation_target == "direct" and self.direct_object_phrase:
            target_phrase = self.direct_object_phrase
        elif self.disambiguation_target == "indirect" and self.indirect_object_phrase:
            target_phrase = self.indirect_object_phrase
        
        if target_phrase:
            target_phrase.game_object_id = selected_object_id
            # Update reference history
            obj_data = game_context.get_object_by_id(selected_object_id) or game_context.get_monster_by_id(selected_object_id)
            if obj_data:
                 entity_type = "monsters" if obj_data.get("threat_tier") else "objects"
                 game_context.reference_entity(selected_object_id, entity_type)

            self.disambiguation_candidates = None
            self.disambiguation_target = None
            self.error_message = None # Clear "multiple objects match" error
            return True
        return False
    
    def __repr__(self):
        return (f"ParsedCommand(action={self.action}, "
                f"direct_object={self.direct_object_phrase}, "
                f"preposition={self.preposition}, "
                f"indirect_object={self.indirect_object_phrase}, "
                f"pattern={self.pattern.value if self.pattern else 'None'}, "
                f"error='{self.error_message}', "
                f"disambiguation_needed={self.needs_disambiguation()})")

class ParserEngine:
    def __init__(self, vocabulary_manager: VocabularyManager, object_resolver: ObjectResolver):
        self.vocabulary = vocabulary_manager
        self.object_resolver = object_resolver
        self.action_handlers: Dict[str, Callable[[ParsedCommand, Dict[str, Any]], ParsedCommand]] = {}
        self.pronouns_map = {
            "it": ["object", "monster"], "them": ["object", "monster"],
            "him": ["monster", "npc"],   "her": ["monster", "npc"],
            # "this", "that", "these", "those" could also be here with more complex logic
        }
        self._register_default_handlers()

    def _register_default_handlers(self) -> None:
        self.action_handlers["attack"] = self._handle_attack_action
        # Add more handlers: e.g., "talk" -> _handle_talk_action (target NPCs)

    def _handle_attack_action(self, command: ParsedCommand, context: Dict[str, Any]) -> ParsedCommand:
        if not command.direct_object_phrase and context.get("in_combat") and context.get("last_enemy"):
            last_enemy_id = context["last_enemy"]
            last_enemy_data = game_context.get_monster_by_id(last_enemy_id)
            if last_enemy_data:
                command.direct_object_phrase = NounPhrase(
                    noun=last_enemy_data["name"],
                    adjectives=last_enemy_data.get("adjectives", []),
                    original_text=last_enemy_data["name"]
                )
                command.direct_object_phrase.game_object_id = last_enemy_id
                command.pattern = CommandPattern.VERB_OBJECT # Update pattern
                command.error_message = None # Clear previous "what to attack?" error
        elif not command.direct_object_phrase:
            command.error_message = "Who or what do you want to attack?"
        return command

    def _normalize_input(self, input_text: str) -> str:
        normalized = input_text.lower()
        translator = str.maketrans('', '', string.punctuation.replace("'", ""))
        normalized = normalized.translate(translator)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized

    def _tokenize(self, input_text: str) -> List[Token]:
        if not input_text: return []
        words = input_text.split()
        tokens = []
        for word in words:
            tokens.append(Token(word, self._determine_token_type(word)))
        return tokens

    def _determine_token_type(self, word: str) -> TokenType:
        if self.vocabulary.is_verb(word): return TokenType.VERB
        if word in self.pronouns_map: return TokenType.PRONOUN
        if self.vocabulary.is_direction(word): return TokenType.DIRECTION
        if self.vocabulary.is_noun(word): return TokenType.NOUN # Checks simple, compound, aliases, monsters
        if self.vocabulary.is_adjective(word): return TokenType.ADJECTIVE
        if self.vocabulary.is_preposition(word): return TokenType.PREPOSITION
        if self.vocabulary.is_article(word): return TokenType.ARTICLE
        return TokenType.UNKNOWN

    def _extract_action(self, tokens: List[Token]) -> Optional[str]:
        if not tokens: return None
        if tokens[0].type == TokenType.VERB:
            return self.vocabulary.get_canonical_verb(tokens[0].word)
        return None

    def _extract_noun_phrase(self, tokens: List[Token], context: Dict[str, Any]) -> Tuple[Optional[NounPhrase], List[Token]]:
        if not tokens: return None, []

        original_tokens_for_phrase = []
        adjectives = []
        determiner = None
        noun_tokens = []
        
        # Handle pronoun first
        if tokens[0].type == TokenType.PRONOUN:
            pronoun_word = tokens[0].word
            original_tokens_for_phrase.append(tokens[0].word)
            resolved_id = self._resolve_pronoun(pronoun_word, context)
            if resolved_id:
                # Fetch the object/monster name to form a NounPhrase
                entity_data = game_context.get_object_by_id(resolved_id) or \
                              game_context.get_monster_by_id(resolved_id) # or NPC
                if entity_data:
                    np = NounPhrase(
                        noun=entity_data["name"], 
                        adjectives=entity_data.get("adjectives", []),
                        original_text=pronoun_word
                        )
                    np.game_object_id = resolved_id
                    return np, tokens[1:]
            return None, tokens # Pronoun not resolved or entity not found

        # Check for determiner/article
        idx = 0
        if idx < len(tokens) and tokens[idx].type == TokenType.ARTICLE:
            determiner = tokens[idx].word
            original_tokens_for_phrase.append(tokens[idx].word)
            idx += 1
            
        # Collect adjectives
        while idx < len(tokens) and tokens[idx].type == TokenType.ADJECTIVE:
            adjectives.append(tokens[idx].word)
            original_tokens_for_phrase.append(tokens[idx].word)
            idx += 1

        # Try to match compound nouns first (longest match)
        remaining_tokens_for_noun = tokens[idx:]
        
        # Check for compound nouns using the remaining tokens
        # We check from longest possible phrase to shortest
        found_compound = False
        for length in range(min(4, len(remaining_tokens_for_noun)), 0, -1): # Max 4 words for compound, can adjust
            potential_compound_words = [t.word for t in remaining_tokens_for_noun[:length]]
            potential_compound_phrase = " ".join(potential_compound_words)
            if self.vocabulary.is_compound_noun(potential_compound_phrase):
                noun_tokens = potential_compound_words
                original_tokens_for_phrase.extend(potential_compound_words)
                idx += length
                found_compound = True
                break
        
        if not found_compound and idx < len(tokens) and tokens[idx].type == TokenType.NOUN:
            noun_tokens = [tokens[idx].word]
            original_tokens_for_phrase.append(tokens[idx].word)
            idx += 1
        
        if not noun_tokens:
            # If we collected adjectives but no noun, it's an error like "take the shiny"
            if adjectives:
                 # This case should be handled by the main parse logic (verb expects object)
                return NounPhrase(noun="", adjectives=adjectives, determiner=determiner, original_text=" ".join(original_tokens_for_phrase)), tokens[idx:] # Return empty noun phrase for error check
            return None, tokens

        # The actual noun (could be compound)
        noun_str = " ".join(noun_tokens)
        # If it's an alias, get the canonical form
        noun_str = self.vocabulary.get_canonical_noun(noun_str)

        return NounPhrase(noun_str, adjectives, determiner, " ".join(original_tokens_for_phrase)), tokens[idx:]

    def _resolve_pronoun(self, pronoun: str, context: Dict[str, Any]) -> Optional[str]:
        if pronoun not in self.pronouns_map:
            return None
        
        allowed_types = self.pronouns_map[pronoun]
        
        # Check recently referenced monsters/NPCs first for "him", "her", "them"
        if "monster" in allowed_types or "npc" in allowed_types:
            recent_monsters = game_context.get_recently_referenced("monsters", n=1)
            if recent_monsters: return recent_monsters[0]
            # Add NPC check here when implemented
            # recent_npcs = game_context.get_recently_referenced("npcs", n=1)
            # if recent_npcs: return recent_npcs[0]

        # Check recently referenced objects for "it", "them"
        if "object" in allowed_types:
            recent_objects = game_context.get_recently_referenced("objects", n=1)
            if recent_objects: return recent_objects[0]
        
        # Fallback for "it": if in combat, could be the current/last enemy
        if pronoun == "it" and context.get("in_combat") and context.get("last_enemy"):
            return context["last_enemy"]
            
        return None

    def _extract_preposition(self, tokens: List[Token]) -> Optional[str]:
        if not tokens: return None
        if tokens[0].type == TokenType.PREPOSITION:
            return tokens[0].word
        return None

    def _handle_implicit_noun_command(self, tokens: List[Token], raw_input: str, context: Dict[str, Any]) -> ParsedCommand:
        """Handles commands like 'sword' -> 'examine sword'."""
        # Assume "examine" as the default action for a lone noun.
        # This could be made more context-sensitive (e.g., if item is a weapon and in combat, maybe "equip sword")
        action = "examine"
        
        # The noun phrase is the entire input in this case
        noun_phrase, _ = self._extract_noun_phrase(tokens, context)

        if not noun_phrase or not noun_phrase.noun:
            return ParsedCommand(raw_input=raw_input, error_message=f"What about the {tokens[0].word}?")

        command = ParsedCommand(action=action, direct_object_phrase=noun_phrase, raw_input=raw_input)
        command.pattern = CommandPattern.IMPLICIT_VERB_OBJECT
        return self._resolve_and_finalize_command(command, context)

    def _resolve_and_finalize_command(self, command: ParsedCommand, context: Dict[str, Any]) -> ParsedCommand:
        """Resolves NounPhrases to game_object_ids and finalizes the command."""
        if command.direct_object_phrase and not command.direct_object_phrase.game_object_id:
            resolved_direct = self.object_resolver.resolve_object(
                command.direct_object_phrase.noun,
                command.direct_object_phrase.adjectives,
                context=context
            )
            if isinstance(resolved_direct, dict) and resolved_direct.get("disambiguation_required"):
                command.error_message = f"Which {command.direct_object_phrase.noun} do you mean?"
                command.disambiguation_target = "direct"
                command.disambiguation_candidates = resolved_direct["candidates"]
                return command
            elif resolved_direct:
                command.direct_object_phrase.game_object_id = resolved_direct
            elif command.action not in ["look", "inventory", "help", "quit", "go"]: # Verbs that might not need an object
                 command.error_message = f"I don't see any '{command.direct_object_phrase.original_text}' here."
                 return command


        if command.indirect_object_phrase and not command.indirect_object_phrase.game_object_id:
            resolved_indirect = self.object_resolver.resolve_object(
                command.indirect_object_phrase.noun,
                command.indirect_object_phrase.adjectives,
                context=context
            )
            if isinstance(resolved_indirect, dict) and resolved_indirect.get("disambiguation_required"):
                command.error_message = f"Which {command.indirect_object_phrase.noun} (for the {command.preposition}) do you mean?"
                command.disambiguation_target = "indirect"
                command.disambiguation_candidates = resolved_indirect["candidates"]
                return command
            elif resolved_indirect:
                command.indirect_object_phrase.game_object_id = resolved_indirect
            else:
                command.error_message = f"I don't see any '{command.indirect_object_phrase.original_text}' to use with '{command.preposition}'."
                return command
        
        # Apply action-specific handlers
        if command.action in self.action_handlers:
            command = self.action_handlers[command.action](command, context)

        # Final pattern determination if not set by implicit handlers
        if command.pattern == CommandPattern.UNKNOWN or command.pattern is None:
             command.pattern = command._determine_pattern()


        return command

    def parse(self, input_text: str, context_override: Optional[Dict[str, Any]] = None) -> ParsedCommand:
        context = context_override if context_override else game_context.get_context()
        normalized = self._normalize_input(input_text)
        tokens = self._tokenize(normalized)

        if not tokens:
            return ParsedCommand(raw_input=input_text, error_message="Please type something.")

        # 1. Handle implicit commands (single word: direction or noun)
        if len(tokens) == 1:
            if tokens[0].type == TokenType.DIRECTION:
                # "north" -> "go north"
                np = NounPhrase(tokens[0].word, original_text=tokens[0].word)
                # Directions don't need ID resolution like objects
                return ParsedCommand(action="go", direct_object_phrase=np, raw_input=input_text, pattern=CommandPattern.IMPLICIT_VERB_DIRECTION)
            
            if tokens[0].type == TokenType.NOUN or \
               (tokens[0].type == TokenType.PRONOUN and tokens[0].word in self.pronouns_map): # "sword" or "it"
                return self._handle_implicit_noun_command(tokens, raw_input, context)

        # 2. Normal parsing: Extract action
        action = self._extract_action(tokens)
        if not action:
            # Attempt to infer action if input starts with noun/adj (e.g. "red sword" -> "examine red sword")
            if tokens[0].type in [TokenType.NOUN, TokenType.ADJECTIVE, TokenType.ARTICLE, TokenType.PRONOUN]:
                 return self._handle_implicit_noun_command(tokens, raw_input, context)
            return ParsedCommand(raw_input=input_text, error_message=f"I don't understand the verb '{tokens[0].word}'.")

        command_tokens_remaining = tokens[1:]

        # 3. Extract Direct Object
        direct_object_phrase, command_tokens_remaining = self._extract_noun_phrase(command_tokens_remaining, context)

        # 4. Extract Preposition
        preposition = self._extract_preposition(command_tokens_remaining)
        if preposition:
            command_tokens_remaining = command_tokens_remaining[1:]

        # 5. Extract Indirect Object (if preposition exists)
        indirect_object_phrase = None
        if preposition:
            if not command_tokens_remaining:
                 return ParsedCommand(action=action, direct_object_phrase=direct_object_phrase, preposition=preposition, raw_input=input_text, error_message=f"What do you want to {action} ... {preposition}?")
            indirect_object_phrase, command_tokens_remaining = self._extract_noun_phrase(command_tokens_remaining, context)
            if not indirect_object_phrase:
                 return ParsedCommand(action=action, direct_object_phrase=direct_object_phrase, preposition=preposition, raw_input=input_text, error_message=f"I'm missing what to use with '{preposition}'.")
        
        # Check for leftover tokens -> indicates a syntax error or unparsed input
        if command_tokens_remaining:
            return ParsedCommand(raw_input=input_text, error_message=f"I'm confused by the part starting with: '{' '.join(t.word for t in command_tokens_remaining)}'.")

        # Basic validation for verb-object requirements
        if action in ["take", "examine", "attack", "use", "open", "close", "drop", "eat", "drink"] and not direct_object_phrase:
            return ParsedCommand(action=action, raw_input=input_text, error_message=f"What do you want to {action}?")
        
        if action in ["put", "give"] and (not direct_object_phrase or not indirect_object_phrase or not preposition):
            if not direct_object_phrase:
                return ParsedCommand(action=action, raw_input=input_text, error_message=f"What do you want to {action}?")
            if not preposition:
                 return ParsedCommand(action=action, direct_object_phrase=direct_object_phrase, raw_input=input_text, error_message=f"Where/what do you want to {action} the {direct_object_phrase.noun}?")
            if not indirect_object_phrase:
                 return ParsedCommand(action=action, direct_object_phrase=direct_object_phrase, preposition=preposition, raw_input=input_text, error_message=f"What do you want to {action} the {direct_object_phrase.noun} {preposition}?")


        # Create initial ParsedCommand
        command = ParsedCommand(
            action=action,
            direct_object_phrase=direct_object_phrase,
            preposition=preposition,
            indirect_object_phrase=indirect_object_phrase,
            raw_input=input_text
        )
        
        # 6. Resolve NounPhrases and finalize
        return self._resolve_and_finalize_command(command, context)

    def execute_command(self, command: ParsedCommand) -> Dict[str, Any]:
        """
        Publishes a PLAYER_COMMAND event.
        Actual execution should be handled by subscribers to this event.
        
        Args:
            command: The parsed command to execute
            
        Returns:
            The command dictionary that was published
        """
        cmd_dict = command.to_command_dict()
        
        # Publish command event if no errors and no disambiguation needed
        if not command.has_error() and not command.needs_disambiguation():
            event = GameEvent(
                type="PLAYER_COMMAND",  # This should be a defined EventType or string
                actor=game_context.get_player_id(), # Assuming game_context is accessible
                context={
                    "command_details": cmd_dict,
                    "location_id": game_context.get_current_location()
                },
                tags=["player_action", command.action if command.action else "unknown_action"]
            )
            event_bus.publish(event) # Assuming event_bus is globally accessible
            
        return cmd_dict

# Global parser instance (requires vocabulary and object_resolver to be initialized first)
# These would typically be initialized in your __init__.py or main application setup
# from .vocabulary import VocabularyManager
# from .object_resolver import ObjectResolver
# vocabulary_manager = VocabularyManager() # Load vocab, monsters etc. here
# object_resolver = ObjectResolver(vocabulary_manager)
# parser_engine = ParserEngine(vocabulary_manager, object_resolver)