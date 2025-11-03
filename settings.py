import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///yacut.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "MY_SECRET_KEY")
    DISK_TOKEN = os.getenv("DISK_TOKEN")
    API_VERSION = os.getenv("API_VERSION", "v1")
    YANDEX_API_BASE = os.getenv(
        "YANDEX_API_BASE", "https://cloud-api.yandex.net"
    )
