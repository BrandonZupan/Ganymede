"""
Miscellaneous commands and features that don't need their own cog
"""
from discord.ext import commands


class Miscellaneous(commands.Cog):
    """
    Holds misc commands and features
    """
    def __init__(self, bot: commands.Bot, reaction_channel):
        self.bot = bot
        self.reaction_channel = reaction_channel

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.id == self.reaction_channel:
            await ctx.add_reaction('👍')
            await ctx.add_reaction('👎')
            await ctx.add_reaction('🤷')

    @commands.command()
    async def hello(self, ctx):
        """
        Says hello
        """
        await ctx.send(f"Hello {ctx.author.display_name}!")
