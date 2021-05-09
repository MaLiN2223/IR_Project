from typing import Iterable, Set
import nltk
from nltk.stem import WordNetLemmatizer
import string
from multiprocessing import Pool


def word_not_in_set(word, set):
    return word not in set


class Pipeline:
    def __init__(self, stopwords: Set[str]) -> None:
        self.stopwords = stopwords
        self.ps = WordNetLemmatizer()
        # self.words = set(nltk.corpus.words.words())
        self.pipeline = [self.tokenize, self.lowering, self.remove_punctuation, self.remove_stopwords, self.remove_empty, self.stemm]

    def tokenize(self, document: str) -> Iterable[str]:
        for word in nltk.word_tokenize(document):
            yield word

    def remove_punctuation(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            yield word.translate(str.maketrans("", "", string.punctuation))
            # if word in self.words:
            #    yield word

    def remove_stopwords(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if word_not_in_set(word, self.stopwords):
                yield word

    def lowering(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            yield word.lower()

    def stemm(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            yield self.ps.lemmatize(word)

    def remove_empty(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if len(word) > 0:
                yield word

    def pipe(self, document: str):
        ob = document
        for task in self.pipeline:
            ob = task(ob)
        return ob
