import axios from 'axios';
import WebSocket from 'ws';
import { DomainType, TagCategory, Tag } from '../shared/types';

interface NPCShadowProfile {
  domains: Record<DomainType, number>;
  recentTags: string[];
  firstEncounter: boolean;
}

// Map of tags to their most associated domains
const tagToDomainMap: Record<string, DomainType[]> = {
  // Crafting & Professions
  "Blacksmithing": ["CRAFT", "BODY"],
  "Tailoring": ["CRAFT"],
  "Potioncraft": ["CRAFT", "MIND"],
  "Enchanting": ["CRAFT", "SPIRIT", "MIND"],
  "Runework": ["CRAFT", "MIND"],
  "Jewelry": ["CRAFT"],
  "Trapmaking": ["CRAFT", "AWARENESS"],
  
  // Arcane Tags & Magic Schools
  "Fire": ["MIND", "SPIRIT"],
  "Ice": ["MIND", "SPIRIT"],
  "Lightning": ["MIND", "SPIRIT"],
  "Decay": ["MIND", "SPIRIT"],
  "Binding": ["MIND", "SPIRIT", "AUTHORITY"],
  "Illusion": ["MIND", "SOCIAL"],
  "Light": ["MIND", "SPIRIT"],
  "Shadow": ["MIND", "SPIRIT"],
  "Spirit": ["SPIRIT"],
  "Astral": ["MIND", "SPIRIT"],
  
  // Academic / Support
  "Research": ["MIND"],
  "Investigation": ["MIND", "AWARENESS"],
  "Translation": ["MIND"],
  
  // Ritual & Alchemy
  "Ritual": ["SPIRIT", "MIND"],
  "Alchemy": ["CRAFT", "MIND"],
  
  // Social Interaction
  "Negotiation": ["SOCIAL"],
  "Deception": ["SOCIAL"],
  "Persuasion": ["SOCIAL"],
  "Authority": ["AUTHORITY", "SOCIAL"]
} as Record<string, DomainType[]>;

// Tag keywords dictionary for automatic action classification
const tagKeywords = {
  // Crafting & Professions
  "Blacksmithing": ["forge", "anvil", "hammer", "iron", "temper", "ingot", "metal"],
  "Tailoring": ["sew", "needle", "thread", "fabric", "cloth", "weave"],
  "Potioncraft": ["brew", "bottle", "herb", "mortar", "vial", "distill", "essence"],
  "Enchanting": ["inscribe", "rune", "infuse", "aura", "sigil", "embed"],
  "Runework": ["glyph", "carve", "channel", "line", "pattern", "etch"],
  "Jewelry": ["gem", "set", "ring", "amulet", "chain", "cut", "inlay"],
  "Trapmaking": ["tripwire", "spring", "trigger", "trap", "mechanism", "camouflage"],

  // Arcane Tags & Magic Schools
  "Fire": ["flame", "burn", "ignite", "heat", "ember", "scorch"],
  "Ice": ["frost", "freeze", "cold", "chill", "shiver", "snow"],
  "Lightning": ["spark", "shock", "bolt", "charge", "thunder"],
  "Decay": ["rot", "blight", "corrupt", "molder", "wither"],
  "Binding": ["chain", "seal", "tether", "lock", "bind", "contract"],
  "Illusion": ["mirror", "fake", "phantom", "glimmer", "blur"],
  "Light": ["shine", "glow", "radiant", "halo", "gleam", "reveal"],
  "Shadow": ["dark", "veil", "conceal", "shade", "silence", "eclipse"],
  "Spirit": ["soul", "essence", "prayer", "ritual", "chant", "offering"],
  "Astral": ["dream", "sleep", "astral", "veil", "beyond", "star"],

  // Academic / Support
  "Research": ["study", "observe", "experiment", "theory", "archive"],
  "Investigation": ["search", "inspect", "clue", "track", "follow", "deduce"],
  "Translation": ["decode", "interpret", "language", "script", "cipher"],

  // Ritual & Alchemy
  "Ritual": ["circle", "chant", "blood", "offering", "sacrifice", "focus", "invoke"],
  "Alchemy": ["transmute", "essence", "catalyst", "brew", "reaction", "balance"],

  // Social Interaction
  "Negotiation": ["deal", "haggle", "bargain", "price", "agree", "contract"],
  "Deception": ["lie", "fake", "mislead", "bluff", "mask"],
  "Persuasion": ["convince", "coax", "influence", "plea", "motivate"],
  "Authority": ["command", "order", "decree", "rule", "lead", "mandate"]
};

