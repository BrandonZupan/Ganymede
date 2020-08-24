import asyncio
import logging

import asyncpg
import discord
from discord.ext import commands

from helpers.checks import Checks
from helpers.config_loader import ConfigLoader

# Cogs
from cogs.command_database import CommandDatabase
from cogs.misc import Miscellaneous


logging.basicConfig(level=logging.INFO)

# Config
config_options = [
    "key",
    "prefix",
    "admin_role_ids",
    "reaction_channel",
    "postgres_username",
    "postgres_password",
    "postgres_db",
    "postgres_host"
]
config = ConfigLoader(config_options, "config.json")


async def run():
    # Database
    credentials = {
        "user": config.get_element("postgres_username"),
        "password": config.get_element("postgres_password"),
        "database": config.get_element("postgres_db"),
        "host": config.get_element("postgres_host")
    }
    try:
        db = await asyncpg.create_pool(**credentials)
    except asyncpg.InvalidCatalogNameError:
        # Create database
        sys_conn = await asyncpg.connect(
            database='template1',
            user='postgres',
            password=config.get_element("postgres_password")
        )
        await sys_conn.execute(
            f'CREATE DATABASE "{config.get_element("postgres_db")}" OWNER "{config.get_element("postgres_username")}"'

        )
        await sys_conn.close()

        db = await asyncpg.create_pool(**credentials)

    bot = Ganymede(command_prefix=config.get_element("prefix"), db=db)

    # Stop command
    @commands.command()
    async def stop(self, ctx):
        await db.close()
        await self.logout()

    # Setup classes
    Checks.config = config

    # Load cogs
    bot.add_cog(Miscellaneous(bot, config.get_element("reaction_channel")))

    command_db = CommandDatabase(bot, db)
    await command_db.setup()
    bot.add_cog(command_db)

    await bot.start(config.get_element("key"))


class Ganymede(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.db = kwargs.pop("db")

    async def on_disconnect(self):
        pass

    async def on_ready(self):
        logging.info(f"We have logged in as {self.user}")


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
