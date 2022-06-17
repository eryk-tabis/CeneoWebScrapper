from app import app
from flask import render_template, redirect, url_for, request
import requests
import json
from bs4 import BeautifulSoup
import os
import pandas as pd

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
        product.save_opinions()
        product.process_stats()
        product.save_stats()

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
    opinions.score = opinions.score.map(lambda x: float(x.split("/")[0].replace(',', '.')))
    stats = {
    "opinions_count": len(opinions.index),
    "pros_count": opinions.pros.map(bool).sum(),
    "cons_count": opinions.cons.map(bool).sum(),
    "average_score": opinions.score.mean().round(2),
    }


    return render_template("product.html", stats=stats, product_id=product_id, opinions=opinions)
