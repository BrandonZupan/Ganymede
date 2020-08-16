import logging

import discord
from discord.ext import commands

from helpers.config_loader import ConfigLoader
from emojibot import emojiPicker


logging.basicConfig(level=logging.INFO)

bot = commands.Bot(command_prefix="~")

config_options = [
    "key"
]
config = ConfigLoader(config_options, "config.json")


@bot.event
async def on_ready():
    logging.info(f"We have logged in as {bot.user}")


bot.load_extension("extensions.test")

print(emojiPicker.__doc__)


bot.run(config.get_element("key"))
