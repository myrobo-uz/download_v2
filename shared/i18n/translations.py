"""
3 tilli tarjima tizimi: uz | ru | en
"""

TEXTS: dict[str, dict[str, str]] = {

    # ─── UMUMIY ───────────────────────────────────────────────────────────────
    "choose_language": {
        "uz": "🌐 Tilni tanlang:",
        "ru": "🌐 Выберите язык:",
        "en": "🌐 Choose language:",
    },
    "language_set": {
        "uz": "✅ Til o'rnatildi: O'zbek",
        "ru": "✅ Язык установлен: Русский",
        "en": "✅ Language set: English",
    },
    "cancel_done": {
        "uz": "✅ Bekor qilindi.",
        "ru": "✅ Отменено.",
        "en": "✅ Cancelled.",
    },
    "no_permission": {
        "uz": "❌ Sizda ruxsat yo'q.",
        "ru": "❌ У вас нет разрешения.",
        "en": "❌ You don't have permission.",
    },
    "not_admin": {
        "uz": "❌ Siz admin emassiz.",
        "ru": "❌ Вы не являетесь администратором.",
        "en": "❌ You are not an admin.",
    },
    "only_root": {
        "uz": "❌ Faqat Bosh admin.",
        "ru": "❌ Только главный администратор.",
        "en": "❌ Only the root admin.",
    },

    # ─── START / OBUNA ────────────────────────────────────────────────────────
    "welcome_subscribed": {
        "uz": "✅ Ruxsat berildi. Endi kod yuboring.",
        "ru": "✅ Доступ разрешён. Отправьте код.",
        "en": "✅ Access granted. Send a code.",
    },
    "subscribe_prompt": {
        "uz": "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling.",
        "ru": "Для использования бота подпишитесь на каналы ниже.",
        "en": "To use the bot, subscribe to the channels below.",
    },
    "subscribe_btn": {
        "uz": "📢 Kanalga obuna bo'lish",
        "ru": "📢 Подписаться на канал",
        "en": "📢 Subscribe to channel",
    },
    "check_sub_btn": {
        "uz": "✅ Tekshirish",
        "ru": "✅ Проверить",
        "en": "✅ Check",
    },
    "not_subscribed": {
        "uz": "❌ Hali obuna bo'lmagansiz.",
        "ru": "❌ Вы ещё не подписались.",
        "en": "❌ You haven't subscribed yet.",
    },

    # ─── KOD / VIDEO ─────────────────────────────────────────────────────────
    "send_code_hint": {
        "uz": "Faqat raqam/kod yuboring (masalan: 101).",
        "ru": "Отправьте только код/номер (например: 101).",
        "en": "Send only a code/number (e.g. 101).",
    },
    "code_not_found": {
        "uz": "❌ Bu kod bo'yicha ma'lumot topilmadi.",
        "ru": "❌ По этому коду ничего не найдено.",
        "en": "❌ Nothing found for this code.",
    },
    "send_error": {
        "uz": "⚠️ Yuborishda xatolik yuz berdi.",
        "ru": "⚠️ Ошибка при отправке.",
        "en": "⚠️ Error while sending.",
    },
    "cooldown_msg": {
        "uz": "⏳ Limit: {seconds} soniyada 1 ta.\nYana {left} soniyadan keyin urinib ko'ring.",
        "ru": "⏳ Лимит: 1 раз в {seconds} секунд.\nПовторите через {left} сек.",
        "en": "⏳ Limit: once per {seconds} seconds.\nTry again in {left} sec.",
    },
    "part_label": {
        "uz": "Qism: {n}",
        "ru": "Часть: {n}",
        "en": "Part: {n}",
    },
    "order_label": {
        "uz": "Qism: {n}",
        "ru": "Цизм: {n}",
        "en": "Part: {n}",
    },

    # ─── UPLOAD ───────────────────────────────────────────────────────────────
    "upload_enter_code": {
        "uz": "📌 Kodni yuboring (faqat raqam). Masalan: 101\n/cancel — bekor qilish",
        "ru": "📌 Отправьте код (только цифры). Например: 101\n/cancel — отмена",
        "en": "📌 Send the code (numbers only). E.g. 101\n/cancel — cancel",
    },
    "upload_bad_code": {
        "uz": "❌ Kod noto'g'ri. Faqat raqam yuboring.",
        "ru": "❌ Неверный код. Только цифры.",
        "en": "❌ Invalid code. Numbers only.",
    },
    "upload_send_title": {
        "uz": "📝 Endi sarlavha (title) yuboring:",
        "ru": "📝 Теперь отправьте заголовок (title):",
        "en": "📝 Now send the title:",
    },
    "upload_send_file": {
        "uz": "📁 Endi faylni yuboring (video/rasm/audio/hujjat/ovoz).",
        "ru": "📁 Теперь отправьте файл (видео/фото/аудио/документ/голос).",
        "en": "📁 Now send the file (video/photo/audio/document/voice).",
    },
    "upload_saved": {
        "uz": "✅ Saqlandi! Kod: {code}",
        "ru": "✅ Сохранено! Код: {code}",
        "en": "✅ Saved! Code: {code}",
    },
    "upload_no_code": {
        "uz": "⚠️ Xatolik: kod topilmadi. /upload ni qayta bosing.",
        "ru": "⚠️ Ошибка: код не найден. Повторите /upload.",
        "en": "⚠️ Error: code not found. Repeat /upload.",
    },
    "upload_send_media": {
        "uz": "❌ Iltimos, fayl yuboring (video/rasm/audio/hujjat).",
        "ru": "❌ Пожалуйста, отправьте файл (видео/фото/аудио/документ).",
        "en": "❌ Please send a file (video/photo/audio/document).",
    },

    # ─── EDIT ─────────────────────────────────────────────────────────────────
    "edit_enter_code": {
        "uz": "✏️ Tahrirlash uchun kodni yuboring:",
        "ru": "✏️ Отправьте код для редактирования:",
        "en": "✏️ Send the code to edit:",
    },
    "edit_not_found": {
        "uz": "❌ Bu kod bilan yozuv topilmadi.",
        "ru": "❌ Запись с таким кодом не найдена.",
        "en": "❌ Record with this code not found.",
    },
    "edit_choose_field": {
        "uz": "Nimani tahrirlaysiz?\nKod: {code} | Sarlavha: {title}",
        "ru": "Что редактируем?\nКод: {code} | Заголовок: {title}",
        "en": "What to edit?\nCode: {code} | Title: {title}",
    },
    "edit_btn_code": {
        "uz": "🔢 Kodni o'zgartirish",
        "ru": "🔢 Изменить код",
        "en": "🔢 Change code",
    },
    "edit_btn_title": {
        "uz": "📝 Sarlavhani o'zgartirish",
        "ru": "📝 Изменить заголовок",
        "en": "📝 Change title",
    },
    "edit_btn_file": {
        "uz": "📁 Faylni almashtirish",
        "ru": "📁 Заменить файл",
        "en": "📁 Replace file",
    },
    "edit_btn_cancel": {
        "uz": "❌ Bekor",
        "ru": "❌ Отмена",
        "en": "❌ Cancel",
    },
    "edit_enter_new_code": {
        "uz": "Yangi kodni yuboring (faqat raqam):",
        "ru": "Отправьте новый код (только цифры):",
        "en": "Send new code (numbers only):",
    },
    "edit_enter_new_title": {
        "uz": "Yangi sarlavhani yuboring:",
        "ru": "Отправьте новый заголовок:",
        "en": "Send new title:",
    },
    "edit_enter_new_file": {
        "uz": "Yangi faylni yuboring:",
        "ru": "Отправьте новый файл:",
        "en": "Send new file:",
    },
    "edit_done": {
        "uz": "✅ Muvaffaqiyatli yangilandi.",
        "ru": "✅ Успешно обновлено.",
        "en": "✅ Successfully updated.",
    },
    "edit_code_taken": {
        "uz": "❌ Bu kod allaqachon mavjud.",
        "ru": "❌ Такой код уже существует.",
        "en": "❌ This code already exists.",
    },

    # ─── CONTACT (murojaat) ───────────────────────────────────────────────────
    "contact_prompt": {
        "uz": "📝 Murojaatingizni yuboring (matn, rasm, video, audio ─ istalgan):",
        "ru": "📝 Отправьте обращение (текст, фото, видео, аудио ─ любое):",
        "en": "📝 Send your message (text, photo, video, audio ─ anything):",
    },
    "contact_sent": {
        "uz": "✅ Murojaatingiz yuborildi. Tez orada javob beramiz.",
        "ru": "✅ Обращение отправлено. Скоро ответим.",
        "en": "✅ Your request has been sent. We'll reply soon.",
    },
    "admin_reply_sent": {
        "uz": "✅ Javob yuborildi.",
        "ru": "✅ Ответ отправлен.",
        "en": "✅ Reply sent.",
    },
    "admin_reply_prefix": {
        "uz": "👨‍💼 Admin javobi:",
        "ru": "👨‍💼 Ответ администратора:",
        "en": "👨‍💼 Admin reply:",
    },
    "admin_notify_header": {
        "uz": "📩 MUROJAAT #{id}\n\n👤 {name}\n🆔 {uid}\n",
        "ru": "📩 ОБРАЩЕНИЕ #{id}\n\n👤 {name}\n🆔 {uid}\n",
        "en": "📩 REQUEST #{id}\n\n👤 {name}\n🆔 {uid}\n",
    },
    "admin_reply_edited": {
        "uz": "✏️ Admin javobini tahrirladi.",
        "ru": "✏️ Администратор отредактировал ответ.",
        "en": "✏️ Admin edited the reply.",
    },

    # ─── PANEL ────────────────────────────────────────────────────────────────
    "panel_root_title": {
        "uz": "👑 Bosh admin panel",
        "ru": "👑 Главная панель администратора",
        "en": "👑 Root admin panel",
    },
    "panel_admin_title": {
        "uz": "🛡 Admin panel",
        "ru": "🛡 Панель администратора",
        "en": "🛡 Admin panel",
    },
    "panel_btn_send": {
        "uz": "📢 Xabar yuborish",
        "ru": "📢 Рассылка",
        "en": "📢 Broadcast",
    },
    "panel_btn_time": {
        "uz": "⏱ Vaqt sozlash",
        "ru": "⏱ Настройка времени",
        "en": "⏱ Time settings",
    },
    "panel_btn_channels": {
        "uz": "📺 Kanallar",
        "ru": "📺 Каналы",
        "en": "📺 Channels",
    },
    "panel_btn_upload": {
        "uz": "📤 Yuklash",
        "ru": "📤 Загрузка",
        "en": "📤 Upload",
    },
    "panel_btn_edit": {
        "uz": "✏️ Tahrirlash",
        "ru": "✏️ Редактировать",
        "en": "✏️ Edit",
    },
    "panel_btn_admins": {
        "uz": "👥 Adminlar",
        "ru": "👥 Администраторы",
        "en": "👥 Admins",
    },
    "panel_btn_supers": {
        "uz": "⭐ SuperAdminlar",
        "ru": "⭐ SuperАдмины",
        "en": "⭐ SuperAdmins",
    },
    "panel_no_perm": {
        "uz": "🔒 Ruxsat yo'q",
        "ru": "🔒 Нет доступа",
        "en": "🔒 No access",
    },
    "panel_back": {
        "uz": "⬅️ Orqaga",
        "ru": "⬅️ Назад",
        "en": "⬅️ Back",
    },

    # ─── CHANNELS ─────────────────────────────────────────────────────────────
    "channels_panel": {
        "uz": "📺 Kanallar paneli:",
        "ru": "📺 Панель каналов:",
        "en": "📺 Channels panel:",
    },
    "channels_list_btn": {
        "uz": "📋 Ro'yxat",
        "ru": "📋 Список",
        "en": "📋 List",
    },
    "channels_add_btn": {
        "uz": "➕ Kanal qo'shish",
        "ru": "➕ Добавить канал",
        "en": "➕ Add channel",
    },
    "channels_remove_btn": {
        "uz": "🗑 Kanal o'chirish",
        "ru": "🗑 Удалить канал",
        "en": "🗑 Remove channel",
    },
    "channels_empty": {
        "uz": "Hozircha kanal yo'q.",
        "ru": "Каналов пока нет.",
        "en": "No channels yet.",
    },
    "channels_list_header": {
        "uz": "📋 Kanallar:",
        "ru": "📋 Каналы:",
        "en": "📋 Channels:",
    },
    "channels_add_prompt": {
        "uz": "➕ Format:\n<code>-1001234567890 https://t.me/link</code>\n\n/cancel — bekor",
        "ru": "➕ Формат:\n<code>-1001234567890 https://t.me/link</code>\n\n/cancel — отмена",
        "en": "➕ Format:\n<code>-1001234567890 https://t.me/link</code>\n\n/cancel — cancel",
    },
    "channels_add_bad_format": {
        "uz": "❌ Format noto'g'ri. Masalan:\n-1001234567890 https://t.me/link",
        "ru": "❌ Неверный формат. Например:\n-1001234567890 https://t.me/link",
        "en": "❌ Wrong format. E.g.:\n-1001234567890 https://t.me/link",
    },
    "channels_added": {
        "uz": "✅ Kanal qo'shildi.",
        "ru": "✅ Канал добавлен.",
        "en": "✅ Channel added.",
    },
    "channels_remove_prompt": {
        "uz": "🗑 Kanal ID yuboring:\n<code>-1001234567890</code>\n\n/cancel — bekor",
        "ru": "🗑 Отправьте ID канала:\n<code>-1001234567890</code>\n\n/cancel — отмена",
        "en": "🗑 Send channel ID:\n<code>-1001234567890</code>\n\n/cancel — cancel",
    },
    "channels_removed": {
        "uz": "✅ Kanal o'chirildi.",
        "ru": "✅ Канал удалён.",
        "en": "✅ Channel removed.",
    },
    "channels_bad_id": {
        "uz": "❌ ID noto'g'ri.",
        "ru": "❌ Неверный ID.",
        "en": "❌ Invalid ID.",
    },

    # ─── BROADCAST ────────────────────────────────────────────────────────────
    "broadcast_who": {
        "uz": "Kimlarga yuboramiz?",
        "ru": "Кому отправляем?",
        "en": "Who to send to?",
    },
    "broadcast_subscribed": {
        "uz": "✅ Obuna bo'lganlar",
        "ru": "✅ Подписчики",
        "en": "✅ Subscribers",
    },
    "broadcast_unsubscribed": {
        "uz": "❌ Obuna bo'lmaganlar",
        "ru": "❌ Не подписчики",
        "en": "❌ Non-subscribers",
    },
    "broadcast_all": {
        "uz": "👥 Hammasi",
        "ru": "👥 Все",
        "en": "👥 All",
    },
    "broadcast_send_content": {
        "uz": "📨 Yubormoqchi bo'lgan xabaringizni yuboring:",
        "ru": "📨 Отправьте сообщение для рассылки:",
        "en": "📨 Send the message to broadcast:",
    },
    "broadcast_done": {
        "uz": "✅ Yuborildi: {sent}\n❌ Xatolik: {failed}",
        "ru": "✅ Отправлено: {sent}\n❌ Ошибка: {failed}",
        "en": "✅ Sent: {sent}\n❌ Failed: {failed}",
    },

    # ─── COOLDOWN ─────────────────────────────────────────────────────────────
    "cooldown_prompt": {
        "uz": "Necha soniya qilib qo'yamiz? (faqat son)",
        "ru": "Сколько секунд? (только цифры)",
        "en": "How many seconds? (numbers only)",
    },
    "cooldown_invalid": {
        "uz": "❌ Faqat musbat son yuboring.",
        "ru": "❌ Отправьте только положительное число.",
        "en": "❌ Send a positive number only.",
    },
    "cooldown_set": {
        "uz": "✅ Endi {seconds} soniyada 1 marta ishlaydi.",
        "ru": "✅ Теперь 1 раз в {seconds} секунд.",
        "en": "✅ Now 1 time per {seconds} seconds.",
    },

    # ─── ADMIN MANAGE ─────────────────────────────────────────────────────────
    "admins_panel": {
        "uz": "👥 Adminlar boshqaruvi:",
        "ru": "👥 Управление администраторами:",
        "en": "👥 Admin management:",
    },
    "admins_list_btn": {
        "uz": "📋 Ro'yxat",
        "ru": "📋 Список",
        "en": "📋 List",
    },
    "admins_add_btn": {
        "uz": "➕ Admin qo'shish",
        "ru": "➕ Добавить",
        "en": "➕ Add",
    },
    "admins_del_btn": {
        "uz": "🗑 Admin o'chirish",
        "ru": "🗑 Удалить",
        "en": "🗑 Remove",
    },
    "admins_empty": {
        "uz": "Admin yo'q.",
        "ru": "Администраторов нет.",
        "en": "No admins.",
    },
    "admins_list_header": {
        "uz": "👥 Adminlar:",
        "ru": "👥 Администраторы:",
        "en": "👥 Admins:",
    },
    "admins_add_prompt": {
        "uz": "➕ TG ID yuboring (faqat raqam):\n/cancel — bekor",
        "ru": "➕ Отправьте TG ID (только цифры):\n/cancel — отмена",
        "en": "➕ Send TG ID (numbers only):\n/cancel — cancel",
    },
    "admins_del_prompt": {
        "uz": "🗑 O'chiriladigan admin TG ID:\n/cancel — bekor",
        "ru": "🗑 TG ID удаляемого admin:\n/cancel — отмена",
        "en": "🗑 Admin TG ID to remove:\n/cancel — cancel",
    },
    "admins_added": {
        "uz": "✅ Admin qo'shildi: <code>{uid}</code>",
        "ru": "✅ Администратор добавлен: <code>{uid}</code>",
        "en": "✅ Admin added: <code>{uid}</code>",
    },
    "admins_removed": {
        "uz": "✅ Admin o'chirildi: <code>{uid}</code>",
        "ru": "✅ Администратор удалён: <code>{uid}</code>",
        "en": "✅ Admin removed: <code>{uid}</code>",
    },
    "id_invalid": {
        "uz": "❌ Faqat raqam yuboring (TG ID).",
        "ru": "❌ Отправьте только цифры (TG ID).",
        "en": "❌ Send numbers only (TG ID).",
    },

    # ─── SUPER MANAGE ─────────────────────────────────────────────────────────
    "supers_panel": {
        "uz": "⭐ SuperAdmin boshqaruvi:",
        "ru": "⭐ Управление SuperAdmin:",
        "en": "⭐ SuperAdmin management:",
    },
    "supers_empty": {
        "uz": "SuperAdmin yo'q.",
        "ru": "SuperAdminов нет.",
        "en": "No SuperAdmins.",
    },
    "supers_list_header": {
        "uz": "⭐ SuperAdminlar:",
        "ru": "⭐ SuperАдмины:",
        "en": "⭐ SuperAdmins:",
    },
    "supers_add_prompt": {
        "uz": "➕ SuperAdmin TG ID:\n/cancel — bekor",
        "ru": "➕ TG ID для SuperAdmin:\n/cancel — отмена",
        "en": "➕ SuperAdmin TG ID:\n/cancel — cancel",
    },
    "supers_del_prompt": {
        "uz": "🗑 O'chiriladigan SuperAdmin TG ID:\n/cancel — bekor",
        "ru": "🗑 TG ID удаляемого SuperAdmin:\n/cancel — отмена",
        "en": "🗑 SuperAdmin TG ID to remove:\n/cancel — cancel",
    },
    "supers_added": {
        "uz": "✅ SuperAdmin qo'shildi: <code>{uid}</code>",
        "ru": "✅ SuperAdmin добавлен: <code>{uid}</code>",
        "en": "✅ SuperAdmin added: <code>{uid}</code>",
    },
    "supers_removed": {
        "uz": "✅ SuperAdmin o'chirildi: <code>{uid}</code>",
        "ru": "✅ SuperAdmin удалён: <code>{uid}</code>",
        "en": "✅ SuperAdmin removed: <code>{uid}</code>",
    },
}


