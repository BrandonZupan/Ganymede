"""
Functions/decorators for checking permissions
"""
import discord

from helpers.config_loader import ConfigLoader


class Checks:
    """
    Class for holding check functions
    """
    config = None

    @staticmethod
    async def is_admin(ctx):
        """Checks if the user has an admin role"""
        for role in Checks.config.get_element("admin_role_ids"):
            test_role = discord.utils.get(ctx.guild.roles, id=role)
            if test_role in ctx.author.roles:
                return True

        return False
