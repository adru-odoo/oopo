import discord
from discord import option
from discord.ext import commands


class MessageSend(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allguilds = {}

    @commands.slash_command(name="send", description="Send a message")
    @option(
        "channel",
        discord.TextChannel,
        description="Select a channel"
    )
    async def create_role_message(self, ctx, message: str, channel: discord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("Sorry, only Administrators can use this commmand.\n")
            return
        await channel.send(message)
        await ctx.respond("Okay!")
