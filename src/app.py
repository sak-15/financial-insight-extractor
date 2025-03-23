import streamlit as st
import os
import json
from fetch_data import fetch_filing_text
from query_engine import search
from vector_store import store_embeddings

# Function to handle file upload
def upload_filing():
    uploaded_file = st.file_uploader("Upload your SEC Filing", type="pdf")
    if uploaded_file is not None:
        # Save uploaded file to a temporary directory
        file_path = os.path.join("data", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        return file_path
    return None

# Function to display search results
def display_results(results):
    if len(results) == 0:
        st.warning("No relevant insights found.")
    else:
        for i, result in enumerate(results, 1):
            st.write(f"{i}. {result}")

# Streamlit app layout
def main():
    st.set_page_config(page_title="Financial Insights Extractor", layout="wide")

    st.title("Financial Insights Extractor using SEC Filings")
    st.markdown("""
    Welcome to the **Financial Insights Extractor**. This tool helps you extract and search relevant financial data 
    from SEC filings like 10-K reports, including data on revenue, earnings, liabilities, and more.
    """)

    # File Upload
    st.sidebar.header("Upload SEC Filing")
    file_path = upload_filing()

    # Select Company and Report Type
    st.sidebar.header("Select Company and Report Type")
    company_name = st.sidebar.text_input("Company Name", "")
    report_type = st.sidebar.selectbox("Report Type", ["10-K", "10-Q"])

    # Fetch Filing Data
    if file_path and company_name:
        if st.button("Process Filing Data"):
            # Fetch and process data (add your logic for fetching here)
            fetch_filing_text(company_name, report_type)
            store_embeddings(company_name, report_type)
            st.success(f"Data processed for {company_name} ({report_type} report)")

    # Query Search
    st.sidebar.header("Search Financial Data")
    query = st.text_input("Enter your financial query", "")

    if query:
        top_k = st.slider("Select number of top results", 1, 10, 5)
        with st.spinner("Searching..."):
            results = search(query, company_name, report_type, top_k=top_k)
            st.success("Search completed!")
            display_results(results)

if __name__ == "__main__":
    main()
