import json
from datetime import datetime
from pathlib import Path

import aiosqlite

DB_PATH = Path("social_content.db")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                source_url TEXT DEFAULT '',
                platform TEXT NOT NULL,
                content TEXT NOT NULL,
                hashtags TEXT DEFAULT '[]',
                status TEXT DEFAULT 'draft',
                scheduled_at TEXT,
                published_at TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS generation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                platforms TEXT NOT NULL,
                post_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        await db.commit()


async def save_post(
    topic: str,
    source_url: str,
    platform: str,
    content: str,
    hashtags: list[str],
    status: str = "draft",
    scheduled_at: str | None = None,
) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            """INSERT INTO posts
            (topic, source_url, platform, content, hashtags, status, scheduled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (topic, source_url, platform, content, json.dumps(hashtags), status, scheduled_at),
        )
        await db.commit()
        return cursor.lastrowid


async def get_post(post_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
        row = await cursor.fetchone()
        if row:
            return _row_to_dict(row)
        return None


async def list_posts(
    platform: str | None = None,
    status: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM posts WHERE 1=1"
        params: list = []
        if platform:
            query += " AND platform = ?"
            params.append(platform)
        if status:
            query += " AND status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        return [_row_to_dict(row) for row in rows]


async def update_post(post_id: int, **fields) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        if "hashtags" in fields:
            fields["hashtags"] = json.dumps(fields["hashtags"])
        fields["updated_at"] = datetime.utcnow().isoformat()
        set_clause = ", ".join(f"{k} = ?" for k in fields)
        values = list(fields.values()) + [post_id]
        result = await db.execute(f"UPDATE posts SET {set_clause} WHERE id = ?", values)
        await db.commit()
        return result.rowcount > 0


async def delete_post(post_id: int) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        result = await db.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        await db.commit()
        return result.rowcount > 0


async def get_stats() -> dict:
    async with aiosqlite.connect(DB_PATH) as db:
        total = await (await db.execute("SELECT COUNT(*) FROM posts")).fetchone()
        draft = await (
            await db.execute("SELECT COUNT(*) FROM posts WHERE status = 'draft'")
        ).fetchone()
        scheduled = await (
            await db.execute("SELECT COUNT(*) FROM posts WHERE status = 'scheduled'")
        ).fetchone()
        published = await (
            await db.execute("SELECT COUNT(*) FROM posts WHERE status = 'published'")
        ).fetchone()
        return {
            "total": total[0],
            "draft": draft[0],
            "scheduled": scheduled[0],
            "published": published[0],
        }


async def get_calendar(year: int, month: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        start = f"{year}-{month:02d}-01"
        if month == 12:
            end = f"{year + 1}-01-01"
        else:
            end = f"{year}-{month + 1:02d}-01"
        cursor = await db.execute(
            "SELECT * FROM posts WHERE scheduled_at >= ? "
            "AND scheduled_at < ? ORDER BY scheduled_at",
            (start, end),
        )
        rows = await cursor.fetchall()
        return [_row_to_dict(row) for row in rows]


def _row_to_dict(row) -> dict:
    d = dict(row)
    if "hashtags" in d and isinstance(d["hashtags"], str):
        d["hashtags"] = json.loads(d["hashtags"])
    return d
