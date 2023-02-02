from src.schemas.api_model import APIModel
from src.schemas.shopify.shopify_product import ShopifyProductAPI


class ShopCopywriterConfig(APIModel):
    # english_language: bool
    enough_historical_ads: bool
    # available_credits: int
    # suggestions_generated: int
    # days_left: int
    website_url: str
    # terms_of_service_read: bool


class CopywriterProductGroup(APIModel):
    title: str
    tag_label: str
    product_list: list[int]


class TaggedProducts(APIModel):
    orders_best: CopywriterProductGroup
    orders_worst: CopywriterProductGroup
    revenue_best: CopywriterProductGroup
    revenue_worst: CopywriterProductGroup
    ltv_best: CopywriterProductGroup
    ltv_worst: CopywriterProductGroup


class ShopCopywriterProducts(APIModel):
    tagged_products: TaggedProducts
    all_products: list[ShopifyProductAPI]


class ShopCopywriterReaction(APIModel):
    value: int
