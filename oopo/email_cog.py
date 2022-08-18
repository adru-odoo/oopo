from discord.ext import commands
import smtplib
import random
import ssl
import re
from email.message import EmailMessage
import pymongo


class Email(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        client = pymongo.MongoClient('mongo', 27017)
        db = client.emaildb
        self.messaged_users = db.messaged
        self.emailed_users = db.emailed
        self.verified_users = db.verified
        self.sender = 'adru@odoo.com'
        self.password = 'gtkktqawfhactgjj'
        self.context = ssl.create_default_context()

    def is_odoo_email(self, string):
        return bool(re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", string)) and string.endswith('@odoo.com')

    def is_email(self, string):
        return bool(re.fullmatch(r"[\w.+-]+@[\w-]+\.[\w.-]+", string))

    def verify_user(self, user):
        print(user)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.messaged_users.insert_one({
            "member_id": member.id,
            "code": random.randrange(111111, 9999999)
        })
        await member.send("""
Hey! We can't wait to give you access to the server. First things first, let's verify your odoo email.
You can enter your odoo quadgram or your odoo email address to do so.
""")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id or message.guild:
            return
        messaged_user = self.messaged_users.find_one({'member_id': message.author.id})
        emailed_user = self.emailed_users.find_one({'member_id': message.author.id})
        if messaged_user:
            if (3 <= len(message.content) <= 4) or self.is_odoo_email(message.content):
                email = EmailMessage()
                email['From'] = self.sender
                to = message.content
                if not self.is_odoo_email(to):
                    to = to + "@odoo.com"
                email['To'] = to
                email['Subject'] = 'Verify your Odoo Discord Account'
                code = messaged_user['code']
                email.set_content(f'Here is your one-time code to verify your discord account.\n{code}')
                self.emailed_users.insert_one(messaged_user)
                self.messaged_users.delete_one({'member_id': message.author.id})
                with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=self.context) as smtp:
                    smtp.login(self.sender, self.password)
                    smtp.sendmail(self.sender, to, email.as_string())
                await message.author.send("Thank you! Now, please tell me the one-time code you recieved in your email.")
            else:
                await message.author.send("Please provide a valid gram or @odoo.com email address.")
        elif emailed_user:
            if message.content.isdigit and int(message.content) == emailed_user['code']:
                self.emailed_users.delete_one({'member_id': message.author.id})
                self.verify_user(message.author.id)
                await message.author.send("Thank you. Your account is now verified.")
            else:
                await message.author.send("Sorry, your one-time code is incorrect. Please try again.")
