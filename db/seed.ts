import { db } from "./index";
import * as schema from "@shared/schema";
import { GAME_CLASSES } from "../client/src/lib/utils";

async function seed() {
  try {
    console.log("Starting database seed...");
    
    // Seed starter locations
    console.log("Seeding locations...");
    const locations = [
      {
        name: "Willowbrook Village",
        description: "A small village on the outskirts of Valoria, known for its sprawling willow trees and friendly inhabitants.",
        type: "village",
        connections: [2, 3],
        npcs: [
          { 
            id: 1, 
            name: "Elder Thorne", 
            description: "The wise village elder who knows much of Eldoria's history.", 
            attitude: "friendly" 
          },
          { 
            id: 2, 
            name: "Merchant Galen", 
            description: "A trader with goods from across the realm.", 
            attitude: "friendly" 
          }
        ]
      },
      {
        name: "Darkwood Forest",
        description: "An ancient forest with towering trees that block out most sunlight. Many travelers speak of strange creatures lurking within.",
        type: "wilderness",
        connections: [1, 4],
        npcs: [
          { 
            id: 3, 
            name: "Ranger Elara", 
            description: "A skilled forest guardian who protects travelers.", 
            attitude: "neutral" 
          }
        ]
      },
      {
        name: "Frostpeak Mountains",
        description: "Towering mountains with snow-capped peaks. Home to hardy mountain folk and dangerous beasts.",
        type: "wilderness",
        connections: [1, 5],
        npcs: []
      },
      {
        name: "Ancient Ruins",
        description: "The crumbling remains of a once-great civilization. Artifacts of power are rumored to be hidden within.",
        type: "dungeon",
        connections: [2],
        npcs: []
      },
      {
        name: "Valorian Capital",
        description: "The grand capital city of the kingdom of Valoria, with towering spires and bustling marketplaces.",
        type: "city",
        connections: [3],
        npcs: [
          { 
            id: 4, 
            name: "King Aldric", 
            description: "The ruler of Valoria, fair but troubled by recent events.", 
            attitude: "neutral" 
          },
          { 
            id: 5, 
            name: "Royal Wizard Thalia", 
            description: "The king's advisor and master of arcane arts.", 
            attitude: "neutral" 
          }
        ]
      }
    ];

    for (const location of locations) {
      await db.insert(schema.locations).values(location);
    }
    console.log(`Added ${locations.length} locations.`);
    
    // Seed starter enemies
    console.log("Seeding enemy templates...");
    // These would be stored in a separate table in a real implementation
    // Here we're just documenting the enemy templates for the game engine to use
    
    const enemyTemplates = [
      {
        name: "Forest Wolf",
        level: 1,
        maxHealth: 20,
        stats: {
          strength: 8,
          dexterity: 12,
          intelligence: 3
        },
        attacks: [
          { name: "Bite", damage: 4, type: "physical" },
          { name: "Claw", damage: 3, type: "physical" }
        ]
      },
      {
        name: "Goblin Scout",
        level: 2,
        maxHealth: 15,
        stats: {
          strength: 6,
          dexterity: 14,
          intelligence: 8
        },
        attacks: [
          { name: "Dagger Strike", damage: 5, type: "physical" },
          { name: "Throw Rock", damage: 3, type: "physical" }
        ]
      },
      {
        name: "Mountain Bear",
        level: 3,
        maxHealth: 40,
        stats: {
          strength: 15,
          dexterity: 8,
          intelligence: 4
        },
        attacks: [
          { name: "Maul", damage: 8, type: "physical" },
          { name: "Crushing Embrace", damage: 10, type: "physical" }
        ]
      },
      {
        name: "Ancient Guardian",
        level: 5,
        maxHealth: 60,
        stats: {
          strength: 14,
          dexterity: 10,
          intelligence: 12
        },
        attacks: [
          { name: "Stone Fist", damage: 12, type: "physical" },
          { name: "Ancient Magic", damage: 15, type: "magical" }
        ]
      }
    ];
    
    console.log(`Prepared ${enemyTemplates.length} enemy templates for the game engine.`);
    console.log("Seed completed successfully!");
  } catch (error) {
    console.error("Error during seeding:", error);
  }
}

seed();
