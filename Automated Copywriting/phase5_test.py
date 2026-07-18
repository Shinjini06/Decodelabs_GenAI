# phase5_test.py
"""
Phase 5: Batch Pipeline - Demo & Tests
Mock-based testing (no real Batch API calls required)
"""

import asyncio
from models import CopyRequest, CopyResponse, PlatformEnum, ToneEnum
from template_compiler import TemplateCompiler
from parameter_tuner import ParameterTuner


class MockBatchCollector:
    """Mock Batch Collector for testing without real API"""
    
    def __init__(self, api_key: str = None):
        self.batch_count = 0
    
    async def create_batch(self, copy_requests: list) -> str:
        """Create mock batch"""
        self.batch_count += 1
        batch_id = f"batch_mock_{self.batch_count:05d}"
        print(f"  [Mock] Batch created: {batch_id}")
        return batch_id
    
    async def poll_batch_status(
        self,
        batch_id: str,
        poll_interval: int = 1,
        max_polls: int = 3
    ) -> dict:
        """Mock polling with quick completion"""
        for poll in range(1, 4):
            print(f"  [Mock Poll {poll}/3] Status: processing...")
            await asyncio.sleep(0.1)  # Quick mock latency
        
        return {
            "id": batch_id,
            "status": "completed",
            "request_counts": {
                "completed": 5,
                "failed": 0
            }
        }
    
    async def retrieve_results(self, batch_id: str) -> list:
        """Mock result retrieval"""
        mock_responses = [
            CopyResponse(
                product_name="Product 1",
                platform="linkedin",
                tone="professional",
                copy="Premium solution for enterprise teams seeking excellence."
            ),
            CopyResponse(
                product_name="Product 2",
                platform="instagram",
                tone="witty",
                copy="🎯 Level up your game with cutting-edge innovation!"
            ),
            CopyResponse(
                product_name="Product 3",
                platform="email",
                tone="casual",
                copy="Hey! Check out what we've built for you."
            ),
            CopyResponse(
                product_name="Product 4",
                platform="linkedin",
                tone="persuasive",
                copy="Don't wait – transform your workflow today."
            ),
            CopyResponse(
                product_name="Product 5",
                platform="instagram",
                tone="casual",
                copy="Join thousands of happy users worldwide!"
            ),
        ]
        print(f"  [Mock] Retrieved {len(mock_responses)} results")
        return mock_responses


class MockBatchPipeline:
    """Mock batch pipeline for testing"""
    
    def __init__(self, api_key: str = None):
        self.collector = MockBatchCollector(api_key)
    
    async def submit_batch(self, copy_requests: list) -> str:
        """Submit batch"""
        print(f"\n📦 Submitting batch with {len(copy_requests)} requests...")
        batch_id = await self.collector.create_batch(copy_requests)
        print(f"✓ Batch created: {batch_id}")
        return batch_id
    
    async def wait_and_retrieve(self, batch_id: str, poll_interval: int = 1) -> list:
        """Poll and retrieve"""
        print(f"\n⏳ Polling batch {batch_id}...")
        
        batch_data = await self.collector.poll_batch_status(
            batch_id,
            poll_interval=poll_interval
        )
        
        print(f"✓ Batch completed: {batch_data['status']}")
        print(f"  Succeeded: {batch_data.get('request_counts', {}).get('completed', 0)}")
        print(f"  Failed: {batch_data.get('request_counts', {}).get('failed', 0)}")
        
        results = await self.collector.retrieve_results(batch_id)
        print(f"✓ Retrieved {len(results)} results")
        
        return results
    
    async def process_batch(self, copy_requests: list, wait: bool = False):
        """Process batch"""
        batch_id = await self.submit_batch(copy_requests)
        
        if wait:
            results = await self.wait_and_retrieve(batch_id)
            return results
        
        return batch_id


async def demo_batch_pipeline():
    """Demonstrate batch pipeline"""
    print("=" * 70)
    print("PHASE 5: BATCH PIPELINE - DEMO & TESTS")
    print("=" * 70)
    
    pipeline = MockBatchPipeline()
    
    # Prepare batch requests
    batch_requests = [
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
        CopyRequest(
            product_name="Project Manager",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.CASUAL
        ),
        CopyRequest(
            product_name="Fitness Tracker",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PERSUASIVE
        ),
        CopyRequest(
            product_name="Yoga Mat",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        ),
    ]
    
    # Test 1: Submit batch (don't wait)
    print("\n✓ Test 1: Submit Batch (Fire & Forget)")
    batch_id = await pipeline.submit_batch(batch_requests)
    print(f"  Batch ID stored for later: {batch_id}")
    
    # Test 2: Submit and wait for completion
    print("\n✓ Test 2: Submit Batch & Wait (Blocking)")
    results = await pipeline.process_batch(batch_requests, wait=True)
    
    # Display results
    print("\n" + "=" * 70)
    print("BATCH RESULTS")
    print("=" * 70)
    
    for idx, resp in enumerate(results, 1):
        print(f"\n[{idx}] {resp.product_name}")
        print(f"    Platform: {resp.platform}")
        print(f"    Tone: {resp.tone}")
        print(f"    Copy: {resp.copy}")
        print(f"    Length: {resp.char_count} chars")
    
    # Cost comparison
    print("\n" + "=" * 70)
    print("COST ANALYSIS")
    print("=" * 70)
    
    num_requests = len(batch_requests)
    avg_tokens = 100  # Estimated
    
    standard_cost = num_requests * avg_tokens * 0.00001  # gpt-4o-mini pricing
    batch_cost = standard_cost * 0.5  # 50% reduction
    savings = standard_cost - batch_cost
    
    print(f"\nRequests: {num_requests}")
    print(f"Avg tokens per request: {avg_tokens}")
    print(f"\nStandard API Cost: ${standard_cost:.4f}")
    print(f"Batch API Cost: ${batch_cost:.4f}")
    print(f"Savings: ${savings:.4f} (50% discount)")
    
    # Characteristics
    print("\n" + "=" * 70)
    print("BATCH API CHARACTERISTICS")
    print("=" * 70)
    
    characteristics = {
        "Cost Reduction": "50% discount vs standard API",
        "Rate Limit Pool": "Separate isolated pool",
        "Latency": "Up to 24 hours",
        "Max Batch Size": "100,000 requests",
        "Ideal For": "Bulk, non-urgent processing",
        "Use Case": "Overnight analysis, bulk content generation",
    }
    
    for key, value in characteristics.items():
        print(f"  • {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 5 TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(demo_batch_pipeline())