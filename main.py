import os
import sys

sys.path.append('lib/')
import discord
from pymongo import MongoClient

try:
    # Import config vars on Heroku
    DISCORD_TOKEN = process.env.DISCORD_TOKEN
    MONGODB_URI = process.env.MONGODB_URI
    MONGODB_DB = process.env.MONGODB_DB
    BOT_CHANNEL_ID = process.env.BOT_CHANNEL_ID
except NameError as e:
    if str(e) != "name 'process' is not defined":
        raise
    try:
        # Import environment vars from .env on local machine
        DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
        MONGODB_URI = os.environ['MONGODB_URI']
        MONGODB_DB = os.environ['MONGODB_DB']
        BOT_CHANNEL_ID = os.environ['BOT_CHANNEL_ID']
    except KeyError:
        print(f"os.environ keys: {sorted(list(os.environ.keys()))}")
        raise

discord_client = discord.Client()
mongo_client = MongoClient(MONGODB_URI)

db = mongo_client[MONGODB_DB]
posts_collection = db.Posts
orgs_collection = db.Orgs

def get_post_data(message):
    attachment_urls = [attachment.url for attachment in message.attachments]
    return {
        'org_id': str(message.author.id),
            # Without `str()`, `org_id` is too large for a JavaScript int
            # TODO: `author.id` really identifies a specific followed
            # channel, not a community server as a whole. If possible,
            # access the Channel Follower Webhook's source guild.
            # More here: https://discord.com/channels/992524047084687461/992524799060496576/997615364462624779
        'message_id': message.id,
        'message_author': message.author.display_name.rsplit(' #', 1)[0],
        'author_avatar_url': str(message.author.avatar_url),
        'date': message.created_at.strftime("%B %d, %Y"),
        'message_text': message.clean_content,
        'attachment_urls': attachment_urls,
    }

def get_org_data(post_data, most_recent_post_date):
    org_id = post_data['org_id']
    org_data = {
        'org_id': org_id,
        'org_name': post_data['message_author'],
        'org_avatar_url': post_data['author_avatar_url'],
        'org_description': "",
        'org_links': [],
        'recency': most_recent_post_date
    }
    return (org_id, org_data)

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
    print()
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
    if not from_followed_channel(
        message, post_data, processing=f"forwarding (to `{MONGODB_DB}`)"):
        return
    posts_collection.insert_one(post_data)
    most_recent_post_date = message.created_at
    org_id, org_data = get_org_data(post_data, most_recent_post_date)
    updated_org = orgs_collection.find_one_and_update(
        { 'org_id': org_id },
        { '$set': { 'recency': most_recent_post_date } })
    if not updated_org:
        orgs_collection.insert_one(org_data)

# Note: An 'on_raw' function is called even if the message was
# originally sent before this `discord.Client()`'s lifetime / during a
# previous Heroku "session."
@discord_client.event
async def on_raw_message_edit(payload):
    message_id = payload.message_id
    
    # Do NOT use `payload.cached_message`; it's the unedited message
    # and also is None if the message was sent before this
    # `discord.Client()`'s lifetime.
    channel = discord_client.get_channel(payload.channel_id)
    message = await channel.fetch_message(message_id)
    
    post_data = get_post_data(message)
    
    if post_data['message_text'] == "[Original Message Deleted]":
        # Really a delete, not an edit
        if payload.cached_message:
            message = payload.cached_message
            post_data = get_post_data(message)
        if not from_followed_channel(
            message, post_data, processing="deleting"):
            return
        posts_collection.delete_one({ 'message_id': message_id })
    else:
        # Really, truly an edit
        if not from_followed_channel(message, post_data, processing="editing"):
            return
        posts_collection.update_one(
            { 'message_id': message_id },
            { '$set': post_data })

@discord_client.event
async def on_raw_message_delete(payload):
    message_id = payload.message_id
    
    # Do NOT use `channel.fetch_message()`; it raises a
    # "discord.errors.NotFound: ... Unknown Message"
    # because the message was deleted.
    message = payload.cached_message
    
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
        print()
        print(
            "Message may or may not be from a followed announcements channel."
            "\n   Bot is attempting to delete message."
            f"   message_id: {message_id}")
    
    posts_collection.delete_one({ 'message_id': message_id })

discord_client.run(DISCORD_TOKEN)
