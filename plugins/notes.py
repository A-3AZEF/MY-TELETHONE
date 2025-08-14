from telethon import events
from typing import Dict
import re

# استخدام هياكل بيانات أكثر أماناً مع تحديد الأنواع
NOTES: Dict[str, str] = {}
FILTERS: Dict[str, str] = {}

def setup(client, is_sudo, log, CREDITS):

    async def check_sudo_permission(event):
        """تحقق من صلاحيات المستخدم"""
        if not is_sudo(event.sender_id):
            await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
            return False
        return True

    @client.on(events.NewMessage(pattern=r"^\.note (\S+)\s+([\s\S]+)$"))
    async def add_note(event):
        """إضافة ملاحظة جديدة"""
        if not await check_sudo_permission(event):
            return

        name = event.pattern_match.group(1).strip()
        text = event.pattern_match.group(2).strip()

        if len(name) > 30:
            return await event.reply("❌ اسم الملاحظة طويل جداً (الحد الأقصى 30 حرفاً)")

        NOTES[name] = text
        await log(f"تم إضافة ملاحظة: {name}")
        await event.reply(f"📝 **تم حفظ الملاحظة:** `{name}`\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.get (\S+)$"))
    async def get_note(event):
        """استرجاع ملاحظة محفوظة"""
        name = event.pattern_match.group(1).strip()
        if name not in NOTES:
            return await event.reply(f"❌ الملاحظة `{name}` غير موجودة")

        await event.reply(f"📌 **{name}:**\n{NOTES[name]}\n\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.notes$"))
    async def list_notes(event):
        """عرض قائمة بالملاحظات المحفوظة"""
        if not NOTES:
            return await event.reply("📭 لا توجد ملاحظات محفوظة")

        notes_list = "\n".join(f"• `{name}`" for name in sorted(NOTES.keys()))
        await event.reply(f"📋 **الملاحظات المحفوظة:**\n{notes_list}\n\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.rmnote (\S+)$"))
    async def rm_note(event):
        """حذف ملاحظة محفوظة"""
        if not await check_sudo_permission(event):
            return

        name = event.pattern_match.group(1).strip()
        if name not in NOTES:
            return await event.reply(f"❌ الملاحظة `{name}` غير موجودة")

        del NOTES[name]
        await log(f"تم حذف ملاحظة: {name}")
        await event.reply(f"🗑️ **تم حذف الملاحظة:** `{name}`\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.filter (.+?)\s*=\s*([\s\S]+)$"))
    async def add_filter(event):
        """إضافة فلتر جديد"""
        if not await check_sudo_permission(event):
            return

        key = event.pattern_match.group(1).strip().lower()
        value = event.pattern_match.group(2).strip()

        if len(key) > 50:
            return await event.reply("❌ الكلمة المفتاحية طويلة جداً (الحد الأقصى 50 حرفاً)")

        FILTERS[key] = value
        await log(f"تم إضافة فلتر: {key}")
        await event.reply(f"🔎 **تم إضافة فلتر:** `{key}`\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.filters$"))
    async def list_filters(event):
        """عرض قائمة الفلاتر"""
        if not FILTERS:
            return await event.reply("📭 لا توجد فلاتر مضيفة")

        filters_list = "\n".join(f"• `{key}`" for key in sorted(FILTERS.keys()))
        await event.reply(f"🔍 **الفلاتر المضيفة:**\n{filters_list}\n\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.rmfilter (.+)$"))
    async def rm_filter(event):
        """حذف فلتر"""
        if not await check_sudo_permission(event):
            return

        key = event.pattern_match.group(1).strip().lower()
        if key not in FILTERS:
            return await event.reply(f"❌ الفلتر `{key}` غير موجود")

        del FILTERS[key]
        await log(f"تم حذف فلتر: {key}")
        await event.reply(f"🗑️ **تم حذف الفلتر:** `{key}`\n{CREDITS}")

    @client.on(events.NewMessage(incoming=True))
    async def filter_watch(event):
        """مراقبة الفلاتر تلقائياً"""
        if not FILTERS or event.out or not event.text:
            return

        text = event.text.lower()
        for key, value in FILTERS.items():
            if re.search(r'\b{}\b'.format(re.escape(key)), text, re.IGNORECASE):
                try:
                    await event.reply(f"{value}\n\n{CREDITS}")
                    break  # لا داعي للتحقق من باقي الفلاتر بعد الرد
                except Exception as e:
                    await log(f"فشل في إرسال رد الفلتر: {str(e)}")
                    break
