import os
from dotenv import load_dotenv

load_dotenv()
# load_dotenv(dotenv_path="/home/ec2-user/app/.env")

TOKEN_KEY = os.getenv("TOKEN_KEY")
DATABASE_TYPE = os.getenv("DATABASE_TYPE")
DBAPI = os.getenv("DBAPI")
HOST = os.getenv("HOST")
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
DATABASE = os.getenv("DATABASE")
PORT = 3306
email_pass = os.getenv("email_pass")
ADMIN_EMAIL1 = os.getenv("ADMIN_EMAIL1")
ADMIN_EMAIL2 = os.getenv("ADMIN_EMAIL2")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_USER = os.getenv("SMTP_USER")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
SECRET_PATH = os.getenv("SECRET_PATH")
REDIRECT_URI = os.getenv("REDIRECT_URI")
DUMMY_DATA_PATH = os.getenv("DUMMY_DATA_PATH")
DUMMY_DATA_SUMMARY_PATH = os.getenv("DUMMY_DATA_SUMMAY_PATH")