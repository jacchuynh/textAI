from typing import Dict, List, Tuple, Set, Any, Optional
from ..shared.models import Tag, TagCategory, DomainType

# Tag keywords dictionary for automatic tag detection
tag_keywords = {
    # ⚒️ Crafting & Professions
    "blacksmith": ["forge", "anvil", "hammer", "iron", "temper", "ingot", "metal"],
    "tailoring": ["sew", "needle", "thread", "fabric", "cloth", "weave"],
    "alchemy": ["brew", "bottle", "herb", "mortar", "vial", "distill", "essence", "transmute", "catalyst", "reaction", "balance"],
    "enchanting": ["inscribe", "rune", "infuse", "aura", "sigil", "embed"],
    "cooking": ["cook", "bake", "roast", "simmer", "knife", "pot", "spice", "ingredient", "recipe"],
    "trapmaking": ["tripwire", "spring", "trigger", "trap", "mechanism", "camouflage"],

    # 🔮 Arcane Tags & Magic Schools
    "elemental": ["flame", "burn", "ignite", "heat", "ember", "scorch", "frost", "freeze", "cold", "chill", "spark", "shock", "bolt"],
    "divination": ["foresee", "vision", "predict", "scry", "glimpse", "future"],
    "illusion": ["mirror", "fake", "phantom", "glimmer", "blur"],
    
    # Combat Tags
    "melee": ["sword", "dagger", "axe", "mace", "strike", "slash", "block", "parry", "stab", "thrust", "swing"],
    "archery": ["bow", "arrow", "quiver", "shoot", "aim", "nock", "draw", "release", "trajectory"],
    "tactics": ["plan", "strategy", "formation", "command", "maneuver", "flank", "position"],

    # 🧠 Academic / Support
    "research": ["study", "observe", "experiment", "theory", "archive"],
    "investigation": ["search", "inspect", "clue", "track", "follow", "deduce"],
    
    # 🗣️ Social Interaction
    "persuasion": ["convince", "coax", "influence", "plea", "motivate"],
    "intimidation": ["threaten", "scare", "frighten", "bully", "force", "menace", "intimidate"],
    "deception": ["lie", "fake", "mislead", "bluff", "mask", "trick", "deceive"],
    
    # Kingdom Management
    "leadership": ["inspire", "motivate", "direct", "guide", "vision", "resolve"],
    "economics": ["trade", "coin", "market", "profit", "budget", "expense", "revenue", "invest"],
    "politics": ["negotiate", "alliance", "faction", "treaty", "diplomacy", "influence", "power"]
}


def auto_tag_action(text: str) -> List[Tuple[str, int]]:
    """Tag an action based on text description
    
    Args:
        text: The text to analyze for tags
        
    Returns:
        List of (tag_name, score) tuples sorted by score
    """
    tag_scores = {}
    text_lower = text.lower()
    
    for tag, keywords in tag_keywords.items():
        score = sum(1 for word in keywords if word in text_lower)
        if score > 0:
            tag_scores[tag] = score
    
    return sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)


def suggest_domain_and_tag(text: str, available_tags: Dict[str, Tag]) -> Tuple[DomainType, Optional[str], float]:
    """Suggest the most appropriate domain and tag for an action
    
    Args:
        text: The action text to analyze
        available_tags: Dictionary of available tags
        
    Returns:
        Tuple of (domain_type, tag_name, confidence)
    """
    # Get tag suggestions
    suggested_tags = auto_tag_action(text)
    
    if not suggested_tags:
        # Default to social domain with no specific tag if no matches
        return DomainType.SOCIAL, None, 0.0
    
    # Get the highest scoring tag that exists in available_tags
    best_tag_name = None
    best_score = 0
    
    for tag_name, score in suggested_tags:
        if tag_name in available_tags and score > best_score:
            best_tag_name = tag_name
            best_score = score
    
    # If we found a valid tag, use its primary domain
    if best_tag_name:
        tag = available_tags[best_tag_name]
        primary_domain = tag.domains[0] if tag.domains else DomainType.SOCIAL
        confidence = min(1.0, best_score / 3)  # Normalize confidence score
        return primary_domain, best_tag_name, confidence
    
    # Otherwise, infer domain from keywords
    domain_keywords = {
        DomainType.BODY: ["strength", "endurance", "physical", "muscle", "run", "climb", "jump", "fight"],
        DomainType.MIND: ["think", "solve", "calculate", "study", "remember", "analyze", "deduce"],
        DomainType.SPIRIT: ["pray", "meditate", "faith", "spiritual", "inner", "will", "belief"],
        DomainType.SOCIAL: ["talk", "speak", "charm", "convince", "negotiate", "diplomat", "interact"],
        DomainType.CRAFT: ["make", "build", "craft", "construct", "repair", "create", "design"],
        DomainType.AUTHORITY: ["command", "lead", "direct", "rule", "govern", "manage", "order"],
        DomainType.AWARENESS: ["notice", "spot", "detect", "perceive", "sense", "feel", "observe"]
    }
    
    domain_scores = {}
    for domain, keywords in domain_keywords.items():
        score = sum(1 for word in keywords if word in text.lower())
        domain_scores[domain] = score
    
    # Get the highest scoring domain
    best_domain = max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else DomainType.SOCIAL
    confidence = min(1.0, domain_scores.get(best_domain, 0) / 3)
    
    return best_domain, None, confidence