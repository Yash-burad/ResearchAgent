import httpx
import json
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from research_agent.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)

class GeminiProvider(LLMProvider):
    # Candidate models ordered by speed and stability
    FALLBACK_MODELS = [
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.8-flash",
        "gemini-flash-latest"
    ]

    def __init__(self, api_key: str, model_name: str = "gemini-3.5-flash-lite"):
        if not api_key:
            raise ValueError("Gemini API key is required")
        self.api_key = api_key
        self.model_name = model_name

    def _get_models_to_try(self) -> list:
        models = [self.model_name]
        for m in self.FALLBACK_MODELS:
            if m not in models:
                models.append(m)
        return models

    def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        last_err = None
        for model in self._get_models_to_try():
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.2
                }
            }
            
            if system_instruction:
                payload["systemInstruction"] = {
                    "parts": [{"text": system_instruction}]
                }

            try:
                response = httpx.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                res_json = response.json()
                return res_json["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                last_err = e
                continue
                
        raise RuntimeError(f"Gemini generation failed across models: {last_err}")

    def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: Optional[str] = None
    ) -> T:
        schema = response_model.model_json_schema()
        
        structured_prompt = (
            f"{prompt}\n\n"
            f"IMPORTANT: You MUST respond ONLY with a valid JSON object matching this exact JSON schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```\n"
            f"Do not include any explanation outside the JSON."
        )

        payload = {
            "contents": [{
                "parts": [{"text": structured_prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json"
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        last_err = None
        content = ""
        for model in self._get_models_to_try():
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            try:
                response = httpx.post(url, json=payload, timeout=60.0)
                response.raise_for_status()
                res_json = response.json()
                content = res_json["candidates"][0]["content"]["parts"][0]["text"]
                
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
                last_err = e
                continue

        raise RuntimeError(
            f"Gemini structured generation failed across models: {last_err}\n"
            f"Last response received: {content}"
        )
