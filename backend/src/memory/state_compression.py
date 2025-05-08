"""
State compression utilities for game state management.

This module provides utilities for:
1. Compressing game state for efficient storage and transmission
2. Summarizing large game state objects into concise representations
3. Creating prioritized state snapshots for relevant context
"""
from typing import Dict, List, Any, Optional, Set, Union, Tuple
from datetime import datetime
import json
import re

# Import shared models
from ..shared.models import (
    Character, Location, NPC, Domain, DomainType, GrowthTier, Tag,
    InventoryItem, Quest
)


class StateCompressor:
    """
    Utility for compressing and summarizing game state information.
    
    This class provides methods for:
    - Summarizing characters
    - Summarizing locations
    - Summarizing NPCs
    - Compressing inventory
    - Prioritizing state elements based on relevance
    """
    
    @staticmethod
    def summarize_character(character: Character, detail_level: str = "medium") -> Dict[str, Any]:
        """
        Create a summary of a character.
        
        Args:
            character: The character to summarize
            detail_level: Amount of detail ("low", "medium", "high")
            
        Returns:
            Summary dictionary
        """
        # Base summary - always included
        summary = {
            "id": str(character.id),
            "name": character.name,
            "class": character.class_name if hasattr(character, "class_name") else character.class_,
            "level": character.level,
            "health": f"{character.current_health}/{character.max_health}"
        }
        
        # Add more details based on detail level
        if detail_level in ["medium", "high"]:
            # Get dominant domains (top 3)
            dominant_domains = []
            if character.domains:
                domain_values = [
                    (domain_type, domain.value)
                    for domain_type, domain in character.domains.items()
                ]
                domain_values.sort(key=lambda x: x[1], reverse=True)
                dominant_domains = [
                    {"type": d[0].value, "value": d[1], 
                     "tier": StateCompressor._get_tier_name(d[1])}
                    for d in domain_values[:3]
                ]
            
            summary.update({
                "background": character.background,
                "dominant_domains": dominant_domains
            })
            
            # Add character stats
            if hasattr(character, "stats"):
                summary["stats"] = {
                    k: v for k, v in character.stats.__dict__.items()
                    if not k.startswith("_")
                }
        
        # Add full details for high detail level
        if detail_level == "high":
            # Add all domains
            if character.domains:
                summary["domains"] = {
                    domain_type.value: {
                        "value": domain.value,
                        "tier": StateCompressor._get_tier_name(domain.value),
                        "growth_points": domain.growth_points,
                        "growth_required": domain.growth_required,
                        "usage_count": domain.usage_count
                    }
                    for domain_type, domain in character.domains.items()
                }
            
            # Add top 5 tags (by rank)
            if character.tags:
                tag_list = list(character.tags.values())
                tag_list.sort(key=lambda x: x.rank, reverse=True)
                summary["top_tags"] = [
                    {
                        "name": tag.name,
                        "rank": tag.rank,
                        "category": tag.category.value
                    }
                    for tag in tag_list[:5]
                ]
                
            # Add shadow profile summary if available
            if hasattr(character, "shadow_profile") and character.shadow_profile:
                summary["shadow_profile"] = {
                    "dominant_domains": StateCompressor._get_dominant_domains(
                        character.shadow_profile.domain_usage, 3
                    ),
                    "recent_tags": character.shadow_profile.recent_tags[:5] if character.shadow_profile.recent_tags else []
                }
        
        return summary
    
    @staticmethod
    def _get_tier_name(value: int) -> str:
        """Get the growth tier name for a domain value."""
        if value <= 2:
            return "Novice"
        elif value <= 4:
            return "Skilled"
        elif value <= 7:
            return "Expert"
        elif value <= 9:
            return "Master"
        else:
            return "Paragon"
    
    @staticmethod
    def _get_dominant_domains(domain_usage: Dict[DomainType, int], top_n: int = 3) -> List[Dict[str, Any]]:
        """Get the dominant domains from usage stats."""
        if not domain_usage:
            return []
            
        # Sort domains by usage
        sorted_domains = sorted(
            [(domain_type, count) for domain_type, count in domain_usage.items()],
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Take top N
        return [
            {"type": domain_type.value, "usage_count": count}
            for domain_type, count in sorted_domains[:top_n]
        ]
    
    @staticmethod
    def summarize_location(location: Location, include_npcs: bool = True) -> Dict[str, Any]:
        """
        Create a summary of a location.
        
        Args:
            location: The location to summarize
            include_npcs: Whether to include NPC summaries
            
        Returns:
            Summary dictionary
        """
        # Base location summary
        summary = {
            "id": location.id,
            "name": location.name,
            "type": location.type,
        }
        
        # Add a shorter description (first paragraph or 200 chars)
        if location.description:
            # Try to get the first paragraph
            paragraphs = location.description.split("\n\n")
            short_desc = paragraphs[0]
            
            # Truncate if still too long
            if len(short_desc) > 200:
                short_desc = short_desc[:197] + "..."
                
            summary["description"] = short_desc
        
        # Add NPCs if requested
        if include_npcs and hasattr(location, "npcs") and location.npcs:
            summary["npcs"] = [
                StateCompressor.summarize_npc(npc, include_dialogue=False)
                for npc in location.npcs
            ]
            
        # Add connections if available
        if hasattr(location, "connections") and location.connections:
            summary["connections"] = location.connections
            
        return summary
    
    @staticmethod
    def summarize_npc(npc: NPC, include_dialogue: bool = False) -> Dict[str, Any]:
        """
        Create a summary of an NPC.
        
        Args:
            npc: The NPC to summarize
            include_dialogue: Whether to include dialogue options
            
        Returns:
            Summary dictionary
        """
        summary = {
            "id": npc.id,
            "name": npc.name,
            "attitude": npc.attitude
        }
        
        # Add a shorter description (first sentence or 100 chars)
        if npc.description:
            # Try to get the first sentence
            sentences = npc.description.split(". ")
            short_desc = sentences[0]
            
            # Truncate if still too long
            if len(short_desc) > 100:
                short_desc = short_desc[:97] + "..."
                
            summary["description"] = short_desc
            
        # Add dialogue if requested
        if include_dialogue and hasattr(npc, "dialogue") and npc.dialogue:
            # Just include entry IDs and text, not full response objects
            summary["dialogue"] = [
                {"id": entry.id, "text": entry.text}
                for entry in npc.dialogue[:3]  # Limit to first 3 entries
            ]
            
        # Add domain bias if available
        if hasattr(npc, "domain_bias") and npc.domain_bias:
            # Sort by bias value
            biases = sorted(
                [(domain, value) for domain, value in npc.domain_bias.items()],
                key=lambda x: abs(x[1]),
                reverse=True
            )
            
            # Take top 3 strongest biases
            summary["domain_bias"] = [
                {"domain": domain.value if hasattr(domain, "value") else str(domain), 
                 "value": value}
                for domain, value in biases[:3]
            ]
            
        # Add first encounter flag if available
        if hasattr(npc, "first_encounter"):
            summary["first_encounter"] = npc.first_encounter
            
        return summary
    
    @staticmethod
    def compress_inventory(inventory: List[InventoryItem], max_items: int = 10) -> Dict[str, Any]:
        """
        Create a compressed representation of inventory.
        
        Args:
            inventory: List of inventory items
            max_items: Maximum number of items to include
            
        Returns:
            Compressed inventory dictionary
        """
        if not inventory:
            return {"items": [], "total_items": 0, "total_weight": 0}
            
        # Sort items by importance (subjective ranking)
        def item_importance(item):
            # Weapons and armor are most important
            if "weapon" in item.type.lower() or "armor" in item.type.lower():
                return 100 + item.quantity
            # Quest items next
            elif "quest" in item.type.lower():
                return 90 + item.quantity
            # Consumables next
            elif "potion" in item.type.lower() or "food" in item.type.lower():
                return 80 + item.quantity
            # Consider quantity for other items
            else:
                return item.quantity
                
        sorted_items = sorted(inventory, key=item_importance, reverse=True)
        
        # Take most important items up to the limit
        important_items = sorted_items[:max_items]
        
        # Summarize the rest
        remaining_count = len(inventory) - len(important_items)
        total_weight = sum(item.weight * item.quantity for item in inventory)
        
        # Create compressed representation
        compressed = {
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "type": item.type
                }
                for item in important_items
            ],
            "total_items": len(inventory),
            "remaining_items": remaining_count,
            "total_weight": total_weight
        }
        
        return compressed
    
    @staticmethod
    def summarize_quests(quests: List[Quest], max_quests: int = 5) -> Dict[str, Any]:
        """
        Create a summary of quests.
        
        Args:
            quests: List of quests
            max_quests: Maximum number of quests to include
            
        Returns:
            Quest summary dictionary
        """
        if not quests:
            return {"active": [], "completed": [], "failed": []}
            
        # Separate by status
        active = [q for q in quests if q.status == "active"]
        completed = [q for q in quests if q.status == "completed"]
        failed = [q for q in quests if q.status == "failed"]
        
        # Prioritize active quests
        active_summaries = []
        for quest in active[:max_quests]:
            # Create a short summary of the quest
            description = quest.description
            if len(description) > 100:
                description = description[:97] + "..."
                
            active_summaries.append({
                "id": quest.id,
                "title": quest.title,
                "description": description
            })
            
        # Create minimal summaries of completed/failed quests
        completed_summaries = [
            {"id": quest.id, "title": quest.title}
            for quest in completed[:max(1, max_quests // 2)]
        ]
        
        failed_summaries = [
            {"id": quest.id, "title": quest.title}
            for quest in failed[:max(1, max_quests // 2)]
        ]
        
        # Create the summary structure
        summary = {
            "active": active_summaries,
            "completed": completed_summaries,
            "failed": failed_summaries,
            "total_active": len(active),
            "total_completed": len(completed),
            "total_failed": len(failed)
        }
        
        return summary
    
    @staticmethod
    def create_game_state_summary(game_state: Dict[str, Any], detail_level: str = "medium") -> Dict[str, Any]:
        """
        Create a summary of the entire game state.
        
        Args:
            game_state: The full game state
            detail_level: Amount of detail ("low", "medium", "high")
            
        Returns:
            Summarized game state
        """
        summary = {
            "game_id": game_state.get("game_id", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Summarize character
        if "character" in game_state and game_state["character"]:
            summary["character"] = StateCompressor.summarize_character(
                game_state["character"], detail_level
            )
            
        # Summarize current location
        if "location" in game_state and game_state["location"]:
            summary["location"] = StateCompressor.summarize_location(
                game_state["location"], include_npcs=True
            )
            
        # Compress inventory
        if "inventory" in game_state and game_state["inventory"]:
            max_items = 5 if detail_level == "low" else (10 if detail_level == "medium" else 20)
            summary["inventory"] = StateCompressor.compress_inventory(
                game_state["inventory"].get("items", []), max_items
            )
            
        # Summarize quests
        if "quests" in game_state and game_state["quests"]:
            max_quests = 3 if detail_level == "low" else (5 if detail_level == "medium" else 10)
            summary["quests"] = StateCompressor.summarize_quests(
                game_state["quests"], max_quests
            )
            
        # Add narrative content if available
        if "narrative_content" in game_state and game_state["narrative_content"]:
            # Truncate if too long
            content = game_state["narrative_content"]
            if len(content) > 300 and detail_level != "high":
                content = content[:297] + "..."
            summary["narrative_content"] = content
            
        return summary
    
    @staticmethod
    def create_narrative_state_summary(game_state: Dict[str, Any]) -> str:
        """
        Create a narrative summary of the game state for AI context.
        
        Args:
            game_state: The full game state
            
        Returns:
            Narrative summary text
        """
        lines = ["# Current Game State"]
        
        # Character summary
        if "character" in game_state and game_state["character"]:
            char = game_state["character"]
            lines.append("## Character")
            
            # Basic info
            lines.append(f"You are {char.name}, a level {char.level} {char.class_}.")
            
            # Health and stats
            lines.append(f"Health: {char.current_health}/{char.max_health}")
            if hasattr(char, "current_mana") and hasattr(char, "max_mana"):
                lines.append(f"Mana: {char.current_mana}/{char.max_mana}")
                
            # Domains
            if hasattr(char, "domains") and char.domains:
                lines.append("\n### Domains")
                domain_lines = []
                for domain_type, domain in char.domains.items():
                    tier = StateCompressor._get_tier_name(domain.value)
                    domain_lines.append(f"- {domain_type.value}: {domain.value} ({tier})")
                lines.extend(sorted(domain_lines))
                
            # Top tags/skills
            if hasattr(char, "tags") and char.tags:
                tag_list = list(char.tags.values())
                tag_list.sort(key=lambda x: x.rank, reverse=True)
                top_tags = tag_list[:5]
                
                if top_tags:
                    lines.append("\n### Top Skills")
                    for tag in top_tags:
                        lines.append(f"- {tag.name}: Rank {tag.rank}")
        
        # Location summary
        if "location" in game_state and game_state["location"]:
            loc = game_state["location"]
            lines.append("\n## Current Location")
            lines.append(f"You are in {loc.name}, a {loc.type}.")
            
            if loc.description:
                # Use first paragraph only
                desc = loc.description.split("\n\n")[0]
                lines.append(desc)
                
            # NPCs present
            if hasattr(loc, "npcs") and loc.npcs:
                lines.append("\nNPCs present:")
                for npc in loc.npcs:
                    attitude = ""
                    if hasattr(npc, "attitude"):
                        attitude = f" ({npc.attitude})"
                    lines.append(f"- {npc.name}{attitude}")
        
        # Inventory summary
        if "inventory" in game_state and game_state["inventory"] and game_state["inventory"].get("items"):
            inv = game_state["inventory"]
            items = inv.get("items", [])
            
            if items:
                lines.append("\n## Inventory Highlights")
                
                # Group similar items
                item_counts = {}
                for item in items:
                    key = item.type
                    if key not in item_counts:
                        item_counts[key] = []
                    item_counts[key].append(item)
                
                # List important items first, then summarize by type
                weapons = item_counts.get("weapon", []) + item_counts.get("Weapon", [])
                armor = item_counts.get("armor", []) + item_counts.get("Armor", [])
                
                # Important items
                important_items = weapons + armor
                if important_items:
                    for item in important_items:
                        lines.append(f"- {item.name} (equipped)")
                        
                # Summarize other items by type
                other_counts = {}
                for key, items in item_counts.items():
                    if key.lower() not in ["weapon", "armor"]:
                        count = sum(item.quantity for item in items)
                        other_counts[key] = count
                
                if other_counts:
                    for key, count in other_counts.items():
                        lines.append(f"- {count}x {key}")
        
        # Quest summary
        if "quests" in game_state and game_state["quests"]:
            quests = game_state["quests"]
            active_quests = [q for q in quests if q.status == "active"]
            
            if active_quests:
                lines.append("\n## Active Quests")
                for quest in active_quests[:3]:  # Top 3 active quests
                    lines.append(f"- {quest.title}")
        
        # Combat status
        if "combat" in game_state and game_state["combat"] and game_state["combat"].get("status") == "active":
            combat = game_state["combat"]
            lines.append("\n## Combat Status")
            enemy_name = combat.get("enemy", {}).get("name", "an enemy")
            enemy_health = combat.get("enemy", {}).get("current_health", 0)
            enemy_max_health = combat.get("enemy", {}).get("max_health", 0)
            
            lines.append(f"You are in combat with {enemy_name}!")
            lines.append(f"Enemy health: {enemy_health}/{enemy_max_health}")
            
            # Recent combat log
            if combat.get("log"):
                lines.append("\nRecent combat actions:")
                for entry in combat.get("log", [])[-3:]:
                    lines.append(f"- {entry}")
        
        return "\n".join(lines)


class PriorityStateQueue:
    """
    Priority queue for game state elements based on relevance and importance.
    
    This class manages which elements of the game state are most relevant 
    for a given context, and prioritizes them for inclusion in AI prompts.
    """
    
    def __init__(self, max_entries: int = 100):
        """
        Initialize the priority queue.
        
        Args:
            max_entries: Maximum number of entries to keep
        """
        self.entries: List[Dict[str, Any]] = []
        self.max_entries = max_entries
        self.entry_ids: Set[str] = set()
    
    def add_entry(self, 
                 id: str, 
                 content: str, 
                 category: str,
                 priority: float,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add an entry to the priority queue.
        
        Args:
            id: Unique identifier for this entry
            content: The content of the entry
            category: Category for grouping (character, location, etc)
            priority: Priority score (higher is more important)
            metadata: Additional data about the entry
        """
        # Don't add duplicate IDs
        if id in self.entry_ids:
            # Update existing entry instead
            for i, entry in enumerate(self.entries):
                if entry["id"] == id:
                    entry["priority"] = priority
                    entry["last_updated"] = datetime.utcnow().isoformat()
                    if metadata:
                        entry["metadata"] = metadata
                    break
            return
            
        # Create new entry
        entry = {
            "id": id,
            "content": content,
            "category": category,
            "priority": priority,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
            "last_updated": datetime.utcnow().isoformat(),
            "access_count": 0
        }
        
        # Add to queue and ID set
        self.entries.append(entry)
        self.entry_ids.add(id)
        
        # Sort by priority (descending)
        self.entries.sort(key=lambda x: x["priority"], reverse=True)
        
        # Trim if over capacity
        if len(self.entries) > self.max_entries:
            removed = self.entries.pop()
            self.entry_ids.remove(removed["id"])
    
    def get_entries(self, 
                   categories: Optional[List[str]] = None, 
                   min_priority: float = 0.0,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get entries from the priority queue.
        
        Args:
            categories: Optional categories to filter by
            min_priority: Minimum priority score
            limit: Maximum number of entries to return
            
        Returns:
            List of entries, sorted by priority
        """
        # Filter by category and priority
        filtered = self.entries
        
        if categories:
            filtered = [e for e in filtered if e["category"] in categories]
            
        if min_priority > 0:
            filtered = [e for e in filtered if e["priority"] >= min_priority]
            
        # Sort by priority
        filtered.sort(key=lambda x: x["priority"], reverse=True)
        
        # Apply limit
        if limit:
            filtered = filtered[:limit]
            
        # Update access counts
        for entry in filtered:
            entry["access_count"] += 1
            entry["last_accessed"] = datetime.utcnow().isoformat()
            
        return filtered
    
    def get_formatted_context(self, 
                             categories: Optional[List[str]] = None,
                             min_priority: float = 0.5,
                             limit: int = 10) -> str:
        """
        Get a formatted context string from the priority queue.
        
        Args:
            categories: Optional categories to filter by
            min_priority: Minimum priority score
            limit: Maximum number of entries to include
            
        Returns:
            Formatted context string
        """
        entries = self.get_entries(categories, min_priority, limit)
        
        if not entries:
            return ""
            
        # Group by category
        by_category = {}
        for entry in entries:
            category = entry["category"]
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(entry)
            
        # Format by category
        lines = ["# Important Context"]
        
        for category, entries in by_category.items():
            # Format category name
            category_name = category.replace("_", " ").title()
            lines.append(f"\n## {category_name}")
            
            for entry in entries:
                lines.append(f"- {entry['content']}")
                
        return "\n".join(lines)
    
    def clear(self) -> None:
        """Clear all entries from the queue."""
        self.entries = []
        self.entry_ids = set()
    
    def update_priorities(self) -> None:
        """
        Update priorities based on recency and access count.
        
        This method is used to decay old entries and boost frequently accessed ones.
        """
        now = datetime.utcnow()
        
        for entry in self.entries:
            # Parse the timestamp
            try:
                last_updated = datetime.fromisoformat(entry["last_updated"])
                age_days = (now - last_updated).days
            except:
                age_days = 0
                
            # Decay factor based on age (loses 10% per day, bottoms out at 50%)
            decay = max(0.5, 1.0 - (age_days * 0.1))
            
            # Boost factor based on access count (up to 20% boost)
            boost = min(0.2, entry["access_count"] * 0.02)
            
            # Update priority
            base_priority = entry["priority"]
            entry["priority"] = base_priority * decay * (1.0 + boost)
            
        # Re-sort by new priorities
        self.entries.sort(key=lambda x: x["priority"], reverse=True)