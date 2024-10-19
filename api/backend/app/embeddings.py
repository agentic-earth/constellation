"""
PDF Embedding Service

This service is responsible for processing PDF files, extracting text,
and generating embeddings using SBERT (Sentence-BERT).

It provides functionality to:
1. Extract text from PDF files
2. Split text into paragraphs
3. Generate embeddings for paragraphs using SBERT
"""

import PyPDF2
import re
from typing import List, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class PDFEmbeddingService:
    def __init__(self):
        self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            str: Extracted text from the PDF.
        """
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def split_into_paragraphs(self, text: str) -> List[str]:
        """
        Split text into paragraphs.

        Args:
            text (str): Input text.

        Returns:
            List[str]: List of paragraphs.
        """
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def create_embeddings(self, paragraphs: List[str]) -> List[List[float]]:
        """
        Create embeddings for a list of paragraphs using SBERT.

        Args:
            paragraphs (List[str]): List of paragraphs.

        Returns:
            List[List[float]]: List of embeddings for each paragraph.
        """
        embeddings = self.sbert_model.encode(paragraphs)
        return embeddings.tolist()  # Convert numpy arrays to lists

    def process_pdf(self, pdf_path: str) -> Tuple[List[str], List[List[float]]]:
        """
        Process a PDF file and create embeddings for each paragraph.

        Args:
            pdf_path (str): Path to the PDF file.

        Returns:
            Tuple[List[str], List[List[float]]]: A tuple containing a list of paragraphs and their corresponding embeddings.
        """
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        
        paragraphs = self.split_into_paragraphs(text)

        # Create embeddings
        embeddings = self.create_embeddings(paragraphs)
        
        return paragraphs, embeddings

    # Debugging function
    def compute_similarity(self, embeddings1: List[List[float]], embeddings2: List[List[float]]) -> np.ndarray:
        embeddings1_array = np.array(embeddings1)
        embeddings2_array = np.array(embeddings2)
        
        similarity_matrix = cosine_similarity(embeddings1_array, embeddings2_array)
        return similarity_matrix

    # def embed_query(self, query: str) -> List[float]:
    #     """
    #     Create embedding for a single query string.

    #     Args:
    #         query (str): The query string to embed.

    #     Returns:
    #         List[float]: The embedding of the query.
    #     """
    #     embedding = self.sbert_model.encode([query])
    #     return embedding[0].tolist()  # Return as a list


# if __name__ == "__main__":
#     pdf_service = PDFEmbeddingService()
    
#     paragraphs1, embeddings1 = pdf_service.process_pdf("/Users/wanminghe/Desktop/swe/constellation-backend/api/backend/app/features/agent/services/demo_papers/s41586-023-06444-3.pdf")
#     paragraphs2, embeddings2 = pdf_service.process_pdf("/Users/wanminghe/Desktop/swe/constellation-backend/api/backend/app/features/agent/services/demo_papers/s43247-022-00344-6.pdf")
    
#     similarity_matrix = pdf_service.compute_similarity(embeddings1, embeddings2)

#     print(f"Similarity matrix shape: {similarity_matrix.shape}")
#     print(f"First similarity score: {similarity_matrix[0, 0]}")
