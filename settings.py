import os


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///yacut.db")
    SECRET_KEY = os.getenv("SECRET_KEY", "MY_SECRET_KEY")
    DISK_TOKEN = os.getenv("DISK_TOKEN")
