import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any

import ollama
from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 2000) -> str:
        pass

    @abstractmethod
    def generate_json(self, prompt: str, system_prompt: str = "", schema: Dict[str, Any] = None) -> dict:
        pass
        
    def _extract_json(self, response_text: str) -> dict:
        # JSON extraction/repair for malformed LLM outputs
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            if "```json" in response_text:
                try:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except Exception as e:
                    logger.error(f"Failed to extract JSON from markdown block: {e}")
            elif "```" in response_text:
                try:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except Exception as e:
                    logger.error(f"Failed to extract JSON from markdown block: {e}")
                    
            # Basic brute force: find first { and last }
            start = response_text.find("{")
            end = response_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(response_text[start:end+1])
                except Exception as e:
                    logger.error(f"Failed brute force JSON extraction: {e}")
                    
            raise ValueError(f"Could not parse valid JSON from response: {response_text[:100]}...")

def with_retry(max_retries=3, base_delay=1):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Max retries reached. Error: {e}")
                        raise
                    
                    delay = base_delay * (2 ** (retries - 1))
                    logger.warning(f"Error calling LLM: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.model = getattr(settings, "OLLAMA_MODEL", "llama3")
        
    @with_retry()
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 2000) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # We don't support streaming easily here since we return a str, but we can stream internally if wanted.
        response = ollama.chat(model=self.model, messages=messages, options={"temperature": temperature, "num_predict": max_tokens})
        return response['message']['content']
        
    @with_retry()
    def generate_json(self, prompt: str, system_prompt: str = "", schema: Dict[str, Any] = None) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        options = {"temperature": 0.0}
        
        response = ollama.chat(
            model=self.model,
            messages=messages,
            format="json",
            options=options
        )
        
        content = response['message']['content']
        return self._extract_json(content)


class OpenAIProvider(LLMProvider):
    def __init__(self):
        api_key = getattr(settings, "OPENAI_API_KEY", "")
        base_url = getattr(settings, "OPENAI_BASE_URL", None)
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4-turbo")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        
    @with_retry()
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7, max_tokens: int = 2000) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False # Could implement streaming generator if needed
        )
        return response.choices[0].message.content
        
    @with_retry()
    def generate_json(self, prompt: str, system_prompt: str = "", schema: Dict[str, Any] = None) -> dict:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        if schema:
            prompt += f"\n\nEnsure your output matches this JSON schema:\n{json.dumps(schema)}"
            
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return self._extract_json(response.choices[0].message.content)


def get_llm_provider() -> LLMProvider:
    provider_name = getattr(settings, "LLM_PROVIDER", "ollama").lower()
    if provider_name == "openai":
        return OpenAIProvider()
    else:
        return OllamaProvider()
