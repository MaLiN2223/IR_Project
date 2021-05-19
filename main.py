from src.crawler.tasks import cleanup_redirects, recompute_processed_text
from src.data_processing.normalization import (
    direct_logs_to_console,
    dump_corpus_to_file,
    generate_bm25,
    generate_fasttext_vectors,
    generate_lookup,
    generate_tfidf,
    generate_weighted_vectors,
    prepare_dictionary,
    search,
    train_fasttext,
    train_prepared_wiki_model,
)
from src.data_processing.tasks.tasks import (
    add_keywords,
    encode_preprocessed_text,
    map_wookiepedia,
    recompute_text,
    summarise,
)


def compute_index():
    direct_logs_to_console()
    dump_corpus_to_file()
    generate_bm25()
    train_fasttext(300, "fin", "fasttext_300.model", generate_tmp_file=True)

    # OLD BELOW
    # prepare_dictionary()
    # generate_tfidf()
    # generate_weighted_vectors()
    # generate_fasttext_vectors()
    # generate_lookup()
    # search()


def initialize_database():
    map_wookiepedia()
    # cleanup_redirects()
    recompute_text()  # html -> page_text
    recompute_processed_text()  # page_test - >processed_tet


def preprocess_for_extraction():
    # summarise()
    encode_preprocessed_text()
    # add_keywords() #


# initialize_database()
# compute_index()

preprocess_for_extraction()
# Re train wiki model?
# train_prepared_wiki_model()
