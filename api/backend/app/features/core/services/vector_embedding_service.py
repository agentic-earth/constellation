"""
Vector Embedding Service Module

TO LEO + RUTH: This is a mock and the API keys / configs with other aspects need to be used.

This module implements a Vector Embedding Service using Haystack's OpenAI Embedders.

Design Pattern:
- Repository Pattern: The VectorEmbeddingService class encapsulates the core operations required to embed texts and documents.
- Dependency Injection: The API key is injected via environment variables or initialization.
- Cohesive Structure: Following consistent design principles for a uniform service interface.

Key Design Decisions:
1. Flexible API: The service provides functions for embedding both text strings and documents (PDFs).
2. Separate Methods for Text and Document: This ensures clear input requirements and error handling.
3. Type Safety and Consistency: Type hints are used to maintain consistency.
4. Error Handling: Exceptions are allowed to propagate for handling by the caller.

This design enables scalable and reusable embedding functionalities for different content types.
"""

import asyncio
from typing import List, Dict, Optional
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack import Document
from haystack.utils import Secret
import os
from backend.app.logger import ConstellationLogger  # Assuming the logger is similar to BlockService
import PyPDF2


class VectorEmbeddingService:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the VectorEmbeddingService.

        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, will use the environment variable OPENAI_API_KEY.
        """
        self.logger = ConstellationLogger()
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in the OPENAI_API_KEY environment variable.")

        self.text_embedder = OpenAITextEmbedder(api_key=Secret.from_token(self.api_key))
        self.document_embedder = OpenAIDocumentEmbedder(api_key=Secret.from_token(self.api_key))

    async def generate_text_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generates a vector embedding for the provided text.

        Args:
            text (str): The text to generate an embedding for.

        Returns:
            Optional[List[float]]: The generated vector embedding. None on exception.
        """
        try:
            result = self.text_embedder.run(text)
            embedding = result["embedding"]
            self.logger.log("VectorEmbeddingService", "info", f"Text embedding generated successfully.", text=text)
            return embedding
        except Exception as e:
            self.logger.log("VectorEmbeddingService", "error", "Failed to generate text embedding", error=str(e))
            return None

    async def generate_document_embedding(self, pdf_file_path: str) -> Optional[List[float]]:
        """
        Generates a vector embedding for the content of a PDF document.

        Args:
            pdf_file_path (str): The path to the PDF file.

        Returns:
            Optional[List[float]]: The generated vector embedding. None on exception.
        """
        try:
            content = self._pdf_to_text(pdf_file_path)
            document = Document(content=content, meta={"name": pdf_file_path})
            result = self.document_embedder.run([document])
            embedding = result["documents"][0].embedding
            self.logger.log("VectorEmbeddingService", "info", "Document embedding generated successfully.", document_name=pdf_file_path)
            return embedding
        except Exception as e:
            self.logger.log("VectorEmbeddingService", "error", "Failed to generate document embedding", error=str(e))
            return None

    def _pdf_to_text(self, pdf_path: str) -> str:
        """
        Internal method to extract text from a PDF file.

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

async def main():
    """
    Main function to demonstrate and test the VectorEmbeddingService functionality.
    """
    print("Starting VectorEmbeddingService test...")

    # Initialize the embedding service
    try:
        embedding_service = VectorEmbeddingService()
    except ValueError as e:
        print(f"Initialization error: {e}")
        return

    # Generate text embedding
    text_to_embed = "The Earth is the only known planet that supports life."
    try:
        text_embedding = await embedding_service.generate_text_embedding(text_to_embed)
        print(f"Generated text embedding: {text_embedding[:5]}... (truncated)")  # Showing only first 5 values for brevity
    except Exception as e:
        print(f"Failed to generate text embedding: {e}")

    # Generate document embedding
    pdf_path = "sample.pdf"  # Assuming a sample PDF exists at this location
    try:
        document_embedding = await embedding_service.generate_document_embedding(pdf_path)
        print(f"Generated document embedding: {document_embedding[:5]}... (truncated)")  # Showing only first 5 values for brevity
    except Exception as e:
        print(f"Failed to generate document embedding: {e}")

if __name__ == "__main__":
    asyncio.run(main())
