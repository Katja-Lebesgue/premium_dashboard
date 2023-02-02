import streamlit as st
from streamlit_option_menu import option_menu
import os
from dotenv import load_dotenv
import nltk

load_dotenv()

from src.app.tabs.descriptive_statistics import descriptive_statistics
from src.app.select_shop_and_load_data import select_shop_and_load_data

from src.app.tabs.default_performance_tests import default_performance_tests
from src.app.tabs.custom_performance_test import custom_performance_test
from src.app.tabs.market_performance_tests import market_performance_tests
from src.app.tabs.market_descriptive_statistics import market_descriptive_statistics


st.set_page_config(layout="wide")


with st.sidebar:

    shop_or_market = option_menu(
        menu_title="Main menu",
        options=["Shop", "Market"],
        menu_icon="menu-app",
        icons=["shop", "globe"],
        default_index=1,
    )

if shop_or_market == "Shop":
    with st.sidebar:
        data_shop = select_shop_and_load_data()
        selected = option_menu(
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

    if selected == "Descriptive statistics":
        descriptive_statistics(data_shop)

    if selected == "Default performance tests":
        default_performance_tests(data_shop)

    if selected == "Custom performance test":
        custom_performance_test(data_shop)


if shop_or_market == "Market":
    with st.sidebar:
        selected = option_menu(
            menu_title="Market",
            options=[
                "Descriptive statistics",
                "Default performance tests",
            ],
            menu_icon="globe",
            icons=["pie-chart-fill", "lightning-fill"],
            default_index=0,
        )

    if selected == "Descriptive statistics":
        market_descriptive_statistics()

    if selected == "Default performance tests":
        market_performance_tests()
