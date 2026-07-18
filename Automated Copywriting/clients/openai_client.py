# clients/openai_client.py
"""
OpenAI API wrapper with retry logic and error handling
"""

import os
import asyncio
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from parameter_tuner import GenerationParams


class OpenAIClient:
    """Async OpenAI client with retry and rate-limit handling"""
    
    def __init__(self, api_key: str = None):
        """Initialize with API key from .env or parameter"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set. Add to .env file.")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_copy(
        self,
        prompt: str,
        params: GenerationParams
    ) -> str:
        """
        Generate copy via OpenAI API with retry logic.
        
        Args:
            prompt: System prompt with injected variables
            params: GenerationParams with temperature, tokens, top_p
            
        Returns:
            Generated text from OpenAI
            
        Raises:
            httpx.HTTPError: On API failures after retries
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional copywriter."},
                {"role": "user", "content": prompt}
            ],
            "temperature": params.temperature,
            "top_p": params.top_p,
            "max_tokens": params.max_tokens
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
    
    async def generate_copy_with_fallback(
        self,
        prompt: str,
        params: GenerationParams,
        fallback_text: str = "[Generation failed - using fallback]"
    ) -> str:
        """
        Generate copy with fallback on error.
        
        Args:
            prompt: System prompt
            params: Generation parameters
            fallback_text: Text to return if API fails
            
        Returns:
            Generated text or fallback
        """
        try:
            return await self.generate_copy(prompt, params)
        except Exception as e:
            print(f"⚠️  API Error: {e}. Using fallback.")
            return fallback_text