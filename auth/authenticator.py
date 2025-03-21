import time
from database import *
import streamlit as st
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from auth.token_manager import AuthTokenManager


class Authenticator:
    def __init__(
        self,
        secret_path: str,
        redirect_uri: str,
        token_key: str,
        cookie_name: str = "auth_jwt",
        token_duration_days: int = 1,
    ):
        st.session_state["connected"] = st.session_state.get("connected", False)
        self.secret_path = secret_path
        self.redirect_uri = redirect_uri
        self.auth_token_manager = AuthTokenManager(
            cookie_name=cookie_name,
            token_key=token_key,
            token_duration_days=token_duration_days,
        )
        self.cookie_name = cookie_name

    def _initialize_flow(self) -> google_auth_oauthlib.flow.Flow:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            self.secret_path,
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/userinfo.email",
            ],
            redirect_uri=self.redirect_uri,
        )
        return flow

    def get_auth_url(self) -> str:
        flow = self._initialize_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )
        return auth_url

    def login(self):
        # if not st.session_state["connected"]:
            auth_url = self.get_auth_url()
            return auth_url
            # css_button(auth_url)
            # st.sidebar.link_button("login with google", auth_url)
            
    

    def check_auth(self):
        def show_custom_toast(message):
            """Displays a toast message at a custom position."""
            toast_style = f"""
            <style>
                .custom-toast {{
                    position: fixed;
                    top: 10vh; left: 20px;
                    background-color: white;
                    color: green;
                    padding: 15px 25px;
                    border-radius: 8px;
                    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                    z-index: 9999;
                    display: flex;
                    align-items: center;
                }}
            </style>
            <div class="custom-toast">{message} ✅ </div>
            """
            toast_container = st.empty()
            toast_container.markdown(toast_style, unsafe_allow_html=True)
            time.sleep(3)
            toast_container.empty()
       
        if st.session_state["connected"]:
            # st.toast(":green[user is authenticated]")
            return

        if st.session_state.get("logout"):
            message = f"Successfully logged out"
            show_custom_toast(message)
            return

        token = self.auth_token_manager.get_decoded_token()
        if token is not None:
            # print(token)
            st.query_params.clear()
            st.session_state["connected"] = True
            st.session_state["user_info"] = {
                "email": token["email"],
                "oauth_id": token["oauth_id"],
            }
            st.rerun()  # update session state

        time.sleep(1)  # important for the token to be set correctly

        auth_code = st.query_params.get("code")
        st.query_params.clear()
        if auth_code:
            flow = self._initialize_flow()
            flow.fetch_token(code=auth_code)
            creds = flow.credentials

            oauth_service = build(serviceName="oauth2", version="v2", credentials=creds)
            user_info = oauth_service.userinfo().get().execute()
            oauth_id = user_info.get("id")
            email = user_info.get("email")
            
            self.auth_token_manager.set_token(email, oauth_id)
            st.session_state["connected"] = True
            st.session_state["user_info"] = user_info


    def logout(self):
        st.session_state["logout"] = True
        st.session_state["connected"] = None
        self.auth_token_manager.delete_token()
        # no rerun
