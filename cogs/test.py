"""
Test extension
"""

import discord
from discord.ext import commands


def setup(bot):
    bot.add_cog(TestCog(bot))


class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Fuck them kids")
