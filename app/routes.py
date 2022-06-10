from app import app
from flask import render_template, redirect, url_for, request
import requests
import json
from bs4 import BeautifulSoup
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from app.models.product import Product

@app.route('/')
def index(name="Hello world"):  # put application's code here
    return render_template('index.html', text=name)

@app.route('/exctract', methods=["POST", "GET"])
def extract():
    if request.method == "POST":
        product_id = request.form.get("product_id")
        product = Product(product_id)
        product.extract_product()

        return redirect(url_for("product", product_id=product_id))
    else:
        return render_template("extract.html")
@app.route('/products')
def products():
    products = [filename.split(".")[0] for filename in os.listdir("app/opinions")]

    return render_template("products.html", products=products)
@app.route('/author')
def author():
    return render_template('author.html')
@app.route('/product/<product_id>')
def product(product_id):
    opinions = pd.read_json(f'app/opinions/{product_id}.json')
    print(opinions)
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
