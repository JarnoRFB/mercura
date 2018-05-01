# Mercura
## The Epidemiological Assistent


Check
https://bot.dialogflow.com/ee501930-f67e-4cfd-b812-5145f632b1e1
for an interactive demo.

## Deployment for developement
1. Install [Docker Engine](https://docs.docker.com/install/).
1. Install [Docker Compose](https://docs.docker.com/compose/install/).
1. Register for and install [ngrok](https://ngrok.com/).
1. Run: `$ docker-compose up`
This might take a while when building the
  containers for the first time.
1. Run `$ ngrok http -bind-tls=true 80` This will give you a url that forwards
  requests to `localhost`.
1. Go to https://console.dialogflow.com/ and open the fulfillment tab.
1. Paste `<ngrok_url>/webhook` in the URL field, where `<ngrok_url>` is the URL
   `ngrok` is tells you it is forwarding to.
1. Merura should now work with your local version on all configured platforms!
