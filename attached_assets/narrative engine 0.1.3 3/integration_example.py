from template_processor_enhanced import TemplateProcessor
from narrative_context_manager import NarrativeContextManager
from world_state_skill_modifier import WorldStateSkillModifier
from ai_gm_dialogue_generator import AIGMDialogueGenerator
from enhanced_branch_definitions import get_enhanced_branch_definitions
from enhanced_domain_themes import get_enhanced_domain_themes
from enhanced_narrative_templates import get_enhanced_templates

# Example integration with the existing system
def example_usage(narrative_context, world_state_manager, event):
    """Example of how the systems integrate and work together."""
    
    # 1. Initialize our enhanced systems
    template_processor = TemplateProcessor()
    context_manager = NarrativeContextManager(narrative_context, world_state_manager)
    skill_modifier = WorldStateSkillModifier(world_state_manager)
    dialogue_generator = AIGMDialogueGenerator(template_processor)
    
    # 2. Prepare rich contextual data
    context = context_manager.prepare_event_context(
        event=event,
        actor_id="player_character_id",
        target_id="mountain_elder",
        location="mountain_peak"
    )
    
    # 3. Generate narrative for the event
    templates = get_enhanced_templates()
    location_entry_templates = templates.get("location_entry", [])
    
    if location_entry_templates:
        # Select a template and process it
        template = location_entry_templates[0]  # For example
        narrative = template_processor.process(template, context)
        print("NARRATIVE:")
        print(narrative)
        print()
        
    # 4. Apply world state effects to a skill check
    branch_definitions = get_enhanced_branch_definitions()
    trial_branch = branch_definitions.get("Trial_of_Might", {})
    if trial_branch:
        stage = trial_branch["stages"][2]  # The pillar lifting stage
        skill_check = stage.get("skill_check", {})
        
        modifier, reason = skill_modifier.calculate_difficulty_modifier(
            branch_definition=trial_branch,
            stage_definition=stage,
            skill_check=skill_check
        )
        
        print("SKILL CHECK MODIFICATION:")
        print(f"Base difficulty: {skill_check.get('difficulty', 10)}")
        print(f"Modifier: {modifier:+d} ({reason})")
        print(f"Final difficulty: {skill_check.get('difficulty', 10) + modifier}")
        print()
        
    # 5. Generate NPC dialogue based on themes
    mountain_elder_dialogue = dialogue_generator.generate_dialogue(
        npc_id="mountain_elder",
        dialogue_themes=["wisdom", "testing", "tradition"],
        context=context,
        player_id="player_character_id"
    )
    
    print("NPC DIALOGUE (Mountain Elder):")
    print(mountain_elder_dialogue)
    print()
    
    # 6. Show AI GM guidance for a branch stage
    if "ai_gm_guidance" in stage:
        print("AI GM GUIDANCE:")
        print(stage["ai_gm_guidance"])