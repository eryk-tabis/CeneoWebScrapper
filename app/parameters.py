selectors = {
    "author": ["span.user-post__author-name"],
    "recomendation": ["span.user-post__author-recomendation > em"],
    "score": ["span.user-post__score-count"],
    "pros": ["div.review-feature__title--positives ~ div.review-feature__item", None, True],
    "cons": ["div.review-feature__title--negatives ~ div.review-feature__item", None, True],
    "usefull": ["button.vote-yes > span"],
    "useless": ["button.vote-no > span"],
    "publish_date": ["span.user-post__published > time:nth-child(1)", "datetime"],
    "purchase_date": ["span.user-post__published > time:nth-child(2)", "datetime"],
}