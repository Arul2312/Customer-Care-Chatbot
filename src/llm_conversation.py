import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.decision_engine import LLMDecisionEngine

class LLMConversationManager:
    """
    Manages the complete conversation flow for refund requests
    Handles user interactions, decision processing, and response formatting
    """
    
    def __init__(self):
        self.engine = LLMDecisionEngine()
        self.conversation_active = False
        self.customer_info = {}
        
    def start_conversation(self):
        """Start the main conversation loop"""
        self.conversation_active = True
        
        print("\n🤖 Welcome to the LLM Refund Decision Bot!")
        print("Please describe your refund request, or type 'help' for more information.")
        print("Type 'quit' to exit at any time.\n")
        
        while self.conversation_active:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Check for system commands
                if self._handle_system_commands(user_input):
                    continue
                
                # Process the refund request
                self._process_user_request(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {str(e)}")
                print("Please try again or type 'help' for assistance.")
    
    def _handle_system_commands(self, user_input):
        """Handle system commands like status, reset, help, quit"""
        command = user_input.lower()
        
        if command == 'quit' or command == 'exit':
            print("👋 Goodbye! Thank you for using the LLM Refund Bot.")
            self.conversation_active = False
            return True
        
        elif command == 'help':
            self._show_help()
            return True
        
        elif command == 'status':
            self._show_status()
            return True
        
        elif command == 'reset':
            self._reset_conversation()
            return True
        
        elif command == 'export':
            self._export_conversation()
            return True
        
        return False
    
    def _process_user_request(self, user_input):
        """Process a user's refund request"""
        # Check if this is a continuation of an existing conversation
        if len(self.engine.conversation_history) > 0:
            result = self.engine.continue_conversation(user_input)
        else:
            result = self.engine.process_refund_request(user_input)
        
        # Display the result
        self._display_result(result)
    
    def _display_result(self, result):
        """Display the processing result to the user"""
        print("\n" + "="*60)
        
        if result['status'] == 'NEED_INFO':
            print("❓ MORE INFORMATION NEEDED")
            print("="*60)
            print(f"🤖 Bot: {result['question']}")
            
            # Show what was extracted so far
            if self.engine.extracted_info:
                print(f"\n📋 Information collected so far:")
                for key, value in self.engine.extracted_info.items():
                    print(f"   • {key}: {value}")
        
        elif result['status'] == 'DECISION':
            print("🎯 FINAL DECISION")
            print("="*60)
            
            # Format decision with appropriate emoji
            decision_emoji = {
                'RefundApproved': '✅',
                'RefundDenied': '❌',
                'PartialRefund': '⚠️',
                'ManualReview': '👥'
            }
            
            emoji = decision_emoji.get(result['decision'], '🤖')
            print(f"{emoji} Decision: {result['decision']}")
            print(f"📝 Reason: {result['reason']}")
            
            if result.get('terminal_node'):
                print(f"🎯 Terminal Node: {result['terminal_node']}")
            
            # Show extracted information
            if self.engine.extracted_info:
                print(f"\n📋 Information processed:")
                for key, value in self.engine.extracted_info.items():
                    print(f"   • {key}: {value}")
            
            # Reset for next request
            print("\n" + "-"*60)
            print("🔄 You can start a new refund request or type 'quit' to exit.")
            self.engine.reset_conversation()
        
        elif result['status'] == 'ERROR':
            print("❌ ERROR OCCURRED")
            print("="*60)
            print(f"🚨 Error: {result['error']}")
            print("Please try rephrasing your request or type 'help' for assistance.")
        
        print("="*60 + "\n")
    
    def _show_help(self):
        """Show help information"""
        print("\n" + "="*60)
        print("🆘 HELP - How to use the LLM Refund Bot")
        print("="*60)
        print("\n📝 DESCRIBE YOUR REFUND REQUEST:")
        print("• Be specific about what you bought and why you want a refund")
        print("• Include details like item type, condition, delivery status")
        print("\n💡 EXAMPLES:")
        print("  - 'I want to return my broken laptop'")
        print("  - 'Requesting refund for digital software that doesn't work'")
        print("  - 'My package was lost in transit'")
        print("  - 'I need a refund for spoiled food I received'")
        print("\n❓ THE BOT WILL ASK QUESTIONS LIKE:")
        print("• What type of item is this? (Physical/Digital/Perishable)")
        print("• Has the item been delivered?")
        print("• Is the item damaged or defective?")
        print("• Who was the seller? (In-house/Third-party)")
        print("• How did you pay? (Credit card/Gift card/etc.)")
        print("\n🛠️ SYSTEM COMMANDS:")
        print("• 'status' - Show current conversation progress")
        print("• 'reset'  - Start a new conversation")
        print("• 'export' - Save conversation history")
        print("• 'help'   - Show this help message")
        print("• 'quit'   - Exit the system")
        print("="*60 + "\n")
    
    def _show_status(self):
        """Show current conversation status"""
        status = self.engine.get_conversation_status()
        print("\n" + "="*60)
        print("📊 CONVERSATION STATUS")
        print("="*60)
        print(f"👤 Customer ID: {status['customer_id']}")
        print(f"💬 Conversation Turns: {status['turns']}")
        print(f"📍 Current State: {status['current_state']}")
        print(f"📋 Extracted Information:")
        if status['extracted_info']:
            for key, value in status['extracted_info'].items():
                print(f"   • {key}: {value}")
        else:
            print("   • No information extracted yet")
        print("="*60 + "\n")
    
    def _reset_conversation(self):
        """Reset the current conversation"""
        self.engine.reset_conversation()
        print("\n🔄 Conversation reset. You can start a new refund request.\n")
    
    def _export_conversation(self):
        """Export conversation history"""
        filename = self.engine.export_conversation()
        if filename:
            print(f"\n📁 Conversation exported to: {filename}\n")
        else:
            print("\n❌ Failed to export conversation.\n")