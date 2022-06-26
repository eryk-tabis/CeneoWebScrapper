import pandas as pd
import requests
import os
import json
from bs4 import BeautifulSoup
from ..utils import get_item
from .opinion import Opinion
import numpy as np
from matplotlib import pyplot as plt

class Product:
    def __init__(self, product_id, product_name="", opinions=[], opinions_count=None, pros_count=None, cons_count=None, average_score=None):
        self.product_id = product_id
        self.product_name = product_name
        self.opinions = opinions
        self.opinions_count = opinions_count
        self.pros_count = pros_count
        self.cons_count = cons_count
        self.average_score = average_score

    def __str__(self):
        return f'Name of product is :{self.product_name},' \
               f' id is :{self.product_id},' \
               f' opinions count is :{self.opinions_count},' \
               f' pros count is :{self.pros_count},' \
               f' cons count is :{self.cons_count},' \
               f' average score is :{self.average_score}'

    def __repr__(self):
       return f'(Product name {self.product_name}),' \
              f' (Product id {self.product_id}),' \
              f' (Opinions count {self.opinions_count}),' \
              f' (Pros count {self.pros_count}),' \
              f' (Cons count {self.cons_count}),' \
              f' (Average score {self.average_score})'

    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "opinions_count": self.opinions_count,
            "pros_count": self.pros_count,
            "cons_count": self.cons_count,
            "average_score": self.average_score,
            "opinions": [opinion.to_dict() for opinion in self.opinions]
        }
    def stats_to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "opinions_count": self.opinions_count,
            "pros_count": int(self.pros_count),
            "cons_count": int(self.cons_count),
            "average_score": self.average_score
        }

    def opinions_to_dict(self):
        return [opinion.to_dict() for opinion in self.opinions]

    def extract_product(self):
        url = f"https://www.ceneo.pl/{self.product_id}#tab=reviews"
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        self.product_name = get_item(page, "h1.product-top__product-info__name")
        self.opinions = []
        while(url):
            response = requests.get(url)
            page = BeautifulSoup(response.text, 'html.parser')
            opinions = page.select("div.js_product-review")
            for opinion in opinions:
                self.opinions.append(Opinion().extract_opinion(opinion))
            try:
                url = "https://www.ceneo.pl"+get_item(page,"a.pagination__next","href")
            except TypeError:
                url = None
        return self

    def opinions_to_df(self):
        opinions = pd.read_json(json.dumps([opinion.to_dict() for opinion in self.opinions]))
        opinions.score = opinions.score.map(lambda x: float(x.split("/")[0].replace(',', '.')))
        return opinions

    def process_stats(self):
        self.opinions_count = len(self.opinions_to_df().index)
        self.pros_count = self.opinions_to_df().pros.map(bool).sum()
        self.cons_count = self.opinions_to_df().cons.map(bool).sum()
        self.average_score = self.opinions_to_df().score.mean().round(2)
        return self

    def save_opinions(self):
        if not os.path.exists("app/opinions"):
            os.makedirs("app/opinions")
        if not os.path.exists("app/static/opinions"):
            os.makedirs("app/static/opinions")
        opinions = [opinion.to_dict() for opinion in self.opinions]
        with open(f"app/opinions/{self.product_id}.json", 'w', encoding="UTF-8")as jf1,\
                open(f"app/static/opinions/{self.product_id}.json", 'w', encoding="UTF-8") as jf2:
            json.dump(opinions, jf1, indent=4, ensure_ascii=False)
            json.dump(opinions, jf2, indent=4, ensure_ascii=False)
        pd.DataFrame(self.opinions_to_df()).to_csv(f"app/static/opinions/{self.product_id}.csv", index=False)
        pd.DataFrame(self.opinions_to_df()).to_excel(f"app/static/opinions/{self.product_id}.xlsx", index=False)

    def save_stats(self):
        if not os.path.exists("app/products"):
            os.makedirs("app/products")
        with open(f"app/products/{self.product_id}.json", 'w', encoding="UTF-8") as jf:
            json.dump(self.stats_to_dict(), jf, indent=4, ensure_ascii=False)

    def draw_charts(self):
        recomendation = self.opinions_to_df().recomendation.value_counts(dropna=False).sort_index().reindex(
            ["Nie polecam", "Polecam", None])
        recomendation.plot.pie(
            label="",
            autopct="%1.1f%%",
            colors=['forestgreen', 'lightskyblue', 'crimson'],
            labels=["Nie polecam", "Polecam", "Nie mam zdania"]
        )
        plt.title("Rekomendacja")
        plt.savefig(f"app/static/plots/{self.product_id}_recomendation.png")
        plt.close()

        score = self.opinions_to_df().score.value_counts().sort_index().reindex(list(np.arange(0, 5.5, 0.5)), fill_value=(0))
        score.plot.bar()
        plt.title("Oceny produktu")
        plt.xlabel("Liczba gwiazdek")
        plt.ylabel("Liczba opinii")
        plt.grid(True)
        plt.xticks(rotation=0)
        plt.savefig(f"app/static/plots/{self.product_id}_stars.png")
        plt.close()

    def read_from_json(self):
        with open(f"app/products/{self.product_id}.json", "r", encoding="UTF-8") as jf:
            product = json.load(jf)
        self.product_id = product["product_id"]
        self.product_name = product["product_name"]
        self.opinions_count = product["opinions_count"]
        self.pros_count = product["pros_count"]
        self.cons_count = product["cons_count"]
        self.average_score = product["average_score"]
        with open(f"app/opinions/{self.product_id}.json", "r", encoding="UTF-8") as jf:
            opinions = json.load(jf)
        for opinion in opinions:
            self.opinions.append(Opinion(**opinion))
        return self
