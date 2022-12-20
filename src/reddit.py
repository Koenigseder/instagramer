import uuid
import requests.auth
import urllib.request
from database import Database
import os
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
SECRET_TOKEN = os.getenv("REDDIT_SECRET_TOKEN")
POSTS_TO_DOWNLOAD = int(os.getenv("POSTS_TO_DOWNLOAD"))


class Reddit:

    def __init__(self):
        self.headers = None

    def auth_for_reddit(self):
        try:
            auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_TOKEN)

            data = {'grant_type': 'password',
                    'username': USERNAME,
                    'password': PASSWORD}

            self.headers = {'User-Agent': 'Instagramer/0.0.1'}

            res_auth = requests.post('https://www.reddit.com/api/v1/access_token',
                                     auth=auth, data=data, headers=self.headers)

            token = res_auth.json()['access_token']

            self.headers = {**self.headers, **{'Authorization': f"bearer {token}"}}

        except BaseException as e:
            print(f"An error occurred for auth to Reddit: {e}")

    def get_list_of_urls_and_titles_of_daily_top_posts(self, subreddit: str, db_client: Database,
                                                       get_only_single_post=False) -> list[tuple[str, str]]:
        res = requests.get(f"https://oauth.reddit.com/{subreddit}/top?t=day", headers=self.headers)

        list_of_posts: list[tuple[str, str]] = []
        number_of_posts: int = 0
        for post in res.json()["data"]["children"]:
            if "url_overridden_by_dest" in post["data"] and "title" in post["data"]:
                if post['data']['url_overridden_by_dest'].endswith(".gif") \
                        or post['data']['url_overridden_by_dest'].endswith(".mp4") \
                        or post['data']['url_overridden_by_dest'].endswith(".jpg"):
                    if not db_client.was_this_post_already_downloaded(post['data']['url_overridden_by_dest']):
                        list_of_posts.append((post['data']['url_overridden_by_dest'], post['data']['title']))
                        number_of_posts += 1
                        if number_of_posts >= (1 if get_only_single_post else POSTS_TO_DOWNLOAD):
                            break

        return list_of_posts

    def download_post(self, url: str, folder: str, post_uuid: uuid.UUID):
        resource_path = os.path.join(os.pardir, "resources")
        date_folder = os.path.join(resource_path, folder)

        if not os.path.isdir(resource_path):
            os.mkdir(resource_path)

        if not os.path.isdir(date_folder):
            os.mkdir(date_folder)

        filename = ""

        if url.endswith(".gif"):
            filename = f"{post_uuid}.gif"
        elif url.endswith(".mp4"):
            filename = f"{post_uuid}.mp4"
        elif url.endswith(".jpg"):
            filename = f"{post_uuid}.jpg"

        if filename != "":
            urllib.request.urlretrieve(url, os.path.join(date_folder, filename))
