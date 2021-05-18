from threading import Thread

from tqdm import tqdm

from src.crawler.PagesDownloader import PagesDownloader
from src.crawler.WebsitesProvider import DataProvider
from src.storage.database import websites_db


class WebsitesProviderForFixing(DataProvider):
    def __init__(self) -> None:
        override_query = {
            "leased": {"$exists": False},
            "error_code": {"$exists": False},
        }
        super().__init__(100, fields_to_download=["_id", "page_text"], additional_query_params=override_query, should_count=False)


class RedirectFixer(Thread):
    def __init__(self, provider: WebsitesProviderForFixing) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        downloader = PagesDownloader()
        print("Starting...")
        while True:
            urls = self.provider.get_records()
            if len(urls) == 0:
                break
            for document in tqdm(urls, desc="urls for fixer"):
                id = document["_id"]
                url = document["fixed_url"]
                page = downloader.get_page(url)
                if page.url != url:
                    q = f"{url} | {page.url}"
                    with open("removed", "a", encoding="utf-8") as f:
                        f.write(q + "\n")
                    websites_db.delete_one({"_id": id})
