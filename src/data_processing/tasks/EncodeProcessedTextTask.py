from threading import Thread

import numpy as np
from gensim.models.fasttext import FastText
from tqdm.std import tqdm

from src.crawler.WebsitesProvider import DataProvider
from src.storage.database import websites_db


class DataProviderForEncodeProcessedTextTask(DataProvider):
    def __init__(self) -> None:
        override_query = {
            "error_code": {"$exists": False},
            "processed_text": {"$exists": True},
        }
        super().__init__(1000, fields_to_download=["_id", "processed_text"], additional_query_params=override_query, should_count=True)


class EncodeProcessedTextTask(Thread):
    def __init__(self, provider: DataProviderForEncodeProcessedTextTask) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        wiki_ft_model = FastText.load("./data/ft/fasttext_300.model")
        while True:
            urls = self.provider.get_records()
            if len(urls) == 0:
                break
            bulk = websites_db.initialize_unordered_bulk_op()
            for document in tqdm(urls, desc="thread", leave=False):
                processed_text = document["processed_text"]
                id = document["_id"]
                encoded = np.mean([wiki_ft_model.wv[vec] for vec in processed_text], axis=0)
                bulk.find({"_id": id}).update_one({"$set": {"encoded_processed_text": encoded}})
            bulk.execute()
