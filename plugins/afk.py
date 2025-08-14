from telethon import events
import time

AFK = {"status": False, "reason": "", "since": 0}

def setup(client, is_sudo, log, CREDITS):
    @client.on(events.NewMessage(pattern=r"^\.afk(?:\s+(.*))?$"))
    async def set_afk(event):
        if not is_sudo(event.sender_id): return
        reason = (event.pattern_match.group(1) or "").strip()
        AFK.update(status=True, reason=reason, since=time.time())
        await event.reply(f"AFK مفعل. السبب: {reason or '—'}\n{CREDITS}")

    @client.on(events.NewMessage(incoming=True))
    async def afk_auto_back(event):
        if AFK["status"] and event.sender_id == (await client.get_me()).id:
            AFK.update(status=False, reason="", since=0)
            await log("رجعت من AFK ✅")

    @client.on(events.NewMessage(incoming=True))
    async def afk_reply(event):
        if AFK["status"] and not event.out:
            mins = int((time.time() - AFK["since"]) // 60)
            txt = f"انا AFK بقالى {mins} دقيقة.\nالسبب: {AFK['reason'] or '—'}\n{CREDITS}"
            # رد تلقائي مرة كل 60 ثانية في نفس الشات
            key = f"afk:{event.chat_id}"
            last = getattr(client, key, 0)
            if time.time() - last > 60:
                await event.reply(txt)
                setattr(client, key, time.time())
