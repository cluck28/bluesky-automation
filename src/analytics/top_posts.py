def get_most_liked_post(user_feed: list, user_handle: str) -> str:
    most_likes = 0
    url = ""
    for post in user_feed:
        if post.author.handle == user_handle:
            if post.like_count > most_likes:
                most_likes = post.like_count
                url = post.embed.thumbnail
    return url, most_likes


def get_most_replied_post(user_feed: list, user_handle: str) -> str:
    most_replies = 0
    url = ""
    for post in user_feed:
        if post.author.handle == user_handle:
            if post.reply_count > most_replies:
                most_replies = post.reply_count
                url = post.embed.thumbnail
    return url, most_replies


def get_most_reposted_post(user_feed: list, user_handle: str) -> str:
    most_reposts = 0
    url = ""
    for post in user_feed:
        if post.author.handle == user_handle:
            if post.repost_count > most_reposts:
                most_reposts = post.repost_count
                url = post.embed.thumbnail
    return url, most_reposts


def get_most_bookmarked_post(user_feed: list, user_handle: str) -> str:
    most_bookmarks = 0
    url = ""
    for post in user_feed:
        if post.author.handle == user_handle:
            if post.bookmark_count > most_bookmarks:
                most_bookmarks = post.bookmark_count
                url = post.embed.thumbnail
    return url, most_bookmarks
