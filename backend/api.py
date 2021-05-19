import time
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api, Resource
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

from backend.data_provider import (
    get_doc_local_id_to_remote_id,
    get_keyword_model,
    get_wiki_ft_model,
    load_bm25,
)
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db

app = Flask(__name__)
api = Api(app)
CORS(app)

stop_words = stopwords.words("english")


try:
    import git

    APP_VERSION = git.Repo().head.object.hexsha[:7]
except:  # noqa
    APP_VERSION = "000"  # TODO: figure out how to make gitpython work on ubuntu (git path issue)


@app.errorhandler(404)
def page_not_found(error):
    return "This route does not exist {}".format(request.url), 404


@dataclass
class DebugRecordInformation:
    keywords: Optional[List[Tuple[str, float]]]
    debug_scores: Dict[str, Any]
    processing_time: float


@dataclass
class RecordResponse:
    url: str
    title: str
    urlId: str
    summary: str
    score: float
    modified_score: float
    debugInformation: Optional[DebugRecordInformation] = None


@dataclass
class SearchResponse:
    original_responses: List[RecordResponse]
    modified_responses: List[RecordResponse]
    time: float


class AbstractIndex(ABC):
    def search(self, query: List[str]):
        raise NotImplementedError()


keyword_fields = ["summary_keywords", "text_keywords", "processed_keywords"]
fields_to_download = {
    x: True for x in ["_id", "fixed_url", "title", "processed_text", "page_text", "xl_summary", "encoded_processed_text"] + keyword_fields
}


def ids_to_records(ids: List[str]):
    to_order = {id: i for i, id in enumerate(ids)}
    data = websites_db.find({"_id": {"$in": ids}}, fields_to_download)
    data = sorted(data, key=lambda x: to_order[x["_id"]])
    return data


def extract_keywords_from_page(page):
    keywords = []
    for key in keyword_fields:
        if key in page:
            d = page[key]
            if d == "None Found" or d[0] == "None Found":
                continue
            keywords.extend(d)
    return keywords


class BM25Index(AbstractIndex):
    def search(self, query: List[str], banned_keywords: List[str], top_n: int, is_debug: bool, temperature: float) -> SearchResponse:
        seach_start = time.time()

        bm25 = load_bm25()
        doc_scores = bm25.get_scores(query)
        negative_doc_scores = bm25.get_scores(banned_keywords)
        doc_scores = np.array(doc_scores)
        negative_doc_scores = np.array(negative_doc_scores)
        arr = doc_scores.argsort()[-top_n * 10 :][::-1]
        index = get_doc_local_id_to_remote_id()
        doc_ids = list(str(index[x]) for x in arr)
        responses: List[RecordResponse] = []

        print("Got the list!")
        wiki_ft_model = get_wiki_ft_model()
        for i, record in zip(arr, ids_to_records(doc_ids)):
            record_start = time.time()
            # our_scores = get_scores(record, query, our_ft_model)
            # wiki_scores = get_scores(record, query, wiki_ft_model)
            modified_score = doc_scores[i]
            bm25_score = doc_scores[i]
            doc_keywords = extract_keywords_from_page(record)
            # keyword_to_banned_similarity = []
            processed_text_similarity = 0
            mean_closeness_to_bad_keywords = 0
            if len(banned_keywords) > 0:
                banned_keywords = (" ".join(banned_keywords)).split()
                encoded_banned_keywords = np.mean([wiki_ft_model.wv[vec] for vec in banned_keywords], axis=0)

                # encoded_doc_keywords = []
                # doc_keyword_scores = []
                # for doc_keyword in doc_keywords:
                #     kw, score = doc_keyword
                #     doc_keyword_scores.append(score)
                #     encoded_doc_keyword = np.mean([wiki_ft_model.wv[vec] for vec in kw], axis=0)
                #     encoded_doc_keywords.append(encoded_doc_keyword)
                # keyword_to_banned_similarity = cosine_similarity([encoded_banned_keywords] + encoded_doc_keywords)[0][1:]
                # for i in range(len(keyword_to_banned_similarity)):
                #     keyword_to_banned_similarity[i] *= doc_keyword_scores[i]
                # if len(keyword_to_banned_similarity) > 0:
                #    mean_closeness_to_bad_keywords = np.mean(keyword_to_banned_similarity)  # higher - worse
                if "encoded_processed_text" in record:
                    mn = record["encoded_processed_text"]
                else:
                    mn = np.mean([wiki_ft_model.wv[vec] for vec in record["processed_text"]], axis=0)
                processed_text_similarity = cosine_similarity([encoded_banned_keywords, mn])[0][1]
                # processed_text_similarity = (processed_text_similarity - 0.5) * 2
                processed_text_similarity = float(processed_text_similarity)
                # modified_score *= (1 - processed_text_similarity)
                modified_score -= negative_doc_scores[i] * processed_text_similarity * temperature  # / 2
            if is_debug:
                summary = record["xl_summary"][:150] + "..."
                debugInformation = DebugRecordInformation(
                    keywords=doc_keywords,
                    debug_scores={
                        "negative_score": negative_doc_scores[i],
                        "processed_text_similarity": processed_text_similarity,
                        "mean_closeness_to_bad_keywords": str(mean_closeness_to_bad_keywords),
                    },
                    processing_time=time.time() - record_start,
                )
            else:
                summary = ""
                debugInformation = None

            response = RecordResponse(
                record["fixed_url"],
                record["title"],
                record["_id"],
                summary,
                bm25_score,
                modified_score,
                debugInformation,
            )
            responses.append(response)
        original_responses = sorted(responses, key=lambda x: -x.score)[:top_n]
        modified_responses = sorted(responses, key=lambda x: -x.modified_score)[:top_n]
        search_time = time.time() - seach_start
        return SearchResponse(original_responses, modified_responses, search_time)


