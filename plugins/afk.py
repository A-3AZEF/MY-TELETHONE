from telethon import events
import time
from typing import Dict, Any

# حالة AFK كمتغير عام مع نوع محدد
AFK: Dict[str, Any] = {
    "status": False,
    "reason": "",
    "since": 0.0,
    "last_reply": {}  # لتتبع آخر وقت رد في كل دردشة
}

def setup(client, is_sudo, log, CREDITS):

    async def check_sudo_permission(event):
        """تحقق من صلاحيات المستخدم"""
        if not is_sudo(event.sender_id):
            await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
            return False
        return True

    @client.on(events.NewMessage(pattern=r"^\.afk(?:\s+(.*))?$"))
    async def set_afk(event):
        """تفعيل وضع AFK مع سبب اختياري"""
        if not await check_sudo_permission(event):
            return

        reason = (event.pattern_match.group(1) or "").strip()
        AFK.update({
            "status": True,
            "reason": reason,
            "since": time.time(),
            "last_reply": {}
        })

        await log(f"تم تفعيل AFK. السبب: {reason or 'غير محدد'}")
        await event.reply(f"🚶‍♂️ **تم تفعيل وضع AFK**\n"
                        f"⌛ **السبب:** {reason or 'غير محدد'}\n"
                        f"{CREDITS}")

    @client.on(events.NewMessage(incoming=True))
    async def afk_auto_back(event):
        """إلغاء AFK تلقائيًا عند إرسال رسالة"""
        if not AFK["status"]:
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            duration = time.time() - AFK["since"]
            mins = int(duration // 60)

            AFK.update({
                "status": False,
                "reason": "",
                "since": 0.0,
                "last_reply": {}
            })

            await log(f"تم إلغاء AFK بعد {mins} دقيقة")
            await event.reply(f"👋 **عدت من AFK بعد {mins} دقيقة**\n"
                            f"{CREDITS}")

    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        """الرد التلقائي على الرسائل الواردة أثناء AFK"""
        if not AFK["status"] or event.out:
            return

        me = await client.get_me()
        if event.sender_id == me.id:
            return

        # تجاهل الرسائل في المجموعات إذا لم يتم ذكر البوت
        if event.is_group and not event.mentioned:
            return

        # حساب مدة AFK
        duration = time.time() - AFK["since"]
        mins = int(duration // 60)

        # تحقق من وقت آخر رد في هذه الدردشة
        chat_id = event.chat_id
        last_reply_time = AFK["last_reply"].get(chat_id, 0)

        if time.time() - last_reply_time > 60:  # رد كل 60 ثانية كحد أدنى
            reply_text = (
                f"⏳ **أنا غير متاح حاليًا (AFK)**\n"
                f"🕒 **منذ:** {mins} دقيقة\n"
                f"📝 **السبب:** {AFK['reason'] or 'غير محدد'}\n"
                f"{CREDITS}"
            )

            try:
                await event.reply(reply_text)
                AFK["last_reply"][chat_id] = time.time()
            except Exception as e:
                await log(f"فشل في إرسال رد AFK: {str(e)}")
