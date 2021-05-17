import warnings
from threading import Thread

from bs4 import BeautifulSoup
from keybert import KeyBERT
from nltk.corpus import stopwords
from summarizer.model_processors import TransformerSummarizer
from tqdm.std import tqdm

from src.crawler.PagesParser import PagesParser
from src.crawler.WebsitesProvider import DataProvider
from src.index.preprocessing_pipeline import Pipeline
from src.storage.database import websites_db

warnings.simplefilter("ignore")


class DataProviderKeywordsExtractionTask(DataProvider):
    def __init__(self) -> None:
        override_query = {
            "error_code": {"$exists": False},
            "page_text": {"$exists": True},
            "xl_summary": {"$exists": True},
            "summary_keywords": {"$exists": False},
        }
        super().__init__(
            100,
            fields_to_download=["_id", "page_text", "xl_summary", "processed_text", "title"],
            additional_query_params=override_query,
            should_count=True,
            no_cursor_timeout=True,
        )


class KeywordsExtractionTask(Thread):
    def __init__(self, provider: DataProviderKeywordsExtractionTask) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        keywords_model = KeyBERT("xlm-r-distilroberta-base-paraphrase-v1")
        stop_words = stopwords.words("english")
        while True:
            urls = self.provider.get_records()
            if len(urls) == 0:
                break
            bulk = websites_db.initialize_unordered_bulk_op()
            for document in tqdm(urls, desc="thread", leave=False):
                page_text = document["page_text"].replace("\n", " ").strip()
                summary = document["xl_summary"]
                processed_text = " ".join(document["processed_text"])
                id = document["_id"]
                try:
                    summary_keywords, text_keywords, processed_keywords = keywords_model.extract_keywords(
                        [summary, page_text, processed_text], keyphrase_ngram_range=(2, 2), stop_words=stop_words
                    )
                except Exception as ex:
                    print(ex)
                    continue
                bulk.find({"_id": id}).update_one(
                    {"$set": {"summary_keywords": summary_keywords, "text_keywords": text_keywords, "processed_keywords": processed_keywords}}
                )
            bulk.execute()
