"""
CLI Parser using argparse
Captures product_name, platform, tone, temperature, and max_tokens
"""

import argparse
from models import PlatformEnum, ToneEnum


def parse_arguments():
    """Parse CLI arguments using argparse"""
    parser = argparse.ArgumentParser(
        description="Automated Copywriting & Tone Transformer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --product "Running Shoe" --platform linkedin --tone witty
  python run.py --product "Yoga Mat" --platform instagram --tone casual --temperature 0.8
        """
    )
    
    parser.add_argument(
        '--product', '-p',
        type=str,
        required=True,
        help='Product name (e.g., "Running Shoe")',
        metavar='PRODUCT'
    )
    
    parser.add_argument(
        '--platform',
        type=str,
        choices=[p.value for p in PlatformEnum],
        required=True,
        help='Target platform: linkedin | instagram | email',
        metavar='PLATFORM'
    )
    
    parser.add_argument(
        '--tone', '-t',
        type=str,
        choices=[t.value for t in ToneEnum],
        required=True,
        help='Desired tone: witty | professional | casual | persuasive',
        metavar='TONE'
    )
    
    parser.add_argument(
        '--temperature',
        type=float,
        default=0.5,
        help='LLM temperature (0.0-1.0, default: 0.5) - Lower = consistent, Higher = creative',
        metavar='TEMP'
    )
    
    parser.add_argument(
        '--max-tokens',
        type=int,
        default=150,
        help='Max tokens for response (default: 150)',
        metavar='TOKENS'
    )
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    print(f"Product: {args.product}")
    print(f"Platform: {args.platform}")
    print(f"Tone: {args.tone}")
    print(f"Temperature: {args.temperature}")
    print(f"Max Tokens: {args.max_tokens}")