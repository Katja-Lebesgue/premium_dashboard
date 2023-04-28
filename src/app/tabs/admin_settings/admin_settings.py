import pandas as pd
import streamlit as st
import yaml
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import false
from streamlit_option_menu import option_menu

from src.app.tabs.admin_settings.manage_user_privileges import \
    manage_user_privileges
from src.app.tabs.admin_settings.manage_users import manage_users
from src.crud import crud_streamlit_user
from src.database.session import db
from src.models import StreamlitUser
from src.utils.hash_password import hash_password


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
