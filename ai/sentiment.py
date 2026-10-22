
from textblob import TextBlob


def analyze_sentiment(text):

    polarity = TextBlob(text).sentiment.polarity

    if polarity <= -0.3:

        return "Very Negative"

    elif polarity < 0:

        return "Negative"

    elif polarity == 0:

        return "Neutral"

    elif polarity < 0.3:

        return "Positive"

    else:

        return "Very Positive"