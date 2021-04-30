import pymongo
from src.Config import Config

config = Config()


def get_mongo_connection():
    myclient = pymongo.MongoClient(
        host=config["remotepath"]
    )  # , authSource="dissertation", username=config["username"], password=config["password"])
    return myclient["IR"]
