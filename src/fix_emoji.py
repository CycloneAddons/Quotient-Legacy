import re
import discord
import asyncio
import aiohttp
import base64
from pathlib import Path
import config

_raw_servers = getattr(config, "EMOJIS_SERVER", None)

if not _raw_servers:
    emoji_server_ids = []
else:
    try:
        emoji_server_ids = [int(x) for x in _raw_servers]
    except Exception:
        emoji_server_ids = []

TOKEN = getattr(config, "DISCORD_TOKEN", None)

BASE_DIR = Path(__file__).resolve().parent.parent
EMOTE_FILE = BASE_DIR / "src" / "utils" / "emote.py"

EMOTE_PATTERN = re.compile(r"<(a?):(\w+):(\d+)>")

MAX_EMOJI_SIZE = 256_000

GUILD_UPLOAD_TIMEOUT = 45
APP_UPLOAD_TIMEOUT = 30

def log_main(idx, icon, emoji_name, message):
    print(f"{idx}. {icon} {emoji_name} {message}")

def log_sub(icon, emoji_name, message):
    print(f"   └ {icon} {emoji_name} {message}")

def emoji_to_string(emoji):
    animated = (
        emoji.animated
        if hasattr(emoji, "animated")
        else emoji.get("animated", False)
    )

    name = (
        emoji.name
        if hasattr(emoji, "name")
        else emoji.get("name")
    )

    emoji_id = (
        emoji.id
        if hasattr(emoji, "id")
        else emoji.get("id")
    )

    return f"<{'a' if animated else ''}:{name}:{emoji_id}>"

def get_emoji_name(emoji):
    return emoji.name if hasattr(emoji, "name") else emoji.get("name")

def get_emoji_id(emoji):
    return emoji.id if hasattr(emoji, "id") else int(emoji.get("id"))

def get_emoji_animated(emoji):
    return (
        emoji.animated
        if hasattr(emoji, "animated")
        else emoji.get("animated", False)
    )

def build_emoji_cache(guilds):
    emojis = {e.id: e for g in guilds for e in g.emojis}
    names = {e.name for e in emojis.values()}
    return emojis, names

def find_existing_emoji(name, emoji_id, all_server_emojis, guilds):
    if emoji_id in all_server_emojis:
        return all_server_emojis[emoji_id]

    for guild in guilds:
        for emoji in guild.emojis:
            if emoji.name == name:
                return emoji

    return None

async def download_emoji(session, url):
    async with session.get(url) as resp:
        if resp.status != 200:
            return None, resp.status

        data = await resp.read()

        if len(data) > MAX_EMOJI_SIZE:
            return "too_large", None

        return data, None

def parse_emotes(file_path: Path):
    print(f"📁 Loading emote file: {file_path.resolve()}")

    if not file_path.exists():
        raise FileNotFoundError(
            f"❌ emote.py not found at {file_path.resolve()}"
        )

    data = file_path.read_text(encoding="utf-8")

    matches = EMOTE_PATTERN.findall(data)

    print(f"📊 Found {len(matches)} emojis")

    emotes = {}

    for animated, name, eid in matches:
        emotes[name] = {
            "id": int(eid),
            "animated": bool(animated),
            "url": (
                f"https://cdn.discordapp.com/emojis/"
                f"{eid}.{'gif' if animated else 'png'}"
            )
        }

    return data, emotes

# =========================
# GUILD EMOJI UPLOAD
# =========================

