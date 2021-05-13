import time
from abc import ABC
from dataclasses import dataclass
from typing import List, Optional, Tuple

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api, Resource
from keybert import KeyBERT
from rank_bm25 import BM25L
from sklearn.metrics.pairwise import cosine_similarity

from src.data_processing.normalization import text_from_file
from src.index.utils import load_fasttext, load_index, load_indexes
from src.storage.database import websites_db

app = Flask(__name__)
api = Api(app)
CORS(app)


@dataclass
class DebugInformation:
    score: float
    keywords: Optional[List[Tuple[str, float]]]
    similarity: List[float]


@dataclass
class SearchResponse:
    url: str
    title: str
    urlId: str
    summary: str
    debugInformation: Optional[DebugInformation] = None


class AbstractIndex(ABC):
    def search(self, query: List[str]):
        raise NotImplementedError()


def ids_to_records(ids: List[str]):
    to_order = {id: i for i, id in enumerate(ids)}
    data = websites_db.find({"_id": {"$in": ids}}, {"fixed_url": True, "title": True, "processed_text": True})
    data = sorted(data, key=lambda x: to_order[x["_id"]])
    return data


class BM25Index(AbstractIndex):
    def __init__(self) -> None:
        tokenized_corpus = [doc for id, doc in text_from_file()]
        self.bm25 = BM25L(tokenized_corpus)

    def search(self, query: List[str]):
        doc_scores = self.bm25.get_scores(query)
        doc_scores = np.array(doc_scores)
        arr = doc_scores.argsort()[-15:][::-1]
        index = get_doc_local_id_to_remote_id()
        doc_ids = list(str(index[x]) for x in arr)
        responses = []

        for i, record in enumerate(ids_to_records(doc_ids)):
            debugInformation = DebugInformation(str(doc_scores[i]), keywords=[], similarity=[])
            response = SearchResponse(record["fixed_url"], record["title"], record["_id"], "summary", debugInformation)
            responses.append(response)
        return responses


class TfidfIndex(AbstractIndex):
    def __init__(self) -> None:
        print("Loading index")
        self.model_name = "test"
        self.index = load_index(self.model_name)
        print("Loading fasttext model")
        self.ft_model = load_fasttext(self.model_name)
        self.keyword_model = get_keyword_model()

    def search(self, query):
        query = [self.ft_model.wv[vec] for vec in query]
        query = np.mean(query, axis=0)
        ids_list = list(load_indexes(self.model_name))
        t0 = time.time()
        ids, distances = self.index.knnQuery(query, k=10)
        t1 = time.time()
        print(f"Searched {len(ids_list)} records in {round(t1-t0,4) } seconds \n")
        return self.get_responses(ids, distances, ids_list, True)

    def get_responses(self, ids: List[int], distances: List[float], ids_list: List[str], include_explainability: bool) -> List[SearchResponse]:
        responses = []
        for i, j in zip(ids, distances):
            website_id = ids_list[i]
            website_score = round(j, 2)
            response = self.prepare_response(website_id, website_score, include_explainability)
            responses.append(response)
        return responses

    def prepare_response(self, website_id: str, website_score: float, include_explainability: bool) -> SearchResponse:
        website = websites_db.find_one({"_id": website_id}, {"fixed_url": True, "title": True, "processed_text": True})
        title = website["title"]
        the_text = " ".join(website["processed_text"])
        similarity, keywords = self.get_ref_vectors(the_text, title, ["darth vader"])
        debugInformation = DebugInformation(str(website_score), keywords=keywords, similarity=similarity)
        response = SearchResponse(website["fixed_url"], website["title"], website_id, "summary", debugInformation)

        return response

    def get_ref_vectors(self, the_text, title, negative_examples: List[str]):
        keywords = self.keyword_model.extract_keywords(the_text) + self.keyword_model.extract_keywords(the_text, keyphrase_ngram_range=(1, 2))
        merged_keywords = [x[0] for x in keywords]
        keywords_vector = [self.ft_model.wv[vec] for vec in merged_keywords] + [self.ft_model.wv[vec] for vec in title]
        keywords_vector = np.mean(keywords_vector, axis=0)
        negative_vector = [self.ft_model.wv[vec] for vec in negative_examples]
        negative_vector = np.mean(negative_vector, axis=0)
        doc_enc = [self.ft_model.wv[vec] for vec in the_text.split()]
        doc_enc = np.mean(doc_enc, axis=0)
        return list(str(x) for x in cosine_similarity(np.array([keywords_vector, negative_vector]))[0]), keywords


limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])

tfidf_index: Optional[TfidfIndex] = None
keyword_model: Optional[KeyBERT] = None
bm_index: Optional[BM25Index] = None
doc_local_id_to_remote_id: Optional[List[str]] = None


def get_keyword_model():
    global keyword_model
    if keyword_model is None:
        keyword_model = KeyBERT("xlm-r-distilroberta-base-paraphrase-v1")
    return keyword_model


def get_doc_local_id_to_remote_id():
    global doc_local_id_to_remote_id
    if doc_local_id_to_remote_id is None:
        doc_local_id_to_remote_id = list(load_indexes())
    return doc_local_id_to_remote_id


@app.before_first_request
def startup():
    print("Starting the app...")


def get_bm25_index():
    global bm_index
    if bm_index is None:
        bm_index = BM25Index()
    return bm_index


def get_tfidf_index():
    global tfidf_index
    if tfidf_index is None:
        tfidf_index = TfidfIndex()
    return tfidf_index


def search(query: str, is_bm25: bool):
    query = query.lower().split(" ")
    if is_bm25:
        index = get_bm25_index()
    else:
        index = get_tfidf_index()
    return index.search(query)


class SearchEngine(Resource):
    def get(self, query):
        # is_debug = request.args.get("debugMode")
        is_bm25 = request.args.get("bm25")

        results = search(query, is_bm25)
        return jsonify(results)


@dataclass
class Explainability:
    score: float


class Admin(Resource):
    def get(self):
        return "admin!"


api.add_resource(SearchEngine, "/engine/<string:query>")
api.add_resource(Admin, "/admin/")
