# ACM x Jumble


## Prerequisites

- Discord account

- Discord server (your "dev server")

- MongoDB Atlas database

- Algolia app

- Heroku account and Heroku CLI
    - https://devcenter.heroku.com/articles/heroku-cli

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
    - Save the generated URL, because it disappears if you navigate away from the page

5. Activate the bot
    - Use the generated URL to invite the bot to your dev server
    - In your dev server settings > **"Roles"** > your bot > **"Permissions"**, turn off `View Channels`. Otherwise, the bot may add messages to MongoDB that you don't want it to. (This is also prevented by `BOT_CHANNEL_IDS` in `main.py`, but just in case.)
    - Under each channel you want the bot to watch > **"Edit Channel"** (gear icon) > **"Permissions"**, turn on `View Channel`


## STEP 2: Create a test community server

1. In Discord, click **[Add a Server]** and follow the steps

2. Under **"Server Settings"** > **"Enable Community"**, click **[Get Started]** and follow the steps

3. Click the plus symbol to **"Create Channel"**, check `Announcement`, and create the channel

4. Next to the new channel name, click **"Follow"** and choose your dev server where you installed the bot

5. Consider creating another Discord app/bot, student org server, dev server, MongoDB database, and Algolia app as your dev environment.

Notes about community servers:
- For a message to appear in the dev server, you must post in the announcements channel *and* click "Publish."
- When you publish, Discord may say, "You've reached your 10 published mesages per-hour limit. But we love the enthusiasm, so please try again in X minutes." Create an additional announcements channel, follow it from your dev server, and post in the new announcements channel for a while.
- When you edit the message in the student org server, it also updates in the dev server.


## STEP 3: Set up the Heroku app

1. Create the Heroku app

2. Connect the Heroku app to GitHub
    - In the Heroku Dashboard, click the **"Deploy"** tab
    - Under **"Deployment method"**, connect the app to your GitHub account
    - Choose the repo where you store your Heroku app's code
    - Select branch to deploy from. Default: main