async def upload_emote(
    bot,
    idx,
    emoji_name,
    info,
    guilds,
    all_server_names
):
    if emoji_name in all_server_names:
        existing = next(
            (
                e
                for guild in guilds
                for e in guild.emojis
                if e.name == emoji_name
            ),
            None
        )

        if existing:
            where = getattr(existing.guild, "name", "Unknown")

            log_main(
                idx,
                "✅",
                emoji_name,
                f"exists - {where}"
            )

            return {
                "type": "existing",
                "emoji": existing
            }

    for guild in guilds:
        if len(guild.emojis) >= guild.emoji_limit:
            log_main(
                idx,
                "⚠️",
                emoji_name,
                f"skipped - {guild.name} full"
            )
            continue

        log_main(
            idx,
            "⬆️",
            emoji_name,
            f"uploading - {guild.name}"
        )

        try:
            img_bytes, error = await download_emoji(
                bot.session,
                info["url"]
            )

            if error:
                log_sub(
                    "❌",
                    emoji_name,
                    f"download failed - HTTP {error}"
                )
                continue

            if img_bytes == "too_large":
                log_sub(
                    "⚠️",
                    emoji_name,
                    "skipped - File Too Large"
                )
                continue

            new_emoji = await asyncio.wait_for(
                guild.create_custom_emoji(
                    name=emoji_name,
                    image=img_bytes,
                    reason="Synced from emote.py"
                ),
                timeout=15
            )

            log_sub(
                "✅",
                emoji_name,
                f"uploaded - {guild.name}"
            )

            return {
                "type": "uploaded",
                "emoji": new_emoji
            }

        except asyncio.TimeoutError:
            log_sub(
                "⌛",
                emoji_name,
                f"timeout - {guild.name}"
            )

        except Exception as e:
            log_sub(
                "❌",
                emoji_name,
                f"failed - {type(e).__name__}"
            )

    log_main(
        idx,
        "❌",
        emoji_name,
        "upload failed - No Available Server"
    )

    return None

async def upload_to_application(
    bot,
    idx,
    emoji_name,
    info,
    token
):
    if not token:
        log_main(
            idx,
            "❌",
            emoji_name,
            "upload failed - Missing Bot Token"
        )
        return None

    headers = {
        "Authorization": f"Bot {token}",
        "Content-Type": "application/json"
    }

    app_id = getattr(bot, "app_id", None)
    app_emojis = getattr(bot, "app_emojis", None)

    if not app_id or app_emojis is None:
        async with bot.session.get(
            "https://discord.com/api/v10/users/@me",
            headers=headers
        ) as r:

            if r.status != 200:
                log_main(
                    idx,
                    "❌",
                    emoji_name,
                    "failed - Cannot Fetch Bot Info"
                )
                return None

            bot_info = await r.json()

            app_id = bot_info.get("id")

            if not app_id:
                log_main(
                    idx,
                    "❌",
                    emoji_name,
                    "failed - Missing Application ID"
                )
                return None

        async with bot.session.get(
            f"https://discord.com/api/v10/applications/{app_id}/emojis",
            headers=headers
        ) as r2:

            if r2.status != 200:
                log_main(
                    idx,
                    "❌",
                    emoji_name,
                    "failed - Cannot Fetch App Emojis"
                )
                return None

            app_emojis = await r2.json()

            if (
                isinstance(app_emojis, dict)
                and "items" in app_emojis
            ):
                app_emojis = app_emojis["items"]

        bot.app_id = app_id
        bot.app_emojis = app_emojis

    for emoji in app_emojis:
        if emoji.get("name") == emoji_name:
            log_main(
                idx,
                "✅",
                emoji_name,
                "exists - Bot Emoji"
            )

            return {
                "type": "existing",
                "emoji": emoji
            }

    log_main(
        idx,
        "⬆️",
        emoji_name,
        "uploading - Bot Emoji"
    )

    img_bytes, error = await download_emoji(
        bot.session,
        info["url"]
    )

    if error:
        log_sub(
            "❌",
            emoji_name,
            f"download failed - HTTP {error}"
        )
        return None

    if img_bytes == "too_large":
        log_sub(
            "⚠️",
            emoji_name,
            "skipped - File Too Large"
        )
        return None

    mime = "image/gif" if info.get("animated") else "image/png"

    b64 = base64.b64encode(img_bytes).decode("utf-8")

    image_uri = f"data:{mime};base64,{b64}"

    payload = {
        "name": emoji_name,
        "image": image_uri
    }

    async with bot.session.post(
        f"https://discord.com/api/v10/applications/{app_id}/emojis",
        headers=headers,
        json=payload
    ) as r3:

        if r3.status in (200, 201):
            new_emoji = await r3.json()

            log_sub(
                "✅",
                emoji_name,
                "uploaded - Bot Emoji"
            )

            return {
                "type": "uploaded",
                "emoji": new_emoji
            }

        text = await r3.text()

        log_sub(
            "❌",
            emoji_name,
            f"failed - HTTP {r3.status}"
        )

        print(f"      {text}")

        return None

