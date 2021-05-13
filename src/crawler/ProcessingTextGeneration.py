from threading import Thread

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from tqdm.std import tqdm

from src.crawler.PagesParser import PagesParser
from src.crawler.WebsitesProvider import DataProvider
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db


class DataProviderForTextProcessingTask(DataProvider):
    def __init__(self) -> None:
        override_query = {"error_code": {"$exists": False}, "page_text": {"$exists": True}, "text_generation_version": {"$exists": True}}
        super().__init__(500, fields_to_download=["_id", "page_text"], additional_query_params=override_query, should_count=False)


class TextProcessingTask(Thread):
    def __init__(self, provider: DataProviderForTextProcessingTask) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        pipeline = Pipeline(stopwords=set(stopwords.words("english")))
        while True:
            urls = self.provider.get_records()
            if len(urls) == 0:
                break
            bulk = websites_db.initialize_unordered_bulk_op()
            for document in tqdm(urls, desc="thread", leave=False):
                page_text = document["page_text"]
                id = document["_id"]
                processed_text = list(pipeline.pipe(page_text))
                bulk.find({"_id": id}).update_one({"$set": {"processed_text": processed_text}})
            bulk.execute()
