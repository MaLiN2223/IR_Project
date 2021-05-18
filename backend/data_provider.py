import pickle
from typing import Iterable, List, Optional

from gensim.models.fasttext import FastText
from keybert.model import KeyBERT
from rank_bm25 import BM25L

from backend.utils import is_prod
from src.index.contants import dump_ids_file_name, index_file_name

wiki_ft_model = None
keyword_model: Optional[KeyBERT] = None
doc_local_id_to_remote_id: Optional[List[str]] = None
bm25: Optional[BM25L] = None


def base_path():
    if is_prod():
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
        wiki_ft_model = FastText.load(f"{base_path()}fasttext_300.model")
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


def load_index(model_name: str):
    import nmslib

    index = nmslib.init(method="hnsw", space="cosinesimil")
    index.loadIndex(filename=f"{base_path()}{model_name}/{index_file_name}")
    return index


def load_indexes(model_name: Optional[str] = None) -> Iterable[str]:
    file_name = f"{base_path()}{model_name}/{dump_ids_file_name}" if model_name is not None else f"{base_path()}{dump_ids_file_name}"
    with open(file_name, "r", encoding="utf-8") as ids:
        for line in ids:
            yield line.strip()
