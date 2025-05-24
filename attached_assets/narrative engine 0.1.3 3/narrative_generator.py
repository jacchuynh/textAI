from .template_processor import TemplateProcessor # Assuming TemplateProcessor is in the same directory
from .narrative_context import NarrativeContext # Assuming NarrativeContext is in the same directory
# from ..event_bus import EventType # If EventType is needed here, adjust import

class NarrativeGenerator:
    def __init__(self, template_library=None):
        self.tp = TemplateProcessor()
        self.templates = template_library or self._load_templates()

    def _load_templates(self):
        # Example templates, should be loaded from data
        base_templates = {
            "location_entry": [
                "{actor} enters {location}, {IF is_familiar}recognizing familiar surroundings{ELSE}taking in the new environment{ENDIF}.",
                "{actor.subjective} {RANDOM[winces in pain|surveys the area|seems thoughtful|looks around cautiously]}."
            ],
            "domain_check_success": [
                "Drawing on {domain} expertise, {actor} {action} with {RANDOM[practiced ease|remarkable skill|confident precision]}."
            ],
            # --- NEW TEMPLATES FOR WORLD EVENTS ---
            "GLOBAL_ECONOMIC_SHIFT": [
                "The markets in {context.observation_point} seem unusually {IF context.economic_status=='recession'}quiet{ELSE}bustling{ENDIF}. Whispers about the realm's {context.economic_status} economy are on everyone's lips.",
                "A general sense of {IF context.economic_status=='recession'}hardship{ELIF context.economic_status=='depression'}despair{ELIF context.economic_status=='booming'}prosperity{ELSE}normalcy{ENDIF} hangs in the air. The current economic climate ({context.economic_status}) affects everyone.",
                "{IF context.economic_status=='recession'}Merchants grumble about slow trade, citing the widespread economic {context.economic_status}.{ELSE}The prosperous mood is palpable; the {context.economic_status} economy brings cheer to many.{ENDIF}"
            ],
            "GLOBAL_POLITICAL_SHIFT": [
                "Tension is noticeable; talk of {context.political_stability} in the {context.affected_region} dominates conversations.",
                "The recent political shifts towards {context.political_stability} have {RANDOM[put the guards on edge|made common folk anxious|emboldened dissidents|brought a fragile peace]}."
            ],
            "AMBIENT_WORLD_NARRATIVE": [
                "The air is crisp as {context.current_season} settles upon the land. {RANDOM[Birds chirp merrily|A chill wind blows|Leaves rustle underfoot|The sun beats down relentlessly]}.",
                "{IF context.active_global_threats}A shadow of unease is cast by the news of {RANDOM_FROM_LIST[context.active_global_threats]}.{ELSE}The realm feels relatively peaceful for now.{ENDIF}",
                "It's a typical day in {context.current_season}. {IF context.economic_status=='recession'}People seem to be conserving their resources.{ELIF context.economic_status=='booming'}There's a buzz of activity everywhere.{ELSE}Life goes on as usual.{ENDIF}"
            ],
            "GLOBAL_THREAT_EVENT": [ # Assuming context might have 'threat_name' and 'threat_details'
                "Word spreads like wildfire about {context.threat_name}. {context.threat_details}",
                "Fear grips the hearts of many as {context.threat_name} continues to {RANDOM[menace the northern borders|corrupt the ancient forests|plague the trade routes]}."
            ]
            # --- END NEW TEMPLATES ---
        }
        # Add a helper to TemplateProcessor for RANDOM_FROM_LIST if it doesn't exist
        # Or handle it here by selecting from list then passing to template
        return base_templates

    def fill_template(self, template: str, context: dict, char_context: Optional[dict] = None) -> str:
        """
        Fills a template using TemplateProcessor.
        The context should already contain all necessary data, including world state if relevant.
        """
        combined_context = dict(context) # Start with event context (which might include world state)
        
        if char_context and char_context.get("exists"): # Player/NPC specific context
            # Ensure 'actor' in combined_context is the character if this narrative is player-focused
            # For world events, 'actor' might be 'World' or 'System' from the event.
            # This part needs careful handling depending on who the narrative is for.
            # If the world event is being narrated *to* a player, actor should be player.
            # If it's a general world broadcast, actor might remain 'World'.
            if 'actor_data' not in combined_context: # Avoid overwriting if event already has specific actor data
                 combined_context['actor'] = {"gender": char_context.get("gender", "neutral"), "name": char_context.get("name", "Someone")}
                 # Add more actor/target/etc. as needed from char_context
        
        # Make sure top-level keys from context are directly accessible
        # e.g. if context = {"world_state": {"economic_status": "recession"}}, template needs {world_state.economic_status}
        # If context = {"economic_status": "recession"}, template can use {economic_status}
        # The WorldEventTriggerSystem currently puts world state items directly in event.context.
        # For RANDOM_FROM_LIST, you might need to pre-process it or extend TemplateProcessor.
        # Quick hack for RANDOM_FROM_LIST:
        if "active_global_threats" in combined_context and isinstance(combined_context["active_global_threats"], list) and combined_context["active_global_threats"]:
            import random
            combined_context["RANDOM_FROM_LIST_active_global_threats"] = random.choice(combined_context["active_global_threats"])
            template = template.replace("{RANDOM_FROM_LIST[context.active_global_threats]}", "{RANDOM_FROM_LIST_active_global_threats}")


        return self.tp.process(template, combined_context)

    def generate(self, event_type: Union[str, EventType], context: dict, char_context: Optional[dict] = None) -> str:
        """
        Generates a narrative string for a given event type and context.
        char_context is optional context for the primary character experiencing/observing.
        """
        key = event_type if isinstance(event_type, str) else getattr(event_type, "name", str(event_type))
        
        templates_for_event = self.templates.get(key)
        if not templates_for_event:
            # Fallback for unknown event types or missing templates
            actor_name = context.get("actor", "Someone")
            if isinstance(actor_name, dict): # If actor is a context dict itself
                actor_name = actor_name.get("name", "Someone")
            return f"{actor_name} experiences an event of type '{key}' with context: {context.get('summary', str(context))}"

        import random
        template = random.choice(templates_for_event)
        
        # The `context` here is the GameEvent.context, which WorldEventTriggerSystem
        # will populate with relevant world state data.
        return self.fill_template(template, context, char_context)
