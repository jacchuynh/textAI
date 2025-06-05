import { db, schema } from './index';
import { eq } from 'drizzle-orm';

/**
 * Seed script for the fantasy RPG game database
 * Populates initial game regions, areas, spells, items, and quests
 */
async function seed() {
  console.log('Starting database seed process...');

  try {
    // Check if we already have data to avoid duplicates
    const existingRegions = await db.select().from(schema.regions);
    if (existingRegions.length > 0) {
      console.log('Database already contains data. Skipping seed process.');
      return;
    }

    // Seed game regions based on your Crimson Accord world
    const regionData = [
      {
        name: 'Skarport',
        description: 'The Harmonized Capital - Built at the delta convergence of three rivers as neutral ground to house the Crimson Accord. The diplomatic heart and economic nerve center of the continent, where all races coexist under the watchful governance of the Accord Council.',
        climate: 'temperate',
        dangerLevel: 1,
        dominantMagicAspect: 'balance',
        magicalProperties: {
          leylineStrength: 'high',
          naturalManaFlow: 'stable',
          magicalPhenomena: ['leyline stabilization zones', 'neutral magic fields', 'harmonic resonance']
        }
      },
      {
        name: 'Stonewake',
        description: 'The Industrial Heart of the Accord - A dwarven-dominated fortress city built into mountain slopes, where the great forges never sleep. Steam and magical energy power massive foundries that supply weapons and tools to the entire continent.',
        climate: 'temperate',
        dangerLevel: 3,
        dominantMagicAspect: 'earth',
        magicalProperties: {
          leylineStrength: 'high',
          naturalManaFlow: 'channeled',
          magicalPhenomena: ['forge-fire elementals', 'metal resonance', 'earth tremors']
        }
      },
      {
        name: 'Lethandrel',
        description: 'The Living Archive - An elven city built into and with nature itself, where towering trees are braided with crystal canopies and knowledge is preserved in living memory. The premier center of magical learning and lore preservation.',
        climate: 'temperate',
        dangerLevel: 2,
        dominantMagicAspect: 'nature',
        magicalProperties: {
          leylineStrength: 'very high',
          naturalManaFlow: 'abundant',
          magicalPhenomena: ['singing trees', 'memory groves', 'temporal echoes']
        }
      },
      {
        name: 'Rivemark',
        description: 'The Grainward Bastion - A fortified agricultural settlement along a massive river delta, surrounded by rich farmlands. Born from wartime necessity, it now feeds much of the continent while maintaining strong military traditions.',
        climate: 'temperate',
        dangerLevel: 4,
        dominantMagicAspect: 'growth',
        magicalProperties: {
          leylineStrength: 'medium',
          naturalManaFlow: 'fertile',
          magicalPhenomena: ['blessing fields', 'river spirits', 'border ward-lines']
        }
      }
    ];

    console.log('Seeding regions...');
    const insertedRegions = await db.insert(schema.regions).values(regionData).returning();
    const regionMap = new Map(insertedRegions.map(region => [region.name, region.id]));

    // Seed areas within regions
    console.log('Seeding areas...');
    const areaData = [
      // Skarport areas
      {
        regionId: regionMap.get('Skarport'),
        name: 'Accord_Ring',
        description: 'Center of governance and diplomacy, housing the Accord chambers and embassies. Towering spire of glass-inlaid stone with floating archives and neutral negotiation halls.',
        terrain: 'urban',
        points_of_interest: [
          { name: 'Accord Chambers', type: 'government', description: 'The heart of continental diplomacy where the Crimson Accord Council meets' },
          { name: 'Floating Archives', type: 'library', description: 'Magical repositories of treaties and diplomatic records' }
        ],
        magicalFeatures: {
          ambientMana: 'very high',
          wardProtections: 'exceptional',
          notableEnchantments: 'diplomatic neutrality fields, truth detection wards'
        }
      },
      {
        regionId: regionMap.get('Skarport'),
        name: 'Bridgeport_Commons',
        description: 'Multicultural public marketplace and residential district where bridges span over canals, featuring layered homes and open-air eateries representing all races.',
        terrain: 'urban',
        points_of_interest: [
          { name: 'Unity Market', type: 'marketplace', description: 'Where traders from all races conduct business under Accord protection' },
          { name: 'Cultural Bridge', type: 'landmark', description: 'Symbol of racial unity spanning the three rivers' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'moderate',
          notableEnchantments: 'translation enchantments, peace-keeping wards'
        }
      },
      // Stonewake areas
      {
        regionId: regionMap.get('Stonewake'),
        name: 'Anvilring',
        description: 'The heart of Stonewake\'s industrial might, where the greatest forges and workshops create weapons and tools for the entire continent.',
        terrain: 'industrial',
        points_of_interest: [
          { name: 'Great Forge', type: 'workshop', description: 'Massive magical forge that never sleeps, powered by earth elementals' },
          { name: 'Mastersmith Hall', type: 'guild', description: 'Where the Forgecouncil meets and master craftsmen are honored' }
        ],
        magicalFeatures: {
          ambientMana: 'high',
          wardProtections: 'fire and heat resistance',
          notableEnchantments: 'eternal flames, metal-shaping enchantments'
        }
      },
      {
        regionId: regionMap.get('Stonewake'),
        name: 'Hammerdeep',
        description: 'Underground residential district carved deep into the mountain, home to dwarven families and ancestral vaults dating back centuries.',
        terrain: 'underground',
        points_of_interest: [
          { name: 'Ancestral Vaults', type: 'tomb', description: 'Sacred burial chambers of great dwarven smiths and warriors' },
          { name: 'Deep Halls', type: 'residential', description: 'Traditional dwarven family compounds built into living rock' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'structural integrity, earth communion',
          notableEnchantments: 'stone-speaking, ancestral memory crystals'
        }
      },
      // Lethandrel areas
      {
        regionId: regionMap.get('Lethandrel'),
        name: 'Verdant_Ring',
        description: 'Central district with council chambers, great archive halls, and philosophical forums, built among singing trees and luminous moss paths.',
        terrain: 'forest',
        points_of_interest: [
          { name: 'Conclave of Vines', type: 'government', description: 'Living council chambers where the elven leadership meets among ancient trees' },
          { name: 'Archive Groves', type: 'library', description: 'Knowledge stored in living memory trees and crystal repositories' }
        ],
        magicalFeatures: {
          ambientMana: 'very high',
          wardProtections: 'nature harmony, temporal stability',
          notableEnchantments: 'memory preservation, living architecture'
        }
      },
      {
        regionId: regionMap.get('Lethandrel'),
        name: 'Leyroot_Grove',
        description: 'Sacred convergence of leyline magic, protected for study and meditation. Only trained mages may enter due to wild magic risks.',
        terrain: 'sacred grove',
        points_of_interest: [
          { name: 'Leyline Nexus', type: 'magical', description: 'Convergence point of multiple magical leylines requiring careful study' },
          { name: 'Spirit Trees', type: 'sacred', description: 'Ancient trees that serve as conduits for communion with nature spirits' }
        ],
        magicalFeatures: {
          ambientMana: 'extreme',
          wardProtections: 'wild magic containment, unauthorized access prevention',
          notableEnchantments: 'leyline channeling, spirit communication'
        }
      },
      // Rivemark areas
      {
        regionId: regionMap.get('Rivemark'),
        name: 'Grainreach',
        description: 'Agricultural core with massive silos, seedhouses, and food distribution centers connected by irrigation canals.',
        terrain: 'agricultural',
        points_of_interest: [
          { name: 'Grand Silos', type: 'storage', description: 'Massive magical storage facilities that preserve grain for the continent' },
          { name: 'Harvest Halls', type: 'market', description: 'Where agricultural guilds coordinate food distribution across the Accord' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'preservation magic, pest control',
          notableEnchantments: 'growth enhancement, weather prediction'
        }
      },
      {
        regionId: regionMap.get('Rivemark'),
        name: 'Border_Watch',
        description: 'Fortified district facing the dangerous eastern borderlands, where the Marshal\'s forces maintain vigilance against threats.',
        terrain: 'fortified',
        points_of_interest: [
          { name: 'Marshal\'s Tower', type: 'military', description: 'Command center for Rivemark\'s military operations and border defense' },
          { name: 'Watch Gates', type: 'fortification', description: 'Heavily defended entry points monitoring the dangerous eastern approaches' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'early warning systems, defensive barriers',
          notableEnchantments: 'scrying networks, magical fortifications'
        }
      }
    ];

    // Validate all areas have valid regionIds and cast to proper type
    const validAreaData = areaData
      .filter((area): area is typeof area & { regionId: number } => {
        const hasValidRegionId = area.regionId !== undefined;
        if (!hasValidRegionId) {
          console.warn(`Skipping area ${area.name} - no valid regionId found`);
        }
        return hasValidRegionId;
      });
    
    await db.insert(schema.areas).values(validAreaData);

    // Seed spells
    console.log('Seeding spells...');
    const spellData = [
      {
        name: 'Accord Binding',
        description: 'A diplomatic spell that creates a temporary zone of peaceful negotiation, preventing hostile actions.',
        aspect: 'balance',
        manaCost: 15,
        castTime: '2.0',
        cooldown: '30.0',
        effects: {
          type: 'utility',
          duration: 300,
          areaOfEffect: 'medium',
          properties: ['peace zone', 'diplomatic enhancement', 'conflict prevention']
        },
        requiredLevel: 3
      },
      {
        name: 'Forgefire Blast',
        description: 'Channels the power of Stonewake\'s great forges into a concentrated blast of superheated energy.',
        aspect: 'earth',
        manaCost: 25,
        castTime: '1.5',
        cooldown: '8.0',
        effects: {
          damageType: 'fire',
          baseDamage: 35,
          scaling: 'spell power',
          properties: ['projectile', 'armor piercing', 'metal heating']
        },
        requiredLevel: 4
      },
      {
        name: 'Memory Grove Communion',
        description: 'Taps into Lethandrel\'s living archives to gain insight from stored memories and knowledge.',
        aspect: 'nature',
        manaCost: 20,
        castTime: '3.0',
        cooldown: '60.0',
        effects: {
          type: 'divination',
          properties: ['knowledge seeking', 'memory access', 'wisdom enhancement'],
          duration: 60
        },
        requiredLevel: 5
      },
      {
        name: 'Crimson Ward',
        description: 'A protective spell developed during the Crimson Dissonance, creating barriers against war magic.',
        aspect: 'arcane',
        manaCost: 30,
        castTime: '2.5',
        cooldown: '45.0',
        effects: {
          type: 'buff',
          duration: 180,
          properties: ['magic resistance', 'war magic protection', 'stability enhancement'],
          values: {
            magicResistance: 0.3,
            warMagicResistance: 0.5
          }
        },
        requiredLevel: 6
      },
      {
        name: 'Grain Blessing',
        description: 'Enhances crop growth and fertility, a staple magic used throughout Rivemark\'s agricultural districts.',
        aspect: 'growth',
        manaCost: 12,
        castTime: '4.0',
        cooldown: '120.0',
        effects: {
          type: 'enhancement',
          areaOfEffect: 'large',
          properties: ['growth acceleration', 'disease resistance', 'yield increase'],
          duration: 3600
        },
        requiredLevel: 2
      },
      {
        name: 'Racial Harmony',
        description: 'Reduces racial tensions and promotes understanding between different peoples, often used in Skarport.',
        aspect: 'balance',
        manaCost: 18,
        castTime: '1.0',
        cooldown: '20.0',
        effects: {
          type: 'social',
          areaOfEffect: 'medium',
          properties: ['empathy enhancement', 'prejudice reduction', 'communication clarity'],
          duration: 1800
        },
        requiredLevel: 3
      },
      {
        name: 'Leyline Tap',
        description: 'Safely draws energy from nearby leylines, a technique mastered by Lethandrel\'s mages.',
        aspect: 'arcane',
        manaCost: 5,
        castTime: '1.5',
        cooldown: '15.0',
        effects: {
          type: 'restoration',
          properties: ['mana restoration', 'leyline connection', 'energy channeling'],
          values: {
            manaRestored: 40
          }
        },
        requiredLevel: 4
      },
      {
        name: 'Border Sentinel',
        description: 'Creates a magical watchtower that alerts defenders to approaching threats, used along Rivemark\'s borders.',
        aspect: 'earth',
        manaCost: 35,
        castTime: '5.0',
        cooldown: '300.0',
        effects: {
          type: 'summoning',
          duration: 7200,
          properties: ['detection', 'early warning', 'threat assessment'],
          areaOfEffect: 'very large'
        },
        requiredLevel: 7
      }
    ];

    const insertedSpells = await db.insert(schema.spells).values(spellData).returning();
    const spellMap = new Map(insertedSpells.map(spell => [spell.name, spell.id]));

    // Seed items
    console.log('Seeding items...');
    const itemData = [
      {
        name: 'Accord Sigil Ring',
        description: 'A ring bearing the seal of the Crimson Accord, granting the wearer recognition and basic diplomatic immunity.',
        type: 'accessory',
        rarity: 'common',
        value: 75,
        stats: {
          diplomacy: 5,
          reputation: 10
        },
        magicProperties: {
          aspects: ['balance'],
          enchantments: ['diplomatic recognition', 'peaceful aura']
        },
        requiredLevel: 1
      },
      {
        name: 'Diplomatic Seal',
        description: 'An official seal allowing the bearer to conduct minor diplomatic business on behalf of the Accord.',
        type: 'document',
        rarity: 'common',
        value: 50,
        stats: {},
        magicProperties: {
          effects: ['diplomatic authority', 'document authentication'],
          duration: 'permanent'
        },
        requiredLevel: 1
      },
      {
        name: 'Forgemaster\'s Hammer',
        description: 'A masterwork hammer imbued with the essence of Stonewake\'s great forges, excellent for both crafting and combat.',
        type: 'weapon',
        rarity: 'uncommon',
        value: 200,
        stats: {
          damage: 25,
          craftingBonus: 15,
          fireResistance: 20
        },
        magicProperties: {
          aspects: ['earth', 'fire'],
          enchantments: ['forge-fire channeling', 'metal shaping']
        },
        requiredLevel: 3
      },
      {
        name: 'Heat-Resistant Gear',
        description: 'Protective equipment designed for working near the intense heat of magical forges and foundries.',
        type: 'armor',
        rarity: 'common',
        value: 120,
        stats: {
          armor: 8,
          fireResistance: 35,
          heatResistance: 50
        },
        magicProperties: {
          aspects: ['earth'],
          enchantments: ['heat dissipation', 'forge protection']
        },
        requiredLevel: 2
      },
      {
        name: 'Living Wood Staff',
        description: 'A staff carved from one of Lethandrel\'s memory trees, still alive and connected to the forest\'s knowledge.',
        type: 'weapon',
        rarity: 'rare',
        value: 350,
        stats: {
          spellPower: 20,
          natureMagicBonus: 25,
          memoryAccess: 15
        },
        magicProperties: {
          aspects: ['nature', 'memory'],
          enchantments: ['living wood growth', 'ancestral wisdom']
        },
        requiredLevel: 5
      },
      {
        name: 'Memory Crystal',
        description: 'A crystal that can store and replay memories, knowledge, and experiences for later study.',
        type: 'consumable',
        rarity: 'uncommon',
        value: 100,
        stats: {},
        magicProperties: {
          effects: ['memory storage', 'knowledge transfer', 'experience replay'],
          duration: 'single use'
        },
        requiredLevel: 1
      },
      {
        name: 'Scout\'s Cloak',
        description: 'A practical cloak worn by Rivemark\'s border scouts, enchanted for stealth and environmental protection.',
        type: 'armor',
        rarity: 'uncommon',
        value: 180,
        stats: {
          armor: 6,
          stealth: 20,
          weatherResistance: 15
        },
        magicProperties: {
          aspects: ['air', 'earth'],
          enchantments: ['environmental adaptation', 'sound dampening']
        },
        requiredLevel: 4
      },
      {
        name: 'Border Map',
        description: 'A detailed map of Rivemark\'s eastern borderlands, updated with current threat assessments and patrol routes.',
        type: 'document',
        rarity: 'common',
        value: 60,
        stats: {
          navigation: 10,
          borderKnowledge: 15
        },
        magicProperties: {
          effects: ['location tracking', 'threat awareness'],
          duration: 'permanent'
        },
        requiredLevel: 1
      },
      {
        name: 'Crimson Dissonance Relic',
        description: 'A fragment from the great war, carefully stabilized and studied. Contains immense but dangerous power.',
        type: 'material',
        rarity: 'legendary',
        value: 1000,
        stats: {},
        magicProperties: {
          aspects: ['war magic', 'chaos'],
          usages: ['powerful enchantments', 'historical research', 'dangerous experiments']
        },
        requiredLevel: 10
      }
    ];

    const insertedItems = await db.insert(schema.items).values(itemData).returning();
    const itemMap = new Map(insertedItems.map(item => [item.name, item.id]));

    // Seed quests
    console.log('Seeding quests...');
    const questData = [
      {
        title: 'Welcome to the Accord',
        description: 'Complete your orientation in Skarport by learning about the Crimson Accord and the delicate balance between the races.',
        region: 'Skarport',
        requiredLevel: 1,
        rewards: {
          experience: 100,
          gold: 50,
          items: [
            { id: itemMap.get('Accord Sigil Ring'), quantity: 1 },
            { id: itemMap.get('Diplomatic Seal'), quantity: 1 }
          ]
        },
        objectives: [
          { type: 'speak_to', target: 'accord_clerk', description: 'Report to the Accord Registry for orientation' },
          { type: 'visit', target: 'unity_crest', description: 'Tour the multicultural Unity Crest district' },
          { type: 'speak_to', target: 'racial_ambassador', description: 'Meet with representatives from each major race' }
        ]
      },
      {
        title: 'Forge Troubles',
        description: 'The great forges of Stonewake are experiencing mysterious malfunctions. Investigate the cause and restore normal operations.',
        region: 'Stonewake',
        requiredLevel: 3,
        rewards: {
          experience: 250,
          gold: 150,
          items: [
            { id: itemMap.get('Forgemaster\'s Hammer'), quantity: 1 },
            { id: itemMap.get('Heat-Resistant Gear'), quantity: 1 }
          ]
        },
        objectives: [
          { type: 'speak_to', target: 'forgemaster', description: 'Consult with the Forgemaster about the malfunctions' },
          { type: 'investigate', target: 'great_forge', description: 'Examine the Great Forge for signs of sabotage' },
          { type: 'collect', target: 'corrupted_ore', count: 3, description: 'Gather samples of the corrupted metal' },
          { type: 'cast_spell', target: 'forge_fire', spell: 'purification', description: 'Cleanse the forge fires of corruption' }
        ]
      },
      {
        title: 'Memory Grove Awakening',
        description: 'The ancient memory trees in Lethandrel\'s Leyroot Grove have begun showing disturbing visions. Help the Conclave of Vines understand what they\'re trying to communicate.',
        region: 'Lethandrel',
        requiredLevel: 5,
        rewards: {
          experience: 400,
          gold: 200,
          items: [
            { id: itemMap.get('Living Wood Staff'), quantity: 1 },
            { id: itemMap.get('Memory Crystal'), quantity: 2 }
          ]
        },
        objectives: [
          { type: 'speak_to', target: 'conclave_elder', description: 'Seek audience with the Conclave of Vines' },
          { type: 'commune', target: 'memory_tree', description: 'Commune with the ancient memory trees' },
          { type: 'interpret', target: 'vision_fragments', count: 5, description: 'Interpret the fragmented visions from the trees' },
          { type: 'speak_to', target: 'dreamroot_shaman', description: 'Consult with a Dreamroot Pact shaman about the meanings' }
        ]
      },
      {
        title: 'Border Incursion',
        description: 'Unknown forces have been spotted near Rivemark\'s eastern borders. The Marshal needs scouts to investigate and determine the threat level.',
        region: 'Rivemark',
        requiredLevel: 4,
        rewards: {
          experience: 350,
          gold: 180,
          items: [
            { id: itemMap.get('Scout\'s Cloak'), quantity: 1 },
            { id: itemMap.get('Border Map'), quantity: 1 }
          ]
        },
        objectives: [
          { type: 'speak_to', target: 'marshal', description: 'Receive orders from the Marshal at the command tower' },
          { type: 'patrol', target: 'eastern_border', description: 'Scout the eastern borderlands for signs of incursion' },
          { type: 'track', target: 'unknown_forces', description: 'Follow the tracks of the mysterious intruders' },
          { type: 'report', target: 'findings', description: 'Return to the Marshal with intelligence on the threat' }
        ]
      }
    ];

    await db.insert(schema.quests).values(questData);

    // Seed magical materials
    console.log('Seeding magical materials...');
    const materialData = [
      {
        name: 'Accord Harmony Crystal',
        description: 'A stabilized crystal found in Skarport\'s diplomatic chambers, resonating with peaceful energy and magical balance.',
        aspect: 'balance',
        rarity: 'uncommon',
        potency: 2,
        usages: ['diplomatic enchantments', 'conflict resolution magic', 'peace ward creation']
      },
      {
        name: 'Forgeheart Iron',
        description: 'Metal infused with the eternal flames of Stonewake\'s great forges. Perpetually warm and incredibly durable.',
        aspect: 'earth',
        rarity: 'common',
        potency: 2,
        usages: ['weapon crafting', 'heat enchantments', 'structural reinforcement']
      },
      {
        name: 'Memory Tree Bark',
        description: 'Bark from Lethandrel\'s living archive trees, containing fragments of stored knowledge and memories.',
        aspect: 'nature',
        rarity: 'uncommon',
        potency: 3,
        usages: ['memory magic', 'knowledge preservation', 'wisdom enchantments']
      },
      {
        name: 'Riverdelta Silt',
        description: 'Magically enriched soil from Rivemark\'s fertile deltas, blessed by generations of agricultural magic.',
        aspect: 'growth',
        rarity: 'common',
        potency: 1,
        usages: ['agricultural magic', 'healing potions', 'growth enchantments']
      },
      {
        name: 'Leyline Resonance Stone',
        description: 'A crystallized fragment of leyline energy, found where multiple magical currents converge.',
        aspect: 'arcane',
        rarity: 'rare',
        potency: 4,
        usages: ['mana restoration', 'leyline manipulation', 'powerful spellcrafting']
      },
      {
        name: 'Crimson Dissonance Shard',
        description: 'A dangerous fragment of war magic from the great conflict, carefully contained and studied.',
        aspect: 'war magic',
        rarity: 'legendary',
        potency: 5,
        usages: ['forbidden research', 'war relic study', 'extremely dangerous enchantments']
      },
      {
        name: 'Post-War Bloom Petal',
        description: 'Petals from flowers that grew in the aftermath of the Crimson Dissonance, symbolizing hope and renewal.',
        aspect: 'healing',
        rarity: 'uncommon',
        potency: 2,
        usages: ['healing magic', 'purification rituals', 'renewal enchantments']
      },
      {
        name: 'Racial Unity Gem',
        description: 'A rare multi-colored gem that forms when representatives of all races work together in magical harmony.',
        aspect: 'harmony',
        rarity: 'rare',
        potency: 3,
        usages: ['diplomatic magic', 'racial cooperation spells', 'unity enchantments']
      }
    ];

    await db.insert(schema.magicalMaterials).values(materialData);

    console.log('Seed data successfully inserted!');
  } catch (error) {
    console.error('Error seeding database:', error);
    process.exit(1);
  }
}

// Run the seed function if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  seed()
    .then(() => {
      console.log('Seed completed successfully');
      process.exit(0);
    })
    .catch((err) => {
      console.error('Seed failed:', err);
      process.exit(1);
    });
}

export { seed };