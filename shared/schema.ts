import { pgTable, serial, text, integer, timestamp, decimal, boolean, json, jsonb } from 'drizzle-orm/pg-core';
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
  locationCoordinates: json('location_coordinates').$type<{ x: number, y: number }>().notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Magic profiles for players
export const magicProfiles = pgTable('magic_profiles', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull().unique(),
  manaCurrent: integer('mana_current').notNull().default(50),
  manaMax: integer('mana_max').notNull().default(50),
  magicAffinity: text('magic_affinity').notNull().default('novice'),
  knownAspects: json('known_aspects').$type<string[]>().notNull().default(['basic']),
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
  itemType: text('item_type').notNull(), // weapon, armor, consumable, quest, etc.
  rarity: text('rarity').notNull().default('common'),
  value: integer('value').notNull().default(0),
  weight: decimal('weight').notNull().default('1'),
  stats: json('stats').$type<Record<string, number>>(),
  requirements: json('requirements').$type<Record<string, number>>(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player items (inventory)
export const playerItems = pgTable('player_items', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  itemId: integer('item_id').references(() => items.id).notNull(),
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
  materialType: text('material_type').notNull(), // ore, herb, leather, fabric, etc.
  rarity: text('rarity').notNull().default('common'),
  value: integer('value').notNull().default(0),
  magicalProperties: json('magical_properties').$type<string[]>(),
  harvestLocations: json('harvest_locations').$type<string[]>(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player materials (crafting inventory)
export const playerMaterials = pgTable('player_materials', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  materialId: integer('material_id').references(() => materials.id).notNull(),
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
  domains: json('domains').$type<string[]>().notNull(),
  requirements: json('requirements').$type<Record<string, number>>(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player spells (known spells)
export const playerSpells = pgTable('player_spells', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  spellId: integer('spell_id').references(() => spells.id).notNull(),
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
  itemRewards: json('item_rewards').$type<{itemId: number, quantity: number}[]>(),
  repeatable: boolean('repeatable').notNull().default(false),
  questType: text('quest_type').notNull().default('main'), // main, side, daily, etc.
  questGiver: text('quest_giver'),
  questLocation: text('quest_location'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Quest stages (steps within a quest)
export const questStages = pgTable('quest_stages', {
  id: serial('id').primaryKey(),
  questId: integer('quest_id').references(() => quests.id).notNull(),
  stageNumber: integer('stage_number').notNull(),
  description: text('description').notNull(),
  objectives: json('objectives').$type<{type: string, target: string, amount: number}[]>(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player quests (active and completed quests)
export const playerQuests = pgTable('player_quests', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  questId: integer('quest_id').references(() => quests.id).notNull(),
  status: text('status').notNull().default('active'), // active, completed, failed
  startedAt: timestamp('started_at').defaultNow().notNull(),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player quest stages (tracking progress of individual quest stages)
export const playerQuestStages = pgTable('player_quest_stages', {
  id: serial('id').primaryKey(),
  playerQuestId: integer('player_quest_id').references(() => playerQuests.id).notNull(),
  stageId: integer('stage_id').references(() => questStages.id).notNull(),
  completed: boolean('completed').notNull().default(false),
  progress: json('progress').$type<Record<string, number>>().default({}),
  completedAt: timestamp('completed_at'),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Crafting recipes
export const recipes = pgTable('recipes', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  craftingType: text('crafting_type').notNull(), // blacksmithing, alchemy, tailoring, etc.
  requiredLevel: integer('required_level').notNull().default(1),
  itemId: integer('item_id').references(() => items.id).notNull(),
  materialsRequired: json('materials_required').$type<{materialId: number, quantity: number}[]>().notNull(),
  skillGain: integer('skill_gain').notNull().default(1),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Player recipes (known crafting recipes)
export const playerRecipes = pgTable('player_recipes', {
  id: serial('id').primaryKey(),
  playerId: integer('player_id').references(() => players.id).notNull(),
  recipeId: integer('recipe_id').references(() => recipes.id).notNull(),
  discovered: boolean('discovered').notNull().default(true),
  timesCrafted: integer('times_crafted').notNull().default(0),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// NPCs
export const npcs = pgTable('npcs', {
  id: serial('id').primaryKey(),
  name: text('name').notNull(),
  description: text('description'),
  npcType: text('npc_type').notNull(), // merchant, quest giver, trainer, etc.
  locationRegion: text('location_region').notNull(),
  locationArea: text('location_area').notNull(),
  dialogue: jsonb('dialogue').$type<Record<string, string[]>>(),
  wares: json('wares').$type<{itemId: number, quantity: number, price: number}[]>(),
  services: json('services').$type<{name: string, description: string, price: number}[]>(),
  createdAt: timestamp('created_at').defaultNow().notNull()
});

// Define table relationships
export const playersRelations = relations(players, ({ one, many }) => ({
  magicProfile: one(magicProfiles, { fields: [players.id], references: [magicProfiles.playerId] }),
  playerItems: many(playerItems),
  playerMaterials: many(playerMaterials),
  playerSpells: many(playerSpells),
  playerQuests: many(playerQuests),
  playerRecipes: many(playerRecipes)
}));

export const magicProfilesRelations = relations(magicProfiles, ({ one }) => ({
  player: one(players, { fields: [magicProfiles.playerId], references: [players.id] })
}));

export const itemsRelations = relations(items, ({ many }) => ({
  playerItems: many(playerItems),
  recipes: many(recipes)
}));

export const playerItemsRelations = relations(playerItems, ({ one }) => ({
  player: one(players, { fields: [playerItems.playerId], references: [players.id] }),
  item: one(items, { fields: [playerItems.itemId], references: [items.id] })
}));

export const materialsRelations = relations(materials, ({ many }) => ({
  playerMaterials: many(playerMaterials)
}));

export const playerMaterialsRelations = relations(playerMaterials, ({ one }) => ({
  player: one(players, { fields: [playerMaterials.playerId], references: [players.id] }),
  material: one(materials, { fields: [playerMaterials.materialId], references: [materials.id] })
}));

export const spellsRelations = relations(spells, ({ many }) => ({
  playerSpells: many(playerSpells)
}));

export const playerSpellsRelations = relations(playerSpells, ({ one }) => ({
  player: one(players, { fields: [playerSpells.playerId], references: [players.id] }),
  spell: one(spells, { fields: [playerSpells.spellId], references: [spells.id] })
}));

export const questsRelations = relations(quests, ({ many }) => ({
  stages: many(questStages),
  playerQuests: many(playerQuests)
}));

export const questStagesRelations = relations(questStages, ({ one, many }) => ({
  quest: one(quests, { fields: [questStages.questId], references: [quests.id] }),
  playerStages: many(playerQuestStages)
}));

export const playerQuestsRelations = relations(playerQuests, ({ one, many }) => ({
  player: one(players, { fields: [playerQuests.playerId], references: [players.id] }),
  quest: one(quests, { fields: [playerQuests.questId], references: [quests.id] }),
  stages: many(playerQuestStages)
}));

export const playerQuestStagesRelations = relations(playerQuestStages, ({ one }) => ({
  playerQuest: one(playerQuests, { fields: [playerQuestStages.playerQuestId], references: [playerQuests.id] }),
  stage: one(questStages, { fields: [playerQuestStages.stageId], references: [questStages.id] })
}));

export const recipesRelations = relations(recipes, ({ one, many }) => ({
  item: one(items, { fields: [recipes.itemId], references: [items.id] }),
  playerRecipes: many(playerRecipes)
}));

export const playerRecipesRelations = relations(playerRecipes, ({ one }) => ({
  player: one(players, { fields: [playerRecipes.playerId], references: [players.id] }),
  recipe: one(recipes, { fields: [playerRecipes.recipeId], references: [recipes.id] })
}));

// Zod schemas for validation
export const playersInsertSchema = createInsertSchema(players);
export const playersSelectSchema = createSelectSchema(players);

export const magicProfilesInsertSchema = createInsertSchema(magicProfiles);
export const magicProfilesSelectSchema = createSelectSchema(magicProfiles);

export const itemsInsertSchema = createInsertSchema(items);
export const itemsSelectSchema = createSelectSchema(items);

export const playerItemsInsertSchema = createInsertSchema(playerItems);
export const playerItemsSelectSchema = createSelectSchema(playerItems);

export const materialsInsertSchema = createInsertSchema(materials);
export const materialsSelectSchema = createSelectSchema(materials);

export const playerMaterialsInsertSchema = createInsertSchema(playerMaterials);
export const playerMaterialsSelectSchema = createSelectSchema(playerMaterials);

export const spellsInsertSchema = createInsertSchema(spells);
export const spellsSelectSchema = createSelectSchema(spells);

export const playerSpellsInsertSchema = createInsertSchema(playerSpells);
export const playerSpellsSelectSchema = createSelectSchema(playerSpells);

export const questsInsertSchema = createInsertSchema(quests);
export const questsSelectSchema = createSelectSchema(quests);

export const questStagesInsertSchema = createInsertSchema(questStages);
export const questStagesSelectSchema = createSelectSchema(questStages);

export const playerQuestsInsertSchema = createInsertSchema(playerQuests);
export const playerQuestsSelectSchema = createSelectSchema(playerQuests);

export const playerQuestStagesInsertSchema = createInsertSchema(playerQuestStages);
export const playerQuestStagesSelectSchema = createSelectSchema(playerQuestStages);

export const recipesInsertSchema = createInsertSchema(recipes);
export const recipesSelectSchema = createSelectSchema(recipes);

export const playerRecipesInsertSchema = createInsertSchema(playerRecipes);
export const playerRecipesSelectSchema = createSelectSchema(playerRecipes);

export const npcsInsertSchema = createInsertSchema(npcs);
export const npcsSelectSchema = createSelectSchema(npcs);

// Type exports
export type Player = z.infer<typeof playersSelectSchema>;
export type PlayerInsert = z.infer<typeof playersInsertSchema>;

export type MagicProfile = z.infer<typeof magicProfilesSelectSchema>;
export type MagicProfileInsert = z.infer<typeof magicProfilesInsertSchema>;

export type Item = z.infer<typeof itemsSelectSchema>;
export type ItemInsert = z.infer<typeof itemsInsertSchema>;

export type PlayerItem = z.infer<typeof playerItemsSelectSchema>;
export type PlayerItemInsert = z.infer<typeof playerItemsInsertSchema>;

export type Material = z.infer<typeof materialsSelectSchema>;
export type MaterialInsert = z.infer<typeof materialsInsertSchema>;

export type PlayerMaterial = z.infer<typeof playerMaterialsSelectSchema>;
export type PlayerMaterialInsert = z.infer<typeof playerMaterialsInsertSchema>;

export type Spell = z.infer<typeof spellsSelectSchema>;
export type SpellInsert = z.infer<typeof spellsInsertSchema>;

export type PlayerSpell = z.infer<typeof playerSpellsSelectSchema>;
export type PlayerSpellInsert = z.infer<typeof playerSpellsInsertSchema>;

export type Quest = z.infer<typeof questsSelectSchema>;
export type QuestInsert = z.infer<typeof questsInsertSchema>;

export type QuestStage = z.infer<typeof questStagesSelectSchema>;
export type QuestStageInsert = z.infer<typeof questStagesInsertSchema>;

export type PlayerQuest = z.infer<typeof playerQuestsSelectSchema>;
export type PlayerQuestInsert = z.infer<typeof playerQuestsInsertSchema>;

export type PlayerQuestStage = z.infer<typeof playerQuestStagesSelectSchema>;
export type PlayerQuestStageInsert = z.infer<typeof playerQuestStagesInsertSchema>;

export type Recipe = z.infer<typeof recipesSelectSchema>;
export type RecipeInsert = z.infer<typeof recipesInsertSchema>;

export type PlayerRecipe = z.infer<typeof playerRecipesSelectSchema>;
export type PlayerRecipeInsert = z.infer<typeof playerRecipesInsertSchema>;

export type NPC = z.infer<typeof npcsSelectSchema>;
export type NPCInsert = z.infer<typeof npcsInsertSchema>;