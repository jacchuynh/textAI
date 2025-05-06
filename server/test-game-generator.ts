import { v4 as uuidv4 } from 'uuid';
import { storage } from './storage';
import * as types from '@shared/types';

/**
 * This file generates a test game for development purposes
 */

export async function generateTestGame(): Promise<types.GameState> {
  // Create a unique game ID
  const gameId = uuidv4();
  
  // Create a test NPC with bias
  const thane: types.NPC = {
    id: 1,
    name: "Thane Bren",
    description: "A stern but fair leader of the local settlement. He has a weathered face and calculating eyes.",
    attitude: "neutral",
    domainBias: {
      [types.DomainType.AUTHORITY]: 2,
      [types.DomainType.SOCIAL]: -1
    },
    firstEncounter: true,
    knownInteractions: []
  };
  
  const blacksmith: types.NPC = {
    id: 2,
    name: "Master Smith Grimmel",
    description: "A burly blacksmith with forearms like tree trunks. His forge is always hot and he seems to respect those with practical skills.",
    attitude: "friendly",
    domainBias: {
      [types.DomainType.CRAFT]: 3,
      [types.DomainType.MIND]: -1
    },
    firstEncounter: true,
    knownInteractions: []
  };
  
  const mystic: types.NPC = {
    id: 3,
    name: "Elder Mystic Valna",
    description: "An elderly woman with knowing eyes that seem to see beyond the physical. She speaks in riddles and values spiritual insight.",
    attitude: "neutral",
    domainBias: {
      [types.DomainType.SPIRIT]: 3,
      [types.DomainType.MIND]: 2,
      [types.DomainType.BODY]: -2
    },
    firstEncounter: true,
    knownInteractions: []
  };
  
  // Create a test location with NPCs
  const location: types.Location = {
    id: 1,
    name: "Willowbrook Village",
    description: "A small village nestled between rolling hills and a gentle stream. The buildings are made of timber and stone, with thatched roofs.",
    type: "settlement",
    connections: [2, 3],
    npcs: [thane, blacksmith, mystic]
  };
  
  // Create test character with domain system
  const character: types.Character = {
    id: 1,
    name: "Test Adventurer",
    class: "Wanderer",
    background: "Mysterious Past",
    level: 1,
    xp: 0,
    stats: {
      strength: 10,
      dexterity: 10,
      intelligence: 10,
      charisma: 10
    },
    maxHealth: 20,
    currentHealth: 20,
    maxMana: 10,
    currentMana: 10,
    domains: {
      [types.DomainType.BODY]: createDomain(types.DomainType.BODY, 1),
      [types.DomainType.MIND]: createDomain(types.DomainType.MIND, 2),
      [types.DomainType.SPIRIT]: createDomain(types.DomainType.SPIRIT, 1),
      [types.DomainType.SOCIAL]: createDomain(types.DomainType.SOCIAL, 2),
      [types.DomainType.CRAFT]: createDomain(types.DomainType.CRAFT, 1),
      [types.DomainType.AUTHORITY]: createDomain(types.DomainType.AUTHORITY, 0),
      [types.DomainType.AWARENESS]: createDomain(types.DomainType.AWARENESS, 1)
    },
    tags: {
      "Persuasion": createTag("Persuasion", types.TagCategory.SOCIAL, "Skill at convincing others", [types.DomainType.SOCIAL], 1),
      "Investigation": createTag("Investigation", types.TagCategory.GENERAL, "Finding clues and solving puzzles", [types.DomainType.MIND, types.DomainType.AWARENESS], 1),
      "Blacksmithing": createTag("Blacksmithing", types.TagCategory.CRAFTING, "Creating and repairing metal items", [types.DomainType.CRAFT, types.DomainType.BODY], 0)
    },
    shadowProfile: {
      characterId: "1",
      domainUsage: {
        [types.DomainType.BODY]: 2,
        [types.DomainType.MIND]: 5,
        [types.DomainType.SPIRIT]: 1,
        [types.DomainType.SOCIAL]: 7,
        [types.DomainType.CRAFT]: 3,
        [types.DomainType.AUTHORITY]: 0,
        [types.DomainType.AWARENESS]: 2
      },
      recentTags: ["Persuasion", "Investigation"],
      timeTracking: {
        recent: {
          [types.DomainType.BODY]: 1,
          [types.DomainType.MIND]: 2,
          [types.DomainType.SPIRIT]: 0,
          [types.DomainType.SOCIAL]: 3,
          [types.DomainType.CRAFT]: 1,
          [types.DomainType.AUTHORITY]: 0,
          [types.DomainType.AWARENESS]: 1
        },
        weekly: {
          [types.DomainType.BODY]: 2,
          [types.DomainType.MIND]: 5,
          [types.DomainType.SPIRIT]: 1,
          [types.DomainType.SOCIAL]: 7,
          [types.DomainType.CRAFT]: 3,
          [types.DomainType.AUTHORITY]: 0,
          [types.DomainType.AWARENESS]: 2
        },
        monthly: {
          [types.DomainType.BODY]: 2,
          [types.DomainType.MIND]: 5,
          [types.DomainType.SPIRIT]: 1,
          [types.DomainType.SOCIAL]: 7,
          [types.DomainType.CRAFT]: 3,
          [types.DomainType.AUTHORITY]: 0,
          [types.DomainType.AWARENESS]: 2
        }
      },
      preferences: {
        [types.DomainType.BODY]: 1,
        [types.DomainType.MIND]: 3,
        [types.DomainType.SPIRIT]: 0,
        [types.DomainType.SOCIAL]: 4,
        [types.DomainType.CRAFT]: 2,
        [types.DomainType.AUTHORITY]: 0,
        [types.DomainType.AWARENESS]: 1
      }
    }
  };
  
  // Create basic inventory
  const inventory: types.Inventory = {
    maxWeight: 50,
    currentWeight: 15,
    items: [
      {
        id: 1,
        name: "Iron Dagger",
        description: "A simple but effective weapon",
        quantity: 1,
        weight: 2,
        type: "weapon",
        properties: {
          damage: 4
        }
      },
      {
        id: 2,
        name: "Health Potion",
        description: "A small vial of red liquid that restores health",
        quantity: 3,
        weight: 1,
        type: "consumable",
        properties: {
          effects: [
            {
              type: "heal",
              value: 10
            }
          ]
        }
      },
      {
        id: 3,
        name: "Blacksmith Hammer",
        description: "A sturdy hammer used for metalworking",
        quantity: 1,
        weight: 5,
        type: "tool"
      }
    ]
  };
  
  // Create test quests
  const quests: types.Quest[] = [
    {
      id: 1,
      title: "The Blacksmith's Request",
      description: "Master Smith Grimmel has asked for your help to collect rare ore from the nearby mines.",
      status: "active"
    },
    {
      id: 2,
      title: "Village Mystery",
      description: "Something strange is happening in Willowbrook. The Thane wants you to investigate.",
      status: "active"
    }
  ];
  
  // Create game state
  const gameState: types.GameState = {
    gameId,
    character,
    location,
    inventory,
    quests,
    narrativeContent: "You find yourself in the small village of Willowbrook. The locals seem friendly but cautious. You can see the village square ahead with several buildings surrounding it, including a blacksmith's forge, a tavern, and what appears to be the Thane's hall.",
    choices: [
      "Visit the blacksmith",
      "Speak with the Thane",
      "Explore the village",
      "Consult with Elder Mystic Valna"
    ]
  };
  
  // Save the test game to storage
  await storage.saveGameState(gameState);
  console.log(`Generated test game with ID: ${gameId}`);
  
  return gameState;
}

// Helper function to create a domain
function createDomain(type: types.DomainType, value: number): types.Domain {
  return {
    type,
    value,
    growthPoints: 0,
    growthRequired: value < 3 ? 5 : value < 6 ? 8 : value < 10 ? 12 : 15,
    usageCount: value * 10,
    growthLog: [],
    levelUpsRequired: 0
  };
}

// Helper function to create a tag
function createTag(name: string, category: types.TagCategory, description: string, domains: types.DomainType[], rank: number): types.Tag {
  return {
    id: name.toLowerCase(),
    name,
    category,
    description,
    domains,
    rank,
    xp: rank * 10,
    xpRequired: rank < 2 ? 20 : rank < 4 ? 40 : rank < 6 ? 60 : 100
  };
}

// Add a route to generate a test game
export function addTestGameRoute(app: any) {
  app.get("/api/debug/generate-test-game", async (_req: any, res: any) => {
    try {
      const gameState = await generateTestGame();
      res.status(200).json({ message: "Test game generated successfully", gameId: gameState.gameId });
    } catch (error) {
      console.error("Error generating test game:", error);
      res.status(500).json({ error: "Failed to generate test game" });
    }
  });
}