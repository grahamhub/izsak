import os
import requests


class Twitter:
    def __init__(self, token=os.environ.get("IZSAK_TWT_TOKEN")):
        self.token = token
        self.user_agent = "izsak/1.0.0"
        self.base_url = "https://api.twitter.com/2"

    @staticmethod
    def parse_id_from_url(url):
        return url.split("/").pop().split("?")[0]

    def _bearer_oauth(self, req):
        req.headers["Authorization"] = f"Bearer {self.token}"
        req.headers["User-Agent"] = self.user_agent
        return req

    def _build_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.request("GET", url, auth=self._bearer_oauth)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def get_tweet(self, tweet_id):
        endpoint = f"tweets?tweet.fields=text,attachments,author_id&ids={tweet_id}"
        resp = self._build_request(endpoint)
        return resp.get("data")

    def get_tweet_media(self, tweet_id):
        endpoint = f"tweets/{tweet_id}?media.fields=preview_image_url,url&expansions=attachments.media_keys"
        resp = self._build_request(endpoint)
        return resp.get("includes", {}).get("media", [])

    def get_user_pfp(self, user_id):
        endpoint = f"users/{user_id}?user.fields=profile_image_url"
        resp = self._build_request(endpoint)
        return resp.get("data", {}).get("profile_image_url")

