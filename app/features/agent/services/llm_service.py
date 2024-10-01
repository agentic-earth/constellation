import asyncio
import sys
import os
from pydantic import ValidationError
# from logger import ConstellationLogger
from haystack import Pipeline, Document
from haystack.components.builders import PromptBuilder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import OpenAITextEmbedder, OpenAIDocumentEmbedder
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.generators import OpenAIGenerator

class LLMService:

    def __init__(self):
        # self.logger = ConstellationLogger().get_logger("LLMService")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")

    def construct_prompt(self, user_message: str, context: dict) -> str:
        # Logic to construct a prompt using user message and graph context
        
        return f"Given the following context: {context}, answer the following question: {user_message}"

    def make_llm_request(self, prompt: str) -> str:
        # Step 1: Initialize a document store (in-memory for this example)
        document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")

        # Step 2: Initialize a retriever and connect it to the document store
        retriever = InMemoryEmbeddingRetriever(document_store=document_store)

        # Step 3: Add some documents to the document store
        documents = [
            Document(content='The Eiffel Tower is located in Paris.'),
            Document(content='The Great Wall of China is one of the greatest wonders of the world.'),
            Document(content='The Statue of Liberty was a gift from France to the United States.')
        ]
        document_store.write_documents(documents)

        # Step 4: Generate embeddings for the documents
        document_store.update_embeddings(retriever)

        # Proceed with the rest of your pipeline
        # Step 5: Initialize text embedder, prompt builder, and generator
        text_embedder = OpenAITextEmbedder()
        prompt_template = """
            Given the following context, answer the question:
            Context: 
            {% for doc in documents %}
                {{ doc.content }}
            {% endfor %}
            Question: {{query}}
            Answer:
        """
        prompt_builder = PromptBuilder(template=prompt_template)
        generator = OpenAIGenerator(model="gpt-3.5-turbo")

        # Build and connect the pipeline
        pipeline = Pipeline()
        pipeline.add_component("text_embedder", text_embedder)
        pipeline.add_component("retriever", retriever)
        pipeline.add_component("prompt_builder", prompt_builder)
        pipeline.add_component("generator", generator)

        # Connect components
        pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
        pipeline.connect("retriever.documents", "prompt_builder.documents")
        pipeline.connect("prompt_builder.prompt", "generator.prompt")

        # Run the pipeline
        query = "Where is the Eiffel Tower located?"
        result = pipeline.run(
            {
                "text_embedder": {"text": query},
                "retriever": {"top_k": 3},
                "prompt_builder": {"query": query}
            }
        )
        print(result)
