from src.schemas.api_model import APIModel


class FacebookCreativeFeaturesBase(APIModel):
    creative_id: str
    creative_type: str

    # texts
    title: list
    primary: list
    description: list

    # text features
    user_addressing: bool
    starts_with_question: bool
    urgency: bool
    emoji: bool
    emojis_list: list[str]
    hashtag: bool
    fact_words: bool
    link: bool
    percentage: bool
    free_shipping: bool
    discount: bool
    discount_list: list[int]
    prices: bool
    cta: bool
    weasel_words: bool
    buttton_cta_list: list[str]

    # target features
    target: str
    targets_US: bool
    number_of_custom_audiences: int
    targets_english: bool
    age_range: int
    number_of_countries: int


class FacebookCreativeFeaturesCreate(FacebookCreativeFeaturesBase):
    shop_id: int
    account_id: str
    ad_id: str


class FacebookCreativeFeaturesUpdate(FacebookCreativeFeaturesBase):
    pass
