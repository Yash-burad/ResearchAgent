from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Send a text prompt to the LLM and return the string response.
        """
        pass

    @abstractmethod
    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        """
        Send a text prompt and get a structured response parsed into response_model.
        """
        pass
