import os
import pytumblr


class Tumblr:
    def __init__(self, api_key=os.environ.get("IZSAK_TUMBLR_API_KEY")):
        self.client = pytumblr.TumblrRestClient(
            os.environ.get("IZSAK_TUMBLR_CLIENT_KEY"),
            os.environ.get("IZSAK_TUMBLR_CLIENT_SECRET"),
            os.environ.get("IZSAK_TUMBLR_OAUTH_TOKEN"),
            os.environ.get("IZSAK_TUMBLR_OAUTH_SECRET"),
        )
        self.api_key = api_key

    @staticmethod
    def parse_url(url):
        if "blog/view/" in url:
            return url.split("/")[-2]
        else:
            url_split = url.split(".")
            if "www" in url_split[0]:
                return url_split[1]
            else:
                return url_split[0].split("/").pop()

    def get_blog_info(self, url):
        subdomain = self.parse_url(url)
        blog_info = self.client.blog_info(subdomain)
        return blog_info

    def get_post_info(self, url):
        subdomain = self.parse_url(url)
        post_id = url.split("/").pop().split("?")[0]
        post_info = self.client.posts(subdomain, id=post_id)
        return post_info
