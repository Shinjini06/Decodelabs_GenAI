# test_parameter_tuner.py
"""
Unit tests for Parameter Tuner
Test temperature profiles, token limits, and parameter validation
"""

import pytest
from models import CopyRequest, PlatformEnum, ToneEnum
from parameter_tuner import ParameterTuner, GenerationParams


class TestParameterTuner:
    """Test parameter tuning logic"""
    
    def test_witty_high_temperature(self):
        """Witty tone should have high temperature for creativity"""
        req = CopyRequest(
            product_name="Shoes",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        params = ParameterTuner.tune(req)
        
        assert params.temperature >= 0.7, "Witty should have high temperature"
        assert params.temperature == 0.8
    
    def test_professional_low_temperature(self):
        """Professional tone should have low temperature for consistency"""
        req = CopyRequest(
            product_name="Software",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.PROFESSIONAL
        )
        params = ParameterTuner.tune(req)
        
        assert params.temperature <= 0.5, "Professional should have low temperature"
        assert params.temperature == 0.3
    
    def test_casual_medium_temperature(self):
        """Casual tone should have medium temperature"""
        req = CopyRequest(
            product_name="Coffee",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        )
        params = ParameterTuner.tune(req)
        
        assert 0.5 <= params.temperature <= 0.7
        assert params.temperature == 0.6
    
    def test_persuasive_high_temperature(self):
        """Persuasive tone should have high temperature for engagement"""
        req = CopyRequest(
            product_name="Course",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PERSUASIVE
        )
        params = ParameterTuner.tune(req)
        
        assert params.temperature >= 0.7
        assert params.temperature == 0.7
    
    def test_email_low_token_count(self):
        """Email platform should have low max_tokens (tight subject line)"""
        req = CopyRequest(
            product_name="Newsletter",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.PROFESSIONAL
        )
        params = ParameterTuner.tune(req)
        
        assert params.max_tokens <= 100
        assert params.max_tokens == 50
    
    def test_instagram_medium_token_count(self):
        """Instagram should have medium max_tokens"""
        req = CopyRequest(
            product_name="Post",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        )
        params = ParameterTuner.tune(req)
        
        assert 80 <= params.max_tokens <= 120
        assert params.max_tokens == 100
    
    def test_linkedin_high_token_count(self):
        """LinkedIn should have higher max_tokens"""
        req = CopyRequest(
            product_name="Article",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        params = ParameterTuner.tune(req)
        
        assert params.max_tokens >= 120
        assert params.max_tokens == 150
    
    def test_user_temperature_override(self):
        """User-provided temperature should override defaults"""
        req = CopyRequest(
            product_name="Shoes",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        
        # Default witty = 0.8, override to 0.9
        params = ParameterTuner.tune(req, user_temperature=0.9)
        assert params.temperature == 0.9
    
    def test_user_max_tokens_override(self):
        """User-provided max_tokens should override defaults"""
        req = CopyRequest(
            product_name="Product",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.PROFESSIONAL
        )
        
        # Default email = 50, override to 75
        params = ParameterTuner.tune(req, user_max_tokens=75)
        assert params.max_tokens == 75
    
    def test_user_top_p_override(self):
        """User-provided top_p should override defaults"""
        req = CopyRequest(
            product_name="Item",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.CASUAL
        )
        
        params = ParameterTuner.tune(req, user_top_p=0.95)
        assert params.top_p == 0.95
    
    def test_multiple_overrides(self):
        """User can override multiple parameters at once"""
        req = CopyRequest(
            product_name="Thing",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.WITTY
        )
        
        params = ParameterTuner.tune(
            req,
            user_temperature=0.5,
            user_max_tokens=200,
            user_top_p=0.9
        )
        
        assert params.temperature == 0.5
        assert params.max_tokens == 200
        assert params.top_p == 0.9
    
    def test_default_top_p_is_one(self):
        """Default top_p should be 1.0"""
        req = CopyRequest(
            product_name="Product",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PROFESSIONAL
        )
        
        params = ParameterTuner.tune(req)
        assert params.top_p == 1.0
    
    def test_generation_params_validation_temperature_low(self):
        """GenerationParams should reject temperature < 0.0"""
        with pytest.raises(ValueError):
            GenerationParams(
                temperature=-0.1,
                top_p=1.0,
                max_tokens=100
            )
    
    def test_generation_params_validation_temperature_high(self):
        """GenerationParams should reject temperature > 2.0"""
        with pytest.raises(ValueError):
            GenerationParams(
                temperature=2.5,
                top_p=1.0,
                max_tokens=100
            )
    
    def test_generation_params_validation_top_p_low(self):
        """GenerationParams should reject top_p < 0.0"""
        with pytest.raises(ValueError):
            GenerationParams(
                temperature=0.5,
                top_p=-0.1,
                max_tokens=100
            )
    
    def test_generation_params_validation_top_p_high(self):
        """GenerationParams should reject top_p > 1.0"""
        with pytest.raises(ValueError):
            GenerationParams(
                temperature=0.5,
                top_p=1.1,
                max_tokens=100
            )
    
    def test_generation_params_validation_tokens_too_low(self):
        """GenerationParams should reject max_tokens < 10"""
        with pytest.raises(ValueError):
            GenerationParams(
                temperature=0.5,
                top_p=1.0,
                max_tokens=5
            )
    
    def test_generation_params_validation_tokens_too_high(self):
        """GenerationParams should reject max_tokens > 4096"""
        with pytest.raises(ValueError):
            GenerationParams(
                temperature=0.5,
                top_p=1.0,
                max_tokens=5000
            )
    
    def test_generation_params_valid_range(self):
        """GenerationParams should accept valid ranges"""
        params = GenerationParams(
            temperature=1.5,
            top_p=0.95,
            max_tokens=2000
        )
        assert params.temperature == 1.5
        assert params.top_p == 0.95
        assert params.max_tokens == 2000


def run_all_tests():
    """Run all parameter tuner tests"""
    print("=" * 70)
    print("PHASE 3: PARAMETER TUNER TESTS")
    print("=" * 70)
    
    test_obj = TestParameterTuner()
    
    print("\n✓ Test 1: Witty → High Temperature")
    test_obj.test_witty_high_temperature()
    print("  PASSED: 0.8 temperature")
    
    print("\n✓ Test 2: Professional → Low Temperature")
    test_obj.test_professional_low_temperature()
    print("  PASSED: 0.3 temperature")
    
    print("\n✓ Test 3: Casual → Medium Temperature")
    test_obj.test_casual_medium_temperature()
    print("  PASSED: 0.6 temperature")
    
    print("\n✓ Test 4: Persuasive → High Temperature")
    test_obj.test_persuasive_high_temperature()
    print("  PASSED: 0.7 temperature")
    
    print("\n✓ Test 5: Email → Low Token Count")
    test_obj.test_email_low_token_count()
    print("  PASSED: 50 tokens")
    
    print("\n✓ Test 6: Instagram → Medium Token Count")
    test_obj.test_instagram_medium_token_count()
    print("  PASSED: 100 tokens")
    
    print("\n✓ Test 7: LinkedIn → High Token Count")
    test_obj.test_linkedin_high_token_count()
    print("  PASSED: 150 tokens")
    
    print("\n✓ Test 8: User Temperature Override")
    test_obj.test_user_temperature_override()
    print("  PASSED: Override works")
    
    print("\n✓ Test 9: User Max Tokens Override")
    test_obj.test_user_max_tokens_override()
    print("  PASSED: Override works")
    
    print("\n✓ Test 10: User Top_P Override")
    test_obj.test_user_top_p_override()
    print("  PASSED: Override works")
    
    print("\n✓ Test 11: Multiple Overrides")
    test_obj.test_multiple_overrides()
    print("  PASSED: All overrides applied")
    
    print("\n✓ Test 12: Default Top_P = 1.0")
    test_obj.test_default_top_p_is_one()
    print("  PASSED")
    
    print("\n✓ Test 13-18: Parameter Validation")
    test_obj.test_generation_params_validation_temperature_low()
    print("  ✓ Rejects temp < 0.0")
    test_obj.test_generation_params_validation_temperature_high()
    print("  ✓ Rejects temp > 2.0")
    test_obj.test_generation_params_validation_top_p_low()
    print("  ✓ Rejects top_p < 0.0")
    test_obj.test_generation_params_validation_top_p_high()
    print("  ✓ Rejects top_p > 1.0")
    test_obj.test_generation_params_validation_tokens_too_low()
    print("  ✓ Rejects tokens < 10")
    test_obj.test_generation_params_validation_tokens_too_high()
    print("  ✓ Rejects tokens > 4096")
    
    print("\n✓ Test 19: Valid Parameter Range")
    test_obj.test_generation_params_valid_range()
    print("  PASSED: Valid range accepted")
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 3 TESTS PASSED (19 tests)")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()