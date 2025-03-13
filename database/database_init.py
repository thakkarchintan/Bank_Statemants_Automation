import mysql.connector
import logging
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, text


# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

db_host = os.getenv("HOST")
db_user = os.getenv("USER")
db_password = os.getenv("PASSWORD")
db_name = os.getenv("DATABASE_NAME")