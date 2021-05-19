from threading import Lock
from typing import Any, Dict, List, Optional

from tqdm import tqdm

from src.crawler.utils import normalize_url
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


class DataProvider:
    def __init__(
        self,
        batch_size: int = 500,
        fields_to_download: List[str] = [],
        additional_query_params: Optional[Dict[str, Any]] = None,
        should_count: bool = False,
        no_cursor_timeout: bool = False,
    ) -> None:
        self.database = websites_db
        query = {}
        if additional_query_params is not None:
            for key, value in additional_query_params.items():
                query[key] = value

        to_download = {key: 1 for key in fields_to_download}
        self.batch_size = batch_size
        self.lock = Lock()
        print("Query", query)
        print("To download", to_download)
        print("Counting...")
        count = self.database.count_documents(query) if should_count else 219719  # TODO: maybe it is not performant?
        print(f"Counted : {count}, cursor initialization...")

        self.cursor = self.database.find(query, to_download, no_cursor_timeout=no_cursor_timeout)
        self.pbar = tqdm(total=count, desc="documents_iteration")

        # self.database.update_many({"leased": True}, {"$unset": {"leased": True}})

    def get_records(self) -> List[Dict[str, Any]]:
        data = []
        with self.lock:
            for item in self.cursor:
                data.append(item)
                if len(data) >= self.batch_size:
                    break
            self.pbar.update(len(data))
            return data


class WebsitesProvider:
    def __init__(
        self, override_query: Optional[Dict[str, Any]] = None, special_fields: Optional[List[str]] = None, no_cursor_timeout: bool = False
    ) -> None:
        self.database = websites_db
        self.query = {
            "page_text": {"$exists": False},
            "leased": {"$exists": False},
            "error_code": {"$exists": False},
            "fixed_url": {"$not": {"$regex": ".*\\.ogg$"}},
        }
        if override_query is not None:
            self.query = override_query
        self.special_fields = special_fields
        self.lock = Lock()
        self.database.update_many({"leased": True}, {"$unset": {"leased": True}})

    def get_pages(self, size: int = 500):
        urls = []
        ids = []
        if self.special_fields is not None:
            additional_fields = [[] * len(self.special_fields)]
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
                if self.special_fields is not None:
                    for i, field in enumerate(self.special_fields):
                        additional_fields[i].append(record[field])
                ids.append(record["_id"])
                if len(urls) == size:
                    break
            self.database.update_many({"_id": {"$in": ids}}, {"$set": {"leased": True}})
            if self.special_fields is not None:
                return urls, additional_fields
            else:
                return urls
