from enum import Enum
from typing import Any, Callable

import pandas as pd
import streamlit as st

from src.app.frontend_names import get_frontend_name


class FilterType(str, Enum):
    slider = "slider"
    selectbox = "selectbox"
    checkbox = "checkbox"


def filter_df(
    df: pd.DataFrame,
    column_name: str,
    filter_type: FilterType,
    frontend_column_name: str | None = None,
    selecter_id: str = "",
    format_func: Callable = get_frontend_name,
    add_expander_for_checkbox: bool = True,
    slider_default_lower_bound: Any | None = None,
    slider_default_upper_bound: Any | None = None,
    **kwargs,
):
    if frontend_column_name is None:
        frontend_column_name = column_name
    frontend_column_name = get_frontend_name(frontend_column_name)

    label = f"Select {frontend_column_name}"
    options = [value for value in df[column_name].unique() if value is not None]
    selector_kwargs = {
        "label": label,
        "key": column_name + "_" + selecter_id,
        "format_func": format_func,
    } | kwargs

    match filter_type:
        case FilterType.slider:
            min_value = df[column_name].min()
            max_value = df[column_name].max()
            if slider_default_lower_bound is not None:
                slider_default_lower_bound = max(min_value, slider_default_lower_bound)
            else:
                slider_default_lower_bound = min_value
            if slider_default_upper_bound is not None:
                slider_default_upper_bound = min(max_value, slider_default_upper_bound)
            else:
                slider_default_upper_bound = max_value
            lower_bound, upper_bound = st.select_slider(
                options=sorted(options),
                value=(slider_default_lower_bound, slider_default_upper_bound),
                **selector_kwargs,
            )

            return df[df[column_name].between(lower_bound, upper_bound)]

        case FilterType.selectbox:
            value = st.selectbox(options=options, **selector_kwargs)
            return df[df[column_name] == value]

        case FilterType.checkbox:
            options = [value for value in df[column_name].unique() if value is not None]
            allowed_values = []

            expander = st.expander(label)

            if add_expander_for_checkbox:
                expander.__enter__()
            else:
                st.write(label)

            for value in options:
                check = st.checkbox(
                    label=format_func(value),
                    value=True,
                    key=f"{column_name}_{value}_{selecter_id}",
                )
                if check:
                    allowed_values.append(value)

            if add_expander_for_checkbox:
                expander.__exit__(type=None, value=None, traceback=None)

            return df[df[column_name].isin(allowed_values)]

        case _:
            return df
