from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()

client = MongoClient(os.getenv("DATABASE_URL"))
db = client.user
collection = db["user_collection"]
