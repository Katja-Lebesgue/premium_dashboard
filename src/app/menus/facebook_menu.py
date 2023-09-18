import streamlit as st

from src.app.menus.my_option_menu import MyOptionMenu, MyButton
from src.app.tabs import *
from src.app.menus.utils import select_shop


facebook_shop_menu = MyOptionMenu(
    title="Shop",
    icon="shop",
    buttons=(
        MyButton(
            name="Creative",
            icon="brush",
            activation_function=facebook_creative_shop_descriptive_tab.show,
        ),
        MyButton(
            name="Target",
            icon="bullseye",
            activation_function=facebook_target_shop_descriptive_tab.show,
        ),
        MyButton(name="Ad analytics", icon="zoom-in", activation_function=ad_analytics_tab),
        MyButton(
            name="Default tests", icon="lightning-fill", activation_function=shop_default_performance_tests
        ),
        MyButton(name="Custom test", icon="lightbulb", activation_function=shop_custom_performance_test),
    ),
)

facebook_market_menu = MyOptionMenu(
    title="Shop",
    icon="shop",
    buttons=(
        MyButton(
            name="Creative",
            icon="brush",
            activation_function=facebook_creative_market_descriptive_tab.show,
        ),
        MyButton(
            name="Target",
            icon="bullseye",
            activation_function=facebook_target_market_descriptive_tab.show,
        ),
        MyButton(
            name="Text",
            icon="cursor-text",
            activation_function=text_analysis,
        ),
        MyButton(
            name="Image",
            icon="card-image",
            activation_function=facebook_image_market_descriptive_tab.show,
        ),
        MyButton(name="Default tests", icon="lightning-fill", activation_function=market_performance_tests),
    ),
)


def shop_button_activation():
    with st.sidebar:
        shop_id = select_shop()
    facebook_shop_menu.show(shop_id=shop_id)


facebook_menu = MyOptionMenu(
    title="Facebook",
    icon="facebook",
    buttons=(
        MyButton(name="Shop", icon="shop", activation_function=shop_button_activation),
        MyButton(name="Market", icon="globe", activation_function=facebook_market_menu.show),
    ),
    default_index=1,
)
