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

    // Seed game regions
    const regionData = [
      {
        name: 'Arcadia',
        description: 'A majestic city-state centered around the Grand Academy of Magic. Its alabaster towers rise high into the clouds, surrounded by a patchwork of gardens, libraries, and magical workshops.',
        climate: 'temperate',
        dangerLevel: 2,
        dominantMagicAspect: 'arcane',
        magicalProperties: {
          leylineStrength: 'high',
          naturalManaFlow: 'very high',
          magicalPhenomena: ['floating islands', 'spontaneous enchantments', 'time anomalies']
        }
      },
      {
        name: 'Shadowvale',
        description: 'Dense, ancient forests where sunlight barely penetrates the thick canopy. Home to ancient spirits and mysterious ruins from a forgotten civilization.',
        climate: 'temperate',
        dangerLevel: 4,
        dominantMagicAspect: 'nature',
        magicalProperties: {
          leylineStrength: 'medium',
          naturalManaFlow: 'high',
          magicalPhenomena: ['talking trees', 'sentient shadows', 'reality distortions']
        }
      },
      {
        name: 'Emberhold',
        description: 'A volcanic mountain range with molten rivers of lava and ash-covered slopes. Home to hardy inhabitants who have learned to harvest the immense heat energy.',
        climate: 'arid',
        dangerLevel: 5,
        dominantMagicAspect: 'fire',
        magicalProperties: {
          leylineStrength: 'high',
          naturalManaFlow: 'high',
          magicalPhenomena: ['eternal flames', 'fire elementals', 'heat mirages']
        }
      },
      {
        name: 'Crystalshore',
        description: 'A coastal region lined with magnificent crystal formations that reflect the ocean waves in a dazzling display of light and color.',
        climate: 'tropical',
        dangerLevel: 3,
        dominantMagicAspect: 'water',
        magicalProperties: {
          leylineStrength: 'medium',
          naturalManaFlow: 'medium',
          magicalPhenomena: ['water crystals', 'singing tides', 'dimensional pools']
        }
      }
    ];

    console.log('Seeding regions...');
    const insertedRegions = await db.insert(schema.regions).values(regionData).returning();
    const regionMap = new Map(insertedRegions.map(region => [region.name, region.id]));

    // Seed areas within regions
    console.log('Seeding areas...');
    const areaData = [
      // Arcadia areas
      {
        regionId: regionMap.get('Arcadia'),
        name: 'Novice_Quarter',
        description: 'Where apprentice mages begin their studies. Small academies and student housing cover the district.',
        terrain: 'urban',
        points_of_interest: [
          { name: 'Apprentice Tower', type: 'academy', description: 'The central training facility for new mages' },
          { name: 'Scribe\'s Alley', type: 'marketplace', description: 'A bustling market for magical scrolls and books' }
        ],
        magicalFeatures: {
          ambientMana: 'high',
          wardProtections: 'strong',
          notableEnchantments: 'self-repairing architecture'
        }
      },
      {
        regionId: regionMap.get('Arcadia'),
        name: 'Grand_Academy',
        description: 'The heart of magical learning in the known world. Towering spires of ivory and gold house the greatest arcane minds.',
        terrain: 'urban',
        points_of_interest: [
          { name: 'Archmage\'s Sanctum', type: 'landmark', description: 'The personal chambers of the Academy\'s leader' },
          { name: 'Great Library', type: 'landmark', description: 'Contains thousands of magical tomes and scrolls' }
        ],
        magicalFeatures: {
          ambientMana: 'very high',
          wardProtections: 'exceptional',
          notableEnchantments: 'animated statues, self-sorting books'
        }
      },
      // Shadowvale areas
      {
        regionId: regionMap.get('Shadowvale'),
        name: 'Twilight_Entrance',
        description: 'The edge of the dark forest where the trees begin to block out the sun and strange sounds echo.',
        terrain: 'forest',
        points_of_interest: [
          { name: 'Warden\'s Post', type: 'settlement', description: 'A small outpost guarding the main path into Shadowvale' },
          { name: 'Whispering Stones', type: 'landmark', description: 'Ancient monoliths that seem to speak to those who listen carefully' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'minimal',
          notableEnchantments: 'illusion detection wards'
        }
      },
      {
        regionId: regionMap.get('Shadowvale'),
        name: 'Heart_of_Shadows',
        description: 'The deepest part of the forest where ancient magic pulses through the very soil and trees.',
        terrain: 'dense forest',
        points_of_interest: [
          { name: 'Elder Tree', type: 'landmark', description: 'A massive tree said to be as old as the world itself' },
          { name: 'Forgotten Temple', type: 'ruin', description: 'Crumbling stone structures with indecipherable carvings' }
        ],
        magicalFeatures: {
          ambientMana: 'very high',
          wardProtections: 'ancient and unpredictable',
          notableEnchantments: 'time dilation, spatial distortion'
        }
      },
      // Emberhold areas
      {
        regionId: regionMap.get('Emberhold'),
        name: 'Ash_Roads',
        description: 'The main path through the lower volcanic slopes, constantly covered in a fine layer of ash.',
        terrain: 'mountain',
        points_of_interest: [
          { name: 'Cinder Trading Post', type: 'settlement', description: 'A hardy outpost where travelers can rest and trade' },
          { name: 'Obsidian Outcrop', type: 'landmark', description: 'A massive formation of black volcanic glass' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'heat resistance',
          notableEnchantments: 'fire resistance enchantments'
        }
      },
      {
        regionId: regionMap.get('Emberhold'),
        name: 'Molten_Core',
        description: 'The heart of the volcanic region where rivers of lava flow and fire elementals roam freely.',
        terrain: 'volcanic',
        points_of_interest: [
          { name: 'Forge of the Ancients', type: 'landmark', description: 'A legendary blacksmithing site that harnesses the volcano\'s power' },
          { name: 'Flamekeepers\' Temple', type: 'landmark', description: 'A temple dedicated to fire magic and elemental summoning' }
        ],
        magicalFeatures: {
          ambientMana: 'high',
          wardProtections: 'extreme heat shielding',
          notableEnchantments: 'eternal flames, lava manipulation'
        }
      },
      // Crystalshore areas
      {
        regionId: regionMap.get('Crystalshore'),
        name: 'Harbor_District',
        description: 'A bustling port town built around natural crystal formations that refract sunlight across the water.',
        terrain: 'coastal',
        points_of_interest: [
          { name: 'Trader\'s Wharf', type: 'marketplace', description: 'Exotic goods from across the seas are bought and sold here' },
          { name: 'Lighthouse Crystal', type: 'landmark', description: 'A massive crystal that serves as a magical lighthouse' }
        ],
        magicalFeatures: {
          ambientMana: 'medium',
          wardProtections: 'storm wards',
          notableEnchantments: 'water breathing, weather prediction'
        }
      },
      {
        regionId: regionMap.get('Crystalshore'),
        name: 'Crystal_Caverns',
        description: 'An extensive network of underwater and coastal caves filled with luminescent crystals.',
        terrain: 'cavern',
        points_of_interest: [
          { name: 'Tidepool Grotto', type: 'landmark', description: 'Magical pools that reveal visions when gazed into' },
          { name: 'Crystal Chorus', type: 'landmark', description: 'A chamber where crystals resonate with musical tones' }
        ],
        magicalFeatures: {
          ambientMana: 'high',
          wardProtections: 'water pressure adaptation',
          notableEnchantments: 'sound amplification, light manipulation'
        }
      }
    ];

    await db.insert(schema.areas).values(areaData);

    // Seed spells
    console.log('Seeding spells...');
    const spellData = [
      {
        name: 'Arcane Missile',
        description: 'Conjures a bolt of pure magical energy that seeks out a target.',
        aspect: 'arcane',
        manaCost: 10,
        castTime: 1.5,
        cooldown: 3.0,
        effects: {
          damageType: 'arcane',
          baseDamage: 15,
          scaling: 'spell power',
          properties: ['projectile', 'seeking']
        },
        requiredLevel: 1
      },
      {
        name: 'Fireball',
        description: 'Hurls a sphere of flame that explodes on impact, damaging all enemies in an area.',
        aspect: 'fire',
        manaCost: 25,
        castTime: 2.0,
        cooldown: 8.0,
        effects: {
          damageType: 'fire',
          baseDamage: 30,
          areaOfEffect: 'medium',
          scaling: 'spell power',
          properties: ['projectile', 'area damage', 'burning']
        },
        requiredLevel: 3
      },
      {
        name: 'Frost Nova',
        description: 'Releases a burst of cold energy, freezing nearby enemies in place.',
        aspect: 'water',
        manaCost: 30,
        castTime: 0.5,
        cooldown: 15.0,
        effects: {
          damageType: 'ice',
          baseDamage: 15,
          areaOfEffect: 'medium',
          scaling: 'spell power',
          properties: ['instant', 'area damage', 'crowd control', 'freezing']
        },
        requiredLevel: 5
      },
      {
        name: 'Stone Skin',
        description: 'Hardens the caster\'s skin, providing protection from physical attacks.',
        aspect: 'earth',
        manaCost: 20,
        castTime: 1.0,
        cooldown: 30.0,
        effects: {
          type: 'buff',
          duration: 60,
          properties: ['armor increase', 'damage reduction'],
          values: {
            armorIncrease: 50,
            damageReduction: 0.2
          }
        },
        requiredLevel: 4
      },
      {
        name: 'Healing Light',
        description: 'Channels healing energy to restore health to the caster or an ally.',
        aspect: 'light',
        manaCost: 35,
        castTime: 2.5,
        cooldown: 5.0,
        effects: {
          type: 'healing',
          baseHealing: 40,
          scaling: 'spell power',
          properties: ['targeted', 'channeled']
        },
        requiredLevel: 2
      },
      {
        name: 'Wind Gust',
        description: 'Summons a powerful gust of wind that pushes enemies away.',
        aspect: 'air',
        manaCost: 15,
        castTime: 1.0,
        cooldown: 12.0,
        effects: {
          type: 'utility',
          properties: ['knockback', 'crowd control'],
          values: {
            knockbackDistance: 10,
            stunDuration: 1.5
          }
        },
        requiredLevel: 2
      },
      {
        name: 'Mana Shield',
        description: 'Creates a protective barrier that absorbs damage at the cost of mana.',
        aspect: 'arcane',
        manaCost: 40,
        castTime: 0.5,
        cooldown: 25.0,
        effects: {
          type: 'buff',
          duration: 120,
          properties: ['damage absorption', 'mana drain'],
          values: {
            damageAbsorption: 100,
            manaDrainRatio: 2 // 2 mana per 1 damage absorbed
          }
        },
        requiredLevel: 6
      },
      {
        name: 'Nature\'s Grasp',
        description: 'Summons vines from the ground to entangle enemies, rooting them in place.',
        aspect: 'nature',
        manaCost: 25,
        castTime: 1.5,
        cooldown: 18.0,
        effects: {
          damageType: 'nature',
          baseDamage: 10,
          damageOverTime: 5,
          duration: 8,
          areaOfEffect: 'small',
          properties: ['targeted', 'area damage', 'crowd control', 'root']
        },
        requiredLevel: 4
      }
    ];

    const insertedSpells = await db.insert(schema.spells).values(spellData).returning();
    const spellMap = new Map(insertedSpells.map(spell => [spell.name, spell.id]));

    // Seed items
    console.log('Seeding items...');
    const itemData = [
      {
        name: 'Apprentice\'s Wand',
        description: 'A basic wand given to new magic students. It helps focus magical energy more efficiently.',
        type: 'weapon',
        rarity: 'common',
        value: 50,
        stats: {
          spellPower: 5,
          manaRegeneration: 1
        },
        magicProperties: {
          aspects: ['arcane'],
          enchantments: ['mana efficiency']
        },
        requiredLevel: 1
      },
      {
        name: 'Spellbook of Fundamentals',
        description: 'Contains basic magical theory and simple spell diagrams. A starting point for any aspiring mage.',
        type: 'offhand',
        rarity: 'common',
        value: 75,
        stats: {
          spellPower: 3,
          manaCapacity: 10
        },
        magicProperties: {
          aspects: ['arcane'],
          enchantments: ['knowledge retention']
        },
        requiredLevel: 1
      },
      {
        name: 'Embercloth Robes',
        description: 'Robes woven with fire-resistant thread from the Emberhold region.',
        type: 'armor',
        rarity: 'uncommon',
        value: 120,
        stats: {
          armor: 5,
          fireResistance: 20
        },
        magicProperties: {
          aspects: ['fire'],
          enchantments: ['heat dissipation']
        },
        requiredLevel: 3
      },
      {
        name: 'Crystal Focus',
        description: 'A clear crystal from Crystalshore that helps channel water magic more efficiently.',
        type: 'focus',
        rarity: 'uncommon',
        value: 150,
        stats: {
          waterSpellPower: 8,
          waterSpellCostReduction: 0.1
        },
        magicProperties: {
          aspects: ['water'],
          enchantments: ['clarity', 'flow']
        },
        requiredLevel: 3
      },
      {
        name: 'Shadowveil Cloak',
        description: 'A cloak that seems to absorb light, making the wearer harder to detect in shadows.',
        type: 'armor',
        rarity: 'rare',
        value: 300,
        stats: {
          armor: 8,
          stealth: 15
        },
        magicProperties: {
          aspects: ['shadow'],
          enchantments: ['light absorption', 'sound dampening']
        },
        requiredLevel: 5
      },
      {
        name: 'Mana Potion',
        description: 'A blue potion that restores magical energy when consumed.',
        type: 'consumable',
        rarity: 'common',
        value: 25,
        stats: {},
        magicProperties: {
          effects: ['restore 50 mana'],
          duration: 'instant'
        },
        requiredLevel: 1
      },
      {
        name: 'Health Potion',
        description: 'A red potion that restores health when consumed.',
        type: 'consumable',
        rarity: 'common',
        value: 25,
        stats: {},
        magicProperties: {
          effects: ['restore 50 health'],
          duration: 'instant'
        },
        requiredLevel: 1
      },
      {
        name: 'Arcane Dust',
        description: 'Crystallized magical energy used in enchanting and spellcrafting.',
        type: 'material',
        rarity: 'common',
        value: 15,
        stats: {},
        magicProperties: {
          aspects: ['arcane'],
          usages: ['enchanting', 'spellcrafting']
        },
        requiredLevel: 1
      },
      {
        name: 'Fire Essence',
        description: 'Bottled fire elemental energy that burns eternally.',
        type: 'material',
        rarity: 'uncommon',
        value: 45,
        stats: {},
        magicProperties: {
          aspects: ['fire'],
          usages: ['enchanting', 'potion brewing']
        },
        requiredLevel: 1
      }
    ];

    const insertedItems = await db.insert(schema.items).values(itemData).returning();
    const itemMap = new Map(insertedItems.map(item => [item.name, item.id]));

    // Seed quests
    console.log('Seeding quests...');
    const questData = [
      {
        title: 'Apprentice\'s First Steps',
        description: 'Complete your basic training at the Arcadia Academy by demonstrating your magical abilities.',
        region: 'Arcadia',
        requiredLevel: 1,
        rewards: {
          experience: 100,
          gold: 50,
          items: [
            { id: itemMap.get('Apprentice\'s Wand'), quantity: 1 },
            { id: itemMap.get('Mana Potion'), quantity: 2 }
          ]
        },
        objectives: [
          { type: 'cast_spell', target: 'training_dummy', count: 5, description: 'Practice your spells on the training dummies' },
          { type: 'collect', target: 'arcane_essence', count: 3, description: 'Collect arcane essence from the practice grounds' },
          { type: 'speak_to', target: 'professor_lumina', description: 'Report back to Professor Lumina' }
        ]
      },
      {
        title: 'Troublesome Fire Sprites',
        description: 'Fire sprites from Emberhold have been spotted in Arcadia\'s gardens. Investigate and resolve the situation.',
        region: 'Arcadia',
        requiredLevel: 2,
        rewards: {
          experience: 200,
          gold: 100,
          items: [
            { id: itemMap.get('Fire Essence'), quantity: 1 },
            { id: itemMap.get('Health Potion'), quantity: 1 }
          ]
        },
        objectives: [
          { type: 'defeat', target: 'fire_sprite', count: 8, description: 'Defeat fire sprites in the gardens' },
          { type: 'collect', target: 'sprite_essence', count: 5, description: 'Collect essence from defeated sprites' },
          { type: 'find', target: 'portal', description: 'Locate the source of the sprites' invasion' },
          { type: 'cast_spell', target: 'portal', spell: 'frost_nova', description: 'Close the portal with frost magic' }
        ]
      },
      {
        title: 'Shadows in the Vale',
        description: 'Strange occurrences have been reported in Shadowvale. Investigate the mysterious sightings.',
        region: 'Shadowvale',
        requiredLevel: 4,
        rewards: {
          experience: 350,
          gold: 200,
          items: [
            { id: itemMap.get('Shadowveil Cloak'), quantity: 1 }
          ]
        },
        objectives: [
          { type: 'speak_to', target: 'forest_warden', description: 'Speak with the Forest Warden at Twilight Entrance' },
          { type: 'explore', target: 'whispering_stones', description: 'Investigate the Whispering Stones' },
          { type: 'defeat', target: 'shadow_entity', count: 3, description: 'Defeat the shadow entities' },
          { type: 'collect', target: 'corrupted_crystal', count: 1, description: 'Retrieve the corrupted crystal' },
          { type: 'speak_to', target: 'elder_druid', description: 'Bring the crystal to the Elder Druid' }
        ]
      },
      {
        title: 'Crystal Resonance',
        description: 'The Lighthouse Crystal in Crystalshore has stopped functioning. Help restore its power.',
        region: 'Crystalshore',
        requiredLevel: 3,
        rewards: {
          experience: 300,
          gold: 150,
          items: [
            { id: itemMap.get('Crystal Focus'), quantity: 1 },
            { id: itemMap.get('Mana Potion'), quantity: 3 }
          ]
        },
        objectives: [
          { type: 'speak_to', target: 'lighthouse_keeper', description: 'Speak with the Lighthouse Keeper' },
          { type: 'explore', target: 'crystal_caverns', description: 'Enter the Crystal Caverns' },
          { type: 'collect', target: 'resonance_shard', count: 5, description: 'Collect resonance shards from the caverns' },
          { type: 'defeat', target: 'crystal_guardian', count: 1, description: 'Defeat the Crystal Guardian' },
          { type: 'use_item', target: 'lighthouse_crystal', item: 'resonance_shard', description: 'Restore the Lighthouse Crystal' }
        ]
      }
    ];

    await db.insert(schema.quests).values(questData);

    // Seed magical materials
    console.log('Seeding magical materials...');
    const materialData = [
      {
        name: 'Arcane Crystal',
        description: 'A crystal infused with pure magical energy. Glows with an inner light.',
        aspect: 'arcane',
        rarity: 'uncommon',
        potency: 2,
        usages: ['enchanting', 'spellcrafting', 'focus creation']
      },
      {
        name: 'Emberroot',
        description: 'A root that grows in volcanic soil. Perpetually warm to the touch.',
        aspect: 'fire',
        rarity: 'common',
        potency: 1,
        usages: ['potion brewing', 'enchanting', 'cooking']
      },
      {
        name: 'Shadowleaf',
        description: 'A plant that grows only in the darkest parts of Shadowvale. Absorbs light around it.',
        aspect: 'shadow',
        rarity: 'uncommon',
        potency: 2,
        usages: ['potion brewing', 'illusion magic', 'stealth enchantments']
      },
      {
        name: 'Tidal Pearl',
        description: 'A pearl infused with water magic, found in the depths of Crystalshore\'s waters.',
        aspect: 'water',
        rarity: 'uncommon',
        potency: 2,
        usages: ['water magic', 'healing potions', 'weather enchantments']
      },
      {
        name: 'Whisperwind Feather',
        description: 'A feather that moves as if constantly touched by a gentle breeze.',
        aspect: 'air',
        rarity: 'common',
        potency: 1,
        usages: ['air magic', 'levitation enchantments', 'speed potions']
      },
      {
        name: 'Living Stone',
        description: 'A small rock that seems to pulse with inner life. Warm to the touch.',
        aspect: 'earth',
        rarity: 'common',
        potency: 1,
        usages: ['earth magic', 'strengthening enchantments', 'defensive wards']
      },
      {
        name: 'Moonlit Flower',
        description: 'A flower that only blooms under moonlight and stores its magical essence.',
        aspect: 'nature',
        rarity: 'uncommon',
        potency: 2,
        usages: ['nature magic', 'healing potions', 'growth enchantments']
      },
      {
        name: 'Dragon Scale',
        description: 'A rare scale from an ancient dragon, infused with powerful magic.',
        aspect: 'various',
        rarity: 'rare',
        potency: 4,
        usages: ['powerful enchantments', 'artifact creation', 'magical armor']
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
if (require.main === module) {
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