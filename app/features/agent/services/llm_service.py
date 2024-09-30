import asyncio
import sys
import os
from pydantic import ValidationError
# from logger import ConstellationLogger
from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import DenseRetriever, PromptNode, EmbeddingRetriever
from haystack.pipelines import ExtractiveQAPipeline
from haystack.pipelines import Pipeline

class LLMService:

    def __init__(self):
        # self.logger = ConstellationLogger().get_logger("LLMService")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")

    def construct_prompt(self, user_message: str, context: dict) -> str:
        # Logic to construct a prompt using user message and graph context
        
        return f"Given the following context: {context}, answer the following question: {user_message}"

    def make_llm_request(self, prompt: str) -> str:
        # Step 1: Initialize a document store (in-memory for this example)
        document_store = InMemoryDocumentStore()

        # Step 2: Add some documents to the document store
        documents = [
            {"content": "The Eiffel Tower is located in Paris."},
            {"content": "The Great Wall of China is one of the greatest wonders of the world."},
            {"content": "The Statue of Liberty was a gift from France to the United States."}
        ]

        document_store.write_documents(documents)

        print("Initializing retriever")
        retriever = EmbeddingRetriever(
            embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1", document_store=document_store, api_key=self.openai_api_key
        )
        print("Initializing prompt node")
        prompt_node = PromptNode(
            model_name_or_path="gpt-3.5-turbo", 
            api_key=self.openai_api_key, 
            default_prompt_template="deepset/question-answering"
        )
        print("Running pipeline")

        query_pipeline = Pipeline()
        query_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
        query_pipeline.add_node(component=prompt_node, name="PromptNode", inputs=["Retriever"])
        query_pipeline.run(prompt)

        # Step 7: Return the answer
        # return results['answers'][0].answer

    # async def process_llm_output(self, llm_json_str: str) -> PipelineAPIRequest:
    #     try:
    #         # Parse and validate the LLM's JSON output
    #         pipeline_request = PipelineAPIRequest.parse_raw(llm_json_str)
    #         # Use the validated object to make API calls or process further
    #         return pipeline_request
    #     except ValidationError as e:
    #         # Handle validation errors, possibly by asking the LLM to correct its output
    #         self.logger.error(f"LLM generated invalid JSON: {e}")
    #         # Implement error handling strategy (e.g., retry, fallback, or user notification)

if __name__ == "__main__":
    # Example usage
    # llm_output = '{"data": {"image_url": "https://example.com/image.jpg"}, "metadata": {"source": "llm"}}'
    # sys.path.insert(0, '/Users/justinxiao/Downloads/coursecode/CSCI2340/constellation-backend/app')
    LLMService = LLMService()
    pipeline_request = LLMService.make_llm_request(
                                        LLMService.construct_prompt("Where is the Eiffel Tower located?", 
                                                {
                                                    "context": "A user is trying to ask you a question regarding, please answer with profession and accuracy"
                                                }))
    print(pipeline_request)
    