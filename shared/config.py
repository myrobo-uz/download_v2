import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    return os.getenv(name, default)


def _env_int(name: str, default: int | None = None) -> int | None:
    v = os.getenv(name)
    if v is None:
        return default
    return int(v.strip())


def _env_int_list(name: str, default: str = "") -> list[int]:
    raw = os.getenv(name, default) or ""
    out: list[int] = []
    for it in (x.strip() for x in raw.split(",") if x.strip()):
        try:
            out.append(int(it))
        except ValueError:
            pass
    return out


@dataclass(frozen=True)
class Settings:
    user_bot_token: str
    admin_bot_token: str
    private_channel_id: int
    private_group_id: int
    root_admin_ids: list[int]
    db_path: str


def load_settings() -> Settings:
    user_bot_token = _env("USER_BOT_TOKEN")
    if not user_bot_token:
        raise RuntimeError("USER_BOT_TOKEN .env da topilmadi")

    admin_bot_token = _env("ADMIN_BOT_TOKEN")
    if not admin_bot_token:
        raise RuntimeError("ADMIN_BOT_TOKEN .env da topilmadi")

    private_channel_id = _env_int("PRIVATE_CHANNEL_ID")
    if private_channel_id is None:
        raise RuntimeError("PRIVATE_CHANNEL_ID .env da topilmadi")

    private_group_id = _env_int("PRIVATE_GROUP_ID", 0) or 0

    root_admin_ids = _env_int_list("ROOT_ADMIN_IDS")
    if not root_admin_ids:
        raise RuntimeError("ROOT_ADMIN_IDS .env da topilmadi")

    db_path = _env("DB_PATH", "data/bot.sqlite3") or "data/bot.sqlite3"

    return Settings(
        user_bot_token=user_bot_token,
        admin_bot_token=admin_bot_token,
        private_channel_id=int(private_channel_id),
        private_group_id=int(private_group_id),
        root_admin_ids=root_admin_ids,
        db_path=db_path,
    )
