RELATIONSHIP_IMPACT = {
    "COMBAT_ENDED": {"trust": 0.5, "respect": 0.5, "value": 1},
    "QUEST_COMPLETED": {"trust": 1, "value": 2},
    "TRANSACTION_COMPLETED": {"familiarity": 0.5, "value": 0.5}
}

class RelationshipSystem:
    def __init__(self, narrative_context):
        self.context = narrative_context

    def update_relationship(self, char_id, other_id, event):
        impacts = RELATIONSHIP_IMPACT.get(event.type, {})
        self.context.update_relationship(char_id, other_id, event, impacts)