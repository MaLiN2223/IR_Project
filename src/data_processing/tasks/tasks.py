import time

from src.crawler.utils import is_any_thread_alive
from src.data_processing.tasks.DownloadPagesTask import (
    DataProviderForDownloadPagesTask,
    DownloadPagesTask,
)
from src.data_processing.tasks.EncodeProcessedTextTask import (
    DataProviderForEncodeProcessedTextTask,
    EncodeProcessedTextTask,
)
from src.data_processing.tasks.KeywordsExtractionTask import (
    DataProviderKeywordsExtractionTask,
    KeywordsExtractionTask,
)
from src.data_processing.tasks.TextFromHtmlGeneration import (
    DataProviderForTextFromHtmlGeneration,
    TextFromHtmlGeneration,
)
from src.data_processing.tasks.XLSummarizationTask import (
    DataProviderForXlSummarizationTask,
    XlSummarizationTask,
)


def map_wookiepedia():
    provider = DataProviderForDownloadPagesTask()
    threads = []
    print("Starting...")
    for _ in range(5):
        crawler = DownloadPagesTask(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("Accumulated")
    while is_any_thread_alive(threads):
        time.sleep(1)


def recompute_text():
    threads_count = 10
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


def summarise():
    threads_count = 2
    provider = DataProviderForXlSummarizationTask()
    threads = []
    print("Starting text processing")
    for _ in range(threads_count):
        crawler = XlSummarizationTask(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("All threads started")
    while is_any_thread_alive(threads):
        time.sleep(1)


def add_keywords():
    threads_count = 2
    provider = DataProviderKeywordsExtractionTask()
    threads = []
    print("Starting text processing")
    for _ in range(threads_count):
        crawler = KeywordsExtractionTask(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("All threads started")
    while is_any_thread_alive(threads):
        time.sleep(1)


def encode_preprocessed_text():
    threads_count = 2
    provider = DataProviderForEncodeProcessedTextTask()
    threads = []
    print("Starting text processing")
    for _ in range(threads_count):
        crawler = EncodeProcessedTextTask(provider)
        crawler.daemon = True
        crawler.start()
        time.sleep(5)
        threads.append(crawler)
    print("All threads started")
    while is_any_thread_alive(threads):
        time.sleep(1)
