import streamlit as st
from streamlit_option_menu import option_menu

from src.app.tabs.admin_settings.manage_user_privileges import manage_user_privileges
from src.app.tabs.admin_settings.manage_users import manage_users
from src import crud
from src.database.session import db


def admin_settings(authenticator):
    with st.sidebar:
        subtab = option_menu(
            menu_title="Settings",
            options=["Manage users", "Manage user privileges"],
            menu_icon="gear",
            icons=["person", "eye-slash"],
            default_index=0,
        )

    if subtab == "Manage users":
        manage_users()

    elif subtab == "Manage user privileges":
        manage_user_privileges()
