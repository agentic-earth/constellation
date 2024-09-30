from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def generate_response(self, prompt: str) -> str:
        pass

class OpenAIProvider(LLMProvider):
    async def generate_response(self, prompt: str) -> str:
        # Implementation for OpenAI
        
        pass

class HuggingFaceProvider(LLMProvider):
    async def generate_response(self, prompt: str) -> str:
        # Implementation for Hugging Face
        pass