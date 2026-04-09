# 2 Bot — 1 DB

| Bot | Token | Kimlar uchun |
|-----|-------|-------------|
| **user_bot** | `USER_BOT_TOKEN` | Foydalanuvchilar — kod yuborsa fayl keladi |
| **admin_bot** | `ADMIN_BOT_TOKEN` | Faqat adminlar — fayl yuklash, tahrirlash, boshqaruv |

Ikkala bot **bitta SQLite DB** (`data/bot.sqlite3`) dan ulashadi.

---

## O'rnatish

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# .env ni to'ldiring
```

## Ishga tushirish

```bash
# Ikkala botni bir vaqtda:
python run_all.py

# Yoki alohida (2 ta terminal):
python user_bot/main.py
python admin_bot/main.py
```

---

## .env sozlamalari

| Kalit | Izoh |
|-------|------|
| `USER_BOT_TOKEN` | Foydalanuvchilar boti tokeni |
| `ADMIN_BOT_TOKEN` | Adminlar boti tokeni |
| `PRIVATE_CHANNEL_ID` | Fayllar saqlanadigan kanal `-100...` |
| `PRIVATE_GROUP_ID` | Murojaatlar tushadigan guruh |
| `ROOT_ADMIN_IDS` | Bosh adminlar TG ID (vergul bilan) |
| `DB_PATH` | SQLite fayl joyi (default: `data/bot.sqlite3`) |

---

## USER BOT buyruqlari

| Buyruq | Izoh |
|--------|------|
| `/start` yoki `/change_language` | Til tanlash (uz/ru/en) |
| `/boglanish` | Admin bilan bog'lanish |
| Raqam yuborish | Shu kodga tegishli fayl keladi |

## ADMIN BOT buyruqlari

| Buyruq | Izoh |
|--------|------|
| `/start` | Xush kelibsiz (faqat adminlar) |
| `/panel` | Inline boshqaruv paneli |
| `/upload` | Fayl yuklash: nom → kod → caption → media |
| `/mylist` | Barcha yozuvlar ro'yxati |
| `/edit` | Yozuvni tahrirlash (kod/nom/caption/fayl) |
| `/send` | Broadcast |
| `/resettime` | Cooldown vaqtini o'zgartirish |
| `/add_admin <id>` | Admin qo'shish (faqat ROOT) |
| `/remove_admin <id>` | Admin o'chirish (faqat ROOT) |
| `/set_perm <id> <perm> <0\|1>` | Ruxsat berish |
| `/admins` | Adminlar ro'yxati |

---

## Loyiha tuzilishi

```
bot_v2/
├── run_all.py          ← Ikkala botni birga ishga tushirish
├── requirements.txt
├── .env.example
├── shared/             ← Ikkala bot ulashadigan kod
│   ├── config.py
│   ├── db/sqlite.py
│   ├── i18n/translations.py
│   └── utils/
├── user_bot/
│   ├── main.py
│   └── handlers/
│       ├── language.py
│       ├── user.py
│       ├── contact.py
│       └── join_request.py
└── admin_bot/
    ├── main.py
    └── handlers/
        ├── admin.py
        ├── panel.py
        ├── admin_manage.py
        └── channel.py
```
