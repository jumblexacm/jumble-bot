// Source: https://betterprogramming.pub/build-a-discord-bot-with-aws-lambda-api-gateway-cc1cff750292

const nacl = require('tweetnacl');

exports.lambda_handler = async (event) => {
  // Checking signature (requirement 1.)
  // Your public key can be found on your application in the Developer Portal
  const PUBLIC_KEY = process.env.PUBLIC_KEY;
  const signature = event.headers['x-signature-ed25519']
  const timestamp = event.headers['x-signature-timestamp'];
  const strBody = event.body; // should be string, for successful sign

  const isVerified = nacl.sign.detached.verify(
    Buffer.from(timestamp + strBody),
    Buffer.from(signature, 'hex'),
    Buffer.from(PUBLIC_KEY, 'hex')
  );
  
  // TODO Remove this after it works
  // client.on('ready', client => {
  //   client.channels.get(process.env.CHANNEL_ID).send('Hello here!');
  // })
  
  console.log("Public key: ", PUBLIC_KEY);
  
  if (!isVerified) {
    console.log("invalid");
    return {
      statusCode: 401,
      body: JSON.stringify('invalid request signature'),
    };
  }
  
  // TODO Remove this after it works
  // client.on('ready', client => {
  //   client.channels.get(process.env.CHANNEL_ID).send('Verified :)');
  // })
  
  // Replying to ping (requirement 2.)
  console.log("valid");
  const body = JSON.parse(strBody)
  if (body.type == 1) {
    return {
      statusCode: 200,
      body: JSON.stringify({ "type": 1 }),
    }
  }
};
