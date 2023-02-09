import streamlit as st
from streamlit_option_menu import option_menu
import yaml


def admin_settings(authenticator, config: dict):
    with st.sidebar:
        subtab = option_menu(
            menu_title="Settings",
            options=["Add/remove user"],
            menu_icon="gear",
            icons=["person"],
            default_index=0,
        )

    st.write(st.session_state)

    if subtab == "Add/remove user":
        st.write(authenticator.register_user("Register user", preauthorization=False)["username"])
        # try:
        #     if authenticator.register_user("Register user", preauthorization=False):
        #         st.success("User registered successfully")
        #         config["credentials"] = authenticator.credentials
        #         st.write(authenticator.register_user("Register user", preauthorization=False))
        #         with open("config.yaml", "w") as file:
        #             yaml.dump(config, file, default_flow_style=False)
        # except Exception as e:
        #     st.error(e)
