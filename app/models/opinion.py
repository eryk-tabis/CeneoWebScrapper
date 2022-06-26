from ..utils import get_item
from app.parameters import selectors
class Opinion:
    def __init__(self,opinion_id=0, author=None, recomendation=None, score=None, pros=None, cons=None, usefull=None, useless=None, publish_date=None, purchase_date=None):
        self.opinion_id = opinion_id
        self.author = author
        self.recomendation = recomendation
        self.score = score
        self.pros = pros
        self.cons = cons
        self.usefull = usefull
        self.useless = useless
        self.publish_date = publish_date
        self.purchase_date = purchase_date

    def __str__(self):
        return f'Author is {self.author},' \
               f' recomendation is {self.recomendation},' \
               f' score is {self.score}, pros is {self.pros},' \
               f' cons is {self.cons}, usefull is {self.usefull},' \
               f' useless is {self.useless},' \
               f' publish date is {self.publish_date},' \
               f' purchase date is {self.purchase_date}'

    def __repr__(self):
        return f'(Author {self.author}),' \
               f' (Recomendation {self.recomendation}),' \
               f' (Score {self.score}),' \
               f' (Pros {self.pros}),' \
               f' (Cons {self.cons}),' \
               f' (Usefull {self.usefull}),' \
               f' (Useless {self.useless}),' \
               f' (Publish date {self.publish_date}),' \
               f' (Purchase date {self.purchase_date})'

    def to_dict(self):
        return {"opinion_id": self.opinion_id} | {key: getattr(self, key) for key in selectors.keys()}

    def extract_opinion(self, opinion):
        for key, value in selectors.items():
            setattr(self,key, get_item(opinion, *value))
        self.opinion_id = opinion["data-entry-id"]
        return self
