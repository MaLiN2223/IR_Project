from threading import Thread

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from tqdm.std import tqdm

from src.crawler.PagesParser import PagesParser
from src.crawler.WebsitesProvider import DataProvider
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db


class DataProviderForTextFromHtmlGeneration(DataProvider):
    def __init__(self) -> None:
        override_query = {
            "error_code": {"$exists": False},
            "html": {"$exists": True},
            "$or": [
                {"text_generation_version": {"$exists": False}},
                {"text_generation_version": {"$eq": 1}},
            ],
        }
        super().__init__(300, fields_to_download=["_id", "html"], additional_query_params=override_query, should_count=True)


class TextFromHtmlGeneration(Thread):
    def __init__(self, provider: DataProviderForTextFromHtmlGeneration) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        parser = PagesParser()
        while True:
            urls = self.provider.get_records()
            if len(urls) == 0:
                break
            bulk = websites_db.initialize_unordered_bulk_op()
            for document in tqdm(urls, desc="thread", leave=False):
                html = document["html"]
                id = document["_id"]
                page = BeautifulSoup(html, "html.parser")
                page_text = parser.get_pure_page_text(page)
                bulk.find({"_id": id}).update_one({"$set": {"page_text": page_text, "text_generation_version": 2}})
            bulk.execute()
