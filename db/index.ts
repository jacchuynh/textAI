import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from '@shared/schema';

// Create a PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Create a Drizzle ORM instance
export const db = drizzle(pool, { schema });

// Helpful function to initialize the database - will be used by other files
export async function initializeDatabase() {
  try {
    // Test database connection
    const result = await pool.query('SELECT NOW()');
    console.log('Database connected:', result.rows[0].now);
    
    // Database is ready
    return true;
  } catch (err) {
    console.error('Database connection error:', err);
    return false;
  }
}

// Export the pool for direct SQL queries if needed
export { pool };