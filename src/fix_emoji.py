import re
import discord
import asyncio
import aiohttp
from pathlib import Path
import config


emoji_server_ids = [int(x) for x in config.EMOJIS_SERVER]
TOKEN = config.DISCORD_TOKEN

BASE_DIR = Path(__file__).resolve().parent.parent
EMOTE_FILE = BASE_DIR / "src" / "utils" / "emote.py"

EMOTE_PATTERN = re.compile(r"<(a?):(\w+):(\d+)>")


def parse_emotes(file_path: Path):
    """Parse all emotes from emote.py"""
    print(f"📁 Loading emote file from: {file_path.resolve()}")

    if not file_path.exists():
        raise FileNotFoundError(f"❌ emote.py not found at {file_path.resolve()}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = f.read()

    matches = EMOTE_PATTERN.findall(data)
    print(f"📊 Regex matched {len(matches)} emojis")

    emotes = {}
    for animated, name, eid in matches:
        emotes[name] = {
            "id": int(eid),
            "animated": bool(animated),
            "url": f"https://cdn.discordapp.com/emojis/{eid}.{'gif' if animated else 'png'}"
        }
    return data, emotes


async def upload_emote(bot, emoji_info, guilds, all_server_names):
    """Upload emoji to the first available server that doesn't already have it"""
    name, info = emoji_info

    if name in all_server_names:
        target_emoji = next(
            (e for guild in guilds for e in guild.emojis if e.name == name),
            None
        )
        if target_emoji:
            emote_string = f"<{'a' if target_emoji.animated else ''}:{target_emoji.name}:{target_emoji.id}>"
            print(f"✅ Emoji {name} already exists — updating file with {emote_string}")
            return {"got": True, "emotee": emote_string}

    for guild in guilds:
        if len(guild.emojis) >= guild.emoji_limit:
            print(f"⚠️ {guild.name} full (limit {guild.emoji_limit}), skipping...")
            continue

        try:
            async with bot.session.get(info["url"]) as resp:
                if resp.status != 200:
                    print(f"❌ Failed to download {name} (status {resp.status})")
                    continue
                img_bytes = await resp.read()

            if len(img_bytes) > 256_000:
                print(f"⚠️ {name} too large (>256 KB), skipping...")
                continue

            new_emoji = await asyncio.wait_for(
                guild.create_custom_emoji(
                    name=name,
                    image=img_bytes,
                    reason="Synced from emote.py"
                ),
                timeout=15
            )
            print(f"🆕 Uploaded {name} to {guild.name}")
            return new_emoji

        except asyncio.TimeoutError:
            print(f"⌛ Timeout uploading {name} in {guild.name}")
        except Exception as e:
            print(f"❌ Failed {name} in {guild.name}: {type(e).__name__} - {e}")

    print(f"🚫 Could not upload {name} (all servers full or exist)")
    return None


async def main():
    intents = discord.Intents.default()
    intents.guilds = True
    intents.emojis_and_stickers = True

    bot = discord.Client(intents=intents)
    bot.session = aiohttp.ClientSession()

    @bot.event
    async def on_ready():
        print(f"✅ Logged in as {bot.user}")
        await bot.wait_until_ready()

        data, all_emotes = parse_emotes(EMOTE_FILE)
        print(f"✅ Found {len(all_emotes)} emotes to check\n")

        guilds = [bot.get_guild(sid) for sid in emoji_server_ids if bot.get_guild(sid)]
        all_server_emojis = {e.id: e for g in guilds for e in g.emojis}
        all_server_names = {e.name for e in all_server_emojis.values()}

        new_data = data
        updated = {}

        for name, info in all_emotes.items():
            if info["id"] in all_server_emojis:
                existing = all_server_emojis[info["id"]]
                updated[name] = f"<{'a' if existing.animated else ''}:{existing.name}:{existing.id}>"
                print(f"✅ Skipping {name}, ID {info['id']} already exists as {existing.name}")
                continue

            new_emoji = await upload_emote(bot, (name, info), guilds, all_server_names)

            if isinstance(new_emoji, dict) and new_emoji.get("got"):
                updated[name] = new_emoji["emotee"]
            elif new_emoji:
                updated[name] = f"<{'a' if new_emoji.animated else ''}:{new_emoji.name}:{new_emoji.id}>"
                all_server_emojis[new_emoji.id] = new_emoji
                all_server_names.add(new_emoji.name)

            if name in updated:
                new_data = re.sub(rf"<a?:{re.escape(name)}:\d+>", updated[name], new_data)

        EMOTE_FILE.write_text(new_data, encoding="utf-8")

        print(f"\n✅ Updated emote.py successfully ({len(updated)} emojis synced).")

        await bot.session.close()
        await bot.close()

    try:
        await bot.start(TOKEN)
    finally:
        if not bot.session.closed:
            await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
