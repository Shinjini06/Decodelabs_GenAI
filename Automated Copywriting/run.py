# run.py
"""
Main entry point: Unified CLI for copy generation
Integrates all phases: Models → Templates → Parameters → Router → Pipeline
"""

import asyncio
import sys
from cli_parser import parse_arguments
from models import CopyRequest
from pipelines.router import PipelineRouter, Router


async def main():
    """Main entry point"""
    
    # Parse CLI arguments
    args = parse_arguments()
    
    print("=" * 70)
    print("AUTOMATED COPYWRITING & TONE TRANSFORMER")
    print("=" * 70)
    
    # Create request
    try:
        copy_request = CopyRequest(
            product_name=args.product,
            platform=args.platform,
            tone=args.tone
        )
        print(f"\n✓ Input validated")
        print(f"  Product: {copy_request.product_name}")
        print(f"  Platform: {copy_request.platform.value}")
        print(f"  Tone: {copy_request.tone.value}")
    
    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        sys.exit(1)
    
    # Route and generate
    try:
        router = PipelineRouter()
        response = await router.generate([copy_request])
        
        if isinstance(response, list):
            result = response[0]
            print(f"\n✓ Copy generated:")
            print(f"  {result.copy}")
            print(f"\n  Length: {result.char_count} characters")
        else:
            print(f"\n✓ Batch submitted: {response}")
    
    except Exception as e:
        print(f"\n❌ Generation Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())