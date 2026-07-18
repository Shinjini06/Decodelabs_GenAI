# pipelines/batch_pipeline.py
"""
Batch Pipeline for bulk processing via OpenAI Batch API
50% cost reduction, 24-hour latency window, separate rate-limit pool
"""

import asyncio
from typing import List
from models import CopyRequest, CopyResponse
from clients.batch_collector import BatchCollector


class BatchPipeline:
    """
    Bulk processing pipeline using OpenAI Batch API.
    
    Features:
    - 50% cost reduction vs real-time API
    - Separate rate-limit pool (doesn't interfere with live requests)
    - 24-hour processing window
    - Structured output validation with Pydantic
    """
    
    def __init__(self, api_key: str = None):
        """Initialize batch pipeline"""
        self.collector = BatchCollector(api_key)
    
    async def submit_batch(self, copy_requests: List[CopyRequest]) -> str:
        """
        Submit batch job.
        
        Args:
            copy_requests: List of CopyRequest objects
            
        Returns:
            Batch job ID for status tracking
        """
        print(f"\n📦 Submitting batch with {len(copy_requests)} requests...")
        
        batch_id = await self.collector.create_batch(copy_requests)
        
        print(f"✓ Batch created: {batch_id}")
        return batch_id
    
    async def wait_and_retrieve(
        self,
        batch_id: str,
        poll_interval: int = 30
    ) -> List[CopyResponse]:
        """
        Poll batch status and retrieve results when complete.
        
        Args:
            batch_id: Batch job ID
            poll_interval: Seconds between status checks
            
        Returns:
            List of CopyResponse objects
        """
        print(f"\n⏳ Polling batch {batch_id}...")
        
        batch_data = await self.collector.poll_batch_status(
            batch_id,
            poll_interval=poll_interval
        )
        
        print(f"✓ Batch completed: {batch_data['status']}")
        print(f"  Succeeded: {batch_data.get('request_counts', {}).get('completed', 0)}")
        print(f"  Failed: {batch_data.get('request_counts', {}).get('failed', 0)}")
        
        # Retrieve results
        results = await self.collector.retrieve_results(batch_id)
        
        print(f"✓ Retrieved {len(results)} results")
        
        return results
    
    async def process_batch(
        self,
        copy_requests: List[CopyRequest],
        wait: bool = False,
        poll_interval: int = 30
    ) -> str:
        """
        Submit batch and optionally wait for completion.
        
        Args:
            copy_requests: Requests to process
            wait: Whether to poll and wait for completion
            poll_interval: Polling interval in seconds
            
        Returns:
            Batch ID (for future tracking)
        """
        batch_id = await self.submit_batch(copy_requests)
        
        if wait:
            await self.wait_and_retrieve(batch_id, poll_interval)
        
        return batch_id