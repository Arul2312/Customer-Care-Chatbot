# LLM-Driven Refund Decision Bot

An intelligent conversational refund processing system that uses Large Language Models to navigate decision trees and make automated refund decisions based on business rules.

## Features

- AI-powered decision tree traversal
- Natural language understanding for customer requests
- Intelligent question generation for missing information
- Comprehensive business rule application
- Transparent decision reasoning with complete audit trails
- Support for multiple payment methods and seller types
- Automated fraud detection and return abuse prevention

## Project Structure

```
proto/
├── main.py                     # Main application entry point
├── requirements.txt            # Python dependencies
├── config/
│   ├── config.py              # Configuration settings
│   └── .env_llm               # Environment variables
├── data/
│   └── customer_data.json     # Customer profile data
└── src/
    ├── decision_engine.py     # Core LLM decision engine
    ├── llm_conversation.py    # Conversation manager
    └── mermaid_decision_tree.py # Decision tree structure
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Arul2312/Customer-Care-Chatbot.git
cd Customer-Care-Chatbot/proto
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp config/.env_llm.example config/.env_llm
```

4. Add your OpenAI API key to [`config/.env_llm`](config/.env_llm):
```
OPENAI_API_KEY=your_api_key_here
```

## Usage

### Basic Usage

Run the main application:
```bash
python main.py
```

### Interactive Commands

- **Help**: Type `help` to see available commands and examples
- **Status**: Type `status` to view conversation progress
- **Reset**: Type `reset` to start a new conversation
- **Export**: Type `export` to save conversation history
- **Quit**: Type `quit` to exit the system

### Example Interactions

```
You: I want to return my broken laptop
Bot: What is the condition of the item? Please specify: damaged, defective, or normal.

You: It's damaged
Bot: Has the item been delivered to you? Please specify: Yes or No.

You: Yes
Bot: Who was the seller for this item? Please specify: In-house or Third-party.

You: In-house
Bot: DECISION: RefundApproved
```

## Configuration

### Environment Variables

The system uses the following configuration in [`config/.env_llm`](config/.env_llm):

- `OPENAI_API_KEY`: Your OpenAI API key
- `MODEL_NAME`: OpenAI model to use (default: gpt-4o-mini)
- `MAX_TOKENS`: Maximum tokens per response (default: 800)
- `CONFIDENCE_THRESHOLD`: Minimum confidence for decisions (default: 0.75)
- `EXTRACTION_TEMPERATURE`: Temperature for information extraction (default: 0.5)
- `NAVIGATION_TEMPERATURE`: Temperature for decision navigation (default: 0.0)
- `QUESTION_TEMPERATURE`: Temperature for question generation (default: 0.3)

### Customer Data

Customer profiles are stored in [`data/customer_data.json`](data/customer_data.json) and include:

- Account status and loyalty tier
- Fraud flags and return abuse history
- Purchase history and lifetime value
- Regional information

## Decision Tree Logic

The system follows a comprehensive decision tree defined in [`src/mermaid_decision_tree.py`](src/mermaid_decision_tree.py) that considers:

1. **Customer Status**: Account standing and fraud flags
2. **Item Category**: Physical, Digital, or Perishable items
3. **Return Eligibility**: Item condition and return policies
4. **Delivery Status**: Shipping issues and delivery confirmation
5. **Seller Policies**: In-house vs third-party seller rules
6. **Payment Method**: Credit card, gift card, BNPL restrictions

## Core Components

### LLMDecisionEngine

The main decision engine ([`src/decision_engine.py`](src/decision_engine.py)) handles:

- Information extraction from user input using LLM
- Decision tree navigation with step-by-step validation
- Dynamic question generation for missing information
- Final decision making with detailed reasoning

### LLMConversationManager

The conversation manager ([`src/llm_conversation.py`](src/llm_conversation.py)) manages:

- User interaction flow and command processing
- Result formatting and display
- Conversation state management
- Export functionality for audit trails

### MermaidDecisionTree

The decision tree structure ([`src/mermaid_decision_tree.py`](src/mermaid_decision_tree.py)) defines:

- Complete flowchart logic in Mermaid format
- Valid keywords and decision nodes
- Terminal conditions and decision paths
- Path validation and navigation rules

## API Reference

### LLMDecisionEngine Methods

- `process_refund_request(user_request)`: Process initial refund request
- `continue_conversation(user_response)`: Continue with additional user input
- `load_customer_data(file_path)`: Load customer profile data
- `reset_conversation()`: Reset conversation state
- `export_conversation(filename)`: Export conversation history

### Response Format

The system returns structured responses:

```python
{
    'status': 'NEED_INFO' | 'DECISION' | 'ERROR',
    'question': 'Generated question for user',
    'decision': 'Final decision name',
    'reason': 'Detailed reasoning',
    'terminal_node': 'Decision tree terminal node'
}
