from atproto import Client

from dotenv import load_dotenv
import os
from bluesky_client.get_author_feed import get_author_feed


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

    data = get_author_feed(client, client_did)
    for post in data:
        print(post.model_dump_json(indent=2))
    