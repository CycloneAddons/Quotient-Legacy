from __future__ import annotations

import discord

from constants import SSType
from utils import BaseSelector, emote


class SStypeSelector(discord.ui.Select):
    view: BaseSelector

    def __init__(self):
        super().__init__(
            placeholder="Select the type of screenshots ... ",
            options=[
                discord.SelectOption(
                    label="Youtube",
                    emoji=emote.youtube,
                    value=SSType.yt.value,
                    description="Youtube Channel Screenshots",
                ),
                discord.SelectOption(
                    label="Instagram",
                    emoji=emote.instagram,
                    value=SSType.insta.value,
                    description="Instagram Screenshots (Premium only)",
                ),
                discord.SelectOption(
                    label="Rooter",
                    emoji=emote.rooter,
                    value=SSType.rooter.value,
                    description="Rooter Screenshots (Premium only)",
                ),
                discord.SelectOption(
                    label="Loco",
                    emoji=emote.loco,
                    value=SSType.loco.value,
                    description="Loco Screenshots (Premium only)",
                ),
                discord.SelectOption(
                    label="Any SS",
                    emoji=emote.hehe,
                    value=SSType.anyss.value,
                    description="Verify any Image (Premium only)",
                ),
                discord.SelectOption(
                    label="Create Custom Filter",
                    emoji=emote.rooCoder,
                    value=SSType.custom.value,
                    description="For anything like app installation, any mobile app,etc.",
                ),
            ],
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        self.view.stop()
        self.view.custom_id = interaction.data["values"][0]
