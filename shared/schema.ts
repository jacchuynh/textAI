import { pgTable, serial, text, integer, timestamp, decimal, json, boolean } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { relations } from 'drizzle-orm';
import { z } from 'zod';

// Players table
export const players = pgTable('players', {
  id: serial('id').primaryKey(),
  userId: text('user_id').notNull().unique(),
  name: text('name').notNull(),
  level: integer('level').notNull().default(1),
  experience: integer('experience').notNull().default(0),
  gold: integer('gold').notNull().default(50),
  healthCurrent: integer('health_current').notNull().default(100),
  healthMax: integer('health_max').notNull().default(100),
  locationRegion: text('location_region').notNull(),
  locationArea: text('location_area').notNull(),
  locationCoordinates: json('location_coordinates').notNull(),
  inventory: json('inventory').$type<Record<string, any>>().default({}),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Magic profiles table
export const magicProfiles = pgTable('magic_profiles', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  magicAffinity: text('magic_affinity').notNull(),
  manaCapacity: integer('mana_capacity').notNull().default(100),
  manaCurrent: integer('mana_current').notNull().default(100),
  knownAspects: text('known_aspects').array().notNull(),
  manaRegenRate: decimal('mana_regen_rate').notNull().default('5.0'),
  spellPower: integer('spell_power').notNull().default(10),
  spellMastery: integer('spell_mastery').notNull().default(1),
  magicResistance: integer('magic_resistance').notNull().default(0),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Spells table
export const spells = pgTable('spells', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  aspect: text('aspect').notNull(),
  manaCost: integer('mana_cost').notNull(),
  castTime: decimal('cast_time').notNull(),
  cooldown: decimal('cooldown').notNull(),
  effects: json('effects').$type<Record<string, any>>().notNull(),
  requiredLevel: integer('required_level').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player spells (junction table)
export const playerSpells = pgTable('player_spells', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  spellId: integer('spell_id').references(() => spells.id).notNull(),
  masteryLevel: integer('mastery_level').notNull().default(1),
  favorite: boolean('favorite').notNull().default(false),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Items table
export const items = pgTable('items', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  type: text('type').notNull(), // weapon, armor, potion, material, etc.
  rarity: text('rarity').notNull(), // common, uncommon, rare, epic, legendary
  value: integer('value').notNull(),
  stats: json('stats').$type<Record<string, any>>().default({}),
  magicProperties: json('magic_properties').$type<Record<string, any>>().default({}),
  requiredLevel: integer('required_level').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player items (inventory)
export const playerItems = pgTable('player_items', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  itemId: integer('item_id').references(() => items.id).notNull(),
  quantity: integer('quantity').notNull().default(1),
  equipped: boolean('equipped').notNull().default(false),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Quests table
export const quests = pgTable('quests', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  description: text('description').notNull(),
  region: text('region').notNull(),
  requiredLevel: integer('required_level').notNull().default(1),
  rewards: json('rewards').$type<Record<string, any>>().notNull(),
  objectives: json('objectives').$type<Record<string, any>[]>().notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player quests (active and completed)
export const playerQuests = pgTable('player_quests', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  questId: integer('quest_id').references(() => quests.id).notNull(),
  status: text('status').notNull().default('active'), // active, completed, failed
  progress: json('progress').$type<Record<string, any>>().notNull(),
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at')
});

// Game regions
export const regions = pgTable('regions', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  climate: text('climate').notNull(),
  dangerLevel: integer('danger_level').notNull(),
  dominantMagicAspect: text('dominant_magic_aspect'),
  magicalProperties: json('magical_properties').$type<Record<string, any>>().default({}),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Region areas
export const areas = pgTable('areas', {
  id: serial('id').primaryKey(),
  regionId: integer('region_id').references(() => regions.id).notNull(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  terrain: text('terrain').notNull(),
  points_of_interest: json('points_of_interest').$type<Record<string, any>[]>().default([]),
  magicalFeatures: json('magical_features').$type<Record<string, any>>().default({}),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Magical materials
export const magicalMaterials = pgTable('magical_materials', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  aspect: text('aspect').notNull(),
  rarity: text('rarity').notNull(),
  potency: integer('potency').notNull().default(1),
  usages: json('usages').$type<string[]>().notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Crafting recipes
export const craftingRecipes = pgTable('crafting_recipes', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description').notNull(),
  category: text('category').notNull(), // blacksmithing, alchemy, etc.
  resultItemId: integer('result_item_id').references(() => items.id).notNull(),
  ingredients: json('ingredients').$type<{itemId: number, quantity: number}[]>().notNull(),
  requiredLevel: integer('required_level').notNull().default(1),
  requiredMagicAffinity: text('required_magic_affinity'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player crafting skills
export const playerCraftingSkills = pgTable('player_crafting_skills', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  skillName: text('skill_name').notNull(), // blacksmithing, alchemy, etc.
  level: integer('level').notNull().default(1),
  experience: integer('experience').notNull().default(0),
  knownRecipes: json('known_recipes').$type<number[]>().default([]),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull()
});

// Define relations
export const playersRelations = relations(players, ({ many, one }) => ({
  magicProfile: one(magicProfiles, {
    fields: [players.id],
    references: [magicProfiles.playerId],
  }),
  spells: many(playerSpells),
  items: many(playerItems),
  quests: many(playerQuests),
  craftingSkills: many(playerCraftingSkills)
}));

export const magicProfilesRelations = relations(magicProfiles, ({ one }) => ({
  player: one(players, {
    fields: [magicProfiles.playerId],
    references: [players.id],
  })
}));

export const spellsRelations = relations(spells, ({ many }) => ({
  players: many(playerSpells)
}));

export const playerSpellsRelations = relations(playerSpells, ({ one }) => ({
  player: one(players, {
    fields: [playerSpells.playerId],
    references: [players.id],
  }),
  spell: one(spells, {
    fields: [playerSpells.spellId],
    references: [spells.id],
  })
}));

export const itemsRelations = relations(items, ({ many }) => ({
  players: many(playerItems)
}));

export const playerItemsRelations = relations(playerItems, ({ one }) => ({
  player: one(players, {
    fields: [playerItems.playerId],
    references: [players.id],
  }),
  item: one(items, {
    fields: [playerItems.itemId],
    references: [items.id],
  })
}));

export const questsRelations = relations(quests, ({ many }) => ({
  players: many(playerQuests)
}));

export const playerQuestsRelations = relations(playerQuests, ({ one }) => ({
  player: one(players, {
    fields: [playerQuests.playerId],
    references: [players.id],
  }),
  quest: one(quests, {
    fields: [playerQuests.questId],
    references: [quests.id],
  })
}));

export const regionsRelations = relations(regions, ({ many }) => ({
  areas: many(areas)
}));

export const areasRelations = relations(areas, ({ one }) => ({
  region: one(regions, {
    fields: [areas.regionId],
    references: [regions.id],
  })
}));

export const magicalMaterialsRelations = relations(magicalMaterials, ({  }) => ({

}));

export const craftingRecipesRelations = relations(craftingRecipes, ({  }) => ({

}));

export const playerCraftingSkillsRelations = relations(playerCraftingSkills, ({  }) => ({

}));

// Zod schemas for validation
export const playerInsertSchema = createInsertSchema(players, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters"),
  locationRegion: (schema) => schema.min(1, "Region is required"),
  locationArea: (schema) => schema.min(1, "Area is required")
});
export type PlayerInsert = z.infer<typeof playerInsertSchema>;
export const playerSelectSchema = createSelectSchema(players);
export type Player = z.infer<typeof playerSelectSchema>;

export const magicProfileInsertSchema = createInsertSchema(magicProfiles, {
  knownAspects: z.array(z.string()).default(['basic'])
});
export type MagicProfileInsert = z.infer<typeof magicProfileInsertSchema>;
export const magicProfileSelectSchema = createSelectSchema(magicProfiles);
export type MagicProfile = z.infer<typeof magicProfileSelectSchema>;

export const spellInsertSchema = createInsertSchema(spells);
export type SpellInsert = z.infer<typeof spellInsertSchema>;
export const spellSelectSchema = createSelectSchema(spells);
export type Spell = z.infer<typeof spellSelectSchema>;

export const itemInsertSchema = createInsertSchema(items);
export type ItemInsert = z.infer<typeof itemInsertSchema>;
export const itemSelectSchema = createSelectSchema(items);
export type Item = z.infer<typeof itemSelectSchema>;

export const questInsertSchema = createInsertSchema(quests);
export type QuestInsert = z.infer<typeof questInsertSchema>;
export const questSelectSchema = createSelectSchema(quests);
export type Quest = z.infer<typeof questSelectSchema>;

export const regionInsertSchema = createInsertSchema(regions);
export type RegionInsert = z.infer<typeof regionInsertSchema>;
export const regionSelectSchema = createSelectSchema(regions);
export type Region = z.infer<typeof regionSelectSchema>;

export const areaInsertSchema = createInsertSchema(areas);
export type AreaInsert = z.infer<typeof areaInsertSchema>;
export const areaSelectSchema = createSelectSchema(areas);
export type Area = z.infer<typeof areaSelectSchema>;

export const magicalMaterialsInsertSchema = createInsertSchema(magicalMaterials);
export type MagicalMaterialsInsert = z.infer<typeof magicalMaterialsInsertSchema>;
export const magicalMaterialsSelectSchema = createSelectSchema(magicalMaterials);
export type MagicalMaterials = z.infer<typeof magicalMaterialsSelectSchema>;

export const craftingRecipesInsertSchema = createInsertSchema(craftingRecipes);
export type CraftingRecipesInsert = z.infer<typeof craftingRecipesInsertSchema>;
export const craftingRecipesSelectSchema = createSelectSchema(craftingRecipes);
export type CraftingRecipes = z.infer<typeof craftingRecipesSelectSchema>;

export const playerCraftingSkillsInsertSchema = createInsertSchema(playerCraftingSkills);
export type PlayerCraftingSkillsInsert = z.infer<typeof playerCraftingSkillsInsertSchema>;
export const playerCraftingSkillsSelectSchema = createSelectSchema(playerCraftingSkills);
export type PlayerCraftingSkills = z.infer<typeof playerCraftingSkillsSelectSchema>;