import string
from multiprocessing import Pool
from typing import Iterable, Set

import nltk
from nltk.stem import SnowballStemmer, WordNetLemmatizer
from nltk.tokenize import ToktokTokenizer


def word_not_in_set(word, set):
    return word not in set


class Pipeline:
    def __init__(self, stopwords: Set[str]) -> None:
        self.stopwords = stopwords
        self.ps = WordNetLemmatizer()
        self.stemmer = SnowballStemmer("english")
        self.tokenizer = ToktokTokenizer()
        self.puncuation = set(string.punctuation)
        # self.words = set(nltk.corpus.words.words())
        self.pipeline = [
            self.remove_punctuation,
            self.tokenize,
            self.lowering,
            self.remove_words,
            self.remove_stopwords,
            self.remove_digits_and_punctuation,
            self.remove_dangling_puncuation,
            self.remove_single,
            self.stemm,
            self.remove_starting_with_file,
        ]
        self.words_to_remove = set(
            "edit wookieepedia format registerr wrapup wiki sandbox click edit page link code preview button format".split(" ")
        )

    def remove_starting_with_file(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if not word.startswith("file"):
                yield word

    def remove_words(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if word not in self.words_to_remove:
                yield word

    def cleanup_space(self, a_string: str) -> str:
        return a_string.replace("|", " ").replace("\n", " ")

    def remove_dangling_puncuation(self, document_iterable: Iterable[str]) -> Iterable[str]:
        return [w.strip(string.punctuation) for w in document_iterable]

    def tokenize(self, document: str) -> Iterable[str]:
        for word in self.tokenizer.tokenize(document):
            yield word

    def remove_digits_and_punctuation(self, document_iterable: Iterable[str]) -> Iterable[str]:
        return [w for w in document_iterable if not all(x.isdigit() or x in self.puncuation for x in w)]

    def remove_punctuation(self, document: str) -> str:
        return document.translate(str.maketrans("", "", string.punctuation))

    def remove_stopwords(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if word_not_in_set(word, self.stopwords):
                yield word

    def remove_everything_with_digit(self, document_iterable: Iterable[str]) -> Iterable[str]:
        return [w for w in document_iterable if not any(x.isdigit() for x in w)]

    def lowering(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            yield word.lower()

    def lemmatize(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            yield self.ps.lemmatize(word)

    def stemm(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            yield self.stemmer.stem(word)

    def remove_single(self, document_iterable: Iterable[str]) -> Iterable[str]:
        for word in document_iterable:
            if len(word) > 1:
                yield word

    def pipe(self, document: str) -> Iterable[str]:
        ob = document
        for task in self.pipeline:
            ob = task(ob)
        return ob
