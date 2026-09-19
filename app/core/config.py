import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
DEBUG = os.getenv("DEBUG","false").lower() == "true"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES")