# phase3_test.py
"""
Phase 3: Parameter Tuner - Demo & Tests
"""

from models import CopyRequest, PlatformEnum, ToneEnum
from parameter_tuner import ParameterTuner


def demo_parameter_tuning():
    """Demonstrate parameter tuning for different scenarios"""
    print("=" * 70)
    print("PHASE 3: PARAMETER TUNER - DEMO & TESTS")
    print("=" * 70)
    
    scenarios = [
        {
            "name": "High Creativity: Witty Social Media",
            "req": CopyRequest(
                product_name="Coffee Mug",
                platform=PlatformEnum.INSTAGRAM,
                tone=ToneEnum.WITTY
            ),
            "user_temp": None,
            "user_tokens": None,
        },
        {
            "name": "Low Consistency: Professional Email",
            "req": CopyRequest(
                product_name="Project Manager",
                platform=PlatformEnum.EMAIL,
                tone=ToneEnum.PROFESSIONAL
            ),
            "user_temp": None,
            "user_tokens": None,
        },
        {
            "name": "Balanced: Casual LinkedIn",
            "req": CopyRequest(
                product_name="Learning Platform",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.CASUAL
            ),
            "user_temp": None,
            "user_tokens": None,
        },
        {
            "name": "High Engagement: Persuasive LinkedIn (with override)",
            "req": CopyRequest(
                product_name="Software Subscription",
                platform=PlatformEnum.LINKEDIN,
                tone=ToneEnum.PERSUASIVE
            ),
            "user_temp": 0.95,
            "user_tokens": 200,
        },
    ]
    
    for idx, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*70}")
        print(f"Scenario {idx}: {scenario['name']}")
        print(f"{'='*70}")
        
        req = scenario["req"]
        params = ParameterTuner.tune(
            req,
            user_temperature=scenario["user_temp"],
            user_max_tokens=scenario["user_tokens"]
        )
        
        print(f"\nInput:")
        print(f"  Product: {req.product_name}")
        print(f"  Platform: {req.platform.value.upper()}")
        print(f"  Tone: {req.tone.value.upper()}")
        
        print(f"\nTuned Parameters:")
        print(f"  Temperature: {params.temperature}")
        print(f"  Top_P: {params.top_p}")
        print(f"  Max Tokens: {params.max_tokens}")
        
        print(f"\n{ParameterTuner.explain_parameters(params)}")
    
    print("\n" + "=" * 70)
    print("✓ PHASE 3 PARAMETER TUNING COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    demo_parameter_tuning()