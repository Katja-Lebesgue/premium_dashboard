import streamlit as st

from src.app.menus.my_option_menu import MyOptionMenu, MyButton
from src.app.menus.google_menu import google_menu
from src.app.menus.facebook_menu import facebook_menu
from src.app.menus.settings_menu import admin_settings_menu, user_settings_menu
from src.app.authenticate import is_admin
from src.app.tabs import *


def get_settings_menu():
    if is_admin():
        return admin_settings_menu
    else:
        return user_settings_menu


def get_main_menu():
    return MyOptionMenu(
        title="Main menu",
        icon="menu-app",
        buttons=(
            MyButton(name="All channels", icon="arrows-fullscreen", activation_function=all_platforms),
            MyButton(name="Google", icon="google", activation_function=google_menu.show),
            MyButton(name="Facebook", icon="facebook", activation_function=facebook_menu.show),
            MyButton(name="Settings", icon="gear", activation_function=get_settings_menu().show),
        ),
        default_index=2,
    )
