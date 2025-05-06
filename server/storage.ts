import { db } from '@db';
import * as schema from '@shared/schema';
import * as types from '@shared/types';

class StorageService {
  /**
   * Get a location by ID
   */
  async getLocationById(locationId: number): Promise<types.Location | null> {
    try {
      const location = await db.query.locations.findFirst({
        where: (locations, { eq }) => eq(locations.id, locationId)
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
      // Check if the game session exists
      let gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameState.gameId)
      });
      
      if (!gameSession) {
        // Create a new game session
        const [newSession] = await db.insert(schema.gameSessions)
          .values({
            gameState: gameState as any,
            updatedAt: new Date()
          })
          .returning();
        
        gameSession = newSession;
      } else {
        // Update existing game session
        await db.update(schema.gameSessions)
          .set({
            gameState: gameState as any,
            updatedAt: new Date()
          })
          .where((sessions, { eq }) => eq(sessions.id, gameSession!.id));
      }
      
      // Save character if it exists
      if (gameState.character) {
        const character = gameState.character;
        
        // Check if the character exists
        const existingCharacter = await db.query.characters.findFirst({
          where: (characters, { eq, and }) => and(
            eq(characters.gameSessionId, gameSession!.id),
            eq(characters.name, character.name)
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
            .where((characters, { eq }) => eq(characters.id, existingCharacter.id));
        }
      }
      
      // Save inventory items if they exist
      if (gameState.inventory && gameState.inventory.items.length > 0 && gameState.character) {
        // Get character ID
        const character = await db.query.characters.findFirst({
          where: (characters, { eq, and }) => and(
            eq(characters.gameSessionId, gameSession!.id),
            eq(characters.name, gameState.character.name)
          )
        });
        
        if (character) {
          // Delete existing inventory items
          await db.delete(schema.inventoryItems)
            .where((items, { eq }) => eq(items.characterId, character.id));
          
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
          .where((quests, { eq }) => eq(quests.gameSessionId, gameSession!.id));
        
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
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameId)
      });
      
      if (!gameSession) {
        return null;
      }
      
      return gameSession.gameState as unknown as types.GameState;
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
      let query = db.query.gameSessions;
      
      const gameSessions = userId
        ? await query.findMany({
            where: (sessions, { eq }) => eq(sessions.userId, userId),
            orderBy: (sessions, { desc }) => [desc(sessions.updatedAt)]
          })
        : await query.findMany({
            orderBy: (sessions, { desc }) => [desc(sessions.updatedAt)]
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
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameId)
      });
      
      if (!gameSession) {
        return false;
      }
      
      // Delete all associated records
      await db.delete(schema.memoryEntries)
        .where((entries, { eq }) => eq(entries.gameSessionId, gameSession.id));
      
      const characters = await db.query.characters.findMany({
        where: (characters, { eq }) => eq(characters.gameSessionId, gameSession.id)
      });
      
      for (const character of characters) {
        await db.delete(schema.inventoryItems)
          .where((items, { eq }) => eq(items.characterId, character.id));
      }
      
      await db.delete(schema.characters)
        .where((characters, { eq }) => eq(characters.gameSessionId, gameSession.id));
      
      await db.delete(schema.quests)
        .where((quests, { eq }) => eq(quests.gameSessionId, gameSession.id));
      
      await db.delete(schema.gameSessions)
        .where((sessions, { eq }) => eq(sessions.id, gameSession.id));
      
      return true;
    } catch (error) {
      console.error('Error deleting game:', error);
      return false;
    }
  }
}

export const storage = new StorageService();
