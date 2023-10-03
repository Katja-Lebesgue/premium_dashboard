import streamlit as st

from src.app.menus.my_option_menu import MyButton, MyOptionMenu
from src.app.menus.utils import select_shop
from src.app.tabs.descriptive_tab import (
    google_campaign_type_market_descriptive_tab,
    google_campaign_type_shop_descriptive_tab)

google_shop_menu = MyOptionMenu(
    title="Shop",
    icon="shop",
    buttons=(
        MyButton(
            name="Campaign type",
            icon="pie-chart-fill",
            activation_function=google_campaign_type_shop_descriptive_tab.show,
        ),
    ),
)

google_market_menu = MyOptionMenu(
    title="Market",
    icon="globe",
    buttons=(
        MyButton(
            name="Campaign type",
            icon="pie-chart-fill",
            activation_function=google_campaign_type_market_descriptive_tab.show,
        ),
    ),
)


def shop_button_activation():
    with st.sidebar:
        shop_id = select_shop()
    google_campaign_type_shop_descriptive_tab.show(shop_id=shop_id)


google_menu = MyOptionMenu(
    title="Google",
    icon="Google",
    buttons=(
        MyButton(name="Shop", icon="shop", activation_function=shop_button_activation),
        MyButton(
            name="Market", icon="globe", activation_function=google_campaign_type_market_descriptive_tab.show
        ),
    ),
)
