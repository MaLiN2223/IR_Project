from src.crawler.tasks import recompute_processed_text, recompute_text
from src.data_processing.normalization import (
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


def compute_index():
    dump_corpus_to_file()
    prepare_dictionary()
    generate_tfidf()
    train_fasttext()
    # generate_weighted_vectors()
    generate_fasttext_vectors()
    generate_tookup()
    search()


# # map_wookiepedia()
# # generate_cleaned_text()
# recompute_text()
# compute_index()

# train_prepared_wiki_model()

# # cleanup_redirects()
# recompute_processed_text()

#
