import logging
import time
from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from backend.data_provider import (
    get_doc_local_id_to_remote_id,
    get_wiki_ft_model,
    load_bm25,
)
from src.Config import Config
from src.storage.database import websites_db

logger = logging.getLogger()


def load_all_models():
    get_wiki_ft_model()
    get_doc_local_id_to_remote_id()
    load_bm25()


config = Config.get_config()
should_load_models_at_startup = config["should_load_models_at_startup"]
if should_load_models_at_startup == "true":
    logger.info("Loading all models at startup!")
    load_all_models()


@dataclass
class DebugRecordInformation:
    keywords: Optional[List[Tuple[str, float]]]
    debug_scores: Dict[str, Any]
    processing_time: float


@dataclass
class RecordResponse:
    url: str
    title: str
    urlId: str
    summary: str
    score: float
    modified_score: float
    debugInformation: Optional[DebugRecordInformation] = None


@dataclass
class SearchResponse:
    original_responses: List[RecordResponse]
    modified_responses: List[RecordResponse]
    time: float


class AbstractIndex(ABC):
    def search(self, query: List[str]):
        raise NotImplementedError()


keyword_fields = ["summary_keywords", "text_keywords", "processed_keywords"]
fields_to_download = {
    x: True for x in ["_id", "fixed_url", "title", "processed_text", "page_text", "xl_summary", "encoded_processed_text"] + keyword_fields
}


def ids_to_records(ids: List[str]):
    to_order = {id: i for i, id in enumerate(ids)}
    data = websites_db.find({"_id": {"$in": ids}}, fields_to_download)
    data = sorted(data, key=lambda x: to_order[x["_id"]])
    return data


def extract_keywords_from_page(page):
    keywords = []
    for key in keyword_fields:
        if key in page:
            d = page[key]
            if d == "None Found" or d[0] == "None Found":
                continue
            keywords.extend(d)
    return keywords


class BM25Index(AbstractIndex):
    def search(self, query: List[str], banned_keywords: List[str], top_n: int, is_debug: bool, temperature: float) -> SearchResponse:
        seach_start = time.time()

        bm25 = load_bm25()
        doc_scores = bm25.get_scores(query)
        negative_doc_scores = bm25.get_scores(banned_keywords)
        doc_scores = np.array(doc_scores)
        negative_doc_scores = np.array(negative_doc_scores)
        arr = doc_scores.argsort()[-top_n * 10 :][::-1]
        index = get_doc_local_id_to_remote_id()
        doc_ids = list(str(index[x]) for x in arr)
        responses: List[RecordResponse] = []

        wiki_ft_model = get_wiki_ft_model()
        for i, record in zip(arr, ids_to_records(doc_ids)):
            record_start = time.time()
            modified_score = doc_scores[i]
            bm25_score = doc_scores[i]
            doc_keywords = extract_keywords_from_page(record)
            processed_text_similarity = 0
            mean_closeness_to_bad_keywords = 0
            if len(banned_keywords) > 0:
                banned_keywords = (" ".join(banned_keywords)).split()
                encoded_banned_keywords = np.mean([wiki_ft_model.wv[vec] for vec in banned_keywords], axis=0)
                if "encoded_processed_text" in record:
                    mn = record["encoded_processed_text"]
                else:
                    mn = np.mean([wiki_ft_model.wv[vec] for vec in record["processed_text"]], axis=0)
                processed_text_similarity = cosine_similarity([encoded_banned_keywords, mn])[0][1]
                processed_text_similarity = float(processed_text_similarity)
                modified_score -= negative_doc_scores[i] * processed_text_similarity * temperature  # / 2
            if is_debug:
                summary = record["xl_summary"][:150] + "..."
                debugInformation = DebugRecordInformation(
                    keywords=doc_keywords,
                    debug_scores={
                        "negative_score": negative_doc_scores[i],
                        "processed_text_similarity": processed_text_similarity,
                        "mean_closeness_to_bad_keywords": str(mean_closeness_to_bad_keywords),
                    },
                    processing_time=time.time() - record_start,
                )
            else:
                summary = record["xl_summary"][:150] + "..."
                debugInformation = None

            response = RecordResponse(record["fixed_url"], record["title"], record["_id"], summary, bm25_score, modified_score, debugInformation)
            responses.append(response)
        logger.info("Response size ", len(responses))
        original_responses = sorted(responses, key=lambda x: -x.score)[:top_n]
        modified_responses = sorted(responses, key=lambda x: -x.modified_score)[:top_n]
        search_time = time.time() - seach_start
        return SearchResponse(original_responses, modified_responses, search_time)
