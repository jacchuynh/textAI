import { Router } from 'express';
import { db } from '@db';
import { 
  players, 
  playerItems,
  playerSpells,
  playerQuests,
  playerMaterials
} from '@shared/schema';
import { eq } from 'drizzle-orm';

const router = Router();

// Get all players
router.get('/players', async (req, res) => {
  try {
    const allPlayers = await db.query.players.findMany({
      with: {
        playerItems: {
          with: {
            item: true
          }
        }
      }
    });
    return res.json(allPlayers);
  } catch (error) {
    console.error('Error fetching players:', error);
    return res.status(500).json({ error: 'Failed to fetch players' });
  }
});

// Get player by ID
router.get('/players/:id', async (req, res) => {
  try {
    const { id } = req.params;
    
    const player = await db.query.players.findFirst({
      where: eq(players.id, id),
      with: {
        magicProfile: true,
        playerItems: {
          with: {
            item: true
          }
        },
        playerSpells: {
          with: {
            spell: true
          }
        },
        playerQuests: {
          with: {
            quest: {
              with: {
                stages: true
              }
            },
            stages: true
          }
        },
        playerMaterials: {
          with: {
            material: true
          }
        }
      }
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    return res.json(player);
  } catch (error) {
    console.error('Error fetching player:', error);
    return res.status(500).json({ error: 'Failed to fetch player' });
  }
});

// Create a new player
router.post('/players', async (req, res) => {
  try {
    const { name, userId } = req.body;
    
    if (!name || !userId) {
      return res.status(400).json({ error: 'Name and userId are required' });
    }
    
    // Create the player with starting attributes
    const [newPlayer] = await db.insert(players).values({
      name,
      userId,
      level: 1,
      experience: 0,
      gold: 100,
      healthCurrent: 100,
      healthMax: 100,
      locationRegion: 'Silvermist Valley',
      locationArea: 'Mossy_Hollow',
      locationCoordinates: { x: 0, y: 0 },
      createdAt: new Date()
    }).returning();
    
    return res.status(201).json(newPlayer);
  } catch (error) {
    console.error('Error creating player:', error);
    return res.status(500).json({ error: 'Failed to create player' });
  }
});

// Parse player command
router.post('/parse-command', async (req, res) => {
  try {
    const { command, playerId } = req.body;
    
    if (!command || !playerId) {
      return res.status(400).json({ error: 'Command and playerId are required' });
    }
    
    // Simple command parsing logic
    const words = command.toLowerCase().split(' ');
    const firstWord = words[0];
    
    let actionType = '';
    let target = '';
    let parameters = {};
    
    // Basic command parsing
    if (['look', 'examine', 'inspect'].includes(firstWord)) {
      actionType = 'examine';
      target = words.slice(1).join(' ') || 'surroundings';
    } else if (['go', 'move', 'walk', 'travel'].includes(firstWord)) {
      actionType = 'movement';
      target = words.slice(1).join(' ');
    } else if (['attack', 'fight', 'hit'].includes(firstWord)) {
      actionType = 'combat';
      target = words.slice(1).join(' ');
    } else if (['talk', 'speak', 'ask'].includes(firstWord)) {
      actionType = 'dialogue';
      if (words[1] === 'to') {
        target = words.slice(2).join(' ');
      } else {
        target = words.slice(1).join(' ');
      }
    } else if (['cast', 'spell', 'magic'].includes(firstWord)) {
      actionType = 'magic';
      target = words.slice(1).join(' ');
    } else if (['craft', 'make', 'create', 'forge'].includes(firstWord)) {
      actionType = 'crafting';
      target = words.slice(1).join(' ');
    } else if (['quest', 'mission', 'task'].includes(firstWord)) {
      actionType = 'quest';
      target = words.slice(1).join(' ');
    } else {
      // Default to dialogue for unknown commands
      actionType = 'dialogue';
      target = command;
    }
    
    // Return the parsed action
    const parsedAction = {
      type: actionType,
      target,
      parameters,
      originalCommand: command
    };
    
    return res.json({ parsedAction });
  } catch (error) {
    console.error('Error parsing command:', error);
    return res.status(500).json({ error: 'Failed to parse command' });
  }
});

// Execute parsed action
router.post('/execute-action', async (req, res) => {
  try {
    const { action, playerId } = req.body;
    
    if (!action || !playerId) {
      return res.status(400).json({ error: 'Action and playerId are required' });
    }
    
    // Fetch the player
    const player = await db.query.players.findFirst({
      where: eq(players.id, playerId),
      with: {
        magicProfile: true,
        playerItems: {
          with: {
            item: true
          }
        },
        playerSpells: {
          with: {
            spell: true
          }
        },
        playerQuests: {
          with: {
            quest: true
          }
        },
        playerMaterials: {
          with: {
            material: true
          }
        }
      }
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Process the action based on type
    let result;
    switch (action.type) {
      case 'examine':
        result = handleExamineAction(action, player);
        break;
      case 'movement':
        result = await handleMovementAction(action, player);
        break;
      case 'combat':
        result = handleCombatAction(action, player);
        break;
      case 'dialogue':
        result = handleDialogueAction(action, player);
        break;
      case 'magic':
        result = await handleMagicAction(action, player);
        break;
      case 'crafting':
        result = handleCraftingAction(action, player);
        break;
      case 'quest':
        result = handleQuestAction(action, player);
        break;
      default:
        return res.status(400).json({ error: 'Unknown action type' });
    }
    
    return res.json(result);
  } catch (error) {
    console.error('Error executing action:', error);
    return res.status(500).json({ error: 'Failed to execute action' });
  }
});

// Helper functions for handling different action types
function handleExamineAction(action: any, player: any) {
  const { target } = action;
  
  // Basic location descriptions
  const locationDescriptions: Record<string, string> = {
    'surroundings': `You are in ${player.locationArea.replace('_', ' ')}, a small settlement in the ${player.locationRegion}. 
      The air is crisp and filled with the scent of pine. You see a few buildings, including a blacksmith's shop, 
      an alchemist's hut, and a tavern. There are several NPCs moving about the village.`,
    'blacksmith': `The blacksmith's shop is filled with the sounds of hammering and the glow of the forge. 
      Tools and weapons line the walls, and the blacksmith, a burly man named Gareth, is working on a sword.`,
    'alchemist': `The alchemist's hut is cluttered with bottles, herbs, and strange contraptions. 
      The alchemist, an elderly woman named Elara, is mixing potions at her workbench.`,
    'tavern': `The tavern is warm and inviting, with a fire crackling in the hearth. 
      Several patrons are enjoying drinks and meals, and the tavern keeper, a jovial man named Torm, is serving drinks.`
  };
  
  // Check if player has items or materials to examine
  if (player.playerItems) {
    const item = player.playerItems.find((pi: any) => pi.item.name.toLowerCase() === target.toLowerCase());
    if (item) {
      return { 
        message: `You examine your ${item.item.name}. ${item.item.description || 'It looks ordinary.'}` 
      };
    }
  }
  
  if (player.playerMaterials) {
    const material = player.playerMaterials.find((pm: any) => pm.material.name.toLowerCase() === target.toLowerCase());
    if (material) {
      return { 
        message: `You examine your ${material.material.name}. ${material.material.description || 'It looks ordinary.'}` 
      };
    }
  }
  
  // Return description based on target or default message
  return { 
    message: locationDescriptions[target.toLowerCase()] || 
      `You examine the ${target}, but don't notice anything special about it.` 
  };
}

async function handleMovementAction(action: any, player: any) {
  const { target } = action;
  
  // Map of possible locations connected to current location
  const locationConnections: Record<string, Record<string, { region: string, area: string }>> = {
    'Mossy_Hollow': {
      'north': { region: 'Silvermist Valley', area: 'Whisperwind_Forest' },
      'east': { region: 'Silvermist Valley', area: 'Crystal_Lake' },
      'south': { region: 'Silvermist Valley', area: 'Ancient_Ruins' },
      'west': { region: 'Silvermist Valley', area: 'Mountain_Pass' }
    },
    'Whisperwind_Forest': {
      'south': { region: 'Silvermist Valley', area: 'Mossy_Hollow' }
    },
    'Crystal_Lake': {
      'west': { region: 'Silvermist Valley', area: 'Mossy_Hollow' }
    },
    'Ancient_Ruins': {
      'north': { region: 'Silvermist Valley', area: 'Mossy_Hollow' }
    },
    'Mountain_Pass': {
      'east': { region: 'Silvermist Valley', area: 'Mossy_Hollow' }
    }
  };
  
  // Check if current location has a connection in the specified direction
  const connections = locationConnections[player.locationArea] || {};
  const newLocation = connections[target.toLowerCase()];
  
  if (!newLocation) {
    return { message: `You can't go ${target} from here.` };
  }
  
  // Update player location
  await db.update(players)
    .set({ 
      locationRegion: newLocation.region,
      locationArea: newLocation.area
    })
    .where(eq(players.id, player.id));
  
  return { 
    message: `You travel ${target} to ${newLocation.area.replace('_', ' ')}.`,
    locationUpdate: {
      region: newLocation.region,
      area: newLocation.area
    }
  };
}

function handleCombatAction(action: any, player: any) {
  const { target } = action;
  
  // List of possible enemies in different areas
  const areaEnemies: Record<string, string[]> = {
    'Mossy_Hollow': ['wolf', 'bandit'],
    'Whisperwind_Forest': ['bear', 'wild boar', 'forest sprite'],
    'Crystal_Lake': ['water elemental', 'crocodile'],
    'Ancient_Ruins': ['skeleton', 'ancient guardian', 'ghost'],
    'Mountain_Pass': ['rock golem', 'mountain troll']
  };
  
  // Check if the target enemy exists in the current area
  const enemies = areaEnemies[player.locationArea] || [];
  const enemyExists = enemies.some(enemy => target.toLowerCase().includes(enemy));
  
  if (!enemyExists) {
    return { message: `There is no ${target} here to attack.` };
  }
  
  // Simplified combat result
  return { 
    message: `You attack the ${target}! After a brief struggle, you defeat it and gain some experience.`,
    combatResult: {
      enemyDefeated: true,
      experienceGained: 25,
      itemsDropped: []
    }
  };
}

function handleDialogueAction(action: any, player: any) {
  const { target, originalCommand } = action;
  
  // List of NPCs in different areas
  const areaNPCs: Record<string, Record<string, string>> = {
    'Mossy_Hollow': {
      'elder': 'The village elder welcomes you to Mossy Hollow and suggests you visit the blacksmith to upgrade your equipment.',
      'blacksmith': 'Gareth the blacksmith offers to craft weapons and armor for you if you bring him the right materials.',
      'alchemist': 'Elara the alchemist can brew potions for you if you gather herbs from the forest.',
      'tavern keeper': 'Torm the tavern keeper tells you about rumors of ancient ruins to the south that might contain valuable treasures.'
    },
    'Whisperwind_Forest': {
      'ranger': 'The forest ranger warns you about dangerous creatures deeper in the forest.',
      'hermit': 'The old hermit shares stories about the magical properties of the forest.'
    },
    'Crystal_Lake': {
      'fisherman': 'The fisherman talks about strange lights he\'s seen beneath the lake\'s surface.',
      'water mage': 'The water mage offers to teach you water spells if you prove yourself worthy.'
    },
    'Ancient_Ruins': {
      'archaeologist': 'The archaeologist is excited about recent discoveries in the ruins.',
      'ghost': 'The ghostly figure speaks in riddles about the history of this place.'
    },
    'Mountain_Pass': {
      'merchant': 'The traveling merchant offers rare goods from distant lands.',
      'miner': 'The dwarf miner talks about valuable ores deep within the mountains.'
    }
  };
  
  // Check if the target NPC exists in the current area
  const npcs = areaNPCs[player.locationArea] || {};
  
  // First check exact matches
  if (npcs[target.toLowerCase()]) {
    return { message: npcs[target.toLowerCase()] };
  }
  
  // Then check partial matches
  for (const npc in npcs) {
    if (target.toLowerCase().includes(npc)) {
      return { message: npcs[npc] };
    }
  }
  
  // If no matching NPC, treat as a general query
  const responses = {
    'quest': 'The locals mention several tasks that need doing. The elder might have more information.',
    'magic': 'You hear that the water mage at Crystal Lake might teach spells to worthy apprentices.',
    'history': 'This region has a rich history. The Ancient Ruins to the south are said to hold many secrets.',
    'crafting': 'The blacksmith in town can craft weapons and armor with the right materials.',
    'monsters': 'The forest is home to wolves and bears, while more dangerous creatures lurk in the ruins to the south.'
  };
  
  for (const keyword in responses) {
    if (originalCommand.toLowerCase().includes(keyword)) {
      return { message: responses[keyword] };
    }
  }
  
  // Default response
  return { 
    message: `You can't find anyone named "${target}" to talk to. Try speaking with the elder, blacksmith, alchemist, or tavern keeper in the village.` 
  };
}

async function handleMagicAction(action: any, player: any) {
  const { target } = action;
  
  // Check if player has magic profile
  if (!player.magicProfile) {
    // Create basic magic profile if player doesn't have one
    await db.insert(players.magicProfile).values({
      playerId: player.id,
      manaCurrent: 50,
      manaMax: 50,
      magicAffinity: 'novice',
      knownAspects: ['basic']
    });
    
    return { 
      message: `You attempt to cast a spell, but realize you haven't learned any magic yet. 
        A strange tingling feeling flows through you as your magical abilities awaken. 
        Visit a mage to learn spells.`,
      magicResult: {
        success: false,
        magicAwakened: true
      }
    };
  }
  
  // Check if player has the spell they're trying to cast
  const words = target.toLowerCase().split(' ');
  const spellName = words.join(' ');
  
  const knownSpell = player.playerSpells?.find(
    (ps: any) => ps.spell.name.toLowerCase() === spellName
  );
  
  if (!knownSpell) {
    return { 
      message: `You don't know a spell called "${target}". Visit a mage to learn new spells.`,
      magicResult: {
        success: false,
        reason: 'unknown_spell'
      }
    };
  }
  
  // Check if player has enough mana
  if (player.magicProfile.manaCurrent < knownSpell.spell.manaCost) {
    return { 
      message: `You don't have enough mana to cast ${knownSpell.spell.name}.`,
      magicResult: {
        success: false,
        reason: 'insufficient_mana'
      }
    };
  }
  
  // Determine environmental effects based on location
  const locationEffects: Record<string, { aspects: string[], multiplier: number }> = {
    'Mossy_Hollow': { aspects: ['earth', 'nature'], multiplier: 1.0 },
    'Whisperwind_Forest': { aspects: ['air', 'nature'], multiplier: 1.2 },
    'Crystal_Lake': { aspects: ['water'], multiplier: 1.5 },
    'Ancient_Ruins': { aspects: ['arcane', 'death'], multiplier: 1.3 },
    'Mountain_Pass': { aspects: ['earth', 'fire'], multiplier: 1.1 }
  };
  
  const effect = locationEffects[player.locationArea] || { aspects: [], multiplier: 1.0 };
  
  // Calculate spell effectiveness based on environmental resonance
  let effectiveness = effect.multiplier;
  const spellAspects = knownSpell.spell.domains || [];
  
  for (const aspect of spellAspects) {
    if (effect.aspects.includes(aspect)) {
      effectiveness += 0.2; // Bonus for matching aspects
    }
  }
  
  // Update player mana
  await db.update(players.magicProfile)
    .set({ 
      manaCurrent: Math.max(0, player.magicProfile.manaCurrent - knownSpell.spell.manaCost)
    })
    .where(eq(players.magicProfile.playerId, player.id));
  
  // Return spell result
  return { 
    message: `You cast ${knownSpell.spell.name}! ${knownSpell.spell.description} 
      ${effectiveness > 1.2 ? 'The spell seems particularly effective here!' : ''}`,
    magicResult: {
      success: true,
      spellCast: knownSpell.spell.name,
      effectiveness,
      environmentalBonus: effectiveness > 1.0
    }
  };
}

function handleCraftingAction(action: any, player: any) {
  const { target } = action;
  
  // Simple crafting recipes
  const recipes: Record<string, { materials: Record<string, number>, description: string }> = {
    'health potion': {
      materials: { 'red herb': 2, 'crystal water': 1 },
      description: 'A simple potion that restores health.'
    },
    'mana potion': {
      materials: { 'blue herb': 2, 'crystal water': 1 },
      description: 'A simple potion that restores mana.'
    },
    'wooden sword': {
      materials: { 'wood': 3, 'string': 1 },
      description: 'A basic wooden sword for training.'
    },
    'leather armor': {
      materials: { 'leather': 5, 'string': 2 },
      description: 'Basic leather armor offering minimal protection.'
    }
  };
  
  // Check if the target item is a valid recipe
  const recipe = Object.entries(recipes).find(
    ([name]) => name === target.toLowerCase() || target.toLowerCase().includes(name)
  );
  
  if (!recipe) {
    return { 
      message: `You don't know how to craft "${target}". Visit crafters in town to learn recipes.`,
      craftingResult: {
        success: false,
        reason: 'unknown_recipe'
      }
    };
  }
  
  const [itemName, itemRecipe] = recipe;
  
  // Check if player has the required materials
  const playerMaterials = player.playerMaterials || [];
  const missingMaterials = [];
  
  for (const [materialName, requiredAmount] of Object.entries(itemRecipe.materials)) {
    const playerMaterial = playerMaterials.find(
      (pm: any) => pm.material.name.toLowerCase() === materialName.toLowerCase()
    );
    
    if (!playerMaterial || playerMaterial.quantity < requiredAmount) {
      missingMaterials.push(`${materialName} (need ${requiredAmount})`);
    }
  }
  
  if (missingMaterials.length > 0) {
    return { 
      message: `You can't craft a ${itemName} because you're missing: ${missingMaterials.join(', ')}.`,
      craftingResult: {
        success: false,
        reason: 'missing_materials',
        missingMaterials
      }
    };
  }
  
  // Simplified crafting result (would actually update inventory in a real implementation)
  return { 
    message: `You successfully craft a ${itemName}! ${itemRecipe.description}`,
    craftingResult: {
      success: true,
      itemCrafted: itemName,
      materialsUsed: itemRecipe.materials
    }
  };
}

function handleQuestAction(action: any, player: any) {
  const { target } = action;
  
  // List of available quests in different areas
  const areaQuests: Record<string, Record<string, { title: string, description: string, giver: string }>> = {
    'Mossy_Hollow': {
      'wolves': {
        title: 'Wolf Problem',
        description: 'The village elder asks you to deal with wolves that have been threatening livestock.',
        giver: 'elder'
      },
      'herbs': {
        title: 'Healing Herbs',
        description: 'The alchemist needs specific herbs from the forest for her potions.',
        giver: 'alchemist'
      },
      'delivery': {
        title: 'Urgent Delivery',
        description: 'The blacksmith needs you to deliver a package to the miner in the Mountain Pass.',
        giver: 'blacksmith'
      }
    },
    'Whisperwind_Forest': {
      'lost child': {
        title: 'Lost Child',
        description: 'A child from the village has wandered into the forest and gone missing.',
        giver: 'ranger'
      }
    },
    'Crystal_Lake': {
      'water samples': {
        title: 'Unusual Water',
        description: 'The water mage needs samples from different parts of the lake for research.',
        giver: 'water mage'
      }
    },
    'Ancient_Ruins': {
      'artifacts': {
        title: 'Ancient Artifacts',
        description: 'The archaeologist wants you to recover specific artifacts from deeper in the ruins.',
        giver: 'archaeologist'
      }
    },
    'Mountain_Pass': {
      'ore samples': {
        title: 'Rare Ore',
        description: 'The miner asks you to collect samples of a strange ore he discovered.',
        giver: 'miner'
      }
    }
  };
  
  // Check active quests if looking for status
  if (['status', 'log', 'active', 'current'].includes(target.toLowerCase())) {
    const activeQuests = player.playerQuests?.filter((pq: any) => pq.status !== 'completed') || [];
    
    if (activeQuests.length === 0) {
      return { message: 'You have no active quests. Talk to NPCs in the village to find quests.' };
    }
    
    const questList = activeQuests.map((pq: any) => `- ${pq.quest.name}: ${pq.quest.description}`).join('\n');
    return { 
      message: `Your active quests:\n${questList}`,
      questResult: {
        type: 'status',
        activeQuests: activeQuests.map((pq: any) => ({
          id: pq.id,
          name: pq.quest.name,
          status: pq.status
        }))
      }
    };
  }
  
  // Check if the target quest exists in the current area
  const quests = areaQuests[player.locationArea] || {};
  let questMatch = null;
  
  for (const [key, quest] of Object.entries(quests)) {
    if (target.toLowerCase().includes(key) || quest.title.toLowerCase().includes(target.toLowerCase())) {
      questMatch = { key, ...quest };
      break;
    }
  }
  
  if (!questMatch) {
    return { 
      message: `There is no quest related to "${target}" in this area. Talk to the locals to discover quests.`,
      questResult: {
        type: 'not_found'
      }
    };
  }
  
  // Check if player already has this quest
  const existingQuest = player.playerQuests?.find(
    (pq: any) => pq.quest.name.toLowerCase() === questMatch.title.toLowerCase()
  );
  
  if (existingQuest) {
    if (existingQuest.status === 'completed') {
      return { 
        message: `You've already completed the quest "${questMatch.title}".`,
        questResult: {
          type: 'already_completed',
          quest: {
            id: existingQuest.id,
            name: existingQuest.quest.name
          }
        }
      };
    } else {
      return { 
        message: `You already have the quest "${questMatch.title}" in progress. ${questMatch.description}`,
        questResult: {
          type: 'in_progress',
          quest: {
            id: existingQuest.id,
            name: existingQuest.quest.name,
            status: existingQuest.status
          }
        }
      };
    }
  }
  
  // Return quest info (would actually add quest to player in a real implementation)
  return { 
    message: `${questMatch.giver} offers you a new quest: "${questMatch.title}"\n${questMatch.description}\n\nDo you accept?`,
    questResult: {
      type: 'offer',
      quest: {
        title: questMatch.title,
        description: questMatch.description,
        giver: questMatch.giver
      }
    }
  };
}

export default router;