# test_template_compiler.py
"""
Unit tests for Template Compiler
Test f-string compilation, variable injection, and constraint mapping
"""

import pytest
from models import CopyRequest, PlatformEnum, ToneEnum
from template_compiler import TemplateCompiler


class TestTemplateCompiler:
    """Test dynamic template compilation"""
    
    def test_compile_witty_linkedin(self):
        """Test witty tone compilation for LinkedIn"""
        req = CopyRequest(
            product_name="Running Shoe",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        
        compiled = TemplateCompiler.compile(req)
        
        # Check that variables are injected
        assert "Running Shoe" in compiled
        assert "LINKEDIN" in compiled
        assert "300 characters" in compiled
        assert "clever" in compiled.lower()
    
    def test_compile_professional_email(self):
        """Test professional tone compilation for Email"""
        req = CopyRequest(
            product_name="Yoga Mat",
            platform=PlatformEnum.EMAIL,
            tone=ToneEnum.PROFESSIONAL
        )
        
        compiled = TemplateCompiler.compile(req)
        
        assert "Yoga Mat" in compiled
        assert "EMAIL" in compiled
        assert "160 characters" in compiled
        assert "professional" in compiled.lower()
    
    def test_compile_casual_instagram(self):
        """Test casual tone compilation for Instagram"""
        req = CopyRequest(
            product_name="Coffee Mug",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        )
        
        compiled = TemplateCompiler.compile(req)
        
        assert "Coffee Mug" in compiled
        assert "INSTAGRAM" in compiled
        assert "280 characters" in compiled
        assert "friendly" in compiled.lower()
    
    def test_compile_persuasive_linkedin(self):
        """Test persuasive tone compilation for LinkedIn"""
        req = CopyRequest(
            product_name="Project Management Tool",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.PERSUASIVE
        )
        
        compiled = TemplateCompiler.compile(req)
        
        assert "Project Management Tool" in compiled
        assert "LINKEDIN" in compiled
        assert "persuasive" in compiled.lower()
        assert "action" in compiled.lower() or "call-to-action" in compiled.lower()
    
    def test_all_platforms_have_constraints(self):
        """Test that all platforms have defined constraints"""
        for platform in PlatformEnum:
            constraints = TemplateCompiler.get_platform_constraints(platform)
            assert constraints is not None
            assert len(constraints) > 0
            print(f"  ✓ {platform.value}: {constraints}")
    
    def test_all_tones_have_templates(self):
        """Test that all tones have master templates"""
        for tone in ToneEnum:
            req = CopyRequest(
                product_name="Test Product",
                platform=PlatformEnum.LINKEDIN,
                tone=tone
            )
            compiled = TemplateCompiler.compile(req)
            assert "Test Product" in compiled
            assert len(compiled) > 0
            print(f"  ✓ {tone.value}: {len(compiled)} chars")
    
    def test_special_characters_in_product_name(self):
        """Test product names with special characters"""
        req = CopyRequest(
            product_name="C++ Learning Kit",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        )
        
        compiled = TemplateCompiler.compile(req)
        assert "C++ Learning Kit" in compiled
    
    def test_constraint_character_limits_are_realistic(self):
        """Test that platform constraints mention realistic limits"""
        linkedin_constraints = TemplateCompiler.get_platform_constraints(PlatformEnum.LINKEDIN)
        instagram_constraints = TemplateCompiler.get_platform_constraints(PlatformEnum.INSTAGRAM)
        email_constraints = TemplateCompiler.get_platform_constraints(PlatformEnum.EMAIL)
        
        # All should mention character limits
        assert "character" in linkedin_constraints.lower()
        assert "character" in instagram_constraints.lower()
        assert "character" in email_constraints.lower()


def run_all_tests():
    """Run all template compiler tests"""
    print("=" * 70)
    print("PHASE 2: TEMPLATE COMPILER TESTS")
    print("=" * 70)
    
    test_obj = TestTemplateCompiler()
    
    print("\n✓ Test 1: Witty + LinkedIn")
    test_obj.test_compile_witty_linkedin()
    print("  PASSED")
    
    print("\n✓ Test 2: Professional + Email")
    test_obj.test_compile_professional_email()
    print("  PASSED")
    
    print("\n✓ Test 3: Casual + Instagram")
    test_obj.test_compile_casual_instagram()
    print("  PASSED")
    
    print("\n✓ Test 4: Persuasive + LinkedIn")
    test_obj.test_compile_persuasive_linkedin()
    print("  PASSED")
    
    print("\n✓ Test 5: All Platforms Have Constraints")
    test_obj.test_all_platforms_have_constraints()
    
    print("\n✓ Test 6: All Tones Have Templates")
    test_obj.test_all_tones_have_templates()
    
    print("\n✓ Test 7: Special Characters in Product Name")
    test_obj.test_special_characters_in_product_name()
    print("  PASSED")
    
    print("\n✓ Test 8: Constraint Character Limits")
    test_obj.test_constraint_character_limits_are_realistic()
    print("  PASSED")
    
    print("\n" + "=" * 70)
    print("✓ ALL PHASE 2 TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()