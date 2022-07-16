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
    - Save the generated URL, because it disappears if you navigate away from the page

5. Activate the bot
    - Use the generated URL to invite the bot to your dev server
    - In your dev server settings > **"Roles"** > your bot > **"Permissions"**, turn off `View Channels`. Otherwise, the bot may add messages to MongoDB that you don't want it to
    - Under the channel you want the bot to watch > **"Edit Channel"** (gear icon) > **"Permissions"**, turn on `View Channel`


## STEP 2: Create a test student org server

1. In Discord, click **[Add a Server]** and follow the steps

2. Under **"Server Settings"** > **"Enable Community"**, click **[Get Started]** and follow the steps

3. Click the plus symbol to **"Create Channel"**, check `Announcement`, and create the channel

4. Next to the new channel name, click **"Follow"** and choose your dev server where you installed the bot

5. Consider creating another Discord app/bot, student org server, and dev server as your dev environment.

Notes about community servers:
- For a message to appear in the dev server, you must post in the announcements channel *and* click "Publish."
- When you publish, Discord may say, "You've reached your 10 published mesages per-hour limit. But we love the enthusiasm, so please try again in X minutes." Create an additional announcements channel, follow it from your dev server, and post in the new announcements channel for a while.
- When you edit the message in the student org server, it also updates in the dev server.


## STEP 3: Set up the Heroku app

1. Create the Heroku app

2. Connect the Heroku app to GitHub
    - Click **"Deploy"**
    - Under **"Deployment method"**, connect the app to your GitHub account
    - Choose the repo where you store your Heroku app's code

TODO Add any other steps/details that Cannon followed

3. Gather secrets
    - Generate the [MongoDB URI](https://www.mongodb.com/docs/manual/reference/connection-string/#dns-seed-list-connection-format)
        - In MongoDB Atlas, click **"Database"** to open the Database Deployments page
        - Next to Jumble, click **[Connect]**
        - Click **[Connect Your Application]**
        - Copy the generated MongoDB URI, replace `<password>` with the password for the specified user, and save it somewhere secure
    - Generate the Discord bot token
        - Open your Discord app in the Discord Developer Portal
        - Menu section: **"Bot"**
        - Under **"Build-A-Bot"**, click `Reset Token` and save it somewhere secure
    - Find the Discord channel ID for the bot to watch
        - Open your dev server
        - Open the channel you want the bot to watch
        - In the URL, save the second number

Note: When storing secrets, please use the Heroku Dashboard, not the CLI. Using the Heroku Dashboard prevents secrets from being stored in your terminal history.

4. Store secrets as [config vars](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard), like environment variables
    - In the Heroku Dashboard, click **"Settings"**
    - Under **"Config Vars"**, click **[Reveal Config Vars]**
    - Add the first config var:
        - KEY: `MONGODB_URI`
        - VALUE: *[Input the MongoDB URI]*
    - Add the second config var:
        - KEY: `DISCORD_TOKEN`
        - VALUE: *[Input the Discord bot token]*
    - Add the third config var:
        - KEY: `BOT_CHANNEL_ID`
        - VALUE: *[Input the Discord channel ID]*

5. Let Heroku access MongoDB
    - In MongoDB Atlas, click **"Network Access"**
    - Click **[Add IP address]**
    - Access List Entry: `0.0.0.0/0`
    - Comment: `All IP addresses so Heroku can access MongoDB`
    - Note: If you're uncomfortable allowing all IP addresses, a Heroku [add-on](https://www.mongodb.com/developer/products/atlas/use-atlas-on-heroku/#configuring-heroku-ip-addresses-in-mongodb-atlas) can create a static IP address. As far as [@kirmar] can tell, without [one of these solutions](https://www.mongodb.com/community/forums/t/connect-atlas-to-heroku-hosted-app/7202), the Heroko app doesn't work and Heroku logs a `ServerSelectionTimeoutError` when it tries to access the MongoDB database.

6. Set your `$HEROKU_APP_NAME` environment variable
    - In your terminal, run:
          
          HEROKU_APP_NAME=*<the name of your Heroku app as displayed in the Heroku Dashboard>*
          echo $HEROKU_APP_NAME # Confirm it's set to the correct name

7. Deploy the Heroku app for the first time
    - Follow [step 6](#step-6-deploy-to-heroku)
    - After this very first deployment, [scale the number of worker dynos](https://devcenter.heroku.com/articles/background-jobs-queueing#process-model)
        - In your terminal, run:
              
              heroku ps:scale worker=1 -a $HEROKU_APP_NAME


## STEP 4: Set up your Heroku CLI and local environment

1. Store secrets in `.env`
    - In your terminal, run:
          
          heroku config:get MONGODB_URI -s -a $HEROKU_APP_NAME >> .env
          heroku config:get BOT_CHANNEL_ID -s -a $HEROKU_APP_NAME >> .env
    
    - Then set `DISCORD_TOKEN` to your dev environment Discord bot's token OR run:
          
          heroku config:get DISCORD_TOKEN -s -a $HEROKU_APP_NAME >> .env

2. Install dependencies
    - In your terminal, run:
    
          python3 -m pip install --target=lib/ -r requirements.txt


## STEP 5: Test the app on your local machine

1. Start the app
    - In your terminal, run:
    
          heroku local
          # TODO Should this be `heroku local worker=1`?
    
    - OR run:
    
          python3 main.py
    
    - TODO Note that as far as [@kirmar](https://github.com/kirmar) can tell, `heroku local` doesn't output "We have logged in as..." or any other `print()`ed messages until you hit \<Ctrl+C>

3. Post and publish a message in your test community server

4. See the new document in MongoDB :)
    - In MongoDB Atlas, click **"Database"** to open the Database Deployments page
    - Next to Jumble, click **[Browse Collections]**
    - Scroll to the last query result

5. If using `heroku local`: When you're done testing, hit \<Ctrl+C> to see the logs


## STEP 6: Deploy to Heroku

<!-- Note: As of 2022-07-14, another step links to this one, so be careful changing the title or step number -->

1. In your terminal, `git push` your branch

2. In the Heroku Dashboard, under **"Manual deploy"**, choose your current branch

3. Click **[Deploy Branch]**


## STEP 7: Test the app

1. Post and publish a message in your test community server

2. See the new document in MongoDB :)

3. View your Heroku logs
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
