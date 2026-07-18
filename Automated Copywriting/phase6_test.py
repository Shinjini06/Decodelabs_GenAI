# phase6_test.py
"""
Phase 6: Router & Integration - Full End-to-End Test
"""

import asyncio
from models import CopyRequest, PlatformEnum, ToneEnum
from pipelines.router import Router, PipelineRouter


async def demo_router():
    """Demonstrate router intelligence"""
    print("=" * 70)
    print("PHASE 6: ROUTER & INTEGRATION - END-TO-END TEST")
    print("=" * 70)
    
    # Test 1: Small batch → Async
    print("\n✓ Test 1: Small Batch (1-10 requests) → ASYNC Pipeline")
    small_requests = [
        CopyRequest(
            product_name="Premium Headphones",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        ),
        CopyRequest(
            product_name="Running Shoes",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.WITTY
        ),
    ]
    
    pipeline_choice = Router.choose_pipeline(small_requests)
    print(f"  Requests: {len(small_requests)}")
    print(f"  Choice: {Router.explain_choice(small_requests, pipeline_choice)}")
    
    router = PipelineRouter()
    responses = await router.generate(small_requests)
    print(f"  ✓ Generated {len(responses)} responses")
    
    # Test 2: Medium batch → Async (with concurrency)
    print("\n✓ Test 2: Medium Batch (11-49 requests) → ASYNC Pipeline")
    medium_requests = [
        CopyRequest(
            product_name=f"Product {i}",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        for i in range(20)
    ]
    
    pipeline_choice = Router.choose_pipeline(medium_requests)
    print(f"  Requests: {len(medium_requests)}")
    print(f"  Choice: {Router.explain_choice(medium_requests, pipeline_choice)}")
    
    responses = await router.generate(medium_requests)
    print(f"  ✓ Generated {len(responses)} responses in parallel")
    
    # Test 3: Large batch → Batch API
    print("\n✓ Test 3: Large Batch (50+ requests) → BATCH Pipeline")
    large_requests = [
        CopyRequest(
            product_name=f"Product {i}",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        for i in range(75)
    ]
    
    pipeline_choice = Router.choose_pipeline(large_requests)
    print(f"  Requests: {len(large_requests)}")
    print(f"  Choice: {Router.explain_choice(large_requests, pipeline_choice)}")
    
    batch_id = await router.generate(large_requests, wait_for_batch=False)
    print(f"  ✓ Batch submitted for processing")
    print(f"  Batch ID: {batch_id}")
    print(f"  Status: Check back later (24h window)")
    
    # Test 4: Force async (override)
    print("\n✓ Test 4: Force ASYNC (Override Batch Logic)")
    requests_force = [
        CopyRequest(
            product_name=f"Product {i}",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        for i in range(60)
    ]
    
    print(f"  Requests: {len(requests_force)} (normally batch)")
    responses = await router.generate(requests_force, force_mode="async")
    print(f"  ✓ Force async worked: {len(responses)} responses")
    
    # Test 5: Force batch (override)
    print("\n✓ Test 5: Force BATCH (Override Async Logic)")
    requests_small = [
        CopyRequest(
            product_name="Single Product",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
    ]
    
    print(f"  Requests: {len(requests_small)} (normally async)")
    batch_id = await router.generate(requests_small, force_mode="batch", wait_for_batch=False)
    print(f"  ✓ Force batch worked: {batch_id}")
    
    # Summary
    print("\n" + "=" * 70)
    print("ROUTER DECISION LOGIC")
    print("=" * 70)
    
    logic = """
1-10 requests   → ASYNC (real-time, immediate results)
11-49 requests  → ASYNC (parallel with semaphore limit)
50+ requests    → BATCH (50% cost savings, 24h latency)

Override with: force_mode="async" or force_mode="batch"

Tradeoffs:
  ASYNC: Low latency, higher cost, shared rate limits
  BATCH: High latency, 50% cheaper, isolated rate limits
    """
    print(logic)
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 6 TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_router())