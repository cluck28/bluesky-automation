from typing import List

from atproto import Client

from bluesky_client.schemas.profile import Follower, Profile


def get_profile(client: Client, client_did: str) -> Profile:
    data = client.get_profile(actor=client_did)
    return Profile(
        did=data.did,
        handle=data.handle,
        followers_count=data.followers_count,
        follows_count=data.follows_count,
        created_at=data.created_at,
    )


def get_follows(client, client_did: str, limit: int = 30) -> List[Follower]:
    cursor = None
    cleaned_data = []
    i = 0
    while True:
        data = client.get_follows(
            actor=client_did,
            limit=limit,
            cursor=cursor,
        )
        if not data.follows:
            break
        for profile in data.follows:
            follows_data = Follower(
                did=profile.did,
                handle=profile.handle,
                display_name=profile.display_name,
                indexed_at=profile.indexed_at,
                created_at=profile.created_at,
                follow_index=i,
            )
            i += 1
            cleaned_data.append(follows_data)
        cursor = data.cursor
        if not cursor:
            break
    return cleaned_data


def get_followers(client, client_did: str, limit: int = 30) -> List[Follower]:
    cursor = None
    cleaned_data = []
    i = 0
    while True:
        data = client.get_followers(
            actor=client_did,
            limit=limit,
            cursor=cursor,
        )
        if not data.followers:
            break
        for profile in data.followers:
            followers_data = Follower(
                did=profile.did,
                handle=profile.handle,
                display_name=profile.display_name,
                indexed_at=profile.indexed_at,
                created_at=profile.created_at,
                follow_index=i,
            )
            i += 1
            cleaned_data.append(followers_data)
        cursor = data.cursor
        if not cursor:
            break
    return cleaned_data
