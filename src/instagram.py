from instagrapi import Client
import moviepy.editor as mp
import os
from dotenv import load_dotenv


load_dotenv()

USERNAME = os.getenv("INSTAGRAM_USERNAME")
PASSWORD = os.getenv("INSTAGRAM_PASSWORD")


class Instagram:

    def __init__(self):
        self.client = Client()

    def login(self):
        if os.path.exists("./session.json"):
            self.client.load_settings("./session.json")

        self.client.login(USERNAME, PASSWORD)
        self.client.get_timeline_feed()

        self.client.dump_settings("./session.json")

    def upload_to_instagram(self, folder: str, filename: str, caption: str):
        self.login()

        path = os.path.join(os.pardir, "resources", folder, filename)

        if filename.endswith(".gif"):
            clip = mp.VideoFileClip(path)
            clip.write_videofile(f"{path}.mp4")
            self.client.video_upload(f"{path}.mp4", caption)

        elif filename.endswith(".mp4"):
            self.client.video_upload(path, caption)

        elif filename.endswith(".jpg"):
            self.client.photo_upload(path, caption)

        # self.client.logout()
