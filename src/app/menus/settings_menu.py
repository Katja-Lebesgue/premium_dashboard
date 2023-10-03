from src.app.authenticate import is_admin
from src.app.menus.my_option_menu import MyButton, MyOptionMenu
from src.app.tabs.settings import (manage_user_privileges, manage_users,
                                   reset_password)

admin_settings_menu = MyOptionMenu(
    title="Settings",
    icon="gear",
    buttons=(
        MyButton(name="Manage users", icon="person", activation_function=manage_users),
        MyButton(name="Manage user privileges", icon="eye-slash", activation_function=manage_user_privileges),
    ),
)

user_settings_menu = MyOptionMenu(
    title="Settings",
    icon="gear",
    buttons=(MyButton(name="Reset password", icon="hash", activation_function=lambda x: reset_password),),
)
