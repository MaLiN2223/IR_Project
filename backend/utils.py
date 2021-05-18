import os


def is_prod():
    return os.environ["FLASK_ENV"] == "production"
