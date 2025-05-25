import { pgTable, serial, text, integer, timestamp, json, boolean, decimal } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { relations } from 'drizzle-orm';
import { z } from 'zod';

// Players table
export const players = pgTable('players', {
  id: serial('id').primaryKey(),
  userId: text('user_id').notNull(), // Link to authentication system
  name: text('name').notNull(),
  level: integer('level').notNull().default(1),
  experience: integer('experience').notNull().default(0),
  gold: integer('gold').notNull().default(100),
  healthCurrent: integer('health_current').notNull().default(100),
  healthMax: integer('health_max').notNull().default(100),
  locationRegion: text('location_region').notNull().default('emerald_vale'),
  locationArea: text('location_area').notNull().default('crossroads'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Magic profiles table
export const magicProfiles = pgTable('magic_profiles', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  manaCurrent: integer('mana_current').notNull().default(50),
  manaMax: integer('mana_max').notNull().default(50),
  manaRegenRate: decimal('mana_regen_rate').notNull().default('1.0'),
  primaryDomains: json('primary_domains').notNull().default(['ARCANE']),
  secondaryDomains: json('secondary_domains').notNull().default([]),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Spells table
export const spells = pgTable('spells', {
  id: serial('id').primaryKey(),
  spellId: text('spell_id').notNull().unique(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  domains: json('domains').notNull(),
  damageTypes: json('damage_types').notNull(),
  effectTypes: json('effect_types').notNull(),
  manaCost: integer('mana_cost').notNull(),
  castingTime: decimal('casting_time').notNull(),
  cooldown: decimal('cooldown').notNull(),
  basePower: decimal('base_power').notNull(),
  levelReq: integer('level_req').notNull(),
  tier: text('tier').notNull(),
  targetingType: text('targeting_type').notNull(),
  rangeMax: decimal('range_max').notNull(),
  duration: decimal('duration').notNull().default('0'),
  components: json('components').notNull().default([]),
  tags: json('tags').notNull().default([]),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Known spells for each player
export const playerSpells = pgTable('player_spells', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  spellId: integer('spell_id').references(() => spells.id).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Items table
export const items = pgTable('items', {
  id: serial('id').primaryKey(),
  itemId: text('item_id').notNull().unique(),
  name: text('name').notNull(),
  type: text('type').notNull(), // weapon, armor, consumable, etc.
  description: text('description').notNull(),
  value: integer('value').notNull().default(0),
  stats: json('stats').notNull().default({}), // damage, defense, etc.
  tags: json('tags').notNull().default([]),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player inventory items
export const playerItems = pgTable('player_items', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  itemId: integer('item_id').references(() => items.id).notNull(),
  quantity: integer('quantity').notNull().default(1),
  equipped: boolean('equipped').notNull().default(false),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Materials table
export const materials = pgTable('materials', {
  id: serial('id').primaryKey(),
  materialId: text('material_id').notNull().unique(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  value: integer('value').notNull().default(0),
  rarity: text('rarity').notNull().default('common'),
  tags: json('tags').notNull().default([]),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player materials
export const playerMaterials = pgTable('player_materials', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  materialId: integer('material_id').references(() => materials.id).notNull(),
  quantity: integer('quantity').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Quests table
export const quests = pgTable('quests', {
  id: serial('id').primaryKey(),
  questId: text('quest_id').notNull().unique(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  giver: text('giver').notNull(),
  rewards: json('rewards').notNull().default({}),
  status: text('status').notNull().default('available'), // available, offered, active, completed
  locationRegion: text('location_region'),
  locationArea: text('location_area'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Quest stages
export const questStages = pgTable('quest_stages', {
  id: serial('id').primaryKey(),
  questId: integer('quest_id').references(() => quests.id).notNull(),
  stageId: text('stage_id').notNull(),
  description: text('description').notNull(),
  target: json('target').notNull().default({}),
  order: integer('order').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player quests
export const playerQuests = pgTable('player_quests', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  questId: integer('quest_id').references(() => quests.id).notNull(),
  status: text('status').notNull().default('active'), // active, completed
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Player quest stages progress
export const playerQuestStages = pgTable('player_quest_stages', {
  id: serial('id').primaryKey(),
  playerQuestId: integer('player_quest_id').references(() => playerQuests.id).notNull(),
  stageId: integer('stage_id').references(() => questStages.id).notNull(),
  completed: boolean('completed').notNull().default(false),
  progress: json('progress').notNull().default({}), // For tracking kill counts, etc.
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Define relationships
export const playersRelations = relations(players, ({ many, one }) => ({
  magicProfile: one(magicProfiles, {
    fields: [players.id],
    references: [magicProfiles.playerId]
  }),
  playerItems: many(playerItems),
  playerMaterials: many(playerMaterials),
  playerQuests: many(playerQuests),
  playerSpells: many(playerSpells)
}));

export const magicProfilesRelations = relations(magicProfiles, ({ one }) => ({
  player: one(players, {
    fields: [magicProfiles.playerId],
    references: [players.id]
  })
}));

export const spellsRelations = relations(spells, ({ many }) => ({
  playerSpells: many(playerSpells)
}));

export const playerSpellsRelations = relations(playerSpells, ({ one }) => ({
  player: one(players, {
    fields: [playerSpells.playerId],
    references: [players.id]
  }),
  spell: one(spells, {
    fields: [playerSpells.spellId],
    references: [spells.id]
  })
}));

export const itemsRelations = relations(items, ({ many }) => ({
  playerItems: many(playerItems)
}));

export const playerItemsRelations = relations(playerItems, ({ one }) => ({
  player: one(players, {
    fields: [playerItems.playerId],
    references: [players.id]
  }),
  item: one(items, {
    fields: [playerItems.itemId],
    references: [items.id]
  })
}));

export const materialsRelations = relations(materials, ({ many }) => ({
  playerMaterials: many(playerMaterials)
}));

export const playerMaterialsRelations = relations(playerMaterials, ({ one }) => ({
  player: one(players, {
    fields: [playerMaterials.playerId],
    references: [players.id]
  }),
  material: one(materials, {
    fields: [playerMaterials.materialId],
    references: [materials.id]
  })
}));

export const questsRelations = relations(quests, ({ many }) => ({
  stages: many(questStages),
  playerQuests: many(playerQuests)
}));

export const questStagesRelations = relations(questStages, ({ one, many }) => ({
  quest: one(quests, {
    fields: [questStages.questId],
    references: [quests.id]
  }),
  playerQuestStages: many(playerQuestStages)
}));

export const playerQuestsRelations = relations(playerQuests, ({ one, many }) => ({
  player: one(players, {
    fields: [playerQuests.playerId],
    references: [players.id]
  }),
  quest: one(quests, {
    fields: [playerQuests.questId],
    references: [quests.id]
  }),
  stages: many(playerQuestStages)
}));

export const playerQuestStagesRelations = relations(playerQuestStages, ({ one }) => ({
  playerQuest: one(playerQuests, {
    fields: [playerQuestStages.playerQuestId],
    references: [playerQuests.id]
  }),
  stage: one(questStages, {
    fields: [playerQuestStages.stageId],
    references: [questStages.id]
  })
}));

// Create Zod schemas for validation
export const playersInsertSchema = createInsertSchema(players, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters")
});
export type PlayerInsert = z.infer<typeof playersInsertSchema>;
export const playersSelectSchema = createSelectSchema(players);
export type Player = z.infer<typeof playersSelectSchema>;

export const magicProfilesInsertSchema = createInsertSchema(magicProfiles);
export type MagicProfileInsert = z.infer<typeof magicProfilesInsertSchema>;
export const magicProfilesSelectSchema = createSelectSchema(magicProfiles);
export type MagicProfile = z.infer<typeof magicProfilesSelectSchema>;

export const spellsInsertSchema = createInsertSchema(spells, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters"),
  description: (schema) => schema.min(10, "Description must be at least 10 characters")
});
export type SpellInsert = z.infer<typeof spellsInsertSchema>;
export const spellsSelectSchema = createSelectSchema(spells);
export type Spell = z.infer<typeof spellsSelectSchema>;

export const itemsInsertSchema = createInsertSchema(items, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters"),
  description: (schema) => schema.min(10, "Description must be at least 10 characters")
});
export type ItemInsert = z.infer<typeof itemsInsertSchema>;
export const itemsSelectSchema = createSelectSchema(items);
export type Item = z.infer<typeof itemsSelectSchema>;

export const materialsInsertSchema = createInsertSchema(materials, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters"),
  description: (schema) => schema.min(10, "Description must be at least 10 characters")
});
export type MaterialInsert = z.infer<typeof materialsInsertSchema>;
export const materialsSelectSchema = createSelectSchema(materials);
export type Material = z.infer<typeof materialsSelectSchema>;

export const questsInsertSchema = createInsertSchema(quests, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters"),
  description: (schema) => schema.min(10, "Description must be at least 10 characters")
});
export type QuestInsert = z.infer<typeof questsInsertSchema>;
export const questsSelectSchema = createSelectSchema(quests);
export type Quest = z.infer<typeof questsSelectSchema>;

export const questStagesInsertSchema = createInsertSchema(questStages, {
  description: (schema) => schema.min(10, "Description must be at least 10 characters")
});
export type QuestStageInsert = z.infer<typeof questStagesInsertSchema>;
export const questStagesSelectSchema = createSelectSchema(questStages);
export type QuestStage = z.infer<typeof questStagesSelectSchema>;