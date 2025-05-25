import { db } from './index';
import { 
  players,
  items,
  materials,
  spells,
  quests,
  questStages,
  npcs
} from '@shared/schema';

async function seed() {
  console.log('Seeding database...');
  
  try {
    // Check if we already have data
    const existingItems = await db.query.items.findMany();
    if (existingItems.length > 0) {
      console.log('Database already seeded with items');
    } else {
      // Seed items
      console.log('Seeding items...');
      await db.insert(items).values([
        {
          name: 'Wooden Sword',
          description: 'A basic sword made of wood. Good for training.',
          itemType: 'weapon',
          rarity: 'common',
          value: 5,
          weight: '2',
          stats: { damage: 3, durability: 50 }
        },
        {
          name: 'Leather Armor',
          description: 'Simple armor made from tanned leather. Provides basic protection.',
          itemType: 'armor',
          rarity: 'common',
          value: 10,
          weight: '5',
          stats: { defense: 5, durability: 100 }
        },
        {
          name: 'Health Potion',
          description: 'A red potion that restores 20 health when consumed.',
          itemType: 'consumable',
          rarity: 'common',
          value: 15,
          weight: '0.5',
          stats: { healthRestore: 20 }
        },
        {
          name: 'Mana Potion',
          description: 'A blue potion that restores 20 mana when consumed.',
          itemType: 'consumable',
          rarity: 'common',
          value: 15,
          weight: '0.5',
          stats: { manaRestore: 20 }
        },
        {
          name: 'Iron Sword',
          description: 'A sturdy sword made of iron. Much more effective than wooden weapons.',
          itemType: 'weapon',
          rarity: 'uncommon',
          value: 50,
          weight: '4',
          stats: { damage: 8, durability: 200 }
        }
      ]);
    }

    // Check if we already have materials
    const existingMaterials = await db.query.materials.findMany();
    if (existingMaterials.length > 0) {
      console.log('Database already seeded with materials');
    } else {
      // Seed materials
      console.log('Seeding materials...');
      await db.insert(materials).values([
        {
          name: 'Wood',
          description: 'Common wood harvested from trees. Used in basic crafting.',
          materialType: 'wood',
          rarity: 'common',
          value: 1,
          harvestLocations: ['forest', 'woodland', 'village']
        },
        {
          name: 'Iron Ore',
          description: 'Raw iron ore that can be smelted into iron ingots.',
          materialType: 'ore',
          rarity: 'common',
          value: 5,
          harvestLocations: ['mountains', 'caves', 'mines']
        },
        {
          name: 'Leather',
          description: 'Tanned animal hide used for crafting armor and clothing.',
          materialType: 'leather',
          rarity: 'common',
          value: 3,
          harvestLocations: ['plains', 'forest', 'village']
        },
        {
          name: 'Red Herb',
          description: 'A common herb with healing properties. Used in potion making.',
          materialType: 'herb',
          rarity: 'common',
          value: 2,
          magicalProperties: ['healing'],
          harvestLocations: ['forest', 'meadow', 'garden']
        },
        {
          name: 'Blue Herb',
          description: 'A herb with magical properties that can restore mana.',
          materialType: 'herb',
          rarity: 'uncommon',
          value: 5,
          magicalProperties: ['mana restoration'],
          harvestLocations: ['lakeside', 'riverbank', 'magic grove']
        },
        {
          name: 'Crystal Water',
          description: 'Pure water collected from magical springs. Base ingredient for many potions.',
          materialType: 'liquid',
          rarity: 'uncommon',
          value: 10,
          magicalProperties: ['purity', 'catalyst'],
          harvestLocations: ['magic spring', 'sacred pool', 'crystal cave']
        }
      ]);
    }

    // Check if we already have spells
    const existingSpells = await db.query.spells.findMany();
    if (existingSpells.length > 0) {
      console.log('Database already seeded with spells');
    } else {
      // Seed spells
      console.log('Seeding spells...');
      await db.insert(spells).values([
        {
          name: 'Firebolt',
          description: 'Launches a bolt of fire at a target, dealing fire damage.',
          manaCost: 10,
          castTime: '1.5',
          cooldown: '3.0',
          damageType: 'fire',
          damageAmount: 15,
          range: 20,
          domains: ['fire', 'destruction']
        },
        {
          name: 'Healing Touch',
          description: 'Channels healing energy to restore health to a target.',
          manaCost: 15,
          castTime: '2.0',
          cooldown: '5.0',
          healAmount: 25,
          range: 5,
          domains: ['life', 'restoration']
        },
        {
          name: 'Arcane Missile',
          description: 'Fires a missile of pure arcane energy that never misses its target.',
          manaCost: 5,
          castTime: '1.0',
          cooldown: '2.0',
          damageType: 'arcane',
          damageAmount: 8,
          range: 30,
          domains: ['arcane']
        },
        {
          name: 'Ice Spike',
          description: 'Creates a spike of ice that pierces the target and slows their movement.',
          manaCost: 12,
          castTime: '1.8',
          cooldown: '4.0',
          damageType: 'ice',
          damageAmount: 12,
          range: 15,
          domains: ['water', 'ice']
        },
        {
          name: 'Nature\'s Shield',
          description: 'Summons protective vines and leaves that absorb damage.',
          manaCost: 20,
          castTime: '2.5',
          cooldown: '30.0',
          duration: 60,
          range: 1,
          domains: ['nature', 'protection']
        }
      ]);
    }

    // Check if we already have quests
    const existingQuests = await db.query.quests.findMany();
    if (existingQuests.length > 0) {
      console.log('Database already seeded with quests');
    } else {
      // Seed quests
      console.log('Seeding quests...');
      const [wolfQuest] = await db.insert(quests).values([
        {
          name: 'Wolf Problem',
          description: 'The village elder asks you to deal with wolves that have been threatening livestock.',
          requiredLevel: 1,
          experienceReward: 100,
          goldReward: 50,
          questType: 'side',
          questGiver: 'Village Elder',
          questLocation: 'Mossy_Hollow'
        }
      ]).returning();

      // Add quest stages
      if (wolfQuest) {
        await db.insert(questStages).values([
          {
            questId: wolfQuest.id,
            stageNumber: 1,
            description: 'Speak with the village elder about the wolf problem',
            objectives: [
              { type: 'talk', target: 'elder', amount: 1 }
            ]
          },
          {
            questId: wolfQuest.id,
            stageNumber: 2,
            description: 'Hunt wolves in the nearby forest (0/3)',
            objectives: [
              { type: 'kill', target: 'wolf', amount: 3 }
            ]
          },
          {
            questId: wolfQuest.id,
            stageNumber: 3,
            description: 'Return to the elder with news of your success',
            objectives: [
              { type: 'talk', target: 'elder', amount: 1 }
            ]
          }
        ]);
      }
    }

    // Check if we already have NPCs
    const existingNPCs = await db.query.npcs.findMany();
    if (existingNPCs.length > 0) {
      console.log('Database already seeded with NPCs');
    } else {
      // Seed NPCs
      console.log('Seeding NPCs...');
      await db.insert(npcs).values([
        {
          name: 'Village Elder',
          description: 'An elderly man with a long white beard and kind eyes. He is the leader of Mossy Hollow.',
          npcType: 'quest giver',
          locationRegion: 'Silvermist Valley',
          locationArea: 'Mossy_Hollow',
          dialogue: {
            greeting: [
              'Welcome, traveler. What brings you to our humble village?',
              'Ah, a new face in Mossy Hollow. How may I assist you?'
            ],
            quest_offer: [
              'We\'ve been having trouble with wolves attacking our livestock. Could you help us deal with this problem?'
            ],
            quest_active: [
              'Have you dealt with those wolves yet? Our farmers are quite worried.'
            ],
            quest_complete: [
              'Thank you for your help with the wolves! Our village is safer thanks to you.'
            ]
          }
        },
        {
          name: 'Gareth the Blacksmith',
          description: 'A burly man with muscular arms and a soot-covered apron. He works the forge in Mossy Hollow.',
          npcType: 'merchant',
          locationRegion: 'Silvermist Valley',
          locationArea: 'Mossy_Hollow',
          dialogue: {
            greeting: [
              'Need some armor or a weapon? I\'ve got the finest steel in the valley!',
              'Welcome to my forge, traveler. What can I craft for you today?'
            ],
            shop: [
              'Take a look at my wares. Quality guaranteed or your money back!'
            ]
          },
          wares: [
            { itemId: 5, quantity: 1, price: 50 }  // Iron Sword
          ],
          services: [
            { name: 'Weapon Repair', description: 'Restore durability to your weapons', price: 10 },
            { name: 'Armor Repair', description: 'Restore durability to your armor', price: 15 }
          ]
        },
        {
          name: 'Elara the Alchemist',
          description: 'An elderly woman with bright eyes and hair tied in a bun. She knows all about herbs and potions.',
          npcType: 'merchant',
          locationRegion: 'Silvermist Valley',
          locationArea: 'Mossy_Hollow',
          dialogue: {
            greeting: [
              'Ah, hello there! Looking for potions or perhaps some alchemical advice?',
              'Welcome to my humble shop. Careful not to knock anything over!'
            ],
            shop: [
              'My potions are of the highest quality, I assure you.'
            ]
          },
          wares: [
            { itemId: 3, quantity: 5, price: 15 },  // Health Potion
            { itemId: 4, quantity: 3, price: 15 }   // Mana Potion
          ]
        }
      ]);
    }

    console.log('Database seeding completed!');
  } catch (error) {
    console.error('Error seeding database:', error);
  }
}

// Run the seed function
seed().catch(console.error);