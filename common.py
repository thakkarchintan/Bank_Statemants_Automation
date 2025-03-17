from auth import Authenticator
from constant_variables import *
from streamlit_cookies_manager import EncryptedCookieManager

authenticator = Authenticator(
    token_key=TOKEN_KEY,
    secret_path = SECRET_PATH,
    redirect_uri=REDIRECT_URI,
)

# test