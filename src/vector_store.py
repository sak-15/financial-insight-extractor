import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def store_embeddings(company_name, report_type):
    # Load Pretrained Sentence Transformer Model (FREE)
    model = SentenceTransformer("all-MiniLM-L6-v2")  # Fast and accurate

    chunk_file_path = f"data/{company_name}_{report_type}_chunks.json"

    # Load preprocessed text chunks from JSON file
    with open(chunk_file_path, "r", encoding="utf-8") as f:
        text_chunks = json.load(f)

    # Generate embeddings for each chunk
    embeddings = model.encode(text_chunks, convert_to_numpy=True)

    # Create FAISS vector database
    dimension = embeddings.shape[1]  # Auto-detect dimensions
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save FAISS index for future use
    faiss.write_index(index, f"data/{company_name}_{report_type}_chunks.index")

    print(f"✅ {len(text_chunks)} embeddings stored in FAISS vector database!")
