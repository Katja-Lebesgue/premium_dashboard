import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader

from src.database.session import db
from src.models.streamlit import StreamlitUser
from src.utils.database import row_to_dict
from loguru import logger


def is_admin():
    return st.session_state["is_superuser"]


def authenticate():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        config = get_username_config()

        authenticator = stauth.Authenticate(
            config,
            cookie_name="cookie_name",
            key="cookie_key",
            cookie_expiry_days=30,
        )

        name, authentication_status, username = authenticator.login("Login", "main")

        # st.write(config)

        if st.session_state["authentication_status"] == True:
            try:
                st.session_state["user_id"] = config["usernames"][st.session_state["username"]]["id"]
                st.session_state["is_superuser"] = config["usernames"][st.session_state["username"]]["is_superuser"]
            except Exception:
                authenticator.cookie_manager.delete(authenticator.cookie_name)
                st.session_state["logout"] = True
                st.session_state["name"] = None
                st.session_state["username"] = None
                st.session_state["authentication_status"] = None
                st.experimental_rerun()

        elif st.session_state["authentication_status"] == False:
            st.error("Username/password is incorrect")
        elif st.session_state["authentication_status"] == None:
            st.warning("Please enter your username and password")

    return authenticator


# @st.experimental_memo
def get_username_config():
    user_data = db.query(StreamlitUser).all()
    list_of_dicts = [row.__dict__ for row in user_data]
    result = {}
    for dic in list_of_dicts:
        username = dic["username"]
        dic["name"] = username
        dic["password"] = dic["hashed_password"]
        result[username] = dic
    return {"usernames": result}
