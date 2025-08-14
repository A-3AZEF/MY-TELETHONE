from telethon import events
from telethon.tl.functions.messages import EditMessageRequest

def setup(client, is_sudo, log, CREDITS):

    @client.on(events.NewMessage(pattern=r"^\.انضم (.+)$"))
    async def join_chat(event):
        if not is_sudo(event.sender_id): return
        link = event.pattern_match.group(1).strip()
        try:
            await client.join_chat(link)
            await event.reply(f"انضممت ✅\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.غادر$"))
    async def leave_chat(event):
        if not is_sudo(event.sender_id): return
        try:
            await client.delete_dialog(event.chat_id)
        except: pass

    @client.on(events.NewMessage(pattern=r"^\.انتحال (.+)$"))
    async def impersonate(event):
        # يغيّر الاسم المعروض
        if not is_sudo(event.sender_id): return
        name = event.pattern_match.group(1).strip()
        try:
            await client(functions.account.UpdateProfileRequest(first_name=name))
            await event.reply(f"الاسم اتغير.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.قول (.+)$"))
    async def say(event):
        txt = event.pattern_match.group(1)
        await event.reply(txt + f"\n\n{CREDITS}")
