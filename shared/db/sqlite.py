import aiosqlite
from pathlib import Path

# ─── DDL ──────────────────────────────────────────────────────────────────────

_DDL = """
CREATE TABLE IF NOT EXISTS users (
    chat_id     INTEGER PRIMARY KEY,
    full_name   TEXT,
    username    TEXT,
    is_subscribed INTEGER NOT NULL DEFAULT 0,
    lang        TEXT NOT NULL DEFAULT 'uz',
    joined_at   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS videos (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    code                TEXT NOT NULL,
    title               TEXT NOT NULL DEFAULT '',
    part_number         INTEGER,
    file_id             TEXT NOT NULL,
    kind                TEXT NOT NULL DEFAULT 'video',
    caption             TEXT,
    channel_message_id  INTEGER,
    created_at          TEXT NOT NULL,
    UNIQUE(code, part_number)
);

CREATE TABLE IF NOT EXISTS channels (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_id  INTEGER UNIQUE NOT NULL,
    invite_link TEXT
);

CREATE TABLE IF NOT EXISTS join_requests (
    user_id     INTEGER NOT NULL,
    channel_id  INTEGER NOT NULL,
    requested_at TEXT NOT NULL,
    approved_at  TEXT,
    status       TEXT NOT NULL DEFAULT 'requested',
    PRIMARY KEY (user_id, channel_id)
);

CREATE TABLE IF NOT EXISTS rate_limits (
    user_id     INTEGER PRIMARY KEY,
    last_used_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cooldown_settings (
    id      INTEGER PRIMARY KEY CHECK (id = 1),
    seconds INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    user_id    INTEGER PRIMARY KEY,
    full_name  TEXT,
    username   TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_permissions (
    user_id            INTEGER PRIMARY KEY,
    can_add_channel    INTEGER NOT NULL DEFAULT 0,
    can_send_broadcast INTEGER NOT NULL DEFAULT 0,
    can_upload         INTEGER NOT NULL DEFAULT 0,
    can_reset_time     INTEGER NOT NULL DEFAULT 0,
    can_manage_admins  INTEGER NOT NULL DEFAULT 0,
    created_at         TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES admins(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS superadmins (
    user_id    INTEGER PRIMARY KEY,
    full_name  TEXT,
    username   TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS superadmin_permissions (
    user_id            INTEGER PRIMARY KEY,
    can_add_channel    INTEGER NOT NULL DEFAULT 0,
    can_send_broadcast INTEGER NOT NULL DEFAULT 0,
    can_upload         INTEGER NOT NULL DEFAULT 0,
    can_reset_time     INTEGER NOT NULL DEFAULT 0,
    can_manage_admins  INTEGER NOT NULL DEFAULT 1,
    created_at         TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES superadmins(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS requests (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    text       TEXT,
    media_type TEXT,
    file_id    TEXT,
    admin_msg_id INTEGER,
    user_msg_id  INTEGER,
    status     TEXT NOT NULL DEFAULT 'open',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn: aiosqlite.Connection | None = None

    # ── connect / close ───────────────────────────────────────────────────────

    async def connect(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = await aiosqlite.connect(self.db_path)
        self.conn.row_factory = aiosqlite.Row
        await self.conn.execute("PRAGMA journal_mode=WAL;")
        await self.conn.execute("PRAGMA foreign_keys=ON;")
        for stmt in _DDL.strip().split(";"):
            stmt = stmt.strip()
            if stmt:
                await self.conn.execute(stmt)
        await self._migrate()
        await self.conn.commit()

    async def _migrate(self):
        """Eski DB larga ustun qo'shish."""
        cur = await self.conn.execute("PRAGMA table_info(videos);")
        cols = {r[1] for r in await cur.fetchall()}
        await cur.close()
        for col, defn in [
            ("kind", "TEXT NOT NULL DEFAULT 'video'"),
            ("caption", "TEXT"),
            ("title", "TEXT NOT NULL DEFAULT ''"),
        ]:
            if col not in cols:
                await self.conn.execute(f"ALTER TABLE videos ADD COLUMN {col} {defn};")

        cur = await self.conn.execute("PRAGMA table_info(users);")
        ucols = {r[1] for r in await cur.fetchall()}
        await cur.close()
        if "lang" not in ucols:
            await self.conn.execute("ALTER TABLE users ADD COLUMN lang TEXT NOT NULL DEFAULT 'uz';")

        cur = await self.conn.execute("PRAGMA table_info(requests);")
        rcols = {r[1] for r in await cur.fetchall()}
        await cur.close()
        for col, defn in [
            ("media_type", "TEXT"),
            ("file_id", "TEXT"),
            ("admin_msg_id", "INTEGER"),
            ("user_msg_id", "INTEGER"),
        ]:
            if col not in rcols:
                await self.conn.execute(f"ALTER TABLE requests ADD COLUMN {col} {defn};")

    async def close(self):
        if self.conn:
            await self.conn.close()

    # ── users ─────────────────────────────────────────────────────────────────

    async def upsert_user(self, chat_id: int, full_name: str,
                          username: str | None, is_subscribed: bool,
                          lang: str = "uz"):
        await self.conn.execute(
            """
            INSERT INTO users(chat_id, full_name, username, is_subscribed, lang, joined_at)
            VALUES(?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(chat_id) DO UPDATE SET
                full_name=excluded.full_name,
                username=excluded.username,
                is_subscribed=excluded.is_subscribed;
            """,
            (chat_id, full_name, username, int(is_subscribed), lang),
        )
        await self.conn.commit()

    async def get_user(self, chat_id: int) -> dict | None:
        cur = await self.conn.execute(
            "SELECT chat_id, full_name, username, is_subscribed, lang FROM users WHERE chat_id=?",
            (chat_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            return None
        return dict(row)

    async def set_user_lang(self, chat_id: int, lang: str):
        await self.conn.execute(
            """
            INSERT INTO users(chat_id, full_name, username, is_subscribed, lang, joined_at)
            VALUES(?, '', NULL, 0, ?, datetime('now'))
            ON CONFLICT(chat_id) DO UPDATE SET lang=excluded.lang;
            """,
            (chat_id, lang),
        )
        await self.conn.commit()

    async def get_user_lang(self, chat_id: int) -> str:
        cur = await self.conn.execute(
            "SELECT lang FROM users WHERE chat_id=?", (chat_id,)
        )
        row = await cur.fetchone()
        await cur.close()
        return row[0] if row else "uz"

    async def get_all_users(self) -> list[dict]:
        cur = await self.conn.execute(
            "SELECT chat_id, is_subscribed FROM users"
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

    # ── videos ────────────────────────────────────────────────────────────────

    async def save_video(self, code: str, title: str, file_id: str, kind: str,
                         caption: str = "", part_number: int | None = None,
                         channel_message_id: int | None = None):
        await self.conn.execute(
            """
            INSERT INTO videos(code, title, part_number, file_id, kind, caption,
                                channel_message_id, created_at)
            VALUES(?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(code, part_number) DO UPDATE SET
                title=excluded.title,
                file_id=excluded.file_id,
                kind=excluded.kind,
                caption=excluded.caption,
                channel_message_id=excluded.channel_message_id;
            """,
            (code, title, part_number, file_id, kind, caption, channel_message_id),
        )
        await self.conn.commit()

    async def get_videos_by_code(self, code: str) -> list[dict]:
        cur = await self.conn.execute(
            """
            SELECT id, code, title, file_id, kind, caption, part_number, channel_message_id
            FROM videos WHERE code=?
            ORDER BY
                CASE WHEN part_number IS NULL THEN 1 ELSE 0 END,
                part_number ASC, id ASC
            """,
            (code,),
        )
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

    async def get_video_by_id(self, vid: int) -> dict | None:
        cur = await self.conn.execute(
            "SELECT id, code, title, file_id, kind, caption, part_number FROM videos WHERE id=?",
            (vid,),
        )
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def code_exists(self, code: str, exclude_id: int | None = None) -> bool:
        if exclude_id is not None:
            cur = await self.conn.execute(
                "SELECT 1 FROM videos WHERE code=? AND id!=? LIMIT 1", (code, exclude_id)
            )
        else:
            cur = await self.conn.execute(
                "SELECT 1 FROM videos WHERE code=? LIMIT 1", (code,)
            )
        row = await cur.fetchone()
        await cur.close()
        return row is not None

    async def update_video_code(self, vid: int, new_code: str):
        await self.conn.execute("UPDATE videos SET code=? WHERE id=?", (new_code, vid))
        await self.conn.commit()

    async def update_video_title(self, vid: int, new_title: str):
        await self.conn.execute("UPDATE videos SET title=? WHERE id=?", (new_title, vid))
        await self.conn.commit()

    async def update_video_file(self, vid: int, file_id: str, kind: str,
                                channel_message_id: int | None = None):
        await self.conn.execute(
            "UPDATE videos SET file_id=?, kind=?, channel_message_id=? WHERE id=?",
            (file_id, kind, channel_message_id, vid),
        )
        await self.conn.commit()

    # ── channels ──────────────────────────────────────────────────────────────

    async def add_channel(self, channel_id: int, invite_link: str):
        await self.conn.execute(
            "INSERT OR IGNORE INTO channels(channel_id, invite_link) VALUES(?,?)",
            (channel_id, invite_link),
        )
        await self.conn.commit()

    async def remove_channel(self, channel_id: int):
        await self.conn.execute("DELETE FROM channels WHERE channel_id=?", (channel_id,))
        await self.conn.commit()

    async def get_channels(self) -> list[dict]:
        cur = await self.conn.execute("SELECT channel_id, invite_link FROM channels")
        rows = await cur.fetchall()
        await cur.close()
        return [dict(r) for r in rows]

    # ── join requests ─────────────────────────────────────────────────────────

    async def upsert_join_request(self, user_id: int, channel_id: int):
        await self.conn.execute(
            """
            INSERT INTO join_requests(user_id, channel_id, requested_at, status)
            VALUES(?,?,datetime('now'),'requested')
            ON CONFLICT(user_id, channel_id) DO UPDATE SET
                requested_at=datetime('now'), status='requested';
            """,
            (user_id, channel_id),
        )
        await self.conn.commit()

    async def has_join_request(self, user_id: int, channel_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT 1 FROM join_requests WHERE user_id=? AND channel_id=? LIMIT 1",
            (user_id, channel_id),
        )
        row = await cur.fetchone()
        await cur.close()
        return row is not None

    async def mark_join_approved(self, user_id: int, channel_id: int):
        await self.conn.execute(
            """
            UPDATE join_requests SET approved_at=datetime('now'), status='approved'
            WHERE user_id=? AND channel_id=?;
            """,
            (user_id, channel_id),
        )
        await self.conn.commit()

    # ── rate limits ───────────────────────────────────────────────────────────

    async def get_last_used_at(self, user_id: int) -> str | None:
        cur = await self.conn.execute(
            "SELECT last_used_at FROM rate_limits WHERE user_id=?", (user_id,)
        )
        row = await cur.fetchone()
        await cur.close()
        return row[0] if row else None

    async def set_last_used_now(self, user_id: int):
        await self.conn.execute(
            """
            INSERT INTO rate_limits(user_id, last_used_at) VALUES(?,datetime('now'))
            ON CONFLICT(user_id) DO UPDATE SET last_used_at=datetime('now');
            """,
            (user_id,),
        )
        await self.conn.commit()

    # ── cooldown ──────────────────────────────────────────────────────────────

    async def get_cooldown_seconds(self) -> int:
        cur = await self.conn.execute("SELECT seconds FROM cooldown_settings WHERE id=1")
        row = await cur.fetchone()
        await cur.close()
        if not row:
            await self.conn.execute("INSERT INTO cooldown_settings(id,seconds) VALUES(1,5)")
            await self.conn.commit()
            return 5
        return row[0]

    async def set_cooldown_seconds(self, seconds: int):
        await self.conn.execute(
            """
            INSERT INTO cooldown_settings(id,seconds) VALUES(1,?)
            ON CONFLICT(id) DO UPDATE SET seconds=?;
            """,
            (seconds, seconds),
        )
        await self.conn.commit()

    # ── admins ────────────────────────────────────────────────────────────────

    async def add_admin(self, user_id: int, full_name: str = "", username: str | None = None):
        await self.conn.execute(
            """
            INSERT OR IGNORE INTO admins(user_id, full_name, username, created_at)
            VALUES(?, ?, ?, datetime('now'));
            """,
            (user_id, full_name, username),
        )
        await self.conn.execute(
            """
            INSERT OR IGNORE INTO admin_permissions(user_id, created_at)
            VALUES(?, datetime('now'));
            """,
            (user_id,),
        )
        await self.conn.commit()

    async def remove_admin(self, user_id: int):
        await self.conn.execute("DELETE FROM admins WHERE user_id=?", (user_id,))
        await self.conn.commit()

    async def is_admin(self, user_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT 1 FROM admins WHERE user_id=? LIMIT 1", (user_id,)
        )
        row = await cur.fetchone()
        await cur.close()
        return row is not None

    async def list_admins(self) -> list[dict]:
        cur = await self.conn.execute(
            """
            SELECT a.user_id, a.full_name, a.username,
                   p.can_add_channel, p.can_send_broadcast, p.can_upload,
                   p.can_reset_time, p.can_manage_admins
            FROM admins a
            LEFT JOIN admin_permissions p ON p.user_id=a.user_id
            ORDER BY a.created_at DESC
            """
        )
        rows = await cur.fetchall()
        await cur.close()
        result = []
        for r in rows:
            result.append({
                "user_id": r[0], "full_name": r[1] or "", "username": r[2] or "",
                "perms": {
                    "can_add_channel": bool(r[3]),
                    "can_send_broadcast": bool(r[4]),
                    "can_upload": bool(r[5]),
                    "can_reset_time": bool(r[6]),
                    "can_manage_admins": bool(r[7]),
                }
            })
        return result

    async def get_admin_perms(self, user_id: int) -> dict | None:
        cur = await self.conn.execute(
            """
            SELECT can_add_channel, can_send_broadcast, can_upload,
                   can_reset_time, can_manage_admins
            FROM admin_permissions WHERE user_id=?
            """,
            (user_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            return None
        return {
            "can_add_channel": bool(row[0]),
            "can_send_broadcast": bool(row[1]),
            "can_upload": bool(row[2]),
            "can_reset_time": bool(row[3]),
            "can_manage_admins": bool(row[4]),
        }

    async def set_admin_perms(self, user_id: int, **kwargs):
        allowed = {"can_add_channel", "can_send_broadcast", "can_upload",
                   "can_reset_time", "can_manage_admins"}
        fields = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return
        sets = ", ".join(f"{k}=?" for k in fields)
        vals = list(fields.values()) + [user_id]
        await self.conn.execute(
            f"UPDATE admin_permissions SET {sets} WHERE user_id=?", vals
        )
        await self.conn.commit()

    # ── superadmins ───────────────────────────────────────────────────────────

    async def add_superadmin(self, user_id: int, full_name: str = "",
                             username: str | None = None):
        await self.conn.execute(
            """
            INSERT OR IGNORE INTO superadmins(user_id, full_name, username, created_at)
            VALUES(?, ?, ?, datetime('now'));
            """,
            (user_id, full_name, username),
        )
        await self.conn.execute(
            """
            INSERT OR IGNORE INTO superadmin_permissions(user_id, created_at)
            VALUES(?, datetime('now'));
            """,
            (user_id,),
        )
        await self.conn.commit()

    async def remove_superadmin(self, user_id: int):
        await self.conn.execute("DELETE FROM superadmins WHERE user_id=?", (user_id,))
        await self.conn.commit()

    async def is_superadmin(self, user_id: int) -> bool:
        cur = await self.conn.execute(
            "SELECT 1 FROM superadmins WHERE user_id=? LIMIT 1", (user_id,)
        )
        row = await cur.fetchone()
        await cur.close()
        return row is not None

    async def list_superadmins(self) -> list[dict]:
        cur = await self.conn.execute(
            "SELECT user_id, full_name, username FROM superadmins ORDER BY created_at DESC"
        )
        rows = await cur.fetchall()
        await cur.close()
        return [{"user_id": r[0], "full_name": r[1] or "", "username": r[2] or ""}
                for r in rows]

    async def get_superadmin_perms(self, user_id: int) -> dict | None:
        cur = await self.conn.execute(
            """
            SELECT can_add_channel, can_send_broadcast, can_upload,
                   can_reset_time, can_manage_admins
            FROM superadmin_permissions WHERE user_id=?
            """,
            (user_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        if not row:
            return None
        return {
            "can_add_channel": bool(row[0]),
            "can_send_broadcast": bool(row[1]),
            "can_upload": bool(row[2]),
            "can_reset_time": bool(row[3]),
            "can_manage_admins": bool(row[4]),
        }

    # ── requests (murojaat) ───────────────────────────────────────────────────

    async def add_request(self, user_id: int, text: str | None,
                          media_type: str | None = None,
                          file_id: str | None = None) -> int:
        cur = await self.conn.execute(
            """
            INSERT INTO requests(user_id, text, media_type, file_id, status)
            VALUES(?, ?, ?, ?, 'open')
            """,
            (user_id, text, media_type, file_id),
        )
        rid = cur.lastrowid
        await self.conn.commit()
        return rid

    async def set_request_admin_msg(self, req_id: int, admin_msg_id: int):
        await self.conn.execute(
            "UPDATE requests SET admin_msg_id=? WHERE id=?", (admin_msg_id, req_id)
        )
        await self.conn.commit()

    async def set_request_user_msg(self, req_id: int, user_msg_id: int):
        await self.conn.execute(
            "UPDATE requests SET user_msg_id=? WHERE id=?", (user_msg_id, req_id)
        )
        await self.conn.commit()

    async def get_request(self, req_id: int) -> dict | None:
        cur = await self.conn.execute(
            "SELECT id, user_id, text, media_type, file_id, admin_msg_id, user_msg_id, status "
            "FROM requests WHERE id=?",
            (req_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def get_request_by_admin_msg(self, admin_msg_id: int) -> dict | None:
        cur = await self.conn.execute(
            "SELECT id, user_id, text, media_type, file_id, admin_msg_id, user_msg_id, status "
            "FROM requests WHERE admin_msg_id=?",
            (admin_msg_id,),
        )
        row = await cur.fetchone()
        await cur.close()
        return dict(row) if row else None

    async def mark_request_answered(self, req_id: int):
        await self.conn.execute(
            "UPDATE requests SET status='answered' WHERE id=?", (req_id,)
        )
        await self.conn.commit()

    # ── Qo'shimcha video metodlar (send_chanel_bot integratsiyasi) ─────────────

    async def get_all_videos_grouped(self) -> list[dict]:
        """Barcha yozuvlarni nom+kod bo'yicha guruhlaydi (mylist uchun)."""
        cur = await self.conn.execute(
            """
            SELECT title, code, COUNT(*) as parts_count
            FROM videos
            GROUP BY title, code
            ORDER BY MAX(id) DESC
            """
        )
        rows = await cur.fetchall()
        await cur.close()
        return [{"title": r[0], "code": r[1], "parts_count": r[2]} for r in rows]

    async def update_video_caption(self, vid: int, new_caption: str):
        await self.conn.execute(
            "UPDATE videos SET caption=? WHERE id=?", (new_caption, vid)
        )
        await self.conn.commit()
