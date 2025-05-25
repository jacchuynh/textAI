import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from '@shared/schema';

// Check for required environment variables
if (!process.env.DATABASE_URL) {
  console.error('DATABASE_URL environment variable is required');
  process.exit(1);
}

// Database connection with postgres.js
const connectionString = process.env.DATABASE_URL;
const client = postgres(connectionString, { max: 10 });

// Create drizzle instance with our schema
export const db = drizzle(client, { schema });

// Export schema for direct usage
export { schema };