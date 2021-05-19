from src.index.preprocessing_pipeline import Pipeline
import unittest
import pytest


class TestingCleanup(unittest.TestCase):
    @staticmethod
    def iterate(document):
        for word in document.split(" "):
            yield word

    def test_remove_stopwords_simple(self):
        stopwords = set(["stop1", "stop2"])
        document = "hello stop1 stop2 !"
        pipeline = Pipeline(stopwords)
        test_text = pipeline.remove_stopwords(TestingCleanup.iterate(document))
        self.assertEqual(" ".join(test_text), "hello !")

    def test_splitting(self):
        document = "hello, is this me you looking for?"
        pipeline = Pipeline(set())
        test_text = pipeline.tokenize(document)
        self.assertEqual(" ".join(test_text), "hello , is this me you looking for ?")

    def test_splitting_new_line(self):
        document = "hello,\n!what? or?"
        pipeline = Pipeline(set())
        test_text = pipeline.tokenize(document)
        self.assertEqual(" ".join(test_text), "hello , ! what ? or ?")

    def test_splitting_with_numbers(self):
        document = "my number is 11-123-15!"
        pipeline = Pipeline(set())
        test_text = pipeline.tokenize(document)
        self.assertEqual(" ".join(test_text), "my number is 11-123-15 !")


# class TestingPipeline(unittest.TestCase):
#     def test_simple(self):
#         stopwords = set(["a", "and", "the", "of"])
#         document = "The Republic, which had lasted for at least 25,034 years, ended following a period of intense political turmoil and the subsequent devastation of the Clone Wars. "
#         pipeline = Pipeline(stopwords)
#         test_text = pipeline.pipe(document)
#         # self.assertEqual(" ".join(test_text), "hello !")


if __name__ == "__main__":
    unittest.main()
