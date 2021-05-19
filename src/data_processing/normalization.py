import pickle
import time
from pathlib import Path
from typing import List, Tuple

import numpy as np
from gensim import models
from gensim.corpora import Dictionary
from gensim.models import fasttext
from gensim.models.callbacks import CallbackAny2Vec
from gensim.models.fasttext import FastText
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from backend.data_provider import load_indexes
from src.index.contants import (
    dict_path,
    dump_file_path,
    dump_ids_file_path,
    fasttext_model_path,
    index_file_path,
    tfidf_model_name,
    vectors_file_path,
)
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db

total_docs = 219719


def direct_logs_to_console():
    import logging
    import sys

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root.addHandler(handler)


def test_model(model):
    d = []
    for input in ["lord vader", "anakin skywalker", "palpatine", "darth bane", "obiwan kenobi"]:
        print(f"Most similar to {input}")
        print(model.wv.most_similar(positive=[input]))
        input = input.lower().split()
        query = [model.wv[vec] for vec in input]
        query = np.mean(query, axis=0)
        d.append(query)
    print("Similartities")
    print(cosine_similarity(d))


class EpochLogger(CallbackAny2Vec):
    def __init__(self):
        self.epoch = 0
        self.stat_time = time.time()

    def on_epoch_begin(self, model):
        self.start_time = time.time()
        print("Epoch #{} start".format(self.epoch))

    def on_epoch_end(self, model):
        test_model(model)
        print(f"Epoch #{self.epoch} end, took {time.time()-self.start_time}")
        self.epoch += 1


def dump_corpus_to_file():
    with open(dump_ids_file_path, "w", encoding="utf-8") as ids:
        with open(dump_file_path, "w", encoding="utf-8") as f:
            for id, text in pull_cleaned_text():
                ids.write(id + "\n")
                f.write(" ".join(text) + "\n")


def text_from_file(split: bool = True):
    with open(dump_ids_file_path, "r", encoding="utf-8") as ids:
        with open(dump_file_path, "r", encoding="utf-8") as f:
            for id, row in tqdm(zip(ids, f), total=total_docs):
                if split:
                    splitted = row.strip().split(" ")
                    yield (id, splitted)
                else:
                    yield (id, row.strip())


def pull_text():
    pipeline = Pipeline(set(stopwords.words("english")))
    for record in tqdm(websites_db.find({"page_text": {"$exists": True}}, {"page_text": 1}), desc="pull from db", total=total_docs):
        text = record["page_text"]
        text = list(pipeline.pipe(text))
        yield text


def pull_cleaned_text() -> Tuple[str, List[str]]:
    for record in tqdm(
        websites_db.find({"processed_text": {"$exists": True}}, {"processed_text": 1}), desc="pull cleaned text from db", total=total_docs
    ):
        yield record["_id"], record["processed_text"]


def prepare_dictionary():
    print("Preparing dictionary")
    dict = Dictionary()
    for id, document in text_from_file():
        dict.add_documents([document])
    dict.save(dict_path)


def generate_fasttext_vectors():
    print("Generate weighted vectors")
    ft_model = FastText.load(fasttext_model_path)
    weighted_doc_vects = []
    for id, doc in tqdm(text_from_file()):
        doc_vector = []
        for word in doc:
            encoded_word = ft_model.wv[word]
            weighted_vector = encoded_word
            doc_vector.append(weighted_vector)
        doc_vector_mean = np.mean(doc_vector, axis=0)
        weighted_doc_vects.append(doc_vector_mean)
    pickle.dump(weighted_doc_vects, open(vectors_file_path, "wb"))


def generate_weighted_vectors():
    print("Generate weighted vectors")
    tfidf_model = models.TfidfModel.load(tfidf_model_name)
    dict = Dictionary.load(dict_path)
    ft_model = FastText.load(fasttext_model_path)
    weighted_doc_vects = []
    for id, doc in tqdm(text_from_file()):
        doc_vector = []
        tfs = {x: y for x, y in tfidf_model[dict.doc2bow(doc)]}
        ids = dict.doc2idx(doc)
        for word, id in zip(doc, ids):
            encoded_word = ft_model.wv[word]
            if id not in tfs:
                weight = 0
            else:
                weight = tfs[id]
            weighted_vector = encoded_word * weight
            doc_vector.append(weighted_vector)
        doc_vector_mean = np.mean(doc_vector, axis=0)
        weighted_doc_vects.append(doc_vector_mean)
    pickle.dump(weighted_doc_vects, open(vectors_file_path, "wb"))


