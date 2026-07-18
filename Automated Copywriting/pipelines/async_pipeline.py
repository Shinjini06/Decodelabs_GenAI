# pipelines/async_pipeline.py
"""
Real-time async pipeline with semaphore-based concurrency control
Uses asyncio.gather for parallel execution with rate-limiting
"""

import asyncio
from typing import List, Tuple
from models import CopyRequest, CopyResponse
from template_compiler import TemplateCompiler
from parameter_tuner import ParameterTuner
from clients.openai_client import OpenAIClient


class AsyncPipeline:
    """
    Real-time async pipeline for copy generation.
    Features:
    - Non-blocking execution via asyncio
    - Semaphore-based concurrency control (prevent rate limits)
    - Parallel batch processing
    """
    
    def __init__(self, api_key: str = None, max_concurrent: int = 5):
        """
        Initialize async pipeline.
        
        Args:
            api_key: OpenAI API key
            max_concurrent: Max simultaneous API calls (default: 5)
        """
        self.client = OpenAIClient(api_key)
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def _bounded_call(self, prompt: str, copy_request: CopyRequest) -> Tuple[CopyRequest, str]:
        """
        Acquire semaphore, call API, release semaphore.
        Prevents rate-limit errors by limiting concurrent requests.
        """
        async with self.semaphore:
            params = ParameterTuner.tune(copy_request)
            
            generated_copy = await self.client.generate_copy_with_fallback(prompt, params)
            return (copy_request, generated_copy)
    
    async def generate_single(self, copy_request: CopyRequest) -> CopyResponse:
        """
        Generate copy for single product asynchronously.
        
        Args:
            copy_request: Request with product, platform, tone
            
        Returns:
            CopyResponse with generated copy and metadata
        """
        prompt = TemplateCompiler.compile(copy_request)
        
        _, generated_copy = await self._bounded_call(prompt, copy_request)
        
        response = CopyResponse(
            product_name=copy_request.product_name,
            platform=copy_request.platform.value,
            tone=copy_request.tone.value,
            copy=generated_copy
        )
        
        return response
    
    async def generate_batch(self, copy_requests: List[CopyRequest]) -> List[CopyResponse]:
        """
        Generate copy for multiple products in parallel.
        
        Args:
            copy_requests: List of CopyRequest objects
            
        Returns:
            List of CopyResponse objects (order matches input)
        """
        tasks = []
        
        for copy_request in copy_requests:
            prompt = TemplateCompiler.compile(copy_request)
            tasks.append(self._bounded_call(prompt, copy_request))
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert results to CopyResponse objects
        responses = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"Error processing request {idx}: {result}")
                responses.append(None)
            else:
                copy_request, generated_copy = result
                response = CopyResponse(
                    product_name=copy_request.product_name,
                    platform=copy_request.platform.value,
                    tone=copy_request.tone.value,
                    copy=generated_copy
                )
                responses.append(response)
        
        return responses


async def main_demo():
    """Demo: Single and batch async generation"""
    print("=" * 70)
    print("PHASE 4: ASYNC PIPELINE DEMO")
    print("=" * 70)
    
    # Initialize pipeline
    pipeline = AsyncPipeline(max_concurrent=3)
    
    # Demo 1: Single generation
    print("\n✓ Single Generation (Async)")
    from models import PlatformEnum, ToneEnum
    
    single_req = CopyRequest(
        product_name="Premium Headphones",
        platform=PlatformEnum.LINKEDIN,
        tone=ToneEnum.PROFESSIONAL
    )
    
    print(f"  Generating for: {single_req.product_name}")
    response = await pipeline.generate_single(single_req)
    print(f"  Generated: {response.copy}")
    print(f"  Char Count: {response.char_count}")
    
    # Demo 2: Batch generation (if API key available)
    print("\n✓ Batch Generation (Parallel, Semaphore-limited)")
    batch_requests = [
        CopyRequest(
            product_name="Running Shoes",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.WITTY
        ),
        CopyRequest(
            product_name="Project Manager Software",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        ),
        CopyRequest(
            product_name="Yoga Mat",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.CASUAL
        ),
    ]
    
    print(f"  Processing {len(batch_requests)} requests in parallel...")
    responses = await pipeline.generate_batch(batch_requests)
    
    for idx, resp in enumerate(responses):
        if resp:
            print(f"\n  [{idx+1}] {resp.product_name} ({resp.platform})")
            print(f"      Copy: {resp.copy[:60]}...")
            print(f"      Chars: {resp.char_count}")


if __name__ == "__main__":
    # Note: Requires valid OPENAI_API_KEY
    try:
        asyncio.run(main_demo())
    except ValueError as e:
        print(f"⚠️  {e}")
        print("\nTo run this demo:")
        print("1. Create .env file with OPENAI_API_KEY=your_key")
        print("2. Run: python -m pipelines.async_pipeline")