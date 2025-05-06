import { db } from '@db';
import * as schema from '@shared/schema';
import * as types from '@shared/types';

export class MemoryManager {
  /**
   * Add a new memory entry to the long-term memory
   */
  async addMemory(
    gameSessionId: string,
    type: "world_event" | "npc_interaction" | "player_action",
    content: string,
    metadata?: Record<string, any>
  ): Promise<void> {
    try {
      // Find the numeric game session id from the string id
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameSessionId)
      });
      
      if (!gameSession) {
        console.error(`Game session not found: ${gameSessionId}`);
        return;
      }
      
      // Insert the memory entry
      await db.insert(schema.memoryEntries).values({
        gameSessionId: gameSession.id,
        type,
        content,
        metadata: metadata || null,
      });
    } catch (error) {
      console.error('Error adding memory:', error);
    }
  }

  /**
   * Get recent memory entries for a game session
   */
  async getRecentMemories(
    gameSessionId: string,
    limit: number = 10
  ): Promise<types.MemoryEntry[]> {
    try {
      // Find the numeric game session id from the string id
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameSessionId)
      });
      
      if (!gameSession) {
        console.error(`Game session not found: ${gameSessionId}`);
        return [];
      }
      
      // Get the most recent memory entries
      const memories = await db.query.memoryEntries.findMany({
        where: (entries, { eq }) => eq(entries.gameSessionId, gameSession.id),
        orderBy: (entries, { desc }) => [desc(entries.createdAt)],
        limit
      });
      
      // Map to the MemoryEntry type
      return memories.map(memory => ({
        id: memory.id,
        type: memory.type as "world_event" | "npc_interaction" | "player_action",
        content: memory.content,
        metadata: memory.metadata as Record<string, any> | undefined,
        timestamp: memory.createdAt.toISOString()
      }));
    } catch (error) {
      console.error('Error getting recent memories:', error);
      return [];
    }
  }

  /**
   * Search memory entries by relevance to a query
   * In a real implementation, this would use a vector database for similarity search
   */
  async searchMemoriesByRelevance(
    gameSessionId: string,
    query: string,
    limit: number = 5
  ): Promise<types.MemoryEntry[]> {
    try {
      // Find the numeric game session id from the string id
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameSessionId)
      });
      
      if (!gameSession) {
        console.error(`Game session not found: ${gameSessionId}`);
        return [];
      }
      
      // For now, we'll do a simple text search
      // In a production app, this would use a vector database or at least full-text search
      const memories = await db.query.memoryEntries.findMany({
        where: (entries, { eq, and, or, like }) => and(
          eq(entries.gameSessionId, gameSession.id),
          or(
            like(entries.content, `%${query}%`),
            like(entries.type, `%${query}%`)
          )
        ),
        orderBy: (entries, { desc }) => [desc(entries.createdAt)],
        limit
      });
      
      // Map to the MemoryEntry type
      return memories.map(memory => ({
        id: memory.id,
        type: memory.type as "world_event" | "npc_interaction" | "player_action",
        content: memory.content,
        metadata: memory.metadata as Record<string, any> | undefined,
        timestamp: memory.createdAt.toISOString()
      }));
    } catch (error) {
      console.error('Error searching memories:', error);
      return [];
    }
  }

  /**
   * Delete old memories beyond a certain count to prevent the database from growing too large
   */
  async pruneOldMemories(gameSessionId: string, keepCount: number = 100): Promise<void> {
    try {
      // Find the numeric game session id from the string id
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameSessionId)
      });
      
      if (!gameSession) {
        console.error(`Game session not found: ${gameSessionId}`);
        return;
      }
      
      // Get total count of memories for this session
      const countResult = await db.query.memoryEntries.findMany({
        where: (entries, { eq }) => eq(entries.gameSessionId, gameSession.id),
        columns: { id: true }
      });
      
      const totalCount = countResult.length;
      
      if (totalCount <= keepCount) {
        // No need to prune
        return;
      }
      
      // Get IDs of memories to keep (the most recent ones)
      const memoriesToKeep = await db.query.memoryEntries.findMany({
        where: (entries, { eq }) => eq(entries.gameSessionId, gameSession.id),
        orderBy: (entries, { desc }) => [desc(entries.createdAt)],
        limit: keepCount,
        columns: { id: true }
      });
      
      const keepIds = memoriesToKeep.map(m => m.id);
      
      // Delete memories that are not in the keep list
      await db.delete(schema.memoryEntries)
        .where((entries, { eq, and, notInArray }) => and(
          eq(entries.gameSessionId, gameSession.id),
          notInArray(entries.id, keepIds)
        ));
      
    } catch (error) {
      console.error('Error pruning old memories:', error);
    }
  }

  /**
   * Get the summary of a game session
   * This is a simplified implementation - in a real app, 
   * you might want to use an LLM to generate a summary
   */
  async getGameSummary(gameSessionId: string): Promise<string> {
    try {
      // Find the numeric game session id from the string id
      const gameSession = await db.query.gameSessions.findFirst({
        where: (sessions, { eq }) => eq(sessions.id.toString(), gameSessionId)
      });
      
      if (!gameSession) {
        console.error(`Game session not found: ${gameSessionId}`);
        return "Game session not found.";
      }
      
      // Get important memories (world events)
      const worldEvents = await db.query.memoryEntries.findMany({
        where: (entries, { eq, and }) => and(
          eq(entries.gameSessionId, gameSession.id),
          eq(entries.type, "world_event")
        ),
        orderBy: (entries, { asc }) => [asc(entries.createdAt)],
        limit: 10
      });
      
      if (worldEvents.length === 0) {
        return "No significant events have occurred yet.";
      }
      
      // Compile a simple summary
      return `Game Summary:\n${worldEvents.map(event => `- ${event.content}`).join('\n')}`;
    } catch (error) {
      console.error('Error getting game summary:', error);
      return "Unable to retrieve game summary.";
    }
  }
}
