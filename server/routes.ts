import express from 'express';
import { db } from '@db';
import { 
  players, 
  magicProfiles, 
  playerSpells, 
  playerItems, 
  playerQuests,
  spells,
  items,
  quests,
  regions,
  areas,
  playerCraftingSkills,
  craftingRecipes,
  playerInsertSchema,
  magicProfileInsertSchema
} from '@shared/schema';
import { eq, and, desc } from 'drizzle-orm';
import { z } from 'zod';

const router = express.Router();

// Game engine integration middleware
import { processGameCommand } from './game-engine';

// Get all players (optimized for faster loading)
router.get('/api/players', async (req, res) => {
  try {
    // Set timeout and add basic query optimization
    const timeout = setTimeout(() => {
      res.status(408).json({ error: 'Request timeout' });
    }, 10000);

    const allPlayers = await db.query.players.findMany({
      with: {
        magicProfile: true
      },
      limit: 50 // Limit results to prevent overwhelming responses
    });
    
    clearTimeout(timeout);
    res.json(allPlayers);
  } catch (error) {
    console.error('Error fetching players:', error);
    res.status(500).json({ error: 'Failed to fetch players' });
  }
});

// Get player by userId
router.get('/api/player/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    
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
    console.error(`Error fetching player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to fetch player' });
  }
});

// Create new player
router.post('/api/player', async (req, res) => {
  try {
    // Validate input data
    const validatedData = playerInsertSchema.parse(req.body);
    
    // Insert player
    const [newPlayer] = await db.insert(players).values(validatedData).returning();
    
    // Create initial magic profile
    const magicProfileData = {
      playerId: newPlayer.id,
      magicAffinity: req.body.magicAffinity || 'arcane',
      knownAspects: req.body.knownAspects || ['basic']
    };
    
    const [magicProfile] = await db.insert(magicProfiles)
      .values(magicProfileData)
      .returning();
    
    // Return player with magic profile
    const playerWithProfile = {
      ...newPlayer,
      magicProfile
    };
    
    res.status(201).json(playerWithProfile);
  } catch (error) {
    console.error('Error creating player:', error);
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    res.status(500).json({ error: 'Failed to create player' });
  }
});

// Update player
router.patch('/api/player/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Update player
    const [updatedPlayer] = await db.update(players)
      .set({
        ...req.body,
        // Prevent these fields from being updated directly
        id: undefined,
        userId: undefined,
        createdAt: undefined
      })
      .where(eq(players.userId, userId))
      .returning();
    
    res.json(updatedPlayer);
  } catch (error) {
    console.error(`Error updating player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to update player' });
  }
});

// Update player magic profile
router.patch('/api/player/:userId/magic-profile', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Find existing magic profile
    const existingProfile = await db.query.magicProfiles.findFirst({
      where: eq(magicProfiles.playerId, existingPlayer.id)
    });
    
    if (!existingProfile) {
      // Create new profile if it doesn't exist
      const magicProfileData = {
        playerId: existingPlayer.id,
        magicAffinity: req.body.magicAffinity || 'arcane',
        knownAspects: req.body.knownAspects || ['basic'],
        updatedAt: new Date()
      };
      
      const [newProfile] = await db.insert(magicProfiles)
        .values(magicProfileData)
        .returning();
      
      return res.status(201).json(newProfile);
    }
    
    // Update existing profile
    const [updatedProfile] = await db.update(magicProfiles)
      .set({
        ...req.body,
        // Prevent these fields from being updated directly
        id: undefined,
        playerId: undefined,
        createdAt: undefined,
        updatedAt: new Date()
      })
      .where(eq(magicProfiles.id, existingProfile.id))
      .returning();
    
    res.json(updatedProfile);
  } catch (error) {
    console.error(`Error updating magic profile for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to update magic profile' });
  }
});

// Get player spells
router.get('/api/player/:userId/spells', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get player spells with spell details
    const playerSpellsList = await db.query.playerSpells.findMany({
      where: eq(playerSpells.playerId, existingPlayer.id),
      with: {
        spell: true
      }
    });
    
    res.json(playerSpellsList);
  } catch (error) {
    console.error(`Error fetching spells for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to fetch player spells' });
  }
});

