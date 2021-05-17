from src.crawler.tasks import recompute_processed_text
from src.data_processing.normalization import (
    direct_logs_to_console,
    dump_corpus_to_file,
    generate_cleaned_text,
    generate_fasttext_vectors,
    generate_tfidf,
    generate_tookup,
    generate_weighted_vectors,
    prepare_dictionary,
    search,
    train_fasttext,
    train_prepared_wiki_model,
)
from src.data_processing.tasks.tasks import (
    add_keywords,
    encode_preprocessed_text,
    recompute_text,
    summarise,
)


def compute_index():
    direct_logs_to_console()
    # dump_corpus_to_file()
    # prepare_dictionary()
    # generate_tfidf()
    train_fasttext(300, "ft", "fasttext_300.model", generate_tmp_file=False)
    # generate_weighted_vectors()
    # generate_fasttext_vectors()
    # generate_tookup()
    # search()


# # map_wookiepedia()
# # generate_cleaned_text()
# recompute_text()
# compute_index()

# train_prepared_wiki_model()

# # cleanup_redirects()
# recompute_processed_text()

#
# summarise()

# recompute_text()
# add_keywords()

# compute_index()
encode_preprocessed_text()
