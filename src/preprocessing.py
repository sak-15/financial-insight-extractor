import re
import json
import os
   

def clean_filing_text(text):
    """
    Filing text ko clean karta hai:
    - Extra whitespaces aur newlines hataata hai.
    - URLs, currency tags, share tags aur 10-digit CIK numbers remove karta hai.
    - Sirf 'us-gaap:' aur 'aapl:' se related data extract karta hai.
    """
    # Remove extra whitespace & newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove URLs
    text = re.sub(r'http\S+', '', text)
    
    # Remove currency and share tags
    text = re.sub(r'\biso4217:USD\b', '', text)
    text = re.sub(r'\bxbrli:shares\b', '', text)
    
    # Remove 10-digit CIK numbers (redundant metadata)
    text = re.sub(r'\b\d{10}\b', '', text)
    
    # Extract only financial statement related tags (e.g., us-gaap: or aapl:)
    important_sections = re.findall(r'(us-gaap:Assets|us-gaap:Liabilities|us-gaap:Revenue|us-gaap:Earnings|us-gaap:RetainedEarnings|aapl:\S+)', text)
    
    # Return unique tags joined by newline
    return '\n'.join(set(important_sections))

def chunk_text(text, chunk_size=300, overlap=50):
    """
    Text ko words ke hisaab se chunks me todta hai.
    Har chunk me 'chunk_size' words honge aur consecutive chunks me 'overlap' words overlap karenge.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = ' '.join(words[i : i + chunk_size])
        chunks.append(chunk)
    return chunks

revenue_keywords = ["Revenue", "Sales", "Net Income", "Gross Profit", "Operating Income", 
                    "Total Revenue", "Earnings", "Growth", "Financial Performance"]

def clean_xbrl_tags(text):
    # Extract relevant financial terms
    important_sections = re.findall(r'([a-zA-Z]+)?[:]?([A-Z]?\d*\.?\d*%?[A-Za-z]+(?:Due\d{4})?Member)', text)

    cleaned_terms = []
    for prefix, term in important_sections:
        term = term.replace("Member", "")  # Remove 'Member' suffix
        term = re.sub(r'([A-Z])(\d)', r'\1 \2', term)  # Separate words & numbers
        term = re.sub(r'(\d+)\.(\d+)', r'\1.\2%', term)  # Convert percentages

        # Normalize bond/note descriptions
        term = re.sub(r'Notesdue(\d{4})', r'Notes Due \1', term, flags=re.IGNORECASE)
        term = re.sub(r'(\d+)%?', r'\1%', term)  # Handling percentage format
        term = term.replace("Member", "")  # Remove 'Member' suffix
        term = re.sub(r'([A-Z])(\d)', r'\1 \2', term)  # Separate words and numbers

        
        # Format final term
        cleaned_terms.append(term.strip())

    return cleaned_terms

def get_interpreted_terms(tags):
    tag_to_description = {
        'RetainedEarnings': 'Retained earnings, representing cumulative profits not distributed as dividends.',
        'Notes Due': 'Bond issued by the company with a specific due date.',
        'Notes Due 2025': 'Bond due in 2025, with interest payments.',
        'Revenue': 'The total revenue earned by the company.',
        'Liabilities': 'Total liabilities owed by the company to creditors.',
    }

    interpreted_terms = []
    for tag in tags:
        # Get the description based on the tag or just use the tag itself
        interpreted_terms.append(tag_to_description.get(tag, tag))

    return interpreted_terms

def preprocess_file(input_filepath, output_filepath):
    """
    Input file (raw filing text) ko read karta hai, clean aur chunk karta hai,
    aur processed chunks ko output JSON file me save kar deta hai.
    """
    if not os.path.exists(input_filepath):
        print(f"❌ File not found: {input_filepath}")
        return
    
    # Read raw filing text
    with open(input_filepath, "r", encoding="utf-8") as f:
        raw_text = f.read()
    
    # Clean the text
    cleaned_text = clean_filing_text(raw_text)
    
    # Chunk the cleaned text
    chunks = chunk_text(cleaned_text)
    chunks = clean_xbrl_tags("\n".join(chunks))
    chunks = get_interpreted_terms(chunks)
    
    # Save chunks to JSON file
    with open(output_filepath, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=4)
    
    print(f"✅ Preprocessing complete. {len(chunks)} chunks saved to {output_filepath}")

