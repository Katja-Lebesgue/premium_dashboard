import inspect
from typing import Callable, Iterable

import streamlit as st
from streamlit_option_menu import option_menu

from src.app.frontend_names import get_frontend_name


class MyButton:
    def __init__(self, name: str, icon: str, activation_function: Callable):
        self.name = name
        self.icon = icon
        self.activate = activation_function


class MyOptionMenu:
    def __init__(self, title: str, icon: str, buttons: Iterable[MyButton], default_index: int = 0):
        self.title = title
        self.icon = icon
        self.default_index = default_index
        self.buttons = buttons

    @property
    def option_menu(self):
        return option_menu(
            menu_title=get_frontend_name(self.title),
            options=[button.name for button in self.buttons],
            menu_icon=self.icon,
            icons=[button.icon for button in self.buttons],
            default_index=self.default_index,
        )

    def show(self, sidebar: bool = True, **kwargs):
        if sidebar:
            with st.sidebar:
                selected = self.option_menu
        else:
            selected = self.option_menu
        for button in self.buttons:
            if selected == button.name:
                filtered_kwargs = {
                    k: v for k, v in kwargs.items() if k in inspect.getfullargspec(button.activate).args
                }
                button.activate(**filtered_kwargs)
