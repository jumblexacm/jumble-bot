# ACM x Jumble


## Prerequisites

- Discord account

- Discord server (your "dev server")

- MongoDB Atlas database

- Heroku account and Heroku CLI

- Python 3 (with `pip`)


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

5. Activate the bot
    - Use the generated URL to invite the bot to your dev server
    - If the channel where you want the bot to listen is private, be sure to give the bot access
    - Hide all other channels from the bot, otherwise it may add their messages to MongoDB


## STEP 2: Create a test student org server

1. In Discord, click **[Add a Server]** and follow the steps

2. Under **"Server Settings"** > **"Enable Community"**, click **[Get Started]** and follow the steps

3. Click the plus symbol to **"Create Channel"**, check `Announcement`, and create the channel

4. Next to the new channel name, click **"Follow"** and choose your dev server where you installed the bot

5. Consider creating another Discord app/bot, student org server, and dev server as your dev environment.

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

3. Generate the MongoDB URI
    - Create a [DNS-constructed seed list connection string](https://www.mongodb.com/docs/manual/reference/connection-string/#dns-seed-list-connection-format)
    - TODO Let Nick make this step more clear/thorough

4. Generate the Discord bot token
    - Open your Discord app in the Discord Developer Portal
    - Menu section: **"Bot"**
    - Under **"Build-A-Bot"**, click `Reset Token` and copy it to somewhere safe

Note: When storing secrets, please use the Heroku Dashboard, not the CLI. Using the Heroku Dashboard prevents secrets from being stored in your terminal history.

5. Store secrets as [config vars](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard), like environment variables
    - In the Heroku Dashboard, click **"Settings"**
    - Under **"Config Vars"**, click **[Reveal Config Vars]**
    - Add the first config var:
        - KEY: `MONGODB_URI`
        - VALUE: *[Input the MongoDB URI]*
    - Add the second config var:
        - KEY: `DISCORD_TOKEN`
        - VALUE: *[Input the Discord bot token]*

6. Let Heroku access MongoDB
    - In MongoDB Atlas, click **"Network Access"**
    - Click **[Add IP address]**
    - Access List Entry: `0.0.0.0/0`
    - Comment: `All IP addresses so Heroku can access (unsafe, so try to find another solution)`
    - TODO Find a safer solution, like using a Heroku [add-on](https://www.mongodb.com/developer/products/atlas/use-atlas-on-heroku/#configuring-heroku-ip-addresses-in-mongodb-atlas) that creates a static IP address


## STEP 4: Set up your Heroku CLI and local environment

1. Set your `$HEROKU_APP_NAME` environment variable
    - In your terminal, run:
          
          HEROKU_APP_NAME=*<the name of your Heroku app as displayed in the Heroku Dashboard>*
          echo $HEROKU_APP_NAME # Confirm it's set to the correct name

2. Store secrets in `.env`
    - In your terminal, run:
          
          heroku config:get MONGODB_URI -s -a $HEROKU_APP_NAME >> .env
    
    - Then set `DISCORD_TOKEN` to your dev environment Discord bot's token OR run:
          
          heroku config:get DISCORD_TOKEN -s -a $HEROKU_APP_NAME >> .env


## STEP 5: Test the app on your local machine

1. Start the app
    - In your terminal, run:
    
          heroku local
          # TODO Should this be `heroku local worker=1`?

2. Note that as far as [@kirmar](https://github.com/kirmar) can tell, the terminal doesn't output "We have logged in as..." until you \<Ctrl+C>
    - TODO Is there a way to print everything immediately?

3. Post and publish a message in your test community server

4. See the new document in MongoDB :)

5. When you're done testing, \<Ctrl+C>


## STEP 6: Deploy to Heroku and test the app

1. In your terminal, `git push` your "branch to deploy"

2. Under **"Manual deploy"**, click **[Deploy Branch]**

3. On the first deployment only, [scale the number of worker dynos](https://devcenter.heroku.com/articles/background-jobs-queueing)
    - In your terminal, run:

          heroku ps:scale worker=1 -a $HEROKU_APP_NAME

4. After Heroku finishes deploying, try publishing an announcement in Discord, check MongoDB, and (if it's not working) view your Heroku logs
    - In your terminal, run:
    
          heroku logs --tail -a $HEROKU_APP_NAME


## Repo conventions

Branch naming convention
- `<team>/<trello-task>/<description>`
- Example: `bot/STA-7/get-announcement-data`

Pull request (PR) conventions
- At the top of the description, include the Trello ticket:

      [STA-10](link)
      This ticket entails...

- PRs aren't needed for README updates. (Commit directly to `main`)
