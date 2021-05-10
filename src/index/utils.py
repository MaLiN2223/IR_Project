from typing import Iterable, Optional
from gensim.models.fasttext import FastText
from src.index.contants import fasttet_model_name, index_file_name, dump_ids_file_name


def load_fasttext(model_name: str):
    return FastText.load(f"./data/{model_name}/{fasttet_model_name}")


def load_index(model_name: str):
    import nmslib

    index = nmslib.init(method="hnsw", space="cosinesimil")
    index.loadIndex(filename=f"./data/{model_name}/{index_file_name}")
    return index


def load_indexes(model_name: Optional[str] = None) -> Iterable[str]:
    file_name = f"./data/{model_name}/{dump_ids_file_name}" if model_name is not None else f"./data/{dump_ids_file_name}"
    with open(file_name, "r", encoding="utf-8") as ids:
        for line in ids:
            yield line.strip()
