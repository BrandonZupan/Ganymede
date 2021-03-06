"""
Miscellaneous commands and features that don't need their own cog
"""
from discord.ext import commands
import discord


class Miscellaneous(commands.Cog):
    """
    Holds misc commands and features
    """
    def __init__(self, bot: commands.Bot, reaction_channel, access_roles, welcome_channel):
        self.bot = bot
        self.reaction_channel = reaction_channel
        self.access_roles = access_roles
        self.welcome_channel = welcome_channel

    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.id == self.reaction_channel:
            await ctx.add_reaction('👍')
            await ctx.add_reaction('👎')
            await ctx.add_reaction('🤷')

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        # Find new role
        # if it exists, see if it is in the list of access roles
        # if it is, send welcome message
        new_role = list(set(after.roles) - set(before.roles))
        # print(new_role)

        if not new_role:
            return
        if new_role[0].id not in self.access_roles:
            return

        # See if this is there only role. If it isn't then don't send message
#         if len(after.roles) == 2:
        if True:
            channel = self.bot.get_channel(self.welcome_channel)
            await channel.send(f"Howdy {after.mention}! Be sure to introduce yourself!")

    @commands.command()
    async def hello(self, ctx):
        """
        Says hello
        """
        await ctx.send(f"Hello {ctx.author.display_name}!")
