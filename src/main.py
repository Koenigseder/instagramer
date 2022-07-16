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


db_client = database.Database()
reddit_client = reddit.Reddit()
instagram_client = instagram.Instagram()

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)


def download_memes():
    logging.info("Downloading memes...")
    db_client.open_connection()

    reddit_client.auth_for_reddit()
    list_of_memes = reddit_client.get_list_of_urls_and_titles_of_daily_top_memes("memes", db_client)

    if len(list_of_memes) > 0:
        for meme in list_of_memes:
            url, title = meme
            meme_uuid = db_client.insert_log_started(url, title)

            try:
                reddit_client.download_meme(url, str(date.today()), meme_uuid)
                db_client.insert_log_finished(meme_uuid)

            except BaseException as e:
                db_client.insert_log_failed(meme_uuid)
                logging.error(f"An error occurred while downloading a meme: {e}")

    db_client.close_connection()
    logging.info("Download finished!")


def upload_meme():
    logging.info("Uploading meme to Instagram...")
    folder = str(date.today() - timedelta(days=1))
    path = os.path.join(os.pardir, "resources", folder)

    if os.path.exists(path):
        for file in listdir(path):
            if file.endswith(".mp4") or file.endswith(".gif") or file.endswith(".jpg"):
                try:
                    db_client.open_connection()
                    caption = db_client.get_title_of_meme(uuid.UUID(file.split(".")[0]))
                    db_client.close_connection()

                    instagram_client.upload_to_instagram(folder, file, caption)
                    for item in listdir(path):
                        if file.split(".")[0] in item:
                            os.remove(os.path.join(path, item))
                    logging.info("Upload finished!")
                    break

                except BaseException as e:
                    logging.error(f"An error occurred while uploading the meme to Instagram: {e}")
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


schedule.every().day.at("22:00").do(download_memes)

schedule.every().day.at("23:00").do(remove_dir)

schedule.every().day.at("06:00").do(upload_meme)
schedule.every().day.at("09:00").do(upload_meme)
schedule.every().day.at("12:00").do(upload_meme)
schedule.every().day.at("15:00").do(upload_meme)
schedule.every().day.at("18:00").do(upload_meme)
schedule.every().day.at("21:00").do(upload_meme)


def start_instagramer():
    logging.info("### Instagramer started! ###")
    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    start_instagramer()
    # download_memes()
    # upload_meme()
    # remove_dir()
