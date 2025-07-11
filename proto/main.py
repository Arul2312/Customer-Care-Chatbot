#!/usr/bin/env python3
"""
LLM-Driven Decision Tree Bot
Completely independent refund processing system

Usage:
    python main.py
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.llm_conversation import LLMConversationManager

def print_banner():
    """Print the application banner"""
    print("=" * 68)
    print("           LLM-DRIVEN DECISION TREE REFUND BOT")
    print("           Intelligent Conversational Refund Processing")
    print("=" * 68)
    print()
    print("Features:")
    print("  AI-powered decision tree traversal")
    print("  Natural language understanding")
    print("  Intelligent question generation")
    print("  Comprehensive business rule application")
    print("  Transparent decision reasoning")
    print()
    print("Commands:")
    print("  'status'  - Show conversation progress")
    print("  'reset'   - Start new conversation")
    print("  'export'  - Save conversation history")
    print("  'help'    - Show detailed help")
    print("  'quit'    - Exit the system")
    print("-" * 70)

def main():
    """Main application entry point"""
    try:
        # Print banner
        print_banner()
        
        # Initialize the conversation manager
        conversation_manager = LLMConversationManager()
        
        # Load customer data with the correct file path
        conversation_manager.engine.load_customer_data('data/customer_data.json')
        
        # Start the conversation
        conversation_manager.start_conversation()
        
    except KeyboardInterrupt:
        print("\n\nGoodbye! Thank you for using the LLM Refund Bot.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()