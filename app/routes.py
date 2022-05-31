from app import app
from flask import render_template, redirect, url_for
import requests
import json
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

def get_item(ancestor, selector, attribute=None, return_list=False):
    try:
        if return_list:
            return [item.get_text() for item in ancestor.select(selector)]
        if attribute:
            return ancestor.select_one(selector)[attribute]
        return ancestor.select_one(selector).get_text().strip()
    except (AttributeError, TypeError):
        return None

selectors = {
    "author": ["span.user-post__author-name"],
    "recomendation": ["span.user-post__author-recomendation > em"],
    "score": ["span.user-post__score-count"],
    "pros": ["div.review-feature__title--positives ~ div.review-feature__item", None, True],
    "cons": ["div.review-feature__title--negatives ~ div.review-feature__item", None, True],
    "usefull": ["button.vote-yes > span"],
    "useless": ["button.vote-no > span"],
    "publish_date": ["span.user-post__published > time:nth-child(1)", "datetime"],
    "purchase_date": ["span.user-post__published > time:nth-child(2)", "datetime"]
}

@app.route('/')
@app.route('/index')
@app.route('/index/<name>')
def index(name="Hello world"):  # put application's code here
    return render_template('index.html', text=name)

@app.route('/exctract/<product_id>')
def extract(product_id):
    url = f"https://www.ceneo.pl/{product_id}#tab=reviews"
    all_opinions = []
    while (url):
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        opinions = page.select("div.js_product-review")
        for opinion in opinions:
            single_opinion = {
                key: get_item(opinion, *value)
                for key, value in selectors.items()
            }
            single_opinion["opinion_id"] = opinion["data-entry-id"]
            all_opinions.append(single_opinion)
        try:
            url = f"https://www.ceneo.pl/{product_id}" + get_item(page, "a.pagination__next", 'href')
        except TypeError:
            url = None
    with open(f"app/opinions/{product_id}.json", 'w', encoding="UTF-8") as jf:
        json.dump(all_opinions, jf, indent=4, ensure_ascii=False)
    return redirect(url_for("product", product_id))
@app.route('/products')
def products():
    products = [filename.split(".")[0] for filename in os.listdir("app/opinions")]

    return render_template("products.html", products=products)
@app.route('/author')
def author():
    return
@app.route('/product/<product_id>')
def product(product_id):
    opinions = pd.read_json(f'app/opinions/{product_id}.json')
    opinions.score = opinions.score.map(lambda x: float(x.split("/")[0].replace(',', '.')))
    stats = {
    "opinions_count": len(opinions.index),
    "pros_count": opinions.pros.map(bool).sum(),
    "cons_count": opinions.cons.map(bool).sum(),
    "average_score": opinions.score.mean().round(2),
    }

    recomendation = opinions.recomendation.value_counts(dropna=False).sort_index().reindex(
        ["Nie polecam", "Polecam", None])
    recomendation.plot.pie(
        label="",
        autopct="%1.1f%%",
        colors=['forestgreen', 'lightskyblue', 'crimson'],
        labels=["Nie polecam", "Polecam", "Nie mam zdania"]
    )
    plt.title("Rekomendacja")
    plt.savefig(f"app/static/plots/{product_id}_recomendation.png")
    plt.close()

    score = opinions.score.value_counts().sort_index().reindex(list(np.arange(0, 5.5, 0.5)), fill_value=(0))
    score.plot.bar()
    plt.title("Oceny produktu")
    plt.xlabel("Liczba gwiazdek")
    plt.ylabel("Liczba opinii")
    plt.grid(True)
    plt.xticks(rotation=0)
    plt.savefig(f"app/static/plots/{product_id}_stars.png")
    plt.close()
    return render_template("product.html", stats=stats, product_id=product_id, opinions=opinions)
