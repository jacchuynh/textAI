"""
Configuration for the integrated AI GM Brain + Text Parser system
"""

from typing import Dict, Any, List

class IntegratedAIGMConfig:
    """Configuration for the integrated AI GM Brain system."""
    
    # Parser Integration Settings
    PARSER_ENABLED = True
    USE_DISAMBIGUATION = True
    MAX_DISAMBIGUATION_OPTIONS = 5
    AUTO_RESOLVE_SINGLE_MATCH = True
    
    # Processing Settings
    LLM_COOLDOWN_SECONDS = 5
    MAX_RECENT_EVENTS = 20
    ENABLE_PARSER_SUGGESTIONS = True
    
    # Response Generation Settings
    USE_ENHANCED_TEMPLATES = True
    ENABLE_CONTEXTUAL_RESPONSES = True
    INCLUDE_PARSER_METADATA = True
    
    # Template Settings for Parser Actions
    ACTION_TEMPLATES = {
        "look": {
            "with_target": "You examine the {parsed_command.direct_object}. {IF command.success}[Detailed description]{ELSE}You don't see anything special.{ENDIF}",
            "without_target": "You look around. {IF location_context}The area {RANDOM[appears|seems|looks]} {location_context.dominant_aura}.{ENDIF}"
        },
        "take": {
            "success": "You take the {parsed_command.direct_object}.",
            "failure": "You cannot take that right now.",
            "template": "{IF command.success}You take the {parsed_command.direct_object}.{ELSE}You cannot take that right now.{ENDIF}"
        },
        "attack": {
            "success": "You attack the {parsed_command.direct_object}!",
            "failure": "You cannot attack that right now.",
            "implicit_target": "You attack!",
            "template": "{IF command.success}You attack{IF parsed_command.direct_object} the {parsed_command.direct_object}{ENDIF}!{ELSE}You cannot attack that right now.{ENDIF}"
        },
        "go": {
            "direction": "{IF command.success}You head {parsed_command.direct_object}.{ELSE}You cannot go that way.{ENDIF}",
            "location": "{IF command.success}You move toward {parsed_command.direct_object}.{ELSE}You cannot reach that destination.{ENDIF}"
        }
    }
    
    # Disambiguation Settings
    DISAMBIGUATION_PROMPT_TEMPLATE = "Which {object_type} do you mean?\n{options}\nEnter the number of your choice, or 'cancel' to abort."
    
    # Error Handling
    ERROR_MESSAGES = {
        "parsing_failed": "I don't understand that command. Try something like 'look', 'take [item]', or 'go [direction]'.",
        "disambiguation_failed": "I couldn't resolve which object you meant. Please try being more specific.",
        "action_failed": "I couldn't complete that action right now.",
        "no_suggestions": "I'm not sure what you want to do. Try 'help' for available commands."
    }
    
    # Conversational Keywords (enhanced from original)
    CONVERSATIONAL_KEYWORDS = {
        'question_words': ['what', 'where', 'when', 'why', 'how', 'who', 'which'],
        'conversational_starters': [
            'tell me', 'explain', 'describe', 'what about', 'how about',
            'can you', 'could you', 'would you', 'do you know'
        ],
        'social_actions': [
            'talk to', 'speak with', 'ask', 'greet', 'converse', 'chat with',
            'question', 'inquire', 'discuss'
        ],
        'narrative_triggers': [
            'what happened', 'tell me about', 'describe the', 'what is',
            'who is', 'where is', 'story', 'legend', 'history'
        ]
    }
    
    # Event Response Configuration
    EVENT_RESPONSE_TRIGGERS = {
        'LOCATION_ENTERED', 'NPC_INTERACTION', 'NARRATIVE_BRANCH_AVAILABLE',
        'WORLD_STATE_CHANGED', 'COMBAT_STARTED', 'QUEST_COMPLETED',
        'PLAYER_COMMAND'  # Added for parser integration
    }
    
    # Parser-specific Event Templates
    PARSER_EVENT_TEMPLATES = {
        "command_executed": "Command '{action}' executed successfully.",
        "disambiguation_resolved": "Choice resolved - continuing with action.",
        "parsing_error": "Unable to parse command: '{error}'",
        "combat_action": "Combat action '{action}' performed."
    }
    
    # LLM Trigger Conditions (for Phase 2)
    LLM_TRIGGER_CONDITIONS = {
        "complex_questions": True,
        "narrative_requests": True,
        "ambiguous_commands": True,
        "social_interactions": True,
        "world_lore_questions": True
    }
    
    # Performance Monitoring
    ENABLE_PERFORMANCE_LOGGING = True
    LOG_PARSER_STATISTICS = True
    LOG_DISAMBIGUATION_RATES = True
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get configuration as dictionary."""
        return {
            'parser_enabled': cls.PARSER_ENABLED,
            'use_disambiguation': cls.USE_DISAMBIGUATION,
            'max_disambiguation_options': cls.MAX_DISAMBIGUATION_OPTIONS,
            'llm_cooldown_seconds': cls.LLM_COOLDOWN_SECONDS,
            'max_recent_events': cls.MAX_RECENT_EVENTS,
            'action_templates': cls.ACTION_TEMPLATES,
            'conversational_keywords': cls.CONVERSATIONAL_KEYWORDS,
            'event_response_triggers': cls.EVENT_RESPONSE_TRIGGERS,
            'error_messages': cls.ERROR_MESSAGES,
            'llm_trigger_conditions': cls.LLM_TRIGGER_CONDITIONS
        }
    
    @classmethod
    def get_template_for_action(cls, action: str, context_key: str = "template") -> str:
        """Get template for a specific action."""
        action_config = cls.ACTION_TEMPLATES.get(action, {})
        return action_config.get(context_key, f"You {action}.")
    
    @classmethod
    def should_trigger_llm(cls, trigger_type: str) -> bool:
        """Check if a condition should trigger LLM processing."""
        return cls.LLM_TRIGGER_CONDITIONS.get(trigger_type, False)