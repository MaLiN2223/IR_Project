from threading import Thread, Lock
from typing import List
from bs4 import BeautifulSoup, element
import urllib.request
from tqdm import tqdm
from crawler.PagesDownloader import PagesDownloader
from crawler.PagesParser import PagesParser
from crawler.RedirectFixer import RedirectFixer
from crawler.WebsitesProvider import WebsitesProvider, should_map
from crawler.utils import encode_url, normalize_url
from src.storage.database import websites_db
import time


def fix_wookiepedia(url: str):
    if url.startswith("https://starwars.fandom.com/wiki/"):
        pass
    elif url.startswith("/wiki/"):
        url = "https://starwars.fandom.com" + url
    else:
        raise Exception(url)
    url = url.split("#")[0]
    return url.split("?")[0]


class WebsitesProviderForFixing:
    def __init__(self) -> None:
        self.database = websites_db
        self.query = {
            "page_text": {"$exists": True},
            "leased": {"$exists": False},
            "error_code": {"$exists": False},
        }
        self.lock = Lock()
        self.database.update_many({"leased": True}, {"$unset": {"leased": True}})

    def get_pages(self, size: int = 500):
        urls = []
        ids = []
        with self.lock:
            for record in tqdm(self.database.find(self.query, {"fixed_url": 1}).limit(size), desc="pull from db"):
                if "error_code" in record:
                    continue
                if "fixed_url" not in record:
                    continue
                url = record["fixed_url"]
                if url == "https://starwars.fandom.com/wiki/Daniel_José_Older":
                    continue
                if (
                    not should_map(url)
                    or url.lower().endswith(".png")
                    or url.lower().endswith(".jpg")
                    or url.lower().endswith(".svg")
                    or url.lower().endswith(".ogg")
                ):
                    print("Skipping", url)
                    continue
                urls.append(url)
                ids.append(record["_id"])
                if len(urls) == size:
                    break
            self.database.update_many({"_id": {"$in": ids}}, {"$set": {"leased": True}})
            return ids, urls


class Crawler(Thread):
    def __init__(self, provider: WebsitesProvider) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        downloader = PagesDownloader()
        parser = PagesParser()
        no_data = 0

        while no_data < 2:
            urls = self.provider.get_pages()
            if len(urls) == 0:
                time.sleep(3)
                no_data += 1
                continue
            else:
                no_data = 0
            i = 0
            every = 10
            for url in tqdm(urls, desc="urls for downloader"):
                hashed_base_url = encode_url(url)
                try:
                    page = downloader.get_page(url)
                except urllib.request.HTTPError as e:
                    code = e.code
                    to_add = {"_id": hashed_base_url, "error_code": int(code)}
                    websites_db.update({"_id": hashed_base_url}, to_add)
                    continue
                except UnicodeEncodeError as uer:
                    to_add = {"_id": hashed_base_url, "error": str(uer), "error_code": -1}
                    websites_db.update({"_id": hashed_base_url}, to_add)
                    continue

                page = BeautifulSoup(page, "html.parser")
                all_links = parser.extract_links(page)

                wookiepedia_links = [(fix_wookiepedia(x), x) for x in all_links if x is not None and should_map(x)]

                bulk = websites_db.initialize_unordered_bulk_op()
                for fixed_link, real_link in wookiepedia_links:
                    hashed_url = encode_url(fixed_link)
                    normalized_url = normalize_url(fixed_link)
                    bulk.find({"_id": hashed_url}).upsert().update_one(
                        {
                            "$setOnInsert": {
                                "_id": hashed_url,
                                "fixed_url": fixed_link,
                                # "represented_as": [real_link],
                                "normalized_url": normalized_url,
                                "real_base_url": normalize_url(url, False)
                                # "from": [hashed_base_url],
                            }
                        }
                    )
                    # bulk.find({"_id": hashed_url}).update_one(
                    #     {"$push": {"represented_as": real_link},}
                    # )
                    i += 1

                to_add = {
                    "_id": hashed_base_url,
                    "all_links": all_links,
                    "page_text": parser.get_pure_page_text(page),
                    "html": str(page),
                    "title": page.find("title").get_text().replace("| Wookieepedia | Fandom", "").strip(),
                }
                bulk.find({"_id": hashed_base_url}).update_one({"$set": to_add})
                if i > every:
                    bulk.execute()
                    i = 0


def is_any_thread_alive(threads):
    return True in [t.is_alive() for t in threads]


def map_wookiepedia():
    provider = WebsitesProvider()
    threads = []
    print("Starting...")
    for _ in range(10):
        crawler = Crawler(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("Accumulated")
    while is_any_thread_alive(threads):
        time.sleep(1)


def cleanup_redirects():
    provider = WebsitesProviderForFixing()
    threads = []
    print("Starting...")
    for _ in range(10):
        crawler = RedirectFixer(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("Accumulated")
    while is_any_thread_alive(threads):
        time.sleep(1)
