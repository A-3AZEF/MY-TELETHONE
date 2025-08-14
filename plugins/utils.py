from telethon import events
from telethon.tl import functions
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError

def setup(client, is_sudo, log, CREDITS):

    async def check_sudo_permission(event):
        """تحقق من صلاحيات المستخدم"""
        if not is_sudo(event.sender_id):
            await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
            return False
        return True

    @client.on(events.NewMessage(pattern=r"^\.انضم (.+)$"))
    async def join_chat(event):
        """الانضمام إلى قناة أو مجموعة"""
        if not await check_sudo_permission(event):
            return

        link = event.pattern_match.group(1).strip()
        try:
            await client(functions.channels.JoinChannelRequest(link))
            await log(f"تم الانضمام إلى: {link}")
            await event.reply(f"✅ تم الانضمام بنجاح\n{CREDITS}")
        except ChannelPrivateError:
            await event.reply("❌ المجموعة خاصة ولا يمكن الانضمام إليها")
        except ValueError:
            await event.reply("❌ الرابط غير صالح أو غير مكتمل")
        except Exception as e:
            await event.reply(f"❌ فشل الانضمام: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.غادر$"))
    async def leave_chat(event):
        """مغادرة الدردشة الحالية"""
        if not await check_sudo_permission(event):
            return

        try:
            await client(functions.channels.LeaveChannelRequest(event.chat_id))
            await log(f"تم مغادرة الدردشة: {event.chat_id}")
            # لا حاجة للرد لأن البوت سيغادر المجموعة
        except ChatAdminRequiredError:
            await event.reply("❌ لا يمكن مغادرة المجموعة لأنك مشرف رئيسي")
        except Exception as e:
            await event.reply(f"❌ فشل المغادرة: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.انتحال (.+)$"))
    async def impersonate(event):
        """تغيير الاسم المعروض للبوت"""
        if not await check_sudo_permission(event):
            return

        name = event.pattern_match.group(1).strip()
        if len(name) > 30:
            return await event.reply("❌ الاسم طويل جداً (الحد الأقصى 30 حرفاً)")

        try:
            await client(functions.account.UpdateProfileRequest(
                first_name=name,
                last_name=""
            ))
            await log(f"تم تغيير الاسم إلى: {name}")
            await event.reply(f"✅ تم تغيير الاسم إلى: {name}\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل تغيير الاسم: {str(e)}")

    @client.on(events.NewMessage(pattern=r"^\.قول (.+)$"))
    async def say(event):
        """إرسال نص معين"""
        if not await check_sudo_permission(event):
            return

        txt = event.pattern_match.group(1)
        if not txt or len(txt) > 2000:
            return await event.reply("❌ النص فارغ أو طويل جداً (الحد الأقصى 2000 حرف)")

        try:
            await event.delete()  # حذف الأمر الأصلي
            await event.respond(txt + f"\n\n{CREDITS}")
        except Exception as e:
            await event.reply(f"❌ فشل إرسال الرسالة: {str(e)}")