def t(key: str, lang: str, **kwargs) -> str:
    """Tarjimani qaytaradi. Agar topilmasa — o'zbekchasi."""
    entry = TEXTS.get(key)
    if not entry:
        return f"[{key}]"
    text = entry.get(lang) or entry.get("uz") or f"[{key}]"
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass
    return text

# ─── Qo'shimcha kalitlar (send_chanel_bot integratsiyasi) ──────────────────────
TEXTS.update({
    "upload_send_caption": {
        "uz": "💬 Caption (tavsif) yuboring yoki — bo'sh qoldirish uchun nuqta (.) yuboring:",
        "ru": "💬 Отправьте caption или точку (.) чтобы пропустить:",
        "en": "💬 Send caption or a dot (.) to skip:",
    },
    "upload_more": {
        "uz": "✅ Saqlandi! Kod: {code} | Nom: {title}\n\nYana media yuborishingiz mumkin yoki ❌ Bekor qilish.",
        "ru": "✅ Сохранено! Код: {code} | Название: {title}\n\nМожно отправить ещё медиа или ❌ Отмена.",
        "en": "✅ Saved! Code: {code} | Title: {title}\n\nYou can send more media or ❌ Cancel.",
    },
    "mylist_empty": {
        "uz": "📭 Hozircha hech qanday yozuv yo'q.",
        "ru": "📭 Записей пока нет.",
        "en": "📭 No records yet.",
    },
    "mylist_header": {
        "uz": "📋 Jami yozuvlar: {total}",
        "ru": "📋 Всего записей: {total}",
        "en": "📋 Total records: {total}",
    },
    "mylist_parts": {
        "uz": "qism",
        "ru": "ч.",
        "en": "pt",
    },
    "edit_btn_caption": {
        "uz": "💬 Caption o'zgartirish",
        "ru": "💬 Изменить caption",
        "en": "💬 Change caption",
    },
    "edit_enter_new_caption": {
        "uz": "Yangi caption yuboring:",
        "ru": "Отправьте новый caption:",
        "en": "Send new caption:",
    },
    "panel_btn_list": {
        "uz": "📋 Ro'yxat",
        "ru": "📋 Список",
        "en": "📋 List",
    },
})
