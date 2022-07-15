import os
import sys

sys.path.append('lib')
import discord
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGODB_URI')
BOT_CHANNEL_ID = os.getenv('BOT_CHANNEL_ID')

discordClient = discord.Client() 
mongoClient = MongoClient(MONGO_URI)

db = mongoClient.JumbleDB
postsCollection = db.Posts

@discordClient.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discordClient))

@discordClient.event
async def on_message(message):
    if message.channel.id != int(BOT_CHANNEL_ID):
        print("Message sent in channel the bot mustn't forward posts from")
        return
    
    attachment_urls = []
    for attachment in message.attachments:
        attachment_urls.append(attachment.url)

    postData = {
        'message_id': message.id,
        'message_author': message.author.display_name.rsplit('#', 1)[0],
        'author_avatar_url': str(message.author.avatar_url),
        'date': message.created_at.strftime('%B %d, %Y'),
        'message_text': message.clean_content,
        'attachment_urls': attachment_urls,
    }

    if message.webhook_id:
        print(postData)
        postsCollection.insert_one(postData)
    else:
        print(
            "Message has no webhook ID, so not from a followed announcements channel."
            " postData:\n{0}".format(postData))

discordClient.run(DISCORD_TOKEN)
