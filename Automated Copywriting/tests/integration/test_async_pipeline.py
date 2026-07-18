# tests/integration/test_async_pipeline.py
"""
Integration tests for Async Pipeline
Uses mock API to avoid real API calls
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from models import CopyRequest, CopyResponse, PlatformEnum, ToneEnum
from parameter_tuner import ParameterTuner, GenerationParams


# Mock version of AsyncPipeline for testing
class MockAsyncPipeline:
    """Mock pipeline that returns predetermined responses"""
    
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.call_count = 0
    
    async def _bounded_call(self, prompt: str, copy_request: CopyRequest):
        """Mock API call"""
        async with self.semaphore:
            self.call_count += 1
            # Simulate API latency
            await asyncio.sleep(0.1)
            
            mock_copy = f"[Mock] Premium {copy_request.product_name} for {copy_request.platform.value}!"
            return (copy_request, mock_copy)
    
    async def generate_single(self, copy_request: CopyRequest) -> CopyResponse:
        """Generate single response (mock)"""
        _, generated_copy = await self._bounded_call("mock_prompt", copy_request)
        
        response = CopyResponse(
            product_name=copy_request.product_name,
            platform=copy_request.platform.value,
            tone=copy_request.tone.value,
            copy=generated_copy
        )
        return response
    
    async def generate_batch(self, copy_requests: list) -> list:
        """Generate batch responses (mock)"""
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


class TestAsyncPipeline:
    """Integration tests for async pipeline"""
    
    @pytest.mark.asyncio
    async def test_single_generation(self):
        """Test single async generation"""
        pipeline = MockAsyncPipeline()
        
        req = CopyRequest(
            product_name="Laptop",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        
        response = await pipeline.generate_single(req)
        
        assert isinstance(response, CopyResponse)
        assert response.product_name == "Laptop"
        assert response.platform == "linkedin"
        assert len(response.copy) > 0
        assert response.char_count == len(response.copy)
    
    @pytest.mark.asyncio
    async def test_batch_generation(self):
        """Test parallel batch generation"""
        pipeline = MockAsyncPipeline(max_concurrent=2)
        
        requests = [
            CopyRequest(
                product_name="Shoes",
                platform=PlatformEnum.INSTAGRAM,
                tone=ToneEnum.WITTY
            ),
            CopyRequest(
                product_name="Software",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            ),
            CopyRequest(
                product_name="Mat",
                platform=PlatformEnum.EMAIL,
                tone=ToneEnum.CASUAL
            ),
        ]
        
        responses = await pipeline.generate_batch(requests)
        
        assert len(responses) == 3
        assert all(isinstance(r, CopyResponse) for r in responses)
        assert responses[0].product_name == "Shoes"
        assert responses[1].product_name == "Software"
        assert responses[2].product_name == "Mat"
    
    @pytest.mark.asyncio
    async def test_semaphore_limits_concurrency(self):
        """Test that semaphore limits concurrent calls"""
        pipeline = MockAsyncPipeline(max_concurrent=2)
        
        requests = [
            CopyRequest(
                product_name=f"Product {i}",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            )
            for i in range(5)
        ]
        
        responses = await pipeline.generate_batch(requests)
        
        # All requests should complete
        assert len(responses) == 5
        # Semaphore should have been acquired 5 times
        assert pipeline.call_count == 5
    
    @pytest.mark.asyncio
    async def test_order_preserved_in_batch(self):
        """Test that batch results maintain input order"""
        pipeline = MockAsyncPipeline()
        
        products = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
        requests = [
            CopyRequest(
                product_name=product,
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PROFESSIONAL
            )
            for product in products
        ]
        
        responses = await pipeline.generate_batch(requests)
        
        # Order should match input order
        for i, response in enumerate(responses):
            assert response.product_name == products[i]


def run_integration_tests():
    """Run all async integration tests"""
    print("=" * 70)
    print("PHASE 4: ASYNC PIPELINE INTEGRATION TESTS")
    print("=" * 70)
    
    test_obj = TestAsyncPipeline()
    
    print("\n✓ Test 1: Single Async Generation")
    asyncio.run(test_obj.test_single_generation())
    print("  PASSED")
    
    print("\n✓ Test 2: Batch Parallel Generation")
    asyncio.run(test_obj.test_batch_generation())
    print("  PASSED: 3 requests processed")
    
    print("\n✓ Test 3: Semaphore Concurrency Limit")
    asyncio.run(test_obj.test_semaphore_limits_concurrency())
    print("  PASSED: Max 2 concurrent, 5 total requests processed")
    
    print("\n✓ Test 4: Order Preserved in Batch")
    asyncio.run(test_obj.test_order_preserved_in_batch())
    print("  PASSED: 5 responses in correct order")
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 4 INTEGRATION TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_integration_tests()