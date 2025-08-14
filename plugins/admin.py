from telethon import events
from telethon.tl.functions.channels import EditBannedRequest, EditAdminRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights

def setup(client, is_sudo, log, CREDITS):
    # تعريف صلاحيات الحظر/الكتم مرة واحدة بدلاً من تكرارها
    MUTE_RIGHTS = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        send_polls=True,
        change_info=True,
        invite_users=True,
        pin_messages=True
    )

    UNMUTE_RIGHTS = ChatBannedRights(until_date=None)

    FULL_ADMIN_RIGHTS = ChatAdminRights(
        post_messages=True,
        edit_messages=True,
        delete_messages=True,
        ban_users=True,
        invite_users=True,
        pin_messages=True,
        add_admins=True,
        change_info=True,
        manage_call=True
    )

    HELPER_ADMIN_RIGHTS = ChatAdminRights(
        post_messages=True,
        edit_messages=True,
        delete_messages=True,
        ban_users=True,
        invite_users=True,
        pin_messages=True,
        add_admins=False
    )

    async def check_permissions(event):
        """دالة مساعدة للتحقق من الصلاحيات"""
        if not await event.is_group():
            await event.reply("⚠️ هذا الأمر يعمل في المجموعات فقط!")
            return False

        if not is_sudo(event.sender_id):
            await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
            return False

        return True

    @client.on(events.NewMessage(pattern=r"^\.طرد$"))
    async def kick_user(event):
        """طرد مستخدم من المجموعة"""
        if not await check_permissions(event):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الشخص المراد طرده")

        try:
            await event.client.kick_participant(event.chat_id, reply.sender_id)
            await log(f"تم طرد المستخدم {reply.sender_id} من {event.chat_id}")
            await event.reply(f"✅ تم الطرد بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل الطرد: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.حظر$"))
    async def ban_user(event):
        """حظر مستخدم من المجموعة"""
        if not await check_permissions(event):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الشخص المراد حظره")

        try:
            await event.client(EditBannedRequest(
                event.chat_id,
                reply.sender_id,
                ChatBannedRights(until_date=None, view_messages=True)
            ))
            await log(f"تم حظر المستخدم {reply.sender_id} من {event.chat_id}")
            await event.reply(f"✅ تم الحظر بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل الحظر: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.سكات$"))
    async def mute_user(event):
        """كتم مستخدم في المجموعة"""
        if not await check_permissions(event):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الشخص المراد كتمه")

        try:
            await event.client(EditBannedRequest(
                event.chat_id,
                reply.sender_id,
                MUTE_RIGHTS
            ))
            await log(f"تم كتم المستخدم {reply.sender_id} في {event.chat_id}")
            await event.reply(f"✅ تم الكتم بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل الكتم: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.فك_السكات$"))
    async def unmute_user(event):
        """إلغاء كتم مستخدم في المجموعة"""
        if not await check_permissions(event):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الشخص المراد إلغاء كتمه")

        try:
            await event.client(EditBannedRequest(
                event.chat_id,
                reply.sender_id,
                UNMUTE_RIGHTS
            ))
            await log(f"تم إلغاء كتم المستخدم {reply.sender_id} في {event.chat_id}")
            await event.reply(f"✅ تم إلغاء الكتم بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل إلغاء الكتم: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.ترقية$"))
    async def promote_user(event):
        """ترقية مستخدم إلى مشرف"""
        if not await check_permissions(event):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الشخص المراد ترقيته")

        try:
            await event.client(EditAdminRequest(
                event.chat_id,
                reply.sender_id,
                HELPER_ADMIN_RIGHTS,
                rank="مساعد"
            ))
            await log(f"تم ترقية المستخدم {reply.sender_id} في {event.chat_id}")
            await event.reply(f"✅ تم الترقية بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل الترقية: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.تنزيل$"))
    async def demote_user(event):
        """تنزيل مشرف إلى عضو عادي"""
        if not await check_permissions(event):
            return

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الشخص المراد تنزيله")

        try:
            await event.client(EditAdminRequest(
                event.chat_id,
                reply.sender_id,
                ChatAdminRights(),  # إزالة جميع الصلاحيات
                rank=""
            ))
            await log(f"تم تنزيل المستخدم {reply.sender_id} في {event.chat_id}")
            await event.reply(f"✅ تم التنزيل بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل التنزيل: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.تثبيت$"))
    async def pin_msg(event):
        """تثبيت رسالة في المجموعة"""
        if not await event.is_group():
            return await event.reply("⚠️ هذا الأمر يعمل في المجموعات فقط!")

        reply = await event.get_reply_message()
        if not reply:
            return await event.reply("⚠️ يرجى الرد على الرسالة المراد تثبيتها")

        try:
            await reply.pin()
            await log(f"تم تثبيت رسالة في {event.chat_id}")
            await event.reply(f"✅ تم التثبيت بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل التثبيت: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.إلغاء_التثبيت$"))
    async def unpin_all(event):
        """إلغاء تثبيت جميع الرسائل"""
        if not await event.is_group():
            return await event.reply("⚠️ هذا الأمر يعمل في المجموعات فقط!")

        try:
            await event.client.unpin_message(event.chat_id)
            await log(f"تم إلغاء تثبيت الرسائل في {event.chat_id}")
            await event.reply(f"✅ تم إلغاء التثبيت بنجاح\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل إلغاء التثبيت: {str(e)}")
