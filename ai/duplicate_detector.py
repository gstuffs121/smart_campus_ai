
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def find_duplicate(new_text, existing_complaints):

    if not existing_complaints:

        return None, 0

    texts = [
        new_text
    ] + existing_complaints

    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    vectors = vectorizer.fit_transform(texts)

    similarity = cosine_similarity(
        vectors[0:1],
        vectors[1:]
    )

    highest_index = similarity.argmax()

    highest_score = (
        similarity[0][highest_index]
    )

    percentage = round(
        highest_score * 100,
        2
    )

    if percentage >= 70:

        return highest_index, percentage

    return None, percentage
