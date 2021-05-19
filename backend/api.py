import logging
import traceback
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler

import git
from flask import Flask, jsonify, request
from flask.logging import default_handler
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api, Resource
from nltk.corpus import stopwords

from backend.BM25IndexWrapper import BM25Index
from src.index.preprocessing_pipeline import Pipeline

app = Flask(__name__)
api = Api(app)
CORS(app)

handler = RotatingFileHandler("log.log", maxBytes=100000, backupCount=3)
root = logging.getLogger()
root.addHandler(default_handler)
root.addHandler(handler)


APP_VERSION = git.Repo().head.object.hexsha[:7]

preprocessing_pipeline = Pipeline(stopwords.words("english"))
limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "60 per hour", "3 per second"])


@app.errorhandler(404)
def page_not_found(error):
    # TODO: log
    return "This route does not exist {}".format(request.url), 404


@app.before_first_request
def startup():
    # TODO: log
    print("Starting the app...")


def preprocess_query(query: str):
    return list(preprocessing_pipeline.pipe(query))


def search(query: str, keywords: str, top_n: int, is_debug: bool, temperature: float):
    # TODO: log query and keywords

    top_n = min(top_n, 10)
    query_list = preprocess_query(query)
    keywords_list = preprocess_query(" ".join(keywords.lower().split(",")))
    index = BM25Index()

    return index.search(query_list, keywords_list, top_n, is_debug, temperature)


class SearchEngine(Resource):
    def do_get(self, query):
        top_n = request.args.get("topn")
        is_debug = request.args.get("debug")
        keywords = request.args.get("keywords")
        temperature = request.args.get("temperature")

        try:
            temperature = 2.0 if temperature is None else float(temperature)
        except:  # noqa
            temperature = 2.0

        if top_n is None:
            top_n = 10
        try:
            top_n = int(top_n)
        except:  # noqa
            top_n = 10

        if is_debug == "true":
            is_debug = True
        else:
            is_debug = False

        results = search(query, keywords, int(top_n), is_debug, temperature)
        return jsonify(results)

    def get(self, query):
        try:
            return self.do_get(query)
        except Exception as ex:
            print("ERROR", ex)  # TODO: log
            track = traceback.format_exc()
            print(track)


@dataclass
class Explainability:
    score: float


class Admin(Resource):
    def get(self):
        return "admin!"


class Metadata(Resource):
    def get(self):
        return APP_VERSION


api.add_resource(SearchEngine, "/engine/<string:query>")
api.add_resource(Admin, "/admin/")
api.add_resource(Metadata, "/metadata/version")
