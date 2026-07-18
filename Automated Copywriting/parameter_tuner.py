# parameter_tuner.py
"""
Parameter Tuner for LLM Generation Control
Adjusts Temperature, Top_P, and max_tokens based on platform/tone
"""

from models import CopyRequest, ToneEnum, PlatformEnum
from dataclasses import dataclass


@dataclass
class GenerationParams:
    """Validated generation parameters for OpenAI API"""
    temperature: float          # 0.0-2.0 (usually 0.0-1.0)
    top_p: float               # 0.0-1.0 (nucleus sampling)
    max_tokens: int            # Completion tokens limit
    
    def __post_init__(self):
        """Validate parameter ranges"""
        if not (0.0 <= self.temperature <= 2.0):
            raise ValueError(f"Temperature must be 0.0-2.0, got {self.temperature}")
        if not (0.0 <= self.top_p <= 1.0):
            raise ValueError(f"Top_P must be 0.0-1.0, got {self.top_p}")
        if not (10 <= self.max_tokens <= 4096):
            raise ValueError(f"Max tokens must be 10-4096, got {self.max_tokens}")


class ParameterTuner:
    """
    Tunes generation parameters based on:
    - Tone (witty=high temp, professional=low temp)
    - Platform (character limits affect token count)
    - User overrides (CLI args)
    """
    
    # Temperature profiles by tone
    # Low (0.1-0.3): Consistent, factual, structured
    # High (0.7-1.0): Diverse, creative, unexpected hooks
    TEMPERATURE_BY_TONE = {
        ToneEnum.WITTY: 0.8,        # High creativity for humor
        ToneEnum.PROFESSIONAL: 0.3, # Low consistency for precision
        ToneEnum.CASUAL: 0.6,       # Medium creativity for conversational
        ToneEnum.PERSUASIVE: 0.7,   # High creativity for engagement
    }
    
    # Max tokens by platform (based on character limits)
    # Twitter/Email: ~150 chars = ~40 tokens
    # Instagram: ~280 chars = ~70 tokens
    # LinkedIn: ~300+ chars = ~100 tokens
    MAX_TOKENS_BY_PLATFORM = {
        PlatformEnum.EMAIL: 50,         # Tight subject line
        PlatformEnum.INSTAGRAM: 100,    # ~280 char limit
        PlatformEnum.LINKEDIN: 150,     # ~300+ char limit
    }
    
    @staticmethod
    def tune(
        copy_request: CopyRequest,
        user_temperature: float = None,
        user_max_tokens: int = None,
        user_top_p: float = None
    ) -> GenerationParams:
        """
        Tune parameters based on tone & platform, with user overrides.
        
        Priority: User override > Tone/Platform defaults
        
        Args:
            copy_request: CopyRequest with tone and platform
            user_temperature: Override temperature (0.0-2.0)
            user_max_tokens: Override max_tokens (10-4096)
            user_top_p: Override top_p (0.0-1.0)
            
        Returns:
            GenerationParams ready for OpenAI API call
        """
        
        # Get default temperature from tone
        default_temp = ParameterTuner.TEMPERATURE_BY_TONE.get(copy_request.tone, 0.5)
        temperature = user_temperature if user_temperature is not None else default_temp
        
        # Get default max_tokens from platform
        default_tokens = ParameterTuner.MAX_TOKENS_BY_PLATFORM.get(copy_request.platform, 100)
        max_tokens = user_max_tokens if user_max_tokens is not None else default_tokens
        
        # Top_P default: usually 1.0 (no nucleus sampling)
        top_p = user_top_p if user_top_p is not None else 1.0
        
        # Create and validate
        params = GenerationParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens
        )
        
        return params
    
    @staticmethod
    def explain_parameters(params: GenerationParams) -> str:
        """Return human-readable explanation of parameter choices"""
        temp_desc = (
            "Very low - Highly consistent, factual, safe" if params.temperature < 0.3
            else "Low - Consistent, professional, structured" if params.temperature < 0.5
            else "Medium - Balanced creativity and consistency" if params.temperature < 0.7
            else "High - Creative, diverse, engaging" if params.temperature < 1.0
            else "Very high - Maximum creativity and risk"
        )
        
        return f"""
Parameter Explanation:
  • Temperature: {params.temperature} ({temp_desc})
  • Top_P: {params.top_p} (Nucleus sampling diversity)
  • Max Tokens: {params.max_tokens} (Max response length)
        """.strip()