from sentence_transformers import SentenceTransformer

import pickle
import bson


def compute_vectors():
    model = SentenceTransformer("paraphrase-distilroberta-base-v1")
    query = {"page_text": {"$exists": True}, "vectorized": {"$exists": False}}
    bulk = websites_db.initialize_unordered_bulk_op()
    i = 0
    N = 1000
    for item in tqdm(websites_db.find(query, {"page_text": True})):
        encoded = model.encode([item["page_text"]])[0]
        encoded = bson.Binary(pickle.dumps(encoded, protocol=2))
        bulk.find({"_id": item["_id"]}).update_one({"$set": {"vectorized": encoded}})
        i += 1
        if i > N:
            bulk.execute()
            bulk = websites_db.initialize_unordered_bulk_op()
            i = 0
