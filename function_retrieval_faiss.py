import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer


# Load FAISS index & metadata
index = faiss.read_index("function_index.faiss")
with open("function_metadata.pkl", "rb") as f:
    function_names = pickle.load(f)

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def retrieve_best_function(user_query):
    query_embedding = model.encode([user_query]).astype(np.float32)
    _, nearest_idx = index.search(query_embedding, 1)

    best_function = function_names[nearest_idx[0][0]]
    return best_function


