import streamlit as st
from streamlit_option_menu import option_menu
from dotenv import load_dotenv
import yaml
from yaml import SafeLoader
from loguru import logger

load_dotenv()

from src.app.tabs.facebook.shop.descriptive_statistics import descriptive_statistics
from src.app.select_shop_and_load_data import select_shop_and_load_data
from src.app.tabs.admin_settings.admin_settings import admin_settings
from src.app.tabs.user_settings.reset_password import reset_password
from src.app.tabs.facebook.market.text_analysis import text_analysis

from src.app.tabs.facebook.shop.default_performance_tests import default_performance_tests
from src.app.tabs.facebook.shop.custom_performance_test import custom_performance_test
from src.app.tabs.facebook.market.market_performance_tests import market_performance_tests
from src.app.tabs.facebook.market.market_descriptive_statistics import market_descriptive_statistics
from src.app.tabs.all_platforms import all_platforms
from src.app.authenticate import authenticate, is_admin
from src.database.session import SessionLocal


st.set_page_config(layout="wide")

logger.debug("poceli smo")

authenticator = authenticate()

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")

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
            fb_subtab = option_menu(
                menu_title="Main menu",
                options=["Shop", "Market"],
                menu_icon="menu-app",
                icons=["shop", "globe"],
                default_index=1,
            )

        if fb_subtab == "Shop":
            with st.sidebar:
                data_shop = select_shop_and_load_data()
                shop_subtab = option_menu(
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

            if shop_subtab == "Descriptive statistics":
                descriptive_statistics(data_shop)

            if shop_subtab == "Default performance tests":
                default_performance_tests(data_shop)

            if shop_subtab == "Custom performance test":
                custom_performance_test(data_shop)

        if fb_subtab == "Market":
            with st.sidebar:
                market_subtab = option_menu(
                    menu_title="Market",
                    options=["Descriptive statistics", "Default performance tests", "Text analysis"],
                    menu_icon="globe",
                    icons=["pie-chart-fill", "lightning-fill", "cursor-text"],
                    default_index=0,
                )

            if market_subtab == "Descriptive statistics":
                market_descriptive_statistics()

            if market_subtab == "Default performance tests":
                market_performance_tests()

            if market_subtab == "Text analysis":
                text_analysis()

    if main_tab == "Settings":
        if is_admin():
            admin_settings(authenticator=authenticator)
        else:
            reset_password(authenticator=authenticator)
