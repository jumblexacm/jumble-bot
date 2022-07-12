# Modified from:
# https://betterprogramming.pub/build-a-discord-bot-with-aws-lambda-api-gateway-cc1cff750292
# https://stackoverflow.com/a/67661930
# https://www.christopherbiscardi.com/validating-discord-slash-command-ed25519-signatures-in-rust

import os
import sys
import json

sys.path.append('pynacl')
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Discord app's public key
# stored as the Lambda function's environment variable
PUBLIC_KEY = os.environ['PUBLIC_KEY']

def lambda_handler(request, lambda_context):
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    
    signature = request['headers']['x-signature-ed25519']
    timestamp = request['headers']['x-signature-timestamp']
    body = request['body']
    
    # print("signature: " + signature)
    # print("timestamp: " + timestamp)
    # print("type(body): " + str(type(body)))
    
    try:
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        # print("valid")
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 1})
        }
    except:
        # print("invalid")
        return {
            'statusCode': 401,
            'body': json.dumps("invalid request signature")
        }

def lambda_handler_with_slash_command(request, lambda_context):
    # print("here 0")
    
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    
    signature = request['headers']['x-signature-ed25519']
    timestamp = request['headers']['x-signature-timestamp']
    strBody = request['body']
    body = json.loads(strBody)
    
    # print("signature: " + signature)
    # print("timestamp: " + timestamp)
    # print("type(body): " + str(type(body)))
    
    # print("here 1")
    
    try:
        verify_key.verify(f'{timestamp}{strBody}'.encode(), bytes.fromhex(signature))
        # print("here 2")
        # print("valid")
    except BadSignatureError:
        print("invalid request signature :(")
        return {
            'statusCode': 401,
            'body': json.dumps("invalid request signature")
        }
    
    # print("here 4")
    
    # Reply to ping
    if body['type'] == 1:
        # print("here 5")
        return {
            'statusCode': 200,
            'body': json.dumps({'type': 1})
        }
    
    # print("here 6")
    # Handle /foo command
    try:
        if body['data']['name'] == "foo":
            # print("here 7")
            return json.dumps({
                'type': 4, # 4: Answer with invocation shown
                'data': {
                    'content': "bar"
                }
            })
    except:
        print(f"body: {body}")
    
    # print("here 8")
    # No handler implemented for Discord's request
    return {
        'statusCode': 404
    }
