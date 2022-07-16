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

    def upload_to_instagram(self, folder: str, filename: str, caption: str):
        self.client.login(USERNAME, PASSWORD)

        path = os.path.join(os.pardir, "resources", folder, filename)

        if filename.endswith(".gif"):
            clip = mp.VideoFileClip(path)
            clip.write_videofile(f"{path}.mp4")
            self.client.video_upload(f"{path}.mp4", caption)

        else:
            self.client.video_upload(path, caption)

        self.client.logout()
