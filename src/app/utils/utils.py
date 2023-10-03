from typing import Any, Callable

import streamlit as st


@st.cache_data
def st_cache_data(_func: Callable, func_name: str, **kwargs) -> Any:
    kwargs = {k.removeprefix("_"): v for k, v in kwargs.items()}
    return _func(**kwargs)
