from threading import Thread

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from summarizer.model_processors import TransformerSummarizer
from tqdm.std import tqdm

from src.crawler.PagesParser import PagesParser
from src.crawler.WebsitesProvider import DataProvider
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db


class DataProviderForXlSummarizationTask(DataProvider):
    def __init__(self) -> None:
        override_query = {
            "error_code": {"$exists": False},
            "page_text": {"$exists": True},
            "text_generation_version": {"$exists": True},
            "xl_summary": {"$exists": False},
        }
        super().__init__(
            100, fields_to_download=["_id", "page_text"], additional_query_params=override_query, should_count=True, no_cursor_timeout=True
        )


class XlSummarizationTask(Thread):
    def __init__(self, provider: DataProviderForXlSummarizationTask) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        model = TransformerSummarizer(transformer_type="XLNet", transformer_model_key="xlnet-base-cased")
        while True:
            urls = self.provider.get_records()
            if len(urls) == 0:
                break
            bulk = websites_db.initialize_unordered_bulk_op()
            for document in tqdm(urls, desc="thread", leave=False):
                page_text = document["page_text"]
                cut = page_text.find("↑")
                if cut > 0:
                    page_text = page_text[:cut]
                id = document["_id"]
                xl_summary = "".join(model(page_text, min_length=60, max_length=120))
                bulk.find({"_id": id}).update_one({"$set": {"xl_summary": xl_summary}})
            bulk.execute()
