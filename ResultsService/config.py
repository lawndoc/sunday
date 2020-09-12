import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "insanely-secret-default-key"
    DB_USER = os.environ.get("DB_USER") or None
    DB_PASS = os.environ.get("DB_PASS") or None
    DB = os.environ.get("DB") or None
    DATABASE_URI = os.environ.get("DATABASE_URI") or None
    LOCALDB = "xcstats20"
