import time

# from src.crawler.Crawler import Crawler
from src.crawler.ProcessingTextGeneration import (
    DataProviderForTextProcessingTask,
    TextProcessingTask,
)

# from src.crawler.RedirectFixer import RedirectFixer
from src.crawler.utils import is_any_thread_alive

# from src.crawler.WebsitesProvider import DataProvider, WebsitesProvider


def cleanup_redirects():
    raise NotImplementedError("Below might not work anymore")
    # provider = WebsitesProviderForFixing()
    # threads = []
    # print("Starting...")
    # for _ in range(10):
    #     crawler = RedirectFixer(provider)
    #     crawler.daemon = True
    #     crawler.start()
    #     time.sleep(5)
    #     threads.append(crawler)
    # print("Accumulated")
    # while is_any_thread_alive(threads):
    #     time.sleep(1)


def recompute_processed_text():
    threads_count = 5
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