// Learn new spell
router.post('/api/player/:userId/spells', async (req, res) => {
  try {
    const { userId } = req.params;
    const { spellId } = req.body;
    
    if (!spellId) {
      return res.status(400).json({ error: 'Spell ID is required' });
    }
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Check if spell exists
    const spell = await db.query.spells.findFirst({
      where: eq(spells.id, spellId)
    });
    
    if (!spell) {
      return res.status(404).json({ error: 'Spell not found' });
    }
    
    // Check if player already knows this spell
    const existingPlayerSpell = await db.query.playerSpells.findFirst({
      where: and(
        eq(playerSpells.playerId, existingPlayer.id),
        eq(playerSpells.spellId, spellId)
      )
    });
    
    if (existingPlayerSpell) {
      return res.status(400).json({ error: 'Player already knows this spell' });
    }
    
    // Check if player meets level requirement
    if (existingPlayer.level < spell.requiredLevel) {
      return res.status(400).json({ 
        error: `Player level (${existingPlayer.level}) is too low for this spell (requires level ${spell.requiredLevel})`
      });
    }
    
    // Add spell to player's spellbook
    const [newPlayerSpell] = await db.insert(playerSpells)
      .values({
        playerId: existingPlayer.id,
        spellId: spellId,
        masteryLevel: 1,
        favorite: false
      })
      .returning();
    
    // Return with spell details
    const result = {
      ...newPlayerSpell,
      spell
    };
    
    res.status(201).json(result);
  } catch (error) {
    console.error(`Error learning spell for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to learn spell' });
  }
});

// Get player inventory
router.get('/api/player/:userId/inventory', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get player items with details
    const playerItemsList = await db.query.playerItems.findMany({
      where: eq(playerItems.playerId, existingPlayer.id),
      with: {
        item: true
      }
    });
    
    res.json(playerItemsList);
  } catch (error) {
    console.error(`Error fetching inventory for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to fetch player inventory' });
  }
});

// Add item to inventory
router.post('/api/player/:userId/inventory', async (req, res) => {
  try {
    const { userId } = req.params;
    const { itemId, quantity = 1 } = req.body;
    
    if (!itemId) {
      return res.status(400).json({ error: 'Item ID is required' });
    }
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Check if item exists
    const item = await db.query.items.findFirst({
      where: eq(items.id, itemId)
    });
    
    if (!item) {
      return res.status(404).json({ error: 'Item not found' });
    }
    
    // Check if player already has this item (for stackable items)
    const existingPlayerItem = await db.query.playerItems.findFirst({
      where: and(
        eq(playerItems.playerId, existingPlayer.id),
        eq(playerItems.itemId, itemId),
        eq(playerItems.equipped, false) // Only stack unequipped items
      )
    });
    
    if (existingPlayerItem) {
      // Update quantity for existing item
      const [updatedPlayerItem] = await db.update(playerItems)
        .set({
          quantity: existingPlayerItem.quantity + quantity
        })
        .where(eq(playerItems.id, existingPlayerItem.id))
        .returning();
      
      const result = {
        ...updatedPlayerItem,
        item
      };
      
      return res.json(result);
    }
    
    // Add new item to player's inventory
    const [newPlayerItem] = await db.insert(playerItems)
      .values({
        playerId: existingPlayer.id,
        itemId: itemId,
        quantity: quantity,
        equipped: false
      })
      .returning();
    
    // Return with item details
    const result = {
      ...newPlayerItem,
      item
    };
    
    res.status(201).json(result);
  } catch (error) {
    console.error(`Error adding item to inventory for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to add item to inventory' });
  }
});

// Process game command
router.post('/api/player/:userId/command', async (req, res) => {
  try {
    const { userId } = req.params;
    const { command } = req.body;
    
    if (!command) {
      return res.status(400).json({ error: 'Command is required' });
    }
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId),
      with: {
        magicProfile: true
      }
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Process the command through game engine
    const result = await processGameCommand(existingPlayer, command);
    
    // Apply any player updates if the command was successful
    if (result.success && result.playerUpdates) {
      await db.update(players)
        .set(result.playerUpdates)
        .where(eq(players.userId, userId));
    }
    
    // Apply any magic profile updates if the command was successful
    if (result.success && result.magicProfileUpdates && existingPlayer.magicProfile) {
      await db.update(magicProfiles)
        .set({
          ...result.magicProfileUpdates,
          updatedAt: new Date()
        })
        .where(eq(magicProfiles.id, existingPlayer.magicProfile.id));
    }
    
    res.json(result);
  } catch (error) {
    console.error(`Error processing command for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to process command' });
  }
});

// Get available quests for player
router.get('/api/player/:userId/available-quests', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get quests available in player's current region and level
    const availableQuests = await db.query.quests.findMany({
      where: and(
        eq(quests.region, existingPlayer.locationRegion),
        eq(quests.requiredLevel, existingPlayer.level)
      )
    });
    
    // Get player's active and completed quests to filter out
    const playerQuestsList = await db.query.playerQuests.findMany({
      where: eq(playerQuests.playerId, existingPlayer.id),
      with: {
        quest: true
      }
    });
    
    const playerQuestIds = new Set(playerQuestsList.map(pq => pq.questId));
    
    // Filter out quests player already has
    const filteredQuests = availableQuests.filter(quest => !playerQuestIds.has(quest.id));
    
    res.json(filteredQuests);
  } catch (error) {
    console.error(`Error fetching available quests for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to fetch available quests' });
  }
});

// Accept a quest
router.post('/api/player/:userId/quests', async (req, res) => {
  try {
    const { userId } = req.params;
    const { questId } = req.body;
    
    if (!questId) {
      return res.status(400).json({ error: 'Quest ID is required' });
    }
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Check if quest exists
    const quest = await db.query.quests.findFirst({
      where: eq(quests.id, questId)
    });
    
    if (!quest) {
      return res.status(404).json({ error: 'Quest not found' });
    }
    
    // Check if player already has this quest
    const existingPlayerQuest = await db.query.playerQuests.findFirst({
      where: and(
        eq(playerQuests.playerId, existingPlayer.id),
        eq(playerQuests.questId, questId)
      )
    });
    
    if (existingPlayerQuest) {
      return res.status(400).json({ error: 'Player already has this quest' });
    }
    
    // Check if player meets requirements
    if (existingPlayer.level < quest.requiredLevel) {
      return res.status(400).json({ 
        error: `Player level (${existingPlayer.level}) is too low for this quest (requires level ${quest.requiredLevel})`
      });
    }
    
    if (existingPlayer.locationRegion !== quest.region) {
      return res.status(400).json({ 
        error: `Player is not in the correct region for this quest (requires ${quest.region})`
      });
    }
    
    // Add quest to player's quest log
    const [newPlayerQuest] = await db.insert(playerQuests)
      .values({
        playerId: existingPlayer.id,
        questId: questId,
        status: 'active',
        progress: {} // Initialize empty progress object
      })
      .returning();
    
    // Return with quest details
    const result = {
      ...newPlayerQuest,
      quest
    };
    
    res.status(201).json(result);
  } catch (error) {
    console.error(`Error accepting quest for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to accept quest' });
  }
});

// Get information about the current location
router.get('/api/player/:userId/location', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId)
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get region information
    const region = await db.query.regions.findFirst({
      where: eq(regions.name, existingPlayer.locationRegion)
    });
    
    if (!region) {
      return res.status(404).json({ error: 'Region not found' });
    }
    
    // Get area information
    const area = await db.query.areas.findFirst({
      where: and(
        eq(areas.regionId, region.id),
        eq(areas.name, existingPlayer.locationArea)
      )
    });
    
    if (!area) {
      return res.status(404).json({ error: 'Area not found' });
    }
    
    // Return combined location information
    const locationInfo = {
      region,
      area
    };
    
    res.json(locationInfo);
  } catch (error) {
    console.error(`Error fetching location for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to fetch location information' });
  }
});

// Get available crafting recipes
router.get('/api/player/:userId/crafting/recipes', async (req, res) => {
  try {
    const { userId } = req.params;
    
    // Find player first
    const existingPlayer = await db.query.players.findFirst({
      where: eq(players.userId, userId),
      with: {
        magicProfile: true
      }
    });
    
    if (!existingPlayer) {
      return res.status(404).json({ error: 'Player not found' });
    }
    
    // Get player's crafting skills
    const playerSkills = await db.query.playerCraftingSkills.findMany({
      where: eq(playerCraftingSkills.playerId, existingPlayer.id)
    });
    
    // Get all recipes that match player's level and magic affinity
    const availableRecipes = await db.query.craftingRecipes.findMany({
      where: and(
        eq(craftingRecipes.requiredLevel, existingPlayer.level)
      )
    });
    
    // Filter by magic affinity if applicable
    const filteredRecipes = availableRecipes.filter(recipe => {
      // If recipe doesn't require magic affinity, it's available
      if (!recipe.requiredMagicAffinity) {
        return true;
      }
      
      // Check if player has the required magic affinity
      return existingPlayer.magicProfile?.magicAffinity === recipe.requiredMagicAffinity;
    });
    
    // Include only recipes player has learned
    const knownRecipeIds = new Set();
    
    // Combine all known recipe IDs from player's skills
    playerSkills.forEach(skill => {
      if (skill.knownRecipes) {
        skill.knownRecipes.forEach(recipeId => knownRecipeIds.add(recipeId));
      }
    });
    
    // Final filtering by known recipes
    const knownRecipes = filteredRecipes.filter(recipe => knownRecipeIds.has(recipe.id));
    
    res.json(knownRecipes);
  } catch (error) {
    console.error(`Error fetching crafting recipes for player ${req.params.userId}:`, error);
    res.status(500).json({ error: 'Failed to fetch crafting recipes' });
  }
});

export default router;