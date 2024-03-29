from http import client
import urllib
import json
import os

BASE_PATH = os.path.dirname(__file__)
KEYS_PATH = os.path.join(BASE_PATH, "..", "keys", "keys.json")
LOG_PATH = os.path.join(BASE_PATH, "..", "cache", "log.txt")


def main():
    with open(LOG_PATH, "a") as f:
        f.write("Executed mood.py\n")

    with open(KEYS_PATH) as f:
        keys = json.load(f)

        conn = client.HTTPSConnection("api.pushover.net:443")

        conn.request(
            "POST",
            "/1/messages.json",
            urllib.parse.urlencode(
                {
                    "token": keys["app-token"],
                    "user": keys["user-key"],
                    "message": "Time to log your mood and energy",
                    "device": keys["device-name"],
                    "url": keys["poll-url"],
                    "url-title": "Poll Form",
                }
            ),
            {"Content-type": "application/x-www-form-urlencoded"},
        )
        conn.getresponse()
        # TODO: when I eventually automate this, I need to make sure I don't emit multiple api calls at once


if __name__ == "__main__":
    main()
