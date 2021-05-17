import pickle
import time
from abc import ABC
from dataclasses import dataclass
from logging import debug
from typing import List, Optional, Tuple

import git
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_restful import Api, Resource
from gensim.models.fasttext import FastText
from keybert import KeyBERT
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity

from src.data_processing.normalization import text_from_file
from src.index.preprocessing_pipeline import Pipeline
from src.index.utils import load_fasttext, load_index, load_indexes
from src.storage.database import websites_db

app = Flask(__name__)
api = Api(app)
CORS(app)

stop_words = stopwords.words("english")


def load_version() -> str:
    with open("VERSION.txt", "r") as f:
        return f.read()


APP_VERSION = git.Repo().head.object.hexsha[:7]  # + " " + str(git.Repo().head.object.authored_date)


@dataclass
class DebugInformation:
    keywords: Optional[List[Tuple[str, float]]]
    similarity: List[float]


@dataclass
class SearchResponse:
    url: str
    title: str
    urlId: str
    summary: str
    score: float
    modified_score: float
    debugInformation: Optional[DebugInformation] = None


class AbstractIndex(ABC):
    def search(self, query: List[str]):
        raise NotImplementedError()


keyword_fields = ["summary_keywords", "text_keywords", "processed_keywords"]
fields_to_download = {
    x: True
    for x in [
        "_id",
        "fixed_url",
        "title",
        "processed_text",
        "page_text",
        "xl_summary",
    ]
    + keyword_fields
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
    def __init__(self) -> None:
        self.bm25 = pickle.load(open("data/bm25.pickle", "rb"))

    def search(self, query: List[str], banned_keywords: List[str], top_n: int, is_debug: bool):
        doc_scores = self.bm25.get_scores(query)
        negative_doc_scores = self.bm25.get_scores(banned_keywords)
        doc_scores = np.array(doc_scores)
        negative_doc_scores = np.array(negative_doc_scores)
        arr = doc_scores.argsort()[-100:][::-1]
        index = get_doc_local_id_to_remote_id()
        doc_ids = list(str(index[x]) for x in arr)
        responses = []

        print("Got the list!")
        wiki_ft_model = get_wiki_ft_model()
        for i, record in zip(arr, ids_to_records(doc_ids)):
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
                mn = np.mean([wiki_ft_model.wv[vec] for vec in record["processed_text"]], axis=0)
                processed_text_similarity = cosine_similarity([encoded_banned_keywords, mn])[0][1]
                # processed_text_similarity = (processed_text_similarity - 0.5) * 2
                processed_text_similarity = float(processed_text_similarity * 2)
                # modified_score *= (1 - processed_text_similarity)
                modified_score -= negative_doc_scores[i] * processed_text_similarity  # / 2
            if is_debug:
                debugInformation = DebugInformation(
                    keywords=doc_keywords,
                    similarity={
                        "wiki": {
                            "negative_score": negative_doc_scores[i],
                            "processed_text_similarity": processed_text_similarity,
                            "mean_closeness_to_bad_keywords": str(mean_closeness_to_bad_keywords),
                        }
                    },
                    # ),"keyword_to_banned_similarity": list([str(x) for x in keyword_to_banned_similarity])}},
                )
            else:
                debugInformation = None

            response = SearchResponse(
                record["fixed_url"],
                record["title"],
                record["_id"],
                record["xl_summary"][:150] + "...",
                bm25_score,
                modified_score,
                debugInformation,
            )
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
print("Loading wiki model.")
wiki_ft_model = None
# our_ft_model = FastText.load("./data/fasttext_wiki_model/wiki.our.bin")
print("Loaded")


def get_keyword_model():
    global keyword_model
    if keyword_model is None:
        keyword_model = KeyBERT("xlm-r-distilroberta-base-paraphrase-v1")
    return keyword_model


def get_wiki_ft_model():
    global wiki_ft_model
    if wiki_ft_model is None:
        print("Loading wiki_ft_model")
        wiki_ft_model = FastText.load("./data/ft/fasttext_300.model")
        print("Loaded.")
    return wiki_ft_model


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


def preprocess_query(query: str):
    p = Pipeline(stopwords.words("english"))
    return list(p.pipe(query))
    return query.lower().split(" ")


def search(query: str, keywords: str, is_bm25: bool, top_n: int, is_debug: bool):

    top_n = 10
    query_list = preprocess_query(query)
    keywords_list = preprocess_query(" ".join(keywords.lower().split(",")))
    if is_bm25:
        index = get_bm25_index()
    else:
        index = get_tfidf_index()

    return index.search(query_list, keywords_list, top_n, is_debug)


class SearchEngine(Resource):
    def get(self, query):
        # is_debug = request.args.get("debugMode")
        is_bm25 = request.args.get("bm25")
        top_n = request.args.get("topn")
        is_debug = request.args.get("debug")
        keywords = request.args.get("keywords")
        if top_n is None:
            top_n = 10
        if is_debug == "true":
            is_debug = True
        else:
            is_debug = False
        print("Is debug?", is_debug)

        results = search(query, keywords, is_bm25, int(top_n), is_debug)
        return jsonify(results)


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
