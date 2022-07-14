# Modified from:
# https://betterprogramming.pub/build-a-discord-bot-with-aws-lambda-api-gateway-cc1cff750292
# https://stackoverflow.com/a/67661930
# https://www.christopherbiscardi.com/validating-discord-slash-command-ed25519-signatures-in-rust

import os
import sys
import json
import traceback

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
    
    # Note: As shown in the following debug examples,
    # CloudWatch Logs seems to format any stringified JSON
    # (nifty but confusing) if the string follows this syntax:
    # - only string keys and string values
    # - only double quotes around each key or value (no single quotes)
    # - no spaces or newlines anywhere
    # Although if the string is a value inside another dictionary,
    # printing the dictionary prints the string as-is, not as a JSON.
    # So, don't be alarmed that `body` is indented in the encoding
    # and unindented in the request.
    # Unfortunately, that's not why the signature's invalid.
    body = request['body']
    
    # dict = {'abc': 1,'def':'gehij', 'klm': { 0: 2, 3: 4 }}
    # print("test: {'abc': 1,'def':'gehij', 'klm': { 0: 2, 3: 4 }}")
    # print(f"test 2: {dict}")
    # print(dict)
    # 
    # dict3 = "{'abc': 1,'def':'gehij', 'klm': { 0: 2, 3: 4 }}"
    # print(f"test 4: {dict3}")
    # print(dict3)
    # 
    # dict4 = '{"abc": 1,"def":"gehij", "klm": { 0: 2, 3: 4 }}'
    # print(f"test 6: {dict4}")
    # print(dict4)
    # 
    # dict5 = '{"abc":1,"def":"gehij","klm":{0:2,3:4}}'
    # print(f"test 8: {dict5}")
    # print(dict5)
    # 
    # # only double quotes, no spaces, only string keys/values
    # dict6 = '{"abc":"xyz", "def":"gehij"}'
    # print(f"test 10: {dict6}")
    # print(dict6)
    # 
    # dict6 = '{"abc":"xyz","def":"gehij"}'
    # print(dict7)
    # print({'test 13': dict7})
    # 
    # dict8 = "{'abc': 'xyz', 'def'  :'gehij'}"
    # print(f"test 14: {dict8}")
    # print(dict8)
    # 
    # print(f"request: {request}")
    # # print("(timestamp + body).encode() == timestamp.encode() + body.encode(): "
    # #       + str((timestamp + body).encode() == timestamp.encode() + body.encode()))
    # print(f"body: {body}")
    # print('"," in body: ' + str('","' in body))
    # print('"," in timestamp + body: ' + str('","' in timestamp + body))
    # print(f"timestamp + body: {timestamp + body}")
    # print(f"(timestamp + body).encode(): {(timestamp + body).encode()}")
    # print(f"bytes.fromhex(signature): {bytes.fromhex(signature)}")
    # 
    # print()
    
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
    except Exception:
        # print("invalid")
        # print(traceback.format_exc())
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
