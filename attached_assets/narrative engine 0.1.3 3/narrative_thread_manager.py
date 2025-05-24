from datetime import datetime

class NarrativeThreadManager:
    def __init__(self, context, director):
        self.context = context
        self.director = director

    def handle_branch_created(self, event):
        branch_id = event.context.get("branch_id")
        branch = self.director.active_branches.get(branch_id)
        thread_data = {
            "id": f"thread_{branch_id}",
            "title": branch.get("name"),
            "description": branch.get("description"),
            "type": "branch_thread",
            "priority": 5,
            "involved_characters": [event.actor],
            "resolved": False,
            "linked_branch": branch_id,
            "progress": 0,
            "status": "active",
            "created_at": event.timestamp,
            "duration": branch.get("duration", None)
        }
        self.context.add_narrative_thread(thread_data["id"], thread_data)

    def tick(self):
        self.context.tick()