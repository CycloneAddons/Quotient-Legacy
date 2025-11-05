TORTOISE = {
    "connections": {
         "default": "postgres://username:password@host/db_name",
     
    },
    "apps": {
        "models": {
            "models": [
                "models.misc",
                "models", 
                "aerich.models"
            ],
            "default_connection": "default",
        }
    }
}

# TORTOISE = {
#     "connections": {
#         "default": {
#             "engine": "tortoise.backends.asyncpg",
#             "credentials": {
#                 "host": "host_address",
#                 "user": "username",
#                 "password": "password",
#                 "database": "db_name",
#                 "port": 5432,
#             }
#         }
#     },
#     "apps": {
#         "models": {
#             "models": [
#                 "models.misc",
#                 "models",
#                 "aerich.models"
#             ],
#             "default_connection": "default",
#         }
#     }
# }

EXTENSIONS = [
    "cogs.esports",
    "cogs.events",
    "cogs.mod",
    "cogs.premium",
    "cogs.quomisc",
    "cogs.reminder",
    "cogs.utility",
]


DISCORD_TOKEN = "..."


COLOR = 0x00FFB3
FOOTER = "Quotient Never Die!"
PREFIX = "q"
PRIME_EMOJI = "⚡"
OWNER_ID = "..."
DEVS = []

SERVER_LINK = "..."
SERVER_ID =  
TOURNEY_CSV_CHANNEL = 
EMOJIS_SERVER = [] #atleast 2 server id required...

BOT_INVITE = "...."

ACTIVITIES = [
    {"type": "playing", "name": "scrims across {servers} servers"},
    {"type": "listening", "name": "strategic calls from {members} players"},
    {"type": "watching", "name": "tournament brackets update in real time"},
    {"type": "competing", "name": "to lead the eSports automation arena"},
    {"type": "streaming", "name": "live event analytics", "url": "https://twitch.tv/Quotient"},
]
# ─────────────────────────────────────────────────────────────
#  Activity Placeholders (usable in "name" field)
#  These will automatically update with live bot stats.
#
#  Available Placeholders:
#    {servers}   → Total number of servers the bot is in
#    {members}   → Sum of all members across all servers
#    {msgs}      → Total messages seen since startup
#    {uptime}    → Current uptime in human-readable format
#    {cmds}      → Total commands executed since startup
#
#  Example:
#    {"type": "playing", "name": "serving {servers} communities"}
# ─────────────────────────────────────────────────────────────


# LOGS
SHARD_LOG = "..."
ERROR_LOG = "..."
PUBLIC_LOG = "..."



# IGNORE RIGHT NOW
WEBSITE = "https://github.com/CycloneAddons/Quotient-Legacy"
REPOSITORY = "https://github.com/CycloneAddons/Quotient-Legacy"
FASTAPI_URL = "https://i_will_tell_you_in_next_video"
FASTAPI_KEY ="i_will_tell_you_in_next_video"
