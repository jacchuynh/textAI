import express from 'express';
import { db } from '../../db';
import { 
  players, playersInsertSchema,
  magicProfiles, magicProfilesInsertSchema,
  quests, playerQuests,
  spells, playerSpells,
  items, playerItems,
  materials, playerMaterials
} from '@shared/schema';
import { eq, and } from 'drizzle-orm';
import { z } from 'zod';

const router = express.Router();

// Define API prefix
const apiPrefix = '/api';

// Health check endpoint
router.get(`${apiPrefix}/health`, (req, res) => {
  res.json({ status: 'ok' });
});

// Player routes
router.get(`${apiPrefix}/players`, async (req, res) => {
  try {
    const allPlayers = await db.query.players.findMany();
    return res.json(allPlayers);
  } catch (error) {
    console.error('Error fetching players:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.get(`${apiPrefix}/players/:id`, async (req, res) => {
  try {
    const { id } = req.params;
    const player = await db.query.players.findFirst({
      where: eq(players.id, parseInt(id)),
      with: {
        magicProfile: true,
        playerItems: {
          with: {
            item: true
          }
        },
        playerMaterials: {
          with: {
            material: true
          }
        },
        playerQuests: {
          with: {
            quest: true,
            stages: {
              with: {
                stage: true
              }
            }
          }
        },
        playerSpells: {
          with: {
            spell: true
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
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.post(`${apiPrefix}/players`, async (req, res) => {
  try {
    const playerData = playersInsertSchema.parse(req.body);
    
    const [newPlayer] = await db.insert(players).values(playerData).returning();
    
    // Create a magic profile for the new player
    const magicProfileData = {
      playerId: newPlayer.id,
      manaCurrent: 50,
      manaMax: 50,
      manaRegenRate: 1.0,
      primaryDomains: ['ARCANE'],
      secondaryDomains: []
    };
    
    const [newMagicProfile] = await db.insert(magicProfiles)
      .values(magicProfileData)
      .returning();
    
    return res.status(201).json({
      ...newPlayer,
      magicProfile: newMagicProfile
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    console.error('Error creating player:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Spell routes
router.get(`${apiPrefix}/spells`, async (req, res) => {
  try {
    const allSpells = await db.query.spells.findMany();
    return res.json(allSpells);
  } catch (error) {
    console.error('Error fetching spells:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.get(`${apiPrefix}/spells/:id`, async (req, res) => {
  try {
    const { id } = req.params;
    const spell = await db.query.spells.findFirst({
      where: eq(spells.id, parseInt(id))
    });

    if (!spell) {
      return res.status(404).json({ error: 'Spell not found' });
    }

    return res.json(spell);
  } catch (error) {
    console.error('Error fetching spell:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Magic profile routes
router.get(`${apiPrefix}/magic-profiles/:playerId`, async (req, res) => {
  try {
    const { playerId } = req.params;
    const profile = await db.query.magicProfiles.findFirst({
      where: eq(magicProfiles.playerId, parseInt(playerId))
    });

    if (!profile) {
      return res.status(404).json({ error: 'Magic profile not found' });
    }

    return res.json(profile);
  } catch (error) {
    console.error('Error fetching magic profile:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Player spells routes
router.get(`${apiPrefix}/players/:playerId/spells`, async (req, res) => {
  try {
    const { playerId } = req.params;
    const playerSpellList = await db.query.playerSpells.findMany({
      where: eq(playerSpells.playerId, parseInt(playerId)),
      with: {
        spell: true
      }
    });

    return res.json(playerSpellList);
  } catch (error) {
    console.error('Error fetching player spells:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.post(`${apiPrefix}/players/:playerId/learn-spell/:spellId`, async (req, res) => {
  try {
    const { playerId, spellId } = req.params;
    
    // Check if player exists
    const player = await db.query.players.findFirst({
      where: eq(players.id, parseInt(playerId))
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Check if spell exists
    const spell = await db.query.spells.findFirst({
      where: eq(spells.id, parseInt(spellId))
    });
    
    if (!spell) {
      return res.status(404).json({ error: 'Spell not found' });
    }
    
    // Check if player already knows this spell
    const existingPlayerSpell = await db.query.playerSpells.findFirst({
      where: and(
        eq(playerSpells.playerId, parseInt(playerId)),
        eq(playerSpells.spellId, parseInt(spellId))
      )
    });
    
    if (existingPlayerSpell) {
      return res.status(400).json({ error: 'Player already knows this spell' });
    }
    
    // Add spell to player's known spells
    const [newPlayerSpell] = await db.insert(playerSpells)
      .values({
        playerId: parseInt(playerId),
        spellId: parseInt(spellId)
      })
      .returning();
    
    return res.status(201).json({
      ...newPlayerSpell,
      spell
    });
  } catch (error) {
    console.error('Error learning spell:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Item routes
router.get(`${apiPrefix}/items`, async (req, res) => {
  try {
    const allItems = await db.query.items.findMany();
    return res.json(allItems);
  } catch (error) {
    console.error('Error fetching items:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Material routes
router.get(`${apiPrefix}/materials`, async (req, res) => {
  try {
    const allMaterials = await db.query.materials.findMany();
    return res.json(allMaterials);
  } catch (error) {
    console.error('Error fetching materials:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Quest routes
router.get(`${apiPrefix}/quests`, async (req, res) => {
  try {
    const allQuests = await db.query.quests.findMany({
      with: {
        stages: true
      }
    });
    return res.json(allQuests);
  } catch (error) {
    console.error('Error fetching quests:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.get(`${apiPrefix}/quests/:id`, async (req, res) => {
  try {
    const { id } = req.params;
    const quest = await db.query.quests.findFirst({
      where: eq(quests.id, parseInt(id)),
      with: {
        stages: true
      }
    });

    if (!quest) {
      return res.status(404).json({ error: 'Quest not found' });
    }

    return res.json(quest);
  } catch (error) {
    console.error('Error fetching quest:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Player quests routes
router.get(`${apiPrefix}/players/:playerId/quests`, async (req, res) => {
  try {
    const { playerId } = req.params;
    const playerQuestList = await db.query.playerQuests.findMany({
      where: eq(playerQuests.playerId, parseInt(playerId)),
      with: {
        quest: {
          with: {
            stages: true
          }
        },
        stages: {
          with: {
            stage: true
          }
        }
      }
    });

    return res.json(playerQuestList);
  } catch (error) {
    console.error('Error fetching player quests:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

router.post(`${apiPrefix}/players/:playerId/accept-quest/:questId`, async (req, res) => {
  try {
    const { playerId, questId } = req.params;
    
    // Check if player exists
    const player = await db.query.players.findFirst({
      where: eq(players.id, parseInt(playerId))
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Check if quest exists
    const quest = await db.query.quests.findFirst({
      where: eq(quests.id, parseInt(questId)),
      with: {
        stages: true
      }
    });
    
    if (!quest) {
      return res.status(404).json({ error: 'Quest not found' });
    }
    
    // Check if player already has this quest
    const existingPlayerQuest = await db.query.playerQuests.findFirst({
      where: and(
        eq(playerQuests.playerId, parseInt(playerId)),
        eq(playerQuests.questId, parseInt(questId))
      )
    });
    
    if (existingPlayerQuest) {
      return res.status(400).json({ error: 'Player already has this quest' });
    }
    
    // Add quest to player's active quests
    const [newPlayerQuest] = await db.insert(playerQuests)
      .values({
        playerId: parseInt(playerId),
        questId: parseInt(questId),
        status: 'active'
      })
      .returning();
    
    return res.status(201).json({
      ...newPlayerQuest,
      quest
    });
  } catch (error) {
    console.error('Error accepting quest:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Game text parser endpoint - simulates parsing natural language into structured commands
router.post(`${apiPrefix}/parse-command`, (req, res) => {
  try {
    const { command, playerId } = req.body;
    
    if (!command || typeof command !== 'string') {
      return res.status(400).json({ error: 'Command is required' });
    }
    
    const lowerCommand = command.toLowerCase();
    let action = null;
    
    // Simple pattern matching for demonstration
    if (lowerCommand.includes('attack') || lowerCommand.includes('fight')) {
      action = {
        type: 'combat',
        action: 'attack',
        target: lowerCommand.includes('wolf') ? 'wolf' : 'unknown',
        method: lowerCommand.includes('sword') ? 'sword' : 'unarmed'
      };
    } else if (lowerCommand.includes('cast')) {
      // Detect spell name
      let spell = 'unknown';
      if (lowerCommand.includes('arcane bolt')) spell = 'arcane_bolt';
      else if (lowerCommand.includes('fireball')) spell = 'fireball';
      else if (lowerCommand.includes('healing')) spell = 'healing_light';
      
      action = {
        type: 'magic',
        action: 'cast',
        spell,
        target: lowerCommand.includes('wolf') ? 'wolf' : 'self'
      };
    } else if (lowerCommand.includes('talk') || lowerCommand.includes('speak')) {
      let npc = 'unknown';
      if (lowerCommand.includes('elder') || lowerCommand.includes('thaddeus')) npc = 'elder_thaddeus';
      else if (lowerCommand.includes('blacksmith') || lowerCommand.includes('goran')) npc = 'blacksmith_goran';
      
      action = {
        type: 'dialogue',
        action: 'talk',
        target: npc
      };
    } else if (lowerCommand.includes('go') || lowerCommand.includes('travel') || lowerCommand.includes('move')) {
      let location = 'unknown';
      if (lowerCommand.includes('forest')) location = 'forest_path';
      else if (lowerCommand.includes('village')) location = 'village_square';
      else if (lowerCommand.includes('crossroads')) location = 'crossroads';
      
      action = {
        type: 'movement',
        action: 'travel',
        destination: location
      };
    } else if (lowerCommand.includes('craft') || lowerCommand.includes('make')) {
      let item = 'unknown';
      if (lowerCommand.includes('sword')) item = 'iron_sword';
      else if (lowerCommand.includes('potion')) item = 'health_potion';
      else if (lowerCommand.includes('armor')) item = 'leather_armor';
      
      action = {
        type: 'crafting',
        action: 'craft',
        item
      };
    } else if (lowerCommand.includes('quest')) {
      if (lowerCommand.includes('accept') || lowerCommand.includes('take')) {
        action = {
          type: 'quest',
          action: 'accept',
          quest: lowerCommand.includes('village troubles') ? 'village_troubles' : 'unknown'
        };
      } else if (lowerCommand.includes('complete') || lowerCommand.includes('finish')) {
        action = {
          type: 'quest',
          action: 'complete',
          quest: lowerCommand.includes('village troubles') ? 'village_troubles' : 'unknown'
        };
      } else {
        action = {
          type: 'quest',
          action: 'view',
          quest: lowerCommand.includes('village troubles') ? 'village_troubles' : 'all'
        };
      }
    } else {
      // Default to an examine action if no other patterns match
      let target = 'surroundings';
      if (lowerCommand.includes('myself') || lowerCommand.includes('inventory')) target = 'self';
      
      action = {
        type: 'examine',
        action: 'look',
        target
      };
    }
    
    // Return the parsed command
    return res.json({ 
      originalCommand: command,
      parsedAction: action,
      message: 'Command parsed successfully'
    });
  } catch (error) {
    console.error('Error parsing command:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Game action endpoint - processes the structured commands from the parser
router.post(`${apiPrefix}/execute-action`, async (req, res) => {
  try {
    const { action, playerId } = req.body;
    
    if (!action || !playerId) {
      return res.status(400).json({ error: 'Action and playerId are required' });
    }
    
    // Get player data
    const player = await db.query.players.findFirst({
      where: eq(players.id, parseInt(playerId)),
      with: {
        magicProfile: true
      }
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Process different action types
    let result: any = null;
    
    switch (action.type) {
      case 'combat':
        result = handleCombatAction(action, player);
        break;
      case 'magic':
        result = await handleMagicAction(action, player);
        break;
      case 'dialogue':
        result = handleDialogueAction(action, player);
        break;
      case 'movement':
        result = await handleMovementAction(action, player);
        break;
      case 'crafting':
        result = handleCraftingAction(action, player);
        break;
      case 'quest':
        result = handleQuestAction(action, player);
        break;
      case 'examine':
        result = handleExamineAction(action, player);
        break;
      default:
        return res.status(400).json({ error: 'Unknown action type' });
    }
    
    return res.json({
      success: true,
      message: result.message,
      gameState: result.gameState
    });
  } catch (error) {
    console.error('Error executing action:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Helper functions for handling different action types
function handleCombatAction(action: any, player: any) {
  // Simulate combat logic
  let message = '';
  let gameState = { player: { ...player }, target: null, combat: { round: 1, status: 'active' } };
  
  if (action.action === 'attack') {
    const targetName = action.target === 'unknown' ? 'the enemy' : `the ${action.target}`;
    const weaponText = action.method === 'unarmed' ? 'your fists' : `your ${action.method}`;
    
    message = `You attack ${targetName} with ${weaponText}! You deal 5 damage.`;
    gameState.target = { 
      name: action.target === 'unknown' ? 'Enemy' : action.target.charAt(0).toUpperCase() + action.target.slice(1),
      health: { current: 15, max: 20 }
    };
  }
  
  return { message, gameState };
}

async function handleMagicAction(action: any, player: any) {
  // Simulate magic logic
  let message = '';
  let gameState = { player: { ...player }, spell: null, target: null };
  
  if (action.action === 'cast') {
    // Get spell details if it exists
    const spell = await db.query.spells.findFirst({
      where: eq(spells.spellId, action.spell)
    });
    
    if (spell) {
      // Check if player knows the spell
      const playerKnowsSpell = await db.query.playerSpells.findFirst({
        where: and(
          eq(playerSpells.playerId, player.id),
          eq(playerSpells.spellId, spell.id)
        )
      });
      
      if (playerKnowsSpell || spell.spellId === 'arcane_bolt') { // Assume players know Arcane Bolt by default
        if (player.magicProfile.manaCurrent >= spell.manaCost) {
          // Update player's mana
          await db.update(magicProfiles)
            .set({
              manaCurrent: Math.max(0, player.magicProfile.manaCurrent - spell.manaCost),
              updatedAt: new Date()
            })
            .where(eq(magicProfiles.playerId, player.id));
          
          // Get updated magic profile
          const updatedProfile = await db.query.magicProfiles.findFirst({
            where: eq(magicProfiles.playerId, player.id)
          });
          
          gameState.player = {
            ...player,
            magicProfile: updatedProfile
          };
          
          const targetName = action.target === 'self' ? 'yourself' : `the ${action.target}`;
          
          if (spell.spellId === 'arcane_bolt') {
            message = `You cast Arcane Bolt at ${targetName}, dealing ${spell.basePower} arcane damage!`;
            gameState.spell = spell;
            gameState.target = {
              name: action.target === 'self' ? 'Self' : action.target.charAt(0).toUpperCase() + action.target.slice(1),
              health: { current: 15, max: 20 }
            };
          } else if (spell.spellId === 'fireball') {
            message = `You cast Fireball at ${targetName}, creating an explosion that deals ${spell.basePower} fire damage in the area!`;
            gameState.spell = spell;
            gameState.target = {
              name: action.target === 'self' ? 'Self' : action.target.charAt(0).toUpperCase() + action.target.slice(1),
              health: { current: 12, max: 20 }
            };
          } else if (spell.spellId === 'healing_light') {
            message = `You cast Healing Light on ${targetName}, restoring ${spell.basePower} health!`;
            gameState.spell = spell;
            gameState.target = {
              name: action.target === 'self' ? 'Self' : action.target.charAt(0).toUpperCase() + action.target.slice(1),
              health: { current: 20, max: 20 }
            };
          } else {
            message = `You cast ${spell.name} on ${targetName}!`;
            gameState.spell = spell;
          }
        } else {
          message = `You don't have enough mana to cast ${spell.name}! (${player.magicProfile.manaCurrent}/${spell.manaCost} mana)`;
        }
      } else {
        message = `You don't know how to cast ${spell.name}. You need to learn this spell first.`;
      }
    } else {
      message = `You try to cast a spell, but the words escape your memory.`;
    }
  }
  
  return { message, gameState };
}

function handleDialogueAction(action: any, player: any) {
  // Simulate dialogue logic
  let message = '';
  let gameState = { player: { ...player }, npc: null, dialogue: null };
  
  if (action.action === 'talk') {
    if (action.target === 'elder_thaddeus') {
      message = `Elder Thaddeus says: "Ah, ${player.name}! Our village has been having trouble with wolves attacking travelers on the forest path. Could you help us deal with them?"`;
      gameState.npc = { 
        id: 'elder_thaddeus',
        name: 'Elder Thaddeus',
        location: 'crossroads',
        attitude: 'friendly'
      };
      gameState.dialogue = {
        options: [
          { id: 'accept_quest', text: 'I would be happy to help with the wolves.' },
          { id: 'ask_reward', text: 'What\'s in it for me?' },
          { id: 'decline_quest', text: 'Sorry, I have other matters to attend to.' }
        ]
      };
    } else if (action.target === 'blacksmith_goran') {
      message = `Blacksmith Goran says: "Welcome to my forge, ${player.name}! Looking to craft something? I can help you make weapons and armor if you have the materials."`;
      gameState.npc = { 
        id: 'blacksmith_goran',
        name: 'Blacksmith Goran',
        location: 'village_square',
        attitude: 'friendly'
      };
      gameState.dialogue = {
        options: [
          { id: 'craft_weapon', text: 'I\'d like to craft a weapon.' },
          { id: 'craft_armor', text: 'I\'d like to craft some armor.' },
          { id: 'browse_goods', text: 'What do you have for sale?' },
          { id: 'goodbye', text: 'Just looking around, thanks.' }
        ]
      };
    } else {
      message = 'You try to start a conversation, but nobody responds.';
    }
  }
  
  return { message, gameState };
}

async function handleMovementAction(action: any, player: any) {
  // Simulate movement logic
  let message = '';
  let gameState = { player: { ...player }, previousLocation: null, newLocation: null };
  
  if (action.action === 'travel') {
    // Save the previous location
    gameState.previousLocation = {
      region: player.locationRegion,
      area: player.locationArea
    };
    
    // Determine the new location details
    let locationDescription = '';
    let region = player.locationRegion;
    let area = '';
    
    if (action.destination === 'forest_path') {
      area = 'forest_path';
      locationDescription = 'A narrow path winding through dense forest. You can hear the sounds of wildlife all around you.';
    } else if (action.destination === 'village_square') {
      area = 'village_square';
      locationDescription = 'The bustling center of the village. Merchants sell their wares and villagers go about their daily business.';
    } else if (action.destination === 'crossroads') {
      area = 'crossroads';
      locationDescription = 'A crossroads where several paths meet. A weathered signpost points in different directions.';
    } else {
      area = action.destination;
      locationDescription = 'You travel to a new area.';
    }
    
    // Update player location in database
    await db.update(players)
      .set({
        locationArea: area,
        updatedAt: new Date()
      })
      .where(eq(players.id, player.id));
    
    // Get updated player data
    const updatedPlayer = await db.query.players.findFirst({
      where: eq(players.id, player.id),
      with: {
        magicProfile: true
      }
    });
    
    gameState.player = updatedPlayer;
    gameState.newLocation = {
      region,
      area,
      description: locationDescription
    };
    
    message = `You travel to the ${area.replace('_', ' ')}. ${locationDescription}`;
  }
  
  return { message, gameState };
}

function handleCraftingAction(action: any, player: any) {
  // Simulate crafting logic
  let message = '';
  let gameState = { player: { ...player }, crafting: null };
  
  if (action.action === 'craft') {
    if (action.item === 'iron_sword') {
      message = 'You craft an Iron Sword. It\'s not the finest blade, but it will serve you well in battle.';
      gameState.crafting = {
        item: {
          id: 'iron_sword',
          name: 'Iron Sword',
          type: 'weapon',
          stats: { damage: 5 }
        },
        materialsUsed: [
          { id: 'iron_ore', name: 'Iron Ore', quantity: 3 },
          { id: 'wood', name: 'Wood', quantity: 1 }
        ],
        success: true
      };
    } else if (action.item === 'health_potion') {
      message = 'You craft a Minor Health Potion. The crimson liquid bubbles slightly in the vial.';
      gameState.crafting = {
        item: {
          id: 'health_potion',
          name: 'Minor Health Potion',
          type: 'consumable',
          stats: { health: 20 }
        },
        materialsUsed: [
          { id: 'herbs', name: 'Medicinal Herbs', quantity: 2 }
        ],
        success: true
      };
    } else if (action.item === 'leather_armor') {
      message = 'You craft Leather Armor. It\'s lightweight but offers decent protection.';
      gameState.crafting = {
        item: {
          id: 'leather_armor',
          name: 'Leather Armor',
          type: 'armor',
          stats: { defense: 3 }
        },
        materialsUsed: [
          { id: 'leather', name: 'Leather', quantity: 5 }
        ],
        success: true
      };
    } else {
      message = 'You\'re not sure how to craft that item.';
      gameState.crafting = {
        success: false,
        reason: 'unknown_recipe'
      };
    }
  }
  
  return { message, gameState };
}

function handleQuestAction(action: any, player: any) {
  // Simulate quest logic
  let message = '';
  let gameState = { player: { ...player }, quest: null };
  
  if (action.action === 'accept') {
    if (action.quest === 'village_troubles') {
      message = 'You accept the quest "Village Troubles". Elder Thaddeus looks relieved. "Thank you! Please deal with those wolves and return to me when you\'re done."';
      gameState.quest = {
        id: 'village_troubles',
        name: 'Village Troubles',
        status: 'active',
        description: 'The village elder has asked for help dealing with the wolves that have been attacking travelers.',
        objectives: [
          { id: 'kill_wolves', description: 'Hunt down and kill the wolves (0/3)', completed: false },
          { id: 'return_to_elder', description: 'Return to Elder Thaddeus', completed: false }
        ]
      };
    } else {
      message = 'You try to accept a quest, but can\'t quite understand the details.';
    }
  } else if (action.action === 'complete') {
    if (action.quest === 'village_troubles') {
      message = 'You complete the quest "Village Troubles". Elder Thaddeus thanks you and rewards you with 50 gold and a pair of leather boots.';
      gameState.quest = {
        id: 'village_troubles',
        name: 'Village Troubles',
        status: 'completed',
        rewards: {
          gold: 50,
          items: [{ id: 'leather_boots', name: 'Leather Boots', type: 'armor' }],
          experience: 100
        }
      };
    } else {
      message = 'That quest isn\'t ready to be completed yet.';
    }
  } else if (action.action === 'view') {
    if (action.quest === 'village_troubles') {
      message = 'Quest: Village Troubles - The village elder has asked for help dealing with the wolves that have been attacking travelers.';
      gameState.quest = {
        id: 'village_troubles',
        name: 'Village Troubles',
        status: 'active',
        description: 'The village elder has asked for help dealing with the wolves that have been attacking travelers.',
        objectives: [
          { id: 'kill_wolves', description: 'Hunt down and kill the wolves (0/3)', completed: false },
          { id: 'return_to_elder', description: 'Return to Elder Thaddeus', completed: false }
        ]
      };
    } else if (action.quest === 'all') {
      message = 'Your active quests: Village Troubles';
      gameState.quest = {
        activeQuests: [
          {
            id: 'village_troubles',
            name: 'Village Troubles',
            status: 'active'
          }
        ]
      };
    } else {
      message = 'You don\'t have that quest in your journal.';
    }
  }
  
  return { message, gameState };
}

function handleExamineAction(action: any, player: any) {
  // Simulate examine logic
  let message = '';
  let gameState = { player: { ...player }, examination: null };
  
  if (action.action === 'look') {
    if (action.target === 'self' || action.target === 'inventory') {
      message = `You check your inventory. You have a backpack containing various items.`;
      gameState.examination = {
        type: 'inventory',
        inventory: {
          gold: player.gold,
          items: [
            { id: 'iron_sword', name: 'Iron Sword', type: 'weapon', quantity: 1 },
            { id: 'health_potion', name: 'Minor Health Potion', type: 'consumable', quantity: 3 }
          ],
          materials: [
            { id: 'iron_ore', name: 'Iron Ore', type: 'material', quantity: 5 },
            { id: 'wood', name: 'Wood', type: 'material', quantity: 8 },
            { id: 'herbs', name: 'Medicinal Herbs', type: 'material', quantity: 3 }
          ]
        }
      };
    } else {
      let location = '';
      let description = '';
      let features: string[] = [];
      let npcs: Array<{id: string, name: string}> = [];
      
      if (player.locationArea === 'crossroads') {
        location = 'Crossroads';
        description = 'A crossroads where several paths meet. A weathered signpost points in different directions.';
        features = ['signpost', 'dirt paths'];
        npcs = [{ id: 'elder_thaddeus', name: 'Elder Thaddeus' }];
      } else if (player.locationArea === 'forest_path') {
        location = 'Forest Path';
        description = 'A narrow path winding through dense forest. You can hear the sounds of wildlife all around you.';
        features = ['tall trees', 'underbrush', 'animal tracks'];
        npcs = [];
      } else if (player.locationArea === 'village_square') {
        location = 'Village Square';
        description = 'The bustling center of the village. Merchants sell their wares and villagers go about their daily business.';
        features = ['well', 'market stalls', 'blacksmith forge'];
        npcs = [{ id: 'blacksmith_goran', name: 'Blacksmith Goran' }];
      }
      
      message = `You look around the ${location}. ${description}`;
      gameState.examination = {
        type: 'surroundings',
        location: {
          name: location,
          description,
          features,
          npcs
        }
      };
    }
  }
  
  return { message, gameState };
}

export default router;