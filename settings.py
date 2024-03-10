from sqlalchemy import URL
from dotenv import load_dotenv
import os

load_dotenv(override=True)


def get_be_url():
    return os.getenv("BE_URL")


def get_fe_url():
    return os.getenv("FE_URL")


def get_upload_dir():
    return os.getenv("UPLOAD_DIR")


def get_access_token_expire_minutes():
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    return int(float(ACCESS_TOKEN_EXPIRE_MINUTES))


def get_secret_key():
    return os.getenv("SECRET_KEY")


def get_algorithm():
    return os.getenv("ALGORITHM")


def get_sqlalchemy_database_url():

    SQLALCHEMY_DATABASE_URL = URL.create(
        "postgresql",
        username="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port=5432,
        database="hojin-bucket",
    )

    return SQLALCHEMY_DATABASE_URL


def get_sqlalchemy_database_url_async():

    SQLALCHEMY_DATABASE_URL_ASYNC = URL.create(
        "postgresql+asyncpg",
        username="postgres",
        password=os.getenv("POSTGRES_PASSWORD"),
        host="localhost",
        port=5432,
        database="hojin-bucket",
    )

    return SQLALCHEMY_DATABASE_URL_ASYNC
