from typing import Iterable, Set


class Pipeline:
    def __init__(self, stopwords: Set[str]) -> None:
        self.stopwords = stopwords

    def remove_stopwords(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if word not in self.stopwords:
                yield word
