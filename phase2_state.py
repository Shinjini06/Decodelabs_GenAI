#!/usr/bin/env python3
"""
Phase 2: State — Custom AI Chatbot with Memory
Structured message objects with timestamps & better model

Goal: Formalize conversation state with metadata, upgrade LLM quality
"""

from transformers import pipeline
import torch
from datetime import datetime
from dataclasses import dataclass, asdict
import json

# Better model than DistilGPT-2
print("Loading upgraded LLM (this takes ~1 min on first run)...")
generator = pipeline(
    "text-generation",
    model="gpt2",  # Larger, better quality than DistilGPT-2
    device=0 if torch.cuda.is_available() else -1
)


@dataclass
class Message:
    """Structured message object with timestamp"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str  # ISO 8601 format
    
    def to_dict(self):
        """Serialize to dictionary"""
        return asdict(self)
    
    def to_json(self):
        """Serialize to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data):
        """Deserialize from dictionary"""
        return cls(**data)
    
    def __repr__(self):
        """Display friendly format"""
        return f"[{self.timestamp}] {self.role.upper()}: {self.content[:60]}..."


class ConversationState:
    """Manages in-memory conversation history with structured messages"""
    
    def __init__(self):
        self.history = []  # Array of Message objects
        self.created_at = datetime.now().isoformat()
    
    def add_message(self, role, content):
        """Append validated message to history"""
        # Validation gate: reject empty/whitespace-only inputs
        if not content or not content.strip():
            raise ValueError("Message cannot be empty or whitespace-only")
        
        message = Message(
            role=role,
            content=content.strip(),
            timestamp=datetime.now().isoformat()
        )
        self.history.append(message)
        return message
    
    def get_history(self):
        """Return conversation history array"""
        return self.history
    
    def get_history_dicts(self):
        """Return history as list of dicts (for API)"""
        return [msg.to_dict() for msg in self.history]
    
    def get_history_json(self):
        """Return history as JSON string"""
        return json.dumps(self.get_history_dicts(), indent=2)
    
    def format_for_prompt(self):
        """Format history into prompt string for LLM"""
        prompt = ""
        for msg in self.history:
            if msg.role == "user":
                prompt += f"User: {msg.content}\n"
            else:
                prompt += f"Assistant: {msg.content}\n"
        prompt += "Assistant:"
        return prompt
    
    def display_history(self):
        """Pretty-print conversation history"""
        print(f"\n📋 Conversation History ({len(self.history)} messages)")
        print("="*70)
        for i, msg in enumerate(self.history):
            role = "👤 USER" if msg.role == "user" else "🤖 ASST"
            timestamp = msg.timestamp.split('T')[1][:8]  # HH:MM:SS
            content_preview = msg.content[:60] + "..." if len(msg.content) > 60 else msg.content
            print(f"[{i}] {role} ({timestamp}): {content_preview}")
        print("="*70)
    
    def __len__(self):
        return len(self.history)


def test_input_validation():
    """Test 1: Input validation gates"""
    print("\n" + "="*60)
    print("TEST 1: Input Validation Gates")
    print("="*60)
    
    state = ConversationState()
    
    # Valid message
    try:
        state.add_message("user", "Hello, how are you?")
        print("✓ Valid message accepted")
    except ValueError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Empty string
    try:
        state.add_message("user", "")
        print("✗ Empty string was accepted (should reject)")
    except ValueError:
        print("✓ Empty string rejected correctly")
    
    # Whitespace only
    try:
        state.add_message("user", "   ")
        print("✗ Whitespace-only was accepted (should reject)")
    except ValueError:
        print("✓ Whitespace-only rejected correctly")
    
    return state


def test_structured_messages():
    """Test 2: Message object structure with timestamps"""
    print("\n" + "="*60)
    print("TEST 2: Structured Message Objects & Timestamps")
    print("="*60)
    
    state = ConversationState()
    
    # Add messages
    state.add_message("user", "What is machine learning?")
    state.add_message("assistant", "Machine learning is a subset of AI...")
    state.add_message("user", "Give me an example.")
    
    print(f"\n✓ Created {len(state)} structured messages")
    print("\nMessage objects with metadata:")
    for msg in state.get_history():
        print(f"  • Role: {msg.role}")
        print(f"    Content: {msg.content[:50]}...")
        print(f"    Timestamp: {msg.timestamp}")
        print()
    
    return state


