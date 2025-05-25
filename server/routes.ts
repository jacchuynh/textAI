import express from 'express';
import { db } from '../db';
import { players, magicProfiles, playerItems, playerSpells, playerMaterials, playerQuests, playerQuestStages, npcs, spells, items, materials, quests, questStages } from '@shared/schema';
import { eq, and } from 'drizzle-orm';

const router = express.Router();

// API endpoint prefix
const apiPrefix = '/api';

// Helper function to check if player exists
async function getPlayerByUserId(userId: string) {
  return await db.query.players.findFirst({
    where: eq(players.userId, userId),
    with: {
      magicProfile: true,
    },
  });
}

// GET player profile
router.get(`${apiPrefix}/player/:userId`, async (req, res) => {
  try {
    const { userId } = req.params;
    const player = await getPlayerByUserId(userId);
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    return res.json(player);
  } catch (error) {
    console.error('Error fetching player:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// POST create new player
router.post(`${apiPrefix}/player`, async (req, res) => {
  try {
    const { userId, name, locationRegion, locationArea } = req.body;
    
    // Check if player already exists
    const existingPlayer = await getPlayerByUserId(userId);
    if (existingPlayer) {
      return res.status(400).json({ error: 'Player already exists' });
    }
    
    // Create the player
    const [player] = await db.insert(players).values({
      userId,
      name,
      locationRegion,
      locationArea,
      locationCoordinates: { x: 0, y: 0 }
    }).returning();
    
    // Create magic profile for the player
    await db.insert(magicProfiles).values({
      playerId: player.id
    });
    
    // Fetch the player with the magic profile
    const newPlayer = await getPlayerByUserId(userId);
    
    return res.status(201).json(newPlayer);
  } catch (error) {
    console.error('Error creating player:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET player inventory
router.get(`${apiPrefix}/player/:userId/inventory`, async (req, res) => {
  try {
    const { userId } = req.params;
    const player = await getPlayerByUserId(userId);
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    const inventory = await db.query.playerItems.findMany({
      where: eq(playerItems.playerId, player.id),
      with: {
        item: true
      }
    });
    
    return res.json(inventory);
  } catch (error) {
    console.error('Error fetching player inventory:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET player spells
router.get(`${apiPrefix}/player/:userId/spells`, async (req, res) => {
  try {
    const { userId } = req.params;
    const player = await getPlayerByUserId(userId);
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    const playerSpellsList = await db.query.playerSpells.findMany({
      where: eq(playerSpells.playerId, player.id),
      with: {
        spell: true
      }
    });
    
    return res.json(playerSpellsList);
  } catch (error) {
    console.error('Error fetching player spells:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET player materials
router.get(`${apiPrefix}/player/:userId/materials`, async (req, res) => {
  try {
    const { userId } = req.params;
    const player = await getPlayerByUserId(userId);
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    const materialsList = await db.query.playerMaterials.findMany({
      where: eq(playerMaterials.playerId, player.id),
      with: {
        material: true
      }
    });
    
    return res.json(materialsList);
  } catch (error) {
    console.error('Error fetching player materials:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET player quests
router.get(`${apiPrefix}/player/:userId/quests`, async (req, res) => {
  try {
    const { userId } = req.params;
    const player = await getPlayerByUserId(userId);
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    const questsList = await db.query.playerQuests.findMany({
      where: eq(playerQuests.playerId, player.id),
      with: {
        quest: true,
        stages: {
          with: {
            stage: true
          }
        }
      }
    });
    
    return res.json(questsList);
  } catch (error) {
    console.error('Error fetching player quests:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET NPCs in the current location
router.get(`${apiPrefix}/npcs/:region/:area`, async (req, res) => {
  try {
    const { region, area } = req.params;
    
    const npcsList = await db.query.npcs.findMany({
      where: and(
        eq(npcs.locationRegion, region),
        eq(npcs.locationArea, area)
      )
    });
    
    return res.json(npcsList);
  } catch (error) {
    console.error('Error fetching NPCs:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET all available spells
router.get(`${apiPrefix}/spells`, async (req, res) => {
  try {
    const spellsList = await db.query.spells.findMany();
    return res.json(spellsList);
  } catch (error) {
    console.error('Error fetching spells:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET all available items
router.get(`${apiPrefix}/items`, async (req, res) => {
  try {
    const itemsList = await db.query.items.findMany();
    return res.json(itemsList);
  } catch (error) {
    console.error('Error fetching items:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET all available materials
router.get(`${apiPrefix}/materials`, async (req, res) => {
  try {
    const materialsList = await db.query.materials.findMany();
    return res.json(materialsList);
  } catch (error) {
    console.error('Error fetching materials:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// GET all available quests
router.get(`${apiPrefix}/quests`, async (req, res) => {
  try {
    const questsList = await db.query.quests.findMany({
      with: {
        stages: true
      }
    });
    return res.json(questsList);
  } catch (error) {
    console.error('Error fetching quests:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// POST process player command
router.post(`${apiPrefix}/command`, async (req, res) => {
  try {
    const { userId, command } = req.body;
    
    if (!userId || !command) {
      return res.status(400).json({ error: 'Missing userId or command' });
    }
    
    const player = await getPlayerByUserId(userId);
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Process the command (this would integrate with the text parser and AI GM system)
    // For now, we'll just return a placeholder response
    const response = {
      message: `Command "${command}" processed successfully.`,
      result: "This is where the game engine response would go. The text parser would analyze your command and the AI GM would generate an appropriate response based on your current location, quest status, and other game state variables."
    };
    
    return res.json(response);
  } catch (error) {
    console.error('Error processing command:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// POST accept a quest
router.post(`${apiPrefix}/player/:userId/quests/:questId/accept`, async (req, res) => {
  try {
    const { userId, questId } = req.params;
    
    const player = await getPlayerByUserId(userId);
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
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
    const existingQuest = await db.query.playerQuests.findFirst({
      where: and(
        eq(playerQuests.playerId, player.id),
        eq(playerQuests.questId, parseInt(questId))
      )
    });
    
    if (existingQuest) {
      return res.status(400).json({ error: 'Quest already accepted' });
    }
    
    // Create player quest
    const [playerQuest] = await db.insert(playerQuests).values({
      playerId: player.id,
      questId: parseInt(questId)
    }).returning();
    
    // Add quest stages
    for (const stage of quest.stages) {
      await db.insert(playerQuestStages).values({
        playerQuestId: playerQuest.id,
        stageId: stage.id,
        progress: {}
      });
    }
    
    // Get the full player quest with stages
    const fullPlayerQuest = await db.query.playerQuests.findFirst({
      where: eq(playerQuests.id, playerQuest.id),
      with: {
        quest: true,
        stages: {
          with: {
            stage: true
          }
        }
      }
    });
    
    return res.json(fullPlayerQuest);
  } catch (error) {
    console.error('Error accepting quest:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

// Placeholder for text parsing and game engine integration
router.post(`${apiPrefix}/game/action`, async (req, res) => {
  try {
    const { userId, action, target, parameters } = req.body;
    
    const player = await getPlayerByUserId(userId);
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // This is where we would integrate with the game engine
    // For now, return a placeholder response
    let response = {
      success: true,
      message: `Action '${action}' processed successfully.`,
      effects: [],
      updatedState: {}
    };
    
    // Example basic response logic based on action type
    switch (action) {
      case 'move':
        response.message = `You move to ${target}.`;
        break;
      case 'attack':
        response.message = `You attack ${target}!`;
        response.effects.push('damage_dealt');
        break;
      case 'cast':
        response.message = `You cast ${target} spell.`;
        response.effects.push('spell_effect');
        break;
      case 'talk':
        response.message = `You talk to ${target}.`;
        response.effects.push('conversation_started');
        break;
      default:
        response.message = `You try to ${action} ${target || ''}.`;
    }
    
    return res.json(response);
  } catch (error) {
    console.error('Error processing game action:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;