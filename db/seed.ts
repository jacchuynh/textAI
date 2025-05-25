import { db, initializeDatabase } from './index';
import { 
  spells, spellsInsertSchema,
  items, itemsInsertSchema,
  materials, materialsInsertSchema,
  quests, questsInsertSchema,
  questStages, questStagesInsertSchema
} from '@shared/schema';
import { eq } from 'drizzle-orm';

// Initial spells data
const initialSpells = [
  {
    spellId: 'arcane_bolt',
    name: 'Arcane Bolt',
    description: 'A simple bolt of arcane energy that deals damage to a single target.',
    domains: ['ARCANE'],
    damageTypes: ['ARCANE'],
    effectTypes: ['DAMAGE'],
    manaCost: 5,
    castingTime: 1.0,
    cooldown: 2.0,
    basePower: 3.0,
    levelReq: 1,
    tier: 'LESSER',
    targetingType: 'single',
    rangeMax: 20.0,
    duration: 0.0,
    components: ['verbal', 'somatic'],
    tags: ['arcane', 'damage', 'beginner']
  },
  {
    spellId: 'fireball',
    name: 'Fireball',
    description: 'A ball of fire that explodes on impact, dealing damage to the target and nearby enemies.',
    domains: ['FIRE'],
    damageTypes: ['FIRE'],
    effectTypes: ['DAMAGE'],
    manaCost: 15,
    castingTime: 2.0,
    cooldown: 5.0,
    basePower: 8.0,
    levelReq: 3,
    tier: 'MODERATE',
    targetingType: 'area',
    rangeMax: 30.0,
    duration: 0.0,
    components: ['verbal', 'somatic', 'material'],
    tags: ['fire', 'damage', 'area']
  },
  {
    spellId: 'healing_light',
    name: 'Healing Light',
    description: 'A gentle light that heals the target\'s wounds.',
    domains: ['LIGHT', 'LIFE'],
    damageTypes: [],
    effectTypes: ['HEALING'],
    manaCost: 10,
    castingTime: 2.0,
    cooldown: 10.0,
    basePower: 5.0,
    levelReq: 2,
    tier: 'LESSER',
    targetingType: 'single',
    rangeMax: 10.0,
    duration: 0.0,
    components: ['verbal', 'somatic'],
    tags: ['healing', 'light', 'support']
  }
];

// Initial items data
const initialItems = [
  {
    itemId: 'iron_sword',
    name: 'Iron Sword',
    type: 'weapon',
    description: 'A simple iron sword. Effective but nothing special.',
    value: 10,
    stats: { damage: 5, weight: 3 },
    tags: ['weapon', 'sword', 'metal', 'common']
  },
  {
    itemId: 'leather_armor',
    name: 'Leather Armor',
    type: 'armor',
    description: 'Basic leather armor that provides minimal protection.',
    value: 15,
    stats: { defense: 3, weight: 5 },
    tags: ['armor', 'leather', 'common']
  },
  {
    itemId: 'health_potion',
    name: 'Minor Health Potion',
    type: 'consumable',
    description: 'A small vial of red liquid that restores a small amount of health when consumed.',
    value: 5,
    stats: { health: 20 },
    tags: ['potion', 'healing', 'consumable']
  }
];

// Initial materials data
const initialMaterials = [
  {
    materialId: 'iron_ore',
    name: 'Iron Ore',
    description: 'Raw iron ore that can be smelted into iron ingots.',
    value: 2,
    rarity: 'common',
    tags: ['metal', 'ore', 'crafting']
  },
  {
    materialId: 'wood',
    name: 'Wood',
    description: 'Common wood that can be used for crafting.',
    value: 1,
    rarity: 'common',
    tags: ['wood', 'crafting']
  },
  {
    materialId: 'leather',
    name: 'Leather',
    description: 'Processed animal hide used for armor and other items.',
    value: 3,
    rarity: 'common',
    tags: ['leather', 'crafting']
  },
  {
    materialId: 'herbs',
    name: 'Medicinal Herbs',
    description: 'Various herbs with healing properties, useful for potions.',
    value: 2,
    rarity: 'common',
    tags: ['plant', 'alchemy', 'crafting']
  },
  {
    materialId: 'arcane_dust',
    name: 'Arcane Dust',
    description: 'Glittering magical dust that holds arcane energy.',
    value: 8,
    rarity: 'uncommon',
    tags: ['magic', 'arcane', 'crafting']
  }
];

