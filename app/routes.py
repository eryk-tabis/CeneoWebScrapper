from app import app
from flask import render_template, redirect, url_for, request
import os
import pandas as pd
from .forms import InputForm
from app.models.product import Product

@app.route('/')
def index(name="Hello world"):  # put application's code here
    return render_template('index.html', text=name)


@app.route('/exctract', methods=["POST", "GET"])
def extract():
    form = InputForm(request.form)
    if request.method == "POST" and form.validate():
        product_id = request.form.get("product_id")
        product = Product(product_id)
        product.extract_product().process_stats()
        product.draw_charts()
        product.save_opinions()
        product.save_stats()
        return redirect(url_for("product", product_id=product_id))
    else:
        return render_template("extract.html", form=form)


@app.route('/products')
def products():
    products_id = [filename.split(".")[0] for filename in os.listdir("app/opinions") ]
    products = [Product(product_id).read_from_json() for product_id in products_id]
    return render_template("products.html", products=products)


@app.route('/author')
def author():
    return render_template('author.html')


@app.route('/product/<product_id>')
def product(product_id):
    opinions = pd.read_json(f'app/opinions/{product_id}.json')
    return render_template("product.html", product_id=product_id,
                           tables=[opinions.to_html(classes='data', index=False)])
