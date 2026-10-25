import os
import asyncpg
from dotenv import load_dotenv
from core.dependency import get_current_user
from fastapi import Depends

load_dotenv()

ADMIN_URL = os.getenv("ADMIN_URL")
DATABASE_URL = os.getenv("DATABASE_URL")
if not ADMIN_URL:
    raise RuntimeError("DATABASE_URL is not set in your .env file")

# the pool — one global pool for the whole app
pool: asyncpg.Pool = None
admin_pool: asyncpg.Pool = None

async def init_pools():
    global pool, admin_pool
    
    # app pool — used for every request
    pool = await asyncpg.create_pool(
        dsn=DATABASE_URL,
        min_size=2,
        max_size=10,
    )
    
    # admin pool — used only for init_db
    admin_pool = await asyncpg.create_pool(
        dsn=ADMIN_URL,
        min_size=1,
        max_size=2,
    )

# fastapi dependency — every route that needs db gets a connection from here
async def get_db():
    async with pool.acquire() as conn:
        yield conn

# for protected routes — token required, RLS applied
async def get_authenticated_db(
    user_id: int = Depends(get_current_user),
):
    async with pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                "SELECT set_config('app.current_user_id', $1, true)",
                str(user_id),
            )
            yield conn

async def init_db():
    async with admin_pool.acquire() as conn:
        # create users table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id              SERIAL PRIMARY KEY,
                email           VARCHAR(255) UNIQUE NOT NULL,
                password_hash   VARCHAR(255) NOT NULL,
                google_id       VARCHAR(255) UNIQUE,
                
                is_active       BOOLEAN NOT NULL DEFAULT TRUE,
                is_verified     BOOLEAN NOT NULL DEFAULT FALSE,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                last_login      TIMESTAMPTZ
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id              SERIAL PRIMARY KEY,
                user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                refresh_token   VARCHAR(512) UNIQUE NOT NULL,
                is_revoked      BOOLEAN NOT NULL DEFAULT FALSE,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                expires_at      TIMESTAMPTZ NOT NULL DEFAULT NOW() + INTERVAL '7 days'
            )
            
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id              SERIAL PRIMARY KEY,
                user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                title           TEXT,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id                  SERIAL PRIMARY KEY,
                conversation_id     INTEGER NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                role                TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                content             TEXT NOT NULL,
                created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
        """)
        
async def close_pools():
    await pool.close()
    await admin_pool.close()