def generate_tfidf():
    print("Generating tfidf")
    dict = Dictionary().load(dict_path)
    corpus = [dict.doc2bow(text) for id, text in text_from_file()]
    model = models.TfidfModel(corpus, normalize=True)
    model.save(tfidf_model_name)


def generate_bm25():
    print("Preparing bm25")
    from rank_bm25 import BM25L

    corpus = [text for id, text in text_from_file()]
    bm25 = BM25L(corpus)
    pickle.dump(bm25, open("./data/bm25.pickle", "wb"))


def train_fasttext(size: int, model_out_dir: str, model_name: str, generate_tmp_file: bool = True):
    model_out_path = f"./data/{model_out_dir}"
    tmp_fasttext_file = "./data/storage"
    Path(model_out_path).mkdir(parents=True, exist_ok=True)
    print("Training fasttext")
    ft_model = FastText(
        sg=1,  # use skip-gram: usually gives better results
        vector_size=size,  # embedding dimension (default)
        window=10,  # window size: 10 tokens before and 10 tokens after to get wider context
        min_count=5,  # only consider tokens with at least n occurrences in the corpus
        negative=10,  # negative subsampling: bigger than default to sample negative examples more
        min_n=2,  # min character n-gram
        max_n=5,  # max character n-gram
        workers=8,
    )
    print("Generating temp file.")
    if generate_tmp_file:
        with open(tmp_fasttext_file, "w", encoding="utf-8") as f:
            for _, sentence in text_from_file():
                sentence = " ".join(sentence)
                try:
                    f.write(sentence + "\n")
                except:  # noqa
                    print(sentence)
                    raise
    ft_model.build_vocab(corpus_file=tmp_fasttext_file)
    total_words = ft_model.corpus_total_words
    epoch_logger = EpochLogger()
    ft_model.train(corpus_file=tmp_fasttext_file, total_examples=total_docs, total_words=total_words, epochs=5, callbacks=[epoch_logger])
    ft_model.save(model_out_path + "/" + model_name)


def generate_lookup():
    import nmslib

    weighted_doc_vects = pickle.load(open(vectors_file_path, "rb"))

    # create a matrix from our document vectors
    data = np.vstack(weighted_doc_vects)

    # initialize a new index, using a HNSW index on Cosine Similarity
    index = nmslib.init(method="hnsw", space="cosinesimil")
    index.addDataPointBatch(data)
    index.createIndex({"post": 2}, print_progress=True)
    index.saveIndex(index_file_path)


def search():
    import nmslib

    input = "Darth Sidious".lower().split()
    ft_model = FastText.load(fasttext_model_path)

    index = nmslib.init(method="hnsw", space="cosinesimil")
    index.loadIndex(filename=index_file_path)
    query = [ft_model.wv[vec] for vec in input]
    query = np.mean(query, axis=0)
    ids_list = list(load_indexes(None))
    t0 = time.time()
    ids, distances = index.knnQuery(query, k=10)
    t1 = time.time()
    print(f"Searched {len(ids_list)} records in {round(t1-t0,4) } seconds \n")
    for i, j in zip(ids, distances):
        print(round(j, 2))
        print(ids_list[i])
        print(websites_db.find_one({"_id": ids_list[i]}, {"fixed_url": 1}))


fasttext_wiki_base_model = "./data/fasttext_wiki_model/wiki.en.bin"
fasttext_wiki_our_prepared_model = "./data/fasttext_wiki_model/wiki.our.bin"
fasttext_wiki_our_trained_model = "./data/fasttext_wiki_model/wiki.our.trained.bin"


def prepare_wiki_fasttext():
    tokenized_corpus = [doc for _, doc in text_from_file()]
    t = time.time()
    ft_model = fasttext.load_facebook_model(fasttext_wiki_base_model)
    t2 = time.time()
    print(f"Took {t2-t} to load the model")
    t = time.time()
    ft_model.build_vocab(tokenized_corpus, update=True)
    t2 = time.time()
    print(f"Took {t2-t} to update the corpus the model")
    ft_model.save(fasttext_wiki_our_prepared_model)


def train_prepared_wiki_model():
    tokenized_corpus = list([doc for _, doc in text_from_file()])
    t = time.time()
    ft_model = FastText.load(fasttext_wiki_our_prepared_model)
    t2 = time.time()
    print(f"Took {t2-t} to load the model")
    epoch_logger = EpochLogger()
    print("Training starts...")
    ft_model.train(tokenized_corpus, total_examples=len(tokenized_corpus), epochs=5, callbacks=[epoch_logger])
    ft_model.save(fasttext_wiki_our_trained_model)
