from src.crawler.Crawler import map_wookiepedia
from src.data_processing.normalization import (
    dump_corpus_to_file,
    prepare_dictionary,
    generate_cleaned_text,
    generate_tfidf,
    generate_weighted_vectors,
    generate_tookup,
    search,
    train_fasttext,
)


def compute_index():
    # dump_corpus_to_file()
    # prepare_dictionary()
    # generate_tfidf()
    train_fasttext()
    generate_weighted_vectors()
    generate_tookup()
    search()


# map_wookiepedia()
# generate_cleaned_text()
compute_index()