limiter = Limiter(app, key_func=get_remote_address, default_limits=["200 per day", "50 per hour", "3 per second"])


def get_scores(document, query: List[str], ft_model):
    query = [ft_model.wv[vec] for vec in query]
    query = np.mean(query, axis=0)

    page_text = document["page_text"].replace("\n", " ").strip()
    summary = document["xl_summary"]
    title = document["title"]
    query = [ft_model.wv[vec] for vec in title.lower().split()]
    query = np.mean(query, axis=0)
    processed_text = " ".join(document["processed_text"])
    summary_encoded = encode_text(summary, ft_model)
    summary_keywords = encode_keywords(summary, ft_model)

    page_text_encoded = encode_text(page_text, ft_model)
    text_keywords = encode_keywords(page_text, ft_model)

    processed_text_encoded = encode_text(processed_text, ft_model)
    processed_keywords = encode_keywords(processed_text, ft_model)
    sim = cosine_similarity([summary_encoded, page_text_encoded, processed_text_encoded, summary_keywords, text_keywords, processed_keywords, query])[
        -1
    ][:-1]
    return [str(x) for x in sim]


def encode_text(text: str, encoding_model):
    text_encoded = np.array([encoding_model.wv[vec] for vec in text.split()])
    text_encoded = np.mean(text_encoded, axis=0)
    return text_encoded


def encode_keywords(text: str, encoding_model):
    text_keywords = get_keyword_model().extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words=stop_words)
    text_keywords = " ".join(set(" ".join([x[0] for x in text_keywords]).split()))
    return encode_text(text_keywords, encoding_model)


@app.before_first_request
def startup():
    print("Starting the app...")


def preprocess_query(query: str):
    p = Pipeline(stopwords.words("english"))
    return list(p.pipe(query))
    return query.lower().split(" ")


def search(query: str, keywords: str, top_n: int, is_debug: bool, temperature: float):

    top_n = min(top_n, 10)
    query_list = preprocess_query(query)
    keywords_list = preprocess_query(" ".join(keywords.lower().split(",")))
    index = BM25Index()

    return index.search(query_list, keywords_list, top_n, is_debug, temperature)


class SearchEngine(Resource):
    def do_get(self, query):
        # is_debug = request.args.get("debugMode")
        top_n = request.args.get("topn")
        is_debug = request.args.get("debug")
        keywords = request.args.get("keywords")
        print("keywords", keywords)
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
        print("Is debug?", is_debug)

        results = search(query, keywords, int(top_n), is_debug, temperature)
        return jsonify(results)

    def get(self, query):
        try:
            return self.do_get(query)
        except Exception as ex:
            print("ERROR", ex)  # TODO: log


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
