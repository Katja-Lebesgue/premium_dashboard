import pandas as pd
from dotenv import load_dotenv


load_dotenv()


def extract_text_and_type(creative: pd.Series) -> pd.Series:

    creative.bodies = none_to_list(creative.bodies)
    creative.descriptions = none_to_list(creative.descriptions)
    creative.titles = none_to_list(creative.titles)
    creative.children = none_to_list(creative.children)
    creative.images = none_to_list(creative.images)
    creative.videos = none_to_list(creative.videos)
    creative.cta_types = none_to_list(creative.cta_types)

    creative = get_primary(creative)
    creative = get_description(creative)
    creative = get_title(creative)
    creative = get_dynamic_price(creative)

    creative = get_creative_type(creative)
    creative = get_cta(creative)

    return creative


def none_to_list(a):
    if a is not None:
        return a
    else:
        return []


def get_primary(creative: pd.Series) -> pd.Series:

    # bodies -> text
    bodies_text = [body["text"] for body in creative.bodies if "text" in body]

    # other primaries
    primary = [
        creative.body,
        creative.video_message,
        creative.link_message,
        creative.template_message,
    ]
    primary.extend(bodies_text)
    primary = [text for text in primary if text is not None and len(text) > 0]

    # removing duplicates
    creative["primary"] = list(set(primary))

    return creative


def get_description(creative: pd.Series) -> pd.Series:

    # descriptions
    extra_descriptions = [
        description["text"]
        for description in creative.descriptions
        if "text" in description
    ]

    # children -> description
    children_descriptions = [
        child["description"] for child in creative.children if "description" in child
    ]

    description = [
        creative.link_description,
        creative.video_description,
        creative.template_description,
    ]
    description.extend(extra_descriptions)
    description.extend(children_descriptions)
    description = [text for text in description if text is not None and len(text) > 0]

    # removing duplicates
    creative["description"] = list(set(description))

    return creative


def get_title(creative: pd.Series) -> pd.Series:

    # titles -> text
    extra_titles = [title["text"] for title in creative.titles]

    # children -> name
    children_names = [child["name"] for child in creative.children if "name" in child]

    children_names = []

    # other titles
    title = [creative.video_title, creative.link_name, creative.template_name]
    title.extend(extra_titles)
    title.extend(children_names)
    title = [text for text in title if text is not None and len(text) > 0]

    # removing duplicates
    creative["title"] = list(set(title))

    return creative


def get_dynamic_price(creative: pd.Series) -> pd.Series:

    cond1 = any(
        [
            ("product.price" in description or "product.current_price" in description)
            for description in creative.description
        ]
    )
    cond2 = creative.template_name is not None and (
        "product.price" in creative.template_name
        or "product.current_price" in creative.template_name
    )

    if cond1 or cond2:
        creative["has_dynamic_price"] = True
    else:
        creative["has_dynamic_price"] = False

    return creative


def get_creative_type(creative: pd.Series) -> pd.Series:

    if (
        (creative.ad_formats and "CAROUSEL" in creative.ad_formats)
        or (creative.ad_formats and "COLLECTION" in creative.ad_formats)
        or (creative.ad_formats and "CAROUSEL_IMAGE" in creative.ad_formats)
        or (creative.multi_share_end_card is not None)
        or len(creative.children)
    ):
        creative_type = "carousel"
    elif any(
        [
            len(creative.primary) > 1,
            len(creative.description) > 1,
            len(creative.title) > 1,
            len(creative.images) + len(creative.videos) > 1,
        ]
    ):
        creative_type = "dynamic"
    elif any(
        [
            creative.video_id,
            creative.video_description,
            creative.video_title,
            creative.video_message,
        ]
    ):
        creative_type = "video"
    elif creative.image_hash or len(creative.images):
        creative_type = "image"
    else:
        creative_type = None

    creative["creative_type"] = creative_type

    return creative


def get_cta(creative: pd.Series) -> pd.Series:

    children_ctas = [
        child["call_to_action"]["type"]
        for child in creative.children
        if "call_to_action" in child
    ]

    cta = creative.cta_types

    if creative.link_cta is not None:
        cta.append(creative.link_cta)

    if creative.video_cta is not None:
        cta.append(creative.video_cta)

    if creative.template_cta is not None:
        cta.append(creative.template_cta)

    cta.extend(children_ctas)
    creative["cta"] = cta

    return creative