// NPC bias configuration
const npcBias: Record<string, Partial<Record<DomainType, number>>> = {
  "Thane Bren": { [DomainType.AUTHORITY]: 2, [DomainType.SOCIAL]: -1 },
  "Acolyte Sera": { [DomainType.SPIRIT]: 3, [DomainType.MIND]: -2 },
  "Master Smith Grimmel": { [DomainType.CRAFT]: 3, [DomainType.MIND]: -1 },
  "Huntress Eira": { [DomainType.AWARENESS]: 2, [DomainType.BODY]: 2, [DomainType.SOCIAL]: -1 },
  "Guild Master Dorn": { [DomainType.SOCIAL]: 2, [DomainType.AUTHORITY]: 1, [DomainType.CRAFT]: 1 },
  "Elder Mystic Valna": { [DomainType.SPIRIT]: 3, [DomainType.MIND]: 2, [DomainType.BODY]: -2 }
};

/**
 * Auto-detects tags in an action description based on keywords
 */
export function autoTagAction(text: string): string[] {
  const tagScores: Record<string, number> = {};
  const lowerText = text.toLowerCase();
  
  for (const [tag, keywords] of Object.entries(tagKeywords)) {
    const score = keywords.reduce((sum, keyword) => 
      lowerText.includes(keyword) ? sum + 1 : sum, 0);
    
    if (score > 0) {
      tagScores[tag] = score;
    }
  }
  
  // Sort by score and return tag names
  return Object.entries(tagScores)
    .sort((a, b) => b[1] - a[1])
    .map(([tag]) => tag);
}

/**
 * Gets the dominant domains from a shadow profile
 */
export function getDominantDomains(profile: Record<DomainType, number>, topN: number = 2): DomainType[] {
  return Object.entries(profile)
    .sort(([, valueA], [, valueB]) => valueB - valueA)
    .slice(0, topN)
    .map(([domain]) => domain as DomainType);
}

/**
 * Calculates NPC affinity score based on their biases and player's domain usage
 */
export function calculateNpcAffinity(
  npcName: string, 
  profile: Record<DomainType, number>
): number {
  const bias = npcBias[npcName] || {};
  let score = 0;
  
  for (const [domain, value] of Object.entries(profile)) {
    const domainAsDomainType = domain as DomainType;
    const biasValue = bias[domainAsDomainType];
    
    if (biasValue !== undefined) {
      // More weight to frequently used domains
      score += biasValue * (Math.floor(value / 10));
    }
  }
  
  return score;
}

/**
 * Infers potential domains from a set of tags
 */
export function inferDomainsFromTags(tags: string[]): DomainType[] {
  const domains = new Set<DomainType>();
  
  for (const tag of tags) {
    if (tag in tagToDomainMap) {
      for (const domain of tagToDomainMap[tag]) {
        domains.add(domain);
      }
    }
  }
  
  return Array.from(domains);
}

/**
 * Generates an NPC response for a first encounter
 */
