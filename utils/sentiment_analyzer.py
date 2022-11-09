import nltk
from nltk.corpus import stopwords
import re
from textblob import TextBlob


def text_cleaner(text):
    extra_stopwords = ["The", "It", "it", "in", "In", "wh"]

    text = re.sub("https?:\/\/\S+", "", text)
    text = re.sub("#[A-Za-z0–9]+", " ", text)
    text = re.sub("#", " ", text)
    text = re.sub("\n", " ", text)
    text = re.sub("@[A-Za-z0–9]+", "", text)
    text = re.sub("RT", "", text)
    text = re.sub("^[a-zA-Z]{1,2}$", "", text)
    text = re.sub("\w*\d\w*", "", text)
    for word in extra_stopwords:
        text = text.replace(word, "")


def lemmatize_text(text):
    w_tokenizer = nltk.tokenize.WhitespaceTokenizer()
    lemmatizer = nltk.stem.WordNetLemmatizer()

    text_tokens = w_tokenizer.tokenize(text)
    return ' '.join(lemmatizer.lemmatize(w) for w in text_tokens if not w in stopwords.words('english'))

def getPolarity(tweet):
    sentiment_polarity = TextBlob(tweet).sentiment.polarity
    return sentiment_polarity

def getPolAnalysis(polarity_score):
    if polarity_score < 0:
        return "Negative"
    elif polarity_score == 0:
        return "Neutral"
    else:
        return "Positive"

def getSubjectivity(tweet):
    sentiment_subjectivity = TextBlob(tweet).sentiment.subjectivity
    return sentiment_subjectivity

def getSubAnalysis(subjectivity_score):
    if subjectivity_score <= 0.5:
        return "Objective"
    else:
        return "Subjective"