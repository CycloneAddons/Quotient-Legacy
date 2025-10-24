from typing import List

import discord

import config
from models import PremiumPlan, PremiumTxn
from utils import emote


class DonateBtn(discord.ui.Button):
    def __init__(self, label="❤️ Support Us", url="https://test.com", style=discord.ButtonStyle.url):
        super().__init__(label=label, style=style, url=url)


class LegacyView(discord.ui.View):
    def __init__(self, text="This feature is available in Quotient Legacy for free!"):
        super().__init__(timeout=None)
        self.text = text
        # Add the donate button
        self.add_item(DonateBtn())

    @property
    def legacy_embed(self) -> discord.Embed:
        _e = discord.Embed(color=0x00FFB3)
        _e.title = "💎 Welcome to Quotient Legacy!"
        _e.description = (
            "__**Perks you get with Quotient Legacy (completely FREE!)**__\n\n"
            f"{emote.white_arrow} Access to `Quotient Legacy` bot.\n"
            f"{emote.white_arrow} Unlimited Scrims.\n"
            f"{emote.white_arrow} Unlimited Tournaments.\n"
            f"{emote.white_arrow} Custom Reactions for Regs.\n"
            f"{emote.white_arrow} Smart SSverification.\n"
            f"{emote.white_arrow} Cancel-Claim Panel.\n"
            f"{emote.white_arrow} Premium Role + more...\n\n"
            "_We provide this for free to honor the memory of Rohit, the original creator of Quotient. "
            "If you love what we do and want to support us to keep this alive, you can donate using the button below._"
        )
        _e.set_footer(text="Thank you for being part of the Quotient Legacy community ❤️")
        return _e
