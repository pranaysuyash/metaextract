import { drizzle } from "drizzle-orm/node-postgres";
import { Pool } from "pg";
import * as schema from "@shared/schema";

// Check if DATABASE_URL is properly configured
const isDatabaseConfigured = process.env.DATABASE_URL && 
  !process.env.DATABASE_URL.includes("user:password@host");

let db: ReturnType<typeof drizzle> | null = null;

if (isDatabaseConfigured) {
  try {
    const pool = new Pool({
      connectionString: process.env.DATABASE_URL,
    });
    db = drizzle(pool, { schema });
  } catch (error) {
    console.error("Failed to initialize database:", error);
  }
}

export { db };