3. Gather secrets
    - Generate the [MongoDB URI](https://www.mongodb.com/docs/manual/reference/connection-string/#dns-seed-list-connection-format)
        - In MongoDB Atlas, click **"Database"** to open the Database Deployments page
        - Next to Jumble, click **[Connect]**
        - Click **[Connect Your Application]**
        - Copy the generated MongoDB URI, replace `<password>` with the password for the specified user, and save it somewhere secure
    - Find the MongoDB database name
        - In MongoDB Atlas, click **"Database"**
        - Next to Jumble, click **[Browse Collections]**
        - Under **"Create Database"** and **"Search Namespaces"**, find the database name and save it somewhere
    - Generate the Discord bot token
        - Open your Discord app in the Discord Developer Portal
        - Menu section: **"Bot"**
        - Under **"Build-A-Bot"**, click `Reset Token` and save it somewhere secure
    - Find the Discord channel IDs for the bot to watch
        - Open your dev server
        - Open each channel you want the bot to watch
        - From each URL, save the second number (the channel ID) with commas separating the channel IDs (no space, just ",")
    - Find the Algolia app's API keys
        - Open your Algolia app's dashboard
        - Below the welcome message, click **"API Keys"**
        - Copy the application ID and admin API key to a safe place

Note: When storing secrets, please use the Heroku Dashboard, not the CLI. Using the Heroku Dashboard prevents secrets from being stored in your terminal history.

4. Store secrets as [config vars](https://devcenter.heroku.com/articles/config-vars#using-the-heroku-dashboard), like environment variables
    - In the Heroku Dashboard, click the **"Settings"** tab
    - Under **"Config Vars"**, click **[Reveal Config Vars]**
    - Add the first config var:
        - KEY: `MONGODB_URI`
        - VALUE: *[Input the MongoDB URI]*
    - Add the second config var:
        - KEY: `MONGODB_DB`
        - VALUE: *[Input the MongoDB database name]*
    - Add the third config var:
        - KEY: `DISCORD_TOKEN`
        - VALUE: *[Input the Discord bot token]*
    - Add the fourth config var:
        - KEY: `BOT_CHANNEL_IDS`
        - VALUE: *[Input the Discord channel IDs]*
    - Add the fifth config var:
        - KEY: ALGOLIA_ID
        - VALUE: *[Input the Algolia app's application ID]*
    - Add the sixth config var:
        - KEY: ALGOLIA_ADMIN_KEY
        - VALUE: *[Input the Algolia app's admin API key]*

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
    - In your terminal, clone this repo and `cd` into its root directory
    
    - Set your local environment variables to your dev environment secrets OR run:
          
          heroku config:get MONGODB_URI -s -a $HEROKU_APP_NAME >> .env
          heroku config:get MONGODB_DB -s -a $HEROKU_APP_NAME >> .env
          heroku config:get BOT_CHANNEL_IDS -s -a $HEROKU_APP_NAME >> .env
          heroku config:get DISCORD_TOKEN -s -a $HEROKU_APP_NAME >> .env
          heroku config:get ALGOLIA_ID -s -a $HEROKU_APP_NAME >> .env
          heroku config:get ALGOLIA_ADMIN_KEY -s -a $HEROKU_APP_NAME >> .env

2. Install dependencies
    - In your terminal, run:
    
          python3 -m pip install --target=lib/ -r requirements.txt


## STEP 5: Test the app on your local machine

1. Start the app
    - In your terminal, run:
    
          heroku local
          # TODO Should this be `heroku local worker=1`?
    
    - OR run:
    
          export $(grep -v '^#' .env | xargs) # Load environment variables
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

2. See the new document in MongoDB and record in Algolia :)

3. View your Heroku logs
    - In your terminal, run:
    
          heroku logs --tail -a $HEROKU_APP_NAME


## Test cases


### Editing

#### Send and edit in a single `discord.Client()` session

1. Send
2. Edit
3. Edit again
4. Edit to "[Original Message Deleted]"

Expected result:
- After step 1, MongoDB and Algolia have the original message content
- After step 2, MongoDB and Algolia have the new message content
- After step 3, MongoDB and Algolia have the new new message content
- After step 4, the message isn't in MongoDB and Algolia

#### Send and edit attachments (in a single session)

1. Send with attachment
2. Remove the attachment

Expected result:
- Before and after editing, MongoDB and Algolia have the attachment
- The edit function doesn't trigger at all and the bot doesn't crash
- However, maybe someday it'll work, and we don't want the bot crashing :)

#### Send in one session and edit in another

Expected result:
- Before editing, MongoDB and Algolia the original message content
- After editing, MongoDB and Algolia the new message content

#### Send when bot is offline and edit when online

Expected result:
- Before and after editing, the message isn't in MongoDB and Algolia
- However, the edit function triggers and doesn't crash

#### Edit non-announcement messages

1. Send and edit a message in the dev server channel you want the bot to watch. Do this in a single `discord.Client()` session so you're not just testing the "try to delete no matter what" `payload.cached_message`.

2. Send and edit a message in a different dev server channel. Again, do this in a single `discord.Client()` session.

Expected result:
- Before and after editing, none are in MongoDB and Algolia
- However, the edit function triggers for each and doesn't crash


### Deletion

#### Send and delete in a single `discord.Client()` session

1. "will delete": Delete from test community server

2. "will fake delete": Edit in test community server to say "[Original Message Deleted]" (This just ensures that if deleting in the test community server doesn't work, it's because Discord has changed the way community server announcements channel following works.)

3. "will manually delete": Delete manually in dev server

The suggested message text here is to give you less to think about as you test and to help identify the entries in MongoDB and Algolia :)

Expected result:
- Before deletion, all three are in MongoDB and Algolia
- After deletion, none are in MongoDB and Algolia

#### Send in one session and delete in another

1. "will delete next time"
2. "will fake delete next time"
3. "will manually delete next time"

Expected result:
- Before deletion, all three are in MongoDB and Algolia
- After deletion, none are in MongoDB and Algolia

#### Send when bot is offline and delete when online

1. "will delete on start"
2. "will fake delete on start"
3. "will manually delete on start"

Expected result:
- Before and after deletion, none are in MongoDB and Algolia
- However, a delete function triggers for each and doesn't crash

#### Delete deleted message

1. Delete one of the messages from above that is now "[Original Message Deleted]"

Expected result:
- Before and after deletion, none are in MongoDB and Algolia
- A delete function triggers, says the message wasn't found in MongoDB, and doesn't crash / raise any Python errors

#### Delete non-announcement messages

1. Delete a welcome message: "Welcome, so-and-so. We hope you brought pizza." This one isn't too important, so it doesn't matter when the message was sent.

2. Delete a channel follow message: "so-and-so has added such-and-such to this channel. Its most important updates will show up here." This one isn't too important, so it doesn't matter when the message was sent.

3. Send and delete a message in the dev server channel you want the bot to watch. Again, do this in a single `discord.Client()` session.

4. Send and delete a message in a different dev server channel. Again, do this in a single `discord.Client()` session.

Expected result:
- Before and after deletion, the message isn't in MongoDB and Algolia
- However, a delete function triggers and doesn't crash



## Manually add post to MongoDB and Algolia

Please note: The "Discord message" is the one in the dev server, not the original one in the student org community server. To manually add a post to MongoDB, you do not need to still be in the server.

1. Duplicate a post's MongoDB document
    - This ensures the new MongoDB document has the correct field names
    - Preferably choose a post by the same org
        - Otherwise, [@kirmar](https://github.com/kirmar) doesn't know how to get the URL of the org's avatar / profile picture
    - If the post is by a different org, update the org fields
        - Copy the Discord message's webhook ID into `org_id`
            - Right-click the org's name
            - **[Copy ID]**
        - Copy the Discord message's author name (just the server name without the channel name) into `message_author`
        - Set `author_avatar_url`: https://cdn.discordapp.com/embed/avatars/0.png

2. Update `message_text`
    - Copy the Discord message's text
    - Add any formatting (bold, underlines, italicization, etc.)

3. Update `attachment_urls`
    - Click the attachment
    - Right-click the image
    - **[Copy image address]** or similar
    - Change "media.discordapp.net" to "cdn.discordapp.net"
    - Paste as an element in the `attachment_urls` array

4. Add the post to Algolia
    - In MongoDB, **[Copy Document]**
    - In the Algolia `posts` index, **[Add records]** then **[Add manually]**
    - Set `_id` directly to the string instead of a JSON
    - Set `message_id` directly to string
    - Set `objectID` to the same string as MongoDB's `_id`



## Repo conventions

Branch naming convention
- `<team>/<trello-task>/<description>`
- Example: `bot/STA-7/get-announcement-data`

Pull request (PR) conventions
- At the top of the description, include the Trello ticket:

      [STA-10](link)
      This ticket entails...

- PRs aren't needed for README updates. (Commit directly to `main`)
