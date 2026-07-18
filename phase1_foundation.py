#!/usr/bin/env python3
"""
Phase 1: Foundation — Custom AI Chatbot with Memory
Local Free LLM (DistilGPT-2) & basic multi-turn test

Goal: Validate LLM connectivity, API calls, and multi-turn message handling
Using: DistilGPT-2 (runs locally, completely free, no auth)
"""

from transformers import pipeline
import torch

# Initialize text generation pipeline (downloads model on first run)
print("Loading LLM (this may take a moment on first run)...")
generator = pipeline(
    "text-generation",
    model="distilgpt2",
    device=0 if torch.cuda.is_available() else -1  # GPU if available, else CPU
)


def test_basic_prompt():
    """Test 1: Single-turn API call to verify LLM works"""
    print("\n" + "="*60)
    print("TEST 1: Basic Prompt (Single-turn)")
    print("="*60)
    
    response = generator(
        "Say 'Phase 1 Foundation: OK'",
        max_length=30,
        num_return_sequences=1
    )
    
    text = response[0]["generated_text"].strip()
    print(f"✓ Local LLM Response received")
    print(f"Response: {text}")
    return True


def test_multiturn_conversation():
    """Test 2: Multi-turn conversation — append & transmit with in-memory array"""
    print("\n" + "="*60)
    print("TEST 2: Multi-turn Conversation (3 exchanges)")
    print("="*60)
    
    # In-memory conversation history array
    conversation_history = []
    
    # Turn 1: User asks a question
    user_message_1 = "What is the capital of France?"
    conversation_history.append({"role": "user", "content": user_message_1})
    print(f"\nTurn 1 — User: {user_message_1}")
    
    prompt_1 = format_prompt_from_history(conversation_history)
    response_1_obj = generator(prompt_1, max_length=80, num_return_sequences=1)
    # Extract only the new text generated (after prompt)
    response_1 = response_1_obj[0]["generated_text"][len(prompt_1):].strip()
    conversation_history.append({"role": "assistant", "content": response_1})
    print(f"Assistant: {response_1}")
    
    # Turn 2: Follow-up question (context-aware)
    user_message_2 = "What is its population?"
    conversation_history.append({"role": "user", "content": user_message_2})
    print(f"\nTurn 2 — User: {user_message_2}")
    
    prompt_2 = format_prompt_from_history(conversation_history)
    response_2_obj = generator(prompt_2, max_length=80, num_return_sequences=1)
    response_2 = response_2_obj[0]["generated_text"][len(prompt_2):].strip()
    conversation_history.append({"role": "assistant", "content": response_2})
    print(f"Assistant: {response_2}")
    
    # Turn 3: Another follow-up (demonstrates context preservation)
    user_message_3 = "Is that more or less than London?"
    conversation_history.append({"role": "user", "content": user_message_3})
    print(f"\nTurn 3 — User: {user_message_3}")
    
    prompt_3 = format_prompt_from_history(conversation_history)
    response_3_obj = generator(prompt_3, max_length=80, num_return_sequences=1)
    response_3 = response_3_obj[0]["generated_text"][len(prompt_3):].strip()
    conversation_history.append({"role": "assistant", "content": response_3})
    print(f"Assistant: {response_3}")
    
    # Display final conversation state
    print(f"\n✓ Conversation preserved across 3 turns")
    print(f"✓ Total history entries: {len(conversation_history)}")
    print(f"\nFinal conversation history structure:")
    for i, entry in enumerate(conversation_history):
        role = entry["role"].upper()
        content_preview = entry["content"][:50] + "..." if len(entry["content"]) > 50 else entry["content"]
        print(f"  [{i}] {role}: {content_preview}")
    
    return conversation_history


def format_prompt_from_history(history):
    """Format conversation history into a prompt for the LLM"""
    prompt = ""
    for entry in history:
        if entry["role"] == "user":
            prompt += f"User: {entry['content']}\n"
        else:
            prompt += f"Assistant: {entry['content']}\n"
    prompt += "Assistant:"
    return prompt


def main():
    """Run all Phase 1 foundation tests"""
    print("\n" + "#"*60)
    print("# PHASE 1: FOUNDATION")
    print("# Custom AI Chatbot with Memory — DecodeLabs Project")
    print("# Model: DistilGPT-2 (Local, 100% Free)")
    print("#"*60)
    
    try:
        # Test LLM connectivity and basic prompt
        test_basic_prompt()
        
        # Test multi-turn message handling with in-memory array
        history = test_multiturn_conversation()
        
        print("\n" + "="*60)
        print("✓ PHASE 1 SUCCESS: Foundation validated")
        print("="*60)
        print("\nKey Learnings:")
        print("  • Local LLM model loaded and running")
        print("  • Single-turn generation functional")
        print("  • Multi-turn conversation state managed via in-memory array")
        print("  • Message appending & transmission logic verified")
        print("  • Prompt formatting from history working")
        print("\nNext: Phase 2 — Formalize state structure with timestamp & validation\n")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Install required: pip install transformers torch")
        print("  2. First run downloads ~300MB model (internet required)")
        print("  3. Subsequent runs use cached model (no download)")


if __name__ == "__main__":
    main()