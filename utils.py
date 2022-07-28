
import os
import re

from constants import TUMBLR_LINK_RE

from functools import lru_cache
from itertools import chain
from clients.tumblr import Tumblr
from clients.twitter import Twitter


@lru_cache(maxsize=128)
def filter_embed_url(url):
    print(f"getting info for {url}")
    twt = Twitter()
    tblr = Tumblr()
    # TODO: other platforms / media formats
    if "twitter" in url:
        twt_media = twt.get_tweet_media(Twitter.parse_id_from_url(url))
        if len(twt_media) >= 1:
            twt_tweet = twt.get_tweet(Twitter.parse_id_from_url(url))
            user_id = twt_tweet[0].get("author_id")
            user_pfp = twt.get_user_pfp(user_id)
            return twt_media[0].get("url"), user_pfp
    elif "tumblr" in url:
        tblr_post = tblr.get_post_info(url)
        raw_post = tblr_post.get("posts", [{}])[0].get("body", "")
        link = re.search(TUMBLR_LINK_RE, raw_post)

        tblr_blog = tblr.get_blog_info(url)
        avatar = tblr_blog.get("blog", {}).get("avatar", [{}])[0]

        if link is None:
            link = tblr_post\
                .get("posts", [{}])[0]\
                .get("photos", [{}])[0]\
                .get("original_size", {})\
                .get("url")
        else:
            link = link[0]

        return link, avatar.get("url")

    return url, None


def can_upload(ctx):
    upload_users = os.environ.get("IZSAK_CAN_UPLOAD", "").split(",")
    upload_users = list(map(lambda id: int(id), upload_users))
    return ctx.user.id in upload_users


def flatten(arr):
    return list(chain(*arr))
