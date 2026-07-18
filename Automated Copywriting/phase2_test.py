# phase2_test.py
"""
Phase 2: Template Compiler - Test & Demo
"""

from models import CopyRequest, PlatformEnum, ToneEnum
from template_compiler import TemplateCompiler


def demo_templates():
    """Demonstrate template compilation"""
    print("=" * 70)
    print("PHASE 2: TEMPLATE COMPILER - DEMO & TESTS")
    print("=" * 70)
    
    test_cases = [
        (
            CopyRequest(product_name="Running Shoe", platform=PlatformEnum.LINKEDIN, tone=ToneEnum.WITTY),
            "Running Shoe + LinkedIn + Witty"
        ),
        (
            CopyRequest(product_name="Yoga Mat", platform=PlatformEnum.INSTAGRAM, tone=ToneEnum.CASUAL),
            "Yoga Mat + Instagram + Casual"
        ),
        (
            CopyRequest(product_name="Project Manager", platform=PlatformEnum.EMAIL, tone=ToneEnum.PROFESSIONAL),
            "Project Manager + Email + Professional"
        ),
        (
            CopyRequest(product_name="Fitness Tracker", platform=PlatformEnum.LINKEDIN, tone=ToneEnum.PERSUASIVE),
            "Fitness Tracker + LinkedIn + Persuasive"
        ),
    ]
    
    for idx, (copy_req, description) in enumerate(test_cases, 1):
        print(f"\n{'='*70}")
        print(f"Test Case {idx}: {description}")
        print(f"{'='*70}")
        
        compiled = TemplateCompiler.compile(copy_req)
        
        print(f"\nInput:")
        print(f"  Product: {copy_req.product_name}")
        print(f"  Platform: {copy_req.platform.value}")
        print(f"  Tone: {copy_req.tone.value}")
        
        print(f"\nCompiled Template ({len(compiled)} chars):")
        print(f"\n{compiled}\n")
    
    print("\n" + "=" * 70)
    print("✓ PHASE 2 TEMPLATE COMPILATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_templates()