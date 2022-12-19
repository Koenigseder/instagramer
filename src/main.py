import os
import uuid
from datetime import timedelta, date
import database
import reddit
import instagram
import time
from os import listdir
import schedule
import logging
from dotenv import load_dotenv


db_client = database.Database()
reddit_client = reddit.Reddit()
instagram_client = instagram.Instagram()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

load_dotenv()

SUBREDDIT = os.getenv("SUBREDDIT")


def download_posts():
    logging.info("Downloading posts...")
    db_client.open_connection()

    reddit_client.auth_for_reddit()
    list_of_posts = reddit_client.get_list_of_urls_and_titles_of_daily_top_posts(SUBREDDIT, db_client)

    if len(list_of_posts) > 0:
        for post in list_of_posts:
            url, title = post
            post_uuid = db_client.insert_download_log_started(url, title)

            try:
                reddit_client.download_post(url, str(date.today()), post_uuid)
                db_client.insert_download_log_finished(post_uuid)
                logging.info("Download finished!")

            except BaseException as e:
                db_client.insert_download_log_failed(post_uuid)
                logging.error(f"An error occurred while downloading a post: {e}")

    db_client.close_connection()


def upload_post():
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

                except BaseException as e:
                    db_client.insert_post_log_failed(post_uuid, str(e))
                    logging.error(f"An error occurred while uploading the post to Instagram: {e}")

                db_client.close_connection()
                break
    else:
        logging.warning("No such directory!")


def remove_dir():
    logging.info("Removing old directory...")
    try:
        folder = str(date.today() - timedelta(days=2))
        path = os.path.join(os.pardir, "resources", folder)
        os.rmdir(path)
        logging.info("Removed old directory!")

    except BaseException as e:
        logging.error(e)


schedule.every().day.at("22:00").do(download_posts)

schedule.every().day.at("23:00").do(remove_dir)

schedule.every().day.at("06:00").do(upload_post)
schedule.every().day.at("09:00").do(upload_post)
schedule.every().day.at("12:00").do(upload_post)
schedule.every().day.at("15:00").do(upload_post)
schedule.every().day.at("18:00").do(upload_post)
schedule.every().day.at("21:00").do(upload_post)


def start_instagramer():
    db_client.configure_db()

    logging.info("### Instagramer started! ###")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    start_instagramer()
    # download_posts()
    # upload_post()
    # remove_dir()
