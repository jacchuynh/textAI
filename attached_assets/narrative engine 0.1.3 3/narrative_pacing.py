import time

class NarrativePacingController:
    """
    Controls pacing: cooldowns, quotas, prioritization.
    All values are configurable per event type.
    """

    def __init__(self, config=None):
        self.type_cooldowns = (config or {}).get("type_cooldowns", {})
        self.global_cooldown = (config or {}).get("global_cooldown", 300)
        self.event_priorities = (config or {}).get("event_priorities", {})
        self.quotas = (config or {}).get("quotas", {
            "hourly": 12,
            "location": 3,
            "character": 5
        })
        self.last_narrative = {}
        self.narrative_counters = {"hourly": [], "location": {}, "character": {}}

    def should_generate(self, event_type, actor, location):
        now = time.time()
        etype = event_type if isinstance(event_type, str) else getattr(event_type, "name", str(event_type))

        cooldown = self.type_cooldowns.get(etype, self.global_cooldown)
        if etype in self.last_narrative and now - self.last_narrative[etype] < cooldown:
            return False

        # Hourly quota
        self.narrative_counters["hourly"] = [t for t in self.narrative_counters["hourly"] if now - t < 3600]
        if len(self.narrative_counters["hourly"]) >= self.quotas["hourly"]:
            if self.event_priorities.get(etype, 0) < 8:
                return False

        # Location quota
        loc_q = self.narrative_counters["location"].setdefault(location, 0)
        if loc_q >= self.quotas["location"]:
            if self.event_priorities.get(etype, 0) < 7:
                return False

        # Character quota
        hour_key = f"{actor}_{int(now/3600)}"
        char_q = self.narrative_counters["character"].setdefault(hour_key, 0)
        if char_q >= self.quotas["character"]:
            if self.event_priorities.get(etype, 0) < 6:
                return False

        # Passed all checks, update state
        self.last_narrative[etype] = now
        self.narrative_counters["hourly"].append(now)
        self.narrative_counters["location"][location] += 1
        self.narrative_counters["character"][hour_key] += 1
        return True