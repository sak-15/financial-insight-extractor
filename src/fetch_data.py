import requests
import os
from bs4 import BeautifulSoup
import warnings
from preprocessing import preprocess_file
from vector_store import store_embeddings
warnings.filterwarnings("ignore")

headers = {
    "User-Agent": "sakshi sakshi@gmail.com"
    }

def fetch_filing_text(cik, accession_number, primary_doc, company_name, report_type):
    """
    Given a company's CIK, filing accession number, and primary document name,
    fetch and return the full filing text.
    """
    # SEC EDGAR filing URL
    filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{primary_doc}.htm"
    
    response = requests.get(filing_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        filing_text = soup.get_text(separator="\n")

        # Generate file name
        filename = f"data/{company_name}_{report_type}.txt"
        chunks_filepath = f"data/{company_name}_{report_type}_chunks.json"


        # Save as text file
        if os.path.exists(filename):
            print(f"File already exists: {filename}")
        else:
            # Save the file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(filing_text)
            preprocess_file(filename, chunks_filepath)
            print(f"Raw and chunks file saved for: {company_name}")
            store_embeddings(company_name, report_type)
            print(f"Embeddings stored for: {company_name}")
    else:
        print(f"Error fetching filing text: {response.status_code}")

# # Example: Apple ke 10-K filing 
cik = "0000320193"
accession_number = "000032019323000106"
primary_doc = "aapl-20230930"
company_name = "Apple"
report_type = "10-K"

filing_text = fetch_filing_text(cik, accession_number, primary_doc, company_name, report_type)
