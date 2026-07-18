# Project 1: Custom AI Chatbot with Memory

**A production-ready conversational AI system with persistent session state**

## 🎯 Objective

Transform a stateless LLM into a fully contextual chatbot through session state management, demonstrating mastery of the "Amnesia Cloud" problem—where LLMs lose context between requests.

## 📊 Project Status

✅ **COMPLETE** | 7 Days | Production-Ready

---

## 🏗 Architecture (5 Phases)

### Phase 1: Foundation
- LLM Integration (GPT-2 via HuggingFace)
- Basic prompt testing
- Multi-turn message handling

### Phase 2: State
- Message dataclass with timestamps
- ConversationState class
- History array management

### Phase 3: Validation
- Custom exception hierarchy (5 types)
- Input validation gates
- Token budget monitoring
- Error recovery framework

### Phase 4: Interface
- Professional web UI (HTML/CSS/JS)
- Real-time metrics dashboard
- Chat message display
- Export to JSON

### Phase 5: Integration
- Flask backend API (5 endpoints)
- Frontend ↔ Backend communication
- Production-ready logging
- Full error handling

---

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run Backend
```bash
python phase5_backend.py
```

Backend starts at: `http://127.0.0.1:5000`

### Open Frontend
Browser → `http://127.0.0.1:5000`

Status should show: **🟢 Connected**

### Test the Chatbot