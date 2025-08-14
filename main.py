import os
import asyncio
import importlib
import glob
from telethon import TelegramClient, events, functions
from telethon.sessions import StringSession
from telethon.tl.functions.users import GetFullUserRequest
from dotenv import load_dotenv

# ========= إعدادات البيئة =========
load_dotenv()
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
STRING_SESSION = os.getenv("STRING_SESSION", "").strip()
PHONE_NUMBER = os.getenv("PHONE_NUMBER", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
SUDO_IDS = [int(x) for x in os.getenv("SUDO_IDS", "").split(",") if x.strip().isdigit()]
LOG_CHAT = int(os.getenv("LOG_CHAT", "0")) if os.getenv("LOG_CHAT", "").isdigit() else None
ALIVE_TEXT = os.getenv("ALIVE_TEXT", "I'm alive as 3AZEF!")
ALIVE_PIC = os.getenv("ALIVE_PIC", "")

CREDITS = "© 3AZEF — @T_8l8"

if not API_ID or not API_HASH:
    raise SystemExit("ضع API_ID و API_HASH في .env")

# ========= بدء الجلسة =========
client = TelegramClient(
    StringSession(STRING_SESSION) if STRING_SESSION else "3azef_session",
    API_ID, API_HASH
)

# لو مفيش STRING_SESSION هيطلب تسجيل دخول لمرة واحدة
async def ensure_signed_in():
    if STRING_SESSION:
        return
    if await client.is_user_authorized():
        return
    if not PHONE_NUMBER:
        raise SystemExit("لا يوجد STRING_SESSION ولا PHONE_NUMBER. وفّر واحدًا على الأقل.")
    await client.send_code_request(PHONE_NUMBER)
    code = input("ادخل كود التحقق: ")
    try:
        await client.sign_in(PHONE_NUMBER, code)
        print("تم تسجيل الدخول بنجاح.")
        print("Session String (انسخه وخزّنه في .env -> STRING_SESSION):")
        print(client.session.save())
    except Exception as e:
        print("فشل تسجيل الدخول:", e)
        raise

# ========= صلاحيات =========
def is_sudo(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_IDS

# ========= لوجر بسيط =========
async def log(msg: str):
    if LOG_CHAT:
        try:
            await client.send_message(LOG_CHAT, msg)
        except Exception as e:
            print(f"فشل إرسال الرسالة إلى اللوج: {e}")

# ========= تحميل الإضافات =========
def load_plugins():
    for path in glob.glob("plugins/*.py"):
        mod_name = os.path.splitext(os.path.basename(path))[0]
        if mod_name.startswith("_"):
            continue
        try:
            module = importlib.import_module(f"plugins.{mod_name}")
            if hasattr(module, "setup"):
                module.setup(client, is_sudo, log, CREDITS)
            print(f"[OK] تم تحميل الإضافة: {mod_name}")
        except Exception as e:
            print(f"[Error] فشل تحميل {mod_name}: {e}")

# ========= أوامر أساسية =========
@client.on(events.NewMessage(pattern=r"^\.(alive|بنج|ping)$"))
async def alive_handler(event):
    if ALIVE_PIC:
        await event.reply(file=ALIVE_PIC, message=f"{ALIVE_TEXT}\n{CREDITS}")
    else:
        await event.reply(f"{ALIVE_TEXT}\n{CREDITS}")

@client.on(events.NewMessage(pattern=r"^\.help$"))
async def help_handler(event):
    text = (
        "**3AZEF — Userbot Help**\n"
        "`أساسيات:` .alive .ping .id .info .bio .username .del .edit .purge\n"
        "`إداري:` .طرد .حظر .سكات .فك_السكات .ترقية .تنزيل .تثبيت .إلغاء_التثبيت\n"
        "`حالة:` .afk [سبب] — وترجع تلقائيًا أول رسالة\n"
        "`ملاحظات:` .note اسم نص | .notes | .get اسم | .rmnote اسم\n"
        "`فلاتر:` .filter كلمة = رد | .filters | .rmfilter كلمة\n"
        "`إذاعة:` .اذاعة نص (للجروبات/الخاص اختيارًا)\n"
        "`أخرى:` .انضم رابط | .غادر | .برودكاست_ملف (بالرد على ملف)\n"
        f"\n{CREDITS}"
    )
    await event.reply(text)

@client.on(events.NewMessage(pattern=r"^\.id$"))
async def id_handler(event):
    reply = await event.get_reply_message()
    if reply:
        await event.reply(f"**Chat:** `{event.chat_id}`\n**User:** `{reply.sender_id}`\n{CREDITS}")
    else:
        await event.reply(f"**Chat:** `{event.chat_id}`\n**User:** `{event.sender_id}`\n{CREDITS}")

@client.on(events.NewMessage(pattern=r"^\.info$"))
async def info_handler(event):
    reply = await event.get_reply_message()
    entity = await event.client.get_entity(reply.sender_id) if reply else await event.get_sender()
    if entity:
        full = await event.client(GetFullUserRequest(entity.id))
        user_info = (
            f"**معلومات المستخدم:**\n"
            f"**الاسم:** {entity.first_name}\n"
            f"**ID:** `{entity.id}`\n"
            f"**اليوزر:** @{entity.username}\n"
            f"**بايو:** {full.about}\n"
            f"**تاريخ الإنشاء:** {entity.date}\n"
            f"{CREDITS}"
        )
        await event.reply(user_info)

@client.on(events.NewMessage(pattern=r"^\.bio (.+)$"))
async def bio_handler(event):
    if not is_sudo(event.sender_id):
        return await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
    try:
        bio = event.pattern_match.group(1).strip()
        await client(functions.account.UpdateProfileRequest(about=bio))
        await event.reply(f"تم تحديث البايو.\n{CREDITS}")
    except Exception as e:
        await event.reply(f"فشل التحديث: `{e}`")

@client.on(events.NewMessage(pattern=r"^\.username (.+)$"))
async def username_handler(event):
    if not is_sudo(event.sender_id):
        return await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
    uname = event.pattern_match.group(1).strip().lstrip("@")
    try:
        await client(functions.account.UpdateUsernameRequest(uname))
        await event.reply(f"تم تحديث اليوزر: @{uname}\n{CREDITS}")
    except Exception as e:
        await event.reply(f"فشل: `{e}`")

@client.on(events.NewMessage(pattern=r"^\.del$"))
async def del_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("رد على الرسالة المراد حذفها.")
    try:
        await reply.delete()
        await event.delete()
    except Exception as e:
        await event.reply(f"فشل الحذف: {e}")

@client.on(events.NewMessage(pattern=r"^\.edit (.+)$"))
async def edit_handler(event):
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("رد على الرسالة المراد تعديلها.")
    txt = event.pattern_match.group(1)
    try:
        await reply.edit(txt + f"\n\n{CREDITS}")
        await event.delete()
    except Exception as e:
        await event.reply(f"فشل: `{e}`")

@client.on(events.NewMessage(pattern=r"^\.purge$"))
async def purge_handler(event):
    if not is_sudo(event.sender_id):
        return await event.reply("⚠️ ليس لديك صلاحية لاستخدام هذا الأمر!")
    reply = await event.get_reply_message()
    if not reply:
        return await event.reply("رد على أول رسالة تبدأ منها التنظيف.")
    try:
        msgs = []
        async for msg in client.iter_messages(event.chat_id, min_id=reply.id, from_user='me'):
            msgs.append(msg.id)
            if len(msgs) >= 99:
                await client.delete_messages(event.chat_id, msgs)
                msgs = []
        if msgs:
            await client.delete_messages(event.chat_id, msgs)
        await event.reply("تم التنظيف ✅")
    except Exception as e:
        await event.reply(f"فشل: `{e}`")

# ========= تشغيل =========
async def main():
    await ensure_signed_in()
    load_plugins()
    await log("✅ 3AZEF userbot started.")
    print("3AZEF is running...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
