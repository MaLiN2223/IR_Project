from src.index.simplification_pipeline import Pipeline
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
        self.assertEqual(test_text, "hello !")


if __name__ == "__main__":
    unittest.main()
