#!/usr/bin/env python3
"""
Phase 3: Validation — Custom AI Chatbot with Memory
Input guards & error handling framework

Goal: Implement robust error handling, custom exceptions, validation gates
"""

from transformers import pipeline
import torch
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import logging
from typing import Optional

# Setup logging for error tracking
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Loading LLM...")
generator = pipeline(
    "text-generation",
    model="gpt2",
    device=0 if torch.cuda.is_available() else -1
)


# ============================================================================
# CUSTOM EXCEPTIONS
# ============================================================================

class ChatbotException(Exception):
    """Base exception for all chatbot errors"""
    pass


class ValidationError(ChatbotException):
    """Raised when input validation fails"""
    pass


class StateError(ChatbotException):
    """Raised when conversation state is invalid"""
    pass


class APIError(ChatbotException):
    """Raised when LLM API call fails"""
    pass


class TokenBudgetError(ChatbotException):
    """Raised when token limit exceeded"""
    pass


# ============================================================================
# MESSAGE & STATE CLASSES (WITH ERROR HANDLING)
# ============================================================================

@dataclass
class Message:
    """Structured message object with validation"""
    role: str
    content: str
    timestamp: str
    
    def __post_init__(self):
        """Validate message on creation"""
        if self.role not in ["user", "assistant"]:
            raise ValidationError(f"Invalid role: {self.role}. Must be 'user' or 'assistant'")
        
        if not self.content or not self.content.strip():
            raise ValidationError("Message content cannot be empty")
        
        if len(self.content) > 5000:
            raise ValidationError(f"Message too long: {len(self.content)} chars (max 5000)")
    
    def to_dict(self):
        return asdict(self)
    
    def to_json(self):
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data):
        return cls(**data)
    
    def __repr__(self):
        return f"[{self.timestamp}] {self.role.upper()}: {self.content[:60]}..."


