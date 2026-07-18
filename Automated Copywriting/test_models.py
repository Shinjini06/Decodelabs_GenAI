# test_models.py
import pytest
from models import CopyRequest, CopyResponse, PlatformEnum, ToneEnum

class TestCopyRequest:
    """Test input validation"""
    
    def test_valid_request(self):
        """Test valid input"""
        req = CopyRequest(
            product_name="Running Shoe",
            platform=PlatformEnum.LINKEDIN,
            tone=ToneEnum.WITTY
        )
        assert req.product_name == "Running Shoe"
        assert req.platform == PlatformEnum.LINKEDIN
    
    def test_product_name_cleanup(self):
        """Test product name is cleaned and titlecased"""
        req = CopyRequest(
            product_name="  running shoe  ",
            platform=PlatformEnum.INSTAGRAM,
            tone=ToneEnum.CASUAL
        )
        assert req.product_name == "Running Shoe"
    
    def test_product_name_too_short(self):
        """Test empty product name fails"""
        with pytest.raises(ValueError):
            CopyRequest(
                product_name="",
                platform=PlatformEnum.EMAIL,
                tone=ToneEnum.PROFESSIONAL
            )
    
    def test_invalid_platform(self):
        """Test invalid platform rejected"""
        with pytest.raises(ValueError):
            CopyRequest(
                product_name="Shoes",
                platform="twitter",  # Not allowed
                tone=ToneEnum.WITTY
            )
    
    def test_invalid_tone(self):
        """Test invalid tone rejected"""
        with pytest.raises(ValueError):
            CopyRequest(
                product_name="Shoes",
                platform=PlatformEnum.LINKEDIN,
                tone="sarcastic"  # Not allowed
            )

class TestCopyResponse:
    """Test output validation"""
    
    def test_valid_response(self):
        """Test valid output"""
        resp = CopyResponse(
            product_name="Running Shoe",
            platform="linkedin",
            tone="witty",
            copy="Elevate your stride with our premium running shoes!"
        )
        assert resp.char_count == len(resp.copy)
    
    def test_copy_too_short(self):
        """Test copy minimum length"""
        with pytest.raises(ValueError):
            CopyResponse(
                product_name="Shoes",
                platform="instagram",
                tone="casual",
                copy="Too short"  # < 10 chars fails
            )
    
    def test_auto_char_count(self):
        """Test character count auto-calculated"""
        resp = CopyResponse(
            product_name="Yoga Mat",
            platform="email",
            tone="professional",
            copy="Transform your yoga practice with our eco-friendly mat."
        )
        assert resp.char_count == 55