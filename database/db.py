import asyncpg
from config import SQLConfig


async def create_pool(config: SQLConfig) -> asyncpg.Pool:
    return await asyncpg.create_pool(
        user=config.user,
        password=config.password,
        database=config.name,
        host=config.host,
        port=config.port,
    )


async def init_db(pool: asyncpg.Pool):
    await pool.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            tg_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    await pool.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id SERIAL PRIMARY KEY,
            user_tg_id BIGINT NOT NULL REFERENCES users(tg_id),
            issue_text TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',
            admin_tg_id BIGINT,
            admin_reply TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


async def add_user(pool: asyncpg.Pool, tg_id: int, username: str, full_name: str):

    query = """
        INSERT INTO users (tg_id, username, full_name)
        VALUES ($1, $2, $3)
        ON CONFLICT (tg_id) DO NOTHING;
    """

    await pool.execute(query, tg_id, username, full_name)


async def create_ticket(pool: asyncpg.Pool, user_tg_id: int, issue_text: str) -> int:

    query = """
        INSERT INTO tickets (user_tg_id, issue_text)
        VALUES ($1, $2)
        RETURNING id;
    """

    return await pool.fetchval(query, user_tg_id, issue_text)


async def get_user_tickets(pool: asyncpg.Pool, user_tg_id: int) -> list[asyncpg.Record]:

     query = """
        SELECT id, issue_text, status, created_at
        FROM tickets
        WHERE user_tg_id = $1
        ORDER BY id DESC;
     """

     return await pool.fetch(query, user_tg_id)


async def get_ticket(pool: asyncpg.Pool, ticket_id) -> asyncpg.Record | None:

     query = """
        SELECT id, user_tg_id, issue_text, status, admin_reply, created_at
        FROM tickets
        WHERE id = $1;
     """

     return await pool.fetchrow(query, ticket_id)


async def update_ticket(pool: asyncpg.Pool, answer: str, admin_id: int, ticket_id: int):

    query = """
        UPDATE tickets
        SET status = 'ANSWERED',
            admin_reply = $1,
            admin_tg_id = $2,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $3
    """

    await pool.execute(query, answer, admin_id, ticket_id)


async def close_spam_ticket(pool: asyncpg.Pool, ticket_id: int):

    query = """
        UPDATE tickets
        SET status = 'CLOSED',
            updated_at = CURRENT_TIMESTAMP
        WHERE id = $1;
    """

    await pool.execute(query, ticket_id)