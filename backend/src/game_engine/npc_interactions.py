import os
import json
import requests
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

from ..shared.models import Character, DomainType
from .shadow_profile import ShadowProfile

# NPC bias definitions - would typically come from a database
npc_biases = {
    "Thane Bren": {"authority": 2, "social": -1, "craft": 1},
    "Acolyte Sera": {"spirit": 3, "mind": 2, "body": -1},
    "Master Forge": {"craft": 3, "mind": 1, "spirit": -1},
    "Captain Vessa": {"body": 2, "awareness": 2, "social": 1},
    "Scholar Tarn": {"mind": 3, "spirit": 1, "body": -2},
    "Merchant Doran": {"social": 3, "craft": 1, "authority": -1},
    "Huntress Iyara": {"awareness": 3, "body": 2, "social": -1},
    "Lord Blackthorn": {"authority": 3, "social": 2, "spirit": -2}
}

# Personality traits associated with each domain
domain_traits = {
    DomainType.BODY: ["physical", "resilient", "strong", "athletic"],
    DomainType.MIND: ["intelligent", "analytical", "studious", "curious"],
    DomainType.SPIRIT: ["faithful", "intuitive", "wise", "spiritual"],
    DomainType.SOCIAL: ["charming", "persuasive", "diplomatic", "charismatic"],
    DomainType.CRAFT: ["creative", "practical", "resourceful", "skilled"],
    DomainType.AUTHORITY: ["commanding", "decisive", "strategic", "resolute"],
    DomainType.AWARENESS: ["perceptive", "attentive", "sharp-eyed", "vigilant"]
}


def get_dominant_domains(profile: ShadowProfile, top_n: int = 2) -> List[DomainType]:
    """Get the most dominant domains from a shadow profile
    
    Args:
        profile: The shadow profile to analyze
        top_n: Number of top domains to return
        
    Returns:
        List of dominant domain types
    """
    dominant = profile.get_dominant_domains(top_n)
    return [domain for domain, _ in dominant]


def calculate_npc_affinity(npc_name: str, profile: ShadowProfile) -> int:
    """Calculate an NPC's affinity toward a character based on domain usage
    
    Args:
        npc_name: Name of the NPC
        profile: Shadow profile of the character
        
    Returns:
        Affinity score (positive = like, negative = dislike)
    """
    if npc_name not in npc_biases:
        return 0
    
    npc_bias = npc_biases[npc_name]
    score = 0
    
    # Get normalized domain usage
    domain_usage = {}
    for domain, count in profile.domain_usage.items():
        domain_usage[domain.value] = count
    
    # Calculate weighted score
    for domain_name, bias in npc_bias.items():
        # Find matching domain
        for domain_type in DomainType:
            if domain_type.value == domain_name:
                usage = profile.domain_usage.get(domain_type, 0)
                weight = usage // 10  # More weight to active domains
                score += bias * max(1, weight)
    
    return score


def get_npc_reaction(npc_name: str, character_id: str, profile: ShadowProfile, 
                   recent_tag: Optional[str] = None) -> Dict[str, Any]:
    """Generate an NPC's reaction to a character based on their profile
    
    Args:
        npc_name: Name of the NPC
        character_id: ID of the character
        profile: Shadow profile of the character
        recent_tag: Optional recently used tag
        
    Returns:
        Dictionary with reaction details
    """
    # Get dominant domains
    dominant_domains = get_dominant_domains(profile)
    domain_names = [d.value for d in dominant_domains]
    
    # Calculate affinity
    affinity = calculate_npc_affinity(npc_name, profile)
    
    # Generate bias summary
    bias_summary = "neutral toward most people"
    if npc_name in npc_biases:
        likes = []
        dislikes = []
        for domain, score in npc_biases[npc_name].items():
            if score > 0:
                likes.append(domain)
            elif score < 0:
                dislikes.append(domain)
        
        if likes:
            bias_summary = f"respects those with {', '.join(likes)} traits"
        if dislikes:
            if likes:
                bias_summary += f" but distrusts those with {', '.join(dislikes)} traits"
            else:
                bias_summary = f"distrusts those with {', '.join(dislikes)} traits"
    
    # Generate reaction text using OpenRouter
    reaction_text = get_dynamic_npc_reply_openrouter(npc_name, domain_names, recent_tag, bias_summary)
    
    # Compile reaction details
    return {
        "npc": npc_name,
        "affinity": affinity,
        "dominant_domains": domain_names,
        "recent_tag": recent_tag,
        "bias_summary": bias_summary,
        "reaction": reaction_text,
        "timestamp": datetime.now().isoformat()
    }


