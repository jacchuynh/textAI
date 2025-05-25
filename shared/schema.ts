import { pgTable, serial, text, integer, timestamp, jsonb, decimal, boolean } from 'drizzle-orm/pg-core';
import { createInsertSchema, createSelectSchema } from 'drizzle-zod';
import { relations } from 'drizzle-orm';
import { z } from 'zod';

// Players table
export const players = pgTable('players', {
  id: serial('id').primaryKey(),
  userId: text('user_id').notNull(),
  name: text('name').notNull(),
  level: integer('level').notNull().default(1),
  experience: integer('experience').notNull().default(0),
  gold: integer('gold').notNull().default(0),
  healthCurrent: integer('health_current').notNull().default(100),
  healthMax: integer('health_max').notNull().default(100),
  locationRegion: text('location_region').notNull(),
  locationArea: text('location_area').notNull(),
  locationCoordinates: jsonb('location_coordinates').notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Magic profiles table
export const magicProfiles = pgTable('magic_profiles', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').notNull().references(() => players.id).unique(),
  manaCurrent: integer('mana_current').notNull().default(50),
  manaMax: integer('mana_max').notNull().default(50),
  magicAffinity: text('magic_affinity').notNull().default('novice'),
  knownAspects: jsonb('known_aspects').notNull().default(['basic']),
  ritualCapacity: integer('ritual_capacity').notNull().default(0),
  magicExperience: integer('magic_experience').notNull().default(0),
  magicLevel: integer('magic_level').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Items table
export const items = pgTable('items', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  itemType: text('item_type').notNull(),
  rarity: text('rarity').notNull().default('common'),
  value: integer('value').notNull().default(0),
  weight: decimal('weight').notNull().default('1'),
  stats: jsonb('stats'),
  requirements: jsonb('requirements'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player items table
export const playerItems = pgTable('player_items', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').notNull().references(() => players.id),
  itemId: integer('item_id').notNull().references(() => items.id),
  quantity: integer('quantity').notNull().default(1),
  isEquipped: boolean('is_equipped').notNull().default(false),
  equippedSlot: text('equipped_slot'),
  durability: integer('durability'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Materials table
export const materials = pgTable('materials', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  materialType: text('material_type').notNull(),
  rarity: text('rarity').notNull().default('common'),
  value: integer('value').notNull().default(0),
  magicalProperties: jsonb('magical_properties'),
  harvestLocations: jsonb('harvest_locations'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player materials table
export const playerMaterials = pgTable('player_materials', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').notNull().references(() => players.id),
  materialId: integer('material_id').notNull().references(() => materials.id),
  quantity: integer('quantity').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Spells table
export const spells = pgTable('spells', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  manaCost: integer('mana_cost').notNull(),
  castTime: decimal('cast_time').notNull().default('1.0'),
  cooldown: decimal('cooldown').notNull().default('0'),
  damageType: text('damage_type'),
  damageAmount: integer('damage_amount'),
  healAmount: integer('heal_amount'),
  range: integer('range').notNull().default(5),
  areaOfEffect: integer('area_of_effect').notNull().default(0),
  duration: integer('duration').notNull().default(0),
  domains: jsonb('domains').notNull(),
  requirements: jsonb('requirements'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player spells table
export const playerSpells = pgTable('player_spells', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').notNull().references(() => players.id),
  spellId: integer('spell_id').notNull().references(() => spells.id),
  proficiency: integer('proficiency').notNull().default(1),
  isFavorite: boolean('is_favorite').notNull().default(false),
  lastCastAt: timestamp('last_cast_at'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Quests table
export const quests = pgTable('quests', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  requiredLevel: integer('required_level').notNull().default(1),
  experienceReward: integer('experience_reward').notNull().default(0),
  goldReward: integer('gold_reward').notNull().default(0),
  itemRewards: jsonb('item_rewards'),
  repeatable: boolean('repeatable').notNull().default(false),
  questType: text('quest_type').notNull().default('main'),
  questGiver: text('quest_giver'),
  questLocation: text('quest_location'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Quest stages table
export const questStages = pgTable('quest_stages', {
  id: serial('id').primaryKey(),
  questId: integer('quest_id').notNull().references(() => quests.id),
  stageNumber: integer('stage_number').notNull(),
  description: text('description').notNull(),
  objectives: jsonb('objectives'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player quests table
export const playerQuests = pgTable('player_quests', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').notNull().references(() => players.id),
  questId: integer('quest_id').notNull().references(() => quests.id),
  status: text('status').notNull().default('active'),
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player quest stages table
export const playerQuestStages = pgTable('player_quest_stages', {
  id: serial('id').primaryKey(),
  playerQuestId: integer('player_quest_id').notNull().references(() => playerQuests.id),
  stageId: integer('stage_id').notNull().references(() => questStages.id),
  completed: boolean('completed').notNull().default(false),
  progress: jsonb('progress').default({}),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Recipes table
export const recipes = pgTable('recipes', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  craftingType: text('crafting_type').notNull(),
  requiredLevel: integer('required_level').notNull().default(1),
  itemId: integer('item_id').notNull().references(() => items.id),
  materialsRequired: jsonb('materials_required').notNull(),
  skillGain: integer('skill_gain').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player recipes table
export const playerRecipes = pgTable('player_recipes', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').notNull().references(() => players.id),
  recipeId: integer('recipe_id').notNull().references(() => recipes.id),
  discovered: boolean('discovered').notNull().default(true),
  timesCrafted: integer('times_crafted').notNull().default(0),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// NPCs table
export const npcs = pgTable('npcs', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  npcType: text('npc_type').notNull(),
  locationRegion: text('location_region').notNull(),
  locationArea: text('location_area').notNull(),
  dialogue: jsonb('dialogue'),
  wares: jsonb('wares'),
  services: jsonb('services'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Define relations
export const playersRelations = relations(players, ({ one, many }) => ({
  magicProfile: one(magicProfiles, {
    fields: [players.id],
    references: [magicProfiles.playerId]
  }),
  items: many(playerItems),
  materials: many(playerMaterials),
  spells: many(playerSpells),
  quests: many(playerQuests),
  recipes: many(playerRecipes)
}));

export const magicProfilesRelations = relations(magicProfiles, ({ one }) => ({
  player: one(players, {
    fields: [magicProfiles.playerId],
    references: [players.id]
  })
}));

export const itemsRelations = relations(items, ({ many }) => ({
  playerItems: many(playerItems),
  recipes: many(recipes)
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

export const recipesRelations = relations(recipes, ({ one, many }) => ({
  item: one(items, {
    fields: [recipes.itemId],
    references: [items.id]
  }),
  playerRecipes: many(playerRecipes)
}));

export const playerRecipesRelations = relations(playerRecipes, ({ one }) => ({
  player: one(players, {
    fields: [playerRecipes.playerId],
    references: [players.id]
  }),
  recipe: one(recipes, {
    fields: [playerRecipes.recipeId],
    references: [recipes.id]
  })
}));

// Define schemas for validation
export const playersInsertSchema = createInsertSchema(players, {
  name: (schema) => schema.min(2, "Name must be at least 2 characters"),
  locationCoordinates: (schema) => schema.optional()
});

export const magicProfilesInsertSchema = createInsertSchema(magicProfiles);
export const itemsInsertSchema = createInsertSchema(items);
export const playerItemsInsertSchema = createInsertSchema(playerItems);
export const materialsInsertSchema = createInsertSchema(materials);
export const playerMaterialsInsertSchema = createInsertSchema(playerMaterials);
export const spellsInsertSchema = createInsertSchema(spells);
export const playerSpellsInsertSchema = createInsertSchema(playerSpells);
export const questsInsertSchema = createInsertSchema(quests);
export const questStagesInsertSchema = createInsertSchema(questStages);
export const playerQuestsInsertSchema = createInsertSchema(playerQuests);
export const playerQuestStagesInsertSchema = createInsertSchema(playerQuestStages);
export const recipesInsertSchema = createInsertSchema(recipes);
export const playerRecipesInsertSchema = createInsertSchema(playerRecipes);
export const npcsInsertSchema = createInsertSchema(npcs);

// Define types for TypeScript
export type PlayerInsert = z.infer<typeof playersInsertSchema>;
export type Player = z.infer<typeof createSelectSchema(players)> & {
  magicProfile?: MagicProfile;
};

export type MagicProfile = z.infer<typeof createSelectSchema(magicProfiles)>;
export type Item = z.infer<typeof createSelectSchema(items)>;
export type PlayerItem = z.infer<typeof createSelectSchema(playerItems)>;
export type Material = z.infer<typeof createSelectSchema(materials)>;
export type PlayerMaterial = z.infer<typeof createSelectSchema(playerMaterials)>;
export type Spell = z.infer<typeof createSelectSchema(spells)>;
export type PlayerSpell = z.infer<typeof createSelectSchema(playerSpells)>;
export type Quest = z.infer<typeof createSelectSchema(quests)>;
export type QuestStage = z.infer<typeof createSelectSchema(questStages)>;
export type PlayerQuest = z.infer<typeof createSelectSchema(playerQuests)>;
export type PlayerQuestStage = z.infer<typeof createSelectSchema(playerQuestStages)>;
export type Recipe = z.infer<typeof createSelectSchema(recipes)>;
export type PlayerRecipe = z.infer<typeof createSelectSchema(playerRecipes)>;
export type NPC = z.infer<typeof createSelectSchema(npcs)>;