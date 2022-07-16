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

MEMES_TO_DOWNLOAD = 6


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

    def get_list_of_urls_and_titles_of_daily_top_memes(self, reddit_page: str, db_client: Database) -> list[tuple[str, str]]:
        res = requests.get(f"https://oauth.reddit.com/r/{reddit_page}/top?t=day", headers=self.headers)

        list_of_memes: list[tuple[str, str]] = []
        number_of_posts: int = 0
        for post in res.json()["data"]["children"]:
            if "url_overridden_by_dest" in post["data"] and "title" in post["data"]:
                if post['data']['url_overridden_by_dest'].endswith(".gif") \
                        or post['data']['url_overridden_by_dest'].endswith(".mp4") \
                        or post['data']['url_overridden_by_dest'].endswith(".jpg"):
                    if not db_client.was_this_meme_already_downloaded(post['data']['url_overridden_by_dest']):
                        list_of_memes.append((post['data']['url_overridden_by_dest'], post['data']['title']))
                        number_of_posts += 1
                        if number_of_posts >= MEMES_TO_DOWNLOAD:
                            break

        return list_of_memes

    def download_meme(self, url: str, folder: str, meme_uuid: uuid.UUID):
        path = os.path.join(os.pardir, "resources", folder)

        if not os.path.isdir(path):
            os.mkdir(path)

        filename = ""

        if url.endswith(".gif"):
            filename = f"{meme_uuid}.gif"
        elif url.endswith(".mp4"):
            filename = f"{meme_uuid}.mp4"
        elif url.endswith(".jpg"):
            filename = f"{meme_uuid}.jpg"

        if filename != "":
            urllib.request.urlretrieve(url, os.path.join(path, filename))
