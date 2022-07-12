# ACM x Jumble


## Prerequisites

- Discord account

- Discord server (your "dev server")

- AWS account

- Python 3.9 (with `pip`)


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


## STEP 3: Create the admin IAM role and first user

https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html

1. After signing in as the root user in your AWS account, create an IAM [admin role](https://alestic.com/2014/09/aws-root-password/)
    - In the Identity and Access Management (IAM) console, click **"Roles"** and **[Create role]**
    - Trusted entity type: `AWS account`
    - An AWS account: `This account`
    - Options: `Require MFA`
    - Add permissions: `AdministratorAccess` (just that; not the one for Amplify or Elastic Beanstalk)
    - Role name: `admin`
    - After creating the role, open its role summary to copy/save both its ARN and its "switch roles" link somewhere safe

2. Create an IAM "assume admin role" [permissions policy](https://docs.aws.amazon.com/lambda/latest/dg/security_iam_id-based-policy-examples.html)
    - In the IAM console, click **"Policies"** and **[Create policy]**
    - Add "assume admin role" permission
        - Service: `STS`
        - Actions:
            - `Write` > `AssumeRole`
        - Resources: `Specific`
            - **"Add ARN"**
            - Paste the ARN from `admin`'s role summary
        - Request conditions: `MFA required`
    - Name: `jumble-assume-admin-policy`

3. Create the IAM [users](https://docs.aws.amazon.com/IAM/latest/UserGuide/id.html#id_which-to-choose)
    - In the IAM console, click **"Users"** and **[Add users]**
    - User name: *[Input your name]*
        - Example: `kira`
    - For each other engineer who needs access to your AWS resources (like your Lambda function), **[Add another user]**
    <!--- - Select AWS credential type: `Access key - Programmatic access` -->
    - Select AWS access type
        - Select AWS credential type: `Password - AWS Management Console access`
        - Console password: `Autogenerated password`
        - Require password reset: `Users must create a new password at next sign-in`
    - Attach existing policies directly: `jumble-assume-admin-policy`
    - After creating the user(s), save the credentials immediately to a safe place, because they disappear forever if you navigate away from the page

4. Set up MFA
    - In the IAM console, click **"Users"** and choose your IAM user
    - Click **"Security credentials"**
    - Assigned MFA device: `Manage`
    - Set up your MFA of choice
    - Note: If you don't set up MFA, trying to assume the admin role might give you this error: "Invalid information in one or more fields."

5. Assume the `admin` role
    - Sign out of the AWS account
    - Sign in as your IAM user
    - Visit the "switch roles" link from `admin`'s role summary
    - Display Name: *[Input anything you'd like that helps you remember what this role is]*

6. From now on, assume the `admin` role any time you need full permissions, instead of using the root user directly

7. Recommended: To make the sign-in URL simpler for IAM users and something that isn't a secret, create an [account alias](https://docs.aws.amazon.com/IAM/latest/UserGuide/console_account-alias.html#CreateAccountAlias)
    - In the IAM console, click **"Dashboard"**
    - Under **"AWS Account"** > **"Account Alias"**, click **[Create]** and choose a unique alias with no private information


## STEP 4: Create the engineer IAM role

1. Still assuming the `admin` role, create an IAM policy for managing Lambda
    - In the IAM console, click **"Policies"** and **[Create policy]**
    - Add Lambda function create/view/edit permissions
        - Service: `Lambda`
        - Actions:
            - `List`
                - `ListFunctions` (to view the list of all functions in the Lambda console)
                - `ListFunctionUrlConfigs` (to view a function URL)
            - `Read`
                - `GetAccountSettings` (to view the list of all functions in the Lambda console)
                - `GetFunction` (to view a function's code, logs, and settings)
            - `Write`
                - `CreateFunction` (to create a function)
                - `CreateFunctionUrlConfig` (to create a function URL)
                - `UpdateFunctionCode` (to update a function's code, lol)
                - `UpdateFunctionConfiguration` (to update function settings like the runtime/language)
            - `Permissions management`
                - `AddPermission` (to create a function URL)
        - Resources: `All resources`
        - Request conditions: `MFA required`
    - Add additional permissions
        - Service: `IAM`
        - Actions:
            - `Write`
                - `CreateRole` (to create a function)
                - `PassRole` (to create a function)
            - `Permissions management`
                - `AttachRolePolicy` (to create a function)
                - `CreatePolicy` (to create a function)
        - Resources: `All resources`
        - Request conditions: `MFA required`
    - Add additional permissions
        - Service: `CloudWatch Logs`
        - Actions:
            - `List`
                - `DescribeLogGroups` (to view the list of Lambda "console" logs)
            - `Read`
                - `FilterLogEvents` (to view the list of Lambda "console" logs)
        - Resources: `All resources`
        - Request conditions: `MFA required`
    - Name: `jumble-lambda-policy`

2. Create an IAM engineer role
    - As earlier with `admin`, choose this account and require MFA
    - However, add `jumble-lambda-policy` (not the "assume admin role" policy)
    - And name the role `engineer`
    - After creating the role, open its role summary to copy its ARN

3. Create an IAM "assume engineer role" policy
    - As earlier with `jumble-assume-admin-policy`, choose `STS` > `Write` > `AssumeRole`
    - However, for the resource, paste the ARN from the `engineer` role summary (not the admin role's summary)
    - Request conditions: `MFA required`
    - Name: `jumble-assume-engineer-policy`

4. Add `jumble-assume-engineer-policy` to each user (including the first IAM user from earlier)
    - For each user:
        - In the IAM console, click **"Users"** and choose the IAM user
        - Click **"Add permissions"**
        - Attach existing policies directly: `jumble-assume-engineer-policy`
    - At the end, each user has `jumble-assume-admin-policy` and `jumble-assume-engineer-policy` (and the automatically-attached `IAMUserChangePassword`)

5. Work with each user to set up their MFA

6. Send each user's credentials securely to the user


## STEP 6: Set up the Lambda function

https://betterprogramming.pub/build-a-discord-bot-with-aws-lambda-api-gateway-cc1cff750292

1. Assuming the `engineer` role, create the function
    - In the Lambda console, click **"Dashboard"** and **[Create function]**
    - Check `Author from scratch`
    - Function name: `jumble-bot-function`
    - Execution role: `Create a new role with basic Lambda permissions`
        - Note: If you ever delete the Lambda function, be sure to delete the role it created too
    - Create a URL
        - Under **"Advanced settings"**, check `Enable function URL`
        - Auth type: `NONE` (We'll authenticate within the Lambda function)

2. Upload your Discord app's public key to AWS
    - Find the public key
        - Visit https://discord.com/developers/applications
        - Choose your app
        - Find the public key
    - Upload the public key
        - In `jumble-bot-function`'s **"Configuration"** tab, click **"Environment variables"**
        - Click **[Edit]** and **[Add environment variable]**
        - Key: `PUBLIC_KEY`
        - Value: *[Input your Discord app's public key]*

3. Install dependencies
    - In your local terminal, run:
    
          cd task/
          <!-- npm i tweetnacl -->
          python3.9 -m pip install --target=pynacl/ pynacl

4. Upload your code
    - In your local terminal (still in `task/`), run:
    
          touch ../lambda_bot.zip # Otherwise the first time, removing will raise an error
          rm ../lambda_bot.zip # Otherwise, zipping won't replace the file
          zip -r ../lambda_bot.zip *
    
    - In `jumble-bot-function`'s **"Code"** tab, **[Upload from]** the .zip file
    - Click **[Deploy]**

5. Add your Lambda function URL to Discord
    - In `jumble-bot-function`'s **"Configuration"** tab, copy the function URL
    - In the Discord app's **"Interactions Endpoint URL"**, paste the function URL

6. Confirm the Lambda function is running and properly authenticating Discord
    - In `jumble-bot-function`'s **"Monitor"** tab, click **[View logs in CloudWatch]**
    - Click **[Search log group]**
    - Click `1m` to view the most recent logs
    - Confirm the function ran without errors
        - If the function didn't run, reset the interactions endpoint URL (by saving it as empty in the Discord development portal) and repeat steps 4 and 5
        - If the function output an error, edit the code as needed, reset the interactions endpoint URL, and repeat steps 3 through 5
        - If the function ran without errors, congratulations! Everything's connected!


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
