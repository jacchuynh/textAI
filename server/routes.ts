import express from 'express';
import { db } from '../db';
import { eq, and } from 'drizzle-orm';
import { 
  players, 
  magicProfiles, 
  items, 
  playerItems,
  spells,
  playerSpells,
  quests,
  playerQuests,
  playersInsertSchema,
  magicProfilesInsertSchema
} from '@shared/schema';

const router = express.Router();

// API prefix
const apiPrefix = '/api';

// Health check endpoint
router.get(`${apiPrefix}/health`, (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Get all players
router.get(`${apiPrefix}/players`, async (req, res) => {
  try {
    const allPlayers = await db.query.players.findMany({
      with: {
        magicProfile: true
      }
    });
    res.json(allPlayers);
  } catch (error) {
    console.error('Error fetching players:', error);
    res.status(500).json({ error: 'Failed to fetch players' });
  }
});

// Get player by ID
router.get(`${apiPrefix}/player/:userId`, async (req, res) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId),
      with: {
        magicProfile: true
      }
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    res.json(player);
  } catch (error) {
    console.error('Error fetching player:', error);
    res.status(500).json({ error: 'Failed to fetch player' });
  }
});

// Create new player
router.post(`${apiPrefix}/player`, async (req, res) => {
  try {
    const validatedData = playersInsertSchema.parse(req.body);
    
    // Check if player with this userId already exists
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, validatedData.userId)
    });
    
    if (existingPlayer) {
      return res.status(409).json({ error: 'Player with this user ID already exists' });
    }
    
    // Create player with default location coordinates if not provided
    const locationCoordinates = validatedData.locationCoordinates || { x: 0, y: 0, z: 0 };
    
    // Insert player
    const [newPlayer] = await db.insert(players).values({
      ...validatedData,
      locationCoordinates
    }).returning();
    
    // Create magic profile for the player
    const [magicProfile] = await db.insert(magicProfiles).values({
      playerId: newPlayer.id
    }).returning();
    
    // Return player with magic profile
    res.status(201).json({ ...newPlayer, magicProfile });
  } catch (error) {
    console.error('Error creating player:', error);
    res.status(500).json({ error: 'Failed to create player' });
  }
});

// Update player
router.patch(`${apiPrefix}/player/:userId`, async (req, res) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Find player
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Update player
    const [updatedPlayer] = await db.update(players)
      .set(req.body)
      .where(eq(players.userId, userId))
      .returning();
      
    res.json(updatedPlayer);
  } catch (error) {
    console.error('Error updating player:', error);
    res.status(500).json({ error: 'Failed to update player' });
  }
});

// Get player items
router.get(`${apiPrefix}/player/:userId/items`, async (req, res) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Find player
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get player items with item details
    const playerItemsList = await db.query.playerItems.findMany({
      where: eq(playerItems.playerId, player.id),
      with: {
        item: true
      }
    });
    
    res.json(playerItemsList);
  } catch (error) {
    console.error('Error fetching player items:', error);
    res.status(500).json({ error: 'Failed to fetch player items' });
  }
});

// Get player spells
router.get(`${apiPrefix}/player/:userId/spells`, async (req, res) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Find player
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get player spells with spell details
    const playerSpellsList = await db.query.playerSpells.findMany({
      where: eq(playerSpells.playerId, player.id),
      with: {
        spell: true
      }
    });
    
    res.json(playerSpellsList);
  } catch (error) {
    console.error('Error fetching player spells:', error);
    res.status(500).json({ error: 'Failed to fetch player spells' });
  }
});

// Get player quests
router.get(`${apiPrefix}/player/:userId/quests`, async (req, res) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Find player
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get player quests with quest details
    const playerQuestsList = await db.query.playerQuests.findMany({
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
    
    res.json(playerQuestsList);
  } catch (error) {
    console.error('Error fetching player quests:', error);
    res.status(500).json({ error: 'Failed to fetch player quests' });
  }
});

// Process player command (text parser entry point)
router.post(`${apiPrefix}/command`, async (req, res) => {
  try {
    const { userId, command } = req.body;
    
    if (!userId || !command) {
      return res.status(400).json({ error: 'User ID and command are required' });
    }
    
    // Find player
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId),
      with: {
        magicProfile: true
      }
    });
    
    if (!player) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Process command (in a real implementation, this would call the text parser and game engine)
    // For now, provide a simple response
    let result = '';
    
    if (command.toLowerCase().includes('look')) {
      result = `You are in ${player.locationArea.replace('_', ' ')} within the ${player.locationRegion}. The area is quiet and peaceful.`;
    } else if (command.toLowerCase().includes('help')) {
      result = 'Available commands: look, inventory, stats, go [direction], cast [spell], attack [target]';
    } else if (command.toLowerCase().includes('inventory') || command.toLowerCase().includes('items')) {
      result = 'You open your backpack and check your items. (Your inventory would be listed here)';
    } else if (command.toLowerCase().includes('stats')) {
      result = `Your stats: Level ${player.level}, HP: ${player.healthCurrent}/${player.healthMax}, MP: ${player.magicProfile?.manaCurrent || 0}/${player.magicProfile?.manaMax || 0}, Gold: ${player.gold}`;
    } else if (command.toLowerCase().includes('cast')) {
      const spellName = command.toLowerCase().replace('cast', '').trim();
      result = `You attempt to cast ${spellName}. (Magic system would process this)`;
    } else if (command.toLowerCase().startsWith('go ')) {
      const direction = command.toLowerCase().replace('go', '').trim();
      result = `You travel ${direction}. (Movement system would process this)`;
    } else if (command.toLowerCase().includes('attack')) {
      const target = command.toLowerCase().replace('attack', '').trim();
      result = `You prepare to attack ${target}. (Combat system would process this)`;
    } else {
      result = `You said: "${command}". (The AI Game Master would process this command)`;
    }
    
    res.json({ result });
  } catch (error) {
    console.error('Error processing command:', error);
    res.status(500).json({ error: 'Failed to process command' });
  }
});

// Update player magic profile
router.patch(`${apiPrefix}/player/:userId/magic-profile`, async (req, res) => {
  try {
    const { userId } = req.params;
    
    if (!userId) {
      return res.status(400).json({ error: 'User ID is required' });
    }
    
    // Find player
    const player = await db.query.players.findFirst({
      where: eq(players.userId, userId),
      with: {
        magicProfile: true
      }
    });
    
    if (!player || !player.magicProfile) {
      return res.status(404).json({ error: 'Player or magic profile not found' });
    }
    
    // Validate magic profile data
    const validatedData = magicProfilesInsertSchema.partial().parse(req.body);
    
    // Update magic profile
    const [updatedMagicProfile] = await db.update(magicProfiles)
      .set(validatedData)
      .where(eq(magicProfiles.id, player.magicProfile.id))
      .returning();
      
    res.json(updatedMagicProfile);
  } catch (error) {
    console.error('Error updating magic profile:', error);
    res.status(500).json({ error: 'Failed to update magic profile' });
  }
});

export default router;