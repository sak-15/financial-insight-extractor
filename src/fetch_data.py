# Import the required libraries

import requests
import os
from bs4 import BeautifulSoup
import warnings
from preprocessing import preprocess_file
from vector_store import store_embeddings
from datetime import datetime
warnings.filterwarnings("ignore")

# Set the headers for the requests
headers = {
    "User-Agent": "sakshi sakshi@gmail.com"
    }

# User will be only knowing company name, so we need to fetch CIK, accession number and primary document from sec for company. 
# So below is the function to fetch CIK, accession number and primary document
def get_cik(company_name):
    '''
    Given a company name, fetch the CIK (Central Index Key) from the SEC API.
    '''
    cik_url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(cik_url, headers=headers)

    if response.status_code == 200:
        cik_data = response.json()

        for company in cik_data.values():  # Directly loop through values()
            if isinstance(company, dict) and "title" in company:
                if company_name.lower() in company["title"].lower():
                    cik = str(company["cik_str"]).zfill(10)
                    print(cik)
                    return str(company["cik_str"]).zfill(10)
    
    return None

def get_latest_filing_details(cik, report_type="10-K"):
    """
    Given a company's CIK, fetch the latest SEC filing details using SEC API.
    """
    base_url = f"https://data.sec.gov/submissions/CIK{int(cik):010}.json"
    
    response = requests.get(base_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        filings = data.get("filings", {}).get("recent", {})

        form_types = filings.get("form", [])
        accession_numbers = filings.get("accessionNumber", [])
        primary_docs = filings.get("primaryDocument", [])

        # Check if required report type (e.g., 10-K) exists
        for i, form in enumerate(form_types):
            if form == report_type:
                accession_number = accession_numbers[i].replace("-", "")
                primary_doc = primary_docs[i]
                print(accession_number, primary_doc)
                return accession_number, primary_doc

    print("No filing found!")
    return None, None


# fetching the fillings from sec
def fetch_filing_text(company_name, report_type):
    """
    Given a company's CIK, filing accession number, and primary document name,
    fetch and return the full filing text.
    """
    cik = get_cik(company_name)
    accession_number, primary_doc = get_latest_filing_details(cik, report_type)
    # primary_doc = get_primary_doc(cik, accession_number)

    # SEC EDGAR filing URL
    filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_number}/{primary_doc}"
    
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

## Example input
# company_name = "Amazon"
# report_type = "10-K"

# filing_text = fetch_filing_text(company_name, report_type)
