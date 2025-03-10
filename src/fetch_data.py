import requests
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

headers = {
    "User-Agent": "sakshi sakshi@gmail.com"
    }

def fetch_filing_text(cik, accession_number, primary_doc):
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
        return filing_text
    else:
        print(f"Error fetching filing text: {response.status_code}")
        return ""

# Example: Apple ke 10-K filing ka text extract karna
cik = "0000320193"
accession_number = "000032019323000106"
primary_doc = "aapl-20230930"

filing_text = fetch_filing_text(cik, accession_number, primary_doc)

# Save as text file
with open("data/apple_10k.txt", "w", encoding="utf-8") as f:
    f.write(filing_text)

print("Apple 10-K filing text saved!")
