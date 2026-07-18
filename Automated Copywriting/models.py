"""
Pydantic Models for Copywriting Framework
Input validation (CopyRequest) and output validation (CopyResponse)
"""

from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum
from typing import Optional


class PlatformEnum(str, Enum):
    """Supported platforms"""
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    EMAIL = "email"


class ToneEnum(str, Enum):
    """Supported tones"""
    WITTY = "witty"
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    PERSUASIVE = "persuasive"


class CopyRequest(BaseModel):
    """Input schema: what the user provides"""
    product_name: str = Field(..., min_length=1, max_length=100, description="Product name")
    platform: PlatformEnum = Field(..., description="Target platform")
    tone: ToneEnum = Field(..., description="Desired tone")
    
    @field_validator('product_name')
    @classmethod
    def product_name_clean(cls, v):
        """Sanitize product name: trim and title-case"""
        return v.strip().title()


class CopyResponse(BaseModel):
    """Output schema: generated marketing copy"""
    product_name: str
    platform: str
    tone: str
    copy: str = Field(..., min_length=10, description="Generated copy")
    char_count: Optional[int] = None
    
    @model_validator(mode='after')
    def set_char_count(self):
        """Auto-calculate character count from copy after validation"""
        if self.copy:
            self.char_count = len(self.copy)
        return self