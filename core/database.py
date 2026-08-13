import os

from pymongo import MongoClient


MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "ims_database")


client = MongoClient(MONGODB_URI)

db = client[MONGODB_DATABASE]