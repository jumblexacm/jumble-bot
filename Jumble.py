import os
import discord
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
MONGO_URI = os.getenv('MONGODB_URI')

discordClient = discord.Client() 
mongoClient = MongoClient(MONGO_URI)

db = mongoClient.JumbleDB
postsCollection = db.Posts

@discordClient.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discordClient))

@discordClient.event
async def on_message(message):
    attachment_urls = []
    for attachment in message.attachments:
        attachment_urls.append(attachment.url)

    postData = {
        'message_author': message.author.display_name.rsplit('#', 1)[0],
        'author_avatar_url': str(message.author.avatar_url),
        'date': message.created_at.strftime('%B %d, %Y'),
        'message_text': message.clean_content,
        'attachment_urls': attachment_urls,
    }

    #print(postData)
    postsCollection.insert_one(postData)



discordClient.run(DISCORD_TOKEN)