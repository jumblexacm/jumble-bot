# ACM x Jumble


## Prerequisites

- Discord account

- Discord server (your "dev server")

- Heroku CLI


## STEP 1: Create the Discord bot

https://discord.com/developers/docs/intro

1. Create the [team](https://discord.com/developers/docs/topics/teams)
    - Visit https://discord.com/developers/teams
    - Click **[New Team]**
    - To add the other engineers, open the new team and **"Invite team members"**

2. Create the [app](https://discord.com/developers/docs/intro#bots-and-apps)
    - Visit https://discord.com/developers/applications
    - Click **[New application]**
    - Choose your team from earlier (not your personal team)

3. Add the redirect URI
    - Menu section: **"Oauth2"**
    - Click **[Add Redirect]**
    - Input your app's about page or another URL for the user to see after installing your app

3. Create the bot  
(As far as [@kirmar](https://github.com/kirmar) can tell, the app must have a bot user to join a server / read any messages.)
    - Menu section: **"Bot"**
    - Click **[Add Bot]**
    - Under **"Privileged Gateway Intents"**, check `Message Content Intent`

4. Generate the invite URL
    - Menu section: **"OAuth2"** > **"URL Generator"**
    - Choose [permissions](https://discord.com/developers/docs/topics/oauth2#oauth2):
        - Under **"Scopes"**, check `bot`
        - Under **"Bot Permissions"**, check `Read Messages/View Channels`
    - As your redirect URL, choose your redirect URI from earlier
    - Copy the generated URL, because it disappears if you navigate away from the page. This URL lets you add the bot to a server, for now your dev server.


## STEP 2: Create a test student org server

1. In Discord, click **[Add a Server]** and follow the steps

2. Under **"Server Settings"** > **"Enable Community"**, click **[Get Started]** and follow the steps

3. Click the plus symbol to **"Create Channel"**, check `Announcement`, and create the channel

4. Next to the new channel name, click **"Follow"** and choose your dev server where you installed the bot

Notes about community servers:
- For a message to appear in the dev server, the person posting in the student org server must send the message *and* click "Publish."
- When someone edits the message in the student org server, it also updates in the dev server.


## STEP 3: Set up the Heroku app

1. Create the Heroku app

2. Connect the Heroku app to GitHub
    - Click **"Deploy"**
    - Under **"Deployment method"**, connect the app to your GitHub account
    - Choose the repo where you store your Heroku app's code
    - Under **"Manual deploy"**, choose your "branch to deploy"

TODO Add any other steps that Cannon followed


## STEP 4: Deploy to Heroku

1. In your terminal, `git push` your "branch to deploy"

2. Under **"Manual deploy"**, click **[Deploy Branch]**

3. On the first deployment only, [scale the number of worker dynos](https://devcenter.heroku.com/articles/background-jobs-queueing)
    - In your terminal:

          heroku ps:scale worker=1


## Resources

https://discord.com/developers/docs/resources/channel#get-channel-messages

https://github.com/kkrypt0nn/Python-Discord-Bot-Template


## Repo conventions

Branch naming convention
- `<team>/<trello-task>/<description>`
- Example: `bot/STA-7/get-announcement-data`

Pull request (PR) conventions
- At the top of the description, include the Trello ticket:

      [STA-10](link)
      This ticket entails...

- PRs aren't needed for README updates. (Commit directly to `main`)
