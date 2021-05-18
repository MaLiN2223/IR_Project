import pickle
from typing import List, Optional

from gensim.models.fasttext import FastText
from keybert.model import KeyBERT
from rank_bm25 import BM25L

from index.utils import load_indexes

wiki_ft_model = None
keyword_model: Optional[KeyBERT] = None
doc_local_id_to_remote_id: Optional[List[str]] = None
bm25: Optional[BM25L] = None


def __is_prod():
    return False


def base_path():
    if __is_prod():
        return "/datadrive/data/"
    else:
        return "./data/"


def load_bm25():
    global bm25
    if bm25 is None:
        bm25 = pickle.load(open(base_path() + "bm25.pickle", "rb"))
    return bm25


def get_wiki_ft_model():
    global wiki_ft_model
    if wiki_ft_model is None:
        print("Loading wiki_ft_model")
        wiki_ft_model = FastText.load("./data/ft/fasttext_300.model")
        print("Loaded.")
    return wiki_ft_model


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