async def main():
    intents = discord.Intents.default()
    intents.guilds = True
    intents.emojis_and_stickers = True

    bot = discord.Client(intents=intents)

    bot.session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=60)
    )

    @bot.event
    async def on_ready():
        print(f"\n✅ Logged in as {bot.user}\n")

        await bot.wait_until_ready()

        data, all_emotes = parse_emotes(EMOTE_FILE)

        print(f"\n✅ Checking {len(all_emotes)} emojis\n")

        guilds = [
            bot.get_guild(sid)
            for sid in emoji_server_ids
            if bot.get_guild(sid)
        ]

        all_server_emojis, all_server_names = (
            build_emoji_cache(guilds)
        )

        use_application = len(guilds) == 0

        if use_application:
            headers = {
                "Authorization": f"Bot {TOKEN}",
                "Content-Type": "application/json"
            }

            async with bot.session.get(
                "https://discord.com/api/v10/users/@me",
                headers=headers
            ) as r:

                if r.status == 200:
                    bot_info = await r.json()

                    app_id = bot_info.get("id")

                    if app_id:
                        async with bot.session.get(
                            f"https://discord.com/api/v10/applications/{app_id}/emojis",
                            headers=headers
                        ) as r2:

                            if r2.status == 200:
                                app_emojis = await r2.json()

                                for emoji in app_emojis:
                                    try:
                                        eid = int(emoji.get("id"))
                                    except Exception:
                                        continue

                                    all_server_emojis[eid] = emoji
                                    all_server_names.add(
                                        emoji.get("name")
                                    )

        new_data = data
        updated = {}

        for idx, (name, info) in enumerate(
            all_emotes.items(),
            start=1
        ):
            existing = find_existing_emoji(
                name,
                info["id"],
                all_server_emojis,
                guilds
            )

            if existing:
                where = (
                    "Bot Emoji"
                    if use_application
                    else getattr(
                        existing.guild,
                        "name",
                        "Unknown"
                    )
                )

                log_main(
                    idx,
                    "✅",
                    name,
                    f"exists - {where}"
                )

                updated[name] = emoji_to_string(existing)
                continue

            try:
                if use_application:
                    result = await asyncio.wait_for(
                        upload_to_application(
                            bot,
                            idx,
                            name,
                            info,
                            TOKEN
                        ),
                        timeout=APP_UPLOAD_TIMEOUT
                    )

                else:
                    result = await asyncio.wait_for(
                        upload_emote(
                            bot,
                            idx,
                            name,
                            info,
                            guilds,
                            all_server_names
                        ),
                        timeout=GUILD_UPLOAD_TIMEOUT
                    )

            except asyncio.TimeoutError:
                log_main(
                    idx,
                    "⌛",
                    name,
                    "timeout"
                )
                continue

            if not result:
                continue

            emoji = result["emoji"]

            emoji_string = emoji_to_string(emoji)

            updated[name] = emoji_string

            try:
                all_server_emojis[get_emoji_id(emoji)] = emoji
                all_server_names.add(get_emoji_name(emoji))
            except Exception:
                pass

            new_data = re.sub(
                rf"<a?:{re.escape(name)}:\d+>",
                emoji_string,
                new_data
            )

        EMOTE_FILE.write_text(
            new_data,
            encoding="utf-8"
        )

        print(
            f"\n✅ Synced {len(updated)} emojis successfully.\n"
        )

        await bot.session.close()
        await bot.close()

    try:
        await bot.start(TOKEN)

    finally:
        if not bot.session.closed:
            await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())