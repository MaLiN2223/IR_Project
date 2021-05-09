from typing import Iterable, List, Tuple
import pickle
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db
from tqdm import tqdm
from gensim.corpora import Dictionary
from nltk.corpus import stopwords
from gensim.models.fasttext import FastText
from gensim import models
from gensim.models.callbacks import CallbackAny2Vec
import numpy as np
import time

#

dict_path = "./data/dictionary.dict"
fasttext_model_name = "./data/ft_model.m"
tfidf_model_name = "./data/tfidf_model.m"
dump_file_path = "./data/dump_processed.dmp"
dump_ids_file_path = "./data/dump_processed_ids.dmp"
vectors_file_path = "./data/weighted_doc_vects.p"
index_file_path = "./data/index"


class EpochLogger(CallbackAny2Vec):
    def __init__(self):
        self.epoch = 0

    def on_epoch_begin(self, model):
        print("Epoch #{} start".format(self.epoch))

    def on_epoch_end(self, model):
        print("Epoch #{} end".format(self.epoch))
        self.epoch += 1


def load_indexes() -> Iterable[str]:
    with open(dump_ids_file_path, "r", encoding="utf-8") as ids:
        for line in ids:
            yield line.strip()


def dump_corpus_to_file():
    with open(dump_ids_file_path, "w", encoding="utf-8") as ids:
        with open(dump_file_path, "w", encoding="utf-8") as f:
            for id, text in pull_cleaned_text():
                ids.write(id + "\n")
                f.write(" ".join(text) + "\n")


def text_from_file(split: bool = True):
    with open(dump_ids_file_path, "r", encoding="utf-8") as ids:
        with open(dump_file_path, "r", encoding="utf-8") as f:
            for id, row in tqdm(zip(ids, f), total=230407):
                if split:
                    splitted = row.strip().split(" ")
                    yield (id, splitted)
                else:
                    yield (id, row.strip())


def pull_text():
    pipeline = Pipeline(set(stopwords.words("english")))
    total = 230407
    for record in tqdm(websites_db.find({"page_text": {"$exists": True}}, {"page_text": 1}), desc="pull from db", total=total):
        text = record["page_text"]
        text = list(pipeline.pipe(text))
        yield text


def pull_cleaned_text() -> Tuple[str, List[str]]:
    total = 230407
    for record in tqdm(websites_db.find({"processed_text": {"$exists": True}}, {"processed_text": 1}), desc="pull cleaned text from db", total=total):
        yield record["_id"], record["processed_text"]


def generate_cleaned_text():
    query = {"page_text": {"$exists": True}, "processed_text": {"$exists": False}}
    pipeline = Pipeline(stopwords=set(stopwords.words("english")))
    bulk_exec = 0
    total = 228405  # websites_db.count_documents(query)  # 230407

    bulk = websites_db.initialize_unordered_bulk_op()
    for record in tqdm(websites_db.find(query, {"page_text": 1}), desc="text processed", total=total):
        text = record["page_text"]
        page_id = record["_id"]
        processed_text = list(pipeline.pipe(text))
        bulk.find({"_id": page_id}).update_one({"$set": {"processed_text": processed_text}})
        bulk_exec += 1
        if bulk_exec > 1000:
            bulk_exec = 0
            bulk.execute()
            bulk = websites_db.initialize_unordered_bulk_op()
    if bulk_exec > 0:
        bulk.execute()


def prepare_dictionary():
    print("Preparing dictionary")
    dict = Dictionary()
    for id, document in text_from_file():
        dict.add_documents([document])
    dict.save(dict_path)


def generate_weighted_vectors():
    tfidf_model = models.TfidfModel.load(tfidf_model_name)
    dict = Dictionary.load(dict_path)
    ft_model = FastText.load(fasttext_model_name)
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


def train_fasttext():
    generate_file = False
    ft_model = FastText(
        sg=1,  # use skip-gram: usually gives better results
        vector_size=1024,  # embedding dimension (default)
        window=10,  # window size: 10 tokens before and 10 tokens after to get wider context
        min_count=5,  # only consider tokens with at least n occurrences in the corpus
        negative=15,  # negative subsampling: bigger than default to sample negative examples more
        min_n=2,  # min character n-gram
        max_n=5,  # max character n-gram
    )
    if generate_file:
        with open("storage", "w", encoding="utf-8") as f:
            for sentence in pull_text():
                sentence = " ".join(sentence)
                try:
                    f.write(sentence + "\n")
                except:  # noqa
                    print(sentence)
                    raise
    ft_model.build_vocab(corpus_file="storage")
    total_words = ft_model.corpus_total_words
    epoch_logger = EpochLogger()
    ft_model.train(corpus_file="storage", total_words=total_words, epochs=5, callbacks=[epoch_logger])
    ft_model.save(fasttext_model_name)


def generate_tookup():
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

    input = "flood defences".lower().split()
    ft_model = FastText.load(fasttext_model_name)

    index = nmslib.init(method="hnsw", space="cosinesimil")
    index.loadIndex(filename=index_file_path)
    query = [ft_model.wv[vec] for vec in input]
    query = np.mean(query, axis=0)
    ids_list = list(load_indexes())
    t0 = time.time()
    ids, distances = index.knnQuery(query, k=10)
    t1 = time.time()
    print(f"Searched {len(ids_list)} records in {round(t1-t0,4) } seconds \n")
    for i, j in zip(ids, distances):
        print(round(j, 2))
        print(ids_list[i])
