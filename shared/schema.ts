import { pgTable, text, serial, integer, boolean, timestamp, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";
import { relations } from "drizzle-orm";

// Users Table
export const users = pgTable("users", {
  id: serial("id").primaryKey(),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

// Game Sessions Table
export const gameSessions = pgTable("game_sessions", {
  id: serial("id").primaryKey(),
  userId: integer("user_id").references(() => users.id),
  gameState: jsonb("game_state").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertGameSessionSchema = createInsertSchema(gameSessions);

// Characters Table
export const characters = pgTable("characters", {
  id: serial("id").primaryKey(),
  gameSessionId: integer("game_session_id").references(() => gameSessions.id).notNull(),
  name: text("name").notNull(),
  characterClass: text("character_class").notNull(),
  background: text("background").notNull(),
  level: integer("level").notNull().default(1),
  xp: integer("xp").notNull().default(0),
  stats: jsonb("stats").notNull(),
  maxHealth: integer("max_health").notNull(),
  currentHealth: integer("current_health").notNull(),
  maxMana: integer("max_mana").notNull(),
  currentMana: integer("current_mana").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertCharacterSchema = createInsertSchema(characters);

// Inventory Items Table
export const inventoryItems = pgTable("inventory_items", {
  id: serial("id").primaryKey(),
  characterId: integer("character_id").references(() => characters.id).notNull(),
  name: text("name").notNull(),
  description: text("description"),
  quantity: integer("quantity").notNull().default(1),
  weight: integer("weight").notNull().default(1),
  type: text("type").notNull(), // weapon, armor, potion, etc.
  properties: jsonb("properties"), // damage, armor, effects, etc.
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertInventoryItemSchema = createInsertSchema(inventoryItems);

// Quests Table
export const quests = pgTable("quests", {
  id: serial("id").primaryKey(),
  gameSessionId: integer("game_session_id").references(() => gameSessions.id).notNull(),
  title: text("title").notNull(),
  description: text("description").notNull(),
  status: text("status").notNull().default("active"), // active, completed, failed
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertQuestSchema = createInsertSchema(quests);

// Memory Entries Table (for LangChain long-term memory)
export const memoryEntries = pgTable("memory_entries", {
  id: serial("id").primaryKey(),
  gameSessionId: integer("game_session_id").references(() => gameSessions.id).notNull(),
  type: text("type").notNull(), // world_event, npc_interaction, player_action, etc.
  content: text("content").notNull(),
  metadata: jsonb("metadata"),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const insertMemoryEntrySchema = createInsertSchema(memoryEntries);

// Locations Table
export const locations = pgTable("locations", {
  id: serial("id").primaryKey(),
  name: text("name").notNull(),
  description: text("description").notNull(),
  type: text("type").notNull(), // town, dungeon, wilderness, etc.
  connections: jsonb("connections"), // IDs of connected locations
  npcs: jsonb("npcs"), // NPCs present in this location
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().notNull(),
});

export const insertLocationSchema = createInsertSchema(locations);

// Define relations
export const gameSessionsRelations = relations(gameSessions, ({ one, many }) => ({
  user: one(users, { fields: [gameSessions.userId], references: [users.id] }),
  characters: many(characters),
  quests: many(quests),
  memoryEntries: many(memoryEntries),
}));

export const charactersRelations = relations(characters, ({ one, many }) => ({
  gameSession: one(gameSessions, { fields: [characters.gameSessionId], references: [gameSessions.id] }),
  inventoryItems: many(inventoryItems),
}));

export const inventoryItemsRelations = relations(inventoryItems, ({ one }) => ({
  character: one(characters, { fields: [inventoryItems.characterId], references: [characters.id] }),
}));

export const questsRelations = relations(quests, ({ one }) => ({
  gameSession: one(gameSessions, { fields: [quests.gameSessionId], references: [gameSessions.id] }),
}));

export const memoryEntriesRelations = relations(memoryEntries, ({ one }) => ({
  gameSession: one(gameSessions, { fields: [memoryEntries.gameSessionId], references: [gameSessions.id] }),
}));

// Types
export type User = typeof users.$inferSelect;
export type GameSession = typeof gameSessions.$inferSelect;
export type Character = typeof characters.$inferSelect;
export type InventoryItem = typeof inventoryItems.$inferSelect;
export type Quest = typeof quests.$inferSelect;
export type MemoryEntry = typeof memoryEntries.$inferSelect;
export type Location = typeof locations.$inferSelect;

// Insert Types
export type InsertUser = z.infer<typeof insertUserSchema>;
export type InsertGameSession = z.infer<typeof insertGameSessionSchema>;
export type InsertCharacter = z.infer<typeof insertCharacterSchema>;
export type InsertInventoryItem = z.infer<typeof insertInventoryItemSchema>;
export type InsertQuest = z.infer<typeof insertQuestSchema>;
export type InsertMemoryEntry = z.infer<typeof insertMemoryEntrySchema>;
export type InsertLocation = z.infer<typeof insertLocationSchema>;