def test_serialization():
    """Test 3: Message serialization (dict & JSON)"""
    print("\n" + "="*60)
    print("TEST 3: Serialization (Dict & JSON)")
    print("="*60)
    
    state = ConversationState()
    state.add_message("user", "Test message")
    state.add_message("assistant", "Test response")
    
    # Dict format
    history_dicts = state.get_history_dicts()
    print(f"\n✓ History as Python dicts:")
    for entry in history_dicts:
        print(f"  {entry}")
    
    # JSON format
    history_json = state.get_history_json()
    print(f"\n✓ History as JSON:")
    print(history_json)
    
    return state


def test_multiturn_with_state():
    """Test 4: 3-turn conversation with structured state"""
    print("\n" + "="*60)
    print("TEST 4: Multi-turn Conversation (Structured State)")
    print("="*60)
    
    state = ConversationState()
    
    # Turn 1
    user_msg_1 = "What is Python?"
    state.add_message("user", user_msg_1)
    print(f"\nTurn 1 — User: {user_msg_1}")
    
    prompt_1 = state.format_for_prompt()
    response_1 = generator(prompt_1, max_new_tokens=60, num_return_sequences=1)
    asst_msg_1 = response_1[0]["generated_text"][len(prompt_1):].strip()[:100]
    state.add_message("assistant", asst_msg_1)
    print(f"Assistant: {asst_msg_1}")
    
    # Turn 2
    user_msg_2 = "Is it used for data science?"
    state.add_message("user", user_msg_2)
    print(f"\nTurn 2 — User: {user_msg_2}")
    
    prompt_2 = state.format_for_prompt()
    response_2 = generator(prompt_2, max_new_tokens=60, num_return_sequences=1)
    asst_msg_2 = response_2[0]["generated_text"][len(prompt_2):].strip()[:100]
    state.add_message("assistant", asst_msg_2)
    print(f"Assistant: {asst_msg_2}")
    
    # Turn 3
    user_msg_3 = "What about web development?"
    state.add_message("user", user_msg_3)
    print(f"\nTurn 3 — User: {user_msg_3}")
    
    prompt_3 = state.format_for_prompt()
    response_3 = generator(prompt_3, max_new_tokens=60, num_return_sequences=1)
    asst_msg_3 = response_3[0]["generated_text"][len(prompt_3):].strip()[:100]
    state.add_message("assistant", asst_msg_3)
    print(f"Assistant: {asst_msg_3}")
    
    # Display final state
    state.display_history()
    
    return state


def main():
    """Run all Phase 2 tests"""
    print("\n" + "#"*60)
    print("# PHASE 2: STATE")
    print("# Custom AI Chatbot with Memory — DecodeLabs Project")
    print("# Model: GPT-2 (Better quality)")
    print("#"*60)
    
    try:
        # Test 1: Validation gates
        state1 = test_input_validation()
        
        # Test 2: Structured messages with timestamps
        state2 = test_structured_messages()
        
        # Test 3: Serialization
        state3 = test_serialization()
        
        # Test 4: Full multi-turn with state
        state4 = test_multiturn_with_state()
        
        print("\n" + "="*60)
        print("✓ PHASE 2 SUCCESS: State formalized")
        print("="*60)
        print("\nKey Achievements:")
        print("  ✓ Input validation gates working (reject empty/whitespace)")
        print("  ✓ Message objects with timestamps implemented")
        print("  ✓ Conversation state class (ConversationState) working")
        print("  ✓ Serialization to dict & JSON functional")
        print("  ✓ Upgraded model quality (GPT-2 vs DistilGPT-2)")
        print("  ✓ Multi-turn conversation with structured state proven")
        print("\nState Architecture:")
        print("  • ConversationState class manages history array")
        print("  • Message dataclass stores role, content, timestamp")
        print("  • Validation gates before API transmission")
        print("  • Serializable to JSON for storage/logging")
        print("\nNext: Phase 3 — Error handling & robust framework\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()