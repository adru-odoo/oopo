import discord
import os
from dotenv import load_dotenv
from email_cog import Email
from reaction_cog import ReactionRoles
from message_cog import MessageSend

load_dotenv()
intents = discord.Intents.default()
intents.members = True

oopo = discord.Bot(intents=intents)
oopo.add_cog(Email(oopo))
oopo.add_cog(ReactionRoles(oopo))
oopo.add_cog(MessageSend(oopo))
oopo.run(os.getenv("PASS"))
print('Oopo Started')
