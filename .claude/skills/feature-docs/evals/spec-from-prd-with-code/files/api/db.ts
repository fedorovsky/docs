import knex from "knex";

// One pool for the API and the workers; tables: merchants, orders, order_items, jobs.
export const db = knex({ client: "pg", connection: process.env.DATABASE_URL });
