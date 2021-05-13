from src.crawler.WebsitesProvider import WebsitesProvider


class WebsitesProviderForFixing(WebsitesProvider):
    def __init__(self) -> None:
        override_query = {
            "leased": {"$exists": False},
            "error_code": {"$exists": False},
        }
        raise Exception("Need to change below!")
        super().__init__(override_query=override_query, include_ids=True)
