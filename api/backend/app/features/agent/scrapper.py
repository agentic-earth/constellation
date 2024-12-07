import io
import os
import pathlib
import json
import uuid
import asyncio
from backend.app.features.core.controllers.block_controller import BlockController
from backend.app.config import Settings
from prisma import Prisma
import requests
import time
import xml.etree.ElementTree as ET
import time
import os.path

class ArxivScraper:
    def __init__(self):
        # self.settings = Settings()
        self.prisma = Prisma(datasource={"url": str(Settings().DATABASE_URL)})
        self.controller = BlockController(self.prisma)

    def arxiv_scraper(self, topics, max_results=100, start_date=None, end_date=None):
        base_url = "http://export.arxiv.org/api/query?"
        paper_data = []
        for topic in topics:
            query = f"search_query=all:{topic}&start=0&max_results={max_results}"
            if start_date and end_date:
                query += f"&date_range={start_date},{end_date}"
            
            response = requests.get(base_url + query)
            
            if response.status_code == 200:
                root = ET.fromstring(response.content)
                
                for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
                    title = entry.find('{http://www.w3.org/2005/Atom}title').text
                    abstract = entry.find('{http://www.w3.org/2005/Atom}summary').text
                    pdf_url = entry.find('{http://www.w3.org/2005/Atom}link[@title="pdf"]')
                    pdf_url = pdf_url.attrib['href'] if pdf_url is not None else None
                    
                    paper_data.append({
                        'title': title,
                        'abstract': abstract,
                        'pdf_url': pdf_url
                    })
                    # save_paper_data(paper_data)
                    print({
                        'title': title,
                        'abstract': abstract,
                        'pdf_url': pdf_url
                    })
            
            time.sleep(3)  # Respect arXiv's rate limit
        return paper_data

    def save_paper_data(self, paper_data):
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

    def save_paper_data_json(self, paper_data):
        # Create a folder to store the papers if it doesn't exist
        current_path = pathlib.Path(__file__).parent.resolve()
        scrape_folder = str(current_path) + "/scraped_papers"
        if not os.path.exists(scrape_folder):
            os.makedirs(scrape_folder)
        file_path = os.path.join(scrape_folder, "paper_data.json")
        with open(f"{file_path}", 'w') as file:
            json.dump(paper_data, file)

    async def store_paper_data(self, paper_data):
        # Store the paper data in a database
        user_id = uuid.uuid4()
        await self.prisma.connect()
        try:
            async with self.prisma.tx(timeout=10000) as tx:
                for paper in paper_data:
                    paper['block_type'] = 'paper'
                    created_block = await self.controller.create_block(paper, user_id)
                    if created_block:
                        print(f"Created block: {created_block}")
                    else:
                        print(f"Failed to create block for {paper['title']}")
        except Exception as e:
            print(f"An error occurred: {e}")
            import traceback
            print(traceback.format_exc())

        finally:
            await self.prisma.disconnect()
            print("Disconnected from the database")


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
    scraper = ArxivScraper()
    current_path = pathlib.Path(__file__).parent.resolve()
    file_path = os.path.join(str(current_path), "scraped_papers/paper_data.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            paper_data = json.load(file)
    else:
        paper_data = scraper.arxiv_scraper(topics, max_results=10, start_date="2023-01-01", end_date="2024-10-12")
        scraper.save_paper_data_json(paper_data)
    asyncio.run(scraper.store_paper_data(paper_data))