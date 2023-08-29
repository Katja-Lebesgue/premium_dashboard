from src.app.menus.my_option_menu import MyOptionMenu, MyButton
from src.app.tabs.settings import manage_users, manage_user_privileges, reset_password
from src.app.authenticate import is_admin

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
