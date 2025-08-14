from telethon import events
from telethon.errors import FloodWaitError
import asyncio
from typing import List

async def get_allowed_dialogs(client, min_date=None):
    """الحصول على الدردشات المسموح بالإذاعة فيها"""
    dialogs = []
    async for dialog in client.iter_dialogs():
        # استثناء الدردشات المحذوفة والخاصة
        if not dialog.is_channel and not dialog.is_group and not dialog.entity.bot:
            continue
        # استثناء الدردشات القديمة إذا تم تحديد تاريخ
        if min_date and dialog.date < min_date:
            continue
        dialogs.append(dialog)
    return dialogs

def setup(client, is_sudo, log, CREDITS):

    async def check_sudo_permission(event):
        """تحقق من صلاحيات المستخدم"""
        if not is_sudo(event.sender_id):
            await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
            return False
        return True

    @client.on(events.NewMessage(pattern=r"^\.اذاعة\s+(.+)$"))
    async def broadcast_text(event):
        """إرسال رسالة نصية لجميع الدردشات"""
        if not await check_sudo_permission(event):
            return

        text = event.pattern_match.group(1).strip()
        if len(text) > 2000:
            return await event.reply("❌ النص طويل جداً (الحد الأقصى 2000 حرف)")

        progress = await event.reply("🔄 جاري بدء الإذاعة...")
        dialogs = await get_allowed_dialogs(client)
        total = len(dialogs)
        success = 0
        failed = 0

        for i, dialog in enumerate(dialogs, 1):
            try:
                await client.send_message(
                    dialog.id,
                    f"{text}\n\n{CREDITS}",
                    link_preview=False
                )
                success += 1

                # تحديث حالة التقدم كل 10 دردشات
                if i % 10 == 0:
                    await progress.edit(
                        f"📤 جاري الإرسال...\n"
                        f"✅ {success} | ❌ {failed} | 📊 {i}/{total}"
                    )

            except FloodWaitError as e:
                await log(f"انتظر {e.seconds} ثانية بسبب FloodWait")
                await asyncio.sleep(e.seconds)
                continue
            except Exception as e:
                failed += 1
                await log(f"فشل الإرسال إلى {dialog.id}: {str(e)}")
                continue

            # تأخير بين الرسائل لتجنب الحظر
            await asyncio.sleep(0.5)

        await progress.delete()
        await event.reply(
            f"🎉 تم الانتهاء من الإذاعة!\n"
            f"✅ تم بنجاح: {success}\n"
            f"❌ فشل: {failed}\n"
            f"📊 المجموع: {total}\n"
            f"{CREDITS}"
        )

    @client.on(events.NewMessage(pattern=r"^\.برودكاست_ملف$"))
    async def broadcast_file(event):
        """إرسال ملف/وسائط لجميع الدردشات"""
        if not await check_sudo_permission(event):
            return

        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await event.reply("❌ يرجى الرد على ملف أو صورة لإرسالها")

        progress = await event.reply("🔄 جاري بدء إرسال الملف...")
        dialogs = await get_allowed_dialogs(client)
        total = len(dialogs)
        success = 0
        failed = 0

        for i, dialog in enumerate(dialogs, 1):
            try:
                await client.send_file(
                    dialog.id,
                    reply.media,
                    caption=reply.text or "",
                    link_preview=False
                )
                success += 1

                # تحديث حالة التقدم كل 5 دردشات (لأن الملفات تأخذ وقت أطول)
                if i % 5 == 0:
                    await progress.edit(
                        f"📤 جاري إرسال الملف...\n"
                        f"✅ {success} | ❌ {failed} | 📊 {i}/{total}"
                    )

            except FloodWaitError as e:
                await log(f"انتظر {e.seconds} ثانية بسبب FloodWait")
                await asyncio.sleep(e.seconds)
                continue
            except Exception as e:
                failed += 1
                await log(f"فشل إرسال الملف إلى {dialog.id}: {str(e)}")
                continue

            # تأخير أطول بين الملفات
            await asyncio.sleep(1)

        await progress.delete()
        await event.reply(
            f"🎉 تم الانتهاء من إرسال الملف!\n"
            f"✅ تم بنجاح: {success}\n"
            f"❌ فشل: {failed}\n"
            f"📊 المجموع: {total}\n"
            f"{CREDITS}"
        )
