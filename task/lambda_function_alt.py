# Sources: https://realpython.com/how-to-make-a-discord-bot-python/
# https://discordpy.readthedocs.io/en/stable/quickstart.html

import os
import sys

sys.path.append('discord')
import discord

# Discord bot's token
# stored as the Lambda function's environment variable
BOT_TOKEN = os.environ['BOT_TOKEN']

client = discord.Client()

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    # client.user.name

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

def lambda_handler(event, context):
    client.run(BOT_TOKEN)