export async function generateFirstEncounterResponse(
  npcName: string,
  recentAction: string,
  detectedTags: string[],
  model?: string
): Promise<string> {
  try {
    const apiUrl = "https://openrouter.ai/api/v1/chat/completions";
    const apiKey = process.env.OPENROUTER_API_KEY;
    
    if (!apiKey) {
      throw new Error("Missing OpenRouter API key");
    }
    
    const inferredDomains = inferDomainsFromTags(detectedTags);
    
    const prompt = `
You are roleplaying an NPC named "${npcName}" in a fantasy world.

This is your FIRST interaction with this player, who just performed this action:
"${recentAction}"

From this action, you've detected these tags: ${detectedTags.join(', ')}
These tags might suggest domains like: ${inferredDomains.length ? inferredDomains.join(', ') : "unknown"}

Generate a brief first-impression response that:
1. Shows curiosity about the player's apparent skills
2. Makes a reasonable guess about their dominant domains
3. Stays true to your NPC's personality
4. Can be speculative, as you don't know the player well yet

Style: In-character, 2-3 sentences, no narration—only the NPC speaking.
`;

    const payload = {
      messages: [{ role: "user", content: prompt }],
      model: model || "openai/gpt-3.5-turbo",
      temperature: 0.85,
      max_tokens: 100
    };
    
    // Add model if specified
    if (model) {
      Object.assign(payload, { model });
    }
    
    const response = await axios.post(apiUrl, payload, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      }
    });
    
    return response.data.choices[0].message.content;
  } catch (error: any) {
    console.error("Error generating first encounter response:", error);
    if (error.response) {
      console.error("API response error:", {
        status: error.response.status,
        data: error.response.data
      });
    }
    // Fallback response
    return `Hmm, I see you're skilled with ${detectedTags.join(', ')}. Interesting choice of techniques.`;
  }
}

/**
 * Generates an NPC response based on the player's shadow profile
 */
export async function generateNpcResponse(
  npcName: string,
  shadowProfile: NPCShadowProfile,
  recentAction: string,
  model?: string
): Promise<string> {
  // For first encounters, use the specialized prompt
  if (shadowProfile.firstEncounter) {
    const detectedTags = autoTagAction(recentAction);
    return generateFirstEncounterResponse(npcName, recentAction, detectedTags, model);
  }
  
  try {
    const apiUrl = "https://openrouter.ai/api/v1/chat/completions";
    const apiKey = process.env.OPENROUTER_API_KEY;
    
    if (!apiKey) {
      throw new Error("Missing OpenRouter API key");
    }
    
    const dominantDomains = getDominantDomains(shadowProfile.domains);
    const recentTag = shadowProfile.recentTags.length > 0 ? shadowProfile.recentTags[0] : "none";
    const npcBiasInfo = npcBias[npcName] || {};
    
    // Format the bias summary
    const biasEntries = Object.entries(npcBiasInfo)
      .map(([domain, value]) => {
        if (value === undefined) return null;
        return `${domain}: ${value > 0 ? "Positive" : "Negative"}`;
      })
      .filter(entry => entry !== null)
      .join(", ");
    
    const biasSummary = biasEntries.length > 0 
      ? `Has opinions about: ${biasEntries}` 
      : "Neutral to most domains";
    
    const prompt = `
You are roleplaying an NPC named "${npcName}" in a fantasy world.

This NPC is interacting with the player, whose dominant skills are:
- Domains: ${dominantDomains.join(', ')}
- Recently used Tag: [${recentTag}]

NPC Bias: ${biasSummary}

Generate a brief but immersive response. It can be:
- Curious if the player's skill surprises them
- Respectful if they admire that domain
- Critical if they're biased negatively
- Casual or humorous if it's fitting

Style: In-character, 1–2 sentences, no narration—only the NPC speaking.
`;

    const payload = {
      messages: [{ role: "user", content: prompt }],
      model: model || "anthropic/claude-3-opus",
      temperature: 0.85,
      max_tokens: 80
    };
    
    // Add model if specified
    if (model) {
      Object.assign(payload, { model });
    }
    
    const response = await axios.post(apiUrl, payload, {
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      }
    });
    
    return response.data.choices[0].message.content;
  } catch (error: any) {
    console.error("Error generating NPC response:", error);
    if (error.response) {
      console.error("API response error:", {
        status: error.response.status,
        data: error.response.data
      });
    }
    // Fallback response
    return `I see you've been focusing on your ${getDominantDomains(shadowProfile.domains).join(' and ')} skills. Interesting choice.`;
  }
}

/**
 * Updates the shadow profile based on a player action
 */
export function updateShadowProfile(
  profile: Record<DomainType, number>,
  domain: DomainType,
  amount: number = 1
): Record<DomainType, number> {
  return {
    ...profile,
    [domain]: (profile[domain] || 0) + amount
  };
}