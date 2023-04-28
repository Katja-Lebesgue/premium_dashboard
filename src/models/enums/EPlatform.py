from enum import Enum

from src.utils.enum import get_enum_values


class EPlatform(str, Enum):
    facebook = "facebook"
    tiktok = "tiktok"
    google = "google"


PLATFORMS = get_enum_values(EPlatform)
