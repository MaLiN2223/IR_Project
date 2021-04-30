from ..Config import Config
from src.storage.utils import get_mongo_connection
import pymongo

config = Config.get_config()

mydb = get_mongo_connection()

websites_db = mydb["Websites"]
