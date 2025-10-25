import re
import discord
import asyncio
from pathlib import Path
import config

emoji_server_ids = config.EMOJIS_SERVER

# Path to your emote file
EMOTE_FILE = Path("utils/emote.py")

# Regex to match <:name:id> or <a:name:id>
EMOTE_PATTERN = re.compile(r"<(a?):(\w+):(\d+)>")

def parse_emotes(file_path):
    """Parse all emotes from emote.py"""
    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()
    matches = EMOTE_PATTERN.findall(data)
    emotes = {}
    for animated, name, eid in matches:
        emotes[name] = {
            "id": int(eid),
            "animated": bool(animated),
            "url": f"https://cdn.discordapp.com/emojis/{eid}.{'gif' if animated else 'png'}"
        }
    return data, emotes


async def upload_emote(bot, emoji_info, emoji_server_ids):
    """Upload emoji to available server if not already present"""
    name, info = emoji_info
    for server_id in emoji_server_ids:
        guild = bot.get_guild(server_id)
        if not guild:
            print(f"⚠️ Guild {server_id} not found or bot not in it")
            continue

        try:
            async with bot.session.get(info["url"]) as resp:
                if resp.status != 200:
                    print(f"❌ Failed to download emoji {name}")
                    continue
                img_bytes = await resp.read()

            new_emoji = await guild.create_custom_emoji(
                name=name,
                image=img_bytes,
                reason="Synced from emote.py"
            )
            print(f"🆕 Uploaded {name} to {guild.name}")
            return new_emoji

        except discord.HTTPException as e:
            if "Maximum number of emojis reached" in str(e):
                print(f"⚠️ {guild.name} full, trying next server...")
                continue
            print(f"❌ Failed to upload {name} to {guild.name}: {e}")
            continue

    print(f"🚫 Could not upload {name} (all servers full)")
    return None


async def main():
    intents = discord.Intents(guilds=True)
    bot = discord.Client(intents=intents)

    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        bot.session = bot.http._HTTPClient__session

        print("🔍 Reading emote.py...")
        data, all_emotes = parse_emotes(EMOTE_FILE)
        print(f"Found {len(all_emotes)} emotes")

        # Collect all emojis across all emoji servers
        all_server_emojis = []
        for sid in emoji_server_ids:
            guild = bot.get_guild(sid)
            if guild:
                all_server_emojis.extend(guild.emojis)
            else:
                print(f"⚠️ Bot not in guild {sid}")

        updated = {}

        for name, info in all_emotes.items():
            # check if emoji ID already exists in servers
            existing = next((e for e in all_server_emojis if e.id == info["id"]), None)
            if existing:
                updated[name] = f"<{'a' if existing.animated else ''}:{existing.name}:{existing.id}>"
                print(f"✅ Matched existing emoji: {updated[name]}")
                continue

            # if not found, upload
            new_emoji = await upload_emote(bot, (name, info), emoji_server_ids)
            if new_emoji:
                updated[name] = f"<{'a' if new_emoji.animated else ''}:{new_emoji.name}:{new_emoji.id}>"
                all_server_emojis.append(new_emoji)

        # Rewrite file
        new_data = data
        for name, tag in updated.items():
            new_data = re.sub(rf"<a?:{name}:\d+>", tag, new_data)

        EMOTE_FILE.write_text(new_data, encoding="utf-8")
        print(f"\n✅ Updated emote.py successfully ({len(updated)} emojis synced).")

        await bot.close()

    await bot.start(config.DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
