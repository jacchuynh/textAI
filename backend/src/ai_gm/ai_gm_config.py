"""
Configuration for the integrated AI GM Brain system.

This module provides configurations for all components of the AI GM Brain,
including parser, decision logic, output generation, and component integration.
"""

from typing import Dict, Any, List
from enum import Enum


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
    
    # Disambiguation Templates
    DISAMBIGUATION_TEMPLATES = {
        "object_choice": "Which {object_type} do you mean?\n{options}\nEnter the number of your choice, or 'cancel' to abort.",
        "action_choice": "How would you like to {action}?\n{options}\nEnter the number of your choice, or 'cancel' to abort.",
        "direction_choice": "Which direction?\n{options}\nEnter the number of your choice, or 'cancel' to abort."
    }
    
    # Event Response Configuration
    EVENT_RESPONSE_TRIGGERS = {
        'LOCATION_ENTERED', 'NPC_INTERACTION', 'NARRATIVE_BRANCH_AVAILABLE',
        'WORLD_STATE_CHANGED', 'COMBAT_STARTED', 'QUEST_COMPLETED',
        'PLAYER_COMMAND'  # Added for parser integration
    }
    
    # LLM Trigger Conditions
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
    
    # Pacing Settings
    PACING_SETTINGS = {
        "ambient_check_interval_minutes": 2,
        "npc_initiative_check_interval_minutes": 1,
        "event_summary_check_interval_hours": 1,
        "session_stale_threshold_hours": 24
    }
    
    # World Reaction Settings
    WORLD_REACTION_SETTINGS = {
        "reputation_decay_rate": 0.1,  # How quickly reputation effects fade
        "positive_action_threshold": 5,  # Threshold for considering actions positive
        "negative_action_threshold": -5,  # Threshold for considering actions negative
        "reputation_max_history": 20  # Maximum number of reputation events to track
    }
    
    # Domain Integration Settings
    DOMAIN_INTEGRATION_SETTINGS = {
        "combat_domain_primary": "COMBAT",
        "social_domain_primary": "SOCIAL",
        "exploration_domain_primary": "EXPLORATION",
        "domain_cooldown_seconds": 60  # Minimum time between same domain uses
    }
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """Get the default configuration dictionary."""
        return {
            "parser": {
                "enabled": cls.PARSER_ENABLED,
                "use_disambiguation": cls.USE_DISAMBIGUATION,
                "max_disambiguation_options": cls.MAX_DISAMBIGUATION_OPTIONS,
                "auto_resolve_single_match": cls.AUTO_RESOLVE_SINGLE_MATCH,
                "enable_suggestions": cls.ENABLE_PARSER_SUGGESTIONS
            },
            "processing": {
                "llm_cooldown_seconds": cls.LLM_COOLDOWN_SECONDS,
                "max_recent_events": cls.MAX_RECENT_EVENTS,
                "use_enhanced_templates": cls.USE_ENHANCED_TEMPLATES,
                "enable_contextual_responses": cls.ENABLE_CONTEXTUAL_RESPONSES,
                "include_parser_metadata": cls.INCLUDE_PARSER_METADATA
            },
            "templates": {
                "action_templates": cls.ACTION_TEMPLATES,
                "conversational_keywords": cls.CONVERSATIONAL_KEYWORDS,
                "disambiguation_templates": cls.DISAMBIGUATION_TEMPLATES
            },
            "integration": {
                "world_reaction_enabled": True,
                "pacing_enabled": True,
                "output_enabled": True,
                "combat_enabled": True,
                "llm_enabled": True
            }
        }
    
    @classmethod
    def get_development_config(cls) -> Dict[str, Any]:
        """Get configuration optimized for development."""
        config = cls.get_config()
        config["processing"]["llm_cooldown_seconds"] = 1  # Faster for development
        config["integration"]["debug_mode"] = True
        config["logging"] = {
            "level": "DEBUG",
            "include_parser_details": True,
            "include_integration_timing": True
        }
        return config
    
    @classmethod
    def get_production_config(cls) -> Dict[str, Any]:
        """Get configuration optimized for production."""
        config = cls.get_config()
        config["processing"]["llm_cooldown_seconds"] = 10  # More conservative for production
        config["integration"]["debug_mode"] = False
        config["logging"] = {
            "level": "INFO",
            "include_parser_details": False,
            "include_integration_timing": False
        }
        config["performance"] = {
            "enable_caching": True,
            "cache_ttl_seconds": 300,
            "max_concurrent_llm_requests": 5
        }
        return config
    
    @classmethod
    def get_testing_config(cls) -> Dict[str, Any]:
        """Get configuration optimized for testing."""
        config = cls.get_config()
        config["processing"]["llm_cooldown_seconds"] = 0  # No cooldown for testing
        config["integration"]["debug_mode"] = True
        config["integration"]["mock_mode"] = True  # Use mocks for external services
        config["logging"] = {
            "level": "DEBUG",
            "include_parser_details": True,
            "include_integration_timing": True
        }
        return config
    
    @classmethod
    def get_template_for_action(cls, action: str, context_key: str = "template") -> str:
        """Get template for a specific action."""
        action_config = cls.ACTION_TEMPLATES.get(action, {})
        return action_config.get(context_key, f"You {action}.")
    
    @classmethod
    def should_trigger_llm(cls, trigger_type: str) -> bool:
        """Check if a condition should trigger LLM processing."""
        return cls.LLM_TRIGGER_CONDITIONS.get(trigger_type, False)