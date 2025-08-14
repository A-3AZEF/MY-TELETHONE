from telethon import events

def setup(client, is_sudo, log, CREDITS):
    @client.on(events.NewMessage(pattern=r"^\.اذاعة (.+)$"))
    async def broadcast_text(event):
        if not is_sudo(event.sender_id): return
        text = event.pattern_match.group(1)
        ok = 0; bad = 0
        async for dialog in client.iter_dialogs():
            try:
                await client.send_message(dialog.id, text + f"\n\n{CREDITS}")
                ok += 1
            except:
                bad += 1
        await event.reply(f"تم الإرسال ✅ {ok} / فاشل {bad}")

    @client.on(events.NewMessage(pattern=r"^\.برودكاست_ملف$"))
    async def broadcast_file(event):
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r or not r.media:
            return await event.reply("رد على ملف/صورة تبعتها للكل.")
        ok = 0; bad = 0
        async for dialog in client.iter_dialogs():
            try:
                await client.send_file(dialog.id, r.media, caption=r.message or "")
                ok += 1
            except:
                bad += 1
        await event.reply(f"تم الإرسال ✅ {ok} / فاشل {bad}")
