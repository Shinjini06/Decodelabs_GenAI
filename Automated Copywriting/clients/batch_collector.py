# clients/batch_collector.py
"""
Batch Collector for OpenAI Batch API
Manages batch job creation, polling, and result retrieval
"""

import json
import time
from typing import List, Dict, Optional
import httpx
from models import CopyRequest, CopyResponse
from template_compiler import TemplateCompiler
from parameter_tuner import ParameterTuner


class BatchCollector:
    """
    Manages OpenAI Batch API operations:
    - Create batch jobs from CopyRequest list
    - Poll job status
    - Retrieve and parse results
    - Validate Pydantic output schemas
    """
    
    def __init__(self, api_key: str = None):
        """Initialize batch collector"""
        import os
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = "https://api.openai.com/v1"
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set")
    
    def _create_batch_request(self, copy_request: CopyRequest) -> Dict:
        """
        Create a single batch request in OpenAI format.
        
        Returns:
            {"custom_id": "req_1", "method": "POST", "url": "...", "body": {...}}
        """
        prompt = TemplateCompiler.compile(copy_request)
        params = ParameterTuner.tune(copy_request)
        
        return {
            "custom_id": f"{copy_request.product_name.replace(' ', '_')}_{copy_request.platform.value}",
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a professional copywriter."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": params.temperature,
                "top_p": params.top_p,
                "max_tokens": params.max_tokens
            }
        }
    
    async def create_batch(self, copy_requests: List[CopyRequest]) -> str:
        """
        Create a batch job via OpenAI Batch API.
        
        Args:
            copy_requests: List of CopyRequest objects
            
        Returns:
            Batch job ID (e.g., "batch_abc123...")
        """
        # Create JSONL file content (newline-delimited JSON)
        batch_requests = [
            self._create_batch_request(req) for req in copy_requests
        ]
        
        jsonl_content = "\n".join(json.dumps(req) for req in batch_requests)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "requests": batch_requests  # OpenAI accepts array format
        }
        
        async with httpx.AsyncClient() as client:
            # Upload batch file
            response = await client.post(
                f"{self.base_url}/batches",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            batch_data = response.json()
            return batch_data["id"]
    
    async def poll_batch_status(
        self,
        batch_id: str,
        poll_interval: int = 30,
        max_polls: int = 1000
    ) -> Dict:
        """
        Poll batch job status until completion.
        
        Args:
            batch_id: Batch job ID
            poll_interval: Seconds between polls (default: 30)
            max_polls: Max number of polls before timeout
            
        Returns:
            Final batch status dict with results
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        polls = 0
        async with httpx.AsyncClient() as client:
            while polls < max_polls:
                response = await client.get(
                    f"{self.base_url}/batches/{batch_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                batch_data = response.json()
                status = batch_data.get("status")
                
                print(f"  [Poll {polls+1}] Status: {status}")
                
                if status in ["completed", "failed", "expired"]:
                    return batch_data
                
                await asyncio.sleep(poll_interval)
                polls += 1
        
        raise TimeoutError(f"Batch {batch_id} did not complete within {max_polls * poll_interval}s")
    
    async def retrieve_results(self, batch_id: str) -> List[CopyResponse]:
        """
        Retrieve and parse batch results.
        
        Args:
            batch_id: Batch job ID
            
        Returns:
            List of CopyResponse objects
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        responses = []
        
        async with httpx.AsyncClient() as client:
            # Get batch data
            response = await client.get(
                f"{self.base_url}/batches/{batch_id}",
                headers=headers
            )
            response.raise_for_status()
            
            batch_data = response.json()
            
            # Get results file URL
            if "output_file_id" not in batch_data:
                print(f"⚠️  Batch {batch_id} has no output file")
                return responses
            
            output_file_id = batch_data["output_file_id"]
            
            # Download results
            result_response = await client.get(
                f"{self.base_url}/files/{output_file_id}/content",
                headers=headers
            )
            result_response.raise_for_status()
            
            # Parse JSONL results
            for line in result_response.text.strip().split("\n"):
                if not line:
                    continue
                
                result = json.loads(line)
                
                # Extract from batch response format
                if result["status_code"] == 200:
                    message = result["response"]["body"]["choices"][0]["message"]["content"]
                    
                    # Parse custom_id to get product info
                    custom_id = result["custom_id"]
                    product_name, platform = custom_id.rsplit("_", 1)
                    product_name = product_name.replace("_", " ")
                    
                    copy_response = CopyResponse(
                        product_name=product_name,
                        platform=platform,
                        tone="professional",  # Would need to store in custom_id
                        copy=message
                    )
                    responses.append(copy_response)
                else:
                    print(f"⚠️  Error for {result['custom_id']}: {result}")
        
        return responses


import asyncio