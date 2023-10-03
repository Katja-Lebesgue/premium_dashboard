import streamlit as st

from src.app.frontend_names import get_frontend_name


def checkbox_menu(
    labels: list | None = None, true_labels: list = [], label_value_dict: dict | None = None, key: str = ""
) -> list:
    if labels is None and label_value_dict is None:
        raise ValueError("Labels must be specified as list or dict.")
    if label_value_dict is None:
        if not len(true_labels):
            true_labels = labels
        label_value_dict = {label: label in true_labels for label in labels}

    selected_labels = []
    for label, value in label_value_dict.items():
        check = st.checkbox(label=get_frontend_name(label), value=value, key=f"{label}_{key}")
        if check:
            selected_labels.append(label)
    return selected_labels
