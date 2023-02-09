import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import yaml
from yaml import SafeLoader

load_dotenv()

from src.app.tabs.descriptive_statistics import descriptive_statistics
from src.app.select_shop_and_load_data import select_shop_and_load_data
from src.app.tabs.admin_settings import admin_settings
from src.app.tabs.user_settings import user_settings

from src.app.tabs.default_performance_tests import default_performance_tests
from src.app.tabs.custom_performance_test import custom_performance_test
from src.app.tabs.market_performance_tests import market_performance_tests
from src.app.tabs.market_descriptive_statistics import market_descriptive_statistics
from src.app.tabs.all_platforms import all_platforms
from src.app.authenticate import authenticate, is_admin
from src.database.session import SessionLocal


st.set_page_config(layout="wide")

authenticator = authenticate()

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")

    with open("config.yaml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    with st.sidebar:

        main_tab = option_menu(
            menu_title="Main menu",
            options=["All platforms", "Facebook", "Settings"],
            menu_icon="menu-app",
            icons=["arrows-fullscreen", "facebook", "gear"],
            default_index=1,
        )

    if main_tab == "All platforms":
        all_platforms()

    if main_tab == "Facebook":
        with st.sidebar:
            subtab1 = option_menu(
                menu_title="Main menu",
                options=["Shop", "Market"],
                menu_icon="menu-app",
                icons=["shop", "globe"],
                default_index=1,
            )

        if subtab1 == "Shop":
            with st.sidebar:
                data_shop = select_shop_and_load_data()
                subtab2 = option_menu(
                    menu_title="Shop",
                    options=[
                        "Descriptive statistics",
                        "Default performance tests",
                        "Custom performance test",
                    ],
                    menu_icon="shop",
                    icons=["pie-chart-fill", "lightning-fill", "lightbulb"],
                    default_index=0,
                )

            if subtab2 == "Descriptive statistics":
                descriptive_statistics(data_shop)

            if subtab2 == "Default performance tests":
                default_performance_tests(data_shop)

            if subtab2 == "Custom performance test":
                custom_performance_test(data_shop)

        if subtab1 == "Market":
            with st.sidebar:
                subtab2 = option_menu(
                    menu_title="Market",
                    options=[
                        "Descriptive statistics",
                        "Default performance tests",
                    ],
                    menu_icon="globe",
                    icons=["pie-chart-fill", "lightning-fill"],
                    default_index=0,
                )

            if subtab2 == "Descriptive statistics":
                market_descriptive_statistics()

            if subtab2 == "Default performance tests":
                market_performance_tests()

    if main_tab == "Settings":

        if is_admin():
            admin_settings(authenticator=authenticator, config=config)
        else:
            user_settings(authenticator=authenticator, config=config)