// Initial quests data
const initialQuests = [
  {
    questId: 'village_troubles',
    name: 'Village Troubles',
    description: 'The village elder has asked for help dealing with the wolves that have been attacking travelers.',
    giver: 'village_elder',
    rewards: { 
      experience: 100, 
      gold: 50, 
      items: ['leather_boots'],
      reputation: { village_elder: 15 } 
    },
    status: 'available',
    locationRegion: 'emerald_vale',
    locationArea: 'crossroads'
  }
];

// Initial quest stages data (related to quests)
const initialQuestStages = [
  // For village_troubles quest
  {
    questId: 0, // Will be updated after quest insert
    stageId: 'talk_to_elder',
    description: 'Talk to Elder Thaddeus about the wolf problem.',
    target: {},
    order: 1
  },
  {
    questId: 0, // Will be updated after quest insert
    stageId: 'kill_wolves',
    description: 'Hunt down and kill the wolves (0/3).',
    target: { type: 'monster', id: 'wolf', count: 3, current: 0 },
    order: 2
  },
  {
    questId: 0, // Will be updated after quest insert
    stageId: 'return_to_elder',
    description: 'Return to Elder Thaddeus to report your success.',
    target: {},
    order: 3
  }
];

// Function to seed the database
async function seedDatabase() {
  console.log('Starting database seeding...');
  
  try {
    // Initialize the database
    const dbInitialized = await initializeDatabase();
    if (!dbInitialized) {
      console.error('Database initialization failed. Cannot proceed with seeding.');
      return;
    }
    
    // Seed spells
    console.log('Seeding spells...');
    for (const spellData of initialSpells) {
      // Check if spell already exists
      const existingSpell = await db.query.spells.findFirst({
        where: eq(spells.spellId, spellData.spellId)
      });
      
      if (!existingSpell) {
        // Validate the spell data
        const validatedSpell = spellsInsertSchema.parse(spellData);
        
        // Insert the spell
        await db.insert(spells).values(validatedSpell);
        console.log(`Inserted spell: ${spellData.name}`);
      } else {
        console.log(`Spell ${spellData.name} already exists, skipping`);
      }
    }
    
    // Seed items
    console.log('Seeding items...');
    for (const itemData of initialItems) {
      // Check if item already exists
      const existingItem = await db.query.items.findFirst({
        where: eq(items.itemId, itemData.itemId)
      });
      
      if (!existingItem) {
        // Validate the item data
        const validatedItem = itemsInsertSchema.parse(itemData);
        
        // Insert the item
        await db.insert(items).values(validatedItem);
        console.log(`Inserted item: ${itemData.name}`);
      } else {
        console.log(`Item ${itemData.name} already exists, skipping`);
      }
    }
    
    // Seed materials
    console.log('Seeding materials...');
    for (const materialData of initialMaterials) {
      // Check if material already exists
      const existingMaterial = await db.query.materials.findFirst({
        where: eq(materials.materialId, materialData.materialId)
      });
      
      if (!existingMaterial) {
        // Validate the material data
        const validatedMaterial = materialsInsertSchema.parse(materialData);
        
        // Insert the material
        await db.insert(materials).values(validatedMaterial);
        console.log(`Inserted material: ${materialData.name}`);
      } else {
        console.log(`Material ${materialData.name} already exists, skipping`);
      }
    }
    
    // Seed quests
    console.log('Seeding quests...');
    for (const questData of initialQuests) {
      // Check if quest already exists
      const existingQuest = await db.query.quests.findFirst({
        where: eq(quests.questId, questData.questId)
      });
      
      if (!existingQuest) {
        // Validate the quest data
        const validatedQuest = questsInsertSchema.parse(questData);
        
        // Insert the quest
        const [insertedQuest] = await db.insert(quests).values(validatedQuest).returning({ id: quests.id });
        console.log(`Inserted quest: ${questData.name}`);
        
        // Now seed related quest stages
        const relatedStages = initialQuestStages.filter(stage => stage.questId === 0);
        
        for (const stageData of relatedStages) {
          // Update the questId to the real one
          stageData.questId = insertedQuest.id;
          
          // Validate the stage data
          const validatedStage = questStagesInsertSchema.parse(stageData);
          
          // Insert the stage
          await db.insert(questStages).values(validatedStage);
          console.log(`Inserted quest stage: ${stageData.stageId} for quest ID ${insertedQuest.id}`);
        }
      } else {
        console.log(`Quest ${questData.name} already exists, skipping`);
      }
    }
    
    console.log('Database seeding completed successfully!');
  } catch (error) {
    console.error('Error seeding database:', error);
  }
}

// Run the seeding function
seedDatabase().catch(console.error);

// Export for use in other files if needed
export { seedDatabase };