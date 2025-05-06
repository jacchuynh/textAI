import { db } from '@db';
import { pool } from '@db';
import * as schema from '@shared/schema';
import * as types from '@shared/types';
import { eq, and, desc } from 'drizzle-orm';

class StorageService {
  /**
   * Get a location by ID
   */
  async getLocationById(locationId: number): Promise<types.Location | null> {
    try {
      const location = await db.query.locations.findFirst({
        where: eq(schema.locations.id, locationId)
      });
      
      if (!location) {
        return null;
      }
      
      return {
        id: location.id,
        name: location.name,
        description: location.description,
        type: location.type,
        connections: location.connections as number[] | undefined,
        npcs: location.npcs as types.NPC[] | undefined
      };
    } catch (error) {
      console.error('Error getting location:', error);
      return null;
    }
  }

  /**
   * Save a game state
   */
  async saveGameState(gameState: types.GameState): Promise<void> {
    try {
      console.log('Saving game state with ID:', gameState.gameId);

      // Find by the gameId in the JSON field
      const result = await pool.query(
        `SELECT * FROM game_sessions WHERE game_state->>'gameId' = $1`,
        [gameState.gameId]
      );
      
      let gameSession = result.rows.length > 0 ? result.rows[0] : null;
      
      if (!gameSession) {
        console.log('Creating new game session for ID:', gameState.gameId);
        // Create a new game session
        const [newSession] = await db.insert(schema.gameSessions)
          .values({
            gameState: gameState as any,
            updatedAt: new Date()
          })
          .returning();
        
        gameSession = newSession;
      } else {
        console.log('Updating existing game session for ID:', gameState.gameId);
        // Update existing game session
        await db.update(schema.gameSessions)
          .set({
            gameState: gameState as any,
            updatedAt: new Date()
          })
          .where(eq(schema.gameSessions.id, gameSession.id));
      }
      
      // Save character if it exists
      if (gameState.character) {
        const character = gameState.character;
        
        // Check if the character exists
        const existingCharacter = await db.query.characters.findFirst({
          where: and(
            eq(schema.characters.gameSessionId, gameSession.id),
            eq(schema.characters.name, character.name)
          )
        });
        
        if (!existingCharacter) {
          // Create new character
          await db.insert(schema.characters)
            .values({
              gameSessionId: gameSession.id,
              name: character.name,
              characterClass: character.class,
              background: character.background,
              level: character.level,
              xp: character.xp,
              stats: character.stats as any,
              maxHealth: character.maxHealth,
              currentHealth: character.currentHealth,
              maxMana: character.maxMana,
              currentMana: character.currentMana
            });
        } else {
          // Update existing character
          await db.update(schema.characters)
            .set({
              level: character.level,
              xp: character.xp,
              stats: character.stats as any,
              maxHealth: character.maxHealth,
              currentHealth: character.currentHealth,
              maxMana: character.maxMana,
              currentMana: character.currentMana,
              updatedAt: new Date()
            })
            .where(eq(schema.characters.id, existingCharacter.id));
        }
      }
      
      // Save inventory items if they exist
      if (gameState.inventory && gameState.inventory.items.length > 0 && gameState.character) {
        // Get character ID
        const character = await db.query.characters.findFirst({
          where: and(
            eq(schema.characters.gameSessionId, gameSession.id),
            eq(schema.characters.name, gameState.character.name)
          )
        });
        
        if (character) {
          // Delete existing inventory items
          await db.delete(schema.inventoryItems)
            .where(eq(schema.inventoryItems.characterId, character.id));
          
          // Insert new inventory items
          for (const item of gameState.inventory.items) {
            await db.insert(schema.inventoryItems)
              .values({
                characterId: character.id,
                name: item.name,
                description: item.description || '',
                quantity: item.quantity,
                weight: item.weight,
                type: item.type,
                properties: item.properties as any
              });
          }
        }
      }
      
      // Save quests if they exist
      if (gameState.quests && gameState.quests.length > 0) {
        // Delete existing quests
        await db.delete(schema.quests)
          .where(eq(schema.quests.gameSessionId, gameSession.id));
        
        // Insert new quests
        for (const quest of gameState.quests) {
          await db.insert(schema.quests)
            .values({
              gameSessionId: gameSession.id,
              title: quest.title,
              description: quest.description,
              status: quest.status
            });
        }
      }
    } catch (error) {
      console.error('Error saving game state:', error);
    }
  }

  /**
   * Get a game state by ID
   */
  async getGameState(gameId: string): Promise<types.GameState | null> {
    try {
      console.log('Getting game state for ID:', gameId);
      
      const result = await pool.query(
        `SELECT * FROM game_sessions WHERE game_state->>'gameId' = $1`,
        [gameId]
      );
      
      const gameSession = result.rows.length > 0 ? result.rows[0] : null;
      
      if (!gameSession) {
        console.log('Game session not found for ID:', gameId);
        return null;
      }
      
      console.log('Found game session for ID:', gameId);
      return gameSession.game_state as unknown as types.GameState;
    } catch (error) {
      console.error('Error getting game state:', error);
      return null;
    }
  }

  /**
   * Get all saved games for a user
   */
  async getSavedGames(userId?: number): Promise<{ id: string; name: string; updatedAt: string }[]> {
    try {
      const gameSessions = userId
        ? await db.query.gameSessions.findMany({
            where: eq(schema.gameSessions.userId, userId),
            orderBy: [desc(schema.gameSessions.updatedAt)]
          })
        : await db.query.gameSessions.findMany({
            orderBy: [desc(schema.gameSessions.updatedAt)]
          });
      
      return gameSessions.map(session => {
        const gameState = session.gameState as unknown as types.GameState;
        return {
          id: session.id.toString(),
          name: gameState.character?.name || `Game ${session.id}`,
          updatedAt: session.updatedAt.toISOString()
        };
      });
    } catch (error) {
      console.error('Error getting saved games:', error);
      return [];
    }
  }

  /**
   * Delete a saved game
   */
  async deleteGame(gameId: string): Promise<boolean> {
    try {
      const result = await pool.query(
        `SELECT * FROM game_sessions WHERE game_state->>'gameId' = $1`,
        [gameId]
      );
      
      const gameSession = result.rows.length > 0 ? result.rows[0] : null;
      
      if (!gameSession) {
        return false;
      }
      
      // Delete all associated records
      await db.delete(schema.memoryEntries)
        .where(eq(schema.memoryEntries.gameSessionId, gameSession.id));
      
      const characters = await db.query.characters.findMany({
        where: eq(schema.characters.gameSessionId, gameSession.id)
      });
      
      for (const character of characters) {
        await db.delete(schema.inventoryItems)
          .where(eq(schema.inventoryItems.characterId, character.id));
      }
      
      await db.delete(schema.characters)
        .where(eq(schema.characters.gameSessionId, gameSession.id));
      
      await db.delete(schema.quests)
        .where(eq(schema.quests.gameSessionId, gameSession.id));
      
      await db.delete(schema.gameSessions)
        .where(eq(schema.gameSessions.id, gameSession.id));
      
      return true;
    } catch (error) {
      console.error('Error deleting game:', error);
      return false;
    }
  }
}

export const storage = new StorageService();
