import urllib.request
from threading import Thread
from urllib.parse import quote

import numpy as np
from bs4 import BeautifulSoup
from gensim.models.fasttext import FastText
from tqdm.std import tqdm

from src.crawler.PagesDownloader import PagesDownloader
from src.crawler.PagesParser import PagesParser
from src.crawler.utils import encode_url, normalize_url
from src.crawler.WebsitesProvider import DataProvider
from src.storage.database import websites_db

page_url_should_not_contain = [
    "action=edit",
    "diff=10",
    "?action=purge",
    "?oldid=",
    "Wookieepedia_talk:",
    "?action=history",
    "/Talk:",
    "/File:",
    "Special:",
    "?redirect",
    "Wookieepedia:Inq",
    ":Diff/",
    "/User:",
    "Wookieepedia:Trash_compactor",
    "?t=",
    "/Forum:",
    "Wookieepedia_Contests_talk:",
    "/Wookieepedia_Help:",
    "Category_talk:",
    "Forum_talk:",
    "Wookieepedia_Contests:",
    "/Wookieepedia_Help_talk:",
    "_talk:",
    "/User_blog:",
    "Thread:1746468",
    "/Terms_of_Use",
    "/Message_Wall:",
    "/Template:",
    "/Message_Wall:",
    "/Community_Central:",
]


def should_map(url: str):
    url = normalize_url(url)
    if url.startswith("starwars.fandom.com/wiki") or url.startswith("wiki/"):
        lower_url = url.lower()
        for banned in page_url_should_not_contain:
            if banned.lower() in lower_url:
                return False
        return True
    else:
        return False


def fix_wookiepedia(url: str):
    if url.startswith("https://starwars.fandom.com/wiki/") or url.startswith("http://starwars.fandom.com/wiki/"):
        pass
    elif url.startswith("/wiki/"):
        url = "https://starwars.fandom.com" + url
    else:
        raise Exception(url)
    url = url.split("#")[0]
    return url.split("?")[0]


class DataProviderForDownloadPagesTask(DataProvider):
    def __init__(self) -> None:
        override_query = {"page_text": {"$exists": False}, "error_code": {"$exists": False}, "fixed_url": {"$exists": True}}
        super().__init__(10, fields_to_download=["_id", "fixed_url"], additional_query_params=override_query, should_count=False)


def get_page(url, downloader, hashed_base_url, as_unicode=False):
    try:
        if as_unicode:
            url = url.replace("https://starwars.fandom.com/wiki/", "")
            url = "https://starwars.fandom.com/wiki/" + quote(url)
        return downloader.get_page(url.replace(" ", "_"))
    except urllib.request.HTTPError as e:
        code = e.code
        to_add = {"_id": hashed_base_url, "error_code": int(code)}
        websites_db.update({"_id": hashed_base_url}, to_add)
        return None
    except UnicodeEncodeError as uer:
        if not as_unicode:
            return get_page(url, downloader, hashed_base_url, True)
        to_add = {"_id": hashed_base_url, "error": str(uer), "error_code": -1}
        websites_db.update({"_id": hashed_base_url}, to_add)
        return None


# new crawler
class DownloadPagesTask(Thread):
    def __init__(self, provider: DataProviderForDownloadPagesTask) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        downloader = PagesDownloader()
        parser = PagesParser()
        while True:
            documents = self.provider.get_records()
            if len(documents) == 0:
                break
            bulk = websites_db.initialize_unordered_bulk_op()
            for document in tqdm(documents, desc="thread", leave=False):
                url = document["fixed_url"]
                id = document["_id"]
                if not should_map(url):
                    bulk.find({"_id": id}).update_one({"$set": {"skipped": "url should not map"}})
                    continue
                hashed_base_url = encode_url(url)
                page = get_page(url, downloader, hashed_base_url)
                if page is None:
                    print("Skipping", url)
                    continue
                page = BeautifulSoup(page, "html.parser")
                all_links = parser.extract_links(page)
                wookiepedia_links = [(fix_wookiepedia(x), x) for x in all_links if x is not None and should_map(x)]
                for fixed_link, _ in wookiepedia_links:
                    hashed_url = encode_url(fixed_link)
                    normalized_url = normalize_url(fixed_link)
                    bulk.find({"_id": hashed_url}).upsert().update_one(
                        {
                            "$setOnInsert": {
                                "_id": hashed_url,
                                "fixed_url": fixed_link,
                                "normalized_url": normalized_url,
                                "real_base_url": normalize_url(url, False),
                            }
                        }
                    )
                page_text = parser.get_pure_page_text(page)
                if page_text is None:
                    bulk.find({"_id": hashed_base_url}).update_one({"$set": {"error": "empty content", "error_code": -1}})
                    continue
                to_add = {
                    "_id": hashed_base_url,
                    "all_links": all_links,
                    "page_text": parser.get_pure_page_text(page),
                    "html": str(page),
                    "title": page.find("title").get_text().replace("| Wookieepedia | Fandom", "").strip(),
                }
                bulk.find({"_id": hashed_base_url}).update_one({"$set": to_add})
            bulk.execute()
