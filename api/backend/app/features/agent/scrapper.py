import io
import os
import pathlib
import requests
import time
import xml.etree.ElementTree as ET
import time
import os.path

def arxiv_scraper(topics, max_results=100, start_date=None, end_date=None):
    base_url = "http://export.arxiv.org/api/query?"
    
    for topic in topics:
        query = f"search_query=all:{topic}&start=0&max_results={max_results}"
        if start_date and end_date:
            query += f"&date_range={start_date},{end_date}"
        
        response = requests.get(base_url + query)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = entry.find('{http://www.w3.org/2005/Atom}title').text
                pdf_url = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]')
                pdf_url = pdf_url.attrib['href'] if pdf_url is not None else None
                
                paper_data = {
                    'title': title,
                    'pdf_url': pdf_url
                }
                save_paper_data(paper_data)
        
        time.sleep(3)  # Respect arXiv's rate limit

def save_paper_data(paper_data):
    # Create a folder to store the papers if it doesn't exist
    current_path = pathlib.Path(__file__).parent.resolve()
    scrape_folder = str(current_path) + "/scraped_papers"
    if not os.path.exists(scrape_folder):
        os.makedirs(scrape_folder)
    
    response = requests.get(paper_data['pdf_url'])
    bytes_io = io.BytesIO(response.content)
    # Construct the full file path
    file_path = os.path.join(scrape_folder, paper_data['title'])
    if response.status_code == 200:
        with open(f"{file_path}.pdf", 'wb') as file:
            file.write(bytes_io.getvalue())
        print(f"PDF downloaded successfully: {file_path}")
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")

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