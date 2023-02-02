import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

sia = SentimentIntensityAnalyzer()

pickle_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
