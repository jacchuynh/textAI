"""
Enhanced domain themes that respond to world state and character contexts.
"""
from enum import Enum
from typing import Dict, List, Any, Tuple

from .world_state import EconomicStatus, PoliticalStability

class NarrativeBranchType(Enum):
    DOMAIN_OPPORTUNITY = "domain_opportunity"
    DOMAIN_CHALLENGE = "domain_challenge"  
    DOMAIN_GROWTH = "domain_growth"
    CHARACTER_ARC = "character_arc"
    RELATIONSHIP = "relationship"
    WORLD_IMPACT = "world_impact"
    WORLD_STATE_RESPONSE = "world_state_response"

def get_enhanced_domain_themes() -> Dict[Tuple[str, str], Dict[str, Any]]:
    """
    Returns a comprehensive dictionary of domain pairings and their narrative themes.
    Each theme contains multiple branch opportunities that are sensitive to world state.
    """
    return {
        # Physical Domains
        ("STRENGTH", "ENDURANCE"): {
            "name": "Physical Prowess",
            "description": "Mastery over physical challenges through raw power and stamina.",
            "recommended_tones": ["HEROIC", "GRIM"],
            "branch_opportunities": [
                {
                    "name": "Trial_of_Might",
                    "type": NarrativeBranchType.DOMAIN_CHALLENGE,
                    "description": "A grueling physical challenge that tests the limits of strength and endurance.",
                    "min_domain_value": 3,
                    "ai_gm_hooks": [
                        "The stone monolith stands immovable, its surface bearing ancient markings that seem to dare anyone to prove their strength.",
                        "Tales speak of warriors who have broken themselves against the mountain path, yet those who conquer it gain legendary status.",
                        "The elder watches you with weathered eyes, silently assessing whether you have what it takes to attempt the trial."
                    ]
                },
                {
                    "name": "Survivors_Crisis",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "When disaster strikes, your physical prowess becomes essential for rescue and survival efforts.",
                    "min_domain_value": 2,
                    "world_state_conditions": {
                        "economic_status": [EconomicStatus.DEPRESSION.value, EconomicStatus.RECESSION.value],
                        "active_global_threats": True  # Requires any active threat
                    },
                    "ai_gm_hooks": [
                        "The collapsed building groans, and desperate cries echo from within. Few have the strength to move the debris.",
                        "The supply caravan needs protection through bandit territory, and only the physically capable are being recruited.",
                        "As resources grow scarce, those with the endurance to venture into the wilderness become invaluable."
                    ]
                },
                {
                    "name": "Championship_Circuit",
                    "type": NarrativeBranchType.CHARACTER_ARC,
                    "description": "Rise through competitive physical contests to become a renowned champion.",
                    "min_domain_value": 4,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.PEACEFUL.value, PoliticalStability.STABLE.value],
                        "economic_status": [EconomicStatus.STABLE.value, EconomicStatus.BOOM.value]
                    },
                    "ai_gm_hooks": [
                        "The tournament crier reads the names of champions past. The crowd waits to see who will join their ranks.",
                        "A scout from the championship circuit eyes your physique appraisingly as you demonstrate your strength.",
                        "Flyers announcing the seasonal games are posted throughout town. The prize purse is substantial this year."
                    ]
                }
            ]
        },
        
        # Mental Domains
        ("INTELLECT", "PERCEPTION"): {
            "name": "Keen Observer",
            "description": "Uncovering hidden truths through mental acuity and sharp senses.",
            "recommended_tones": ["MYSTERIOUS", "ANALYTICAL"],
            "branch_opportunities": [
                {
                    "name": "Unsolved_Mystery",
                    "type": NarrativeBranchType.DOMAIN_OPPORTUNITY,
                    "description": "A perplexing case or mystery that others have failed to crack.",
                    "min_domain_value": 3,
                    "ai_gm_hooks": [
                        "The constable looks defeated, shuffling through notes on a case that's gone cold. He glances up as you enter.",
                        "Whispers of strange occurrences have been spreading. Most dismiss them as superstition, but you notice patterns others don't.",
                        "An intricate puzzle box sits abandoned on a scholar's desk. A note beside it declares it 'unsolvable'."
                    ]
                },
                {
                    "name": "Political_Intrigue",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Navigate a web of political deception where perception and intellect are your only reliable allies.",
                    "min_domain_value": 4,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.UNREST.value, PoliticalStability.REBELLION.value]
                    },
                    "ai_gm_hooks": [
                        "The courier delivers a sealed message. Within is an invitation to a gathering where words are weapons and secrets are currency.",
                        "Court advisors speak with carefully chosen words, but their subtle glances convey volumes to the attentive observer.",
                        "A political treatise circulates among the educated elite. Between its lines lie coded messages about coming upheaval."
                    ]
                },
                {
                    "name": "Arcane_Research",
                    "type": NarrativeBranchType.DOMAIN_GROWTH,
                    "description": "Dive into forbidden knowledge and arcane research that requires both intellect and careful observation.",
                    "min_domain_value": 3,
                    "ai_gm_hooks": [
                        "The ancient tome's script shifts before your eyes, as if testing whether you're worthy of its secrets.",
                        "Strange energies emanate from the forgotten ruin, detected only by those with sufficiently tuned senses.",
                        "The eccentric scholar's notes appear nonsensical at first glance, but patterns emerge when viewed with the right perspective."
                    ]
                }
            ]
        },
        
        # Social Domains
        ("CHARISMA", "MANIPULATION"): {
            "name": "Social Maestro",
            "description": "Mastery of social dynamics, from genuine leadership to subtle manipulation.",
            "recommended_tones": ["DRAMATIC", "INTRIGUE"],
            "branch_opportunities": [
                {
                    "name": "Rise_to_Power",
                    "type": NarrativeBranchType.CHARACTER_ARC,
                    "description": "Climb the social and political ladder to a position of significant influence.",
                    "min_domain_value": 4,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.STABLE.value, PoliticalStability.UNREST.value]
                    },
                    "ai_gm_hooks": [
                        "The council seat lies vacant after the previous occupant's fall from grace. Ambitious eyes turn toward it.",
                        "Factions seek figureheads who can sway public opinion. Your reputation has not gone unnoticed.",
                        "The aging noble makes a point to introduce you around at the gathering. This is no mere courtesy."
                    ]
                },
                {
                    "name": "Black_Market_Network",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Establish connections in the underground economy that flourishes during hardship.",
                    "min_domain_value": 3,
                    "world_state_conditions": {
                        "economic_status": [EconomicStatus.RECESSION.value, EconomicStatus.DEPRESSION.value]
                    },
                    "ai_gm_hooks": [
                        "The shopkeeper's smile fades as he sizes you up, then he quietly mentions having 'other wares' for discerning customers.",
                        "A cryptic symbol chalked on the alley wall would mean nothing to most, but to those in the know, it signifies opportunity.",
                        "The tavern falls silent as you enter. After a moment, a figure in the corner raises a glass in subtle acknowledgment."
                    ]
                },
                {
                    "name": "Diplomatic_Mission",
                    "type": NarrativeBranchType.WORLD_IMPACT,
                    "description": "Serve as an envoy in delicate negotiations that could avert conflict.",
                    "min_domain_value": 5,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.UNREST.value, PoliticalStability.WAR.value]
                    },
                    "ai_gm_hooks": [
                        "The sealed missive bears the highest authority's mark. Inside are instructions for a mission requiring the utmost discretion.",
                        "Representatives from opposing factions sit in tense silence. They await a neutral mediator respected by both sides.",
                        "War drums sound in the distance while councilors debate. A skilled negotiator could still find a path to peace."
                    ]
                }
            ]
        },
        
        # Survival & Adaptability
        ("AWARENESS", "SURVIVAL"): {
            "name": "Wilderness Wayfinder",
            "description": "Mastery of natural environments and survival against the elements.",
            "recommended_tones": ["PRIMAL", "SERENE"],
            "branch_opportunities": [
                {
                    "name": "Lost_Expedition",
                    "type": NarrativeBranchType.DOMAIN_CHALLENGE,
                    "description": "Track and rescue a missing expedition in treacherous wilderness.",
                    "min_domain_value": 3,
                    "ai_gm_hooks": [
                        "Weathered parchment outlines the last known route of the expedition. No one else has dared follow their trail.",
                        "A lone survivor stumbles into town, feverish and babbling about companions left behind in uncharted territory.",
                        "The tracker shakes his head and turns back. 'This is beyond my skills now,' he admits, looking at you meaningfully."
                    ]
                },
                {
                    "name": "Seasonal_Crisis",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Help communities prepare for or recover from seasonal disasters.",
                    "min_domain_value": 2,
                    "world_state_conditions": {
                        "current_season": ["winter", "flood_season"] # Example seasons that might trigger this
                    },
                    "ai_gm_hooks": [
                        "Frost creeps earlier than expected into the region. The harvest isn't complete, and preparations are insufficient.",
                        "Rising waters threaten the lowland settlements. Someone with wilderness knowledge could identify safe routes and resources.",
                        "Game has grown scarce near the village. Without alternative food sources, winter will bring starvation."
                    ]
                },
                {
                    "name": "Frontier_Pathfinder",
                    "type": NarrativeBranchType.CHARACTER_ARC,
                    "description": "Become renowned for opening safe passages through dangerous territories.",
                    "min_domain_value": 4,
                    "ai_gm_hooks": [
                        "Merchants gather around maps of treacherous mountain passes, discussing the fortune awaiting someone who finds a safer route.",
                        "The frontier settlement's growth is stunted by isolation. Their leader seeks someone to establish reliable pathways.",
                        "Ancient markers hint at forgotten roads through what is now considered impassable wilderness."
                    ]
                }
            ]
        },
        
        # Crafting & Creation
        ("CRAFTING", "INTELLECT"): {
            "name": "Master Artificer",
            "description": "Creating works that blend technical skill with innovation and insight.",
            "recommended_tones": ["CREATIVE", "METHODICAL"],
            "branch_opportunities": [
                {
                    "name": "Revolutionary_Design",
                    "type": NarrativeBranchType.DOMAIN_GROWTH,
                    "description": "Develop a groundbreaking invention or technique that solves a significant problem.",
                    "min_domain_value": 4,
                    "ai_gm_hooks": [
                        "The guild master presents a seemingly impossible commission, one that has defeated all previous artisans.",
                        "A brilliant but impractical design needs refinement to become viable. Its creator seeks a collaborator with both vision and skill.",
                        "Unusual materials with extraordinary properties arrive from distant lands, inspiring new crafting possibilities."
                    ]
                },
                {
                    "name": "Wartime_Production",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Your crafting skills become vital for military efforts during conflict.",
                    "min_domain_value": 3,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.WAR.value]
                    },
                    "ai_gm_hooks": [
                        "Military officers review diagrams of siege equipment. They need someone who can turn plans into reality.",
                        "Wounded soldiers pour in with damaged armor and weapons. The standard blacksmiths cannot keep pace with repairs.",
                        "A commander seeks unconventional weapons to break the stalemate, looking to craftsmen with innovative minds."
                    ]
                },
                {
                    "name": "Economic_Innovation",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Create new products or production methods to revitalize a struggling economy.",
                    "min_domain_value": 3,
                    "world_state_conditions": {
                        "economic_status": [EconomicStatus.RECESSION.value, EconomicStatus.DEPRESSION.value]
                    },
                    "ai_gm_hooks": [
                        "The once-bustling workshop district stands nearly abandoned, tools gathering dust while craftsmen beg in the streets.",
                        "Merchants discuss the shortage of affordable goods as raw materials grow increasingly scarce or expensive.",
                        "A struggling guildmaster offers partnership to anyone who can help modernize their outdated production methods."
                    ]
                }
            ]
        },
        
        # Leadership & Strategy
        ("LEADERSHIP", "TACTICS"): {
            "name": "Mastermind Commander",
            "description": "Exceptional ability to lead groups and devise winning strategies.",
            "recommended_tones": ["COMMANDING", "CALCULATED"],
            "branch_opportunities": [
                {
                    "name": "Militia_Formation",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Organize and train local defense forces during times of danger.",
                    "min_domain_value": 2,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.UNREST.value, PoliticalStability.REBELLION.value, PoliticalStability.WAR.value],
                        "active_global_threats": True
                    },
                    "ai_gm_hooks": [
                        "Villagers argue chaotically about defense, each with different ideas but no one to organize them effectively.",
                        "The town guard is stretched thin, with untrained volunteers eagerly but clumsily attempting to fill the gaps.",
                        "A retired soldier approaches you, noting your air of authority: 'These people need leadership if they're going to survive.'"
                    ]
                },
                {
                    "name": "Strategic_Enterprise",
                    "type": NarrativeBranchType.DOMAIN_OPPORTUNITY,
                    "description": "Apply tactical thinking to business or civil planning for exceptional results.",
                    "min_domain_value": 3,
                    "world_state_conditions": {
                        "economic_status": [EconomicStatus.STABLE.value, EconomicStatus.BOOM.value]
                    },
                    "ai_gm_hooks": [
                        "Competing merchant guilds create market inefficiencies. Someone with strategic vision could unify and streamline operations.",
                        "The city's expansion is occurring haphazardly, creating problems that a planned approach could avoid.",
                        "Investors seek a coordinator for a complex venture spanning multiple industries and regions."
                    ]
                },
                {
                    "name": "Legendary_Command",
                    "type": NarrativeBranchType.CHARACTER_ARC,
                    "description": "Rise to a position of significant military or organizational leadership.",
                    "min_domain_value": 5,
                    "ai_gm_hooks": [
                        "The aging commander watches you drill troops, nodding with approval and later asking about your longer-term ambitions.",
                        "Your reputation for effective leadership has spread. A summons arrives from authorities seeking to elevate your position.",
                        "Crisis leaves a power vacuum in the command structure. Subordinates already look to you for guidance despite your current rank."
                    ]
                }
            ]
        },
        
        # Knowledge & Secrecy
        ("LORE", "DECEPTION"): {
            "name": "Shadow Scholar",
            "description": "Mastery of forbidden knowledge and the art of keeping secrets.",
            "recommended_tones": ["MYSTERIOUS", "OMINOUS"],
            "branch_opportunities": [
                {
                    "name": "Forbidden_Texts",
                    "type": NarrativeBranchType.DOMAIN_OPPORTUNITY,
                    "description": "Discover and decipher dangerous knowledge that must be carefully controlled.",
                    "min_domain_value": 4,
                    "ai_gm_hooks": [
                        "The librarian nervously checks if anyone is watching before leading you to a hidden section behind a false bookshelf.",
                        "Scattered pages of an ancient manuscript appear innocuous, but contain subtle ciphers indicating far more dangerous content.",
                        "Strange symbols begin appearing in your dreams after encountering an unusual artifact, compelling you to seek their meaning."
                    ]
                },
                {
                    "name": "Information_Network",
                    "type": NarrativeBranchType.WORLD_STATE_RESPONSE,
                    "description": "Establish a covert network for gathering and controlling sensitive information during turbulent times.",
                    "min_domain_value": 3,
                    "world_state_conditions": {
                        "political_stability": [PoliticalStability.UNREST.value, PoliticalStability.REBELLION.value]
                    },
                    "ai_gm_hooks": [
                        "A stranger passes you a note with a symbol matching one you've seen in restricted texts, along with an address and time.",
                        "Former colleagues have gone missing after researching sensitive topics. Their hidden notes suggest they foresaw trouble.",
                        "Authorities have begun censoring and confiscating certain materials. A resistance forms among scholars and knowledge-keepers."
                    ]
                },
                {
                    "name": "Truth_Seeker",
                    "type": NarrativeBranchType.CHARACTER_ARC,
                    "description": "Embark on a personal quest to uncover reality behind carefully constructed falsehoods.",
                    "min_domain_value": 4,
                    "ai_gm_hooks": [
                        "The dying sage whispers, 'Everything you know is built on lies,' and presses an enigmatic key into your hand.",
                        "Historical accounts contain subtle contradictions that most overlook, but form a pattern suggesting deliberate revision.",
                        "A prophetic text describes events matching current affairs, but was supposedly written centuries ago and hidden."
                    ]
                }
            ]
        }
    }