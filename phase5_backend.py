#!/usr/bin/env python3
"""
Phase 5: Integration — Complete Backend Server (FIXED)
Integrates Phase 1 (LLM) + Phase 2 (State) + Phase 3 (Validation)
Serves Phase 4 (Web UI) via Flask API

Run: python phase5_backend.py
Then open: http://localhost:5000
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import pipeline
import torch
from datetime import datetime
from dataclasses import dataclass, asdict
import json
import logging
import os

# ============================================================================
# SETUP
# ============================================================================

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

print("Loading LLM...")
try:
    generator = pipeline(
        "text-generation",
        model="gpt2",
        device=0 if torch.cuda.is_available() else -1
    )
    print("✓ LLM loaded successfully")
except Exception as e:
    print(f"✗ Error loading LLM: {e}")
    generator = None

# ============================================================================
# CUSTOM EXCEPTIONS (FROM PHASE 3)
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
# MESSAGE & STATE CLASSES (FROM PHASE 2)
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


class ConversationState:
    """Manages conversation history (FROM PHASE 2)"""
    
    MAX_HISTORY_TOKENS = 800
    
    def __init__(self):
        self.history = []
        self.created_at = datetime.now().isoformat()
        self.error_count = 0
        logger.info(f"Conversation initialized at {self.created_at}")
    
    def add_message(self, role, content):
        """Add message with validation (FROM PHASE 3)"""
        try:
            if not isinstance(role, str) or not isinstance(content, str):
                raise ValidationError("Role and content must be strings")
            
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
            logger.error(f"Unexpected error: {e}")
            raise StateError(f"Failed to add message: {str(e)}")
    
    def get_history(self):
        """Return history as list of dicts"""
        try:
            return [msg.to_dict() for msg in self.history]
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            raise StateError("Failed to retrieve history")
    
    def format_for_prompt(self):
        """Format history for LLM"""
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
        """Estimate token count (rough: 4 chars per token)"""
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
                    f"Token budget exceeded: {tokens}/{self.MAX_HISTORY_TOKENS}"
                )
            return tokens
        except TokenBudgetError:
            raise
        except Exception as e:
            logger.error(f"Error checking token budget: {e}")
            return 0


# ============================================================================
# GLOBAL STATE (Persists across requests)
# ============================================================================

conversation_state = ConversationState()


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def serve_frontend():
    """Serve the web UI (Phase 4)"""
    try:
        return send_from_directory('.', 'phase4_chatbot_ui.html')
    except FileNotFoundError:
        return jsonify({
            "error": "Frontend file not found",
            "solution": "Ensure 'phase4_chatbot_ui.html' is in current directory",
            "current_directory": os.getcwd(),
            "files": os.listdir('.')
        }), 404


@app.route('/api/send-message', methods=['POST'])
def send_message():
    """
    API endpoint: Accept user message, generate response
    Integrates Phase 1 (LLM) + Phase 2 (State) + Phase 3 (Validation)
    """
    try:
        data = request.get_json()
        user_input = data.get('message', '').strip()
        
        # =====================================================================
        # PHASE 3: VALIDATION GATES
        # =====================================================================
        
        errors = []
        
        if not user_input:
            errors.append("Message cannot be empty")
        
        if len(user_input) > 5000:
            errors.append(f"Message too long: {len(user_input)}/5000")
        
        # Check token budget
        tokens = conversation_state.estimate_tokens()
        new_tokens = len(user_input) // 4
        if (tokens + new_tokens) > conversation_state.MAX_HISTORY_TOKENS:
            errors.append(f"Token budget exceeded: {tokens + new_tokens}/800")
        
        if errors:
            return jsonify({
                "success": False,
                "errors": errors,
                "tokens": tokens
            }), 400
        
        # =====================================================================
        # PHASE 2: ADD USER MESSAGE TO STATE
        # =====================================================================
        
        try:
            conversation_state.add_message("user", user_input)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "errors": [str(e)],
                "tokens": tokens
            }), 400
        
        # =====================================================================
        # PHASE 1: GENERATE RESPONSE FROM LLM
        # =====================================================================
        
        if generator is None:
            assistant_response = "[LLM not loaded - using fallback response]"
        else:
            try:
                prompt = conversation_state.format_for_prompt()
                
                response = generator(
                    prompt,
                    max_new_tokens=80,
                    num_return_sequences=1
                )
                
                generated_text = response[0]["generated_text"]
                assistant_response = generated_text[len(prompt):].strip()[:200]
                
                if not assistant_response:
                    assistant_response = "I understood your question. How can I help further?"
                
                logger.info(f"Generated response: {assistant_response[:50]}...")
            
            except Exception as api_error:
                logger.error(f"LLM API error: {api_error}")
                assistant_response = f"[Response generation encountered an issue. Error: {str(api_error)[:50]}]"
        
        # =====================================================================
        # PHASE 2: ADD ASSISTANT RESPONSE TO STATE
        # =====================================================================
        
        try:
            conversation_state.add_message("assistant", assistant_response)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "errors": [str(e)]
            }), 400
        
        # =====================================================================
        # RETURN RESPONSE TO FRONTEND
        # =====================================================================
        
        new_tokens = conversation_state.estimate_tokens()
        
        return jsonify({
            "success": True,
            "response": assistant_response,
            "history": conversation_state.get_history(),
            "tokens": new_tokens,
            "errors": [],
            "message_count": len(conversation_state.history)
        }), 200
    
    except Exception as e:
        logger.error(f"Unexpected error in /send-message: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "errors": [f"Server error: {str(e)}"]
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get current conversation history"""
    try:
        return jsonify({
            "success": True,
            "history": conversation_state.get_history(),
            "tokens": conversation_state.estimate_tokens(),
            "message_count": len(conversation_state.history),
            "created_at": conversation_state.created_at
        }), 200
    except Exception as e:
        logger.error(f"Error retrieving history: {e}")
        return jsonify({
            "success": False,
            "errors": [str(e)]
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history"""
    global conversation_state
    try:
        conversation_state = ConversationState()
        logger.info("Conversation cleared")
        return jsonify({
            "success": True,
            "message": "Conversation cleared"
        }), 200
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        return jsonify({
            "success": False,
            "errors": [str(e)]
        }), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get conversation statistics"""
    try:
        tokens = conversation_state.estimate_tokens()
        return jsonify({
            "success": True,
            "message_count": len(conversation_state.history),
            "tokens": tokens,
            "max_tokens": conversation_state.MAX_HISTORY_TOKENS,
            "errors": conversation_state.error_count,
            "created_at": conversation_state.created_at
        }), 200
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            "success": False,
            "errors": [str(e)]
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Custom AI Chatbot with Memory",
        "version": "Phase 5 - Integration",
        "backend": "Flask + GPT-2",
        "llm_loaded": generator is not None
    }), 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("PHASE 5: INTEGRATION — BACKEND SERVER (FIXED)")
    print("Custom AI Chatbot with Memory — DecodeLabs Project")
    print("="*60)
    print("\n✓ Phase 1: LLM (GPT-2)")
    print("✓ Phase 2: State (ConversationState)")
    print("✓ Phase 3: Validation (Error handling)")
    print("✓ Phase 4: Frontend (Web UI)")
    print("✓ Phase 5: Integration (Flask API)")
    print("\n🚀 Backend starting...")
    print("📡 API running on: http://localhost:5000")
    print("🌐 Frontend: Open http://localhost:5000 in browser")
    print("\nAPI Endpoints:")
    print("  • POST /api/send-message - Send chat message")
    print("  • GET  /api/history - Get conversation history")
    print("  • POST /api/clear - Clear conversation")
    print("  • GET  /api/stats - Get statistics")
    print("  • GET  /api/health - Health check")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=False, host='127.0.0.1', port=5000, use_reloader=False)