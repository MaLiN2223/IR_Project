import time

from src.crawler.Crawler import Crawler
from src.crawler.ProcessingTextGeneration import (
    DataProviderForTextProcessingTask,
    TextProcessingTask,
)
from src.crawler.RedirectFixer import RedirectFixer
from src.crawler.TextFromHtmlGeneration import (
    DataProviderForTextFromHtmlGeneration,
    TextFromHtmlGeneration,
)
from src.crawler.utils import is_any_thread_alive
from src.crawler.WebsitesProvider import DataProvider, WebsitesProvider
from src.crawler.WebsitesProviderForFixing import WebsitesProviderForFixing


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


def recompute_text():
    threads_count = 1
    provider = DataProviderForTextFromHtmlGeneration()
    threads = []
    print("Starting text recompute")
    for _ in range(threads_count):
        crawler = TextFromHtmlGeneration(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("All threads started")
    while is_any_thread_alive(threads):
        time.sleep(1)


def recompute_processed_text():
    threads_count = 10
    provider = DataProviderForTextProcessingTask()
    threads = []
    print("Starting text processing")
    for _ in range(threads_count):
        crawler = TextProcessingTask(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("All threads started")
    while is_any_thread_alive(threads):
        time.sleep(1)
