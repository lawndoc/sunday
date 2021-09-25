import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "insanely-secret-default-key"
    MONGODB_SETTINGS = {
        "host": os.environ.get("DB_URI") or "mongodb://localhost/testStats"
    }
