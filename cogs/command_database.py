"""
Database for storing commands
"""
import csv
import logging
import os

import asyncpg
import discord
from discord.ext import commands

from helpers.checks import Checks


class CommandDatabase(commands.Cog):
    """
    Handles the command database.

    Must call setup before using any other commands
    """

    def __init__(self, bot: commands.Bot, db):
        self.bot = bot
        self.db = db

        self.table = "commands"

    async def setup(self):
        await self.db.execute(
            "CREATE TABLE IF NOT EXISTS commands(command TEXT PRIMARY KEY, response TEXT, category TEXT)"
        )

    async def add_command(self, ctx, command, response, category):
        """
        Adds a command to the database

        :param ctx: Message context
        :param command: Name of command
        :param response: Response of command
        :param category: Category to add to
        """
        await self.db.execute(
            f"INSERT INTO {self.table} "
            f"(command, response, category) "
            f"VALUES ('{command}', '{response}', '{category}') "
            f"ON CONFLICT (command) DO UPDATE SET response = '{response}';"
        )
        await ctx.message.add_reaction('👌')
        logging.info(f"{ctx.author.name} added {command} with response {response} to {category}")

    async def delete_command(self, ctx, command):
        """
        Removes a command from the database

        :param ctx: Message context
        :param command: Command to remove
        """
        if await self.db.fetchrow(f"SELECT * FROM {self.table} where command = '{command}'") is not None:
            await self.db.execute(
                f"DELETE FROM {self.table} WHERE command = '{command}'"
            )
            await ctx.send(f"Deleted the command for `{command}`")
            logging.info(f"{ctx.author.name} deleted {command}")
        else:
            await ctx.send(f"Error: `{command}` is not a command")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def cc(self, ctx: commands.Context, command, *, response):
        """
        Modifies the command database

        List commands: !cc
        Modify or create a command: !cc <command_name> <response>
        Delete a command: !cc <command_name>
        Bot will confirm with :ok_hand:
        """
        # Add a command
        if not ctx.message.mention_everyone:
            category = "fun"
            await self.add_command(ctx, command, response, category)

        else:
            await ctx.send(f"Please do not add everyone or here to a command, {ctx.author}")

    @cc.error
    async def cc_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'command':
                # Output command list
                output = [""]
                i = 0
                for command in await self.db.fetch(f"SELECT command FROM {self.table}"):
                    if (int(len(output[i])/900)) == 1:
                        i = i + 1
                        output.append("")
                    output[i] += f"{command['command']} "

                i = 1
                for message in output:
                    embed = discord.Embed(
                        title=f'CC commands, pg {i}',
                        color=0xbf5700)
                    embed.add_field(
                        name='All CC commands, times out after 2 minutes',
                        value=message,
                        inline=False)
                    i += 1
                    await ctx.send(embed=embed, delete_after=120)

            elif error.param.name == "response":
                await self.delete_command(ctx, ctx.args[2])
        else:
            raise error

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def hc(self, ctx: commands.Context, command, *, response):
        """
        Modifies the command database

        List commands: !hc

        === Admin only ===
        Modify or create a command: !hc <command_name> <response>
        Delete a command: !hc <command_name>
        Bot will confirm with :ok_hand:
        """
        if await Checks.is_admin(ctx):
            if not ctx.message.mention_everyone:
                category = "help"
                await self.add_command(ctx, command, response, category)

            else:
                await ctx.send(f"Please do not add everyone or here to a command, {ctx.author}")

    @hc.error
    async def hc_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'command':
                # Output command list
                output = [""]
                i = 0
                for command in await self.db.fetch(f"SELECT command, category FROM {self.table}"):
                    if command['category'] == "help":
                        if (int(len(output[i]) / 900)) == 1:
                            i = i + 1
                            output.append("")
                        output[i] += f"{command['command']} "

                i = 1
                for message in output:
                    embed = discord.Embed(
                        title=f'Help commands, pg {i}',
                        color=0xbf5700)
                    embed.add_field(
                        name='All help commands, times out after 2 minutes',
                        value=message,
                        inline=False)
                    i += 1
                    await ctx.send(embed=embed, delete_after=120)

            elif error.param.name == 'response':
                if await Checks.is_admin(ctx):
                    await self.delete_command(ctx, ctx.args[2])

        else:
            raise error

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def cc_db(self, ctx, *, query):
        """
        Provides direct access to database
        """
        await self.db.execute(query)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            # Get first word in command and remove prefix from it
            command = ctx.message.content.split(" ", 1)[0][1:]

            response = await self.db.fetchrow(f"SELECT * FROM {self.table} where command = '{command}'")
            if response is not None:
                await ctx.send(response['response'])
                return

        raise error

    @commands.command(name="cc-to-csv")
    @commands.check(Checks.is_admin)
    async def cc_to_csv(self, ctx):
        """
        Generates a CSV of the command database
        """
        with open('cc.csv', 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            for command in await self.db.fetch(f"SELECT * FROM {self.table}"):
                csv_writer.writerow([command["category"], command["command"], command["response"]])

        await ctx.send(file=discord.File('cc.csv'))
        os.remove('cc.csv')

    @commands.command(name="cc-import-csv", hidden=True)
    @commands.check(Checks.is_admin)
    async def cc_import_csv(self, ctx, filename):
        """
        Imports a csv file full of commands

        Usage: !import-csv filename.csv
        Note: File path is relative to server instance

        File Format:
        [category], [name], [responce]
        """
        try:
            with open(filename, 'r', newline='') as csv_file:
                reader = csv.reader(csv_file)
                commands_added = 0
                for row in reader:
                    print(row)
                    await self.add_command(ctx, row[1], row[2], row[0])
                    commands_added += 1

                await ctx.send(f'Added {commands_added} commands to database')

        except Exception as oof:
            await ctx.send("Something went wrong with import, check log for details")
            raise oof
