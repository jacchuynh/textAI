import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from '@shared/schema';

// Use the environment DATABASE_URL or create a default one
const connectionString = process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/postgres';

// Create a client for standard queries
const client = postgres(connectionString);

// Create db instance with all schema imports
export const db = drizzle(client, { schema });

// Export a standalone function to run queries directly
export const query = client;