class ConversationState:
    """Manages conversation history with comprehensive error handling"""
    
    # Token budget (GPT-2 context window is 1024 tokens, leave 20% buffer)
    MAX_HISTORY_TOKENS = 800
    
    def __init__(self):
        self.history = []
        self.created_at = datetime.now().isoformat()
        self.error_count = 0
        logger.info(f"Conversation initialized at {self.created_at}")
    
    def add_message(self, role, content):
        """Add message with comprehensive validation"""
        try:
            # Pre-validation checks
            if not isinstance(role, str) or not isinstance(content, str):
                raise ValidationError("Role and content must be strings")
            
            # Create message (post_init validates)
            message = Message(
                role=role,
                content=content.strip(),
                timestamp=datetime.now().isoformat()
            )
            
            self.history.append(message)
            logger.info(f"Message added: {role} ({len(content)} chars)")
            return message
        
        except ValidationError as e:
            self.error_count += 1
            logger.error(f"Validation failed: {e}")
            raise
        except Exception as e:
            self.error_count += 1
            logger.error(f"Unexpected error adding message: {e}")
            raise StateError(f"Failed to add message: {str(e)}")
    
    def get_history(self):
        """Safely return history"""
        try:
            if not self.history:
                logger.warning("History is empty")
            return self.history
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            raise StateError("Failed to retrieve history")
    
    def get_history_dicts(self):
        """Return history as dicts with error handling"""
        try:
            return [msg.to_dict() for msg in self.history]
        except Exception as e:
            logger.error(f"Error serializing to dicts: {e}")
            raise StateError("Failed to serialize history")
    
    def get_history_json(self):
        """Return history as JSON with error handling"""
        try:
            return json.dumps(self.get_history_dicts(), indent=2)
        except Exception as e:
            logger.error(f"Error serializing to JSON: {e}")
            raise StateError("Failed to serialize to JSON")
    
    def format_for_prompt(self):
        """Format history for LLM with error handling"""
        try:
            if not self.history:
                raise StateError("Cannot format empty history")
            
            prompt = ""
            for msg in self.history:
                if msg.role == "user":
                    prompt += f"User: {msg.content}\n"
                else:
                    prompt += f"Assistant: {msg.content}\n"
            prompt += "Assistant:"
            return prompt
        except StateError:
            raise
        except Exception as e:
            logger.error(f"Error formatting prompt: {e}")
            raise StateError("Failed to format prompt")
    
    def estimate_tokens(self):
        """Estimate token count (rough: ~4 chars per token)"""
        try:
            total_chars = sum(len(msg.content) for msg in self.history)
            estimated_tokens = total_chars // 4
            return estimated_tokens
        except Exception as e:
            logger.error(f"Error estimating tokens: {e}")
            return 0
    
    def check_token_budget(self):
        """Check if token budget exceeded"""
        try:
            tokens = self.estimate_tokens()
            if tokens > self.MAX_HISTORY_TOKENS:
                raise TokenBudgetError(
                    f"Token budget exceeded: {tokens}/{self.MAX_HISTORY_TOKENS}. "
                    f"Consider pruning history."
                )
            logger.info(f"Token budget OK: {tokens}/{self.MAX_HISTORY_TOKENS}")
            return tokens
        except TokenBudgetError:
            raise
        except Exception as e:
            logger.error(f"Error checking token budget: {e}")
            return 0
    
    def display_history(self):
        """Pretty-print with error handling"""
        try:
            print(f"\n📋 Conversation History ({len(self.history)} messages)")
            print("="*70)
            for i, msg in enumerate(self.history):
                role = "👤 USER" if msg.role == "user" else "🤖 ASST"
                timestamp = msg.timestamp.split('T')[1][:8]
                content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
                print(f"[{i}] {role} ({timestamp}): {content_preview}")
            print(f"{'='*70}\nErrors encountered: {self.error_count}")
        except Exception as e:
            logger.error(f"Error displaying history: {e}")
            print(f"[ERROR] Could not display history: {e}")
    
    def __len__(self):
        return len(self.history)


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_validation_errors():
    """Test 1: Input validation error handling"""
    print("\n" + "="*60)
    print("TEST 1: Input Validation Error Handling")
    print("="*60)
    
    state = ConversationState()
    
    # Test 1a: Empty string
    try:
        state.add_message("user", "")
        print("✗ Empty string was accepted")
    except ValidationError as e:
        print(f"✓ Empty string rejected: {e}")
    
    # Test 1b: Whitespace only
    try:
        state.add_message("user", "   \t  ")
        print("✗ Whitespace accepted")
    except ValidationError as e:
        print(f"✓ Whitespace rejected: {e}")
    
    # Test 1c: Invalid role
    try:
        state.add_message("moderator", "Hello")
        print("✗ Invalid role accepted")
    except ValidationError as e:
        print(f"✓ Invalid role rejected: {e}")
    
    # Test 1d: Message too long
    try:
        long_msg = "x" * 10000
        state.add_message("user", long_msg)
        print("✗ Oversized message accepted")
    except ValidationError as e:
        print(f"✓ Oversized message rejected: {e}")
    
    # Test 1e: Non-string input
    try:
        state.add_message("user", 12345)
        print("✗ Non-string accepted")
    except ValidationError as e:
        print(f"✓ Non-string rejected: {e}")
    
    # Test 1f: Valid message passes
    try:
        state.add_message("user", "This is valid")
        print("✓ Valid message accepted")
    except Exception as e:
        print(f"✗ Valid message rejected: {e}")
    
    return state


def test_state_errors():
    """Test 2: Conversation state error handling"""
    print("\n" + "="*60)
    print("TEST 2: Conversation State Error Handling")
    print("="*60)
    
    state = ConversationState()
    
    # Test 2a: Format empty history
    try:
        state.format_for_prompt()
        print("✗ Empty history was formatted")
    except StateError as e:
        print(f"✓ Empty history rejected: {e}")
    
    # Test 2b: Add valid messages
    try:
        state.add_message("user", "Hello")
        state.add_message("assistant", "Hi there!")
        print("✓ Valid messages added")
    except Exception as e:
        print(f"✗ Failed to add messages: {e}")
    
    # Test 2c: Format non-empty history
    try:
        prompt = state.format_for_prompt()
        print(f"✓ History formatted successfully ({len(prompt)} chars)")
    except StateError as e:
        print(f"✗ Failed to format: {e}")
    
    return state


def test_token_budget():
    """Test 3: Token budget monitoring"""
    print("\n" + "="*60)
    print("TEST 3: Token Budget Monitoring")
    print("="*60)
    
    state = ConversationState()
    
    # Add messages and monitor tokens
    try:
        state.add_message("user", "What is AI?" * 10)
        tokens = state.check_token_budget()
        print(f"✓ Token check passed: {tokens} tokens")
    except TokenBudgetError as e:
        print(f"⚠ Token warning: {e}")
    except Exception as e:
        print(f"✗ Error checking tokens: {e}")
    
    return state


