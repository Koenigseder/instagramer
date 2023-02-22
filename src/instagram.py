import logging
import os

from dotenv import load_dotenv
from instagrapi import Client
import moviepy.editor as mp

load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


class Instagram:

    def __init__(self):
        self.client = Client()

    def login(self) -> bool:
        try:
            if os.path.exists("./session.json"):
                self.client.load_settings("./session.json")

            self.client.login(USERNAME, PASSWORD)
            self.client.get_timeline_feed()

            self.client.dump_settings("./session.json")

            return True  # Stands for success -> Client was able to log in

        except BaseException as e:
            logging.error(f"An error occurred while logging in to Instagram: {e}")
            return False  # Stands for failure -> Client was not able to log in

    def upload_to_instagram(self, folder: str, filename: str, caption: str) -> bool:

        logged_in: bool = False
        tries_to_login_remaining: int = 3

        while not logged_in and tries_to_login_remaining > 0:
            logged_in = self.login()
            if not logged_in:
                tries_to_login_remaining -= 1

        if not logged_in:
            return False  # Stands for failure -> After 3 attempts the client was not able to log in

        path = os.path.join(os.pardir, "resources", folder, filename)

        try:
            if filename.endswith(".gif"):
                clip = mp.VideoFileClip(path)
                clip.write_videofile(f"{path}.mp4")
                self.client.video_upload(f"{path}.mp4", caption)

            elif filename.endswith(".mp4"):
                self.client.video_upload(path, caption)

            elif filename.endswith(".jpg"):
                self.client.photo_upload(path, caption)

            return True  # Stand for success -> Post was uploaded

        except BaseException as e:
            logging.error(f"An error occurred while uploading a post to Instagram: {e}")
            return False  # Stands for failure -> Post could not be uploaded
