# ACM x Jumble

https://discord.com/developers/docs/resources/channel#get-channel-messages


## Create the Discord bot

https://discord.com/developers/docs/intro

1. Create the [team](https://discord.com/developers/docs/topics/teams)
    - Visit https://discord.com/developers/teams
    - Click **[New Team]**

2. Create the [app](https://discord.com/developers/docs/intro#bots-and-apps)
    - Visit https://discord.com/developers/applications
    - Click **[New application]**
    - Choose the team you created (not your personal team)

3. Choose permissions
    - **"OAuth2"** > **"General"** > **"Default Authorization Link"**
    - Under **"Authorization Method"**, choose `In-app Authorization`
    - Under **"Scopes"**, check `bot`
    - Under **"Bot Permissions"**, check `Read Messages/View Channels`
    - TODO Add any other permissions and their purposes as development progresses

<!---
3. Create the invite link
    - TODO What's the difference between the default authorization link
    - **"OAuth2"** > **"URL Generator"**
    - Choose [permissions](https://discord.com/developers/docs/topics/oauth2#oauth2):
        - messages.read
-->


## Repo conventions

Branch naming convention
- `bot/STA-#/description`
- Example: `bot/STA-7/get-announcement-data`
