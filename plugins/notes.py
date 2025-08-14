from telethon import events

NOTES = {}
FILTERS = {}

def setup(client, is_sudo, log, CREDITS):
    @client.on(events.NewMessage(pattern=r"^\.note (\S+)\s+(.+)$"))
    async def add_note(event):
        if not is_sudo(event.sender_id): return
        name, text = event.pattern_match.group(1), event.pattern_match.group(2)
        NOTES[name] = text
        await event.reply(f"اتحفظت الملاحظة `{name}`.\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.get (\S+)$"))
    async def get_note(event):
        name = event.pattern_match.group(1)
        await event.reply(NOTES.get(name, "مش لاقي الملاحظة."))

    @client.on(events.NewMessage(pattern=r"^\.notes$"))
    async def list_notes(event):
        if not NOTES:
            return await event.reply("مفيش ملاحظات.")
        items = "\n".join(f"- {k}" for k in NOTES.keys())
        await event.reply(f"**Notes:**\n{items}\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.rmnote (\S+)$"))
    async def rm_note(event):
        if not is_sudo(event.sender_id): return
        name = event.pattern_match.group(1)
        if NOTES.pop(name, None) is None:
            await event.reply("مش موجودة.")
        else:
            await event.reply("اتمسحت.")

    @client.on(events.NewMessage(pattern=r"^\.filter (.+)$"))
    async def add_filter(event):
        if not is_sudo(event.sender_id): return
        raw = event.pattern_match.group(1)
        if "=" not in raw:
            return await event.reply("الصيغة: `.filter كلمة = رد`")
        key, val = [x.strip() for x in raw.split("=", 1)]
        FILTERS[key.lower()] = val
        await event.reply(f"اتضاف الفلتر `{key}`.\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.filters$"))
    async def list_filters(event):
        if not FILTERS:
            return await event.reply("مفيش فلاتر.")
        items = "\n".join(f"- {k}" for k in FILTERS.keys())
        await event.reply(f"**Filters:**\n{items}\n{CREDITS}")

    @client.on(events.NewMessage(pattern=r"^\.rmfilter (.+)$"))
    async def rm_filter(event):
        if not is_sudo(event.sender_id): return
        key = event.pattern_match.group(1).lower().strip()
        if FILTERS.pop(key, None) is None:
            await event.reply("مش موجود.")
        else:
            await event.reply("اتمسح.")

    @client.on(events.NewMessage(incoming=True))
    async def filter_watch(event):
        if not FILTERS or event.out: return
        text = (event.raw_text or "").lower()
        for k, v in FILTERS.items():
            if k in text:
                await event.reply(v + f"\n\n{CREDITS}")
                break
