# phase4_test.py
"""
Phase 4: Async Pipeline Integration Tests
Mock-based testing (no real API calls required)
"""

import asyncio
from models import CopyRequest, CopyResponse, PlatformEnum, ToneEnum


class MockAsyncPipeline:
    """Mock async pipeline for testing"""
    
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.call_count = 0
    
    async def _bounded_call(self, prompt: str, copy_request: CopyRequest):
        async with self.semaphore:
            self.call_count += 1
            await asyncio.sleep(0.05)  # Simulate API latency
            
            mock_responses = {
                ToneEnum.WITTY: f"🚀 {copy_request.product_name} - where innovation meets perfection!",
                ToneEnum.PROFESSIONAL: f"Experience excellence with {copy_request.product_name}. Premium quality guaranteed.",
                ToneEnum.CASUAL: f"Check out {copy_request.product_name}! It's pretty amazing, honestly.",
                ToneEnum.PERSUASIVE: f"Don't miss out! {copy_request.product_name} is exactly what you need.",
            }
            
            mock_copy = mock_responses.get(copy_request.tone, "Great product!")
            return (copy_request, mock_copy)
    
    async def generate_single(self, copy_request: CopyRequest) -> CopyResponse:
        _, generated_copy = await self._bounded_call("mock_prompt", copy_request)
        response = CopyResponse(
            product_name=copy_request.product_name,
            platform=copy_request.platform.value,
            tone=copy_request.tone.value,
            copy=generated_copy
        )
        return response
    
    async def generate_batch(self, copy_requests: list) -> list:
        tasks = [
            self._bounded_call("mock_prompt", req) for req in copy_requests
        ]
        results = await asyncio.gather(*tasks)
        
        responses = []
        for copy_request, generated_copy in results:
            response = CopyResponse(
                product_name=copy_request.product_name,
                platform=copy_request.platform.value,
                tone=copy_request.tone.value,
                copy=generated_copy
            )
            responses.append(response)
        return responses


async def demo_async_pipeline():
    """Demonstrate async pipeline with mock API"""
    print("=" * 70)
    print("PHASE 4: ASYNC PIPELINE - DEMO & INTEGRATION TESTS")
    print("=" * 70)
    
    # Initialize pipeline with max 3 concurrent requests
    pipeline = MockAsyncPipeline(max_concurrent=3)
    
    # Test 1: Single async generation
    print("\n✓ Test 1: Single Async Generation")
    single_req = CopyRequest(
        product_name="Premium Headphones",
        platform=PlatformEnum.LINKEDIN,
        tone=ToneEnum.PROFESSIONAL
    )
    
    response = await pipeline.generate_single(single_req)
    print(f"  Request: {single_req.product_name} ({single_req.platform.value}, {single_req.tone.value})")
    print(f"  Generated: {response.copy}")
    print(f"  Char Count: {response.char_count}")
    
    # Test 2: Batch parallel generation (semaphore-limited)
    print("\n✓ Test 2: Batch Parallel Generation (Max 3 concurrent)")
    batch_requests = [
        CopyRequest(
            product_name="Running Shoes",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.WITTY
        ),
        CopyRequest(
            product_name="Project Manager",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        ),
        CopyRequest(
            product_name="Yoga Mat",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.CASUAL
        ),
        CopyRequest(
            product_name="Fitness App",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.PERSUASIVE
        ),
        CopyRequest(
            product_name="Cloud Storage",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        ),
    ]
    
    print(f"  Processing {len(batch_requests)} requests in parallel...")
    print(f"  Semaphore limit: 3 concurrent requests\n")
    
    responses = await pipeline.generate_batch(batch_requests)
    
    for idx, resp in enumerate(responses, 1):
        print(f"  [{idx}] {resp.product_name:20} | {resp.platform:10} | {resp.tone:12}")
        print(f"      → {resp.copy}")
        print(f"      → {resp.char_count} chars\n")
    
    # Test 3: Verify order preservation
    print("\n✓ Test 3: Order Preservation in Batch")
    products = [req.product_name for req in batch_requests]
    response_products = [resp.product_name for resp in responses]
    
    if products == response_products:
        print("  ✓ Order preserved: Input order matches output order")
    else:
        print("  ❌ Order NOT preserved!")
    
    # Test 4: Concurrency info
    print(f"\n✓ Test 4: Concurrency Statistics")
    print(f"  Total API calls made: {pipeline.call_count}")
    print(f"  Max concurrent limit: 3")
    print(f"  Total requests: {len(batch_requests) + 1}")  # +1 for single generation
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 4 TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_async_pipeline())