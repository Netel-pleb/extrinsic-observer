# bot.py
# This script sends embed messages to a Discord channel using a webhook.
# It defines a function to format the embed data and make a POST request.
import requests
import json

def post_to_discord(embed, webhook_url):
    # print(webhook_url)
    if embed == None:
        return
    data = {
        "embeds": [embed]
    }
    response = requests.post(webhook_url, data=json.dumps(data), headers={"Content-Type": "application/json"})
    return response.status_code, response.text

