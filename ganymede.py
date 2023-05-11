#!/usr/bin/python3
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
from cogs.goofystreak import GoofyStreak

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
    "postgres_host",
    "server_access_roles",
    "welcome_channel",
    "edit_delete_channel",
    "speedway_channel_id",
    "goofy_emote_id",
    "goofy_streak_filepath"
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
    except ConnectionRefusedError:
        # If no database is installed, set db to none
        logging.error("Could not connect to database. Database command will not work")
        db = None

    # Intents
    intents = discord.Intents(members=True, messages=True, guilds=True)

    bot = Ganymede(command_prefix=config.get_element("prefix"), intents=intents, db=db)

    # Setup classes
    Checks.config = config

    # Load cogs
    misc = Miscellaneous(bot,
                         config.get_element("reaction_channel"),
                         config.get_element("server_access_roles"),
                         config.get_element("welcome_channel"),
                         config.get_element("edit_delete_channel"))
    bot.add_cog(misc)

    # misc.get_weather.start()

    command_db = CommandDatabase(bot, db)
    await command_db.setup()
    bot.add_cog(command_db)

    gs = GoofyStreak(bot,
                     config.get_element("speedway_channel_id"),
                     config.get_element("goofy_emote_id"),
                     config.get_element("goofy_streak_filepath"))
    bot.add_cog(gs)

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
