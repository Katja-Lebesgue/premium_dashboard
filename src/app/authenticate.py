import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml import SafeLoader


def is_admin():
    return st.session_state["username"] == "lebeg"


def save_yaml(config: dict):
    with open("config.yaml", "w") as file:
        yaml.dump(config, file, default_flow_style=False)


def load_yaml():
    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config


def authenticate():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        config = load_yaml()

        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
            config["preauthorized"],
        )

        name, authentication_status, username = authenticator.login("Login", "main")

        if st.session_state["authentication_status"] == False:
            st.error("Username/password is incorrect")
        elif st.session_state["authentication_status"] == None:
            st.warning("Please enter your username and password")

    return authenticator

    # if authentication_status:
    #     try:
    #         if authenticator.reset_password(username, 'Reset password'):
    #             st.success('Password modified successfully')
    #     except Exception as e:
    #         st.error(e)
