from atproto import Client

from dotenv import load_dotenv
import os
import json


load_dotenv()  # Looks for .env in the current directory



if __name__ == "__main__":
    client = Client()
    client_username = os.getenv("CLIENT_USERNAME")
    client_password = os.getenv("CLIENT_PASSWORD")
    print(f"client username is: {client_username}")
    print(f"client password: ***")
    client.login(client_username, client_password)
    client_did = client.me.did
    print("Getting data")
    data = client.get_author_feed(
        actor=client_did,
        filter='posts_and_author_threads',
        limit=30,
    )
    feed = data.feed
    for item in feed:
        post = item.post
        reply = item.reply
        reason = item.reason
        print("Post:")
        print(post)
        print("Reply:")
        print(reply)
        print("Reason:")
        print(reason)
    next_page = data.cursor
    print(next_page)