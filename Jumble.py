import os
import json
import discord
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

discordClient = discord.Client() 


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
        'attachmentUrls': attachment_urls,
    }

    print(data)



discordClient.run(DISCORD_TOKEN)