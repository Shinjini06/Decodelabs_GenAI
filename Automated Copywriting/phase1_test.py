"""
Phase 1: Pydantic Models + CLI Test
Unit tests for input/output validation
"""

from models import CopyRequest, CopyResponse, PlatformEnum, ToneEnum


def test_models():
    """Manually test the models"""
    print("=" * 70)
    print("PHASE 1: PYDANTIC MODELS + CLI TEST")
    print("=" * 70)
    
    # Test 1: Valid Input
    print("\n✓ Test 1: Valid CopyRequest")
    req = CopyRequest(
        product_name="  running shoe  ",
        platform=PlatformEnum.LINKEDIN,
        tone=ToneEnum.WITTY
    )
    print(f"  Product: {req.product_name}")
    print(f"  Platform: {req.platform.value}")
    print(f"  Tone: {req.tone.value}")
    assert req.product_name == "Running Shoe", "Product name not cleaned"
    print("  ✓ PASSED: Product name cleaned to 'Running Shoe'")
    
    # Test 2: Valid Output
    print("\n✓ Test 2: Valid CopyResponse")
    resp = CopyResponse(
        product_name="Running Shoe",
        platform="linkedin",
        tone="witty",
        copy="Elevate your running game with our premium performance shoes designed for champions!"
    )
    print(f"  Copy: {resp.copy}")
    print(f"  Character Count: {resp.char_count}")
    assert resp.char_count == len(resp.copy), "Char count mismatch"
    print("  ✓ PASSED: Character count auto-calculated correctly")
    
    # Test 3: Invalid Product Name (empty)
    print("\n✓ Test 3: Empty Product Name (should FAIL)")
    try:
        CopyRequest(
            product_name="",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        )
        print("  ❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"  ✓ PASSED: Correctly rejected")
    
    # Test 4: Invalid Platform
    print("\n✓ Test 4: Invalid Platform (should FAIL)")
    try:
        CopyRequest(
            product_name="Shoes",
            platform="twitter",
            tone=ToneEnum.WITTY
        )
        print("  ❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"  ✓ PASSED: Correctly rejected invalid platform")
    
    # Test 5: Invalid Tone
    print("\n✓ Test 5: Invalid Tone (should FAIL)")
    try:
        CopyRequest(
            product_name="Shoes",
            platform=PlatformEnum.INSTAGRAM,
            tone="sarcastic"
        )
        print("  ❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"  ✓ PASSED: Correctly rejected invalid tone")
    
    # Test 6: Copy too short
    print("\n✓ Test 6: Copy Too Short (should FAIL)")
    try:
        CopyResponse(
            product_name="Shoes",
            platform="instagram",
            tone="casual",
            copy="Brief"
        )
        print("  ❌ FAILED: Should have raised ValueError")
        return False
    except ValueError as e:
        print(f"  ✓ PASSED: Correctly rejected short copy")
    
    # Test 7: All platforms
    print("\n✓ Test 7: All Platforms")
    for platform in [PlatformEnum.LINKEDIN, PlatformEnum.INSTAGRAM, PlatformEnum.EMAIL]:
        req = CopyRequest(
            product_name="Test Product",
            platform=platform,
            tone=ToneEnum.PROFESSIONAL
        )
        print(f"  ✓ {platform.value.upper()}")
    
    # Test 8: All tones
    print("\n✓ Test 8: All Tones")
    for tone in [ToneEnum.WITTY, ToneEnum.PROFESSIONAL, ToneEnum.CASUAL, ToneEnum.PERSUASIVE]:
        req = CopyRequest(
            product_name="Test Product",
            platform=PlatformEnum.LINKEDIN,
            tone=tone
        )
        print(f"  ✓ {tone.value.upper()}")
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 1 TESTS PASSED")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_models()
    exit(0 if success else 1)