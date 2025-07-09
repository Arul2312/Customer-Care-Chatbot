# LLM-Driven Refund Decision Bot

An intelligent conversational AI system that automates refund request processing using Large Language Models (LLMs) and decision tree navigation. Uses OpenAI GPT-4o-mini with Mermaid flowchart technology to analyze customer requests, navigate complex business rules, and make intelligent refund decisions.

## Features

- **Agentic AI Decision Making**: Autonomous refund processing using OpenAI GPT-4o-mini
- **Interactive Conversation Mode**: Human-guided dialogue with AI-assisted analysis  
- **Mermaid Flowchart Navigation**: Follows comprehensive decision tree with 18+ outcome scenarios
- **Customer Profile Integration**: Real-time analysis of loyalty tier, account status, and return history
- **Natural Language Understanding**: Processes customer requests in conversational English

## Project Structure

```
LLM-Chatbot/
├── proto/
│   ├── config/
│   │   ├── config.py               # Main configuration
│   │   └── .env_llm               # Environment variables
│   ├── src/
│   │   ├── decision_engine.py     # Core AI decision engine
│   │   ├── mermaid_decision_tree.py # Flowchart logic
│   │   ├── llm_conversation.py    # Conversation manager
│   │   └── test_complete_requests.py # Test suite
│   ├── data/
│   │   └── customer_data.json     # Customer profile data
│   ├── main.py                    # Application entry point
│   ├── requirements.txt           # Dependencies
│   └── README.md
```

## Installation

1. **Clone repository:**
   ```bash
   git clone https://github.com/yourusername/LLM-Chatbot.git
   cd LLM-Chatbot/proto
   ```

2. **Install dependencies:**
   ```bash
   pip install openai python-dotenv
   ```

3. **Set OpenAI API key:**
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

## Usage

### Interactive Conversation Mode (Default)

```bash
python main.py
```

### Automated Testing Mode

```bash
python test_complete_requests.py
```

### Configuration

Edit config.py:

```python
class LLMConfig:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    MODEL_NAME = "gpt-4o-mini"          # AI model
    CONFIDENCE_THRESHOLD = 0.75          # Decision confidence
    TEMPERATURE = 0.1                    # Response creativity
```

Edit customer_data.json:

```json
{
  "customer_id": "CUST_67890",
  "account_status": "good_standing",     
  "loyalty_tier": "gold",                
  "fraud_flag": "no",                    
  "return_abuse": "no",                  
  "previous_returns": 8
}
```

## Core Components

### decision_engine.py
- **LLMDecisionEngine**: Main AI processing engine
- **Information Extraction**: NLP-based data extraction
- **Flowchart Navigation**: Step-by-step decision tree traversal
- **Customer Integration**: Profile-aware decision making

### mermaid_decision_tree.py  
- **Decision Flowchart**: Complete Mermaid-based logic tree
- **Leaf Node Mapping**: 18+ outcome scenarios
- **Business Rule Engine**: Policy compliance validation

### llm_conversation.py
- **Conversation Manager**: Multi-turn dialogue handling
- **Context Preservation**: Maintains conversation state
- **Progress Tracking**: Real-time conversation analysis

## Decision Outcomes

### Approval Scenarios
- **RefundApproved**: Standard full refund
- **Refund Approved: Lost in transit**: Package never delivered

### Denial Scenarios  
- **Refund Denied: Account issue**: Customer account problems
- **Refund Denied: Fraud flag**: Security concerns
- **Refund Denied: Perishable items**: Food/groceries not returnable
- **Refund Denied: Digital goods**: Software/downloads non-refundable
- **Refund Denied: Return window expired**: Time limit exceeded
- **Refund Denied: Third-party restriction**: Marketplace seller limitations
- **Refund Denied: BNPL terms**: Buy-now-pay-later restrictions

### Partial Refund Scenarios
- **Partial Refund Approved**: VIP customers with expired windows
- **Partial Refund to Gift Card Balance**: Gift card payment restrictions

### Manual Review Scenarios
- **Manual Review Required**: Return abuse patterns detected
- **Manual Review: Shipping delayed**: Delivery delay assessment needed
