import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Function metadata
functions = {
    "open_chrome": "Launch Google Chrome browser.",
    "open_calculator": "Open the system calculator.",
    "get_cpu_usage": "Retrieve current CPU usage in percentage.",
    "get_ram_usage": "Retrieve current RAM usage in percentage.",
    "run_shell_command": "Execute a given shell command and return output."
}

# Encode function descriptions
function_names = list(functions.keys())
descriptions = list(functions.values())
embeddings = model.encode(descriptions)

# Create FAISS index
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(np.array(embeddings, dtype=np.float32))

# Save index & metadata
faiss.write_index(index, "function_index.faiss")
with open("function_metadata.pkl", "wb") as f:
    pickle.dump(function_names, f)

print("FAISS index and metadata saved successfully.")