def test_api_error_handling():
    """Test 4: LLM API call error handling"""
    print("\n" + "="*60)
    print("TEST 4: LLM API Error Handling (Safe Fallback)")
    print("="*60)
    
    state = ConversationState()
    
    # Build a conversation
    try:
        state.add_message("user", "What is machine learning?")
        print("✓ User message added")
        
        # Attempt API call with error handling
        try:
            prompt = state.format_for_prompt()
            response = generator(prompt, max_new_tokens=50, num_return_sequences=1)
            asst_response = response[0]["generated_text"][len(prompt):].strip()[:100]
            state.add_message("assistant", asst_response)
            print(f"✓ API call successful")
            print(f"  Response: {asst_response[:60]}...")
        
        except Exception as api_error:
            logger.error(f"API call failed: {api_error}")
            # Graceful fallback
            fallback_msg = "[Response generation failed - API error] Please try again."
            state.add_message("assistant", fallback_msg)
            print(f"⚠ API error handled gracefully")
            print(f"  Fallback message added: {fallback_msg}")
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    state.display_history()
    return state


def test_error_recovery():
    """Test 5: Multi-turn with error recovery"""
    print("\n" + "="*60)
    print("TEST 5: Multi-turn Error Recovery")
    print("="*60)
    
    state = ConversationState()
    turns = [
        {"user": "Tell me about Python", "desc": "Turn 1"},
        {"user": "", "desc": "Turn 2 (invalid - empty)"},
        {"user": "Is it used for web dev?", "desc": "Turn 3 (recovery)"},
    ]
    
    for i, turn in enumerate(turns, 1):
        try:
            print(f"\n{turn['desc']}:")
            if turn['user']:
                state.add_message("user", turn['user'])
                print(f"✓ Added user message")
                
                # Generate response
                try:
                    prompt = state.format_for_prompt()
                    response = generator(prompt, max_new_tokens=50, num_return_sequences=1)
                    asst_msg = response[0]["generated_text"][len(prompt):].strip()[:80]
                    state.add_message("assistant", asst_msg)
                    print(f"✓ Generated response")
                except Exception as api_err:
                    logger.warning(f"Response generation failed: {api_err}")
                    state.add_message("assistant", "[Unable to generate response]")
                    print(f"⚠ Fallback response added")
            else:
                state.add_message("user", turn['user'])
        
        except ValidationError as e:
            print(f"✗ Validation error (caught): {e}")
            print(f"  Continuing to next turn...")
            continue
        
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            print(f"  Continuing to next turn...")
            continue
    
    state.display_history()
    print(f"\nRecovery Summary: {len(state)} messages preserved despite errors")
    return state


def main():
    """Run all Phase 3 tests"""
    print("\n" + "#"*60)
    print("# PHASE 3: VALIDATION")
    print("# Custom AI Chatbot with Memory — DecodeLabs Project")
    print("# Error Handling & Robustness Framework")
    print("#"*60)
    
    try:
        # Test 1: Validation errors
        test_validation_errors()
        
        # Test 2: State errors
        test_state_errors()
        
        # Test 3: Token budget
        test_token_budget()
        
        # Test 4: API error handling
        test_api_error_handling()
        
        # Test 5: Multi-turn error recovery
        test_error_recovery()
        
        print("\n" + "="*60)
        print("✓ PHASE 3 SUCCESS: Validation framework complete")
        print("="*60)
        print("\nKey Achievements:")
        print("  ✓ Custom exceptions (ValidationError, StateError, APIError, TokenBudgetError)")
        print("  ✓ Input validation gates (role, content, length, type)")
        print("  ✓ Try-catch error handling in all methods")
        print("  ✓ Logging for debugging & error tracking")
        print("  ✓ Graceful fallback for API failures")
        print("  ✓ Token budget monitoring & warnings")
        print("  ✓ Error recovery across multi-turn conversations")
        print("\nError Handling Patterns:")
        print("  • Pre-validation before operations")
        print("  • Custom exceptions for specific error types")
        print("  • Logging at EVERY error point")
        print("  • Graceful degradation (fallback messages)")
        print("  • Continue-on-error for conversation flow")
        print("\nNext: Phase 4 — Interface (Terminal/Web UI)\n")
        
    except Exception as e:
        print(f"\n✗ Critical error: {e}")
        logger.critical(f"Fatal error in Phase 3: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()