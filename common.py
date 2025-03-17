from auth import Authenticator
from dotenv import load_dotenv
import os
from constant_variables import *
from streamlit_cookies_manager import EncryptedCookieManager

authenticator = Authenticator(
    token_key=TOKEN_KEY,
    secret_path = SECRET_PATH,
    redirect_uri=REDIRECT_URI,
)