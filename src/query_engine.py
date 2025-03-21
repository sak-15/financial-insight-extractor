import faiss
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from fetch_data import fetch_filing_text

# Load the same SentenceTransformer model
model = SentenceTransformer("all-MiniLM-L6-v2")

def check_file(company_name, report_type):
    """Check if data exists for the company; if not, fetch and process it."""
    index_path = f"data/{company_name}_{report_type}_chunks.index"
    json_path = f"data/{company_name}_{report_type}_chunks.json"

    if os.path.exists(index_path) and os.path.exists(json_path):
        print(f"✅ Data already exists for {company_name}.")
        return True  # Data is already available

    print(f"⚡ Fetching & processing data for {company_name}...")
    
    # Fetch filing text
    fetch_filing_text(company_name, report_type)
    
    # After fetching, ensure files were created
    if os.path.exists(index_path) and os.path.exists(json_path):
        print(f"✅ Data successfully processed for {company_name}.")
        return True
    else:
        print(f"❌ Failed to process data for {company_name}.")
        return False

def search(query,company_name, report_type, top_k=5):
    """Search for top_k most relevant chunks in FAISS"""

    # Check if data exists for the company; if not, fetch and process it
    check_file(company_name, report_type)

    # Load FAISS index
    index = faiss.read_index(f"data/{company_name}_{report_type}_chunks.index")
    text_chunks = json.load(open(f"data/{company_name}_{report_type}_chunks.json", "r"))

    # Convert query to embedding
    query_embedding = model.encode([query], convert_to_numpy=True)

    # Search FAISS index
    distances, indices = index.search(query_embedding, top_k)

    # Get the matching text chunks
    results = [text_chunks[idx] for idx in indices[0]]
    
    return results


# Example Usage
query = "Apple's revenue growth in 2023"  # Replace with any financial query
top_matches = search(query, "Apple", "10-K")

print("\n🔍 **Top Relevant Financial Insights:**\n")
for i, match in enumerate(top_matches, 1):
    print(f"{i}. {match}\n")
