import re
import string
import emoji


def clean_text(text: str) -> str:
    # text = text.replace("\n", " ")

    for fun in [
        remove_URL,
        remove_html,
        remove_hashtags,
        # remove_backslashes,
        # remove_emojis,
        # remove_punct,
    ]:
        text = fun(text)

    text = text.replace("\n", " ")
    return text


def remove_URL(text: str) -> str:
    url = re.compile(r"https?://\S+|www\.\S+")
    return url.sub(r"", text)


def remove_forbidden_punctation_for_hf(text: str):
    return re.sub(r"[-|.|:|;]+", "_", text)


def remove_hashtags(text: str) -> str:
    hashtag = re.compile(r"#\S+")
    return hashtag.sub(r"", text)


def remove_html(text: str) -> str:
    html = re.compile(r"<.*?>")
    return html.sub(r"", text)


def remove_emojis(text: str) -> str:
    delimiter = "#4="
    for i in range(5):
        text = emoji.demojize(string=text, delimiters=(delimiter, delimiter))
    text = re.sub(f"{delimiter}\S+{delimiter}", "", text)
    return text


def remove_punct(text):
    table = str.maketrans("", "", string.punctuation)
    return text.translate(table)


def remove_backslashes(text: str) -> str:
    backslash = re.compile(r"\\\S+")
    return backslash.sub(r"", text)
