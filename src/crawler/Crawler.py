import time
import urllib.request
from threading import Thread

from bs4 import BeautifulSoup
from tqdm import tqdm

from src.crawler.PagesDownloader import PagesDownloader
from src.crawler.PagesParser import PagesParser
from src.crawler.utils import encode_url, normalize_url
from src.crawler.WebsitesProvider import WebsitesProvider, should_map
from src.storage.database import websites_db


def fix_wookiepedia(url: str):
    if url.startswith("https://starwars.fandom.com/wiki/"):
        pass
    elif url.startswith("/wiki/"):
        url = "https://starwars.fandom.com" + url
    else:
        raise Exception(url)
    url = url.split("#")[0]
    return url.split("?")[0]


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
                raise Exception("Check if page url is the same as page.url!")
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
