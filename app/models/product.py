import requests
import os
import json
from bs4 import BeautifulSoup
from ..utils import get_item
from .opinion import Opinion

class Product:
    def __init__(self, product_id, product_name=None, opinions=[], opinions_count=None, pros_count=None, cons_count=None, average_score=None):
        self.product_id = product_id
        self.product_name = product_name
        self.opinions = opinions
        self.opinions_count = opinions_count
        self.pros_count = pros_count
        self.cons_count = cons_count
        self.average_score = average_score

    def __str__(self):
        return self.product_name

    def extract_product(self):
        url = f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        self.product_name = get_item(page, "h1.product-top__product-info__name")
        while (url):
            response = requests.get(url)
            page = BeautifulSoup(response.text, 'html.parser')
            opinions = page.select("div.js_product-review")
            for opinion in opinions:
                self.opinions.append(Opinion().extract_opinion(opinion))
            try:
                url = f"https://www.ceneo.pl/{self.product_id}" + get_item(page, "a.pagination__next", 'href')
            except TypeError:
                url = None

    def process_stats(self):
        self.opinions_count = len(self.opinions)
        self.pros_count = self.opinions.pros.map(bool).sum()
        self.cons_count = self.opinions.cons.map(bool).sum()
        self.average_score = self.opinions.score.mean().round(2)
        return self
    def save_opinions(self):
        if not os.path.exists("app/opinions"):
            os.makedirs("app/opinions")
        with open(f"app/opinions/{self.product_id}.json", 'w', encoding="UTF-8") as jf:
            json.dump(self.opinions, jf, indent=4, ensure_ascii=False)

    def save_stats(self):
        if not os.path.exists("app/opinions"):
            os.makedirs("app/opinions")
        with open(f"app/opinions/{self.product_id}.json", 'w', encoding="UTF-8") as jf:
            json.dump(self.opinions, jf, indent=4, ensure_ascii=False)
