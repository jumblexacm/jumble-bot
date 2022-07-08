# ACM x Jumble


## Prerequisites

- Discord account

- Discord server (your "dev server")

- AWS account


## STEP 1: Create the Discord bot

https://discord.com/developers/docs/intro

1. Create the [team](https://discord.com/developers/docs/topics/teams)
    - Visit https://discord.com/developers/teams
    - Click **[New Team]**

2. Create the [app](https://discord.com/developers/docs/intro#bots-and-apps)
    - Visit https://discord.com/developers/applications
    - Click **[New application]**
    - Choose your team from earlier (not your personal team)

3. Add the redirect URI
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


## STEP 3: Create the admin IAM role and user

https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html

1. Sign in as the root user in your AWS account

2. Create an IAM [admin role](https://alestic.com/2014/09/aws-root-password/)
    - In the Identity and Access Management (IAM) console, click **"Roles"**
    - Click **[Create role]**
    - Trusted entity type: `AWS account`
    - An AWS account: `This account`
    - Options: `Require MFA`
    - Add permissions: `AdministratorAccess`
    - Name: `jumble-admin-role`

3. Create an IAM [permissions policy](https://docs.aws.amazon.com/lambda/latest/dg/security_iam_id-based-policy-examples.html)
    - In the IAM console, click **"Policies"**
    - Click **[Create policy]**
    - Add Lambda function view/edit permissions
        - Service: `STS`
        - Actions:
            - `Write` > `AssumeRole`
        - Resources: `Specific`
            - **"Add ARN"**
            - Paste the ARN from the `jumble-admin-role` summary
        - Request conditions: `MFA required`
    - Name: `jumble-admin-policy`

4. Create your IAM [user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id.html#id_which-to-choose)
    - In the IAM console, click **"Users"**
    - Click **[Add users]**
    - User name: `jumble-<your-name>-user`
        - Example: `jumble-kira-user`
    <!--- - Select AWS credential type: `Access key - Programmatic access` -->
    - Select AWS access type
        - Select AWS credential type: `Password - AWS Management Console access`
        - Console password: `Autogenerated password`
        - Require password reset: `Users must create a new password at next sign-in`
    - Attach existing policies directly: `jumble-admin-policy`
    - After creating the user, save the credentials immediately to a safe place, because they disappear forever if you navigate away from the page

5. Switch to the admin role
    - Get the link
        - In the IAM console, click **"Roles"**
        - Open `jumble-admin-role`
        - Copy and save the "switch roles" link
    - Sign out of the AWS account
    - Sign in as your IAM user
    - Visit the "switch roles" link

5. From now on, use the admin role any time you need full permissions, instead of using the root user directly


## STEP 4: Finish creating the IAM users

1. In your IAM user and the admin role, create an IAM policy
    - In the IAM console, click **"Policies"**
    - Click **[Create policy]**
    - Add Lambda function view/edit permissions
        - Service: `Lambda`
        - Actions:
            - `Read` > `GetAccountSettings` (to view the list of all functions in the Lambda console)
            - `List` > `ListFunctions`
            - `Read` > `GetFunction` (to view a Lambda function's code, logs, and settings)
            - `List` > `ListFunctionUrlConfigs` (to view a function URL)
            - `Write` > `CreateFunctionUrlConfig` (to create a function URL)
        - Resources: `All resources`
        - Request conditions: `MFA required`
    - Name: `jumble-bot-function-policy`

2. Create an IAM user group
    - In the Identity and Access Management (IAM) console, click **"User groups"**
    - Click **[Create group]**
    - Attach permissions policies: `jumble-bot-function-policy`
    - User group name: `jumble-engineer-group`

3. Add your IAM user to the user group
    - In the IAM console, click **"Users"** and choose your IAM user
    - Click **"Groups"**
    - Add user to groups: `jumble-engineer-group`

4. For each engineer who needs access to your AWS resources (like your Lambda function), create an IAM user
    - Use the same naming convention and access type from your IAM user
    - However, this time:
        - Add user to group: `jumble-engineer-group`
        - (Do NOT attach any policies directly, except for the policy that IAM automatically attaches for password changes)

5. Set up MFA for each user
    - In the IAM console, click **"Users"** and choose an IAM user
    - Click **"Security credentials"**
    - Assigned MFA device: `Manage`
    - Work with the user to set up their MFA of choice

6. Optional: To make the sign-in URL simpler for IAM users and something that isn't a secret, create an [account alias](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html#CreateAccountAlias)
    - In the IAM console, click **"Dashboard"**
    - Under **"AWS Account"** > **"Account Alias"**, click **[Create]** and choose a unique alias with no private information

7. Send each user's credentials securely to the user


## STEP 5: Set up the AWS Lambda function

1. In your IAM user and the admin role, create the function
    - In the Lambda console, click **"Dashboard"**
    - Click **[Create function]**
    - Check `Author from scratch`
    - Function name: `jumble-bot-function`
    - Execution role: `Create a new role with basic Lambda permissions`
    - Create a URL
        - Under **"Advanced settings"**, check `Enable function URL`
        - Auth type: `NONE` (We'll authenticate within the Lambda function)

2. As any user, create the function URL
    - In the Lambda console, click **[Functions]**
    - Open `jumble-bot-function`
    - Under **"Configuration"**, click **[Create function URL]**


## Resources

https://discord.com/developers/docs/resources/channel#get-channel-messages

https://github.com/kkrypt0nn/Python-Discord-Bot-Template


## Repo conventions

Branch naming convention
- `<team>/<trello-task>/<description>`
- Example: `bot/STA-7/get-announcement-data`
