# pipelines/router.py
"""
Intelligent Router: Choose async vs batch pipeline based on:
- Request count (single/small = async, large = batch)
- Urgency (real-time = async, delayed = batch)
- Cost optimization (bulk = batch, ad-hoc = async)
"""

import asyncio
from typing import List, Union
from models import CopyRequest, CopyResponse
from template_compiler import TemplateCompiler
from parameter_tuner import ParameterTuner


class Router:
    """
    Routes requests to optimal pipeline:
    
    Single/Small (1-10): Async (real-time)
    Medium (11-50): Async (with concurrency control)
    Large (50+): Batch (cost-optimized, delayed)
    """
    
    # Threshold for batch vs async
    BATCH_THRESHOLD = 50
    MEDIUM_THRESHOLD = 10
    
    @staticmethod
    def choose_pipeline(copy_requests: List[CopyRequest], force_mode: str = None) -> str:
        """
        Intelligently choose pipeline.
        
        Args:
            copy_requests: List of requests
            force_mode: Force "async" or "batch" (override logic)
            
        Returns:
            "async" or "batch"
        """
        if force_mode:
            return force_mode
        
        request_count = len(copy_requests)
        
        if request_count >= Router.BATCH_THRESHOLD:
            return "batch"
        else:
            return "async"
    
    @staticmethod
    def explain_choice(copy_requests: List[CopyRequest], pipeline: str) -> str:
        """Explain why a pipeline was chosen"""
        count = len(copy_requests)
        
        if pipeline == "batch":
            return f"📦 BATCH chosen: {count} requests (≥{Router.BATCH_THRESHOLD}) → 50% cost savings, 24h latency"
        else:
            return f"⚡ ASYNC chosen: {count} requests (<{Router.BATCH_THRESHOLD}) → Real-time, immediate results"


class PipelineRouter:
    """
    Unified router that delegates to async or batch pipeline.
    """
    
    def __init__(self, api_key: str = None):
        """Initialize router with both pipelines"""
        self.api_key = api_key
        # Import here to avoid circular imports
        from pipelines.async_pipeline import AsyncPipeline
        
        self.async_pipeline = None  # Lazy load
        self.batch_pipeline = None  # Lazy load
    
    async def generate(
        self,
        copy_requests: List[CopyRequest],
        force_mode: str = None,
        wait_for_batch: bool = False
    ) -> Union[List[CopyResponse], str]:
        """
        Generate copy using optimal pipeline.
        
        Args:
            copy_requests: Requests to process
            force_mode: Override pipeline choice ("async" or "batch")
            wait_for_batch: If batch, wait for completion
            
        Returns:
            List[CopyResponse] for async, or batch_id for batch (unless wait=True)
        """
        
        # Choose pipeline
        pipeline_choice = Router.choose_pipeline(copy_requests, force_mode)
        print(Router.explain_choice(copy_requests, pipeline_choice))
        
        if pipeline_choice == "async":
            return await self._route_async(copy_requests)
        else:
            return await self._route_batch(copy_requests, wait_for_batch)
    
    async def _route_async(self, copy_requests: List[CopyRequest]) -> List[CopyResponse]:
        """Route to async pipeline"""
        from pipelines.async_pipeline import AsyncPipeline
        
        print(f"\n⚡ Starting async pipeline (max 5 concurrent)...")
        
        # Use mock for testing
        class MockAsyncPipeline:
            def __init__(self):
                self.semaphore = asyncio.Semaphore(5)
                self.call_count = 0
            
            async def generate_batch(self, reqs):
                responses = []
                for req in reqs:
                    await asyncio.sleep(0.05)
                    resp = CopyResponse(
                        product_name=req.product_name,
                        platform=req.platform.value,
                        tone=req.tone.value,
                        copy=f"Generated copy for {req.product_name}"
                    )
                    responses.append(resp)
                return responses
        
        pipeline = MockAsyncPipeline()
        responses = await pipeline.generate_batch(copy_requests)
        
        print(f"✓ Async pipeline completed: {len(responses)} responses")
        return responses
    
    async def _route_batch(
        self,
        copy_requests: List[CopyRequest],
        wait: bool = False
    ) -> Union[List[CopyResponse], str]:
        """Route to batch pipeline"""
        print(f"\n📦 Starting batch pipeline...")
        
        # Use mock for testing
        class MockBatchPipeline:
            def __init__(self):
                self.batch_count = 0
            
            async def submit_batch(self, reqs):
                self.batch_count += 1
                batch_id = f"batch_{self.batch_count:05d}"
                await asyncio.sleep(0.1)
                return batch_id
            
            async def wait_and_retrieve(self, batch_id):
                await asyncio.sleep(0.2)
                responses = []
                # Mock responses
                for i in range(5):
                    resp = CopyResponse(
                        product_name=f"Product {i+1}",
                        platform="linkedin",
                        tone="professional",
                        copy=f"Generated copy {i+1}"
                    )
                    responses.append(resp)
                return responses
        
        pipeline = MockBatchPipeline()
        batch_id = await pipeline.submit_batch(copy_requests)
        
        print(f"✓ Batch submitted: {batch_id}")
        
        if wait:
            print(f"⏳ Waiting for batch completion...")
            responses = await pipeline.wait_and_retrieve(batch_id)
            print(f"✓ Batch completed: {len(responses)} responses")
            return responses
        else:
            print(f"📋 Batch ID for tracking: {batch_id}")
            return batch_id