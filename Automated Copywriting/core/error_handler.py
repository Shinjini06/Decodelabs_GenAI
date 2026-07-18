# core/error_handler.py
"""
Error handling and recovery strategies
"""

from typing import Optional, Callable
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential


class CopywritingError(Exception):
    """Base exception for copywriting framework"""
    pass


class APIError(CopywritingError):
    """API-related errors"""
    pass


class ValidationError(CopywritingError):
    """Validation errors"""
    pass


class RateLimitError(CopywritingError):
    """Rate limit exceeded"""
    pass


class ErrorHandler:
    """
    Centralized error handling with recovery strategies
    """
    
    @staticmethod
    def handle_api_error(error: Exception, retry_count: int = 0) -> str:
        """Handle API errors with recovery suggestions"""
        
        error_type = type(error).__name__
        error_msg = str(error)
        
        if "429" in error_msg or "rate limit" in error_msg.lower():
            return f"""
❌ RATE LIMIT ERROR (Attempt {retry_count + 1})
   The API is rate-limited. Strategies:
   
   1. Use Batch API for bulk requests (50% cheaper, no rate limits)
   2. Reduce concurrent requests (current: 5, try: 2-3)
   3. Add exponential backoff delay between requests
   4. Wait 60 seconds before retrying
   
   Recommendation: Switch to batch_pipeline for large volumes.
            """.strip()
        
        elif "401" in error_msg or "authentication" in error_msg.lower():
            return f"""
❌ AUTHENTICATION ERROR
   Your API key is invalid or expired.
   
   Steps:
   1. Check .env file: OPENAI_API_KEY=...
   2. Verify key at: https://platform.openai.com/account/api-keys
   3. Regenerate if necessary
   4. Restart the application
            """.strip()
        
        elif "model" in error_msg.lower():
            return f"""
❌ MODEL ERROR
   Model not available or incorrect.
   
   Available models:
   - gpt-4o-mini (faster, cheaper)
   - gpt-4 (slower, more capable)
   - gpt-3.5-turbo (legacy)
   
   Update .env: OPENAI_MODEL=gpt-4o-mini
            """.strip()
        
        else:
            return f"""
❌ UNKNOWN ERROR
   Type: {error_type}
   Message: {error_msg}
   
   Debug steps:
   1. Check internet connection
   2. Verify API key is valid
   3. Check request format (Pydantic models)
   4. Review logs for stack trace
            """.strip()
    
    @staticmethod
    def handle_validation_error(error: Exception) -> str:
        """Handle validation errors"""
        return f"""
❌ VALIDATION ERROR
   Invalid input data:
   
   {str(error)}
   
   Check:
   - Product name (1-100 chars)
   - Platform (linkedin, instagram, email)
   - Tone (witty, professional, casual, persuasive)
   - Generated copy (min 10 chars)
        """.strip()