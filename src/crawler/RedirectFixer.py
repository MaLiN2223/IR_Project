from threading import Thread
from tqdm import tqdm
from crawler.Crawler import WebsitesProviderForFixing
from crawler.PagesDownloader import PagesDownloader
from src.storage.database import websites_db


class RedirectFixer(Thread):
    def __init__(self, provider: WebsitesProviderForFixing) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        downloader = PagesDownloader()
        print("Starting...")
        while True:
            urls = self.provider.get_pages()
            if len(urls) == 0:
                break
            for id, url in tqdm(zip(*urls), desc="urls for fixer"):
                page = downloader.get_page(url)
                if page.url != url:
                    q = f"{url} | {page.url}"
                    with open("removed", "a", encoding="utf-8") as f:
                        f.write(q + "\n")
                    websites_db.delete_one({"_id": id})
