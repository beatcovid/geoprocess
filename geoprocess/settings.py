import os

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.environ.get("REDIS_HOST", default="127.0.0.10")

GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY")

MONGO_CONNECT_URL = os.environ.get("MONGO_CONNECT_URL")
