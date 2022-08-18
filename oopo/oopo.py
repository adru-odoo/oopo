import discord
import os
from dotenv import load_dotenv
from email_cog import Email
from reaction_cog import ReactionRoles

load_dotenv()
intents = discord.Intents.default()
intents.members = True

oopo = discord.Bot(intents=intents)
oopo.add_cog(Email(oopo))
oopo.add_cog(ReactionRoles(oopo))
oopo.run(os.getenv("PASS"))
print('Oopo Started')
