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


# LOGS
SHARD_LOG = "..."
ERROR_LOG = "..."
PUBLIC_LOG = "..."



# IGNORE RIGHT NOW
WEBSITE = "https://github.com/CycloneAddons/Quotient-Legacy"
REPOSITORY = "https://github.com/CycloneAddons/Quotient-Legacy"
FASTAPI_URL = "https://i_will_tell_you_in_next_video"
FASTAPI_KEY ="i_will_tell_you_in_next_video"