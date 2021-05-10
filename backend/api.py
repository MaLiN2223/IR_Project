from typing import Optional
from flask import Flask
from flask_restful import Resource, Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask import request
from dataclasses import dataclass, asdict
import json
from flask import jsonify
import time
from src.storage.database import websites_db
import numpy as np
from src.index.utils import load_index, load_fasttext, load_indexes


app = Flask(__name__)
api = Api(app)
CORS(app)


class Index:
    def __init__(self) -> None:
        import nmslib

        print("Loading index")
        self.model_name = "pure_fasttext"
        self.index = load_index(self.model_name)
        print("Loading fasttext model")
        self.ft_model = load_fasttext(self.model_name)

    def search(self, query):
        input = query.lower().split()
        query = [self.ft_model.wv[vec] for vec in input]
        query = np.mean(query, axis=0)
        ids_list = list(load_indexes(self.model_name))
        t0 = time.time()
        ids, distances = self.index.knnQuery(query, k=10)
        t1 = time.time()
        print(f"Searched {len(ids_list)} records in {round(t1-t0,4) } seconds \n")
        responses = []
        for i, j in zip(ids, distances):
            website_id = ids_list[i]
            website_score = round(j, 2)
            website = websites_db.find_one({"_id": website_id}, {"fixed_url": True, "title": True})
            debugInformation = DebugInformation(str(website_score))
            response = SearchResponse(website["fixed_url"], website["title"], website_id, "summary", debugInformation)
            responses.append(response)
        return responses


limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

index: Optional[Index] = None


@app.before_first_request
def startup():
    global index
    print("Starting the app...")
    index = Index()


class SearchEngine(Resource):
    def get(self, query):

        # debug = request.args.get("debugMode")
        results = index.search(query)
        print(results)
        return jsonify(results)


@dataclass
class DebugInformation:
    score: float


@dataclass
class SearchResponse:
    url: str
    title: str
    urlId: str
    summary: str
    debugInformation: Optional[DebugInformation] = None


class Admin(Resource):
    def get(self):
        return "admin!"


api.add_resource(SearchEngine, "/engine/<string:query>")
api.add_resource(Admin, "/admin/")
