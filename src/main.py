from datetime import timedelta, date
import logging
import os
from os import listdir
import shutil
import uuid

from dotenv import load_dotenv
import flask

import database
import discord
import instagram
import reddit

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

load_dotenv()
SUBREDDIT = os.getenv("SUBREDDIT")
DISCORD_WEBHOOK = None if os.getenv("DISCORD_WEBHOOK").strip() == "" else os.getenv("DISCORD_WEBHOOK")
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"  # Sometimes necessary for Linux

app = flask.Flask(__name__)
db_client = database.Database()
reddit_client = reddit.Reddit()
instagram_client = instagram.Instagram()
discord_client = discord.Discord(DISCORD_WEBHOOK) if DISCORD_WEBHOOK else None

INFO_COLOR = "03b2f8"
SUCCESS_COLOR = "03a306"
ERROR_COLOR = "a30303"


@app.route("/download-posts", methods=["POST"])
def download_posts(download_only_single_post=False) -> flask.Response:
    should_backfill: bool = True if flask.request.args.get("backfill") == "true" else False

    logging.info("Downloading posts...")
    db_client.open_connection()

    logged_in_to_reddit: bool = False
    retries_to_login_remaining: int = 3

    while not logged_in_to_reddit and retries_to_login_remaining > 3:
        logged_in_to_reddit = reddit_client.auth_for_reddit()
        if not logged_in_to_reddit:
            retries_to_login_remaining -= 1

    if not logged_in_to_reddit:
        return flask.Response(status=408)  # Timeout

    list_of_posts = reddit_client.get_list_of_urls_and_titles_of_daily_top_posts(SUBREDDIT,
                                                                                 db_client,
                                                                                 download_only_single_post)

    error_count = 0

    if len(list_of_posts) > 0:
        for post in list_of_posts:
            url, title = post
            post_uuid = db_client.insert_download_log_started(url, title)

            try:
                reddit_client.download_post(
                    url,
                    str(date.today() - timedelta(days=1)) if (download_only_single_post or should_backfill) else str(
                        date.today()),
                    post_uuid)
                db_client.insert_download_log_finished(post_uuid)
                logging.info("Download finished!")

            except BaseException as e:
                db_client.insert_download_log_failed(post_uuid)
                logging.error(f"An error occurred while downloading a post: {e}")

                error_count += 1

                if discord_client:
                    discord_client.set_embed("Download not successful!",
                                             f"I was not able to download a new post.\nReason: **{str(e)}**",
                                             ERROR_COLOR)
                    discord_client.send_message()

    db_client.close_connection()

    if discord_client:
        discord_client.set_embed("Download status",
                                 "🎉 Download successful! 🎉" if error_count <= 0 else "🚨 Download not successful! 🚨",
                                 SUCCESS_COLOR if error_count <= 0 else ERROR_COLOR)
        discord_client.send_message()

    return flask.Response(status=200)


@app.route("/upload-post", methods=["POST"])
def upload_post() -> flask.Response:
    logging.info("Uploading post to Instagram...")
    folder = str(date.today() - timedelta(days=1))
    path = os.path.join(os.pardir, "resources", folder)

    if os.path.exists(path):
        for file in listdir(path):
            if file.endswith(".mp4") or file.endswith(".gif") or file.endswith(".jpg"):
                post_uuid: uuid.UUID = uuid.UUID(file.split(".")[0])

                db_client.open_connection()
                db_client.insert_post_log_started(post_uuid)

                try:
                    caption = db_client.get_title_of_post(post_uuid)

                    instagram_client.upload_to_instagram(folder, file, caption)
                    for item in listdir(path):
                        if file.split(".")[0] in item:
                            os.remove(os.path.join(path, item))

                    db_client.insert_post_log_finished(post_uuid)
                    logging.info("Upload finished!")

                    if discord_client:
                        discord_client.set_embed("Post status", "🎉 Post uploaded! 🎉", SUCCESS_COLOR)
                        discord_client.send_message()

                except BaseException as e:
                    db_client.insert_post_log_failed(post_uuid, str(e))
                    logging.error(f"An error occurred while uploading the post to Instagram: {e}")

                    if discord_client:
                        discord_client.set_embed("Post status",
                                                 f"🚨 Error while uploading post! 🚨\n**{str(e)}**",
                                                 ERROR_COLOR)
                        discord_client.send_message()

                    if str(e) == "Uploaded image isn't in an allowed aspect ratio":
                        logging.info("Getting new post and retrying...")

                        for item in listdir(path):
                            if file.split(".")[0] in item:
                                os.remove(os.path.join(path, item))

                        download_posts(download_only_single_post=True)
                        upload_post()

                db_client.close_connection()
                break
    else:
        logging.warning("No such directory!")

    return flask.Response(status=200)


@app.route("/remove-dir", methods=["DELETE"])
def remove_dir() -> flask.Response:
    folder_name: str = flask.request.args.get("folder")

    logging.info("Removing old directory...")
    try:
        folder = folder_name if folder_name else str(date.today() - timedelta(days=2))
        path = os.path.join(os.pardir, "resources", folder)
        shutil.rmtree(path)
        logging.info("Removed old directory!")

    except BaseException as e:
        logging.error(e)

        if discord_client:
            discord_client.set_embed("Delete error",
                                     f"🚨 Error while deleting old directory! 🚨\n**{str(e)}**",
                                     ERROR_COLOR)
            discord_client.send_message()

    return flask.Response(status=200)


@app.route("/health-check", methods=["GET"])
def health_check():
    return {"message": "Instagramer is up and running"}


def start_instagramer():
    db_client.configure_db()

    logging.info("### Instagramer started! ###")

    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))


if __name__ == "__main__":
    start_instagramer()
