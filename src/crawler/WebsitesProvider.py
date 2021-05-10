from threading import Lock
from tqdm import tqdm
from crawler.utils import normalize_url
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


class WebsitesProvider:
    def __init__(self) -> None:
        self.database = websites_db
        self.query = {
            "page_text": {"$exists": False},
            "leased": {"$exists": False},
            "error_code": {"$exists": False},
            "fixed_url": {"$not": {"$regex": ".*\\.ogg$"}},
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
            return urls
