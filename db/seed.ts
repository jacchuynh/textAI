import { db } from './index';
import { 
  players,
  magicProfiles,
  items,
  playerItems,
  spells,
  playerSpells,
  quests,
  questStages,
  playerQuests,
  materials,
  recipes,
  npcs,
  playersInsertSchema
} from '@shared/schema';
import { eq } from 'drizzle-orm';

async function seed() {
  console.log('Starting database seeding...');
  
  try {
    // Check if we already have data
    const existingPlayers = await db.query.players.findMany();
    if (existingPlayers.length > 0) {
      console.log('Database already has data, skipping seed.');
      console.log(`Found ${existingPlayers.length} existing players.`);
      return;
    }
    
    // 1. Create some initial items
    console.log('Creating items...');
    const seedItems = [
      {
        name: 'Wooden Staff',
        description: 'A basic wooden staff, perfect for novice mages.',
        itemType: 'weapon',
        rarity: 'common',
        value: 10,
        weight: 2.5,
        stats: { magicDamage: 3, magicBoost: 1 },
        requirements: { level: 1 }
      },
      {
        name: 'Leather Robe',
        description: 'A simple robe made of leather, offering minimal protection.',
        itemType: 'armor',
        rarity: 'common',
        value: 15,
        weight: 3.0,
        stats: { defense: 2, magicDefense: 1 },
        requirements: { level: 1 }
      },
      {
        name: 'Health Potion',
        description: 'A small vial of red liquid that restores 25 health when consumed.',
        itemType: 'consumable',
        rarity: 'common',
        value: 5,
        weight: 0.5,
        stats: { healAmount: 25 },
        requirements: null
      },
      {
        name: 'Mana Potion',
        description: 'A small vial of blue liquid that restores 25 mana when consumed.',
        itemType: 'consumable',
        rarity: 'common',
        value: 5,
        weight: 0.5,
        stats: { manaAmount: 25 },
        requirements: null
      },
      {
        name: 'Crystal Focus',
        description: 'A small crystal that helps focus magical energy.',
        itemType: 'focus',
        rarity: 'uncommon',
        value: 25,
        weight: 0.2,
        stats: { magicEfficiency: 5, spellCritical: 2 },
        requirements: { level: 3, magicLevel: 2 }
      }
    ];
    
    const createdItems = await db.insert(items).values(seedItems).returning();
    console.log(`Created ${createdItems.length} items.`);
    
    // 2. Create some spells
    console.log('Creating spells...');
    const seedSpells = [
      {
        name: 'Firebolt',
        description: 'A simple bolt of fire that deals minor damage to a single target.',
        manaCost: 10,
        castTime: 1.0,
        cooldown: 2.0,
        damageType: 'fire',
        damageAmount: 15,
        healAmount: null,
        range: 20,
        areaOfEffect: 0,
        duration: 0,
        domains: ['fire', 'destruction'],
        requirements: { level: 1, magicLevel: 1 }
      },
      {
        name: 'Heal',
        description: 'A basic healing spell that restores a small amount of health to a single target.',
        manaCost: 15,
        castTime: 2.0,
        cooldown: 5.0,
        damageType: null,
        damageAmount: null,
        healAmount: 25,
        range: 10,
        areaOfEffect: 0,
        duration: 0,
        domains: ['life', 'restoration'],
        requirements: { level: 1, magicLevel: 1 }
      },
      {
        name: 'Arcane Missile',
        description: 'A magical missile of pure arcane energy that never misses its target.',
        manaCost: 5,
        castTime: 0.5,
        cooldown: 1.0,
        damageType: 'arcane',
        damageAmount: 8,
        healAmount: null,
        range: 30,
        areaOfEffect: 0,
        duration: 0,
        domains: ['arcane'],
        requirements: { level: 1, magicLevel: 1 }
      },
      {
        name: 'Frostbite',
        description: 'Freezes the target, dealing ice damage and slowing movement.',
        manaCost: 12,
        castTime: 1.5,
        cooldown: 3.0,
        damageType: 'ice',
        damageAmount: 10,
        healAmount: null,
        range: 15,
        areaOfEffect: 0,
        duration: 5,
        domains: ['water', 'ice', 'control'],
        requirements: { level: 2, magicLevel: 2 }
      },
      {
        name: 'Lightning Strike',
        description: 'Calls down a bolt of lightning on the target area.',
        manaCost: 20,
        castTime: 2.0,
        cooldown: 8.0,
        damageType: 'lightning',
        damageAmount: 30,
        healAmount: null,
        range: 25,
        areaOfEffect: 3,
        duration: 0,
        domains: ['air', 'lightning', 'destruction'],
        requirements: { level: 5, magicLevel: 3 }
      }
    ];
    
    const createdSpells = await db.insert(spells).values(seedSpells).returning();
    console.log(`Created ${createdSpells.length} spells.`);
    
    // 3. Create some materials
    console.log('Creating materials...');
    const seedMaterials = [
      {
        name: 'Iron Ore',
        description: 'Raw iron ore, can be smelted into iron ingots.',
        materialType: 'metal_ore',
        rarity: 'common',
        value: 2,
        magicalProperties: null,
        harvestLocations: ['mountains', 'caves', 'mines']
      },
      {
        name: 'Oak Wood',
        description: 'Strong wood from oak trees, useful for crafting.',
        materialType: 'wood',
        rarity: 'common',
        value: 1,
        magicalProperties: null,
        harvestLocations: ['forest', 'woodlands']
      },
      {
        name: 'Magebloom',
        description: 'A flower with inherent magical properties, glows softly in the dark.',
        materialType: 'herb',
        rarity: 'uncommon',
        value: 8,
        magicalProperties: { manaRegeneration: 1, spellPotency: 2 },
        harvestLocations: ['magical_groves', 'ancient_forests', 'leyline_intersections']
      },
      {
        name: 'Arcane Crystal',
        description: 'A small crystal imbued with raw magical energy.',
        materialType: 'crystal',
        rarity: 'uncommon',
        value: 12,
        magicalProperties: { spellFocus: 3, magicAmplification: 1 },
        harvestLocations: ['magical_caves', 'arcane_ruins', 'leyline_nodes']
      },
      {
        name: 'Dragon Scale',
        description: 'A tough, heat-resistant scale from a dragon.',
        materialType: 'monster_part',
        rarity: 'rare',
        value: 50,
        magicalProperties: { fireResistance: 10, durability: 5 },
        harvestLocations: ['dragon_lairs', 'volcanic_regions']
      }
    ];
    
    const createdMaterials = await db.insert(materials).values(seedMaterials).returning();
    console.log(`Created ${createdMaterials.length} materials.`);
    
    // 4. Create some quests
    console.log('Creating quests...');
    const seedQuests = [
      {
        name: 'Apprentice\'s First Steps',
        description: 'Prove your worth as a magical apprentice by completing a series of basic tasks.',
        requiredLevel: 1,
        experienceReward: 100,
        goldReward: 25,
        itemRewards: [{ itemId: createdItems[0].id, quantity: 1 }],
        repeatable: false,
        questType: 'main',
        questGiver: 'Archmage Thalen',
        questLocation: 'Mage\'s Guild'
      },
      {
        name: 'Magical Herb Collection',
        description: 'Collect rare magical herbs for the local alchemist.',
        requiredLevel: 2,
        experienceReward: 150,
        goldReward: 35,
        itemRewards: [{ itemId: createdItems[3].id, quantity: 2 }],
        repeatable: true,
        questType: 'side',
        questGiver: 'Alchemist Elara',
        questLocation: 'Whispering Woods'
      },
      {
        name: 'Crystal Cave Exploration',
        description: 'Explore the magical crystal caves and bring back samples for research.',
        requiredLevel: 3,
        experienceReward: 200,
        goldReward: 50,
        itemRewards: [{ itemId: createdItems[4].id, quantity: 1 }],
        repeatable: false,
        questType: 'side',
        questGiver: 'Researcher Valen',
        questLocation: 'Crystal Caves'
      }
    ];
    
    const createdQuests = await db.insert(quests).values(seedQuests).returning();
    console.log(`Created ${createdQuests.length} quests.`);
    
    // 5. Create quest stages
    console.log('Creating quest stages...');
    const seedQuestStages = [
      // First quest stages
      {
        questId: createdQuests[0].id,
        stageNumber: 1,
        description: 'Speak with Professor Lydia at the Training Grounds',
        objectives: { type: 'talk', targetNpc: 'Professor Lydia' }
      },
      {
        questId: createdQuests[0].id,
        stageNumber: 2,
        description: 'Cast three basic spells successfully on the training dummies',
        objectives: { type: 'cast', spellCount: 3, targetType: 'training_dummy' }
      },
      {
        questId: createdQuests[0].id,
        stageNumber: 3,
        description: 'Return to Archmage Thalen with your training results',
        objectives: { type: 'talk', targetNpc: 'Archmage Thalen' }
      },
      
      // Second quest stages
      {
        questId: createdQuests[1].id,
        stageNumber: 1,
        description: 'Collect 5 Magebloom flowers from Whispering Woods',
        objectives: { type: 'gather', itemId: createdMaterials[2].id, quantity: 5, area: 'Whispering Woods' }
      },
      {
        questId: createdQuests[1].id,
        stageNumber: 2,
        description: 'Return to Alchemist Elara with the collected herbs',
        objectives: { type: 'talk', targetNpc: 'Alchemist Elara' }
      },
      
      // Third quest stages
      {
        questId: createdQuests[2].id,
        stageNumber: 1,
        description: 'Find the entrance to Crystal Caves',
        objectives: { type: 'explore', area: 'Crystal Caves Entrance' }
      },
      {
        questId: createdQuests[2].id,
        stageNumber: 2,
        description: 'Collect 3 Arcane Crystal samples',
        objectives: { type: 'gather', itemId: createdMaterials[3].id, quantity: 3, area: 'Crystal Caves' }
      },
      {
        questId: createdQuests[2].id,
        stageNumber: 3,
        description: 'Defeat the Crystal Guardian',
        objectives: { type: 'defeat', enemyName: 'Crystal Guardian', quantity: 1 }
      },
      {
        questId: createdQuests[2].id,
        stageNumber: 4,
        description: 'Return to Researcher Valen with your findings',
        objectives: { type: 'talk', targetNpc: 'Researcher Valen' }
      }
    ];
    
    const createdQuestStages = await db.insert(questStages).values(seedQuestStages).returning();
    console.log(`Created ${createdQuestStages.length} quest stages.`);
    
    // 6. Create NPCs
    console.log('Creating NPCs...');
    const seedNpcs = [
      {
        name: 'Archmage Thalen',
        description: 'An elderly mage with a long white beard, head of the Mage\'s Guild.',
        npcType: 'quest_giver',
        locationRegion: 'Arcadia',
        locationArea: 'Mage\'s_Guild',
        dialogue: {
          greeting: "Ah, welcome to the Mage's Guild. Are you here to learn the arcane arts?",
          quests: [createdQuests[0].id],
          farewell: "May the arcane forces guide your path."
        },
        wares: null,
        services: { training: ['arcane', 'elemental'], teleportation: true }
      },
      {
        name: 'Professor Lydia',
        description: 'A stern-looking woman with spectacles and practical robes. She oversees training of new mages.',
        npcType: 'trainer',
        locationRegion: 'Arcadia',
        locationArea: 'Training_Grounds',
        dialogue: {
          greeting: "Welcome to the Training Grounds. I hope you're ready to work hard.",
          questDialogue: {
            [createdQuests[0].id]: {
              1: "So, Archmage Thalen sent you? Very well. Let's see what you can do. I want you to practice your basic spells on those training dummies over there.",
              2: "Good job with those spells. You have potential, but need more practice. Return to Archmage Thalen and let him know you've completed the basic training."
            }
          },
          farewell: "Practice makes perfect. Remember that."
        },
        wares: null,
        services: { training: ['basic_spells'], practice: true }
      },
      {
        name: 'Alchemist Elara',
        description: 'A middle-aged woman with hands stained from various reagents. Her shop smells of herbs and potions.',
        npcType: 'merchant',
        locationRegion: 'Arcadia',
        locationArea: 'Market_District',
        dialogue: {
          greeting: "Welcome to Elara's Elixirs! What can I brew for you today?",
          quests: [createdQuests[1].id],
          farewell: "Come back anytime you need a potion!"
        },
        wares: {
          sell: [
            { itemId: createdItems[2].id, price: 5, stock: 10 },
            { itemId: createdItems[3].id, price: 5, stock: 10 }
          ],
          buy: [
            { itemId: createdMaterials[2].id, price: 6 },
            { itemId: createdMaterials[3].id, price: 9 }
          ]
        },
        services: { alchemy: true, identify: true }
      },
      {
        name: 'Researcher Valen',
        description: 'A young, enthusiastic scholar with ink-stained fingers and messy hair.',
        npcType: 'quest_giver',
        locationRegion: 'Arcadia',
        locationArea: 'University',
        dialogue: {
          greeting: "Oh! Hello there! I'm in the middle of a fascinating study on magical crystals and their resonance patterns.",
          quests: [createdQuests[2].id],
          farewell: "So much to learn, so little time! Farewell!"
        },
        wares: null,
        services: { research: true, identification: true }
      }
    ];
    
    const createdNpcs = await db.insert(npcs).values(seedNpcs).returning();
    console.log(`Created ${createdNpcs.length} NPCs.`);
    
    // 7. Create a default player for testing
    console.log('Creating default test player...');
    const testPlayerData = {
      userId: 'test-user-1',
      name: 'Thalia',
      level: 1,
      experience: 0,
      gold: 50,
      healthCurrent: 100,
      healthMax: 100,
      locationRegion: 'Arcadia',
      locationArea: 'Novice_Quarter',
      locationCoordinates: { x: 50, y: 50, z: 0 }
    };
    
    // Validate using schema
    const validatedPlayerData = playersInsertSchema.parse(testPlayerData);
    
    // Insert player
    const [testPlayer] = await db.insert(players).values(validatedPlayerData).returning();
    
    // Create magic profile for the player
    const [testMagicProfile] = await db.insert(magicProfiles).values({
      playerId: testPlayer.id,
      manaCurrent: 50,
      manaMax: 50,
      magicAffinity: 'arcane',
      knownAspects: ['basic', 'arcane', 'fire'],
      ritualCapacity: 1,
      magicExperience: 0,
      magicLevel: 1
    }).returning();
    
    // Give player some starter items
    await db.insert(playerItems).values([
      {
        playerId: testPlayer.id,
        itemId: createdItems[0].id, // Wooden Staff
        quantity: 1,
        isEquipped: true,
        equippedSlot: 'weapon'
      },
      {
        playerId: testPlayer.id,
        itemId: createdItems[1].id, // Leather Robe
        quantity: 1,
        isEquipped: true,
        equippedSlot: 'body'
      },
      {
        playerId: testPlayer.id,
        itemId: createdItems[2].id, // Health Potion
        quantity: 3
      },
      {
        playerId: testPlayer.id,
        itemId: createdItems[3].id, // Mana Potion
        quantity: 3
      }
    ]);
    
    // Give player some starter spells
    await db.insert(playerSpells).values([
      {
        playerId: testPlayer.id,
        spellId: createdSpells[0].id, // Firebolt
        proficiency: 5,
        isFavorite: true
      },
      {
        playerId: testPlayer.id,
        spellId: createdSpells[1].id, // Heal
        proficiency: 3
      },
      {
        playerId: testPlayer.id,
        spellId: createdSpells[2].id, // Arcane Missile
        proficiency: 7,
        isFavorite: true
      }
    ]);
    
    // Assign first quest to player
    const [playerQuest] = await db.insert(playerQuests).values({
      playerId: testPlayer.id,
      questId: createdQuests[0].id,
      status: 'active'
    }).returning();
    
    console.log('Database seeding completed successfully!');
    console.log(`Created test player: ${testPlayer.name} (ID: ${testPlayer.id})`);
  } catch (error) {
    console.error('Error seeding database:', error);
    throw error;
  }
}

// Run the seed function
seed().catch(console.error);