from enum import Enum

from src.utils import get_enum_values


from enum import Enum


class TextType(str, Enum):
    description = "description"
    primary = "primary"
    title = "title"


class TextFeature(str, Enum):
    cta = "cta"
    discount = "discount"
    discount_list = "discount_list"
    emoji = "emoji"
    emoji_list = "emoji_list"
    fact_words = "fact_words"
    free_shipping = "free_shipping"
    hashtag = "hashtag"
    link = "link"
    percentage = "percentage"
    price = "price"
    starts_with_question = "starts_with_question"
    urgency = "urgency"
    user_addressing = "user_addressing"
    weasel_words = "weasel_words"
    button_cta_list = "button_cta_list"


class TargetFeature(str, Enum):
    target = "target"
    age_range = "age_range"
    number_of_custom_audiences = "number_of_custom_audiences"
    number_of_countries = "number_of_countries"
    targets_english = "targets_english"
    targets_US = "targets_US"
    audience = "audience"


class CreativeType(str, Enum):
    image = "image"
    video = "video"
    dynamic = "dynamic"
    carousel = "carousel"
    unknown = "unknown"


TARGET_FEATURES = get_enum_values(TargetFeature)


class CreativeType(str, Enum):
    image = "image"
    video = "video"
    dynamic = "dynamic"
    carousel = "carousel"
    unknown = "unknown"


BOOLEAN_TEXT_FEATURES = [feature for feature in get_enum_values(TextFeature) if "list" not in feature]
