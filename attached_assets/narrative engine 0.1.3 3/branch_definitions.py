"""
Expanded branch definitions with rich narrative details for AI GM use.
"""
from typing import Dict, Any
from .world_state import EconomicStatus, PoliticalStability

def get_enhanced_branch_definitions() -> Dict[str, Dict[str, Any]]:
    """
    Returns a dictionary of detailed narrative branch definitions.
    Each branch contains rich implementation details, stage progression,
    and world state awareness for the AI GM to leverage.
    """
    return {
        "Trial_of_Might": {
            "name": "Trial of Might",
            "type": "DOMAIN_CHALLENGE",
            "description": "A grueling physical challenge that tests the limits of strength and endurance.",
            "domain": "STRENGTH",
            "min_domain_value": 3,
            "implementation": {
                "type": "skill_challenge_series",
                "required_checks": [
                    {"domain": "STRENGTH", "difficulty": 12, "description": "Lift the ancient stone pillar from its resting place."},
                    {"domain": "ENDURANCE", "difficulty": 10, "description": "Climb the treacherous mountain path without rest."},
                    {"domain": "STRENGTH", "difficulty": 14, "description": "Break through the sealed stone door at the summit."}
                ],
                "location": "mountain_peak",
                "npc_involvement": [
                    {
                        "id": "mountain_elder", 
                        "role": "guide",
                        "dialogue_themes": ["wisdom", "tradition", "testing", "worthiness"]
                    },
                    {
                        "id": "rival_warrior", 
                        "role": "competitor",
                        "dialogue_themes": ["challenge", "respect", "jealousy", "honor"]
                    }
                ],
                "rewards": [
                    {"type": "item", "id": "strength_amulet", "description": "The Amulet of Enduring Might, warm to the touch and thrumming with ancient power."},
                    {"type": "domain_xp", "domain": "STRENGTH", "amount": 50},
                    {"type": "reputation", "faction": "mountain_folk", "amount": 25}
                ]
            },
            "stages": [
                {
                    "progress": 0, 
                    "title": "The Legend Heard",
                    "description": "You've heard tales of the Trial of Might, where warriors prove their strength.",
                    "narrative_description": "Whispers speak of an ancient trial in the mountains where warriors test their strength against challenges left by giants of old. Those who succeed return changed, their physical prowess enhanced by mystical favor.",
                    "available_actions": [
                        "seek_information", "find_mountain_elder", "begin_journey"
                    ],
                    "ai_gm_guidance": "Introduce this branch through tavern tales, scrolls in a library, or a warrior showing unusual strength. The focus should be on legendary status achieved by completing the trial."
                },
                {
                    "progress": 25,
                    "title": "The Base of the Mountain",
                    "description": "You've arrived at the mountain where the Trial takes place.",
                    "narrative_description": "The imposing mountain looms before you, its peak shrouded in mist. At its base, ancient stone markers bear worn carvings of muscled figures performing feats of strength. The path upward is steep and foreboding.",
                    "available_actions": [
                        "meet_elder", "assess_path", "begin_climb", "observe_rival"
                    ],
                    "ai_gm_guidance": "Emphasize the atmosphere of challenge and ancient tradition. The mountain should feel imposing but not impossible. If the character has high PERCEPTION, they might notice hidden markers or paths."
                },
                {
                    "progress": 50,
                    "title": "The First Trial: The Pillar",
                    "description": "You face the first challenge: lifting an ancient stone pillar.",
                    "narrative_description": "In a flat clearing stands a cylindrical stone pillar, etched with runes that glow faintly at your approach. According to tradition, warriors must lift it from its resting place and hold it aloft to prove their strength.",
                    "available_actions": [
                        "attempt_lift", "study_technique", "prepare_body"
                    ],
                    "skill_check": {"domain": "STRENGTH", "difficulty": 12},
                    "success_text": "With muscles straining and veins standing out on your forehead, you gradually raise the impossibly heavy pillar. The runes glow brighter as you hold it aloft, acknowledging your strength.",
                    "failure_text": "Despite your best efforts, the pillar barely budges. You'll need to rest and try again, perhaps with better technique or preparation.",
                    "ai_gm_guidance": "This is a pivotal physical challenge. Describe the weight and ancient power of the pillar. If the character has relevant background (like blacksmithing or mining), let them draw on that experience."
                },
                {
                    "progress": 75,
                    "title": "The Mountain Path",
                    "description": "You must climb the grueling path to the summit without rest.",
                    "narrative_description": "The path grows steeper and more treacherous, with loose stones and narrow ledges. The air thins as you ascend, making each breath more difficult. According to the trial, you must reach the summit without stopping to rest.",
                    "available_actions": [
                        "steady_climb", "push_through_pain", "find_better_route"
                    ],
                    "skill_check": {"domain": "ENDURANCE", "difficulty": 10},
                    "success_text": "Though your legs burn and your lungs ache for proper breath, you maintain a steady pace up the mountain, never once stopping to rest. Your determination carries you ever upward.",
                    "failure_text": "Exhaustion forces you to pause, leaning against a rock face as you gasp for breath. You'll need to start this segment again after recovering.",
                    "ai_gm_guidance": "Focus on the physical strain and environmental challenges. This is about endurance, not just strength. If the rival warrior is present, they might be struggling too, creating tension."
                },
                {
                    "progress": 90,
                    "title": "The Summit Door",
                    "description": "At the summit, you must break through a sealed stone door to complete the trial.",
                    "narrative_description": "The summit reveals an ancient structure, its entrance sealed by a massive stone door that has not yielded in centuries. Inscriptions indicate this final test requires not just strength, but the perfect application of force.",
                    "available_actions": [
                        "direct_strike", "find_weak_point", "channel_strength"
                    ],
                    "skill_check": {"domain": "STRENGTH", "difficulty": 14},
                    "success_text": "You focus your strength and strike the perfect point. With a thunderous crack, the ancient door splits and crumbles, revealing the sacred chamber beyond.",
                    "failure_text": "Your blow lands with tremendous force, but the door holds firm. The impact reverberates up your arm painfully.",
                    "ai_gm_guidance": "This final challenge combines raw strength with precision. If character has failed previous attempts, consider hinting at technique from the elder or observation of the door's structure."
                },
                {
                    "progress": 100,
                    "title": "Champion of the Mountain",
                    "description": "You've completed the Trial of Might and earned its rewards.",
                    "narrative_description": "Inside the sacred chamber, ancient magic awakens. The Amulet of Enduring Might rises to your grasp, acknowledging you as worthy. You feel its power merge with your own, enhancing the strength that brought you here.",
                    "completion_effects": [
                        {"type": "item_granted", "id": "strength_amulet"},
                        {"type": "domain_xp", "domain": "STRENGTH", "amount": 50},
                        {"type": "reputation", "faction": "mountain_folk", "amount": 25},
                        {"type": "trait_granted", "id": "mountain_champion"}
                    ],
                    "ai_gm_guidance": "This is a moment of triumph. The character has proven themselves against ancient standards. Emphasize the mystical acknowledgment of their achievement and the respect they've earned."
                }
            ],
            "world_state_conditions": {
                "political_stability": ["PEACEFUL", "STABLE"], # Only available in relatively peaceful times
                "economic_status": ["STABLE", "BOOM"],     # Less likely if the world is in a deep depression
                "not_active_global_threats": ["Dragon Menace Nearby"] # Not available if a specific threat is active
            },
            "exclusivity": ["Endurance_Test", "Mountain_Pilgrimage"],
            "repeatable": False,
            "unlocks": ["Mountain_Champion", "Strength_Mentor"]
        },
        
        "Unsolved_Mystery": {
            "name": "Unsolved Mystery",
            "type": "DOMAIN_OPPORTUNITY",
            "description": "A perplexing case or mystery that others have failed to crack.",
            "domain": "INTELLECT",
            "min_domain_value": 3,
            "implementation": {
                "type": "investigation",
                "clue_trail": [
                    {"domain": "PERCEPTION", "difficulty": 11, "description": "Locate overlooked evidence at the scene."},
                    {"domain": "INTELLECT", "difficulty": 13, "description": "Connect seemingly unrelated facts into a pattern."},
                    {"domain": "AWARENESS", "difficulty": 12, "description": "Determine when someone is hiding information."}
                ],
                "location": "town_and_surroundings",
                "npc_involvement": [
                    {
                        "id": "constable", 
                        "role": "quest_giver",
                        "dialogue_themes": ["frustration", "authority", "suspicion", "respect_for_intellect"]
                    },
                    {
                        "id": "witnesses", 
                        "role": "information_sources",
                        "dialogue_themes": ["fear", "confusion", "partial_knowledge", "superstition"]
                    },
                    {
                        "id": "actual_culprit", 
                        "role": "antagonist",
                        "dialogue_themes": ["deception", "nervousness", "misdirection", "hubris"],
                        "hidden": True
                    }
                ],
                "rewards": [
                    {"type": "currency", "amount": 100, "description": "Payment for solving the case."},
                    {"type": "domain_xp", "domain": "INTELLECT", "amount": 40},
                    {"type": "reputation", "faction": "town_authorities", "amount": 25}
                ]
            },
            "stages": [
                {
                    "progress": 0,
                    "title": "The Cold Case",
                    "description": "You learn of a mystery that has baffled local authorities.",
                    "narrative_description": "The constable's office is cluttered with papers, but one case clearly weighs on him. He explains that valuable items have been disappearing with no signs of forced entry, and despite thorough questioning, no leads have emerged. The town is growing fearful of some supernatural explanation.",
                    "available_actions": [
                        "review_evidence", "question_constable", "visit_scene"
                    ],
                    "ai_gm_guidance": "Introduce this as a puzzle that normal methods haven't solved. The constable should be competent but mystified, implying the need for a sharper intellect or fresh perspective."
                },
                {
                    "progress": 30,
                    "title": "Following the Trail",
                    "description": "You begin investigating and find your first solid leads.",
                    "narrative_description": "Where others saw random incidents, you begin to discern patterns. The timing of the thefts, the specific items taken, the locations - all suggest a methodical mind rather than opportunity. Something others missed catches your attention...",
                    "available_actions": [
                        "examine_pattern", "interview_witnesses", "research_similar_cases", "stake_out_location"
                    ],
                    "skill_check": {"domain": "PERCEPTION", "difficulty": 11},
                    "success_text": "Your careful examination reveals minute details others overlooked - a partial footprint in dust, a displaced item indicating someone's path, or a pattern to the timing that suggests inside knowledge.",
                    "failure_text": "Despite your efforts, the clues remain frustratingly elusive. You'll need to try a different approach or look elsewhere.",
                    "ai_gm_guidance": "This stage should emphasize the character's unique observational abilities. If they have a background related to investigation (guard, scholar, etc.), highlight how that experience guides their approach."
                },
                {
                    "progress": 60,
                    "title": "Connecting the Dots",
                    "description": "You begin to form a theory based on the evidence gathered.",
                    "narrative_description": "Fragments of information swirl in your mind: witness statements, physical evidence, town gossip, and historical records. Where others see chaos, you begin to see connections, forming a hypothesis about what really happened and who might be responsible.",
                    "available_actions": [
                        "analyze_evidence", "test_theory", "consult_expert", "set_trap"
                    ],
                    "skill_check": {"domain": "INTELLECT", "difficulty": 13},
                    "success_text": "The disparate pieces click together in your mind, forming a coherent picture. You now understand what must have happened, and who would have the means, motive, and opportunity.",
                    "failure_text": "The pieces resist your attempts to order them. Your theory feels incomplete, missing some crucial element that ties everything together.",
                    "ai_gm_guidance": "This is the intellectual heart of the quest. The character should feel like they're solving a complex puzzle. Reward creative thinking and logical deductions."
                },
                {
                    "progress": 80,
                    "title": "Confronting the Truth",
                    "description": "You must confront the culprit with your evidence.",
                    "narrative_description": "Your investigation has led you to the surprising conclusion that [specific_npc] is behind the incidents. Now you must confront them and navigate their denials and potential dangers.",
                    "available_actions": [
                        "direct_confrontation", "set_trap", "bring_authorities", "negotiation"
                    ],
                    "skill_check": {"domain": "AWARENESS", "difficulty": 12},
                    "success_text": "As you present your evidence, you catch the subtle signs of deception and adjust your approach accordingly. When their facade finally cracks, the truth is revealed.",
                    "failure_text": "The suspect maintains their innocence convincingly. Either your theory is wrong, or they're more skilled at deception than anticipated.",
                    "ai_gm_guidance": "This confrontation should be tense and potentially dangerous. The culprit might be desperate or have contingency plans. Adjust based on whether the character brought allies or authorities."
                },
                {
                    "progress": 100,
                    "title": "Case Closed",
                    "description": "You've solved the mystery and revealed the truth.",
                    "narrative_description": "The final pieces fall into place as the culprit confesses or evidence irrefutably proves their guilt. The constable looks at you with newfound respect as the community buzzes with the news. Your reputation as a keen-minded problem solver is established.",
                    "completion_effects": [
                        {"type": "currency_reward", "amount": 100},
                        {"type": "domain_xp", "domain": "INTELLECT", "amount": 40},
                        {"type": "reputation", "faction": "town_authorities", "amount": 25},
                        {"type": "trait_granted", "id": "mystery_solver"}
                    ],
                    "ai_gm_guidance": "The resolution should satisfy the player's intellectual engagement. Ensure they feel their deductions mattered. Include reactions from NPCs who doubted or supported them."
                }
            ],
            "world_state_conditions": {
                "not_active_global_threats": ["Ongoing Invasion"] # Too chaotic during an invasion
            },
            "exclusivity": [],
            "repeatable": True,
            "unlocks": ["Recurring_Investigator", "Criminal_Network_Discovery"]
        },
        
        "Black_Market_Network": {
            "name": "Black Market Network",
            "type": "WORLD_STATE_RESPONSE",
            "description": "Establish connections in the underground economy that flourishes during hardship.",
            "domain": "MANIPULATION",
            "min_domain_value": 3,
            "implementation": {
                "type": "social_network_building",
                "key_interactions": [
                    {"domain": "MANIPULATION", "difficulty": 10, "description": "Convince a fence to reveal their suppliers."},
                    {"domain": "CHARISMA", "difficulty": 12, "description": "Gain the trust of suspicious smugglers."},
                    {"domain": "AWARENESS", "difficulty": 11, "description": "Identify undercover authorities before they identify you."}
                ],
                "location": "city_underbelly",
                "npc_involvement": [
                    {
                        "id": "fence", 
                        "role": "initial_contact",
                        "dialogue_themes": ["caution", "profit", "testing", "connections"]
                    },
                    {
                        "id": "smuggler_captain", 
                        "role": "key_ally",
                        "dialogue_themes": ["suspicion", "pragmatism", "opportunity", "risk"]
                    },
                    {
                        "id": "city_guard_captain", 
                        "role": "potential_threat",
                        "dialogue_themes": ["law", "order", "corruption", "compromise"]
                    }
                ],
                "rewards": [
                    {"type": "special_access", "id": "black_market_inventory", "description": "Access to rare and restricted goods."},
                    {"type": "domain_xp", "domain": "MANIPULATION", "amount": 35},
                    {"type": "contact_network", "faction": "smugglers_guild", "level": 2}
                ]
            },
            "stages": [
                {
                    "progress": 0,
                    "title": "Underground Whispers",
                    "description": "You hear rumors of a black market network operating amid economic hardship.",
                    "narrative_description": "As legitimate businesses struggle and goods grow scarce, whispers spread of another economy operating in the shadows. Those with the right connections can still obtain luxuries and necessities - for a price. A subtle invitation has been extended to you through veiled conversation.",
                    "available_actions": [
                        "visit_fence", "observe_suspicious_activity", "gather_information"
                    ],
                    "ai_gm_guidance": "Emphasize economic hardship in descriptions - empty market stalls, shuttered shops, desperate people. The black market should feel like a necessary adaptation rather than simple criminality."
                },
                {
                    "progress": 35,
                    "title": "Making Connections",
                    "description": "You begin establishing yourself in the underground network.",
                    "narrative_description": "The fence sizes you up carefully before sharing limited information. To go deeper into the network, you'll need to prove your reliability and discretion. A simple but risky task is proposed as a test of your capabilities and trustworthiness.",
                    "available_actions": [
                        "accept_task", "negotiate_terms", "demonstrate_value"
                    ],
                    "skill_check": {"domain": "MANIPULATION", "difficulty": 10},
                    "world_state_effects": {
                        "economic_status": {
                            "DEPRESSION": "The desperate economic situation makes people more willing to deal with you, reducing the difficulty by 2.",
                            "RECESSION": "The difficult economy makes this slightly easier, reducing difficulty by 1.",
                            "BOOM": "In these prosperous times, fewer people need black market services, increasing difficulty by 2."
                        }
                    },
                    "success_text": "Your careful approach wins over the cautious fence. They reveal more about the network and who controls various aspects of the underground economy.",
                    "failure_text": "The fence remains guarded, unwilling to risk their position on an unknown quantity. You'll need to find another way in or prove yourself differently.",
                    "ai_gm_guidance": "This is about social navigation rather than combat. The character should feel they're being evaluated. Use descriptions of body language, subtle tests, and coded language."
                },
                {
                    "progress": 70,
                    "title": "Valuable Intermediary",
                    "description": "You position yourself as a useful connection between different parts of the network.",
                    "narrative_description": "Having proven your basic reliability, you begin to see opportunities to connect different factions within the underground economy. Smugglers need discreet sellers, crafters need raw materials, and everyone needs information. You could become the nexus that brings them together.",
                    "available_actions": [
                        "broker_deal", "gather_intelligence", "establish_hideout", "recruit_associates"
                    ],
                    "skill_check": {"domain": "CHARISMA", "difficulty": 12},
                    "success_text": "Your diplomatic approach and clear value proposition bring cautious agreement from various factions. They begin to see the benefits of working with you as an intermediary.",
                    "failure_text": "Suspicion and competition prevent effective cooperation. You'll need to rebuild trust or find leverage to bring these parties together.",
                    "ai_gm_guidance": "Focus on the character creating value rather than just exploiting opportunities. This stage should involve negotiation and relationship building."
                },
                {
                    "progress": 90,
                    "title": "Avoiding the Authorities",
                    "description": "Your growing operation attracts unwanted attention from law enforcement.",
                    "narrative_description": "Success brings visibility, and the city guard has noticed the new patterns of activity. They've begun investigating, putting pressure on known associates and watching key locations. You'll need to identify their agents and adapt your operations to avoid exposure.",
                    "available_actions": [
                        "identify_informants", "establish_new_routes", "create_diversion", "bribe_officials"
                    ],
                    "skill_check": {"domain": "AWARENESS", "difficulty": 11},
                    "success_text": "You successfully identify the guard's methods and agents, allowing you to operate just beyond their reach. Their investigation yields nothing substantial.",
                    "failure_text": "A close call alerts you that you've been compromised. You'll need to lie low and rebuild parts of your network with greater caution.",
                    "ai_gm_guidance": "Create tension with near-discoveries and suspicious characters. The character should feel they're walking a dangerous line between success and exposure."
                },
                {
                    "progress": 100,
                    "title": "Shadow Economy Fixture",
                    "description": "You've established yourself as a key figure in the underground economy.",
                    "narrative_description": "What began as casual involvement has evolved into a significant position within the shadow economy. You have reliable contacts, protected channels of communication, and access to goods and services unavailable to most. In these hard times, your network has become valuable to many - from desperate commoners to wealthy merchants and even some authorities.",
                    "completion_effects": [
                        {"type": "special_access", "id": "black_market_inventory"},
                        {"type": "domain_xp", "domain": "MANIPULATION", "amount": 35},
                        {"type": "contact_network", "faction": "smugglers_guild", "level": 2},
                        {"type": "trait_granted", "id": "shadow_broker"}
                    ],
                    "ai_gm_guidance": "This resolution should feel like an establishment of a long-term asset rather than a simple quest completion. Emphasize the character's new position in society - respected and feared, with both opportunities and responsibilities."
                }
            ],
            "world_state_conditions": {
                "economic_status": ["RECESSION", "DEPRESSION"]
            },
            "exclusivity": ["Guard_Captain_Ally", "Legitimate_Merchant_Guild_Leadership"],
            "repeatable": False,
            "unlocks": ["Smuggling_Operations", "Information_Broker"]
        }
        # More branch definitions would continue here...
    }