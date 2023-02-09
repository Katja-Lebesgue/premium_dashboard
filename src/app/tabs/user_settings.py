import streamlit as st
from streamlit_option_menu import option_menu
import yaml


def user_settings(authenticator, config: dict):
    with st.sidebar:
        subtab = option_menu(
            menu_title="Settings",
            options=["Change password"],
            menu_icon="gear",
            icons=["hash"],
            default_index=0,
        )

    if subtab == "Change password":
        try:
            if authenticator.reset_password(st.session_state["username"], "Reset password"):
                st.success("Password modified successfully")
                config["credentials"] = authenticator.credentials
                with open("config.yaml", "w") as file:
                    yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)
