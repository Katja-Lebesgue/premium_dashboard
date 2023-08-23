import streamlit as st
from dotenv import load_dotenv
from streamlit_option_menu import option_menu
import warnings
import pandas as pd

load_dotenv()

import nltk

nltk.download("vader_lexicon")
nltk.download("stopwords")

from src.app import *
from src.app.authenticate import authenticate, is_admin
from src.app.tabs.admin_settings.admin_settings import admin_settings
from src.app.tabs.all_platforms import all_platforms
from src.app.tabs.facebook.market.image_analysis import image_analysis
from src.app.tabs.facebook.market.market_descriptive_statistics import market_descriptive_statistics
from src.app.tabs.facebook.market.market_performance_tests import market_performance_tests
from src.app.tabs.facebook.market.text_analysis import text_analysis
from src.app.tabs.facebook.shop.custom_performance_test import custom_performance_test
from src.app.tabs.facebook.shop.default_performance_tests import default_performance_tests
from src.app.tabs.facebook.shop.descriptive_statistics import descriptive_statistics
from src.app.tabs.facebook.shop.select_shop_and_load_data import select_shop_and_load_data
from src.app.tabs.google.google_market_descriptive_statistics import google_market_descriptive_statistics
from src.app.tabs.user_settings.reset_password import reset_password

st.set_page_config(layout="wide")

pd.set_option("mode.chained_assignment", None)


authenticator = authenticate()

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar")

    with st.sidebar:
        main_tab = option_menu(
            menu_title="Main menu",
            options=["All platforms", "Facebook", "Google", "Settings"],
            menu_icon="menu-app",
            icons=["arrows-fullscreen", "facebook", "google", "gear"],
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
                data_shop, selected_shop_id = select_shop_and_load_data()
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
                facebook_creative_shop_descriptive_tab.show(shop_id=selected_shop_id)

            if shop_subtab == "Default performance tests":
                default_performance_tests(data_shop)

            if shop_subtab == "Custom performance test":
                custom_performance_test(data_shop)

        if fb_subtab == "Market":
            with st.sidebar:
                market_subtab = option_menu(
                    menu_title="Market",
                    options=[
                        "Creative descriptive",
                        "Target descriptive",
                        "Default performance tests",
                        "Text analysis",
                        "Image analysis",
                    ],
                    menu_icon="globe",
                    icons=[
                        "brush",
                        "bullseye",
                        "lightning-fill",
                        "cursor-text",
                        "card-image",
                    ],
                    default_index=0,
                )

            if market_subtab == "Creative descriptive":
                facebook_creative_market_descriptive_tab.show()

            if market_subtab == "Target descriptive":
                facebook_target_market_descriptive_tab.show()

            if market_subtab == "Default performance tests":
                market_performance_tests()

            if market_subtab == "Text analysis":
                text_analysis()

            if market_subtab == "Image analysis":
                image_analysis()

    if main_tab == "Google":
        with st.sidebar:
            google_subtab = option_menu(
                menu_title="Google",
                options=["Descriptive statistics"],
                menu_icon="globe",
                icons=["pie-chart-fill"],
                default_index=0,
            )

        if google_subtab == "Descriptive statistics":
            google_campaign_type_market_descriptive_tab.show()

    if main_tab == "Settings":
        if is_admin():
            admin_settings(authenticator=authenticator)
        else:
            reset_password(authenticator=authenticator)
