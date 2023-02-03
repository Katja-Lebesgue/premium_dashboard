import sys

sys.path.append("./.")

from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.api import FacebookAdsApi
import psycopg2
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.ad import Ad
from datetime import date, datetime
import pandas as pd
from dotenv import load_dotenv
import numpy as np
import nltk
import emojis
import re
from price_parser import Price


def get_emojis(text: str) -> list:
    # tokens = nltk.word_tokenize(text)
    # list_with_nones = [emojis.get(token) for token in tokens]
    list_with_nones = [emojis.get(symbol) for symbol in text]
    return [emo.pop() for emo in list_with_nones if len(emo)]


def has_urgency(text: str) -> bool:
    urgency_phrases = [
        "limited time",
        "limited quantity",
        "limited edition",
        "shop now",
        "now!",
        "order now",
        "limited in stock",
        "limited collection",
        "low on stock",
        "order your samples today",
    ]
    return any([phrase.upper() in text.upper() for phrase in urgency_phrases])


def has_free_shipping(text: str) -> bool:
    free_shipping_phrases = [
        "free shipping",
        "free international shipping",
        "free domestic shipping",
        "free delivery",
        "free international delivery",
        "free domestic delivery",
    ]
    return any([phrase.upper() in text.upper() for phrase in free_shipping_phrases])


def has_cta(text: str) -> bool:
    cta_phrases = [
        "try now",
        "try here",
        "buy now",
        "buy here",
        "shop now",
        "shop here",
        "order now",
        "order here",
        "get yours now",
        "shop today",
        "order your samples today",
    ]
    return any([phrase.upper() in text.upper() for phrase in cta_phrases])


def get_discounts(text: str) -> list:
    discounts = []
    discounts.extend([x.group() for x in re.finditer("(?i)(discount)\s(of\s)?()[\d]+\s?%", text)])
    discounts.extend([x.group() for x in re.finditer("(?i)(save)\s[\d]+\s?%", text)])
    discounts.extend([x.group() for x in re.finditer("(?i)[\d]+\s?%\s(off)", text)])
    discounts.extend([x.group() for x in re.finditer("(?i)[\d]+\s?%\s(discount)", text)])
    discounts.extend([x.group() for x in re.finditer("(?i)-[\d]+\s?%", text)])
    return discounts


def get_percentages(text: str) -> list:
    try:
        prc = [x.group() for x in re.finditer("[\d]+\s?%", text)]
    except:
        print(text)
        return
    return prc


def get_hashtags(text):
    return re.findall(r"\B(\#[a-zA-Z]+\b)(?!;)", text)


def get_links(text):
    return [x.group() for x in re.finditer(r"(www|http).*(?=\b)", text)]


def has_links(text: str) -> bool:
    return ("http" in text) or ("www" in text)


def number_of_questions(text: str) -> bool:
    return len([i for i in range(len(text)) if text.startswith("?", i)])


def get_user_addressing(text: str) -> dict:
    tokens = nltk.word_tokenize(text.lower())
    keywords = ["you", "your", "yourself"]
    return {kw: tokens.count(kw) for kw in keywords}


def price_to_dict(price: Price) -> dict:
    return {"amount": price.amount_float, "currency": price.currency}


def get_prices(text: str) -> list:
    prices = []
    pattern = "(?P<price>\d+(\s\d+)*)"
    prog = re.compile(pattern)
    previous_end = 0
    end = 0

    while end < len(text):
        m = prog.search(text[end:])
        if m is None:
            break
        beg = m.start("price")
        end = m.end("price") + previous_end
        price_with_currency = text[max(0, beg - 4, previous_end) : min(len(text), end + 4)]
        price = Price.fromstring(price_with_currency)

        if (
            price.currency is not None
            and not (price.currency == "FR" and ("free" in text[end : min(end + 6, len(text))].lower()))
            and price.currency != "RD"
        ):
            price = price_to_dict(price)
            prices.append(price)
        previous_end = end + 1

    return prices


def get_fact_words(text: str) -> list[str]:
    fact_words = []
    fact_words.extend([x.group() for x in re.finditer("(?i)scienti", text)])
    fact_words.extend([x.group() for x in re.finditer(r"(?i)(?<!in )(?<=\b)fact(s)*(?=\b)", text)])
    fact_words.extend([x.group() for x in re.finditer("(?i)proven", text)])
    fact_words.extend([x.group() for x in re.finditer("(?i)clinical", text)])
    return fact_words


def starts_with_question(text: str, tokenizer=nltk.data.load("tokenizers/punkt/english.pickle")) -> bool:
    sentences = tokenizer.tokenize(text)
    if len(sentences) == 0:
        return None
    first_sentence = sentences[0]
    return first_sentence[len(first_sentence) - 1] == "?"


def main():
    print(get_fact_words("in fact facts"))


if __name__ == "__main__":
    main()
