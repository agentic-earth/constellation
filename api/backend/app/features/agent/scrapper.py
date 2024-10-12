from datetime import datetime
import json
import os
import pathlib
import requests
from bs4 import BeautifulSoup
import time
import xml.etree.ElementTree as ET

def arxiv_scraper(topics, max_results=100, start_date=None, end_date=None):
    base_url = "http://export.arxiv.org/api/query?"
    paper_counts = 0
    
    for topic in topics:
        query = f"search_query=all:{topic}&start=0&max_results={max_results}"
        if start_date and end_date:
            query += f"&date_range={start_date},{end_date}"
        
        response = requests.get(base_url + query)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                authors = [author.find('{http://www.w3.org/2005/Atom}name').text 
                           for author in entry.findall('{http://www.w3.org/2005/Atom}author')]
                abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text
                published = entry.find('{http://www.w3.org/2005/Atom}published').text
                doi = entry.find('{http://arxiv.org/schemas/atom}doi')
                doi = doi.text if doi is not None else None
                pdf_url = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]')
                pdf_url = pdf_url.attrib['href'] if pdf_url is not None else None
                
                paper_data = {
                    'title': title,
                    'authors': authors,
                    'abstract': abstract,
                    'published_date': published,
                    'doi': doi,
                    'pdf_url': pdf_url
                }
                # print(paper_data)
                save_paper_data(paper_data)
        
        time.sleep(3)  # Respect arXiv's rate limit

def save_paper_data(paper_data):
    # Create a folder to store the papers if it doesn't exist
    current_path = pathlib.Path(__file__).parent.resolve()
    scrape_folder = str(current_path) + "/scraped_papers"
    if not os.path.exists(scrape_folder):
        os.makedirs(scrape_folder)
    
    # Generate a unique filename for each paper
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(c for c in paper_data['title'] if c.isalnum() or c in (' ', '-', '_'))[:50]
    filename = f"{timestamp}_{safe_title}.json"
    
    # Construct the full file path
    file_path = os.path.join(scrape_folder, filename)
    
    # Save the paper data as a JSON file
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(paper_data, file, ensure_ascii=False, indent=4)
    
    print(f"Saved paper: {file_path}")

# Usage
if __name__ == "__main__":
    topics = [
        "earth science machine learning", 
        "earth science artificial intelligence", 
        "geoscience machine learning", 
        "geoscience artificial intelligence", 
        "climate science machine learning", 
        "climate science artificial intelligence"
    ]
    arxiv_scraper(topics, max_results=10, start_date="2020-01-01", end_date="2024-10-12")