import logging
import psycopg2
import psycopg2.extras
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

HOSTNAME = os.getenv("POSTGRES_HOSTNAME")
PORT = os.getenv("POSTGRES_PORT")
USERNAME = os.getenv("POSTGRES_USERNAME")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DBNAME = os.getenv("POSTGRES_DBNAME")

psycopg2.extras.register_uuid()


class Database:

    def __init__(self) -> None:
        self.conn = None
        self.uuid = None

    def open_connection(self) -> None:
        try:
            self.conn = psycopg2.connect(
                f"host={HOSTNAME} port={PORT} dbname={DBNAME} user={USERNAME} password={PASSWORD}")
        except BaseException as e:
            print(f"Connection to the database {DBNAME} on host {HOSTNAME} with user {USERNAME} failed. Reason: {e}")

    def close_connection(self) -> None:
        self.conn.close()

    def was_this_post_already_downloaded(self, url: str) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT *
            FROM "DownloadLog"
            WHERE "url" = %s AND "downloadStatus" = %s
            """, (url, "Completed"))
            self.conn.commit()

            if cursor.fetchone() is None:
                return False
        return True

    def get_title_of_post(self, post_uuid: uuid.UUID) -> str:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT "title"
            FROM "DownloadLog"
            WHERE "uuid" = %s
            """, (str(post_uuid),))
            self.conn.commit()

            return cursor.fetchone()[0]

    def insert_download_log_started(self, url: str, title: str) -> uuid.UUID:
        self.uuid: uuid.UUID = uuid.uuid4()
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO "DownloadLog" ("uuid", "url", "title", "startedAt", "finishedAt", "downloadStatus")
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.uuid, url, title, datetime.utcnow(), None, "Downloading"))
            self.conn.commit()
        return self.uuid

    def insert_download_log_finished(self, post_uuid: uuid.UUID) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE "DownloadLog"
            SET "finishedAt" = %s, "downloadStatus" = %s
            WHERE "uuid" = %s
            """, (datetime.utcnow(), "Completed", str(post_uuid)))
            self.conn.commit()

    def insert_download_log_failed(self, post_uuid: uuid.UUID) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE "DownloadLog"
            SET "finishedAt" = %s, "downloadStatus" = %s
            WHERE "uuid" = %s
            """, (datetime.utcnow(), "Failed", str(post_uuid)))
            self.conn.commit()

    def was_this_post_already_posted(self, post_uuid: uuid.UUID) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT *
            FROM "PostLog"
            WHERE "uuid" = %s AND "postStatus" = %s
            """, (str(post_uuid), "Completed"))
            self.conn.commit()

            if cursor.fetchone() is None:
                return False
        return True

    def insert_post_log_started(self, post_uuid: uuid.UUID) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT *
            FROM "PostLog"
            WHERE uuid = %s
            """, (str(post_uuid),))
            self.conn.commit()

            if cursor.fetchone() is None:
                cursor.execute("""
                INSERT INTO "PostLog" ("uuid", "startedAt", "finishedAt", "postStatus", "errorMsg")
                VALUES (%s, %s, %s, %s, %s)
                """, (str(post_uuid), datetime.utcnow(), None, "Posting", None))
                self.conn.commit()
            else:
                cursor.execute("""
                UPDATE "PostLog"
                SET "startedAt" = %s, "finishedAt" = %s, "postStatus" = %s, errorMsg = %s
                WHERE "uuid" = %s
                """, (datetime.utcnow(), None, "Posting", None, str(post_uuid)))

    def insert_post_log_finished(self, post_uuid: uuid.UUID) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE "PostLog"
            SET "finishedAt" = %s, "postStatus" = %s
            WHERE "uuid" = %s
            """, (datetime.utcnow(), "Completed", str(post_uuid)))
            self.conn.commit()

    def insert_post_log_failed(self, post_uuid: uuid.UUID, error_msg: str) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE "PostLog"
            SET "finishedAt" = %s, "postStatus" = %s, "errorMsg" = %s
            WHERE "uuid" = %s
            """, (datetime.utcnow(), "Failed", error_msg, str(post_uuid)))
            self.conn.commit()

    def configure_db(self) -> None:
        logging.info("Configuring database if necessary...")

        self.open_connection()
        with self.conn.cursor() as cursor:
            cursor.execute("""
            ALTER TABLE IF EXISTS "Log"
            RENAME TO "DownloadLog"
            """)
            self.conn.commit()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS public."DownloadLog" (
                "uuid" TEXT PRIMARY KEY,
                "url" TEXT NOT NULL,
                "title" TEXT,
                "startedAt" TIMESTAMP NOT NULL,
                "finishedAt" TIMESTAMP,
                "downloadStatus" TEXT NOT NULL
            )
            """)
            self.conn.commit()

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS public."PostLog" (
	            "uuid" TEXT PRIMARY KEY,
	            "startedAt" TIMESTAMP NOT NULL,
	            "finishedAt" TIMESTAMP,
	            "postStatus" TEXT NOT NULL,
	            "errorMsg" TEXT
            )
            """)
            self.conn.commit()

        self.close_connection()
        logging.info("Finished!")
