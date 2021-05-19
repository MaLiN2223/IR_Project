import os


def is_prod():
    try:
        return os.environ["FLASK_ENV"] == "production"
    except:  # noqa
        return False
