import httpx
import json
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from research_agent.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)

class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model_name: str):
        self.base_url = base_url.rstrip("/")
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        url = f"{self.base_url}/api/chat"
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.2
            }
        }

        try:
            response = httpx.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            res_json = response.json()
            return res_json["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"Ollama generation failed: {e}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        url = f"{self.base_url}/api/chat"
        
        # Format the schema for the model
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        schema_prompt = (
            f"\nYou MUST output a JSON object that strictly adheres to the following JSON Schema:\n"
            f"{schema_json}\n"
            f"Do not return any conversational text, explanations, or code fences. "
            f"Only return the raw JSON object."
        )
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt + schema_prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.1
            }
        }

        content = ""
        try:
            response = httpx.post(url, json=payload, timeout=60.0)
            response.raise_for_status()
            res_json = response.json()
            content = res_json["message"]["content"]
            
            # Clean and validate JSON
            cleaned = content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            return response_model.model_validate_json(cleaned)
        except Exception as e:
            raise RuntimeError(
                f"Ollama structured generation failed: {e}\n"
                f"Response content received: {content}"
            )
