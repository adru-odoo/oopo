import discord
from discord import option
from discord.ext import commands
import emoji


class Guild():
    def __init__(self, guild: discord.guild):
        self.guild = guild
        self.reaction_messages = {}
        self.ids = {}

    def check_message(self, name: str):
        return self.reaction_messages.get(name)

    def check_message_id(self, mid):
        return self.reaction_messages.get(self.ids.get(mid))

    def add_message(self, message: discord.message, name: str):
        self.ids[message.id] = name
        self.reaction_messages[name] = Message(message, name)


class Message():
    def __init__(self, message: discord.message, name: str):
        self.message = message
        self.rules = {}

    def add_rule(self, role: discord.role, reaction: str):
        self.rules[reaction] = Rule(role, reaction)

    def check_rule(self, reaction: str):
        return self.rules.get(reaction)


class Rule():
    def __init__(self, role: discord.role, reaction: str):
        self.role = role
        self.reaction = reaction

    def get_role(self):
        return self.role


class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allguilds = {}

    @commands.slash_command(name="create_role_message", description="Create a reaction role message")
    @option(
        "channel",
        discord.TextChannel,
        description="Select a channel"
    )
    async def create_role_message(self, ctx, name: str, channel: discord.TextChannel):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("Sorry, only Administrators can use this commmand.\n")
            return
        reaction_messages = self.allguilds.get(ctx.guild_id)
        if not reaction_messages:
            self.allguilds[ctx.guild_id] = reaction_messages = Guild(ctx.guild)
        reaction_messages.add_message(await channel.send(f"**{name}** Role Menu\nReact to give yourself roles."), name)
        await ctx.respond(f"Reaction role message `{name}` sent.")

    @commands.slash_command(name="register_reaction_role", description="Register a reaction role")
    @option(
        "role",
        discord.Role,
        description="Role to assign"
    )
    async def register_reaction_role(self, ctx, name: str, role: discord.Role, reaction):
        if not ctx.author.guild_permissions.administrator:
            await ctx.respond("Sorry, only Administrators can use this commmand.\n")
            return
        if not (bool(re.fullmatch(r"<:.*:[0-9]*>", reaction)) or len(emoji.emoji_list(reaction)) == 1):
            await ctx.respond(f"{reaction} is not a valid emoji")
            return
        reaction_messages = self.allguilds.get(ctx.guild_id)
        if not reaction_messages:
            await ctx.respond("no reaction messages for this server, please create one")
            return
        reaction_message = reaction_messages.check_message(name)
        if not reaction_message:
            await ctx.respond(f"no reaction message found by the name {name}")
            return
        reaction_message.message.content += f"\n\n{reaction}: `{role.name}`"
        await reaction_message.message.edit(content=reaction_message.message.content)
        await reaction_message.message.add_reaction(reaction)
        await ctx.respond("Reaction Role Created")
        reaction_message.add_rule(role, reaction)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        reaction_messages = self.allguilds.get(payload.guild_id)
        rmsg = reaction_messages.check_message_id(payload.message_id)
        if not rmsg:
            return
        if payload.emoji.is_unicode_emoji():
            rule = rmsg.check_rule(payload.emoji.name)
        else:
            rule = rmsg.check_rule(f"<:{payload.emoji.name}:{payload.emoji.id}>")
        if not rule:
            # i know elizabeth asked me to handle this case but man i really dont wanna right now
            return
        await payload.member.add_roles(rule.role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        reaction_messages = self.allguilds.get(payload.guild_id)
        rmsg = reaction_messages.check_message_id(payload.message_id)
        if not rmsg:
            return
        if payload.emoji.is_unicode_emoji():
            rule = rmsg.check_rule(payload.emoji.name)
        else:
            rule = rmsg.check_rule(f"<:{payload.emoji.name}:{payload.emoji.id}>")
        if not rule:
            return
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        await member.remove_roles(rule.role)


