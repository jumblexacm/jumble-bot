import os
import sys

sys.path.append('lib/')
import discord
from pymongo import MongoClient

try:
    # Import config vars on Heroku
    DISCORD_TOKEN = process.env.DISCORD_TOKEN
    MONGODB_URI = process.env.MONGODB_URI
except NameError as e:
    if str(e) != "name 'process' is not defined":
        raise
    try:
        # Import environment vars from .env on local machine
        DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
        MONGODB_URI = os.environ['MONGODB_URI']
        BOT_CHANNEL_ID = os.environ['BOT_CHANNEL_ID']
    except KeyError:
        print(f"os.environ keys: {sorted(list(os.environ.keys()))}")
        raise

discord_client = discord.Client()
mongo_client = MongoClient(MONGODB_URI)

db = mongo_client.JumbleDB
posts_collection = db.Posts

def get_post_data(message):
    attachment_urls = [attachment.url for attachment in message.attachments]
    return {
        'message_id': message.id,
        'message_author': message.author.display_name.rsplit("#", 1)[0],
        'author_avatar_url': str(message.author.avatar_url),
        'date': message.created_at.strftime("%B %d, %Y"),
        'message_text': message.clean_content,
        'attachment_urls': attachment_urls,
    }

@discord_client.event
async def on_ready():
    print(f"We have logged in as @{discord_client.user}")

@discord_client.event
async def on_message(message):
    if message.channel.id != int(BOT_CHANNEL_ID):
        print("Message sent in a channel that bot mustn't forward posts from.")
        return
    
    post_data = get_post_data(message)
    if message.webhook_id:
        print(
            "Message from a followed channel, so bot is forwarding to MongoDB."
            f"   post_data: {post_data}")
        posts_collection.insert_one(post_data)
    else:
        print(
            "Message has no webhook ID,"
            " so not from a followed announcements channel."
            f"   post_data: {post_data}")

discord_client.run(DISCORD_TOKEN)
