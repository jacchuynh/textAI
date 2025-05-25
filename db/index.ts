import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from '@shared/schema';

// Initialize PostgreSQL client with DATABASE_URL environment variable
const connectionString = process.env.DATABASE_URL;

if (!connectionString) {
  throw new Error('DATABASE_URL environment variable is required');
}

// For query purposes (non-transaction)
export const sql = postgres(connectionString, { max: 10 });

// Initialize Drizzle ORM
export const db = drizzle(sql, { schema });

// Export a query function for raw SQL queries
export const query = sql;