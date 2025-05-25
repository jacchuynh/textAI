// Database schema push script
// This script applies the schema defined in shared/schema.ts to the database

import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';

async function main() {
  console.log('Starting database schema push...');
  
  try {
    // Use the DATABASE_URL environment variable for the connection
    const connectionString = process.env.DATABASE_URL;
    if (!connectionString) {
      throw new Error('DATABASE_URL environment variable is not set');
    }
    
    // Connect to the database
    const migrationClient = postgres(connectionString, { max: 1 });
    
    // Create all tables that don't exist yet
    const sqlStatements = [];
    
    // Players table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        level INTEGER NOT NULL DEFAULT 1,
        experience INTEGER NOT NULL DEFAULT 0,
        gold INTEGER NOT NULL DEFAULT 0,
        health_current INTEGER NOT NULL DEFAULT 100,
        health_max INTEGER NOT NULL DEFAULT 100,
        location_region TEXT NOT NULL,
        location_area TEXT NOT NULL,
        location_coordinates JSONB NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Magic profiles table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS magic_profiles (
        id SERIAL PRIMARY KEY,
        player_id INTEGER NOT NULL UNIQUE REFERENCES players(id),
        mana_current INTEGER NOT NULL DEFAULT 50,
        mana_max INTEGER NOT NULL DEFAULT 50,
        magic_affinity TEXT NOT NULL DEFAULT 'novice',
        known_aspects JSONB NOT NULL DEFAULT '["basic"]',
        ritual_capacity INTEGER NOT NULL DEFAULT 0,
        magic_experience INTEGER NOT NULL DEFAULT 0,
        magic_level INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Items table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS items (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        item_type TEXT NOT NULL,
        rarity TEXT NOT NULL DEFAULT 'common',
        value INTEGER NOT NULL DEFAULT 0,
        weight DECIMAL NOT NULL DEFAULT 1,
        stats JSONB,
        requirements JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Player items table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS player_items (
        id SERIAL PRIMARY KEY,
        player_id INTEGER NOT NULL REFERENCES players(id),
        item_id INTEGER NOT NULL REFERENCES items(id),
        quantity INTEGER NOT NULL DEFAULT 1,
        is_equipped BOOLEAN NOT NULL DEFAULT false,
        equipped_slot TEXT,
        durability INTEGER,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Materials table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS materials (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        material_type TEXT NOT NULL,
        rarity TEXT NOT NULL DEFAULT 'common',
        value INTEGER NOT NULL DEFAULT 0,
        magical_properties JSONB,
        harvest_locations JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Player materials table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS player_materials (
        id SERIAL PRIMARY KEY,
        player_id INTEGER NOT NULL REFERENCES players(id),
        material_id INTEGER NOT NULL REFERENCES materials(id),
        quantity INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Spells table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS spells (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        mana_cost INTEGER NOT NULL,
        cast_time DECIMAL NOT NULL DEFAULT 1.0,
        cooldown DECIMAL NOT NULL DEFAULT 0,
        damage_type TEXT,
        damage_amount INTEGER,
        heal_amount INTEGER,
        range INTEGER NOT NULL DEFAULT 5,
        area_of_effect INTEGER NOT NULL DEFAULT 0,
        duration INTEGER NOT NULL DEFAULT 0,
        domains JSONB NOT NULL,
        requirements JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Player spells table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS player_spells (
        id SERIAL PRIMARY KEY,
        player_id INTEGER NOT NULL REFERENCES players(id),
        spell_id INTEGER NOT NULL REFERENCES spells(id),
        proficiency INTEGER NOT NULL DEFAULT 1,
        is_favorite BOOLEAN NOT NULL DEFAULT false,
        last_cast_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Quests table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS quests (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        required_level INTEGER NOT NULL DEFAULT 1,
        experience_reward INTEGER NOT NULL DEFAULT 0,
        gold_reward INTEGER NOT NULL DEFAULT 0,
        item_rewards JSONB,
        repeatable BOOLEAN NOT NULL DEFAULT false,
        quest_type TEXT NOT NULL DEFAULT 'main',
        quest_giver TEXT,
        quest_location TEXT,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Quest stages table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS quest_stages (
        id SERIAL PRIMARY KEY,
        quest_id INTEGER NOT NULL REFERENCES quests(id),
        stage_number INTEGER NOT NULL,
        description TEXT NOT NULL,
        objectives JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Player quests table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS player_quests (
        id SERIAL PRIMARY KEY,
        player_id INTEGER NOT NULL REFERENCES players(id),
        quest_id INTEGER NOT NULL REFERENCES quests(id),
        status TEXT NOT NULL DEFAULT 'active',
        started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        completed_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Player quest stages table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS player_quest_stages (
        id SERIAL PRIMARY KEY,
        player_quest_id INTEGER NOT NULL REFERENCES player_quests(id),
        stage_id INTEGER NOT NULL REFERENCES quest_stages(id),
        completed BOOLEAN NOT NULL DEFAULT false,
        progress JSONB DEFAULT '{}',
        completed_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Recipes table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS recipes (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        crafting_type TEXT NOT NULL,
        required_level INTEGER NOT NULL DEFAULT 1,
        item_id INTEGER NOT NULL REFERENCES items(id),
        materials_required JSONB NOT NULL,
        skill_gain INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Player recipes table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS player_recipes (
        id SERIAL PRIMARY KEY,
        player_id INTEGER NOT NULL REFERENCES players(id),
        recipe_id INTEGER NOT NULL REFERENCES recipes(id),
        discovered BOOLEAN NOT NULL DEFAULT true,
        times_crafted INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // NPCs table
    sqlStatements.push(`
      CREATE TABLE IF NOT EXISTS npcs (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        npc_type TEXT NOT NULL,
        location_region TEXT NOT NULL,
        location_area TEXT NOT NULL,
        dialogue JSONB,
        wares JSONB,
        services JSONB,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
      )
    `);
    
    // Execute all SQL statements
    for (const sql of sqlStatements) {
      await migrationClient.unsafe(sql);
    }
    
    console.log('Schema push completed successfully!');
    
    // Close the connection
    await migrationClient.end();
  } catch (error) {
    console.error('Error pushing schema to database:', error);
    process.exit(1);
  }
}

main();