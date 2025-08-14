from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights

def setup(client, is_sudo, log, CREDITS):
    mute_rights = ChatBannedRights(send_messages=True)
    unmute_rights = ChatBannedRights()

    @client.on(events.NewMessage(pattern=r"^\.طرد$"))
    async def kick_user(event):
        if not event.is_group: return
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r: return await event.reply("⚠️ لازم ترد على الشخص.")
        try:
            await event.client.kick_participant(event.chat_id, r.sender_id)
            await event.reply(f"تم طرده.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.حظر$"))
    async def ban_user(event):
        if not event.is_group: return
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r: return await event.reply("⚠️ لازم ترد على الشخص.")
        try:
            rights = ChatBannedRights(view_messages=True)
            await event.client(EditBannedRequest(event.chat_id, r.sender_id, rights))
            await event.reply(f"تم حظره.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.سكات$"))
    async def mute_user(event):
        if not event.is_group: return
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r: return await event.reply("⚠️ لازم ترد على الشخص.")
        try:
            await event.client(EditBannedRequest(event.chat_id, r.sender_id, mute_rights))
            await event.reply(f"اتسكت.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.فك_السكات$"))
    async def unmute_user(event):
        if not event.is_group: return
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r: return await event.reply("⚠️ لازم ترد على الشخص.")
        try:
            await event.client(EditBannedRequest(event.chat_id, r.sender_id, unmute_rights))
            await event.reply(f"اتشال السكات.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.ترقية$"))
    async def promote_user(event):
        if not event.is_group: return
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r: return await event.reply("⚠️ لازم ترد على الشخص.")
        try:
            rights = ChatAdminRights(post_messages=True, edit_messages=True, delete_messages=True,
                                     ban_users=True, invite_users=True, pin_messages=True, add_admins=False)
            await event.client(EditAdminRequest(event.chat_id, r.sender_id, rights, rank="Helper"))
            await event.reply(f"اترقّى Helper.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.تنزيل$"))
    async def demote_user(event):
        if not event.is_group: return
        if not is_sudo(event.sender_id): return
        r = await event.get_reply_message()
        if not r: return await event.reply("⚠️ لازم ترد على الشخص.")
        try:
            rights = ChatAdminRights()  # remove
            await event.client(EditAdminRequest(event.chat_id, r.sender_id, rights, rank=""))
            await event.reply(f"اتشال منه الأدمن.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.تثبيت$"))
    async def pin_msg(event):
        r = await event.get_reply_message()
        if not r: return await event.reply("رد على الرسالة لتثبيتها.")
        try:
            await r.pin()
            await event.reply(f"اتثبتت.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")

    @client.on(events.NewMessage(pattern=r"^\.إلغاء_التثبيت$"))
    async def unpin_all(event):
        try:
            await event.client.unpin_message(event.chat_id)
            await event.reply(f"اتشال التثبيت.\n{CREDITS}")
        except Exception as e:
            await event.reply(f"فشل: `{e}`")
