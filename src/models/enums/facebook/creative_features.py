from enum import Enum

from src.utils import get_enum_values


class TextType(str, Enum):
    description = "description"
    primary = "primary"
    title = "title"


class TextFeature(str, Enum):
    cta = "cta"
    discount = "discount"
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


class TargetFeature(str, Enum):
    target = "target"
    age_range = "age_range"
    number_of_custom_audiences = "number_of_custom_audiences"
    number_of_countries = "number_of_countries"
    targets_english = "targets_english"
    targets_US = "targets_US"


class CreativeType(str, Enum):
    image = "image"
    video = "video"
    dynamic = "dynamic"
    carousel = "carousel"
    unknown = "unknown"


BOOLEAN_TEXT_FEATURES = list(set(get_enum_values(TextFeature)).difference({TextFeature.emoji_list}))
