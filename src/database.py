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

    def was_this_meme_already_downloaded(self, url: str) -> bool:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT *
            FROM "Log"
            WHERE "url" = %s AND "downloadStatus" = %s
            """, (url, "Completed"))
            self.conn.commit()

            if cursor.fetchone() is None:
                return False
        return True

    def get_title_of_meme(self, meme_uuid: uuid.UUID) -> str:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            SELECT "title"
            FROM "Log"
            WHERE "uuid" = %s
            """, (str(meme_uuid),))
            self.conn.commit()

            return cursor.fetchone()[0]

    def insert_log_started(self, url: str, title: str) -> uuid.UUID:
        self.uuid: uuid.UUID = uuid.uuid4()
        with self.conn.cursor() as cursor:
            cursor.execute("""
            INSERT INTO "Log" ("uuid", "url", "title", "startedAt", "finishedAt", "downloadStatus")
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.uuid, url, title, datetime.utcnow(), None, "Downloading"))
            self.conn.commit()
        return self.uuid

    def insert_log_finished(self, meme_uuid: uuid.UUID) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE "Log"
            SET "finishedAt" = %s, "downloadStatus" = %s
            WHERE "uuid" = %s
            """, (datetime.utcnow(), "Completed", str(meme_uuid)))
            self.conn.commit()

    def insert_log_failed(self, meme_uuid: uuid.UUID) -> None:
        with self.conn.cursor() as cursor:
            cursor.execute("""
            UPDATE "Log"
            SET "finishedAt" = %s, "downloadStatus" = %s
            WHERE "uuid" = %s
            """, (datetime.utcnow(), "Failed", str(meme_uuid)))
            self.conn.commit()
