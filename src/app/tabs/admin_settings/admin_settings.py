import streamlit as st
from streamlit_option_menu import option_menu
import yaml
import pandas as pd

from src.database.session import db
from src.crud import crud_streamlit_user
from sqlalchemy.sql.expression import false
from src.utils.hash_password import hash_password
from src.app.tabs.admin_settings.manage_users import manage_users
from src.app.tabs.admin_settings.manage_user_privileges import manage_user_privileges
from src.models import StreamlitUser

from sqlalchemy.exc import IntegrityError


def admin_settings(authenticator):
    with st.sidebar:
        subtab = option_menu(
            menu_title="Settings",
            options=["Manage users", "Manage user privileges"],
            menu_icon="gear",
            icons=["person", "eye-slash"],
            default_index=0,
        )

    users = crud_streamlit_user.ping_all_subusernames(db=db)

    if subtab == "Manage users":
        manage_users()

    elif subtab == "Manage user privileges":
        manage_user_privileges()
