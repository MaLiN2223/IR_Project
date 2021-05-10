from threading import Thread
from crawler.PagesDownloader import PagesDownloader
from crawler.PagesParser import PagesParser
from crawler.WebsitesProvider import WebsitesProvider


class TextFromHtmlGeneration(Thread):
    def __init__(self, provider: WebsitesProvider) -> None:
        self.provider = provider
        return super().__init__()

    def run(self) -> None:
        pass
        # downloader = PagesDownloader()
        # parser = PagesParser()
        # no_data = 0
