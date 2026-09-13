import os 
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL= os.getenv("DATABASE_URL")
ALGORITHM = os.getenv("ALGORITHM")
DEBUG = os.getenv("DEBUG","false").lower() == "true"