def get_dynamic_npc_reply_openrouter(npc_name: str, dominant_domains: List[str], 
                                   tag: Optional[str], bias_summary: str,
                                   model: Optional[str] = None) -> str:
    """Generate dynamic NPC dialogue using OpenRouter API
    
    Args:
        npc_name: Name of the NPC
        dominant_domains: List of dominant domain names
        tag: Recently used tag or None
        bias_summary: Summary of NPC biases
        model: Optional model name to use
        
    Returns:
        Generated NPC dialogue
    """
    api_url = "https://openrouter.ai/api/v1/chat/completions"
    api_key = os.environ.get("OPENROUTER_API_KEY")
    
    if not api_key:
        return f"{npc_name} looks at you thoughtfully."
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://replit.com/",  # Required by OpenRouter
        "X-Title": "Chronicles RPG"
    }

    tag_text = f"Recently used Tag: [{tag}]" if tag else "No specific skill used recently"
    
    prompt = f"""
    You are roleplaying an NPC named "{npc_name}" in a fantasy world.

    This NPC is interacting with the player, whose dominant skills are:
    - Domains: {', '.join(dominant_domains)}
    - {tag_text}

    NPC Bias: {bias_summary}

    Generate a brief but immersive response. It can be:
    - Curious if the player's skill surprises them
    - Respectful if they admire that domain
    - Critical if they're biased negatively
    - Casual or humorous if it's fitting

    Style: In-character, 1–2 sentences, no narration—only the NPC speaking.
    """

    payload = {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.85,
        "max_tokens": 80
    }

    # Only include the model if explicitly provided
    if model:
        payload["model"] = model

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"OpenRouter API Error: {response.status_code} - {response.text}")
            return f"{npc_name} looks at you with interest but says nothing."
    except Exception as e:
        print(f"Error calling OpenRouter API: {str(e)}")
        return f"{npc_name} nods slowly, deep in thought."


def get_fallback_npc_reply(npc_name: str, dominant_domains: List[str], tag: Optional[str]) -> str:
    """Get a fallback NPC reply when API is unavailable
    
    Args:
        npc_name: Name of the NPC
        dominant_domains: List of dominant domain names
        tag: Recently used tag or None
        
    Returns:
        Fallback NPC dialogue
    """
    # Simple template responses based on domain combinations
    templates = {
        "body,craft": [
            "I can see the calluses on your hands. A hard worker, I appreciate that.",
            "You've the build of both warrior and craftsman. Rare combination."
        ],
        "body,authority": [
            "You carry yourself like a soldier who's used to giving orders.",
            "The way you stand... military background, I'd wager. And not just any grunt."
        ],
        "mind,spirit": [
            "There's wisdom in your eyes, both scholarly and... something deeper.",
            "Interesting... you've cultivated both intellect and spiritual awareness."
        ],
        "social,authority": [
            "You've got the silver tongue of a diplomat and the bearing of a leader.",
            "I can tell you're used to both commanding rooms and charming individuals."
        ],
        "mind,craft": [
            "An inventor's mind, I see. Theory and application in perfect balance.",
            "You approach problems with both scholarly rigor and practical ingenuity."
        ],
        "awareness,social": [
            "Nothing escapes your notice, does it? Including exactly what to say to whom.",
            "You're reading this room as easily as breathing. Impressive social awareness."
        ]
    }
    
    # Sort domains alphabetically to match template keys
    key = ",".join(sorted(dominant_domains[:2]))
    
    if key in templates:
        import random
        return random.choice(templates[key])
    
    # Generic fallbacks based on individual domains
    if dominant_domains:
        primary_domain = dominant_domains[0]
        if primary_domain == "body":
            return "You move with the confidence of someone who knows their physical capabilities."
        elif primary_domain == "mind":
            return "There's a calculating intelligence behind your eyes. Fascinating."
        elif primary_domain == "spirit":
            return "I sense an unusual spiritual strength about you. Interesting."
        elif primary_domain == "social":
            return "You've a way with words, don't you? I can tell already."
        elif primary_domain == "craft":
            return "Those are a creator's hands. What do you make with them, I wonder?"
        elif primary_domain == "authority":
            return "People naturally follow you, don't they? I can see why."
        elif primary_domain == "awareness":
            return "Nothing escapes your notice, does it? I feel quite... observed."
    
    return f"{npc_name} regards you with a measured gaze."