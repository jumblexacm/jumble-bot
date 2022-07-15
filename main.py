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

def in_correct_channel(message):
    """Verify message is from bot's assigned "to-watch" channel."""
    if message.channel.id != int(BOT_CHANNEL_ID):
        print("Message from a channel that bot isn't assigned to watch.")
        return False
    return True

def from_webhook(message):
    """Verify message is from a webhook.
    Note: The message may or may not be
    from a Channel Follower Webhook."""
    if not message.webhook_id:
        print(
            "Message has no webhook ID,"
            " so not from a followed announcements channel.")
        return False
    return True

def from_followed_channel(message, post_data, processing="processing"):
    success = in_correct_channel(message) and from_webhook(message)
    if success:
        print(
            "Message from a followed announcements channel." # probably :)
            f"\n   Bot is {processing} message.")
    else:
        print(f"   Bot is not {processing} message.")
    if post_data:
        print(f"   post_data: {post_data}")
    return success

@discord_client.event
async def on_ready():
    print(f"We have logged in as @{discord_client.user}")

@discord_client.event
async def on_message(message):
    post_data = get_post_data(message)
    if not from_followed_channel(message, post_data, processing="forwarding"):
        return
    posts_collection.insert_one(post_data)

@discord_client.event
async def on_message_edit(before, after):
    # TODO Should this be on_raw_message_edit()?
    raise Exception("Not yet implemented")

# @discord_client.event
# async def on_message_delete(message):
#     """When a followed announcement is deleted, delete it in MongoDB.
#     Note that this function is called only if the deleted message was
#     originally sent during this `discord_client`'s lifetime / during
#     the current Heroku "session.""""
#     # TODO Get `on_message_delete()` for messages that were sent
#     # in a previous app/bot run session
#     post_data = get_post_data(message)
#     if not from_followed_channel(message, post_data, processing="deleting"):
#         return
#     posts_collection.delete_one({ 'message_id': message.id })

@discord_client.event
async def on_raw_message_delete(payload):
    """When any message is deleted, try to delete it in MongoDB.
    This function is called even if the deleted message was
    originally sent before this `discord_client`'s lifetime / during a
    previous Heroku "session." However, it tries to delete a MongoDB
    document no matter what and doesn't check the channel/webhook IDs."""
    
    # Only for Users, not Clients:
    # message = await discord_client.get_message(payload.message_id)
    
    # "ValueError: <id> is not in deque"
    # message = discord_client.cached_messages[discord_client.cached_messages.index(payload.message_id)]
    
    # "discord.errors.NotFound: 404 Not Found (error code: 10008): Unknown Message"
    # "Read Message History" and "Manage Messages" don't seem to help
    # channel = discord_client.get_channel(payload.channel_id)
    # message = await channel.fetch_message(payload.message_id)
    
    message = payload.cached_message
    message_id = payload.message_id
    
    if message:
        post_data = get_post_data(message)
        if not from_followed_channel(
            message, post_data, processing="deleting"):
            return
    else:
        # If message was sent before this `discord_client`'s lifetime,
        # then `message` is None. Just spend some extra effort trying
        # to delete a possibly-nonexistent document from MongoDB.
        # Source: https://stackoverflow.com/a/64227013
        print(
            "Message may or may not be from a followed announcements channel."
            "\n   Bot is attempting to delete message."
            f"   message_id: {message_id}")
    
    posts_collection.delete_one({ 'message_id': message_id })

discord_client.run(DISCORD_TOKEN)
