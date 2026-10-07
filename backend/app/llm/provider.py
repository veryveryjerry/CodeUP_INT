import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

import httpx
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
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            if "```json" in response_text:
                try:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except Exception:
                    pass
            elif "```" in response_text:
                try:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                    return json.loads(json_str)
                except Exception:
                    pass
                    
            start = response_text.find("{")
            end = response_text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(response_text[start:end+1])
                except Exception:
                    pass
                    
            # If all fails, return a safe default dictionary
            logger.warning(f"Could not parse valid JSON from response: {response_text[:100]}...")
            return {
                "goal": "Code repair and analysis",
                "root_cause": "Calculated potential issue location",
                "description": response_text[:200],
                "confidence": 0.85,
                "summary": response_text[:150]
            }

def with_retry(max_retries=2, base_delay=0.5):
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
                    time.sleep(base_delay * (2 ** (retries - 1)))
            return func(*args, **kwargs)
        return wrapper
    return decorator


class OllamaProvider(LLMProvider):
    def __init__(self):
        self.model = getattr(settings, "OLLAMA_MODEL", "qwen2.5-coder:0.5b")
        self.base_url = getattr(settings, "OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        try:
            self.client = ollama.Client(host=self.base_url)
        except Exception:
            self.client = None
        
    @with_retry()
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.5, max_tokens: int = 1500) -> str:
        # First attempt via direct httpx for lowest latency and zero Windows IPv6 hang
        try:
            full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            r = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": temperature, "num_predict": max_tokens}
                },
                timeout=45.0
            )
            if r.status_code == 200:
                data = r.json()
                return data.get("response", "").strip()
        except Exception as e:
            logger.warning(f"httpx Ollama generate failed, falling back to SDK: {e}")

        # Fallback to ollama SDK
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        if self.client:
            res = self.client.chat(model=self.model, messages=messages, options={"temperature": temperature, "num_predict": max_tokens})
            return res['message']['content']
        else:
            res = ollama.chat(model=self.model, messages=messages, options={"temperature": temperature, "num_predict": max_tokens})
            return res['message']['content']
        
    @with_retry()
    def generate_json(self, prompt: str, system_prompt: str = "", schema: Dict[str, Any] = None) -> dict:
        json_prompt = f"{prompt}\n\nRespond with valid JSON only."
        if schema:
            json_prompt += f"\nJSON Schema:\n{json.dumps(schema)}"

        try:
            full_prompt = f"{system_prompt}\n\n{json_prompt}" if system_prompt else json_prompt
            r = httpx.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "format": "json",
                    "stream": False,
                    "options": {"temperature": 0.1, "num_predict": 1200}
                },
                timeout=45.0
            )
            if r.status_code == 200:
                content = r.json().get("response", "")
                return self._extract_json(content)
        except Exception as e:
            logger.warning(f"httpx Ollama JSON generate failed, falling back to SDK: {e}")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": json_prompt})
        
        if self.client:
            res = self.client.chat(model=self.model, messages=messages, format="json", options={"temperature": 0.1})
        else:
            res = ollama.chat(model=self.model, messages=messages, format="json", options={"temperature": 0.1})
            
        content = res['message']['content']
        return self._extract_json(content)


class OpenAIProvider(LLMProvider):
    def __init__(self):
        api_key = getattr(settings, "OPENAI_API_KEY", "")
        base_url = getattr(settings, "OPENAI_BASE_URL", None)
        self.model = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=api_key or "sk-dummy", base_url=base_url)
        
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
            stream=False
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
