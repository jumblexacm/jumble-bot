# Modified from:
# https://betterprogramming.pub/build-a-discord-bot-with-aws-lambda-api-gateway-cc1cff750292
# https://stackoverflow.com/a/67661930

import os
import sys
import json

sys.path.append('pynacl')
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# Discord app's public key
# stored as the Lambda function's environment variable
PUBLIC_KEY = os.environ['PUBLIC_KEY']

# Source: https://www.christopherbiscardi.com/validating-discord-slash-command-ed25519-signatures-in-rust
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
