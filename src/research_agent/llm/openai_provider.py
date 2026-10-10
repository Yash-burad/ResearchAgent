import httpx
import json
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from research_agent.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model_name: str = "gpt-4o-mini"):
        if not api_key:
            raise ValueError("OpenAI API key is required")
        self.api_key = api_key
        self.model_name = model_name

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.2
        }

        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            res_json = response.json()
            return res_json["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Inject schema instruction
        schema_json = json.dumps(response_model.model_json_schema(), indent=2)
        schema_prompt = (
            f"\nYou MUST output a JSON object that strictly adheres to the following JSON Schema:\n"
            f"{schema_json}\n"
            f"Only return the raw JSON object."
        )
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt + schema_prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {
                "type": "json_object"
            }
        }

        content = ""
        try:
            response = httpx.post(url, json=payload, headers=headers, timeout=60.0)
            response.raise_for_status()
            res_json = response.json()
            content = res_json["choices"][0]["message"]["content"]
            
            # Clean and validate
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
                f"OpenAI structured generation failed: {e}\n"
                f"Response content received: {content}"
            )
